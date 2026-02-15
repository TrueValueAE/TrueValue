"""
WhatsApp Bot for TrueValue AI
===============================
Handles incoming WhatsApp messages via Twilio webhook.
Supports text queries and voice message transcription.
"""

import os
import sys
import logging
from typing import Optional

import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.bot_core import (
    register_user, check_rate_limit, process_query, SUBSCRIPTION_TIERS,
)
from transcription import transcribe_voice, is_transcription_available

logger = logging.getLogger("whatsapp_bot")

# Twilio config
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

MAX_WHATSAPP_LENGTH = 4096


def _phone_to_user_id(phone: str) -> int:
    """Convert phone number to a numeric user ID (hash)."""
    # Use last 10 digits to create a stable ID
    digits = "".join(c for c in phone if c.isdigit())[-10:]
    return int(digits) if digits else hash(phone) % (10**10)


async def handle_whatsapp_message(
    from_number: str,
    body: str,
    media_url: Optional[str] = None,
    media_content_type: Optional[str] = None,
) -> str:
    """
    Process an incoming WhatsApp message.

    Args:
        from_number: Sender's WhatsApp number (e.g. whatsapp:+971...)
        body: Text body of the message
        media_url: URL of attached media (voice note, image, etc.)
        media_content_type: MIME type of attached media

    Returns:
        Response text to send back via Twilio TwiML.
    """
    user_id = _phone_to_user_id(from_number)
    username = from_number.replace("whatsapp:", "")

    # Register user
    user_data, is_new = await register_user(
        user_id=user_id,
        username=username,
        platform="whatsapp",
    )

    if is_new:
        welcome = (
            "Welcome to TrueValue AI! I'm your Dubai real estate analyst.\n\n"
            "Ask me anything about Dubai properties:\n"
            "- 'Find 2BR apartments in Marina under 2M'\n"
            "- 'Analyze Boulevard Point Business Bay'\n"
            "- 'What's the chiller cost for 1500 sqft in Marina?'\n\n"
            "You can also send voice messages!"
        )
        return welcome

    # Check rate limit
    allowed, remaining = await check_rate_limit(user_id)
    if not allowed:
        tier = user_data.get("tier", "free")
        return (
            f"You've reached your daily query limit ({SUBSCRIPTION_TIERS[tier]['queries_per_day']} queries).\n"
            f"Upgrade for more queries!"
        )

    # Handle voice messages
    query = body
    if media_url and media_content_type and "audio" in media_content_type:
        if is_transcription_available():
            try:
                # Download audio from Twilio
                async with httpx.AsyncClient() as client:
                    audio_resp = await client.get(
                        media_url,
                        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                        timeout=30.0,
                    )
                if audio_resp.status_code == 200:
                    fmt = "ogg" if "ogg" in media_content_type else "mp3"
                    transcribed = await transcribe_voice(audio_resp.content, fmt)
                    if transcribed:
                        query = transcribed
                    else:
                        return "Sorry, I couldn't understand the voice message. Please try again or send text."
                else:
                    return "Could not download the voice message. Please try sending text instead."
            except Exception as exc:
                logger.error("Voice processing error: %s", exc)
                return "Error processing voice message. Please send text instead."
        else:
            return "Voice messages are not available yet. Please send text instead."

    if not query or not query.strip():
        return "Please send me a question about Dubai real estate!"

    # Process the query
    try:
        response_text, tools_used = await process_query(
            user_id=user_id,
            query=query,
            platform="whatsapp",
            username=username,
        )

        # Truncate for WhatsApp
        if len(response_text) > MAX_WHATSAPP_LENGTH:
            response_text = response_text[:MAX_WHATSAPP_LENGTH - 100] + (
                "\n\n---\n(Response truncated. Send 'Full Report' for complete analysis.)"
            )

        return response_text

    except Exception as exc:
        logger.error("WhatsApp query error: %s", exc)
        return "Sorry, something went wrong. Please try again."
