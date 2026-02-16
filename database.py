"""
Database Module for TrueValue AI
=================================
PostgreSQL persistence via asyncpg with connection pooling.

Tables:
  - users: User profiles, tiers, Stripe IDs, daily query tracking
  - conversations: Full query/response log for analytics
  - query_logs: Structured property query analytics
  - subscription_events: Tier change audit trail

Usage:
    from database import init_db, close_db, get_or_create_user, ...

    await init_db()          # call once at startup
    user = await get_or_create_user(123, "alice", "Alice")
    await close_db()         # call on shutdown
"""

import os
import json
import logging
from datetime import datetime, date
from typing import Optional

import asyncpg

logger = logging.getLogger("database")

# Module-level pool singleton
_pool: Optional[asyncpg.Pool] = None

# =====================================================
# SCHEMA DDL (idempotent — safe to run on every startup)
# =====================================================

SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS users (
    user_id        BIGINT PRIMARY KEY,
    telegram_username TEXT,
    first_name     TEXT,
    tier           TEXT NOT NULL DEFAULT 'free',
    stripe_customer_id    TEXT,
    stripe_subscription_id TEXT,
    joined_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    queries_today  INT NOT NULL DEFAULT 0,
    last_reset     DATE NOT NULL DEFAULT CURRENT_DATE,
    total_queries  BIGINT NOT NULL DEFAULT 0,
    platform       TEXT NOT NULL DEFAULT 'telegram'
);

CREATE TABLE IF NOT EXISTS conversations (
    id             BIGSERIAL PRIMARY KEY,
    user_id        BIGINT REFERENCES users(user_id),
    query          TEXT NOT NULL,
    response       TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    response_time_ms FLOAT,
    format         TEXT DEFAULT 'concise',
    tools_used     JSONB DEFAULT '[]'::jsonb,
    success        BOOLEAN DEFAULT TRUE,
    platform       TEXT DEFAULT 'telegram'
);

CREATE TABLE IF NOT EXISTS query_logs (
    id             BIGSERIAL PRIMARY KEY,
    user_id        BIGINT REFERENCES users(user_id),
    query_text     TEXT NOT NULL,
    property_zone  TEXT,
    property_type  TEXT,
    price_range    TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subscription_events (
    id             BIGSERIAL PRIMARY KEY,
    user_id        BIGINT REFERENCES users(user_id),
    event_type     TEXT NOT NULL,
    from_tier      TEXT,
    to_tier        TEXT,
    stripe_event_id TEXT,
    amount_aed     FLOAT DEFAULT 0,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS saved_properties (
    id             BIGSERIAL PRIMARY KEY,
    user_id        BIGINT NOT NULL REFERENCES users(user_id),
    property_data  JSONB NOT NULL,
    notes          TEXT,
    saved_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, (property_data->>'id'))
);

CREATE TABLE IF NOT EXISTS referrals (
    id              BIGSERIAL PRIMARY KEY,
    referrer_id     BIGINT NOT NULL REFERENCES users(user_id),
    referee_id      BIGINT NOT NULL REFERENCES users(user_id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    bonus_awarded   BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE(referee_id)
);

CREATE TABLE IF NOT EXISTS digest_preferences (
    user_id        BIGINT PRIMARY KEY REFERENCES users(user_id),
    frequency      TEXT NOT NULL DEFAULT 'weekly',
    zones          TEXT[] NOT NULL DEFAULT '{}',
    enabled        BOOLEAN NOT NULL DEFAULT TRUE,
    last_sent      TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_query_logs_user_id ON query_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_events_user_id ON subscription_events(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_user ON saved_properties(user_id);
CREATE INDEX IF NOT EXISTS idx_referral_referrer ON referrals(referrer_id);
"""

# Additional schema migrations (run after main DDL)
SCHEMA_MIGRATIONS = """
ALTER TABLE users ADD COLUMN IF NOT EXISTS bonus_queries INT NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_code TEXT;
"""


# =====================================================
# LIFECYCLE
# =====================================================

async def init_db(database_url: Optional[str] = None) -> None:
    """Initialise the connection pool and create tables if needed."""
    global _pool

    if _pool is not None:
        return  # already initialised

    url = database_url or os.getenv("DATABASE_URL", "")
    if not url or url == "postgresql://user:pass@localhost/dubai_estate":
        logger.warning("DATABASE_URL not configured — database features disabled")
        return

    try:
        _pool = await asyncpg.create_pool(url, min_size=2, max_size=10)
        async with _pool.acquire() as conn:
            await conn.execute(SCHEMA_DDL)
            # Run migrations for new columns (idempotent)
            for stmt in SCHEMA_MIGRATIONS.strip().split(";"):
                stmt = stmt.strip()
                if stmt:
                    try:
                        await conn.execute(stmt)
                    except Exception:
                        pass  # Column may already exist
        logger.info("Database initialised successfully")
    except Exception as exc:
        logger.error("Failed to initialise database: %s", exc)
        _pool = None


async def close_db() -> None:
    """Close the connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


def is_db_available() -> bool:
    """Check if the database pool is available."""
    return _pool is not None


# =====================================================
# USER OPERATIONS
# =====================================================

async def get_or_create_user(
    user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    platform: str = "telegram",
) -> Optional[dict]:
    """Upsert a user and return their record as a dict."""
    if not _pool:
        return None

    async with _pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO users (user_id, telegram_username, first_name, platform)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) DO UPDATE SET
                telegram_username = COALESCE($2, users.telegram_username),
                first_name = COALESCE($3, users.first_name)
            RETURNING *
            """,
            user_id, username, first_name, platform,
        )
        return dict(row) if row else None


async def get_user(user_id: int) -> Optional[dict]:
    """Fetch a user by ID."""
    if not _pool:
        return None

    async with _pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        return dict(row) if row else None


async def update_user_tier(
    user_id: int,
    tier: str,
    stripe_customer_id: Optional[str] = None,
    stripe_subscription_id: Optional[str] = None,
) -> Optional[dict]:
    """Update a user's subscription tier and optional Stripe IDs."""
    if not _pool:
        return None

    async with _pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            UPDATE users
            SET tier = $2,
                stripe_customer_id = COALESCE($3, stripe_customer_id),
                stripe_subscription_id = COALESCE($4, stripe_subscription_id)
            WHERE user_id = $1
            RETURNING *
            """,
            user_id, tier, stripe_customer_id, stripe_subscription_id,
        )
        return dict(row) if row else None


async def increment_query_count(user_id: int) -> Optional[dict]:
    """
    Increment queries_today (auto-resets on new day) and total_queries.
    Returns the updated user record.
    """
    if not _pool:
        return None

    async with _pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            UPDATE users
            SET queries_today = CASE
                    WHEN last_reset < CURRENT_DATE THEN 1
                    ELSE queries_today + 1
                END,
                last_reset = CURRENT_DATE,
                total_queries = total_queries + 1
            WHERE user_id = $1
            RETURNING *
            """,
            user_id,
        )
        return dict(row) if row else None


async def reset_daily_queries(user_id: int) -> None:
    """Manually reset a user's daily query counter."""
    if not _pool:
        return

    async with _pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET queries_today = 0, last_reset = CURRENT_DATE WHERE user_id = $1",
            user_id,
        )


async def get_remaining_queries(user_id: int, tier_limits: dict) -> int:
    """
    Return how many queries the user has left today.
    Returns -1 for unlimited tiers.
    """
    if not _pool:
        return 50  # fallback when DB is unavailable

    user = await get_user(user_id)
    if not user:
        return 50

    tier = user.get("tier", "free")
    limit = tier_limits.get(tier, {}).get("queries_per_day", 50)

    if limit == -1:
        return -1

    # Auto-reset if new day
    if user.get("last_reset") and user["last_reset"] < date.today():
        await reset_daily_queries(user_id)
        return limit

    return max(0, limit - user.get("queries_today", 0))


# =====================================================
# CONVERSATION LOGGING
# =====================================================

async def log_conversation(
    user_id: int,
    query: str,
    response: str,
    response_time_ms: float = 0,
    format_type: str = "concise",
    tools_used: list = None,
    success: bool = True,
    platform: str = "telegram",
) -> Optional[int]:
    """Log a conversation exchange. Returns the row ID."""
    if not _pool:
        return None

    async with _pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO conversations (user_id, query, response, response_time_ms, format, tools_used, success, platform)
            VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7, $8)
            RETURNING id
            """,
            user_id,
            query[:5000],
            response[:20000],
            response_time_ms,
            format_type,
            json.dumps(tools_used or []),
            success,
            platform,
        )
        return row["id"] if row else None


async def get_recent_conversations(user_id: int, limit: int = 10) -> list:
    """Get recent conversations for a user."""
    if not _pool:
        return []

    async with _pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, query, response, created_at, response_time_ms, tools_used, success
            FROM conversations
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """,
            user_id, limit,
        )
        return [dict(r) for r in rows]


# =====================================================
# QUERY ANALYTICS
# =====================================================

async def log_query_analytics(
    user_id: int,
    query_text: str,
    property_zone: Optional[str] = None,
    property_type: Optional[str] = None,
    price_range: Optional[str] = None,
) -> None:
    """Log structured query analytics."""
    if not _pool:
        return

    async with _pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO query_logs (user_id, query_text, property_zone, property_type, price_range)
            VALUES ($1, $2, $3, $4, $5)
            """,
            user_id, query_text[:1000], property_zone, property_type, price_range,
        )


# =====================================================
# SUBSCRIPTION EVENTS
# =====================================================

async def log_subscription_event(
    user_id: int,
    event_type: str,
    from_tier: Optional[str] = None,
    to_tier: Optional[str] = None,
    stripe_event_id: Optional[str] = None,
    amount_aed: float = 0,
) -> None:
    """Log a subscription lifecycle event."""
    if not _pool:
        return

    async with _pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO subscription_events (user_id, event_type, from_tier, to_tier, stripe_event_id, amount_aed)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            user_id, event_type, from_tier, to_tier, stripe_event_id, amount_aed,
        )


# =====================================================
# SAVED PROPERTIES / WATCHLIST
# =====================================================

async def save_property(user_id: int, property_data: dict, notes: str = None) -> Optional[int]:
    """Save a property to user's watchlist. Returns the row ID or None on conflict."""
    if not _pool:
        return None

    async with _pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO saved_properties (user_id, property_data, notes)
                VALUES ($1, $2::jsonb, $3)
                ON CONFLICT (user_id, (property_data->>'id')) DO UPDATE SET notes = COALESCE($3, saved_properties.notes)
                RETURNING id
                """,
                user_id, json.dumps(property_data), notes,
            )
            return row["id"] if row else None
        except Exception as exc:
            logger.error("save_property failed: %s", exc)
            return None


async def get_saved_properties(user_id: int) -> list:
    """Get all saved properties for a user."""
    if not _pool:
        return []

    async with _pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, property_data, notes, saved_at
            FROM saved_properties
            WHERE user_id = $1
            ORDER BY saved_at DESC
            """,
            user_id,
        )
        result = []
        for r in rows:
            data = r["property_data"]
            if isinstance(data, str):
                data = json.loads(data)
            result.append({
                "id": r["id"],
                "property_data": data,
                "notes": r["notes"],
                "saved_at": r["saved_at"].isoformat() if r["saved_at"] else None,
            })
        return result


async def remove_saved_property(user_id: int, property_id: str) -> bool:
    """Remove a property from watchlist by property_data->>'id'."""
    if not _pool:
        return False

    async with _pool.acquire() as conn:
        result = await conn.execute(
            """
            DELETE FROM saved_properties
            WHERE user_id = $1 AND property_data->>'id' = $2
            """,
            user_id, property_id,
        )
        return result != "DELETE 0"


async def count_saved_properties(user_id: int) -> int:
    """Count saved properties for a user."""
    if not _pool:
        return 0

    async with _pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT COUNT(*) as cnt FROM saved_properties WHERE user_id = $1",
            user_id,
        )
        return row["cnt"] if row else 0


# =====================================================
# REFERRAL SYSTEM
# =====================================================

async def get_or_create_referral_code(user_id: int) -> str:
    """Get or generate a referral code for a user."""
    if not _pool:
        return f"ref_{user_id}"

    async with _pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT referral_code FROM users WHERE user_id = $1",
            user_id,
        )
        if row and row["referral_code"]:
            return row["referral_code"]

        code = f"ref_{user_id}"
        await conn.execute(
            "UPDATE users SET referral_code = $2 WHERE user_id = $1",
            user_id, code,
        )
        return code


async def create_referral(referrer_id: int, referee_id: int) -> bool:
    """Create a referral link between two users. Returns True if new referral created."""
    if not _pool:
        return False

    async with _pool.acquire() as conn:
        try:
            await conn.execute(
                """
                INSERT INTO referrals (referrer_id, referee_id)
                VALUES ($1, $2)
                ON CONFLICT (referee_id) DO NOTHING
                """,
                referrer_id, referee_id,
            )
            return True
        except Exception as exc:
            logger.error("create_referral failed: %s", exc)
            return False


async def award_referral_bonus(referrer_id: int, referee_id: int, referrer_bonus: int = 10, referee_bonus: int = 5) -> None:
    """Award bonus queries to both referrer and referee."""
    if not _pool:
        return

    async with _pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "UPDATE users SET bonus_queries = bonus_queries + $2 WHERE user_id = $1",
                referrer_id, referrer_bonus,
            )
            await conn.execute(
                "UPDATE users SET bonus_queries = bonus_queries + $2 WHERE user_id = $1",
                referee_id, referee_bonus,
            )
            await conn.execute(
                "UPDATE referrals SET bonus_awarded = TRUE WHERE referrer_id = $1 AND referee_id = $2",
                referrer_id, referee_id,
            )


async def get_referral_stats(user_id: int) -> dict:
    """Get referral stats for a user."""
    if not _pool:
        return {"referral_count": 0, "total_bonus_earned": 0}

    async with _pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT COUNT(*) as cnt,
                   COALESCE(SUM(CASE WHEN bonus_awarded THEN 10 ELSE 0 END), 0) as bonus
            FROM referrals
            WHERE referrer_id = $1
            """,
            user_id,
        )
        return {
            "referral_count": row["cnt"] if row else 0,
            "total_bonus_earned": row["bonus"] if row else 0,
        }


# =====================================================
# DIGEST PREFERENCES
# =====================================================

async def set_digest_preference(user_id: int, frequency: str, zones: list) -> None:
    """Set or update digest preference for a user."""
    if not _pool:
        return

    async with _pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO digest_preferences (user_id, frequency, zones, enabled)
            VALUES ($1, $2, $3, TRUE)
            ON CONFLICT (user_id) DO UPDATE SET
                frequency = $2,
                zones = $3,
                enabled = TRUE
            """,
            user_id, frequency, zones,
        )


async def get_digest_subscribers(frequency: str) -> list:
    """Get all active digest subscribers for a given frequency."""
    if not _pool:
        return []

    async with _pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT user_id, zones, last_sent
            FROM digest_preferences
            WHERE frequency = $1 AND enabled = TRUE
            """,
            frequency,
        )
        return [{"user_id": r["user_id"], "zones": r["zones"], "last_sent": r["last_sent"]} for r in rows]


async def update_digest_sent(user_id: int) -> None:
    """Update the last_sent timestamp for a user's digest."""
    if not _pool:
        return

    async with _pool.acquire() as conn:
        await conn.execute(
            "UPDATE digest_preferences SET last_sent = NOW() WHERE user_id = $1",
            user_id,
        )


async def disable_digest(user_id: int) -> None:
    """Disable digest for a user."""
    if not _pool:
        return

    async with _pool.acquire() as conn:
        await conn.execute(
            "UPDATE digest_preferences SET enabled = FALSE WHERE user_id = $1",
            user_id,
        )
