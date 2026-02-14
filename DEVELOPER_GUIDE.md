# 🏗️ Recommended Architecture for Developers

## For: Developers who want to build fast and scale later

---

## 🎯 TLDR - Best Setup

### Phase 1: MVP (Weeks 1-4)
```
Single Server / Your Laptop
├── One FastAPI/Express app
├── Claude API calls
├── Direct API calls to Bayut, Property Finder, etc.
└── Deploy to Heroku (one click)
```

### Phase 2: Scale (Months 3-6)
```
Microservices
├── Main API (FastAPI/Express)
├── MCP Gateway (consolidates all MCP servers)
├── Database (PostgreSQL)
├── Redis Cache
└── Deploy to Docker/AWS
```

### Phase 3: Production (Months 6+)
```
Full Microservices
├── Separate MCP servers (containerized)
├── Load balancer
├── Auto-scaling
├── Monitoring
└── Multi-region
```

---

## 🚀 The Fastest Path (What I Recommend)

### **Architecture: Monolith → Gateway → Microservices**

#### Step 1: Start with Monolith (Week 1)

```python
# main.py - Everything in one file

from fastapi import FastAPI
from anthropic import Anthropic
import httpx
import os

app = FastAPI()
claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Define tools inline
async def search_bayut(location: str, purpose: str, min_price: int = None):
    """Call Bayut API directly"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://bayut.p.rapidapi.com/properties/list",
            params={
                "locationExternalIDs": location,
                "purpose": purpose,
                "priceMin": min_price or 0,
                "hitsPerPage": 25
            },
            headers={
                "X-RapidAPI-Key": os.getenv("BAYUT_API_KEY"),
                "X-RapidAPI-Host": "bayut.p.rapidapi.com"
            }
        )
        return response.json()

async def calculate_chiller_cost(provider: str, area_sqft: int):
    """Calculate chiller costs - no external API needed"""
    rates = {
        "empower": {"consumption": 0.58, "capacity": 85},
        "lootah": {"consumption": 0.52, "capacity": 0}
    }
    # Your calculation logic here
    return {"total_annual_cost": 22500}  # Example

# Main endpoint
@app.post("/api/query")
async def handle_query(query: str):
    """Main query handler"""
    
    # Call Claude with tools
    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        tools=[
            {
                "name": "search_bayut",
                "description": "Search Bayut for properties",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "purpose": {"type": "string"},
                        "min_price": {"type": "number"}
                    }
                }
            },
            {
                "name": "calculate_chiller_cost",
                "description": "Calculate chiller costs",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "provider": {"type": "string"},
                        "area_sqft": {"type": "number"}
                    }
                }
            }
        ],
        messages=[{"role": "user", "content": query}]
    )
    
    # If Claude wants to use tools
    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use":
                # Execute tool
                if block.name == "search_bayut":
                    result = await search_bayut(**block.input)
                elif block.name == "calculate_chiller_cost":
                    result = await calculate_chiller_cost(**block.input)
                
                # Send result back to Claude
                # (simplified - in production, loop until done)
        
    return {"response": "Final answer here"}

# Run: uvicorn main:app --reload
```

**Deploy to Heroku:**
```bash
git init
heroku create dubai-estate-api
git push heroku main
```

**Time to launch: 1 week**

---

#### Step 2: Extract to Gateway (Month 2)

When you have 100+ users, split into:

```
┌─────────────────────────────────────────┐
│  Main App (Telegram Bot / API)         │
│  - User interface                       │
│  - Calls Claude API                     │
│  - Routes tool requests to Gateway      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  MCP Gateway (mcp-gateway/server.js)    │
│  - Single HTTP server                   │
│  - Exposes all tools via REST           │
│  - Calls external APIs                  │
│  - Handles caching                      │
└─────────────────────────────────────────┘
```

**Benefits:**
- Main app stays simple
- Gateway handles all MCP logic
- Easy to cache responses
- One server to deploy

---

#### Step 3: Microservices (Month 6+)

When you have 1000+ users, separate services:

```
┌──────────────┐
│   Main App   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────┐
│        API Gateway (Kong/Nginx)          │
└────┬─────┬─────┬─────┬─────┬─────┬──────┘
     │     │     │     │     │     │
     ▼     ▼     ▼     ▼     ▼     ▼
   Bayut Dubai Chiller Social Property ...
   MCP   REST  MCP     MCP    Finder
   (8001)(8002)(8003) (8004)  (8005)
```

Each MCP server runs in its own container, can scale independently.

---

## 💻 Local Development Setup

### What You'll Actually Run:

```bash
# Terminal 1: Main app (one file!)
cd dubai-estate-agent
python main.py
# Runs on localhost:8000

# That's it! Everything else is API calls.
```

### File Structure:

```
dubai-estate-agent/
├── main.py                 # Everything here to start
├── requirements.txt        # Just: fastapi, anthropic, httpx
├── .env                    # API keys
└── Procfile               # For Heroku: "web: uvicorn main:app"
```

**Lines of code: ~200**

---

## 🐳 When to Use Docker

### Don't Use Docker For:
- ❌ Local development (overkill)
- ❌ MVP / first 100 users
- ❌ Heroku deployment (they handle it)

### Use Docker When:
- ✅ Deploying to AWS/DigitalOcean
- ✅ Multiple services to orchestrate
- ✅ Team of developers
- ✅ Need reproducible environments

---

## 🗄️ Database Strategy

### Phase 1 (MVP): SQLite
```python
# No setup needed!
import sqlite3
conn = sqlite3.connect('users.db')
```

### Phase 2 (100+ users): PostgreSQL
```python
# Heroku Postgres (free tier)
DATABASE_URL = os.getenv("DATABASE_URL")
```

### Phase 3 (1000+ users): Managed PostgreSQL
```python
# AWS RDS or DigitalOcean Managed DB
```

---

## ⚡ Caching Strategy

### Phase 1: No cache
Just call APIs directly

### Phase 2: Simple dict cache
```python
from datetime import datetime, timedelta

cache = {}

def get_cached(key, ttl_minutes=60):
    if key in cache:
        value, timestamp = cache[key]
        if datetime.now() - timestamp < timedelta(minutes=ttl_minutes):
            return value
    return None

def set_cache(key, value):
    cache[key] = (value, datetime.now())
```

### Phase 3: Redis
```python
import redis
r = redis.Redis(host='localhost', port=6379)
```

---

## 📊 Where MCP Servers Actually Run

### Development (Your Laptop):
```
You don't run separate MCP servers!
All logic is in main.py
```

### Production (Cloud):

**Option A: Monolith (Recommended for start)**
```
Heroku Dyno
├── Your app (main.py)
└── Calls external APIs directly
```

**Option B: Gateway**
```
Server 1: Main app
Server 2: MCP Gateway (consolidates all tools)
```

**Option C: Microservices (Later)**
```
Container 1: Main app
Container 2: Bayut MCP
Container 3: Dubai REST MCP
Container 4: Chiller MCP
...
```

---

## 🎯 My Specific Recommendation for YOU

### Week 1: One File, One Server

```python
# main.py
from fastapi import FastAPI
from anthropic import Anthropic
import httpx

# Put ALL logic here:
# - Bayut search
# - Chiller calculator
# - Dubai REST calls
# - Reddit scraping
# - Everything!

# Total: ~500 lines of code
```

Deploy to Heroku: `git push heroku main`

**Cost: $0 (Heroku free tier)**

### Month 2: Split to Gateway

Create `mcp-gateway/server.js` (I already created this for you!)

Move all tool logic there.

Main app just calls:
```python
tool_result = await httpx.post(
    "http://localhost:8000/api/bayut/search",
    json={"location": "marina", "purpose": "sale"}
)
```

**Cost: ~$30/month (2 servers)**

### Month 6: Microservices (if needed)

Only if you have:
- 1000+ users
- Multiple developers
- Need to scale different parts independently

**Cost: ~$200/month**

---

## 🛠️ Using Claude Code (Claude.ai Desktop)

Since you'll use Claude Code to build this:

### Setup Claude Code with Your Codebase:

```bash
# In your project
code .

# Claude Code can help you:
# - Write the monolith main.py
# - Debug API calls
# - Write tests
# - Refactor when ready to split
```

### What to Ask Claude Code:

```
"Help me write a FastAPI app that:
1. Takes a user query
2. Calls Claude API with tools
3. Executes tools by calling Bayut API, calculating chiller costs
4. Returns result to user"
```

Claude Code will write it for you in ~5 minutes.

---

## 📝 Checklist for Week 1

- [ ] Create `main.py` with FastAPI
- [ ] Add Anthropic SDK
- [ ] Implement 3 core tools:
  - [ ] Bayut search (call their API)
  - [ ] Chiller calculator (math only, no API)
  - [ ] Dubai REST (call their API)
- [ ] Test locally
- [ ] Deploy to Heroku
- [ ] Create Telegram bot that calls your API

**Total time: 1-2 days of coding**

---

## 🎓 Learning Resources

### FastAPI Tutorial:
https://fastapi.tiangolo.com/tutorial/

### Anthropic Tool Use:
https://docs.anthropic.com/claude/docs/tool-use

### Deploying to Heroku:
https://devcenter.heroku.com/articles/getting-started-with-python

---

## 💡 Key Insight

**You don't need MCP servers as separate processes!**

MCP is just a protocol. You can:

1. **Option A**: Implement tools directly in your app (fastest)
2. **Option B**: Run MCP servers and call them via HTTP (scalable)
3. **Option C**: Use OpenClaw's stdio approach (only for dev tools)

For a **product that makes money**, Option A → Option B is the path.

---

## 🚀 Final Recommendation

```python
# Week 1: Start here
main.py (500 lines, everything inline)
    ↓
# Month 2: If growing
main.py + mcp-gateway (2 servers)
    ↓
# Month 6: If scaling
Docker Compose (5-10 microservices)
```

**Don't over-engineer early. Ship fast, refactor later.**

---

## ❓ FAQ

**Q: Do I run the MCP servers in the package?**
A: No! Start by calling APIs directly from your main app.

**Q: When do I need separate MCP servers?**
A: When you have 1000+ users and need to scale.

**Q: Can I use OpenClaw?**
A: Use Claude Code to BUILD your app, but the app itself doesn't use OpenClaw.

**Q: Where does this run in production?**
A: Heroku/AWS/DigitalOcean - one server to start.

---

**Ready to code? Ask Claude Code to generate `main.py` for you! 🚀**
