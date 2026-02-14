#!/usr/bin/env python3
"""
Set Telegram Bot Commands
Run this once to register commands with BotFather
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

commands = [
    {"command": "start", "description": "Welcome message and quick start guide"},
    {"command": "help", "description": "Show all available commands"},
    {"command": "search", "description": "Search for properties (e.g., /search Marina 2BR under 2M)"},
    {"command": "analyze", "description": "Deep analysis of a property (e.g., /analyze Marina Gate Tower 1)"},
    {"command": "compare", "description": "Compare properties (e.g., /compare PropertyA vs PropertyB)"},
    {"command": "trends", "description": "Get market trends for a zone (e.g., /trends Business Bay)"},
    {"command": "status", "description": "Check your account status and usage"},
    {"command": "subscribe", "description": "View and upgrade subscription plans"},
]

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
response = requests.post(url, json={"commands": commands})

if response.status_code == 200:
    print("✅ Bot commands registered successfully!")
    print("\nRegistered commands:")
    for cmd in commands:
        print(f"  /{cmd['command']} - {cmd['description']}")
else:
    print(f"❌ Failed to register commands: {response.text}")
