#!/usr/bin/env python3
"""
Dubai Estate AI - Main Entry Point
Runs FastAPI (uvicorn) + Telegram bot concurrently via asyncio.gather.
Supports BOT_MODE=webhook for production (bot receives updates via webhook).
"""

import os
import sys
import asyncio
import signal
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_required_vars():
    """Validate required environment variables."""
    required_vars = ["ANTHROPIC_API_KEY", "TELEGRAM_BOT_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file and add your API keys.")
        sys.exit(1)


def print_startup_banner():
    """Print startup status."""
    print("Starting TrueValue AI...")
    print(f"  Anthropic API Key: {'Set' if os.getenv('ANTHROPIC_API_KEY') else 'Missing'}")
    print(f"  Telegram Token:    {'Set' if os.getenv('TELEGRAM_BOT_TOKEN') else 'Missing'}")
    print(f"  Bayut API Key:     {'Set' if os.getenv('BAYUT_API_KEY') and os.getenv('BAYUT_API_KEY') not in ['demo', 'your_rapidapi_key_here'] else 'Mock data'}")
    print(f"  Brave API Key:     {'Set' if os.getenv('BRAVE_API_KEY') and os.getenv('BRAVE_API_KEY') not in ['demo', ''] else 'Disabled'}")
    print(f"  Database:          {'Set' if os.getenv('DATABASE_URL') and 'user:pass' not in os.getenv('DATABASE_URL', '') else 'In-memory'}")
    print(f"  Redis:             {'Set' if os.getenv('REDIS_URL') else 'Disabled'}")
    print(f"  Stripe:            {'Set' if os.getenv('STRIPE_SECRET_KEY') else 'Disabled'}")
    print(f"  OpenAI (Whisper):  {'Set' if os.getenv('OPENAI_API_KEY') else 'Disabled'}")
    print(f"  Bot Mode:          {os.getenv('BOT_MODE', 'polling')}")
    print()


async def start_fastapi():
    """Run the FastAPI server."""
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=False,
    )
    server = uvicorn.Server(config)
    await server.serve()


async def start_telegram_bot():
    """Run the Telegram bot in polling mode."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "telegram-bot"))
    from bot import TelegramBotServer

    bot = TelegramBotServer()
    await bot.run()


async def init_services():
    """Initialise database and cache connections."""
    from database import init_db
    from cache import init_cache

    await init_db()
    await init_cache()


async def shutdown_services():
    """Clean up database and cache connections."""
    from database import close_db
    from cache import close_cache

    await close_db()
    await close_cache()


async def main():
    """Main async entry point — runs FastAPI + Telegram bot concurrently."""
    await init_services()

    bot_mode = os.getenv("BOT_MODE", "polling").lower()

    try:
        if bot_mode == "webhook":
            # Webhook mode: only run FastAPI (bot receives updates via /webhook/telegram)
            print("Running in webhook mode (FastAPI only)...")
            await start_fastapi()
        else:
            # Polling mode: run both FastAPI and Telegram bot
            print("Running in polling mode (FastAPI + Telegram bot)...")
            await asyncio.gather(
                start_fastapi(),
                start_telegram_bot(),
            )
    finally:
        await shutdown_services()


if __name__ == "__main__":
    check_required_vars()
    print_startup_banner()
    asyncio.run(main())
