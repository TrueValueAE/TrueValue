# 🚀 Build Dubai Estate AI with Claude Code

**Your Complete Guide to Building Locally with Claude as Your Pair Programmer**

---

## 📋 What You're Building

A **Telegram bot** that gives institutional-grade Dubai real estate analysis:

**Input (from agent):**
```
"Give me top 10 studios under 600K"
"Validate: Marina Gate 1, Unit 2506, AED 2.5M"
```

**Output (from bot):**
```
Complete 4-pillar analysis:
- Macro & Market context
- Liquidity & Exit strategy
- Technical & Engineering (chiller costs!)
- Legal & Regulatory compliance
- GO/NO-GO recommendation
```

---

## 🎯 Your Build Plan

### **Slice 0: Complete MVP (This Week)**

Build a single-file FastAPI app that:
1. Takes queries from Telegram
2. Calls Claude API with 15 analysis tools
3. Executes tools (searches Bayut, calculates costs, etc.)
4. Returns institutional-grade analysis
5. Works end-to-end

**Core Files:**
- `main.py` - Your entire backend (one file!)
- `requirements.txt` - Dependencies
- `.env` - API keys
- `Procfile` - For deployment

---

## 💻 Setup Your Development Environment

### **Step 1: Create Project Folder**

```bash
mkdir dubai-estate-ai
cd dubai-estate-ai
```

### **Step 2: Copy Files from Package**

From the downloaded `dubai-estate-agent.zip`, copy these files:

```bash
# Essential files
dubai-estate-ai/
├── main.py              # Your starter code
├── requirements.txt     # Dependencies
├── .env.template       # Copy to .env and fill
├── Procfile            # For deployment
└── README.md           # Reference
```

### **Step 3: Install Dependencies**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### **Step 4: Get API Keys**

#### **Required (to start):**

1. **Anthropic API Key** (5 minutes)
   - Go to: https://console.anthropic.com
   - Create account
   - Generate API key
   - Copy to `.env` as `ANTHROPIC_API_KEY`

2. **Bayut API Key** (5 minutes)
   - Go to: https://rapidapi.com/apicommunity/api/bayut
   - Sign up (free tier available)
   - Subscribe to API
   - Copy key to `.env` as `BAYUT_API_KEY`

3. **Telegram Bot Token** (3 minutes)
   - Open Telegram, find `@BotFather`
   - Send: `/newbot`
   - Follow prompts, name your bot
   - Copy token to `.env` as `TELEGRAM_BOT_TOKEN`

#### **Optional (add later):**

4. **Reddit API** (for building issues)
5. **Dubai REST API** (for title verification)

### **Step 5: Configure .env File**

```bash
cp .env.template .env
nano .env  # or use your editor
```

**Minimum .env to start:**
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
BAYUT_API_KEY=your_rapidapi_key
TELEGRAM_BOT_TOKEN=your_bot_token
```

---

## 🤖 Using Claude Code to Build

### **Open VS Code with Claude Code**

```bash
code .
```

### **Activate Claude Code**
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
- Type "Claude"
- Start chatting with Claude

---

## 💬 Conversation Flow with Claude Code

### **Session 1: Build Core Analysis Engine**

**You:** 
```
I need to build a Dubai real estate analysis system in main.py. 

Requirements:
1. FastAPI app
2. Takes property data as input
3. Runs 4-pillar institutional analysis:
   - Macro & Market (supply pipeline, trends)
   - Liquidity & Exit (DOM, transaction volume)
   - Technical (chiller costs, building issues)
   - Legal (service charges, disputes)
4. Returns structured analysis with GO/NO-GO recommendation

Start by implementing the core analyze_property() function that takes property data and returns complete analysis.

Here's the structure I want:

async def analyze_property(property_data: dict) -> dict:
    """
    Run complete 4-pillar analysis
    
    Input: property_data from Bayut API
    Output: {
        "property": {...},
        "macro": {...},
        "liquidity": {...},
        "technical": {...},
        "legal": {...},
        "investment": {...},
        "recommendation": {"decision": "GO/NO-GO", ...}
    }
    """
    # Implement this
```

**Claude will:**
- Write the complete function
- Add all sub-functions needed
- Include proper error handling
- Add type hints and docstrings

**Your next prompt:**
```
Good! Now implement the recommendation engine that takes the 4-pillar analysis and generates GO/NO-GO decision with reasoning.

Rules:
- 2+ red flags = DO NOT BUY
- 1 red flag + 2 yellow = CAUTION
- 3+ yellow flags = PROCEED WITH CAUTION
- Otherwise = GOOD INVESTMENT

Red flags:
- Overpriced >5%
- Net yield <3%
- Chiller cost >15/sqft
- Supply ratio >2.0
- DOM >90 days

Yellow flags:
- Overpriced 2-5%
- Net yield 3-4%
- Chiller cost 10-15/sqft
- Building issues 5-10
- DOM 60-90 days
```

---

### **Session 2: Add Bayut Integration**

**You:**
```
Now add Bayut API integration. I need:

1. search_bayut_properties(location, purpose, filters) function
   - Calls Bayut RapidAPI
   - Returns property listings
   - Handles pagination

2. get_property_details(property_id) function
   - Gets full property data
   - Calculates price per sqft
   - Extracts all needed fields

Use the Bayut API from RapidAPI:
Base URL: https://bayut.p.rapidapi.com/properties/list
Headers: X-RapidAPI-Key, X-RapidAPI-Host

The API key is in os.getenv("BAYUT_API_KEY")

Add proper error handling and timeouts (30 seconds).
```

**Claude will:**
- Implement both functions
- Add proper async/await
- Handle API errors gracefully
- Add timeout handling

---

### **Session 3: Add Chiller Cost Calculator**

**You:**
```
Implement the chiller cost calculator. This is CRITICAL - it's our unique value prop!

Function signature:
async def calculate_chiller_cost(provider: str, area_sqft: int) -> dict

Providers and rates:
- Empower: 
  - Consumption: 0.58 fils/kWh
  - Fixed capacity: AED 85/TR/month (THIS IS THE TRAP!)
  - 1 TR ≈ 285.7 sqft
  
- Lootah:
  - Consumption: 0.52 fils/kWh  
  - No fixed capacity charges

Calculate:
1. Estimated capacity (TR) = area_sqft / 285.7
2. Estimated consumption = area_sqft * 12 kWh/year
3. Consumption cost = consumption * rate / 100
4. Capacity cost = TR * monthly_rate * 12
5. Total annual cost
6. Cost per sqft per year
7. Warning level: HIGH if >15, MEDIUM if >10, LOW otherwise

Return detailed breakdown with warnings.
```

---

### **Session 4: Add Social Intelligence (Reddit Scraping)**

**You:**
```
Add Reddit integration to find building issues (snagging reports).

Function:
async def search_building_issues(building_name: str) -> dict

Requirements:
1. Use Reddit API (PRAW library)
2. Search subreddits: r/dubai, r/DubaiPetrolHeads
3. Look for keywords: snagging, defect, problem, issue, leak, crack
4. Search last 12 months
5. Return list of issues found with:
   - Source (reddit post URL)
   - Issue type (water damage, elevator, AC, etc.)
   - Severity (based on keywords)
   - Date posted

Reddit credentials are in .env:
REDDIT_CLIENT_ID
REDDIT_CLIENT_SECRET

Use PRAW library: pip install praw
```

---

### **Session 5: Add Market Trends Calculator**

**You:**
```
Implement market trends analysis using Bayut search data.

Function:
async def get_market_trends(location: str, purpose: str) -> dict

Logic:
1. Search recent properties in location (last 30 days)
2. Calculate:
   - Average price
   - Average price per sqft
   - Price range (min, max)
   - Total active listings
   - Market status (high/medium/low supply)
3. Compare to 90-day average (if we have cached data)

Return:
{
    "location": location,
    "total_listings": count,
    "avg_price": price,
    "avg_price_sqft": price_sqft,
    "price_range": {"min": x, "max": y},
    "market_status": "HIGH_SUPPLY" if >500 listings else "MODERATE",
    "trend": "RISING/STABLE/FALLING" (if historical data available)
}
```

---

### **Session 6: Add Supply Pipeline Estimator**

**You:**
```
Calculate supply pipeline risk from Bayut data.

Function:
async def get_supply_pipeline(zone: str) -> dict

Logic:
1. Search for off-plan/under-construction properties in zone
2. Filter by completion year (2025, 2026)
3. Count units
4. Search ready properties to get current inventory
5. Calculate completion ratio = future_units / current_inventory
6. Risk level:
   - HIGH if ratio > 2.0
   - MEDIUM if ratio > 0.5
   - LOW otherwise

Return full breakdown with risk assessment.
```

---

### **Session 7: Build Main Query Handler**

**You:**
```
Now build the main FastAPI endpoint that ties everything together.

POST /api/query
Input: {"query": "Find top 10 studios under 600K", "user_id": "xxx"}

Flow:
1. Parse query with Claude to extract intent and filters
2. If intent is "search_and_rank":
   - Search Bayut with filters
   - Analyze top 50 properties
   - Rank by investment score
   - Return top 10 with brief analysis
3. If intent is "validate_offer":
   - Get property details
   - Run full 4-pillar analysis
   - Return detailed recommendation

Use Claude API (Anthropic) to parse the query and orchestrate tools.

System prompt:
"You are a Dubai real estate analyst. Parse user queries and use available tools to provide institutional-grade analysis."

Available tools:
- search_bayut_properties
- analyze_property
- calculate_chiller_cost
- search_building_issues
- get_market_trends
- get_supply_pipeline

Implement the full tool-use loop (Claude calls tools, you execute, send results back, Claude responds).
```

---

### **Session 8: Add Telegram Bot**

**You:**
```
Create a simple Telegram bot (separate file: telegram_bot.py) that:

1. Receives messages from agents
2. Calls our FastAPI endpoint (http://localhost:8000/api/query)
3. Sends formatted response back

Use python-telegram-bot library.

Commands:
/start - Welcome message
/help - Show examples

Any text message = query to analyze

Format responses with Markdown:
- Bold for headers
- Emojis for visual appeal
- Clear sections for each pillar
- Highlight red flags with ⚠️ or ❌

Keep responses under 4096 chars (Telegram limit). If longer, split into multiple messages.
```

---

### **Session 9: Add Response Formatting**

**You:**
```
Create a response formatter that takes analysis dict and returns beautiful Telegram message.

Function:
def format_telegram_response(analysis: dict, query_type: str) -> str

For "top_10" queries:
- Show numbered list of top properties
- Each property: name, price, area, key metrics, brief recommendation
- Add summary at end

For "validate" queries:
- Full 4-pillar breakdown
- Each pillar with 3-5 key points
- Use emojis to show good/bad
- Clear GO/NO-GO recommendation
- Alternative suggestions

Make it look professional but easy to read on mobile.
```

---

### **Session 10: Add Error Handling & Logging**

**You:**
```
Add robust error handling throughout:

1. Try-catch all API calls
2. Return user-friendly error messages
3. Log errors to console with context
4. Handle rate limits gracefully
5. Add retry logic for transient failures (max 3 retries)

Also add request logging:
- Log every query received
- Log tools used
- Log response time
- Log any errors

Use Python's logging module, output to console for now.
```

---

## 🧪 Testing Your Build

### **Test 1: Run Locally**

```bash
# Terminal 1: Start API
python main.py
# Should see: "Uvicorn running on http://0.0.0.0:8000"

# Terminal 2: Test endpoint
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Find 2BR apartments in Marina under 2M", "user_id": "test"}'

# Should return analysis
```

### **Test 2: Test with Telegram Bot**

```bash
# Terminal 1: API running (from above)

# Terminal 2: Start bot
python telegram_bot.py

# Terminal 3: Message your bot on Telegram
# Send: "Find studios under 600K"
```

### **Test 3: Test Each Tool Individually**

Ask Claude Code:
```
Create a test_tools.py file with pytest tests for each function:
- test_search_bayut
- test_calculate_chiller_cost
- test_analyze_property
- etc.

Use mock data so we don't hit real APIs in tests.
```

---

## 📊 Prompts for Adding More Features

### **Add Caching**

**Prompt:**
```
Add Redis caching to reduce API calls:

1. Cache Bayut search results for 1 hour
2. Cache property details for 6 hours  
3. Cache market trends for 12 hours
4. Use property_id + timestamp as cache key

Add functions:
- get_cached(key)
- set_cached(key, value, ttl_seconds)

Use Redis URL from environment: REDIS_URL
Fall back to in-memory dict if Redis not available.
```

### **Add Database for User Tracking**

**Prompt:**
```
Add SQLite database to track:
- Users (user_id, join_date, tier)
- Queries (user_id, query, timestamp, tools_used)
- Usage limits (queries_today per user)

Use SQLAlchemy ORM.

Models:
- User(id, telegram_id, tier, created_at)
- Query(id, user_id, query_text, response, created_at)

Add middleware to check usage limits before processing query.
```

### **Add Subscription Management**

**Prompt:**
```
Add subscription tiers:
- Free: 3 queries/day
- Basic: 20 queries/day, AED 99/month
- Pro: 100 queries/day, AED 299/month

Functions:
- check_usage_limit(user_id) -> bool
- increment_usage(user_id)
- reset_daily_usage() (cron job)

Add /subscribe command to Telegram bot that shows pricing and Stripe payment link.
```

---

## 🚀 Deployment Prompts

### **Deploy to Railway**

**Prompt:**
```
Help me deploy to Railway.app:

1. Create railway.json config
2. Add start command
3. Set environment variables
4. Configure PostgreSQL database
5. Add health check endpoint

Then show me the exact commands to deploy.
```

### **Add Monitoring**

**Prompt:**
```
Add application monitoring:

1. Health check endpoint (/health) that returns:
   - API status
   - Database status
   - Redis status
   - Last successful query timestamp

2. Metrics endpoint (/metrics) that returns:
   - Total queries today
   - Average response time
   - Error rate
   - Active users

3. Add Sentry for error tracking (use SENTRY_DSN from env)
```

---

## 🎯 Example Complete Session

Here's what a full session with Claude Code looks like:

```
You: "I need to build the core analysis engine. Start with main.py structure."

Claude: [Creates complete FastAPI app skeleton with all imports and basic structure]

You: "Good! Now add the analyze_property function with 4 pillars."

Claude: [Implements full function with all sub-functions]

You: "Perfect! Add Bayut API integration."

Claude: [Adds search function with proper error handling]

You: "Now add chiller calculator with the rates I specified."

Claude: [Implements with all calculations and warnings]

You: "Add Reddit scraping for building issues."

Claude: [Implements PRAW integration with keyword search]

You: "Wire everything together in the main query handler."

Claude: [Creates endpoint with Claude API integration and tool orchestration]

You: "Add Telegram bot to interact with the API."

Claude: [Creates telegram_bot.py with message handling]

You: "Add beautiful response formatting for Telegram."

Claude: [Implements formatter with emojis and Markdown]

You: "Let's test it. Add some debug logging."

Claude: [Adds logging throughout]

You: "It works! Now add caching to reduce API costs."

Claude: [Implements Redis caching with fallback]

You: "Add user tracking and usage limits."

Claude: [Creates database models and middleware]

You: "Perfect! Help me deploy to Railway."

Claude: [Creates deployment config and instructions]
```

**Time: 3-4 hours of focused work with Claude**
**Result: Production-ready app**

---

## 📁 File Organization Tips

### **Keep It Simple (Slice 0)**

```
dubai-estate-ai/
├── main.py              # Everything here!
├── telegram_bot.py      # Bot interface
├── requirements.txt     # Dependencies
├── .env                 # Secrets
├── Procfile            # Deployment
└── README.md           # Docs
```

### **When to Split Files (Later)**

Only split when main.py > 1000 lines:

```
dubai-estate-ai/
├── main.py              # FastAPI app + routes
├── tools/
│   ├── bayut.py
│   ├── chiller.py
│   ├── reddit.py
│   └── analysis.py
├── models/
│   └── database.py
├── utils/
│   ├── cache.py
│   └── formatting.py
├── telegram_bot.py
└── requirements.txt
```

---

## 🐛 Common Issues & Solutions

### **Issue: Bayut API returns 403**
**Solution:**
```
Ask Claude: "Bayut API returns 403. Help me debug."

Claude will check:
1. API key format
2. Headers correct
3. Rate limits
4. Request structure
```

### **Issue: Claude API timeout**
**Solution:**
```
Ask Claude: "Claude API times out on complex queries. How to fix?"

Claude will:
1. Add timeout handling
2. Implement retry logic
3. Break into smaller tool calls
```

### **Issue: Telegram message too long**
**Solution:**
```
Ask Claude: "Response exceeds 4096 chars. Help split it."

Claude will:
1. Chunk message intelligently
2. Send multiple parts
3. Add "...continued" markers
```

---

## ✅ Success Checklist

After building with Claude, you should have:

- [ ] FastAPI app running on localhost:8000
- [ ] Can search Bayut properties
- [ ] Chiller cost calculator working
- [ ] 4-pillar analysis generating recommendations
- [ ] Telegram bot responding to queries
- [ ] Error handling in place
- [ ] Caching reducing API calls
- [ ] User tracking working
- [ ] Deployed to Railway/Heroku
- [ ] Real agent tested it successfully

---

## 🎓 Learning from Claude

**Best Practices:**

1. **Be Specific**
   - ❌ "Add Bayut search"
   - ✅ "Add async function to search Bayut API with filters for location, price range, and property type. Handle pagination and return max 25 results."

2. **Provide Context**
   - Share API docs
   - Show example responses
   - Explain business logic

3. **Iterate**
   - Build feature by feature
   - Test each piece
   - Refine based on results

4. **Ask for Explanations**
   - "Why did you use asyncio here?"
   - "Explain this error handling approach"
   - Learn as you build!

---

## 🚀 Next Steps

1. **Start with Session 1** (Core Analysis Engine)
2. **Test each function** as Claude builds it
3. **Move to Session 2** once working
4. **Deploy early** (after Session 7)
5. **Get real feedback** from agents
6. **Iterate** based on what they say

---

## 💡 Pro Tips

### **Use Claude Code Like a Senior Developer**

**Good prompts:**
```
"Implement X following the same pattern as Y"
"Add error handling like in function Z"
"Refactor this to be more maintainable"
"Add type hints and docstrings"
"Write unit tests for this function"
```

### **Claude Can Help You Learn**

```
"Explain why you chose this approach"
"What are the trade-offs here?"
"How would this scale to 1000 users?"
"What edge cases should I consider?"
```

### **Let Claude Handle Boilerplate**

```
"Add logging to all API calls"
"Create .env.template from .env"
"Write deployment documentation"
"Generate API documentation"
```

---

## 📞 When You Get Stuck

**Ask Claude:**
```
"I'm getting error X. Here's the full traceback: [paste]
Help me debug this."

"This function is slow. How can I optimize it?"

"I want to add feature X but not sure how to structure it. Suggestions?"
```

**Claude will:**
- Analyze the error
- Suggest fixes
- Explain why it happened
- Prevent it in future

---

## 🎉 You're Ready!

You have:
- ✅ Complete build plan
- ✅ Session-by-session prompts
- ✅ Testing strategy
- ✅ Deployment guide
- ✅ Troubleshooting tips

**Open VS Code, start Claude Code, and begin with Session 1!**

**You'll have a working MVP in 1 weekend of focused building.** 🚀

---

**Questions while building? Just ask Claude! It's like having a senior engineer pair programming with you 24/7.**
