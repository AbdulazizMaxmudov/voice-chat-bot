"""
UzbekVoice AI yordamida audio → matn (Speech-to-Text) moduli.
API: https://uzbekvoice.ai/api/v1/stt
"""

import asyncio
import logging
import os

import requests

logger = logging.getLogger(__name__)

UZBEKVOICE_STT_URL = "https://uzbekvoice.ai/api/v1/stt"


def _extract_text(result: dict) -> str:
    """
    UzbekVoice turli javob formatlaridan matnni ajratib oladi.
    To'liq javob log da ko'rinadi — format o'zgarse shu funksiyani moslashtiring.
    """
    # Oddiy string maydonlar
    for field in ("text", "transcript", "transcription"):
        val = result.get(field)
        if isinstance(val, str) and val.strip():
            return val.strip()

    # "result" maydoni — string, dict yoki list bo'lishi mumkin
    r = result.get("result")
    if isinstance(r, str) and r.strip():
        return r.strip()

    if isinstance(r, dict):
        # {"result": {"text": "..."}} yoki {"result": {"transcript": "..."}}
        for field in ("text", "transcript", "transcription"):
            val = r.get(field)
            if isinstance(val, str) and val.strip():
                return val.strip()

    if isinstance(r, list):
        # [{"text": "..."}, ...] — segmentlar ro'yxati
        parts = []
        for item in r:
            if isinstance(item, dict):
                for field in ("text", "transcript", "word"):
                    val = item.get(field)
                    if isinstance(val, str):
                        parts.append(val)
            elif isinstance(item, str):
                parts.append(item)
        joined = " ".join(parts).strip()
        if joined:
            return joined

    return ""


def _transcribe_sync(audio_bytes: bytes, api_key: str) -> str:
    """
    Blokirovchi STT chaqiruvi — run_in_executor ichida ishlaydi.
    Audio baytlarni UzbekVoice ga yuboradi va matni qaytaradi.
    """
    language = os.getenv("STT_LANGUAGE", "uz-ru")
    model    = os.getenv("STT_MODEL", "general")

    files = {
        "file": ("audio.wav", audio_bytes, "audio/wav"),
    }
    data = {
        "return_offsets": "false",
        "run_diarization": "false",
        "language":        language,
        "model":           model,
        "blocking":        "true",
    }
    headers = {"Authorization": api_key}

    logger.info(f"UzbekVoice STT: {len(audio_bytes)} bayt, til={language}, model={model}")

    try:
        response = requests.post(
            UZBEKVOICE_STT_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=60,
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("UzbekVoice STT so'rovi vaqt limitidan oshdi (60s)")

    if response.status_code != 200:
        raise RuntimeError(
            f"UzbekVoice STT xatosi {response.status_code}: {response.text}"
        )

    result = response.json()
    logger.info(f"UzbekVoice STT javobi: {result}")   # tuzatish uchun to'liq log

    text = _extract_text(result)

    if not text:
        raise RuntimeError(f"Nutq aniqlanmadi. UzbekVoice javobi: {result}")

    logger.info(f"STT natijasi: {text!r}")
    return text


async def speech_to_text(audio_bytes: bytes) -> str:
    """
    WAV audio baytlarni matnga aylantiradi.
    Tillar: uz (o'zbek), ru (rus), uz-ru (aralash) — .env da STT_LANGUAGE orqali.
    """
    if not audio_bytes:
        raise ValueError("Audio ma'lumot bo'sh")

    api_key = os.getenv("UZBEKVOICE_API_KEY")
    if not api_key:
        raise ValueError("UZBEKVOICE_API_KEY .env faylida topilmadi")

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _transcribe_sync, audio_bytes, api_key)
