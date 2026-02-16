# TrueValue AI — Developer Guide

## Project Structure

```
TrueValue/
├── main.py                 # FastAPI app + Claude tool-use engine (12 tools)
├── run.py                  # Entry point — asyncio.gather(FastAPI, bot, digest)
├── database.py             # PostgreSQL via asyncpg (7 tables)
├── cache.py                # Redis caching with per-tool TTLs
├── digest.py               # Market digest generator + hourly scheduler
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
│   └── grafana/provisioning/
├── .env                    # Environment variables (gitignored)
└── requirements.txt
```

## Local Development Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Set at minimum: ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN

# Run the application
python run.py
```

This starts three async services via `asyncio.gather`:
1. FastAPI on port 8000
2. Telegram bot (polling mode)
3. Digest scheduler (hourly cycle)

## How the AI Engine Works

### Tool-Use Loop (`main.py`)

The core logic is in `handle_query()`:

1. Build a system prompt with Dubai real estate expertise + 12 tool schemas
2. Send user query to Claude Haiku 4.5
3. If Claude returns `tool_use` blocks, execute each tool via `_execute_tool()`
4. Feed tool results back to Claude as `tool_result` messages
5. Repeat until Claude returns a text response (or 7 iteration cap)

### Adding a New Tool

1. Write the async function in `main.py`:
```python
async def my_new_tool(param1: str, param2: int = 10) -> dict:
    # Try live API, fall back to mock data
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.example.com/...", timeout=10.0)
            if resp.status_code == 200:
                return resp.json()
    except Exception:
        pass
    # Mock fallback
    return {"result": "mock data", "source": "mock"}
```

2. Add the tool schema to the `TOOLS` list:
```python
{
    "name": "my_new_tool",
    "description": "What this tool does — be specific for Claude",
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."},
            "param2": {"type": "integer", "description": "..."}
        },
        "required": ["param1"]
    }
}
```

3. Add the dispatch entry in `_execute_tool_raw()`:
```python
elif tool_name == "my_new_tool":
    return await my_new_tool(**tool_input)
```

4. Optionally add a cache TTL in `cache.py`:
```python
CACHE_TTLS = {
    ...
    "my_new_tool": 3600,  # 1 hour
}
```

5. Add tests in `tests/test_all.py`.

### Zone Data Maps

When adding a new zone, you must update all 6 synchronized maps:

- `BAYUT_LOCATION_IDS` — Bayut API location code
- `LOCATION_ALIASES` — fuzzy name variants → canonical slug
- `zone_yield_map` — gross yield estimate (inside `get_market_trends`)
- `sc_per_sqft_map` — service charge per sqft (inside `analyze_investment`)
- `zone_avg_psf_map` — average price per sqft (inside `analyze_investment`)
- `liquidity_map` — liquidity score 0-20 (inside `analyze_investment`)
- `SUPPLY_PIPELINE` — risk level, units in pipeline
- `MOCK_PROPERTIES` — 3 representative mock listings

## Database

### Schema

PostgreSQL via asyncpg. Tables are created on startup via `SCHEMA_DDL` in `database.py`. Column migrations run via `SCHEMA_MIGRATIONS`.

The database is entirely optional. When `DATABASE_URL` is not set or connection fails, all database functions return safe defaults (empty lists, None, False). This allows the app to run without PostgreSQL.

### Adding a New Table

1. Add the `CREATE TABLE` statement to `SCHEMA_DDL` in `database.py`
2. Add any `ALTER TABLE` column additions to `SCHEMA_MIGRATIONS`
3. Write async functions (e.g., `async def get_thing(...)`)
4. Always guard with `if _pool is None: return default`
5. Add cleanup to `tests/conftest.py` `db_pool` fixture

## Cache

Redis via aioredis. The cache layer wraps tool execution in `_execute_tool()`:

- Before executing a tool, check Redis for `tool_name:sha256(args)`
- On hit, return cached JSON
- On miss, execute tool, store with tool-specific TTL
- On Redis unavailable, skip silently

Like the database, Redis is optional. Without `REDIS_URL`, caching is disabled.

## Telegram Bot

### Adding a New Command

1. Write the handler in `telegram-bot/bot.py`:
```python
async def cmd_mycommand(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text("Response here")
```

2. Register it in `setup_handlers()`:
```python
self.app.add_handler(CommandHandler("mycommand", self.cmd_mycommand))
```

3. Update the `/help` command text.

4. Run `python set_bot_commands.py` to update the Telegram command menu.

### Inline Buttons

Add callback handlers in `handle_callback()`. Callback data uses prefixes for routing:
- `full_` — full report
- `compare_` — comparison
- `mortgage_` — mortgage calculator
- `websearch_` — web search
- `save_` — save to watchlist
- `removeprop_` — remove from watchlist

## Testing

```bash
# Run all tests (118 total)
python -m pytest tests/test_all.py -v

# Run a specific test class
python -m pytest tests/test_all.py::TestMortgageCalculator -v

# Run with Claude API e2e tests
ANTHROPIC_API_KEY=sk-ant-... python -m pytest tests/test_all.py -v
```

Tests cover:
- Zone data consistency across all maps
- All 12 tool functions (unit tests with mock data)
- Tool routing and schema validation
- Cache configuration
- Database schema and no-pool fallback
- Digest generation
- FastAPI endpoints
- Bot structure
- Integration pipelines (multi-tool sequences)
- Claude API e2e (skipped without API key)

## Observability

### Metrics

`observability.py` exports Prometheus counters and histograms. Scraped at `GET /metrics`.

### Monitoring Stack

```bash
cd observability
docker-compose up -d
```

- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

### Adding Custom Metrics

```python
from observability import record_query_metric, record_tool_metric

record_query_metric(status="success", tier="pro")
record_tool_metric(tool_name="my_tool", status="success")
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude API key |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token |
| `BAYUT_API_KEY` | No | RapidAPI key for Bayut (mock fallback) |
| `BRAVE_API_KEY` | No | Brave Search API key |
| `DATABASE_URL` | No | PostgreSQL connection string |
| `REDIS_URL` | No | Redis connection string |
| `STRIPE_SECRET_KEY` | No | Stripe for payments |
| `OPENAI_API_KEY` | No | OpenAI Whisper for voice |
| `BOT_MODE` | No | `polling` (default) or `webhook` |
| `PORT` | No | FastAPI port (default 8000) |
| `ENVIRONMENT` | No | `test` to skip DB in tests |

## Common Tasks

### Run a test query via API
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze a studio in Dubai Marina for 650K AED"}'
```

### Run a test query via CLI
```bash
python test_query.py "Analyze a 1BR in Arjan for investment"
```

### Simulate cost for conversations
```bash
python test_cost_sim.py
```

### Set Telegram bot command menu
```bash
python set_bot_commands.py
```
