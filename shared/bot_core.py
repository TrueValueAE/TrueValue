"""
Shared Bot Core — Common Logic for Telegram and WhatsApp
=========================================================
Centralizes user management, rate limiting, query processing,
and conversation logging for all bot platforms.
"""

import os
import sys
import time
import logging
from typing import Optional, Tuple

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import handle_query
from conversation import ConversationStore, is_followup
from database import (
    is_db_available, get_or_create_user, get_user,
    increment_query_count, log_conversation,
)
from observability import (
    user_analytics, record_user_signup, record_followup_detected,
    update_active_conversations,
)

logger = logging.getLogger("bot_core")

# Subscription tier limits
SUBSCRIPTION_TIERS = {
    "free": {"name": "Free", "price": 0, "queries_per_day": 50},
    "basic": {"name": "Basic", "price": 99, "queries_per_day": 20},
    "pro": {"name": "Professional", "price": 299, "queries_per_day": 100},
    "enterprise": {"name": "Enterprise", "price": 999, "queries_per_day": -1},
}

# Shared conversation store
conversation_store = ConversationStore()


async def register_user(
    user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    platform: str = "telegram",
) -> Tuple[dict, bool]:
    """
    Register or fetch a user. Returns (user_data, is_new).
    Falls back to a synthetic dict if DB is unavailable.
    """
    if is_db_available():
        existing = await get_user(user_id)
        is_new = existing is None
        user = await get_or_create_user(user_id, username, first_name, platform)
        if is_new and user:
            user_analytics.track_event(
                user_id=str(user_id),
                event="user_signup",
                properties={"username": username, "first_name": first_name, "platform": platform},
            )
            record_user_signup("free")
            logger.info("New user signup: %s (%s) on %s", user_id, username, platform)
        return user or _fallback_user(user_id), is_new
    else:
        return _fallback_user(user_id), False


def _fallback_user(user_id: int) -> dict:
    """Synthetic user dict when DB is unavailable."""
    return {
        "user_id": user_id,
        "tier": "free",
        "queries_today": 0,
        "total_queries": 0,
    }


async def check_rate_limit(user_id: int) -> Tuple[bool, int]:
    """
    Check if user has queries remaining.
    Returns (allowed, remaining).
    """
    if is_db_available():
        user = await get_user(user_id)
        if not user:
            return True, 50

        tier = user.get("tier", "free")
        limit = SUBSCRIPTION_TIERS.get(tier, {}).get("queries_per_day", 50)

        if limit == -1:
            return True, -1

        from datetime import date
        if user.get("last_reset") and user["last_reset"] < date.today():
            # Will be reset on next increment
            return True, limit

        used = user.get("queries_today", 0)
        remaining = max(0, limit - used)
        return remaining > 0, remaining
    else:
        return True, 50


async def process_query(
    user_id: int,
    query: str,
    platform: str = "telegram",
    username: Optional[str] = None,
) -> Tuple[str, list]:
    """
    Process a user query end-to-end.
    Returns (response_text, tools_used).
    """
    uid = str(user_id)
    start_time = time.time()

    # Detect follow-up
    followup = is_followup(query, conversation_store.has_session(uid))
    record_followup_detected(followup)
    conv_context = conversation_store.get_context(uid) if followup else None

    # Execute query
    result = await handle_query(query, user_id=uid, conversation_context=conv_context)
    response_text = result.response if hasattr(result, "response") else str(result)
    tools_used = result.tools_used if hasattr(result, "tools_used") else []

    # Update conversation store
    conversation_store.update(uid, query, response_text)
    update_active_conversations(conversation_store.active_session_count())

    # Increment usage and log
    elapsed_ms = (time.time() - start_time) * 1000
    if is_db_available():
        await increment_query_count(user_id)
        await log_conversation(
            user_id=user_id,
            query=query,
            response=response_text,
            response_time_ms=elapsed_ms,
            tools_used=tools_used,
            platform=platform,
        )

    return response_text, tools_used
