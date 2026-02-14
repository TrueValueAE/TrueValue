#!/usr/bin/env python3
"""
Dubai Estate AI - Main Entry Point
Runs the Telegram bot with main.py imported directly
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point"""

    # Check required environment variables
    required_vars = ["ANTHROPIC_API_KEY", "TELEGRAM_BOT_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file from .env.template and add your API keys.")
        sys.exit(1)

    print("🚀 Starting Dubai Estate AI Bot...")
    print(f"📊 Anthropic API Key: {'✅ Set' if os.getenv('ANTHROPIC_API_KEY') else '❌ Missing'}")
    print(f"📱 Telegram Token: {'✅ Set' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌ Missing'}")
    print(f"🔑 Bayut API Key: {'✅ Set' if os.getenv('BAYUT_API_KEY') and os.getenv('BAYUT_API_KEY') not in ['demo', 'your_rapidapi_key_here'] else '⚠️  Using mock data'}")
    print(f"🏛️ Dubai REST API: {'✅ Set' if os.getenv('DUBAI_REST_API_KEY') and os.getenv('DUBAI_REST_API_KEY') not in ['demo', 'your_dubai_rest_key_here'] else '⚠️  Using mock data'}")
    print(f"📖 Reddit API: {'✅ Set' if os.getenv('REDDIT_CLIENT_ID') else '⚠️  Using mock data'}")
    print()

    # Import and run the Telegram bot
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'telegram-bot'))
    from bot import TelegramBotServer

    bot = TelegramBotServer()
    asyncio.run(bot.run())

if __name__ == "__main__":
    main()
