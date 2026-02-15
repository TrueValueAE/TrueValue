#!/usr/bin/env python3
"""
Start both FastAPI (for metrics) and Telegram bot together
"""
import asyncio
import threading
import uvicorn
from dotenv import load_dotenv

load_dotenv()

def run_fastapi():
    """Run FastAPI server for /metrics endpoint"""
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")

def run_telegram_bot():
    """Run Telegram bot"""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'telegram-bot'))

    from bot import DubaiEstateBot
    bot = DubaiEstateBot()
    asyncio.run(bot.run())

if __name__ == "__main__":
    print("🚀 Starting Dubai Estate AI with Observability")
    print("=" * 60)
    print("  FastAPI:  http://localhost:8000")
    print("  Metrics:  http://localhost:8000/metrics")
    print("  Health:   http://localhost:8000/health")
    print("  Grafana:  http://localhost:3000 (admin/admin)")
    print("=" * 60)
    print()

    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()

    # Give FastAPI time to start
    import time
    time.sleep(2)

    # Run Telegram bot in main thread
    try:
        run_telegram_bot()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
