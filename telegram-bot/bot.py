#!/usr/bin/env python3
"""
Dubai Estate Telegram Bot
Direct integration with main.py analysis engine
"""

import os
import sys
import asyncio
from datetime import datetime
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

# Subscription tiers
SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Free",
        "price": 0,
        "queries_per_day": 3,
        "features": ["Basic property search", "Simple analysis", "Limited results"],
    },
    "basic": {
        "name": "Basic",
        "price": 99,  # AED per month
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
        "price": 299,  # AED per month
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
        "price": 999,  # AED per month
        "queries_per_day": -1,  # Unlimited
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

        # User database (in production, use real database)
        self.users_db = {}

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
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))

        # Handle all text messages as property queries
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message and registration"""
        user_id = update.effective_user.id

        if user_id not in self.users_db:
            self.users_db[user_id] = {
                "tier": "free",
                "joined": datetime.now().isoformat(),
                "queries_today": 0,
                "last_reset": datetime.now().date().isoformat(),
            }

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

📊 *Your Plan:* {SUBSCRIPTION_TIERS[self.users_db[user_id]['tier']]['name']}
📈 *Queries Left Today:* {self.get_remaining_queries(user_id)}

💡 *Quick Start:*
Just send me a message like:
• "Find 2BR apartments in Marina under 2M"
• "Analyze Boulevard Point Business Bay"
• "Compare Marina Gate vs Princess Tower"
• "Calculate chiller cost for 1500 sqft Empower property"

Type /help for all commands or /subscribe to upgrade!
        """

        await update.message.reply_text(
            welcome_msg,
            parse_mode="Markdown",
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        help_msg = """
📚 *Available Commands:*

/search - Search for properties
  Example: /search Marina 2BR under 2M

/analyze - Deep analysis of a specific property
  Example: /analyze Marina Gate Tower 1

/compare - Compare multiple properties
  Example: /compare property1 vs property2

/trends - Get market trends for a zone
  Example: /trends Business Bay

/subscribe - View and upgrade subscription plans

/status - Check your account status and usage

*Natural Language Queries:*
You can also just type naturally:
• "What's the best investment in JBR under 3M?"
• "Show me villas in Arabian Ranches"
• "Is Business Bay oversupplied in 2026?"
• "Calculate ROI for 2.5M apartment in Downtown"

I'll understand and help! 🤖
        """

        await update.message.reply_text(help_msg, parse_mode="Markdown")

    async def cmd_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Search properties"""
        user_id = update.effective_user.id

        if not self.check_query_limit(user_id):
            await self.send_upgrade_message(update)
            return

        query = " ".join(context.args) if context.args else ""
        if not query:
            await update.message.reply_text(
                "Please provide search criteria.\nExample: /search Marina 2BR under 2M"
            )
            return

        # Send typing indicator
        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            # Call main.py's handle_query function
            result = await handle_query(
                f"Search for properties: {query}. Return top 5 results with key metrics.",
                user_id=str(user_id)
            )
            self.increment_usage(user_id)
            await self.send_split_message(update, result)
        except Exception as e:
            error_msg = self.format_error_message(e)
            await update.message.reply_text(error_msg, parse_mode="Markdown")

    async def cmd_analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze a specific property"""
        user_id = update.effective_user.id

        if not self.check_query_limit(user_id):
            await self.send_upgrade_message(update)
            return

        property_query = " ".join(context.args) if context.args else ""
        if not property_query:
            await update.message.reply_text(
                "Please specify a property.\nExample: /analyze Marina Gate Tower 1"
            )
            return

        await update.message.chat.send_action(ChatAction.TYPING)

        await update.message.reply_text(
            "🔬 Analyzing property...\n"
            "This includes: market analysis, chiller costs, building issues, "
            "liquidity analysis, and investment scoring."
        )

        try:
            # Call main.py with full analysis request
            result = await handle_query(
                f"Perform comprehensive institutional analysis on: {property_query}. "
                f"Include all 4 pillars: Macro/Market, Liquidity, Technical, Legal. "
                f"Provide GO/NO-GO recommendation with investment score.",
                user_id=str(user_id)
            )

            self.increment_usage(user_id)

            # If Pro or Enterprise, offer PDF report
            if self.users_db[user_id]["tier"] in ["pro", "enterprise"]:
                keyboard = [
                    [InlineKeyboardButton("📄 Generate PDF Report", callback_data=f"pdf_{property_query}")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await self.send_split_message(update, result, reply_markup=reply_markup)
            else:
                await self.send_split_message(update, result)
        except Exception as e:
            error_msg = self.format_error_message(e)
            await update.message.reply_text(error_msg, parse_mode="Markdown")

    async def cmd_subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show subscription options"""
        user_id = update.effective_user.id
        current_tier = self.users_db.get(user_id, {}).get("tier", "free")

        msg = "💳 *Subscription Plans*\n\n"

        keyboard = []
        for tier_id, tier_info in SUBSCRIPTION_TIERS.items():
            is_current = tier_id == current_tier
            status = "✅ Current Plan" if is_current else f"AED {tier_info['price']}/month"

            msg += f"*{tier_info['name']}* - {status}\n"
            msg += f"• {tier_info['queries_per_day']} queries/day\n" if tier_info['queries_per_day'] > 0 else "• Unlimited queries\n"
            msg += "\n".join(f"• {feature}" for feature in tier_info['features'])
            msg += "\n\n"

            if not is_current:
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
        user_data = self.users_db.get(user_id, {})

        tier_info = SUBSCRIPTION_TIERS.get(user_data.get("tier", "free"), {})
        queries_remaining = self.get_remaining_queries(user_id)

        msg = f"""
📊 *Your Account Status*

*Plan:* {tier_info.get('name', 'Free')}
*Price:* AED {tier_info.get('price', 0)}/month
*Queries Today:* {user_data.get('queries_today', 0)}
*Queries Remaining:* {queries_remaining if queries_remaining >= 0 else 'Unlimited'}
*Member Since:* {user_data.get('joined', 'N/A')[:10]}

Type /subscribe to upgrade for more queries and features!
        """

        await update.message.reply_text(msg, parse_mode="Markdown")

    async def cmd_trends(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get market trends"""
        user_id = update.effective_user.id

        if not self.check_query_limit(user_id):
            await self.send_upgrade_message(update)
            return

        zone = " ".join(context.args) if context.args else "Dubai Marina"

        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            result = await handle_query(
                f"Get comprehensive market trends for {zone}. "
                f"Include: price trends, supply pipeline, liquidity metrics, "
                f"and investment recommendation.",
                user_id=str(user_id)
            )
            self.increment_usage(user_id)
            await self.send_split_message(update, result)
        except Exception as e:
            error_msg = self.format_error_message(e)
            await update.message.reply_text(error_msg, parse_mode="Markdown")

    async def cmd_compare(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Compare properties"""
        user_id = update.effective_user.id

        if not self.check_query_limit(user_id):
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
            result = await handle_query(
                f"Compare these properties: {query}. "
                f"Create side-by-side comparison with price, location, "
                f"chiller costs, ROI, and recommendation.",
                user_id=str(user_id)
            )
            self.increment_usage(user_id)
            await self.send_split_message(update, result)
        except Exception as e:
            error_msg = self.format_error_message(e)
            await update.message.reply_text(error_msg, parse_mode="Markdown")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language queries"""
        user_id = update.effective_user.id

        if not self.check_query_limit(user_id):
            await self.send_upgrade_message(update)
            return

        query = update.message.text

        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            # Call main.py's handle_query directly
            result = await handle_query(query, user_id=str(user_id))
            self.increment_usage(user_id)
            await self.send_split_message(update, result)
        except Exception as e:
            # Handle API errors gracefully
            error_msg = self.format_error_message(e)
            await update.message.reply_text(error_msg, parse_mode="Markdown")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()

        data = query.data

        if data.startswith("upgrade_"):
            tier = data.replace("upgrade_", "")
            await self.process_upgrade(query, tier)
        elif data.startswith("pdf_"):
            property_query = data.replace("pdf_", "")
            await self.generate_pdf_report(query, property_query)

    def check_query_limit(self, user_id: int) -> bool:
        """Check if user has queries remaining"""
        user_data = self.users_db.get(user_id, {})
        tier = user_data.get("tier", "free")
        tier_info = SUBSCRIPTION_TIERS[tier]

        # Reset daily counter if needed
        today = datetime.now().date().isoformat()
        if user_data.get("last_reset") != today:
            self.users_db[user_id]["queries_today"] = 0
            self.users_db[user_id]["last_reset"] = today

        # Check limit
        if tier_info["queries_per_day"] == -1:  # Unlimited
            return True

        return user_data.get("queries_today", 0) < tier_info["queries_per_day"]

    def get_remaining_queries(self, user_id: int) -> int:
        """Get remaining queries for today"""
        user_data = self.users_db.get(user_id, {})
        tier = user_data.get("tier", "free")
        tier_info = SUBSCRIPTION_TIERS[tier]

        if tier_info["queries_per_day"] == -1:
            return -1  # Unlimited

        return max(0, tier_info["queries_per_day"] - user_data.get("queries_today", 0))

    def increment_usage(self, user_id: int):
        """Increment query usage"""
        if user_id in self.users_db:
            self.users_db[user_id]["queries_today"] = (
                self.users_db[user_id].get("queries_today", 0) + 1
            )

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

    def format_error_message(self, error: Exception) -> str:
        """Format error message for user"""
        error_str = str(error)

        # Check for specific error types
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
            # Generic error
            return (
                "❌ *Something Went Wrong*\n\n"
                "An error occurred while processing your request.\n\n"
                "Please try again or contact support if the issue persists.\n\n"
                f"_Error details: {error_str[:100]}_"
            )

    async def send_split_message(self, update: Update, text: str, reply_markup=None):
        """Split long messages to respect Telegram's 4096 char limit"""
        MAX_LENGTH = 4096

        if len(text) <= MAX_LENGTH:
            await update.message.reply_text(
                text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            return

        # Split by paragraphs first
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

        # Send all parts
        for i, part in enumerate(parts):
            is_last = (i == len(parts) - 1)
            await update.message.reply_text(
                part,
                parse_mode="Markdown",
                reply_markup=reply_markup if is_last else None
            )
            await asyncio.sleep(0.5)  # Small delay between messages

    async def process_upgrade(self, query, tier: str):
        """Process subscription upgrade"""
        tier_info = SUBSCRIPTION_TIERS.get(tier, {})

        # In production, integrate with Stripe/payment gateway
        await query.edit_message_text(
            f"💳 *Upgrade to {tier_info['name']}*\n\n"
            f"Price: AED {tier_info['price']}/month\n\n"
            f"To complete payment, please contact:\n"
            f"📧 billing@dubaiestate.ai\n"
            f"📱 WhatsApp: +971-XX-XXX-XXXX\n\n"
            f"Or visit: https://dubaiestate.ai/subscribe",
            parse_mode="Markdown",
        )

    async def generate_pdf_report(self, query, property_query: str):
        """Generate PDF report for Pro/Enterprise users"""
        await query.edit_message_text(
            f"📄 Generating institutional report for: {property_query}\n\n"
            f"This will take 30-60 seconds...",
            parse_mode="Markdown",
        )

        # In production, generate actual PDF report
        await asyncio.sleep(2)

        await query.message.reply_text(
            "✅ Report generated!\n"
            "Download link: https://dubaiestate.ai/reports/xxx.pdf\n"
            "(Link expires in 24 hours)",
            parse_mode="Markdown",
        )

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
