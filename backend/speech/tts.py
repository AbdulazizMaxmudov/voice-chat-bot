import asyncio
import logging
import os
from typing import AsyncGenerator

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

VOICE_MAP: dict[str, str] = {
    "uz-UZ": "uz-UZ-MadinaNeural",
    "ru-RU": "ru-RU-SvetlanaNeural",
    "en-US": "en-US-JennyNeural",
}

CHUNK_SIZE = 4096


def _create_speech_config(language: str) -> speechsdk.SpeechConfig:
    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        raise EnvironmentError(
            "AZURE_SPEECH_KEY va AZURE_SPEECH_REGION .env faylida belgilanishi kerak"
        )
    config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION,
    )
    config.speech_synthesis_voice_name = VOICE_MAP.get(language, VOICE_MAP["uz-UZ"])
    config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Raw24Khz16BitMonoPcm
    )
    return config


async def text_to_speech_stream(
    text: str, language: str = "uz-UZ"
) -> AsyncGenerator[bytes, None]:
    """
    Matnni audioga o'girib, Real-time streaming shaklida qaytaradi.

    Args:
        text: TTS ga beriladigan matn
        language: Audio tili (uz-UZ, ru-RU, en-US)

    Yields:
        Raw PCM audio baytlari (chunks)

    Raises:
        RuntimeError: Azure TTS synthesis bekor qilinsa
    """
    if not text or not text.strip():
        raise ValueError("TTS uchun matn bo'sh bo'lishi mumkin emas")

    # get_running_loop() — async funksiya ichida ishlatilishi to'g'ri yo'l
    loop = asyncio.get_running_loop()
    audio_queue: asyncio.Queue[bytes | Exception | None] = asyncio.Queue()

    def _on_synthesizing(evt: speechsdk.SpeechSynthesisEventArgs) -> None:
        if evt.result.audio_data:
            loop.call_soon_threadsafe(audio_queue.put_nowait, bytes(evt.result.audio_data))

    def _on_completed(evt: speechsdk.SpeechSynthesisEventArgs) -> None:
        loop.call_soon_threadsafe(audio_queue.put_nowait, None)

    def _on_canceled(evt: speechsdk.SpeechSynthesisEventArgs) -> None:
        details = speechsdk.SpeechSynthesisCancellationDetails(evt.result)
        err = RuntimeError(
            f"TTS bekor qilindi: {details.reason} — {details.error_details}"
        )
        logger.error(str(err))
        # None o'rniga Exception yuboriladi — consumer uni raise qiladi
        loop.call_soon_threadsafe(audio_queue.put_nowait, err)

    speech_config = _create_speech_config(language)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    synthesizer.synthesizing.connect(_on_synthesizing)
    synthesizer.synthesis_completed.connect(_on_completed)
    synthesizer.synthesis_canceled.connect(_on_canceled)

    loop.run_in_executor(None, lambda: synthesizer.speak_text_async(text).get())

    while True:
        chunk = await audio_queue.get()
        if chunk is None:
            break
        if isinstance(chunk, Exception):
            raise chunk
        for i in range(0, len(chunk), CHUNK_SIZE):
            yield chunk[i : i + CHUNK_SIZE]


async def text_to_speech_bytes(text: str, language: str = "uz-UZ") -> bytes:
    """Matnni to'liq audioga o'girib bayt sifatida qaytaradi (test uchun)."""
    chunks: list[bytes] = []
    async for chunk in text_to_speech_stream(text, language):
        chunks.append(chunk)
    return b"".join(chunks)
