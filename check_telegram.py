#!/usr/bin/env python3
"""
Check Telegram Bot Status and Recent Updates
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

print("="*60)
print("TELEGRAM BOT DIAGNOSTIC")
print("="*60)

# 1. Get bot info
response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
if response.status_code == 200:
    bot = response.json()['result']
    print(f"\n✅ Bot Connected:")
    print(f"   Username: @{bot['username']}")
    print(f"   Name: {bot['first_name']}")
    print(f"   ID: {bot['id']}")
else:
    print(f"\n❌ Bot connection failed: {response.status_code}")
    print(response.text)
    exit(1)

# 2. Get recent updates
print(f"\n📥 Checking recent messages...")
response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?limit=10")

if response.status_code == 200:
    updates = response.json()['result']
    print(f"   Found {len(updates)} recent updates")

    if updates:
        print(f"\n📜 Recent Messages:")
        for update in updates[-5:]:  # Last 5
            if 'message' in update:
                msg = update['message']
                user = msg.get('from', {})
                text = msg.get('text', '[no text]')
                chat_id = msg.get('chat', {}).get('id')
                date = msg.get('date')

                print(f"\n   From: {user.get('first_name', 'Unknown')} (ID: {user.get('id')})")
                print(f"   Chat ID: {chat_id}")
                print(f"   Message: {text[:50]}...")
                print(f"   Timestamp: {date}")
    else:
        print("   No messages found!")
        print("\n⚠️  PROBLEM: The bot hasn't received any messages yet!")
        print("   Have you sent /start to the bot on Telegram?")
else:
    print(f"   ❌ Failed to get updates: {response.status_code}")

# 3. Test sending a message
print(f"\n📤 Testing message send...")
print("   Note: I need a chat_id to send to.")
print("   Send /start to the bot on Telegram first!")

if updates:
    # Try to send to the last chat
    last_chat_id = updates[-1]['message']['chat']['id']
    print(f"   Attempting to send test message to chat {last_chat_id}...")

    test_response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": last_chat_id,
            "text": "✅ TEST MESSAGE from check_telegram.py\n\nIf you see this, the bot CAN send messages!"
        }
    )

    if test_response.status_code == 200:
        print(f"   ✅ Test message sent successfully!")
        print(f"   Check your Telegram - you should see the test message!")
    else:
        print(f"   ❌ Test message failed: {test_response.status_code}")
        print(f"   Error: {test_response.text}")

print(f"\n{'='*60}")
print("DIAGNOSTIC COMPLETE")
print(f"{'='*60}\n")
