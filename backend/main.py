# RAG Voice Chatbot — FastAPI backend
# Endpointlar: GET /health | GET /documents | POST /ingest | POST /upload
#              POST /chat/text | POST /chat/voice | DELETE /session/{session_id}

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

from rag.ingest import DOCS_DIR, SUPPORTED_EXTENSIONS, ingest_documents
from rag.query import clear_session, invalidate_index_cache, query_rag, query_rag_stream
from speech.stt import speech_to_text
from speech.tts import text_to_speech_stream


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("RAG Voice Chatbot serveri ishga tushdi")
    yield
    logger.info("Server to'xtatildi")


app = FastAPI(
    title="RAG Voice Chatbot API",
    description="FastAPI + LlamaIndex + ChromaDB + Gemini 2.5 Flash + Azure Speech",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Detected-Language", "X-Question-Text"],
)


# ── Pydantic modellari ──────────────────────────────────────────────────────

class TextRequest(BaseModel):
    question: str
    session_id: str | None = None


class IngestResponse(BaseModel):
    message: str
    total_chunks: int
    processed_files: list[str]
    failed_files: list[dict]


# ── Endpointlar ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    """Server va API kalitlari holatini tekshiradi."""
    return {
        "status": "ok",
        "services": {
            "gemini_key_set": bool(os.getenv("GEMINI_API_KEY")),
            "azure_speech_key_set": bool(os.getenv("AZURE_SPEECH_KEY")),
            "azure_region": os.getenv("AZURE_SPEECH_REGION", "belgilanmagan"),
        },
    }


@app.get("/documents", tags=["RAG"])
async def list_documents():
    """Yuklangan hujjatlar ro'yxatini qaytaradi."""
    DOCS_DIR.mkdir(exist_ok=True)
    files = [
        {"name": f.name, "size_bytes": f.stat().st_size, "type": f.suffix.lower()}
        for f in sorted(DOCS_DIR.iterdir())
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return {"documents": files, "count": len(files)}


@app.post("/ingest", response_model=IngestResponse, tags=["RAG"])
async def ingest():
    """
    /backend/documents/ papkasidagi hujjatlarni o'qib ChromaDB ga yuklaydi.
    Har safar chaqirilganda collection tozalanib qayta indekslanadi (dublikat yo'q).
    """
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, ingest_documents)
        invalidate_index_cache()
        return IngestResponse(
            message=f"{result['total_chunks']} ta chunk muvaffaqiyatli saqlandi",
            total_chunks=result["total_chunks"],
            processed_files=result["processed_files"],
            failed_files=result["failed_files"],
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ingest xatosi: {e}")
        raise HTTPException(status_code=500, detail=f"Hujjat yuklashda xato: {e}")


@app.post("/upload", response_model=IngestResponse, tags=["RAG"])
async def upload_document(file: UploadFile = File(...)):
    """
    Hujjat yuklaydi va avtomatik indekslaydi.
    Qabul qilinadigan formatlar: .docx, .pdf, .txt, .md
    """
    ext = Path(file.filename or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Qo'llab-quvvatlanmaydigan format '{ext}'. "
                   f"Ruxsat etilgan: {sorted(SUPPORTED_EXTENSIONS)}",
        )

    DOCS_DIR.mkdir(exist_ok=True)
    file_path = DOCS_DIR / (file.filename or f"upload{ext}")
    content = await file.read()
    file_path.write_bytes(content)
    logger.info(f"Fayl yuklandi: {file.filename} ({len(content):,} bayt)")

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, ingest_documents)
        invalidate_index_cache()
        return IngestResponse(
            message=f"'{file.filename}' yuklandi va {result['total_chunks']} ta chunk saqlandi",
            total_chunks=result["total_chunks"],
            processed_files=result["processed_files"],
            failed_files=result["failed_files"],
        )
    except Exception as e:
        logger.error(f"Upload ingest xatosi: {e}")
        raise HTTPException(status_code=500, detail=f"Indekslashda xato: {e}")


@app.post("/chat/text", tags=["Chat"])
async def chat_text(request: TextRequest):
    """
    Matnli savol qabul qiladi, Gemini 2.5 Flash orqali streaming javob qaytaradi.

    Request body: {"question": "...", "session_id": "optional-uuid"}
    Response: text/plain streaming
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Savol bo'sh bo'lishi mumkin emas")

    async def generate():
        try:
            async for token in query_rag_stream(request.question, request.session_id):
                yield token
        except RuntimeError as e:
            logger.error(f"Text streaming xatosi: {e}")
            yield f"\n[Xato: {e}]"

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")


@app.post("/chat/voice", tags=["Chat"])
async def chat_voice(
    audio: UploadFile = File(...),
    session_id: str | None = Form(default=None),
):
    """
    Audio fayl qabul qilib, audio javob qaytaradi.

    Pipeline:
      1. STT   — Azure Speech: audio → matn (til avtomatik aniqlanadi)
      2. RAG   — matn → Gemini javob (sessiya tarixi saqlanadi)
      3. TTS   — Azure Speech: javob matni → streaming audio (Raw PCM)

    Request : multipart/form-data  audio=<file>  session_id=<optional>
    Response: audio/pcm streaming
    Headers : X-Detected-Language, X-Question-Text
    """
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Audio fayl bo'sh")

    content_type = audio.content_type or "audio/wav"
    logger.info(f"Audio qabul qilindi: {len(audio_bytes):,} bayt | tur: {content_type}")

    try:
        question_text, detected_lang = await speech_to_text(audio_bytes, content_type)
        logger.info(f"STT [{detected_lang}]: {question_text}")

        if not question_text.strip():
            raise HTTPException(status_code=422, detail="Audioda nutq aniqlanmadi")

        response_text = await query_rag(question_text, session_id)
        logger.info(f"RAG javobi: {response_text[:120]}...")

        async def audio_pipeline():
            async for chunk in text_to_speech_stream(response_text, detected_lang):
                yield chunk

        return StreamingResponse(
            audio_pipeline(),
            media_type="audio/pcm",
            headers={
                "X-Question-Text": question_text[:200],
                "X-Detected-Language": detected_lang,
            },
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Voice chat xatosi: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Kutilmagan xato: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server xatosi: {e}")


@app.delete("/session/{session_id}", tags=["Chat"])
async def delete_session(session_id: str):
    """Sessiyaning suhbat tarixini o'chiradi."""
    clear_session(session_id)
    return {"message": f"Sessiya '{session_id}' tozalandi"}
