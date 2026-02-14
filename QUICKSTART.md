# 🚀 Quick Start - 5 Minutes to Running Bot

## Step 1: Install (2 minutes)

```bash
cd /Users/tad/Downloads/TrueValue

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Add API Keys (2 minutes)

Edit `.env` file:
```bash
nano .env
```

Add these two keys (minimum):
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
TELEGRAM_BOT_TOKEN=123456:ABCdefGHI...
```

Get keys:
- **Anthropic:** https://console.anthropic.com
- **Telegram:** Message @BotFather on Telegram, type `/newbot`

## Step 3: Run (1 minute)

```bash
python run.py
```

You should see:
```
🚀 Starting Dubai Estate AI Bot...
📊 Anthropic API Key: ✅ Set
📱 Telegram Token: ✅ Set
✅ Telegram bot running...
📱 Bot ready to receive messages
```

## Step 4: Test on Telegram

Open Telegram, find your bot, and try:

```
/start
```

Then try a real query:
```
Find 2BR apartments in Dubai Marina under 2 million
```

Or:
```
Analyze Marina Gate Tower 1
```

Or:
```
Calculate chiller cost for 1500 sqft Empower property
```

## What You'll See

The bot will:
1. Show typing indicator
2. Call Claude with your query
3. Claude will use tools (search, calculate, analyze)
4. Return formatted analysis with:
   - Property details
   - Chiller cost warnings
   - Investment score (0-100)
   - GO/NO-GO recommendation

## Example Response

```
🏢 Marina Gate Tower 1

💰 PRICE: AED 2,500,000
📏 1,500 sqft | 🛏️ 2BR | 🏊 Pool view
📍 Dubai Marina | 🚇 Metro: 5 min walk

⚠️ RED FLAGS:
1. ❌ Chiller trap: AED 22,500/year (Empower fixed charges)
2. ⚠️ Overpriced by 6.4% vs market average
3. ⚠️ Net yield only 1.08% after hidden costs

🎯 INVESTMENT SCORE: 32/100

📋 VERDICT: ⚠️ NEGOTIATE HARD
- Hidden chiller costs destroy ROI
- Request AED 150K discount to fair value
- Or consider alternative properties

💡 BETTER OPTION:
Princess Tower #4509 (AED 2.6M)
- 4.2% net yield (4x better)
- Lootah chiller (47% lower costs)
- No major building issues
```

## Commands Available

- `/start` - Welcome
- `/help` - All commands
- `/search <query>` - Find properties
- `/analyze <property>` - Deep analysis
- `/compare A vs B` - Side-by-side
- `/trends <zone>` - Market data
- `/status` - Your account
- `/subscribe` - Upgrade plans

Or just type naturally!

## Troubleshooting

**Bot won't start?**
- Check `.env` has both keys
- Make sure virtual environment is activated: `source venv/bin/activate`

**Bot doesn't respond?**
- Check Telegram token is correct
- Make sure you messaged the bot first (click "Start")
- Check terminal for errors

**"API error"?**
- Check Anthropic key is valid
- Check you have credits at console.anthropic.com
- Bot will use mock data if APIs fail

## What's Working

✅ Natural language queries
✅ Property search (uses mock data if no Bayut key)
✅ Chiller cost calculator (always works - pure math!)
✅ Investment scoring (0-100 scale)
✅ Market trends
✅ Property comparison
✅ Building issue reports (mock data if no Reddit key)
✅ Subscription management (3 queries/day free tier)

## Adding Real Data

The bot works with mock data. To add real APIs:

**Bayut (property listings):**
1. Sign up: https://rapidapi.com/apicommunity/api/bayut
2. Add to `.env`: `BAYUT_API_KEY=your_key`
3. Restart bot

**Reddit (building issues):**
1. Create app: https://reddit.com/prefs/apps
2. Add to `.env`: `REDDIT_CLIENT_ID=xxx` and `REDDIT_CLIENT_SECRET=xxx`
3. Restart bot

Bot switches to real data automatically!

## Next Steps

1. ✅ Test all commands
2. ✅ Try natural language queries
3. ⚠️ Optionally add Bayut/Reddit keys
4. 🚀 Deploy to Heroku for 24/7 (see SETUP_GUIDE.md)

## Cost

- **Free tier:** 3 queries/day
- **API costs:** ~$0.02-0.04 per query (Anthropic)
- **Hosting:** Free (local) or $7/mo (Heroku hobby)

## Files

- `main.py` - Analysis engine
- `telegram-bot/bot.py` - Telegram interface
- `run.py` - Starts everything
- `.env` - Your API keys (never commit!)

## Support

- **Setup issues:** Read SETUP_GUIDE.md
- **How it works:** Read IMPLEMENTATION_COMPLETE.md
- **Business context:** Read CONTEXT.md

---

**That's it! You now have a working AI real estate analyst.** 🏢✨
