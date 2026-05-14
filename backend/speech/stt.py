import asyncio
import logging
import os
import threading

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

SUPPORTED_LANGUAGES = ["uz-UZ", "ru-RU", "en-US"]


def _create_speech_config() -> speechsdk.SpeechConfig:
    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        raise EnvironmentError(
            "AZURE_SPEECH_KEY va AZURE_SPEECH_REGION .env faylida belgilanishi kerak"
        )
    config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION,
    )
    config.set_profanity(speechsdk.ProfanityOption.Raw)
    return config


def _recognize_sync(audio_bytes: bytes, content_type: str) -> tuple[str, str]:
    """
    Uzluksiz tanish (continuous recognition) — har qanday uzunlikdagi audio uchun ishlaydi.
    recognize_once() faqat ~15 soniya bilan cheklanadi, bu esa undan xoli.

    Returns:
        (aniqlangan_matn, aniqlangan_til) juftligi
    """
    speech_config = _create_speech_config()

    if "webm" in content_type or "ogg" in content_type:
        audio_format = speechsdk.audio.AudioStreamFormat(
            compressed_stream_format=speechsdk.AudioStreamContainerFormat.ANY
        )
    else:
        audio_format = speechsdk.audio.AudioStreamFormat.get_wave_format_pcm(16000, 16, 1)

    push_stream = speechsdk.audio.PushAudioInputStream(stream_format=audio_format)
    audio_config = speechsdk.audio.AudioConfig(stream=push_stream)

    auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=SUPPORTED_LANGUAGES
    )

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config,
        auto_detect_source_language_config=auto_detect_config,
    )

    all_texts: list[str] = []
    detected_lang = SUPPORTED_LANGUAGES[0]
    done_event = threading.Event()
    error_holder: list[str] = []

    def on_recognized(evt: speechsdk.SpeechRecognitionEventArgs) -> None:
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            nonlocal detected_lang
            lang_result = speechsdk.AutoDetectSourceLanguageResult(evt.result)
            detected_lang = lang_result.language or SUPPORTED_LANGUAGES[0]
            all_texts.append(evt.result.text)
            logger.debug(f"STT fragment [{detected_lang}]: {evt.result.text[:60]}")

    def on_canceled(evt: speechsdk.SpeechRecognitionCanceledEventArgs) -> None:
        details = speechsdk.CancellationDetails(evt.result)
        if details.reason == speechsdk.CancellationReason.Error:
            error_holder.append(f"STT xatosi: {details.error_details}")
        done_event.set()

    def on_session_stopped(evt) -> None:
        done_event.set()

    recognizer.recognized.connect(on_recognized)
    recognizer.canceled.connect(on_canceled)
    recognizer.session_stopped.connect(on_session_stopped)

    push_stream.write(audio_bytes)
    push_stream.close()

    recognizer.start_continuous_recognition()
    done_event.wait(timeout=60)
    recognizer.stop_continuous_recognition()

    if error_holder:
        raise RuntimeError(error_holder[0])

    if not all_texts:
        raise ValueError("Audioda nutq aniqlanmadi")

    full_text = " ".join(all_texts)
    logger.info(f"STT [{detected_lang}]: {full_text[:120]}")
    return full_text, detected_lang


async def speech_to_text(audio_bytes: bytes, content_type: str = "audio/wav") -> tuple[str, str]:
    """
    Audio baytlarini matnga o'giradi (async wrapper).

    Args:
        audio_bytes: Wav yoki WebM audio fayl baytlari
        content_type: MIME turi (audio/wav, audio/webm, ...)

    Returns:
        (aniqlangan_matn, aniqlangan_til) juftligi
    """
    if not audio_bytes:
        raise ValueError("Audio ma'lumotlari bo'sh")

    loop = asyncio.get_running_loop()
    text, language = await loop.run_in_executor(
        None, _recognize_sync, audio_bytes, content_type
    )
    return text, language
