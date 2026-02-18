"""
Admin Dashboard — API endpoints + HTML serving
===============================================
Provides /admin routes for the TrueValue business dashboard.
"""

import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

import database
from database import is_db_available
from observability import metrics_tracker, user_analytics

router = APIRouter(prefix="/admin", tags=["admin"])


def _safe_float(val, default=0):
    """Convert a value to float safely (handles strings, None, etc.)."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


# ── Helper to run raw SQL ──────────────────────────────────

async def _fetch(sql: str, *args):
    """Run a SELECT and return list[dict]."""
    if not is_db_available():
        return []
    async with database._pool.acquire() as conn:
        rows = await conn.fetch(sql, *args)
        return [dict(r) for r in rows]


async def _fetchval(sql: str, *args):
    """Run a SELECT and return a single scalar value."""
    if not is_db_available():
        return 0
    async with database._pool.acquire() as conn:
        return await conn.fetchval(sql, *args)


# ══════════════════════════════════════════════════════════
#  API ENDPOINTS
# ══════════════════════════════════════════════════════════

@router.get("/api/overview")
async def overview():
    """Top-line KPIs for the dashboard header."""
    total_users = await _fetchval("SELECT COUNT(*) FROM users")
    users_today = await _fetchval(
        "SELECT COUNT(*) FROM users WHERE joined_at >= CURRENT_DATE"
    )
    users_7d = await _fetchval(
        "SELECT COUNT(*) FROM users WHERE joined_at >= NOW() - INTERVAL '7 days'"
    )

    total_queries = await _fetchval("SELECT COALESCE(SUM(total_queries), 0) FROM users")
    queries_today = await _fetchval(
        "SELECT COUNT(*) FROM conversations WHERE created_at >= CURRENT_DATE"
    )
    queries_7d = await _fetchval(
        "SELECT COUNT(*) FROM conversations WHERE created_at >= NOW() - INTERVAL '7 days'"
    )

    tier_dist = await _fetch(
        "SELECT tier, COUNT(*) AS cnt FROM users GROUP BY tier ORDER BY cnt DESC"
    )

    # Cost data from in-memory metrics
    summary = metrics_tracker.get_summary()

    return {
        "total_users": total_users,
        "users_today": users_today,
        "users_7d": users_7d,
        "total_queries": total_queries,
        "queries_today": queries_today,
        "queries_7d": queries_7d,
        "total_cost_usd": round(_safe_float(summary.get("total_cost_usd", 0)), 4),
        "avg_cost_per_query": round(_safe_float(summary.get("avg_cost_per_query", 0)), 4),
        "success_rate": round(_safe_float(summary.get("success_rate", 0)), 2),
        "tier_distribution": {r["tier"]: r["cnt"] for r in tier_dist},
        "funnel": user_analytics.get_funnel(),
    }


@router.get("/api/users")
async def users_list():
    """All users with key stats."""
    rows = await _fetch("""
        SELECT
            u.user_id,
            u.telegram_username,
            u.first_name,
            u.tier,
            u.joined_at,
            u.total_queries,
            u.queries_today,
            u.bonus_queries,
            u.referral_code,
            (SELECT COUNT(*) FROM saved_properties sp WHERE sp.user_id = u.user_id) AS saved_count,
            (SELECT COUNT(*) FROM referrals r WHERE r.referrer_id = u.user_id) AS referral_count
        FROM users u
        ORDER BY u.joined_at DESC
    """)
    # Serialise timestamps
    for r in rows:
        if r.get("joined_at"):
            r["joined_at"] = r["joined_at"].isoformat()
    return rows


@router.get("/api/users/{user_id}")
async def user_detail(user_id: int):
    """Single user deep dive."""
    user = await _fetch("SELECT * FROM users WHERE user_id = $1", user_id)
    if not user:
        return {"error": "User not found"}
    user = user[0]
    if user.get("joined_at"):
        user["joined_at"] = user["joined_at"].isoformat()
    if user.get("last_reset"):
        user["last_reset"] = str(user["last_reset"])

    convos = await _fetch("""
        SELECT query, created_at, response_time_ms, tools_used, success
        FROM conversations
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT 30
    """, user_id)
    for c in convos:
        if c.get("created_at"):
            c["created_at"] = c["created_at"].isoformat()

    in_mem = metrics_tracker.get_user_stats(str(user_id))

    return {
        "user": user,
        "recent_queries": convos,
        "metrics": in_mem,
    }


@router.get("/api/queries")
async def query_analytics():
    """Query volume, trends, and breakdown."""
    # Daily query counts (last 30 days)
    daily = await _fetch("""
        SELECT DATE(created_at) AS day, COUNT(*) AS cnt
        FROM conversations
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY DATE(created_at)
        ORDER BY day
    """)
    for r in daily:
        r["day"] = str(r["day"])

    # Hourly distribution
    hourly = await _fetch("""
        SELECT EXTRACT(HOUR FROM created_at)::int AS hour, COUNT(*) AS cnt
        FROM conversations
        GROUP BY hour
        ORDER BY hour
    """)

    # Top users by queries
    top_users = await _fetch("""
        SELECT u.user_id, u.telegram_username, u.first_name, u.tier, u.total_queries
        FROM users u
        ORDER BY u.total_queries DESC
        LIMIT 15
    """)

    # Average response time
    avg_rt = await _fetchval(
        "SELECT ROUND(AVG(response_time_ms)::numeric, 0) FROM conversations WHERE success = TRUE"
    )

    # Success/failure
    success_fail = await _fetch("""
        SELECT success, COUNT(*) AS cnt
        FROM conversations
        GROUP BY success
    """)

    return {
        "daily_volume": daily,
        "hourly_distribution": hourly,
        "top_users": top_users,
        "avg_response_time_ms": avg_rt or 0,
        "success_failure": {str(r["success"]): r["cnt"] for r in success_fail},
    }


@router.get("/api/tools")
async def tool_usage():
    """Which AI tools are used most."""
    # From conversations.tools_used (JSONB array)
    rows = await _fetch("""
        SELECT tool, COUNT(*) AS cnt
        FROM conversations, jsonb_array_elements_text(tools_used) AS tool
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY tool
        ORDER BY cnt DESC
    """)

    # Also get from in-memory metrics
    summary = metrics_tracker.get_summary()

    return {
        "tool_usage_30d": rows,
        "in_memory_tools": summary.get("most_used_tools", {}),
    }


@router.get("/api/costs")
async def cost_analytics():
    """AI cost breakdown."""
    summary = metrics_tracker.get_summary()

    # Per-user cost from in-memory
    top_cost_users = sorted(
        [
            {"user_id": uid, **stats}
            for uid, stats in (
                (uid, metrics_tracker.get_user_stats(uid))
                for uid in set(
                    q.get("user_id", "")
                    for q in getattr(metrics_tracker, "_queries", [])
                )
                if uid
            )
            if stats.get("cost_usd", 0) > 0
        ],
        key=lambda x: x.get("cost_usd", 0),
        reverse=True,
    )[:10]

    return {
        "total_cost_usd": round(_safe_float(summary.get("total_cost_usd", 0)), 4),
        "avg_cost_per_query": round(_safe_float(summary.get("avg_cost_per_query", 0)), 6),
        "total_queries_tracked": summary.get("total_queries", 0),
        "top_cost_users": top_cost_users,
        "response_times": summary.get("response_times", {}),
    }


@router.get("/api/revenue")
async def revenue():
    """Subscription events and revenue."""
    events = await _fetch("""
        SELECT event_type, to_tier, amount_aed, created_at, user_id
        FROM subscription_events
        ORDER BY created_at DESC
        LIMIT 50
    """)
    for e in events:
        if e.get("created_at"):
            e["created_at"] = e["created_at"].isoformat()

    total_revenue = await _fetchval(
        "SELECT COALESCE(SUM(amount_aed), 0) FROM subscription_events WHERE event_type = 'checkout_completed'"
    )

    mrr = await _fetchval("""
        SELECT COALESCE(SUM(
            CASE tier
                WHEN 'basic' THEN 99
                WHEN 'pro' THEN 299
                WHEN 'enterprise' THEN 999
                ELSE 0
            END
        ), 0)
        FROM users
        WHERE tier != 'free'
    """)

    paid_users = await _fetchval("SELECT COUNT(*) FROM users WHERE tier != 'free'")

    return {
        "total_revenue_aed": float(total_revenue),
        "mrr_aed": float(mrr),
        "paid_users": paid_users,
        "recent_events": events,
    }


@router.get("/api/referrals")
async def referral_stats():
    """Referral program analytics."""
    total = await _fetchval("SELECT COUNT(*) FROM referrals")
    bonuses = await _fetchval("SELECT COUNT(*) FROM referrals WHERE bonus_awarded = TRUE")

    top_referrers = await _fetch("""
        SELECT r.referrer_id, u.telegram_username, u.first_name, COUNT(*) AS referred,
               SUM(CASE WHEN r.bonus_awarded THEN 1 ELSE 0 END) AS bonuses
        FROM referrals r
        JOIN users u ON u.user_id = r.referrer_id
        GROUP BY r.referrer_id, u.telegram_username, u.first_name
        ORDER BY referred DESC
        LIMIT 10
    """)

    return {
        "total_referrals": total,
        "bonuses_awarded": bonuses,
        "top_referrers": top_referrers,
    }


@router.get("/api/engagement")
async def engagement():
    """User engagement metrics."""
    # Users active in last 24h
    active_24h = await _fetchval("""
        SELECT COUNT(DISTINCT user_id) FROM conversations
        WHERE created_at >= NOW() - INTERVAL '24 hours'
    """)

    # Users active in last 7 days
    active_7d = await _fetchval("""
        SELECT COUNT(DISTINCT user_id) FROM conversations
        WHERE created_at >= NOW() - INTERVAL '7 days'
    """)

    # Digest subscribers
    digest_subs = await _fetch("""
        SELECT frequency, COUNT(*) AS cnt
        FROM digest_preferences
        WHERE enabled = TRUE
        GROUP BY frequency
    """)

    # Saved properties count
    total_saved = await _fetchval("SELECT COUNT(*) FROM saved_properties")

    # Avg queries per user (active users only)
    avg_queries = await _fetchval("""
        SELECT ROUND(AVG(total_queries)::numeric, 1)
        FROM users WHERE total_queries > 0
    """)

    # User signups over last 14 days
    signups_daily = await _fetch("""
        SELECT DATE(joined_at) AS day, COUNT(*) AS cnt
        FROM users
        WHERE joined_at >= NOW() - INTERVAL '14 days'
        GROUP BY DATE(joined_at)
        ORDER BY day
    """)
    for r in signups_daily:
        r["day"] = str(r["day"])

    return {
        "active_24h": active_24h,
        "active_7d": active_7d,
        "digest_subscribers": {r["frequency"]: r["cnt"] for r in digest_subs},
        "total_saved_properties": total_saved,
        "avg_queries_per_user": float(avg_queries or 0),
        "signups_daily": signups_daily,
    }


# ══════════════════════════════════════════════════════════
#  HTML DASHBOARD (served as a single page)
# ══════════════════════════════════════════════════════════

@router.get("/", response_class=HTMLResponse)
async def dashboard_page():
    """Serve the admin dashboard HTML."""
    html_path = os.path.join(os.path.dirname(__file__), "templates", "admin.html")
    with open(html_path, "r") as f:
        return HTMLResponse(content=f.read())
