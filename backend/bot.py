"""
Telegram bot — RAG + FAQ voice chatbot.

Ishga tushirish:
    cd backend
    python bot.py

Zarur ENV:
    TELEGRAM_BOT_TOKEN — BotFather dan olingan token
    GEMINI_API_KEY, UZBEKVOICE_API_KEY — mavjud .env da
"""

import asyncio
import io
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pydub import AudioSegment
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv(Path(__file__).resolve().parent / ".env", override=False)

from rag.query import get_answer
from speech.stt import speech_to_text
from speech.tts import text_to_speech

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

GREETING = (
    "Assalomu alaykum! Davlat Ekologik Ekspertizasi Markazining raqamli yordamchisiga xush kelibsiz.\n"
    "Men Vazirlar Mahkamasining 541 hamda 1038-qarorlariga muvofiq javob beraman, "
    "hamda markaz xizmatlari, hududiy filiallar haqida ma'lumot beraman."
)


def _ogg_to_wav(ogg_bytes: bytes) -> bytes:
    """Telegram dan kelgan OGG/OPUS audio ni WAV ga aylantiradi."""
    audio = AudioSegment.from_ogg(io.BytesIO(ogg_bytes))
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    return wav_io.getvalue()


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(GREETING)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = update.message.text.strip()
    if not question:
        return

    thinking = await update.message.reply_text("⏳")

    try:
        answer = await get_answer(question)
        await thinking.edit_text(answer)
    except Exception as e:
        logger.error(f"Matnli savol xatosi: {e}", exc_info=True)
        await thinking.edit_text("Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    thinking = await update.message.reply_text("⏳")

    try:
        # OGG yuklab olish
        voice_file = await update.message.voice.get_file()
        ogg_bytes = await voice_file.download_as_bytearray()

        # OGG → WAV konvertatsiya (pydub + ffmpeg)
        loop = asyncio.get_running_loop()
        wav_bytes = await loop.run_in_executor(None, _ogg_to_wav, bytes(ogg_bytes))

        # STT → savol matni
        question = await speech_to_text(wav_bytes)
        logger.info(f"STT natijasi: {question!r}")

        # RAG → javob matni
        answer = await get_answer(question)
        logger.info(f"Javob: {answer!r}")

        # TTS → audio
        audio_bytes, mime_type = await text_to_speech(answer)

        # Matn javobini yuborish (savol + javob)
        await thinking.edit_text(f"Savol: {question}\n\n{answer}")

        # Audio javobini yuborish
        audio_io = io.BytesIO(audio_bytes)
        audio_io.name = "answer.mp3" if "mpeg" in mime_type else "answer.wav"
        await update.message.reply_audio(audio=audio_io)

    except Exception as e:
        logger.error(f"Ovozli xabar xatosi: {e}", exc_info=True)
        await thinking.edit_text("Ovozni qayta ishlashda xatolik. Iltimos, qaytadan urinib ko'ring.")


def create_application() -> Application:
    """Sozlangan Application ob'ektini qaytaradi (FastAPI lifespan uchun)."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN .env faylida topilmadi")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    return app


def main() -> None:
    """Botni mustaqil (standalone) rejimda ishga tushiradi."""
    app = create_application()
    logger.info("Telegram bot ishga tushdi (standalone)...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
