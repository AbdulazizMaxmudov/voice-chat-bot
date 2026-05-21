"""
RAG + FAQ Voice Chatbot — FastAPI asosiy server.

Ishga tushirish:
    cd backend
    uvicorn main:app --reload --port 8000
"""

import base64
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent

# .env faylini yuklash (boshqa importlardan oldin bo'lishi kerak)
load_dotenv()

from rag.ingest import ingest_documents
from rag.query import get_answer
from speech.stt import speech_to_text
from speech.tts import text_to_speech
from bot import create_application

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server ishga tushdi")

    # Auto-ingest: ChromaDB bo'sh yoki collection mavjud bo'lmasa — hujjatlarni yukla
    try:
        client = chromadb.PersistentClient(path=str(BASE_DIR / "chroma_db"))
        try:
            col = client.get_collection("documents")
            count = col.count()
        except Exception:
            count = 0
        if count == 0:
            logger.info("ChromaDB bo'sh — avtomatik ingest boshlanmoqda...")
            result = await ingest_documents()
            logger.info(f"Avtomatik ingest natijasi: {result}")
        else:
            logger.info(f"ChromaDB tayyor: {count} ta chunk")
    except Exception as e:
        logger.warning(f"Avtomatik ingest tekshirishda xato: {e}")

    # Telegram bot — token bo'lsa ishga tushirish
    tg_app = None
    if os.getenv("TELEGRAM_BOT_TOKEN"):
        try:
            tg_app = create_application()
            await tg_app.initialize()
            await tg_app.start()
            await tg_app.updater.start_polling(drop_pending_updates=True)
            logger.info("Telegram bot ishga tushdi")
        except Exception as e:
            logger.warning(f"Telegram bot ishga tushmadi: {e}")
            tg_app = None

    yield

    # Telegram bot ni to'xtatish
    if tg_app:
        try:
            await tg_app.updater.stop()
            await tg_app.stop()
            await tg_app.shutdown()
            logger.info("Telegram bot to'xtatildi")
        except Exception as e:
            logger.warning(f"Telegram bot to'xtatishda xato: {e}")

    logger.info("Server to'xtatildi")


app = FastAPI(
    title="RAG Voice Chatbot API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Sxemalar ----------

class ChatRequest(BaseModel):
    message: str


# ---------- Endpointlar ----------

@app.get("/health", tags=["Tizim"])
async def health():
    """Server ishlayotganini tekshirish."""
    return {"status": "ok"}


@app.post("/ingest", tags=["Ma'lumotlar"])
async def ingest():
    """
    backend/documents/ papkasidagi barcha .docx fayllarni
    ChromaDB ga yuklaydi. Qayta chaqirilsa eski ma'lumotlar yangilanadi.
    """
    try:
        result = await ingest_documents()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"/ingest xatosi: {e}")
        raise HTTPException(status_code=500, detail="Server ichki xatosi")


@app.post("/chat/text", tags=["Chat"])
async def chat_text(request: ChatRequest):
    """Matnli savol qabul qilib, matnli javob qaytaradi."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Savol bo'sh bo'lmasligi kerak")
    try:
        answer = await get_answer(request.message)
        return {"answer": answer}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"/chat/text xatosi: {e}")
        raise HTTPException(status_code=500, detail="Server ichki xatosi")


@app.post("/chat/voice", tags=["Chat"])
async def chat_voice(audio: UploadFile = File(...)):
    """
    Audio fayl qabul qilib (multipart/form-data, field: 'audio'),
    audio/wav javobi qaytaradi.

    Jarayon: audio → STT → get_answer() → TTS → WAV
    """
    try:
        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Audio fayl bo'sh")

        # Nutqni matnga o'tkazish
        question = await speech_to_text(audio_bytes)
        logger.info(f"STT natijasi: {question!r}")

        if not question.strip():
            raise HTTPException(status_code=422, detail="Nutq aniqlanmadi")

        # Javob topish
        answer = await get_answer(question)
        logger.info(f"Javob: {answer!r}")

        # Javobni nutqqa aylantirish
        audio_bytes, audio_type = await text_to_speech(answer)

        # Savol (STT natijasi), javob va audio birga qaytariladi
        return {
            "question":   question,
            "answer":     answer,
            "audio":      base64.b64encode(audio_bytes).decode("ascii"),
            "audio_type": audio_type,
        }

    except HTTPException:
        raise
    except RuntimeError as e:
        # STT/TTS dan kelgan aniq xato xabarlari
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"/chat/voice xatosi: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
