#!/usr/bin/env python3
"""
Dubai Estate Telegram Bot
Direct integration with main.py analysis engine.
Persistent user storage via database.py (Step 2).
"""

import os
import sys
import asyncio
import logging
import time
from datetime import datetime, date
from typing import Dict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ChatAction
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the main analysis engine
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import handle_query
from conversation import ConversationStore, is_followup

# Database imports (Step 2)
from database import (
    init_db, close_db, is_db_available,
    get_or_create_user, get_user, increment_query_count,
    log_conversation, reset_daily_queries, log_subscription_event,
    save_property, get_saved_properties, remove_saved_property, count_saved_properties,
    get_or_create_referral_code, create_referral, award_referral_bonus, get_referral_stats,
    set_digest_preference, disable_digest,
)

# Payments import (Step 4)
from payments import (
    create_checkout_session, create_customer_portal_session,
    is_stripe_configured,
)

# Transcription import (Step 8)
from transcription import transcribe_voice, is_transcription_available

# Import observability
from observability import (
    setup_json_logging,
    log_user_error,
    user_analytics,
    record_command_metrics,
    record_user_signup,
    record_subscription_upgrade,
    record_query_limit_hit,
    record_followup_detected,
    record_conversation_reset,
    update_active_conversations,
)

# Set up logging for bot
bot_logger = setup_json_logging("telegram_bot")

# Subscription tiers
SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Free",
        "price": 0,
        "queries_per_day": 50,
        "features": ["Basic property search", "Simple analysis", "Limited results"],
    },
    "basic": {
        "name": "Basic",
        "price": 99,
        "queries_per_day": 20,
        "features": [
            "Advanced property search",
            "Chiller cost analysis",
            "Market trends",
            "ROI calculator",
        ],
    },
    "pro": {
        "name": "Professional",
        "price": 299,
        "queries_per_day": 100,
        "features": [
            "All Basic features",
            "Institutional reports (PDF)",
            "Price predictions",
            "Portfolio tracking",
            "Priority support",
            "API access",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 999,
        "queries_per_day": -1,
        "features": [
            "All Pro features",
            "Unlimited queries",
            "White-label reports",
            "CRM integration",
            "Dedicated support",
            "Custom analytics",
            "Team accounts",
        ],
    },
}


class TelegramBotServer:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")

        self.admin_ids = os.getenv("TELEGRAM_ADMIN_IDS", "").split(",")

        # In-memory fallback for when DB is unavailable
        self._users_fallback = {}

        # Conversation memory for follow-up detection
        self.conversation_store = ConversationStore()

        self.application = Application.builder().token(self.bot_token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Setup Telegram bot command handlers"""
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("search", self.cmd_search))
        self.application.add_handler(CommandHandler("analyze", self.cmd_analyze))
        self.application.add_handler(CommandHandler("subscribe", self.cmd_subscribe))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("trends", self.cmd_trends))
        self.application.add_handler(CommandHandler("compare", self.cmd_compare))
        self.application.add_handler(CommandHandler("new", self.cmd_new))
        self.application.add_handler(CommandHandler("manage", self.cmd_manage))
        self.application.add_handler(CommandHandler("reset_limit", self.cmd_reset_limit))
        self.application.add_handler(CommandHandler("save", self.cmd_save))
        self.application.add_handler(CommandHandler("watchlist", self.cmd_watchlist))
        self.application.add_handler(CommandHandler("remove", self.cmd_remove))
        self.application.add_handler(CommandHandler("referral", self.cmd_referral))
        self.application.add_handler(CommandHandler("digest", self.cmd_digest))
        self.application.add_handler(CommandHandler("digest_off", self.cmd_digest_off))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))

        # Voice message handler (Step 8)
        self.application.add_handler(
            MessageHandler(filters.VOICE | filters.AUDIO, self.handle_voice)
        )

        # Handle all text messages as property queries
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    # =====================================================
    # USER DATA HELPERS (DB-backed with in-memory fallback)
    # =====================================================

    async def _get_user_data(self, user_id: int) -> dict:
        """Get user data from DB or fallback."""
        if is_db_available():
            user = await get_user(user_id)
            if user:
                return user
        # Fallback
        return self._users_fallback.get(user_id, {
            "user_id": user_id,
            "tier": "free",
            "queries_today": 0,
            "last_reset": date.today(),
            "total_queries": 0,
        })

    async def _get_user_tier(self, user_id: int) -> str:
        """Get user's subscription tier."""
        data = await self._get_user_data(user_id)
        return data.get("tier", "free")

    async def check_query_limit(self, user_id: int) -> bool:
        """Check if user has queries remaining."""
        user_data = await self._get_user_data(user_id)
        tier = user_data.get("tier", "free")
        tier_info = SUBSCRIPTION_TIERS[tier]

        if tier_info["queries_per_day"] == -1:
            return True

        # Reset daily counter if needed
        last_reset = user_data.get("last_reset")
        today = date.today()
        queries_today = user_data.get("queries_today", 0)

        if last_reset and last_reset < today:
            queries_today = 0
            if is_db_available():
                await reset_daily_queries(user_id)
            elif user_id in self._users_fallback:
                self._users_fallback[user_id]["queries_today"] = 0
                self._users_fallback[user_id]["last_reset"] = today

        has_queries = queries_today < tier_info["queries_per_day"]

        if not has_queries:
            user_analytics.track_event(
                user_id=str(user_id),
                event='query_limit_hit',
                properties={'tier': tier, 'queries_used': queries_today}
            )
            record_query_limit_hit(tier)

        return has_queries

    async def get_remaining_queries(self, user_id: int) -> int:
        """Get remaining queries for today (includes bonus queries from referrals)."""
        user_data = await self._get_user_data(user_id)
        tier = user_data.get("tier", "free")
        tier_info = SUBSCRIPTION_TIERS[tier]

        if tier_info["queries_per_day"] == -1:
            return -1

        queries_today = user_data.get("queries_today", 0)
        last_reset = user_data.get("last_reset")
        if last_reset and last_reset < date.today():
            queries_today = 0

        bonus = user_data.get("bonus_queries", 0)
        return max(0, tier_info["queries_per_day"] + bonus - queries_today)

    async def increment_usage(self, user_id: int):
        """Increment query usage."""
        if is_db_available():
            await increment_query_count(user_id)
        elif user_id in self._users_fallback:
            self._users_fallback[user_id]["queries_today"] = (
                self._users_fallback[user_id].get("queries_today", 0) + 1
            )

    # =====================================================
    # COMMANDS
    # =====================================================

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message and registration"""
        user_id = update.effective_user.id
        username = update.effective_user.username
        first_name = update.effective_user.first_name

        record_command_metrics('start', str(user_id))

        # Register user in DB (Step 2)
        is_new = True
        if is_db_available():
            existing = await get_user(user_id)
            is_new = existing is None
            await get_or_create_user(user_id, username, first_name)
        else:
            is_new = user_id not in self._users_fallback
            if is_new:
                self._users_fallback[user_id] = {
                    "user_id": user_id,
                    "tier": "free",
                    "joined": datetime.now().isoformat(),
                    "queries_today": 0,
                    "last_reset": date.today(),
                    "total_queries": 0,
                }

        # Handle referral code from deep link: /start ref_XXXX
        if is_new and context.args and is_db_available():
            arg = context.args[0]
            if arg.startswith("ref_"):
                try:
                    referrer_id = int(arg[4:])
                    if referrer_id != user_id:
                        created = await create_referral(referrer_id, user_id)
                        if created:
                            await award_referral_bonus(referrer_id, user_id)
                            bot_logger.info("Referral: %s referred by %s", user_id, referrer_id)
                except (ValueError, Exception) as exc:
                    bot_logger.debug("Referral processing failed: %s", exc)

        if is_new:
            user_analytics.track_event(
                user_id=str(user_id),
                event='user_signup',
                properties={'username': username, 'first_name': first_name}
            )
            record_user_signup('free')
            bot_logger.info("New user signup", extra={
                'user_id': str(user_id), 'username': username, 'tier': 'free'
            })

        tier = await self._get_user_tier(user_id)
        remaining = await self.get_remaining_queries(user_id)

        welcome_msg = f"""
🏢 *Welcome to Dubai Estate AI!*

I'm your AI-powered real estate analyst for the Dubai property market.

🎯 *What I Can Do:*
• Search properties across all platforms
• Analyze investment potential with institutional-grade metrics
• Track chiller costs and hidden fees (our secret weapon!)
• Identify red flags and building issues
• Calculate ROI and rental yields
• Compare properties side-by-side
• Monitor market trends

📊 *Your Plan:* {SUBSCRIPTION_TIERS[tier]['name']}
📈 *Queries Left Today:* {remaining if remaining >= 0 else 'Unlimited'}

💡 *Quick Start:*
Just send me a message like:
• "Find 2BR apartments in Marina under 2M"
• "Analyze Boulevard Point Business Bay"
• "Compare Marina Gate vs Princess Tower"
• "Calculate chiller cost for 1500 sqft Empower property"

🎤 *Voice messages supported!* Just record and send.

Type /help for all commands or /subscribe to upgrade!
        """

        await update.message.reply_text(welcome_msg, parse_mode="Markdown")

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        record_command_metrics('help', str(update.effective_user.id))
        help_msg = """
📚 *Available Commands:*

*Analysis:*
/search - Search for properties
/analyze - Deep analysis of a specific property
/compare - Compare multiple properties
/trends - Get market trends for a zone

*Watchlist:*
/save <id> - Save a property to your watchlist
/watchlist - View saved properties
/remove <id> - Remove from watchlist

*Account:*
/subscribe - View and upgrade subscription plans
/manage - Manage your subscription
/status - Check your account status
/referral - Get your referral link & earn bonus queries

*Digest:*
/digest <zones> - Subscribe to market digest
/digest\\_off - Unsubscribe from digest

/new - Start a fresh conversation

*Natural Language:*
Just type naturally — I understand questions like:
• "What's the best investment in JBR under 3M?"
• "Calculate mortgage for 2M property"
• "Show DLD transactions in Dubai Marina"
• "What are actual rents for 1BR in Business Bay?"

🎤 Voice messages supported!
💡 Follow-up questions work!
        """

        await update.message.reply_text(help_msg, parse_mode="Markdown")

    async def cmd_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Search properties"""
        user_id = update.effective_user.id
        record_command_metrics('search', str(user_id))

        if not await self.check_query_limit(user_id):
            await self.send_upgrade_message(update)
            return

        query = " ".join(context.args) if context.args else ""
        if not query:
            await update.message.reply_text(
                "Please provide search criteria.\nExample: /search Marina 2BR under 2M"
            )
            return

        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            uid = str(user_id)
            search_query = f"Search for properties: {query}. Return top 5 results with key metrics."
            start = time.time()
            result = await handle_query(search_query, user_id=uid)
            elapsed = (time.time() - start) * 1000
            await self.increment_usage(user_id)
            response_text = result.response if hasattr(result, 'response') else str(result)
            self.conversation_store.update(uid, search_query, response_text)
            update_active_conversations(self.conversation_store.active_session_count())
            # Log to DB (Step 2)
            if is_db_available():
                await log_conversation(user_id, search_query, response_text,
                                       response_time_ms=elapsed,
                                       tools_used=result.tools_used if hasattr(result, 'tools_used') else [])
            await self.send_split_message(update, response_text)
        except Exception as e:
            error_msg = self.format_error_message(e, user_id=str(user_id), query=query)
            try:
                await update.message.reply_text(error_msg, parse_mode="Markdown")
            except:
                await update.message.reply_text(error_msg)

    async def cmd_analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze a specific property"""
        user_id = update.effective_user.id

        if not await self.check_query_limit(user_id):
            await self.send_upgrade_message(update)
            return

        property_query = " ".join(context.args) if context.args else ""
        if not property_query:
            await update.message.reply_text(
                "Please specify a property.\nExample: /analyze Marina Gate Tower 1"
            )
            return

        progress_msg = await update.message.reply_text(
            "🔍 Analyzing...\n⏱️ This will take 30-60 seconds"
        )

        try:
            full_query = f"Analyze this property: {property_query}"
            uid = str(user_id)
            start = time.time()
            result = await handle_query(full_query, user_id=uid)
            elapsed = (time.time() - start) * 1000
            await self.increment_usage(user_id)
            response_text = result.response if hasattr(result, 'response') else str(result)

            try:
                await progress_msg.delete()
            except:
                pass

            self.conversation_store.update(uid, full_query, response_text)
            update_active_conversations(self.conversation_store.active_session_count())

            if is_db_available():
                await log_conversation(user_id, full_query, response_text,
                                       response_time_ms=elapsed,
                                       tools_used=result.tools_used if hasattr(result, 'tools_used') else [])

            # Interactive buttons
            keyboard = [
                [
                    InlineKeyboardButton("📊 Full Report", callback_data=f"full_{property_query[:50]}"),
                    InlineKeyboardButton("📈 Compare Options", callback_data=f"compare_{property_query[:50]}")
                ],
                [
                    InlineKeyboardButton("💰 Calculate Mortgage", callback_data=f"mortgage_{property_query[:50]}"),
                    InlineKeyboardButton("🔍 Web Search", callback_data=f"websearch_{property_query[:50]}")
                ]
            ]

            # PDF button for Pro/Enterprise (Step 5)
            tier = await self._get_user_tier(user_id)
            if tier in ["pro", "enterprise"]:
                keyboard.append([
                    InlineKeyboardButton("📄 Generate PDF Report", callback_data=f"pdf_{property_query[:50]}")
                ])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await self.send_split_message(update, response_text, reply_markup=reply_markup)
        except Exception as e:
            error_msg = self.format_error_message(e, user_id=str(user_id), query=property_query)
            try:
                await update.message.reply_text(error_msg, parse_mode="Markdown")
            except:
                await update.message.reply_text(error_msg)

    async def cmd_subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show subscription options"""
        user_id = update.effective_user.id
        current_tier = await self._get_user_tier(user_id)

        msg = "💳 *Subscription Plans*\n\n"

        keyboard = []
        for tier_id, tier_info in SUBSCRIPTION_TIERS.items():
            is_current = tier_id == current_tier
            status = "✅ Current Plan" if is_current else f"AED {tier_info['price']}/month"

            msg += f"*{tier_info['name']}* - {status}\n"
            msg += f"• {tier_info['queries_per_day']} queries/day\n" if tier_info['queries_per_day'] > 0 else "• Unlimited queries\n"
            msg += "\n".join(f"• {feature}" for feature in tier_info['features'])
            msg += "\n\n"

            if not is_current and tier_id != "free":
                keyboard.append([
                    InlineKeyboardButton(
                        f"Upgrade to {tier_info['name']}",
                        callback_data=f"upgrade_{tier_id}"
                    )
                ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user status"""
        user_id = update.effective_user.id
        user_data = await self._get_user_data(user_id)

        tier = user_data.get("tier", "free")
        tier_info = SUBSCRIPTION_TIERS.get(tier, {})
        queries_remaining = await self.get_remaining_queries(user_id)
        total = user_data.get("total_queries", 0)
        joined = user_data.get("joined_at", user_data.get("joined", "N/A"))
        if hasattr(joined, "strftime"):
            joined = joined.strftime("%Y-%m-%d")
        elif isinstance(joined, str):
            joined = joined[:10]

        msg = f"""
📊 *Your Account Status*

*Plan:* {tier_info.get('name', 'Free')}
*Price:* AED {tier_info.get('price', 0)}/month
*Queries Today:* {user_data.get('queries_today', 0)}
*Queries Remaining:* {queries_remaining if queries_remaining >= 0 else 'Unlimited'}
*Total Queries:* {total}
*Member Since:* {joined}

Type /subscribe to upgrade for more queries and features!
        """

        await update.message.reply_text(msg, parse_mode="Markdown")

    async def cmd_trends(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get market trends"""
        user_id = update.effective_user.id

        if not await self.check_query_limit(user_id):
            await self.send_upgrade_message(update)
            return

        zone = " ".join(context.args) if context.args else "Dubai Marina"

        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            trends_query = (
                f"Get comprehensive market trends for {zone}. "
                f"Include: price trends, supply pipeline, liquidity metrics, "
                f"and investment recommendation."
            )
            uid = str(user_id)
            start = time.time()
            result = await handle_query(trends_query, user_id=uid)
            elapsed = (time.time() - start) * 1000
            await self.increment_usage(user_id)
            response_text = result.response if hasattr(result, 'response') else str(result)
            self.conversation_store.update(uid, trends_query, response_text)
            update_active_conversations(self.conversation_store.active_session_count())
            if is_db_available():
                await log_conversation(user_id, trends_query, response_text,
                                       response_time_ms=elapsed,
                                       tools_used=result.tools_used if hasattr(result, 'tools_used') else [])
            await self.send_split_message(update, response_text)
        except Exception as e:
            error_msg = self.format_error_message(e, user_id=str(user_id), query=zone)
            try:
                await update.message.reply_text(error_msg, parse_mode="Markdown")
            except:
                await update.message.reply_text(error_msg)

    async def cmd_compare(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Compare properties"""
        user_id = update.effective_user.id

        if not await self.check_query_limit(user_id):
            await self.send_upgrade_message(update)
            return

        query = " ".join(context.args) if context.args else ""
        if not query or "vs" not in query.lower():
            await update.message.reply_text(
                "Please specify properties to compare.\n"
                "Example: /compare Marina Gate vs Princess Tower"
            )
            return

        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            compare_query = (
                f"Compare these properties: {query}. "
                f"Create side-by-side comparison with price, location, "
                f"chiller costs, ROI, and recommendation."
            )
            uid = str(user_id)
            start = time.time()
            result = await handle_query(compare_query, user_id=uid)
            elapsed = (time.time() - start) * 1000
            await self.increment_usage(user_id)
            response_text = result.response if hasattr(result, 'response') else str(result)
            self.conversation_store.update(uid, compare_query, response_text)
            update_active_conversations(self.conversation_store.active_session_count())
            if is_db_available():
                await log_conversation(user_id, compare_query, response_text,
                                       response_time_ms=elapsed,
                                       tools_used=result.tools_used if hasattr(result, 'tools_used') else [])
            await self.send_split_message(update, response_text)
        except Exception as e:
            error_msg = self.format_error_message(e, user_id=str(user_id), query=query)
            try:
                await update.message.reply_text(error_msg, parse_mode="Markdown")
            except:
                await update.message.reply_text(error_msg)

    async def cmd_new(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reset conversation context"""
        uid = str(update.effective_user.id)
        record_command_metrics('new', uid)
        self.conversation_store.reset(uid)
        record_conversation_reset('command')
        update_active_conversations(self.conversation_store.active_session_count())
        await update.message.reply_text("🔄 Conversation reset. Ask me anything about Dubai real estate!")

    async def cmd_manage(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Open Stripe Customer Portal for subscription management (Step 4)."""
        user_id = update.effective_user.id
        record_command_metrics('manage', str(user_id))

        if not is_stripe_configured():
            await update.message.reply_text(
                "Subscription management is not available yet.\n"
                "Contact billing@dubaiestate.ai for help."
            )
            return

        user_data = await self._get_user_data(user_id)
        stripe_customer_id = user_data.get("stripe_customer_id")

        if not stripe_customer_id:
            await update.message.reply_text(
                "No active subscription found.\nUse /subscribe to get started!"
            )
            return

        portal_url = await create_customer_portal_session(stripe_customer_id)
        if portal_url:
            keyboard = [[InlineKeyboardButton("🔧 Manage Subscription", url=portal_url)]]
            await update.message.reply_text(
                "Click below to manage your subscription, update payment method, or cancel:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await update.message.reply_text("Could not create portal session. Please try again.")

    async def cmd_reset_limit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin command to reset query limits for testing"""
        user_id = update.effective_user.id
        uid = str(user_id)

        if uid not in self.admin_ids and str(user_id) not in self.admin_ids:
            await update.message.reply_text("⛔ Admin access required.")
            return

        if context.args:
            target_user_id = int(context.args[0])
        else:
            target_user_id = user_id

        if is_db_available():
            await reset_daily_queries(target_user_id)
            await update.message.reply_text(f"✅ Query limit reset for user {target_user_id}")
        elif target_user_id in self._users_fallback:
            self._users_fallback[target_user_id]["queries_today"] = 0
            self._users_fallback[target_user_id]["last_reset"] = date.today()
            await update.message.reply_text(f"✅ Query limit reset for user {target_user_id}")
        else:
            await update.message.reply_text(f"❌ User {target_user_id} not found in database")

    # =====================================================
    # SAVED PROPERTIES / WATCHLIST (Feature 5)
    # =====================================================

    async def cmd_save(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Save a property to watchlist"""
        user_id = update.effective_user.id
        record_command_metrics('save', str(user_id))

        if not context.args:
            await update.message.reply_text(
                "Please provide a property ID to save.\n"
                "Example: /save m001\n\n"
                "You can also use the Save button after search results."
            )
            return

        property_id = context.args[0]
        notes = " ".join(context.args[1:]) if len(context.args) > 1 else None

        if not is_db_available():
            await update.message.reply_text("Database not available. Please try again later.")
            return

        # Try to find property in mock data for richer saves
        from main import MOCK_PROPERTIES
        property_data = {"id": property_id}
        for zone_props in MOCK_PROPERTIES.values():
            for prop in zone_props:
                if prop["id"] == property_id:
                    property_data = prop
                    break

        saved_id = await save_property(user_id, property_data, notes)
        if saved_id:
            title = property_data.get("title", property_id)
            await update.message.reply_text(f"✅ Saved *{title}* to your watchlist!\n\nUse /watchlist to view all saved properties.", parse_mode="Markdown")
        else:
            await update.message.reply_text("Property already in your watchlist.")

    async def cmd_watchlist(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show saved properties"""
        user_id = update.effective_user.id
        record_command_metrics('watchlist', str(user_id))

        if not is_db_available():
            await update.message.reply_text("Database not available. Please try again later.")
            return

        props = await get_saved_properties(user_id)

        if not props:
            await update.message.reply_text(
                "📋 Your watchlist is empty.\n\n"
                "Save properties using /save <property_id> or the Save button after searches."
            )
            return

        msg = f"📋 *Your Watchlist* ({len(props)} properties)\n\n"
        keyboard = []

        for p in props:
            pd = p["property_data"]
            prop_id = pd.get("id", "unknown")
            title = pd.get("title", prop_id)
            msg += f"🏠 *{title}*\n"
            if pd.get("price"):
                purpose = pd.get("purpose", "for-sale")
                label = "Price" if purpose == "for-sale" else "Rent"
                msg += f"  {label}: AED {pd['price']:,.0f}\n"
            if pd.get("location"):
                msg += f"  Location: {pd['location']}\n"
            if pd.get("area"):
                msg += f"  Area: {pd['area']} sqft\n"
            if p.get("notes"):
                msg += f"  Notes: {p['notes']}\n"
            msg += f"  Saved: {p['saved_at'][:10] if p['saved_at'] else 'N/A'}\n\n"
            keyboard.append([
                InlineKeyboardButton(f"❌ Remove {prop_id}", callback_data=f"removeprop_{prop_id}")
            ])

        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        await self.send_split_message(update, msg, reply_markup=reply_markup)

    async def cmd_remove(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove a property from watchlist"""
        user_id = update.effective_user.id
        record_command_metrics('remove', str(user_id))

        if not context.args:
            await update.message.reply_text(
                "Please provide a property ID to remove.\n"
                "Example: /remove m001\n\n"
                "Use /watchlist to see your saved properties."
            )
            return

        property_id = context.args[0]

        if not is_db_available():
            await update.message.reply_text("Database not available. Please try again later.")
            return

        removed = await remove_saved_property(user_id, property_id)
        if removed:
            await update.message.reply_text(f"✅ Removed *{property_id}* from your watchlist.", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"Property *{property_id}* not found in your watchlist.", parse_mode="Markdown")

    # =====================================================
    # REFERRAL SYSTEM (Feature 6)
    # =====================================================

    async def cmd_referral(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show referral link and stats"""
        user_id = update.effective_user.id
        record_command_metrics('referral', str(user_id))

        if not is_db_available():
            await update.message.reply_text("Database not available. Please try again later.")
            return

        referral_code = await get_or_create_referral_code(user_id)
        stats = await get_referral_stats(user_id)

        bot_username = (await context.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"

        msg = f"""
🎁 *Your Referral Program*

Share your link and earn bonus queries!

🔗 *Your Referral Link:*
`{referral_link}`

📊 *Stats:*
• Friends referred: {stats['referral_count']}
• Bonus queries earned: {stats['total_bonus_earned']}

💰 *Rewards:*
• You get: *10 bonus queries* per referral
• Your friend gets: *5 bonus queries*

Share the link above — when someone signs up, you both get rewarded!
        """

        await update.message.reply_text(msg, parse_mode="Markdown")

    # =====================================================
    # MARKET DIGEST (Feature 7)
    # =====================================================

    async def cmd_digest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Subscribe to market digest"""
        user_id = update.effective_user.id
        record_command_metrics('digest', str(user_id))

        if not context.args:
            await update.message.reply_text(
                "📰 *Market Digest*\n\n"
                "Get automated market updates for your favorite zones!\n\n"
                "*Usage:*\n"
                "/digest Dubai Marina, JVC, Business Bay\n"
                "/digest weekly Dubai Marina\n"
                "/digest daily Downtown Dubai\n\n"
                "Use /digest\\_off to unsubscribe.",
                parse_mode="Markdown",
            )
            return

        if not is_db_available():
            await update.message.reply_text("Database not available. Please try again later.")
            return

        # Parse frequency and zones
        args_text = " ".join(context.args)
        frequency = "weekly"
        if args_text.lower().startswith("daily "):
            frequency = "daily"
            args_text = args_text[6:]
        elif args_text.lower().startswith("weekly "):
            frequency = "weekly"
            args_text = args_text[7:]

        zones = [z.strip() for z in args_text.split(",") if z.strip()]
        if not zones:
            await update.message.reply_text("Please specify at least one zone.\nExample: /digest Dubai Marina, JVC")
            return

        await set_digest_preference(user_id, frequency, zones)

        zones_list = ", ".join(zones)
        await update.message.reply_text(
            f"✅ *Digest subscribed!*\n\n"
            f"📅 Frequency: {frequency.title()}\n"
            f"📍 Zones: {zones_list}\n\n"
            f"You'll receive market updates with price trends, yield shifts, and notable transactions.\n\n"
            f"Use /digest\\_off to unsubscribe.",
            parse_mode="Markdown",
        )

    async def cmd_digest_off(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unsubscribe from market digest"""
        user_id = update.effective_user.id
        record_command_metrics('digest_off', str(user_id))

        if not is_db_available():
            await update.message.reply_text("Database not available. Please try again later.")
            return

        await disable_digest(user_id)
        await update.message.reply_text("✅ Market digest unsubscribed.\n\nUse /digest to re-subscribe anytime.")

    # =====================================================
    # MESSAGE HANDLERS
    # =====================================================

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language queries"""
        user_id = update.effective_user.id
        uid = str(user_id)

        if not await self.check_query_limit(user_id):
            await self.send_upgrade_message(update)
            return

        query = update.message.text

        # Detect follow-up and get context if needed
        followup = is_followup(query, self.conversation_store.has_session(uid))
        record_followup_detected(followup)
        conv_context = self.conversation_store.get_context(uid) if followup else None

        progress_msg = await update.message.reply_text(
            "🔍 Analyzing...\n⏱️ This will take 30-60 seconds"
        )

        try:
            start = time.time()
            result = await handle_query(query, user_id=uid, conversation_context=conv_context)
            elapsed = (time.time() - start) * 1000
            await self.increment_usage(user_id)
            response_text = result.response if hasattr(result, 'response') else str(result)

            try:
                await progress_msg.delete()
            except:
                pass

            self.conversation_store.update(uid, query, response_text)
            update_active_conversations(self.conversation_store.active_session_count())

            if is_db_available():
                await log_conversation(user_id, query, response_text,
                                       response_time_ms=elapsed,
                                       tools_used=result.tools_used if hasattr(result, 'tools_used') else [])

            keyboard = [
                [
                    InlineKeyboardButton("📊 Full Report", callback_data=f"full_{query[:50]}"),
                    InlineKeyboardButton("📈 Compare Options", callback_data=f"compare_{query[:50]}")
                ],
                [
                    InlineKeyboardButton("💰 Calculate Mortgage", callback_data=f"mortgage_{query[:50]}"),
                    InlineKeyboardButton("🔍 Web Search", callback_data=f"websearch_{query[:50]}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await self.send_split_message(update, response_text, reply_markup=reply_markup)
        except Exception as e:
            error_msg = self.format_error_message(e, user_id=uid, query=query)
            try:
                await update.message.reply_text(error_msg, parse_mode="Markdown")
            except:
                await update.message.reply_text(error_msg)

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages (Step 8)."""
        user_id = update.effective_user.id
        uid = str(user_id)

        if not is_transcription_available():
            await update.message.reply_text(
                "🎤 Voice messages are not available yet.\n"
                "Please type your question instead."
            )
            return

        if not await self.check_query_limit(user_id):
            await self.send_upgrade_message(update)
            return

        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            # Download the voice file
            voice = update.message.voice or update.message.audio
            file = await context.bot.get_file(voice.file_id)
            audio_bytes = await file.download_as_bytearray()

            # Determine format
            file_format = "ogg"
            if voice.mime_type:
                if "mp3" in voice.mime_type:
                    file_format = "mp3"
                elif "wav" in voice.mime_type:
                    file_format = "wav"
                elif "m4a" in voice.mime_type:
                    file_format = "m4a"

            # Transcribe
            transcribed_text = await transcribe_voice(bytes(audio_bytes), file_format)

            if not transcribed_text:
                await update.message.reply_text(
                    "❌ Could not transcribe the voice message.\n"
                    "Please try again or type your question."
                )
                return

            # Show what we heard
            await update.message.reply_text(f"🎤 I heard: _{transcribed_text}_", parse_mode="Markdown")

            # Process as regular text message
            update.message.text = transcribed_text
            await self.handle_message(update, context)

        except Exception as e:
            error_msg = self.format_error_message(e, user_id=uid, query="[voice message]")
            await update.message.reply_text(error_msg)

    # =====================================================
    # CALLBACK HANDLERS
    # =====================================================

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()

        data = query.data
        user_id = query.from_user.id
        uid = str(user_id)

        if data.startswith("upgrade_"):
            tier = data.replace("upgrade_", "")
            await self.process_upgrade(query, tier, user_id)
        elif data.startswith("pdf_"):
            property_query = data.replace("pdf_", "")
            await self.generate_pdf_report(query, property_query, user_id)
        elif data.startswith("full_"):
            original_query = data.replace("full_", "")
            await query.edit_message_text("📊 Generating full institutional report...\n⏱️ This will take 1-2 minutes")

            full_query = f"Give me a full detailed analysis with all sections for: {original_query}"
            result = await handle_query(full_query, user_id=uid)
            response_text = result.response if hasattr(result, 'response') else str(result)

            await query.message.reply_text(response_text[:4096])
            if len(response_text) > 4096:
                await query.message.reply_text(response_text[4096:8192])

        elif data.startswith("compare_"):
            original_query = data.replace("compare_", "")
            await query.edit_message_text("📈 Finding comparable properties...")

            compare_query = f"Show me 3 comparable alternatives to: {original_query}"
            result = await handle_query(compare_query, user_id=uid)
            response_text = result.response if hasattr(result, 'response') else str(result)
            await query.message.reply_text(response_text[:4096])

        elif data.startswith("mortgage_"):
            original_query = data.replace("mortgage_", "")
            await query.edit_message_text("💰 Calculating mortgage scenarios...")

            mortgage_query = f"Calculate mortgage options for: {original_query}. Show 75% and 80% LTV scenarios."
            result = await handle_query(mortgage_query, user_id=uid)
            response_text = result.response if hasattr(result, 'response') else str(result)
            await query.message.reply_text(response_text[:4096])

        elif data.startswith("websearch_"):
            original_query = data.replace("websearch_", "")
            await query.edit_message_text("🔍 Searching web for latest info...")

            web_query = f"Search the web for current information about: {original_query}"
            result = await handle_query(web_query, user_id=uid)
            response_text = result.response if hasattr(result, 'response') else str(result)
            await query.message.reply_text(response_text[:4096])

        elif data.startswith("save_"):
            property_id = data.replace("save_", "")
            if is_db_available():
                saved = await save_property(user_id, {"id": property_id, "source": "inline_save"})
                if saved:
                    await query.answer("Saved to watchlist!", show_alert=False)
                else:
                    await query.answer("Already in watchlist", show_alert=False)
            else:
                await query.answer("Database not available", show_alert=True)

        elif data.startswith("removeprop_"):
            property_id = data.replace("removeprop_", "")
            if is_db_available():
                removed = await remove_saved_property(user_id, property_id)
                if removed:
                    await query.answer("Removed from watchlist", show_alert=False)
                    # Refresh watchlist
                    props = await get_saved_properties(user_id)
                    if props:
                        msg = "📋 *Your Watchlist*\n\n"
                        for p in props:
                            pd = p["property_data"]
                            msg += f"• *{pd.get('title', pd.get('id', 'Unknown'))}*\n"
                            if pd.get("price"):
                                msg += f"  Price: AED {pd['price']:,.0f}\n"
                            if pd.get("location"):
                                msg += f"  Location: {pd['location']}\n"
                            msg += f"  Saved: {p['saved_at'][:10] if p['saved_at'] else 'N/A'}\n\n"
                        await query.edit_message_text(msg, parse_mode="Markdown")
                    else:
                        await query.edit_message_text("📋 Your watchlist is empty.")

    # =====================================================
    # STRIPE INTEGRATION (Step 4)
    # =====================================================

    async def process_upgrade(self, query, tier: str, user_id: int):
        """Process subscription upgrade via Stripe."""
        tier_info = SUBSCRIPTION_TIERS.get(tier, {})

        if is_stripe_configured():
            checkout_url = await create_checkout_session(
                user_id=user_id,
                tier=tier,
                username=query.from_user.username,
            )
            if checkout_url:
                keyboard = [[InlineKeyboardButton("💳 Pay Now", url=checkout_url)]]
                await query.edit_message_text(
                    f"💳 *Upgrade to {tier_info['name']}*\n\n"
                    f"Price: AED {tier_info['price']}/month\n\n"
                    f"Click below to complete payment securely via Stripe:",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
                return

        # Fallback if Stripe not configured
        await query.edit_message_text(
            f"💳 *Upgrade to {tier_info['name']}*\n\n"
            f"Price: AED {tier_info['price']}/month\n\n"
            f"To complete payment, please contact:\n"
            f"📧 billing@dubaiestate.ai\n"
            f"📱 WhatsApp: +971-XX-XXX-XXXX\n\n"
            f"Or visit: https://dubaiestate.ai/subscribe",
            parse_mode="Markdown",
        )

    # =====================================================
    # PDF GENERATION (Step 5)
    # =====================================================

    async def generate_pdf_report(self, query, property_query: str, user_id: int):
        """Generate and send a real PDF report for Pro/Enterprise users."""
        tier = await self._get_user_tier(user_id)
        if tier not in ["pro", "enterprise"]:
            await query.edit_message_text(
                "📄 PDF reports are available for Pro and Enterprise subscribers.\n"
                "Use /subscribe to upgrade!"
            )
            return

        await query.edit_message_text(
            f"📄 Generating institutional report for: {property_query}\n\n"
            f"This will take 30-60 seconds..."
        )

        try:
            # Run a full analysis
            uid = str(user_id)
            full_query = f"Give me a full detailed analysis with all sections for: {property_query}"
            result = await handle_query(full_query, user_id=uid)
            response_text = result.response if hasattr(result, 'response') else str(result)
            tools_used = result.tools_used if hasattr(result, 'tools_used') else []

            # Generate PDF
            from pdf_generator import generate_report
            import io

            user_name = query.from_user.first_name or query.from_user.username or "Investor"
            pdf_bytes = await generate_report(
                analysis_text=response_text,
                query=property_query,
                user_name=user_name,
                tools_used=tools_used,
            )

            # Send as Telegram document
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_file.name = f"TrueValue_Report_{property_query[:30].replace(' ', '_')}.pdf"

            await query.message.reply_document(
                document=pdf_file,
                filename=pdf_file.name,
                caption=f"📄 TrueValue AI Report: {property_query}",
            )

        except Exception as e:
            bot_logger.error("PDF generation failed: %s", e)
            await query.message.reply_text(
                f"❌ Could not generate PDF report.\nError: {str(e)[:100]}\n\n"
                f"Please try again or contact support."
            )

    # =====================================================
    # UTILITIES
    # =====================================================

    async def send_upgrade_message(self, update: Update):
        """Send upgrade prompt when limit reached"""
        keyboard = [[
            InlineKeyboardButton("📈 Upgrade Now", callback_data="upgrade_basic")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "⚠️ *Daily Query Limit Reached*\n\n"
            "Upgrade to get more queries and advanced features!\n"
            "Type /subscribe to see plans.",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )

    def format_error_message(self, error: Exception, user_id: str = None, query: str = None) -> str:
        """Format error message for user and log it"""
        error_str = str(error)

        if user_id:
            log_user_error(
                logger=bot_logger,
                user_id=user_id,
                error_message=error_str,
                exception=error,
                query=query
            )

        if "credit balance is too low" in error_str.lower():
            return (
                "❌ *API Credits Issue*\n\n"
                "The Anthropic API credits are running low.\n\n"
                "📧 Please contact support or try again later.\n\n"
                "_Error: Insufficient API credits_"
            )
        elif "rate limit" in error_str.lower():
            return (
                "⏱️ *Rate Limit Reached*\n\n"
                "Too many requests. Please wait a moment and try again.\n\n"
                "_The API has temporary rate limits._"
            )
        elif "timeout" in error_str.lower():
            return (
                "⏱️ *Request Timeout*\n\n"
                "The analysis took too long. Please try a simpler query.\n\n"
                "_The API request timed out._"
            )
        elif "network" in error_str.lower() or "connection" in error_str.lower():
            return (
                "🌐 *Connection Issue*\n\n"
                "Could not connect to the AI service.\n\n"
                "Please try again in a moment.\n\n"
                "_Network connectivity error_"
            )
        else:
            return (
                "❌ *Something Went Wrong*\n\n"
                "An error occurred while processing your request.\n\n"
                "Please try again or contact support if the issue persists.\n\n"
                f"_Error details: {error_str[:100]}_"
            )

    async def send_split_message(self, update: Update, text: str, reply_markup=None):
        """Split long messages to respect Telegram's 4096 char limit"""
        MAX_LENGTH = 4096

        try:
            if len(text) <= MAX_LENGTH:
                await update.message.reply_text(
                    text, parse_mode="Markdown", reply_markup=reply_markup
                )
                return

            parts = []
            current = ""

            for paragraph in text.split("\n\n"):
                if len(current) + len(paragraph) + 2 < MAX_LENGTH:
                    current += paragraph + "\n\n"
                else:
                    if current:
                        parts.append(current.strip())
                    current = paragraph + "\n\n"

            if current:
                parts.append(current.strip())

            for i, part in enumerate(parts):
                is_last = (i == len(parts) - 1)
                await update.message.reply_text(
                    part, parse_mode="Markdown",
                    reply_markup=reply_markup if is_last else None
                )
                await asyncio.sleep(0.5)

        except Exception:
            if len(text) <= MAX_LENGTH:
                await update.message.reply_text(text, reply_markup=reply_markup)
            else:
                parts = []
                current = ""
                for paragraph in text.split("\n\n"):
                    if len(current) + len(paragraph) + 2 < MAX_LENGTH:
                        current += paragraph + "\n\n"
                    else:
                        if current:
                            parts.append(current.strip())
                        current = paragraph + "\n\n"
                if current:
                    parts.append(current.strip())

                for i, part in enumerate(parts):
                    is_last = (i == len(parts) - 1)
                    await update.message.reply_text(
                        part, reply_markup=reply_markup if is_last else None
                    )
                    await asyncio.sleep(0.5)

    # =====================================================
    # RUN
    # =====================================================

    async def run(self):
        """Run the bot"""
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

        print("✅ Telegram bot running...")
        print(f"📱 Bot ready to receive messages")

        # Keep running
        await asyncio.Event().wait()


if __name__ == "__main__":
    bot = TelegramBotServer()
    asyncio.run(bot.run())
