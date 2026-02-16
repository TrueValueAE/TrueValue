# TrueValue AI

Institutional-grade Dubai real estate investment analysis, delivered via Telegram bot and REST API. Powered by Claude (Anthropic) with 12 specialized analysis tools, 15+ zone coverage, and cost-optimized AI queries (~$0.02/query).

## What It Does

Ask a question in natural language via Telegram or the API:

```
"Analyze a 1BR in Dubai Marina, AED 1.2M, 850 sqft"
```

TrueValue returns a scored investment verdict (0-100) covering:

- **Price Analysis** — comparison to zone averages, value assessment
- **Yield Calculation** — gross/net yield with real rental comps
- **Chiller Cost Warning** — Empower vs Lootah hidden cost detection (our moat)
- **Supply Risk** — pipeline analysis, oversupply detection
- **Liquidity Score** — days on market, transaction volume
- **Live Web Validation** — Brave Search for current market intel
- **DLD Transactions** — actual sold prices from Dubai Land Department
- **Mortgage Modeling** — EMI, total cost, cash vs leveraged returns

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      User Interfaces                      │
│  ┌─────────────────────┐  ┌────────────────────────────┐ │
│  │   Telegram Bot       │  │   FastAPI REST API          │ │
│  │   17 commands        │  │   /query  /health  /metrics │ │
│  └──────────┬──────────┘  └──────────────┬─────────────┘ │
└─────────────┼────────────────────────────┼───────────────┘
              └──────────┬─────────────────┘
                         │
              ┌──────────▼──────────┐
              │   main.py            │
              │   Claude Haiku 4.5   │
              │   12 Tool Functions  │
              │   Iterative Tool Use │
              └──────────┬──────────┘
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
  ┌─────▼──────┐  ┌──────▼───────┐  ┌─────▼──────┐
  │ PostgreSQL  │  │ Redis Cache  │  │ External   │
  │ 7 tables    │  │ Per-tool TTL │  │ APIs       │
  │ asyncpg     │  │ aioredis     │  │            │
  └────────────┘  └──────────────┘  └─────┬──────┘
                                          │
                                    ┌─────┴──────┐
                                    │ Bayut      │
                                    │ Brave      │
                                    │ DLD        │
                                    │ Telegram   │
                                    └────────────┘
```

**Background services:**
- Digest Scheduler — hourly check, sends daily/weekly market digests to subscribers
- Observability Stack — Prometheus, Grafana, Loki, Tempo (Docker Compose)

## 12 Analysis Tools

| Tool | Description | Cache TTL |
|------|-------------|-----------|
| `search_bayut_properties` | Property listings from Bayut API + mock fallback | 1 hour |
| `get_market_trends` | Price trends, yield estimates, occupancy by zone | 1 hour |
| `get_supply_pipeline` | Upcoming supply, risk level, pipeline units | 6 hours |
| `analyze_investment` | 4-pillar investment scoring (0-100) | 1 hour |
| `calculate_chiller_cost` | Empower/Lootah/Palm cost breakdown + warnings | 24 hours |
| `compare_properties` | Side-by-side comparison matrix | none |
| `verify_title_deed` | Ownership, encumbrances, DLD verification | 24 hours |
| `search_building_issues` | Snagging reports from Reddit + web search | 6 hours |
| `web_search_dubai` | Live Brave Search with Dubai context | 1 hour |
| `calculate_mortgage` | EMI, total cost, cash vs leveraged yield | none |
| `get_dld_transactions` | DLD actual sold prices, volume, trends | 24 hours |
| `get_rental_comps` | Real rental comparables, demand indicator | 1 hour |

## 15+ Zones Covered

Dubai Marina, Downtown Dubai, Business Bay, JBR, Palm Jumeirah, JVC, International City, Dubai South, JLT, Arjan, Dubai Hills, Arabian Ranches, City Walk, Creek Harbour, Emaar Beachfront

Each zone has curated data for: yield estimates, service charges, average PSF, liquidity scores, supply pipeline risk, and mock property listings.

## Telegram Bot Commands

**Analysis:**
`/analyze` `/search` `/compare` `/help`

**Watchlist:**
`/save` `/watchlist` `/remove`

**Account:**
`/start` `/subscription` `/referral`

**Market Digest:**
`/digest` `/digest_off`

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (optional — graceful degradation to in-memory)
- Redis (optional — runs without caching)

### Setup

```bash
# Clone and enter directory
cd TrueValue

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Required Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...    # Required — Claude API
TELEGRAM_BOT_TOKEN=123456:ABC... # Required — Telegram bot
```

### Optional Environment Variables

```bash
BAYUT_API_KEY=...          # RapidAPI key for live Bayut data (falls back to mock)
BRAVE_API_KEY=...          # Brave Search API for live web search
DATABASE_URL=postgresql://user:pass@host:5432/truevalue
REDIS_URL=redis://localhost:6379
STRIPE_SECRET_KEY=sk_...   # Stripe for subscription payments
OPENAI_API_KEY=sk-...      # OpenAI Whisper for voice transcription
```

### Run

```bash
python run.py
```

This starts three concurrent services:
1. **FastAPI** on port 8000 (REST API + metrics)
2. **Telegram bot** in polling mode
3. **Digest scheduler** (hourly market digest checks)

For webhook mode (production):
```bash
BOT_MODE=webhook python run.py
```

## Database

PostgreSQL via asyncpg with 7 tables:

| Table | Purpose |
|-------|---------|
| `users` | User accounts, tiers, query counts, bonus queries, referral codes |
| `conversations` | Chat history for context |
| `query_logs` | Query analytics and cost tracking |
| `subscription_events` | Stripe subscription lifecycle |
| `saved_properties` | User watchlist (JSONB property data) |
| `referrals` | Referral tracking with bonus allocation |
| `digest_preferences` | Market digest subscriptions (zones, frequency) |

Tables are created automatically on startup. Runs without a database (in-memory fallback).

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all 118 tests
python -m pytest tests/test_all.py -v

# Run with Claude API e2e tests (requires ANTHROPIC_API_KEY)
ANTHROPIC_API_KEY=sk-ant-... python -m pytest tests/test_all.py -v
```

## Observability

Optional Docker Compose stack for monitoring:

```bash
cd observability
docker-compose up -d
```

- **Grafana** — http://localhost:3000 (admin/admin)
- **Prometheus** — http://localhost:9090
- **Loki** — log aggregation
- **Tempo** — distributed tracing

See [GRAFANA_OBSERVABILITY_GUIDE.md](GRAFANA_OBSERVABILITY_GUIDE.md) for dashboard details.

## Project Structure

```
TrueValue/
├── main.py                 # FastAPI app + Claude tool-use engine (12 tools)
├── run.py                  # Entry point — runs FastAPI + bot + digest scheduler
├── database.py             # PostgreSQL via asyncpg (7 tables)
├── cache.py                # Redis caching with per-tool TTLs
├── digest.py               # Market digest generator + scheduler
├── payments.py             # Stripe subscription management
├── observability.py        # Prometheus metrics + structured logging
├── conversation.py         # Conversation context management
├── transcription.py        # Voice message transcription (Whisper)
├── telegram-bot/
│   └── bot.py              # Telegram bot (17 commands + inline buttons)
├── tests/
│   ├── test_all.py         # 118 tests (unit + integration)
│   └── conftest.py         # Test fixtures
├── observability/          # Docker Compose monitoring stack
│   ├── docker-compose.yml
│   ├── prometheus/
│   ├── loki/
│   ├── tempo/
│   └── grafana/
├── .env                    # Environment variables (gitignored)
└── requirements.txt        # Python dependencies
```

## Cost

Claude Haiku 4.5 with optimized system prompt and 7-iteration cap:

- **Average query cost**: ~$0.02
- **91% reduction** from initial Sonnet-based architecture
- Per-tool caching reduces redundant API calls

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — Detailed system architecture and data flows
- [CONTEXT.md](CONTEXT.md) — Dubai real estate domain knowledge
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — Production deployment strategies
- [MONETIZATION_GUIDE.md](MONETIZATION_GUIDE.md) — Business model and pricing tiers
- [GRAFANA_OBSERVABILITY_GUIDE.md](GRAFANA_OBSERVABILITY_GUIDE.md) — Monitoring stack guide

## License

MIT
