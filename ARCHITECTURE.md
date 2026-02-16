# TrueValue AI — System Architecture

## Overview

TrueValue AI is a monolithic Python application that provides AI-powered Dubai real estate investment analysis through two interfaces: a Telegram bot and a FastAPI REST API. The AI engine uses Claude Haiku 4.5 with iterative tool calling (up to 7 iterations) across 12 specialized analysis tools.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACES                                 │
│                                                                              │
│  ┌──────────────────────────────┐    ┌──────────────────────────────────┐   │
│  │     Telegram Bot              │    │     FastAPI REST API              │   │
│  │     telegram-bot/bot.py       │    │     main.py                      │   │
│  │                               │    │                                   │   │
│  │  Commands:                    │    │  Endpoints:                       │   │
│  │  /analyze  /search  /compare  │    │  POST /query    — AI analysis     │   │
│  │  /save  /watchlist  /remove   │    │  GET  /health   — health check    │   │
│  │  /referral  /subscription     │    │  GET  /metrics  — Prometheus      │   │
│  │  /digest  /digest_off         │    │  POST /feedback — user feedback   │   │
│  │  /start  /help                │    │  POST /webhook/telegram           │   │
│  │                               │    │                                   │   │
│  │  Inline Buttons:              │    │                                   │   │
│  │  Full Report | Compare        │    │                                   │   │
│  │  Mortgage | Web Search        │    │                                   │   │
│  │  Save | Remove                │    │                                   │   │
│  └──────────────┬───────────────┘    └──────────────────┬───────────────┘   │
└─────────────────┼───────────────────────────────────────┼───────────────────┘
                  └───────────────────┬───────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AI ORCHESTRATION ENGINE                              │
│                               main.py                                        │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        handle_query()                                │    │
│  │  1. Receive query + user context                                     │    │
│  │  2. Build system prompt (domain expertise + tool definitions)        │    │
│  │  3. Call Claude Haiku 4.5 API                                        │    │
│  │  4. Loop: execute tool calls → feed results back → repeat            │    │
│  │  5. Return final text response (max 7 iterations)                    │    │
│  └──────────────────────────────┬──────────────────────────────────────┘    │
│                                  │                                           │
│  ┌───────────────────────────────▼──────────────────────────────────────┐   │
│  │                    _execute_tool() + Cache Layer                      │   │
│  │                                                                       │   │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                   │   │
│  │  │  MARKET DATA         │  │  FINANCIAL           │                   │   │
│  │  │  search_bayut_props  │  │  analyze_investment   │                   │   │
│  │  │  get_market_trends   │  │  calculate_chiller    │                   │   │
│  │  │  get_supply_pipeline │  │  calculate_mortgage   │                   │   │
│  │  │  web_search_dubai    │  │  get_rental_comps     │                   │   │
│  │  │  get_dld_transactions│  │                       │                   │   │
│  │  └─────────────────────┘  └─────────────────────┘                   │   │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                   │   │
│  │  │  BUILDING INTEL      │  │  UTILITY             │                   │   │
│  │  │  search_bldg_issues  │  │  compare_properties   │                   │   │
│  │  │  verify_title_deed   │  │                       │                   │   │
│  │  └─────────────────────┘  └─────────────────────┘                   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└────────┬──────────────────────────┬──────────────────────────┬──────────────┘
         │                          │                          │
         ▼                          ▼                          ▼
┌─────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
│  PostgreSQL      │    │  Redis Cache          │    │  External APIs       │
│  database.py     │    │  cache.py             │    │                      │
│                  │    │                        │    │  Anthropic Claude    │
│  7 Tables:       │    │  Per-tool TTLs:        │    │  Bayut (RapidAPI)   │
│  users           │    │  search: 3600s         │    │  Brave Search       │
│  conversations   │    │  trends: 3600s         │    │  DLD Open Data      │
│  query_logs      │    │  pipeline: 21600s      │    │  Telegram Bot API   │
│  subscription_   │    │  investment: 3600s     │    │                      │
│    events        │    │  chiller: 86400s       │    │  Fallback:           │
│  saved_          │    │  title: 86400s         │    │  All tools have      │
│    properties    │    │  issues: 21600s        │    │  curated mock data   │
│  referrals       │    │  web: 3600s            │    │  for offline use     │
│  digest_         │    │  dld: 86400s           │    │                      │
│    preferences   │    │  rental: 3600s         │    │                      │
└─────────────────┘    └──────────────────────┘    └──────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          BACKGROUND SERVICES                                 │
│                                                                              │
│  ┌──────────────────────────────┐    ┌──────────────────────────────────┐   │
│  │  Digest Scheduler             │    │  Observability Stack (Docker)     │   │
│  │  digest.py                    │    │  observability/                   │   │
│  │                               │    │                                   │   │
│  │  - Runs every 1 hour         │    │  Prometheus → metrics storage     │   │
│  │  - Checks digest_preferences │    │  Grafana    → dashboards          │   │
│  │  - Generates market digests   │    │  Loki      → log aggregation     │   │
│  │  - Sends via Telegram API     │    │  Tempo     → distributed tracing │   │
│  │  - Daily + weekly frequency   │    │  Promtail  → log shipping        │   │
│  └──────────────────────────────┘    └──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Entry Point (`run.py`)

```python
asyncio.gather(
    start_fastapi(),           # uvicorn on port 8000
    start_telegram_bot(),      # polling mode
    start_digest_scheduler(),  # hourly digest cycle
)
```

In webhook mode (`BOT_MODE=webhook`), only FastAPI runs — the bot receives updates via `/webhook/telegram`.

## AI Engine — Tool Calling Flow

```
User Query
    │
    ▼
Claude Haiku 4.5  (temperature=0.2, max_tokens=4000)
    │
    ├─ Returns tool_use blocks?
    │   YES ──▶ Execute each tool
    │           │
    │           ├─ Check Redis cache first
    │           │   HIT  ──▶ Return cached result
    │           │   MISS ──▶ Call tool function
    │           │            │
    │           │            ├─ Try live API (Bayut, Brave, DLD)
    │           │            │   SUCCESS ──▶ Cache result, return
    │           │            │   FAIL    ──▶ Use mock data fallback
    │           │            │
    │           │            └─ Return JSON result
    │           │
    │           └─ Feed tool_results back to Claude
    │              └─ Loop (max 7 iterations)
    │
    └─ Returns text response (no more tools)?
        └─ Return final analysis to user
```

**Cost optimization**: Claude Haiku 4.5 instead of Sonnet. 7-iteration cap. Per-tool caching. Result: ~$0.02/query (91% reduction from original).

## Investment Scoring (4-Pillar Framework)

The `analyze_investment` tool calculates a 0-100 score:

| Pillar | Weight | What It Measures |
|--------|--------|------------------|
| Price | 30 pts | Price per sqft vs zone average |
| Yield | 25 pts | Gross yield from zone yield map |
| Liquidity | 20 pts | Transaction volume / days on market |
| Quality/Supply | 15 pts | Supply pipeline risk level |
| Chiller | 10 pts | Cooling cost warning level |

**Verdict mapping**: 80-100 Strong Buy, 60-79 Good Buy, 40-59 Caution, 20-39 Negotiate, 0-19 Do Not Buy.

## Zone Data Architecture

Each of the 15+ zones has synchronized data across 6 maps in `main.py`:

| Map | Purpose | Example (Dubai Marina) |
|-----|---------|----------------------|
| `BAYUT_LOCATION_IDS` | API location code | `5002` |
| `LOCATION_ALIASES` | Fuzzy name matching | `marina`, `dubai marina` → `dubai-marina` |
| `zone_yield_map` | Gross yield estimate | `0.065` (6.5%) |
| `sc_per_sqft_map` | Service charge/sqft | `22` AED |
| `zone_avg_psf_map` | Average price/sqft | `1600` AED |
| `liquidity_map` | Liquidity score (0-20) | `18` |
| `SUPPLY_PIPELINE` | Risk level + units | `MODERATE`, 8500 units |
| `MOCK_PROPERTIES` | Fallback listings | 3 representative properties |

## Database Schema

```sql
-- Core user management
users (user_id, username, tier, queries_today, total_queries,
       bonus_queries, referral_code, created_at, last_query)

-- Chat context
conversations (id, user_id, role, content, created_at)

-- Analytics
query_logs (id, user_id, query, tools_used, response_time_ms,
            token_count, cost_usd, created_at)

-- Payments
subscription_events (id, user_id, event_type, tier, stripe_sub_id,
                     amount_usd, created_at)

-- Watchlist
saved_properties (id, user_id, property_data JSONB, notes, saved_at)
  UNIQUE(user_id, property_data->>'id')

-- Referral system
referrals (id, referrer_id, referee_id, created_at, bonus_awarded)
  UNIQUE(referee_id)

-- Market digests
digest_preferences (user_id PK, frequency, zones TEXT[], enabled,
                    last_sent, created_at)
```

All tables are created idempotently on startup via `SCHEMA_DDL`. Column migrations run via `SCHEMA_MIGRATIONS`. The entire database layer is optional — all functions return safe defaults when the connection pool is `None`.

## Caching Strategy

Redis via `aioredis` with transparent cache wrapping in `_execute_tool`:

1. Before calling any tool, check Redis for `tool_name:hash(args)`
2. On cache hit, return stored JSON immediately
3. On cache miss, execute tool, store result with tool-specific TTL
4. On Redis unavailable, skip caching (no errors propagated)

TTLs are tuned per tool: calculations with static data get 24h, market data gets 1h, supply pipeline gets 6h.

## Telegram Bot Architecture

`telegram-bot/bot.py` uses `python-telegram-bot` (async):

- **Registration**: `/start` creates user in DB, handles referral deep links (`?start=ref_USERID`)
- **Query handling**: Free text → `handle_query()` → response with inline buttons
- **Inline buttons**: Full Report, Compare, Mortgage, Web Search, Save, Remove
- **Rate limiting**: Per-tier daily query limits (free=5, pro=10, enterprise=unlimited) + bonus queries from referrals
- **Message splitting**: Auto-splits responses at 4096 character Telegram limit
- **Progress indicator**: "Analyzing..." message shown during 30-60s analysis

## Digest System

```
digest.py
  │
  ├── generate_digest(zones)
  │   - Calls get_market_trends() + get_supply_pipeline() per zone
  │   - Formats compact Telegram message with risk emojis
  │   - Returns formatted string
  │
  └── start_digest_scheduler()
      - Infinite loop, sleeps 3600s between cycles
      - _run_digest_cycle():
        - Query digest_preferences for daily/weekly subscribers
        - Check if last_sent is older than frequency interval
        - Generate digest, send via Telegram Bot API HTTP POST
        - Update last_sent timestamp
```

## Referral System

1. User runs `/referral` → gets unique link `https://t.me/BotName?start=ref_USERID`
2. New user clicks link → `/start ref_USERID` → `create_referral()` in DB
3. Referrer gets 10 bonus queries, referee gets 5
4. Bonus queries added to `users.bonus_queries`, included in rate limit check

## Error Handling

Every tool follows the same pattern:

```
Try live API call
  → Success: return structured data
  → Failure (timeout, 404, rate limit, missing key):
      → Fall back to curated mock data
      → Add "source": "mock" to response
      → Continue analysis (degraded but functional)
```

Claude receives the mock data and can note data freshness in its response. No tool failure causes a query to fail entirely.

## Observability

`observability.py` exports Prometheus metrics:

| Metric | Type | Labels |
|--------|------|--------|
| `dubai_estate_queries_total` | Counter | status, tier |
| `dubai_estate_tool_calls_total` | Counter | tool_name, status |
| `dubai_estate_query_duration_seconds` | Histogram | — |
| `dubai_estate_claude_tokens` | Histogram | type (input/output) |
| `dubai_estate_errors_total` | Counter | error_type |

Scraped by Prometheus at `GET /metrics`. Grafana dashboards in `observability/grafana/provisioning/dashboards/`.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| Web Framework | FastAPI + uvicorn |
| AI | Claude Haiku 4.5 (Anthropic API) |
| Bot | python-telegram-bot 21+ (async) |
| Database | PostgreSQL via asyncpg |
| Cache | Redis via aioredis |
| HTTP Client | httpx (async) |
| Search | Brave Search API |
| Real Estate Data | Bayut via RapidAPI |
| Payments | Stripe |
| Transcription | OpenAI Whisper |
| Metrics | prometheus-client |
| Monitoring | Prometheus, Grafana, Loki, Tempo |

## File Reference

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | ~3000 | FastAPI app, 12 tools, Claude engine, zone data |
| `database.py` | ~640 | PostgreSQL schema, 7 tables, ~20 query functions |
| `telegram-bot/bot.py` | ~1350 | Telegram bot, 17 commands, inline buttons |
| `cache.py` | ~140 | Redis cache with per-tool TTLs |
| `digest.py` | ~145 | Digest generator + hourly scheduler |
| `run.py` | ~125 | Entry point, starts 3 async services |
| `observability.py` | ~200 | Prometheus metrics + logging |
| `payments.py` | ~150 | Stripe subscription management |
| `conversation.py` | ~100 | Conversation context helper |
| `transcription.py` | ~80 | Whisper voice transcription |
| `tests/test_all.py` | ~700 | 118 tests (unit + integration + e2e) |
