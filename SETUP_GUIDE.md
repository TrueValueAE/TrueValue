# Dubai Estate AI - Setup Guide

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
cd /Users/tad/Downloads/TrueValue

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit `.env` file and add your keys:

```bash
nano .env
```

**Minimum required:**
- `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com
- `TELEGRAM_BOT_TOKEN` - Get from @BotFather on Telegram

**Optional (bot works without these using mock data):**
- `BAYUT_API_KEY` - For real property data
- `DUBAI_REST_API_KEY` - For real title deed verification
- `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` - For real building issue reports

### 3. Run the Bot

```bash
python run.py
```

You should see:
```
🚀 Starting Dubai Estate AI Bot...
📊 Anthropic API Key: ✅ Set
📱 Telegram Token: ✅ Set
🔑 Bayut API Key: ⚠️  Using mock data
✅ Telegram bot running...
📱 Bot ready to receive messages
```

### 4. Test on Telegram

Open Telegram and find your bot, then try:

- `/start` - Welcome message
- `/help` - See all commands
- "Find 2BR in Marina under 2M" - Natural language query
- "/analyze Marina Gate Tower 1" - Deep analysis
- "/trends Business Bay" - Market trends
- "Calculate chiller cost for 1500 sqft Empower property" - Chiller analysis

## Architecture

### How It Works

```
┌─────────────────────────────────────┐
│   Telegram User                     │
│   Sends: "Analyze Marina Gate"     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   telegram-bot/bot.py               │
│   - Handles commands                │
│   - Manages subscriptions           │
│   - Splits long messages            │
└──────────────┬──────────────────────┘
               │
               │ from main import handle_query
               │ (in-process call, no HTTP)
               ▼
┌─────────────────────────────────────┐
│   main.py                           │
│   - 8 tool functions                │
│   - Claude iterative loop           │
│   - Mock data fallback              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Claude Sonnet 4                   │
│   - Calls tools                     │
│   - Analyzes data                   │
│   - Returns formatted response      │
└─────────────────────────────────────┘
```

### File Structure

```
TrueValue/
├── main.py                 # Core analysis engine (8 tools, FastAPI)
├── run.py                  # Entry point (runs Telegram bot)
├── telegram-bot/
│   └── bot.py             # Telegram interface
├── requirements.txt        # Python dependencies
├── .env                   # Your API keys (DO NOT COMMIT)
├── .gitignore             # Excludes .env, venv, etc.
├── Procfile               # Heroku deployment config
├── CONTEXT.md             # Business domain knowledge
└── README.md              # Project overview
```

## The 8 Tools

| Tool | Description | Requires API |
|------|-------------|--------------|
| `search_bayut_properties` | Search for properties | Bayut API (has mock fallback) |
| `calculate_chiller_cost` | Calculate annual cooling costs | No (pure math) |
| `verify_title_deed` | Verify property ownership | Dubai REST (has mock fallback) |
| `get_market_trends` | Get zone trends and prices | Bayut API (has mock fallback) |
| `search_building_issues` | Find snagging reports | Reddit API (has mock fallback) |
| `analyze_investment` | Full 4-pillar scoring | No (uses other tools) |
| `get_supply_pipeline` | Check oversupply risk | No (hardcoded research data) |
| `compare_properties` | Side-by-side comparison | No (uses other tools) |

## Mock Data

The bot works **end-to-end without any external APIs** using realistic mock data:

- **Properties:** 30+ Dubai properties across 5 zones with realistic prices
- **Chiller costs:** Real Empower/Lootah rate calculations
- **Building issues:** Sample snagging reports for major buildings
- **Supply pipeline:** Research data for 7 major zones
- **Market trends:** Estimated yields and liquidity scores

When you add real API keys, it switches automatically!

## Subscription Tiers

Built-in subscription management (in-memory for MVP):

- **Free:** 3 queries/day
- **Basic (AED 99/mo):** 20 queries/day + chiller analysis
- **Pro (AED 299/mo):** 100 queries/day + PDF reports
- **Enterprise (AED 999/mo):** Unlimited

## Telegram Commands

- `/start` - Welcome message
- `/help` - Command list
- `/search <query>` - Search properties
- `/analyze <property>` - Full analysis
- `/compare <A> vs <B>` - Compare properties
- `/trends <zone>` - Market trends
- `/status` - Account info
- `/subscribe` - Upgrade plan

Or just type naturally: "Find studios in JVC under 600K"

## Key Features

### ✅ Chiller Cost Analysis (The Moat!)
- Empower: Fixed capacity charges (AED 85/TR/month) = trap!
- Lootah: Variable charges only = better
- Example: 1500 sqft Empower = AED 22.5K/year vs AED 6K expected
- Nobody else tracks this!

### ✅ 4-Pillar Analysis Framework
1. **Macro & Market** - Supply, interest rates, zone momentum
2. **Liquidity & Exit** - Days on market, transaction velocity
3. **Technical** - Chiller costs, building quality, snagging
4. **Legal** - Title deeds, compliance, disputes

### ✅ Investment Scoring (0-100)
- Price score: 30 pts
- Yield score: 25 pts
- Liquidity score: 20 pts
- Quality score: 15 pts
- Chiller score: 10 pts

**Recommendations:**
- 80-100: ✅ STRONG BUY
- 60-79: ✅ GOOD BUY
- 40-59: ⚠️ CAUTION
- 20-39: ⚠️ NEGOTIATE
- 0-19: ⛔ DO NOT BUY

## Troubleshooting

### Bot won't start
```bash
# Check your .env file has the required keys
cat .env | grep ANTHROPIC_API_KEY
cat .env | grep TELEGRAM_BOT_TOKEN

# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Bot doesn't respond on Telegram
- Check the bot token is correct (from @BotFather)
- Ensure you've started a conversation with the bot first
- Check the terminal for error messages

### "API error" messages
- Check your Anthropic API key is valid
- Check you have credits in your Anthropic account
- The bot will use mock data if external APIs fail

## Adding Real API Keys

### Bayut API
1. Sign up at https://rapidapi.com
2. Subscribe to "Bayut" API
3. Copy your RapidAPI key
4. Add to `.env`: `BAYUT_API_KEY=your_key_here`

### Reddit API
1. Go to https://reddit.com/prefs/apps
2. Create a "script" app
3. Copy client ID and secret
4. Add to `.env`:
   ```
   REDDIT_CLIENT_ID=your_id
   REDDIT_CLIENT_SECRET=your_secret
   ```

### Dubai REST API
1. Visit https://dubairest.gov.ae
2. Apply for developer access
3. Wait for approval (can take days)
4. Add to `.env`: `DUBAI_REST_API_KEY=your_key_here`

## Deployment to Heroku

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create dubai-estate-bot

# Set environment variables
heroku config:set ANTHROPIC_API_KEY=your_key
heroku config:set TELEGRAM_BOT_TOKEN=your_token

# Deploy
git push heroku main

# Scale bot worker
heroku ps:scale bot=1
```

## Next Steps

1. ✅ Test all commands locally
2. ✅ Add your Anthropic + Telegram keys
3. ⚠️ Optionally add Bayut, Reddit, Dubai REST keys for real data
4. 🚀 Deploy to Heroku for 24/7 availability
5. 💰 Set up Stripe for subscription payments
6. 📊 Add PostgreSQL database for user persistence
7. 📈 Monitor usage and costs

## Support

- **Issues:** Check terminal output for errors
- **Questions:** Read CONTEXT.md for business logic
- **API Costs:** Anthropic API is pay-per-use (check console.anthropic.com)

## Security

- ✅ `.env` is in `.gitignore` - your keys are safe
- ✅ Never commit API keys to git
- ✅ Use environment variables for production (Heroku config)
- ✅ Rotate keys if exposed

---

**You're all set! The bot is ready to run.** 🚀
