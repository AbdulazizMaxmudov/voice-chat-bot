import asyncio
import logging
import os
import uuid
from pathlib import Path
from typing import AsyncGenerator

import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
from rag.embedding import GeminiEmbedding

load_dotenv()

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
CHROMA_DIR = str(BASE_DIR / "chroma_db")
COLLECTION_NAME = "rag_documents"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = (
    "Sen hujjatlardagi ma'lumotlarga asoslangan yordamchi assistantsan. "
    "Faqat berilgan kontekstdagi ma'lumotlarga tayanib javob ber. "
    "Agar kontekstda javob bo'lmasa, 'Bu haqida hujjatda ma'lumot topilmadi' de. "
    "Qisqa, aniq va foydali javob ber."
)

_cached_index: VectorStoreIndex | None = None
_session_engines: dict[str, object] = {}


def _get_index() -> VectorStoreIndex:
    global _cached_index
    if _cached_index is not None:
        return _cached_index

    Settings.llm = GoogleGenAI(
        model="gemini-2.5-flash",
        api_key=GEMINI_API_KEY,
        temperature=0.1,
    )
    Settings.embed_model = GeminiEmbedding(api_key=GEMINI_API_KEY)

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    _cached_index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
    )
    logger.info("VectorStoreIndex keshga yuklandi")
    return _cached_index


def invalidate_index_cache() -> None:
    """Ingest dan keyin chaqiriladi — eski kesh va barcha sessiyalarni tozalaydi."""
    global _cached_index, _session_engines
    _cached_index = None
    _session_engines.clear()
    logger.info("Index keshi va barcha sessiyalar tozalandi")


def clear_session(session_id: str) -> None:
    """Bitta sessiyaning suhbat tarixini o'chiradi."""
    _session_engines.pop(session_id, None)
    logger.info(f"Sessiya tozalandi: {session_id}")


def _get_chat_engine(session_id: str):
    """
    Sessiyaga tegishli chat engine ni qaytaradi.
    Har sessiya o'z ChatMemoryBuffer ini saqlab, suhbat tarixini saqlaydi.
    """
    if session_id not in _session_engines:
        index = _get_index()
        memory = ChatMemoryBuffer.from_defaults(token_limit=4000)
        _session_engines[session_id] = index.as_chat_engine(
            chat_mode="condense_plus_context",
            memory=memory,
            similarity_top_k=5,
            system_prompt=SYSTEM_PROMPT,
        )
        logger.debug(f"Yangi chat sessiyasi yaratildi: {session_id}")
    return _session_engines[session_id]


_RETRY_DELAYS = [5, 15, 30]


def _is_retryable(e: Exception) -> bool:
    msg = str(e)
    return "503" in msg or "429" in msg or "UNAVAILABLE" in msg or "RESOURCE_EXHAUSTED" in msg


async def query_rag(question: str, session_id: str | None = None) -> str:
    """
    Savolni sessiya tarixi bilan birga Gemini 2.5 Flash ga yuboradi.
    503/429 xatolarda avtomatik retry qiladi.
    """
    sid = session_id or str(uuid.uuid4())
    last_exc: Exception | None = None

    for attempt, delay in enumerate([0] + _RETRY_DELAYS):
        if delay:
            logger.warning(f"LLM {delay}s kutilmoqda (urinish {attempt}/{len(_RETRY_DELAYS)})")
            await asyncio.sleep(delay)
        try:
            chat_engine = _get_chat_engine(sid)
            response = await chat_engine.achat(question)
            return str(response)
        except Exception as e:
            if _is_retryable(e) and attempt < len(_RETRY_DELAYS):
                last_exc = e
                continue
            logger.error(f"RAG query xatosi: {e}")
            raise RuntimeError(f"Savol qayta ishlashda xato: {e}")

    raise RuntimeError(f"Bir necha urinishdan keyin ham xato: {last_exc}")


async def query_rag_stream(question: str, session_id: str | None = None) -> AsyncGenerator[str, None]:
    """
    Savolni sessiya tarixi bilan streaming rejimda qayta ishlaydi.
    503/429 xatolarda streaming boshlanmasidan oldin retry qiladi.
    """
    sid = session_id or str(uuid.uuid4())
    last_exc: Exception | None = None

    for attempt, delay in enumerate([0] + _RETRY_DELAYS):
        if delay:
            logger.warning(f"LLM stream {delay}s kutilmoqda (urinish {attempt}/{len(_RETRY_DELAYS)})")
            await asyncio.sleep(delay)
        try:
            chat_engine = _get_chat_engine(sid)
            streaming_response = await chat_engine.astream_chat(question)
            async for token in streaming_response.async_response_gen():
                yield token
            return
        except Exception as e:
            if _is_retryable(e) and attempt < len(_RETRY_DELAYS):
                last_exc = e
                continue
            logger.error(f"RAG stream xatosi: {e}")
            raise RuntimeError(f"Streaming xatosi: {e}")

    raise RuntimeError(f"Bir necha urinishdan keyin ham xato: {last_exc}")
