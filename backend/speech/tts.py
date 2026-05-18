"""
UzbekVoice AI yordamida matn → audio (Text-to-Speech) moduli.
API: https://uzbekvoice.ai/api/v1/tts
Modellar: lola, shoira
"""

import asyncio
import base64
import logging
import os
import re

import requests

logger = logging.getLogger(__name__)

UZBEKVOICE_TTS_URL = "https://uzbekvoice.ai/api/v1/tts"

# Rim raqamlarini o'zbek so'zlariga almashtirish (uzunroqdan qisqaga qarab)
_ROMAN_MAP = [
    (r'\bXIII\b', "o'n uchinchi"),
    (r'\bXII\b',  "o'n ikkinchi"),
    (r'\bXI\b',   "o'n birinchi"),
    (r'\bVIII\b', "sakkizinchi"),
    (r'\bVII\b',  "yettinchi"),
    (r'\bIX\b',   "to'qqizinchi"),
    (r'\bVI\b',   "oltinchi"),
    (r'\bIV\b',   "to'rtinchi"),
    (r'\bIII\b',  "uchinchi"),
    (r'\bII\b',   "ikkinchi"),
    (r'\bXX\b',   "yigirmanchi"),
    (r'\bXV\b',   "o'n beshinchi"),
    (r'\bX\b',    "o'ninchi"),
    (r'\bV\b',    "beshinchi"),
    (r'\bI\b',    "birinchi"),
]


def _preprocess_for_tts(text: str) -> str:
    """TTS ga yuborishdan oldin matni tozalaydi: markdown, emoji, rim raqamlari, satr bo'limlari."""

    # Markdown bold/italic: ** *** * __ _
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'(?<!\w)_+(?!\w)', '', text)

    # Markdown header: # ## ### ...
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)

    # Ro'yxat belgilari satr boshida: "- band", "• band" → bo'shliq
    text = re.sub(r'^\s*[-•]\s+', ' ', text, flags=re.MULTILINE)

    # Kod bloki: `code` yoki ```code```
    text = re.sub(r'`+[^`]*`+', '', text)

    # Markdown link: [matn](url) → matn
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # @username → username
    text = re.sub(r'@(\w+)', lambda m: m.group(1).replace('_', ' '), text)

    # Emoji va maxsus unicode belgilar
    text = re.sub(r'[\U0001F000-\U0001FFFF\U00002600-\U000027FF]', '', text)

    # Rim raqamlarini o'zbek so'zlariga almashtirish (uzunroqdan qisqaga)
    for pattern, replacement in _ROMAN_MAP:
        text = re.sub(pattern, replacement, text)

    # Satr bo'limlari → tinish belgisi/bo'shliq
    # \n\n → ". "  (gap tugadi, pauza)
    # \n   → ", "  (ro'yxat bandi, kichik pauza)
    text = re.sub(r'\n\n+', '. ', text)
    text = re.sub(r'\n', ', ', text)

    # Ortiqcha nuqta-vergullarni tozalash
    text = re.sub(r'\.\s*,', '.', text)
    text = re.sub(r',\s*,', ',', text)
    text = re.sub(r'\.{2,}', '.', text)

    # Ortiqcha bo'shliqlar
    text = re.sub(r'[ \t]+', ' ', text)

    return text.strip()


def _extract_audio_url(result: dict) -> str:
    """
    UzbekVoice TTS javobidan audio URL ni topadi.
    Format: {"status":"SUCCESS","result":{"url":"https://..."},...}
    """
    # result.result.url — asosiy yo'l
    inner = result.get("result")
    if isinstance(inner, dict):
        url = inner.get("url") or inner.get("audio_url") or inner.get("file_url")
        if isinstance(url, str) and url.startswith("http"):
            return url

    # Yuqori darajada to'g'ridan-to'g'ri URL maydonlar
    for field in ("url", "audio_url", "audio_link", "file_url"):
        url = result.get(field, "")
        if isinstance(url, str) and url.startswith("http"):
            return url

    return ""


def _detect_audio_type(data: bytes) -> str:
    """Audio baytlaridan MIME turini aniqlaydi."""
    if data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        return "audio/wav"
    if data[:3] == b"ID3" or (len(data) > 1 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0):
        return "audio/mpeg"
    if data[:4] == b"OggS":
        return "audio/ogg"
    return "audio/mpeg"


def _synthesize_sync(text: str, api_key: str) -> tuple[bytes, str]:
    """
    Blokirovchi TTS chaqiruvi — run_in_executor ichida ishlaydi.
    Returns: (audio_bytes, mime_type)
    """
    model = os.getenv("TTS_MODEL", "lola")

    payload = {
        "text":     text,
        "model":    model,
        "blocking": "true",
    }
    headers = {
        "Authorization": api_key,
        "Content-Type":  "application/json",
    }

    logger.info(f"UzbekVoice TTS: {len(text)} belgi, model={model}")

    try:
        response = requests.post(
            UZBEKVOICE_TTS_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("UzbekVoice TTS so'rovi vaqt limitidan oshdi (60s)")

    if response.status_code != 200:
        raise RuntimeError(
            f"UzbekVoice TTS xatosi {response.status_code}: {response.text}"
        )

    # Agar server to'g'ridan-to'g'ri audio qaytarsa
    content_type = response.headers.get("content-type", "")
    if content_type.startswith("audio/"):
        logger.info(f"TTS: to'g'ridan-to'g'ri audio ({len(response.content)} bayt)")
        return response.content, content_type

    # JSON javob
    result = response.json()
    logger.info(f"UzbekVoice TTS javobi: {result}")

    audio_url = _extract_audio_url(result)
    if not audio_url:
        raise RuntimeError(
            f"UzbekVoice TTS: audio URL topilmadi. Javob: {result}"
        )

    logger.info(f"TTS: audio yuklanmoqda: {audio_url[:60]}...")
    audio_resp = requests.get(audio_url, timeout=30)
    audio_resp.raise_for_status()
    audio = audio_resp.content
    return audio, _detect_audio_type(audio)


async def text_to_speech(text: str) -> tuple[bytes, str]:
    """
    Matnni audio baytlariga aylantiradi.
    Returns: (audio_bytes, mime_type)  — mime_type frontend uchun kerak.
    """
    if not text.strip():
        raise ValueError("Matn bo'sh, TTS bajarish mumkin emas")

    api_key = os.getenv("UZBEKVOICE_API_KEY")
    if not api_key:
        raise ValueError("UZBEKVOICE_API_KEY .env faylida topilmadi")

    processed = _preprocess_for_tts(text)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _synthesize_sync, processed, api_key)
