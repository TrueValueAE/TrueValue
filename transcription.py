"""
Voice Message Transcription for TrueValue AI
=============================================
Uses OpenAI Whisper API to transcribe voice messages to text.
"""

import os
import io
import logging
from typing import Optional

import httpx

logger = logging.getLogger("transcription")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"


def is_transcription_available() -> bool:
    """Check if transcription is configured."""
    return bool(OPENAI_API_KEY)


async def transcribe_voice(
    audio_bytes: bytes,
    file_format: str = "ogg",
) -> Optional[str]:
    """
    Transcribe voice audio to text using OpenAI Whisper API.

    Args:
        audio_bytes: Raw audio file bytes
        file_format: Audio format (ogg, mp3, wav, m4a, etc.)

    Returns:
        Transcribed text string, or None on failure.
    """
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set — voice transcription unavailable")
        return None

    try:
        filename = f"voice.{file_format}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                WHISPER_URL,
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                files={"file": (filename, io.BytesIO(audio_bytes), f"audio/{file_format}")},
                data={
                    "model": "whisper-1",
                    "language": "en",
                    "response_format": "text",
                },
                timeout=30.0,
            )

        if response.status_code == 200:
            text = response.text.strip()
            logger.info("Transcribed %d bytes of audio → %d chars", len(audio_bytes), len(text))
            return text
        else:
            logger.error("Whisper API returned %d: %s", response.status_code, response.text[:200])
            return None

    except httpx.TimeoutException:
        logger.error("Whisper API timed out")
        return None
    except Exception as exc:
        logger.error("Transcription failed: %s", exc)
        return None
