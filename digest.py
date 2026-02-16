"""
Market Digest Generator for TrueValue AI
==========================================
Generates compact market digest messages by pulling data from existing tools.
Used by the scheduler to send periodic updates to subscribed users.
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger("digest")


async def generate_digest(zones: list[str]) -> str:
    """
    Generate a market digest for the given zones.
    Pulls data from get_market_trends and get_supply_pipeline for each zone.
    Returns a formatted Telegram-friendly message.
    """
    from main import get_market_trends, get_supply_pipeline

    sections = []
    sections.append(f"📰 *TrueValue Market Digest*")
    sections.append(f"📅 {datetime.now().strftime('%B %d, %Y')}\n")

    for zone in zones:
        try:
            # Fetch market data
            trends = await get_market_trends(zone, "for-sale")
            pipeline = await get_supply_pipeline(zone)

            zone_name = pipeline.get("zone", zone)
            avg_psf = trends.get("avg_price_per_sqft_aed", 0)
            gross_yield = trends.get("gross_yield_estimate_pct")
            risk_level = pipeline.get("risk_level", "UNKNOWN")
            units_pipeline = pipeline.get("units_pipeline")

            # Risk emoji
            risk_emoji = {"LOW": "🟢", "MODERATE": "🟡", "HIGH": "🔴", "VERY HIGH": "🔴"}.get(risk_level, "⚪")

            section = f"━━━━━━━━━━━━━━━\n"
            section += f"📍 *{zone_name}*\n"
            if avg_psf:
                section += f"  💰 Avg PSF: AED {avg_psf:,.0f}\n"
            if gross_yield:
                section += f"  📈 Gross Yield: {gross_yield}%\n"
            section += f"  {risk_emoji} Supply Risk: {risk_level}\n"
            if units_pipeline:
                section += f"  🏗️ Pipeline: {units_pipeline:,} units\n"

            # Market activity
            activity = trends.get("market_activity", "N/A")
            section += f"  📊 Activity: {activity}\n"

            # Recommendation snippet
            rec = pipeline.get("recommendation", "")
            if rec:
                section += f"  💡 _{rec[:80]}{'...' if len(rec) > 80 else ''}_\n"

            sections.append(section)

        except Exception as exc:
            logger.warning("Failed to generate digest for zone '%s': %s", zone, exc)
            sections.append(f"📍 *{zone}* — data unavailable\n")

    sections.append("━━━━━━━━━━━━━━━")
    sections.append("_Powered by TrueValue AI — your institutional-grade Dubai analyst_")
    sections.append("Use /digest\\_off to unsubscribe")

    return "\n".join(sections)


async def start_digest_scheduler():
    """
    Background scheduler that checks for digest subscribers and sends updates.
    Runs every hour, checks if subscribers are due for their digest.
    """
    import asyncio

    logger.info("Digest scheduler started")

    while True:
        try:
            await _run_digest_cycle()
        except Exception as exc:
            logger.error("Digest cycle failed: %s", exc)

        # Sleep for 1 hour between checks
        await asyncio.sleep(3600)


async def _run_digest_cycle():
    """Single digest cycle — check subscribers and send due digests."""
    from database import get_digest_subscribers, update_digest_sent, is_db_available
    import os
    import httpx

    if not is_db_available():
        return

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        return

    now = datetime.now()

    for frequency in ("daily", "weekly"):
        subscribers = await get_digest_subscribers(frequency)

        for sub in subscribers:
            user_id = sub["user_id"]
            zones = sub["zones"]
            last_sent = sub["last_sent"]

            # Check if due
            if last_sent:
                if frequency == "daily" and (now - last_sent) < timedelta(hours=23):
                    continue
                if frequency == "weekly" and (now - last_sent) < timedelta(days=6, hours=23):
                    continue

            if not zones:
                continue

            try:
                digest_text = await generate_digest(zones)

                # Send via Telegram Bot API
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        json={
                            "chat_id": user_id,
                            "text": digest_text,
                            "parse_mode": "Markdown",
                        },
                        timeout=15.0,
                    )

                await update_digest_sent(user_id)
                logger.info("Digest sent to user %s (%s, %d zones)", user_id, frequency, len(zones))

            except Exception as exc:
                logger.warning("Failed to send digest to user %s: %s", user_id, exc)
