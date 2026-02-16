# TrueValue AI — Docker, Deployment & Auth/Subscription Plan

## Context

All 7 features are implemented, 118 tests pass, docs are updated. The app runs locally but has no production deployment, no API authentication, and the subscription flow needs hardening. This plan covers three areas the user requested:

1. **Dockerize** — Already mostly done (Dockerfile, docker-compose.yml exist). Needs a lightweight production compose and .env.example update.
2. **Production deployment** — Recommend Railway.app. Dockerfile + railway.json already exist.
3. **User management / auth / subscriptions** — The big gap. FastAPI endpoints are completely unprotected.

## What Already Exists

| Component | Status | File |
|-----------|--------|------|
| Dockerfile | Done | `Dockerfile` (Python 3.11-slim, healthcheck) |
| docker-compose.yml | Done (9 services, dev/observability) | `docker-compose.yml` |
| .dockerignore | Done | `.dockerignore` |
| railway.json | Done | `railway.json` (Dockerfile builder, /health check) |
| Procfile | Done | `Procfile` |
| CI/CD | Done | `.github/workflows/ci.yml` (lint, test, docker build) |
| Stripe integration | Done | `payments.py` (checkout, webhooks, portal, cancel) |
| User DB schema | Done | `database.py` (users table with tier, stripe IDs, bonus_queries) |
| Bot rate limiting | Done | `bot.py` (per-tier daily limits, auto-reset, bonus queries) |

## What's Missing

| Gap | Severity | Fix |
|-----|----------|-----|
| No API auth on /api/query, /api/tools, /api/metrics | Critical | Bearer token middleware |
| No Telegram webhook validation | Critical | X-Telegram-Bot-Api-Secret-Token check |
| CORS allow_origins=["*"] | Medium | Env-configurable origins |
| No rate limiting on FastAPI endpoints | Medium | slowapi on /api/query |
| No post-payment notification to user | Low | Telegram message after webhook |
| .env.example missing newer vars | Low | Update file |
| No lightweight production compose | Low | New docker-compose.prod.yml |
| Free tier has 50 queries/day, Basic has 20 | Bug | Fix to free=5 |

---

## Part 1: Docker Cleanup

### 1A. Create `docker-compose.prod.yml` (new file)

Lightweight 3-service production compose (vs the 9-service dev stack):
- `app` — builds from Dockerfile, port 8000, BOT_MODE=webhook
- `postgres` — postgres:16-alpine, no exposed port, healthcheck
- `redis` — redis:7-alpine, no exposed port, healthcheck

Keep existing `docker-compose.yml` as the full dev/observability stack.

### 1B. Update `.env.example`

Add all current env vars with placeholder values. Currently missing:
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_BASIC/PRO/ENTERPRISE`
- `OPENAI_API_KEY`
- `TELEGRAM_ADMIN_IDS`
- `BOT_MODE`, `WEBHOOK_URL`
- New auth vars: `API_SECRET_KEY`, `TELEGRAM_WEBHOOK_SECRET`, `CORS_ALLOWED_ORIGINS`

---

## Part 2: API Authentication & Security

### 2A. Bearer Token Auth on Protected Endpoints

**File: `main.py` (~line 27 imports, ~line 71 after CORS)**

Add `FastAPI.Depends` with `HTTPBearer` security scheme:
- If `API_SECRET_KEY` env var is set → require `Authorization: Bearer <key>` on protected endpoints
- If not set → auth disabled (dev mode, backward compatible)

Protected endpoints (add `Depends(verify_api_key)`):
- `POST /api/query` (line 2872)
- `GET /api/tools` (line 2915)
- `GET /api/metrics` (line 2926)
- `GET /api/metrics/user/{user_id}` (line 2936)

Public endpoints (no auth):
- `GET /` , `GET /health`, `GET /metrics` (Prometheus)
- `POST /webhook/stripe` (has Stripe signature validation)
- `POST /webhook/telegram` (gets its own validation below)
- `POST /webhook/whatsapp`

### 2B. Telegram Webhook Validation

**File: `main.py` (line 2978, `/webhook/telegram` endpoint)**

Check `X-Telegram-Bot-Api-Secret-Token` header against `TELEGRAM_WEBHOOK_SECRET` env var. When setting the webhook via Telegram API, pass `secret_token` parameter.

### 2C. CORS Tightening

**File: `main.py` (lines 64-70)**

Read `CORS_ALLOWED_ORIGINS` from env var (comma-separated). Default to `["*"]` when not set (dev mode).

### 2D. Rate Limiting on /api/query

**File: `main.py`, `requirements.txt`**

Add `slowapi` dependency. Apply `@limiter.limit("10/minute")` to `POST /api/query`. Uses client IP as key. Bot calls `handle_query()` directly (bypasses HTTP), so bot users are unaffected.

### 2E. Fix Free Tier Query Limit

**File: `telegram-bot/bot.py` (line 77)**

Change free tier from `queries_per_day: 50` to `queries_per_day: 5`. Currently free users get MORE queries than Basic subscribers (50 vs 20), which is a bug.

---

## Part 3: Subscription Flow Hardening

### 3A. Post-Payment Telegram Notification

**File: `payments.py`**

After `_handle_checkout_completed()` updates the DB (line 173), send a Telegram message to the user confirming their upgrade. Similarly in `_handle_subscription_deleted()` (line 228), notify the user of cancellation. Uses direct Telegram Bot API HTTP call (same pattern as digest.py).

### 3B. Per-User API Keys (Optional Enhancement)

**File: `database.py`, `telegram-bot/bot.py`**

- Add `api_key TEXT UNIQUE` column to users table via SCHEMA_MIGRATIONS
- Add `generate_api_key(user_id)` and `get_user_by_api_key(api_key)` functions
- Add `/apikey` bot command — generates/shows API key (Pro/Enterprise only)
- Update auth middleware to also check per-user keys from DB

This is a nice-to-have. The global `API_SECRET_KEY` is sufficient for initial deployment. Can be added later.

---

## Part 4: Railway Deployment

### Why Railway

- Native Docker deployment (Dockerfile already exists, railway.json already configured)
- Built-in PostgreSQL + Redis add-ons (one click, auto-injects DATABASE_URL/REDIS_URL)
- $5/month hobby plan, scales to pay-per-use
- GitHub auto-deploy support
- Built-in health checks (already configured in railway.json → /health)
- Simple CLI: `railway up`

### Deployment Steps

1. `railway login` + `railway init`
2. Add PostgreSQL and Redis add-ons
3. Set all env vars (ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, STRIPE keys, BOT_MODE=webhook, TELEGRAM_WEBHOOK_SECRET, API_SECRET_KEY)
4. `railway up` (or connect GitHub for auto-deploy)
5. Set Telegram webhook: `curl "https://api.telegram.org/bot${TOKEN}/setWebhook?url=${APP_URL}/webhook/telegram&secret_token=${SECRET}"`
6. Set Stripe webhook in Stripe Dashboard → `${APP_URL}/webhook/stripe`
7. Verify: `curl ${APP_URL}/health`

---

## Files to Modify

| File | Changes |
|------|---------|
| `main.py` | Auth middleware (~30 lines), CORS from env (~5 lines), webhook validation (~8 lines), rate limiting (~15 lines) |
| `payments.py` | Post-payment Telegram notifications (~30 lines in 2 handlers) |
| `telegram-bot/bot.py` | Fix free tier limit (1 line), add /apikey command (~35 lines, optional) |
| `database.py` | Add api_key migration + 2 functions (~25 lines, optional) |
| `requirements.txt` | Add `slowapi==0.1.9` (1 line) |
| `.env.example` | Full rewrite with all vars (~35 lines) |
| `docker-compose.prod.yml` | New file (~45 lines) |
| `DEPLOYMENT_GUIDE.md` | Add Railway section (~40 lines) |

## Implementation Order

1. `.env.example` update
2. `docker-compose.prod.yml` (new file)
3. CORS tightening (`main.py`)
4. Telegram webhook validation (`main.py`)
5. Bearer token auth middleware (`main.py`)
6. Rate limiting with slowapi (`main.py` + `requirements.txt`)
7. Fix free tier query limit (`bot.py`)
8. Post-payment notifications (`payments.py`)
9. Per-user API keys (`database.py` + `bot.py`) — optional
10. Update DEPLOYMENT_GUIDE.md with Railway steps
11. Deploy to Railway

## Verification

1. **Auth**: `curl -X POST localhost:8000/api/query -d '{"query":"test"}' -H 'Content-Type: application/json'` → 401. Add `-H 'Authorization: Bearer <key>'` → 200.
2. **Rate limit**: Fire 11 rapid requests to /api/query → 11th gets 429.
3. **Webhook validation**: POST to /webhook/telegram without secret header → 403.
4. **CORS**: Browser request from unlisted origin → blocked.
5. **Free tier fix**: Free user sees "5 queries remaining" not "50".
6. **Payment notification**: Trigger test Stripe webhook → user receives Telegram message.
7. **Docker prod**: `docker-compose -f docker-compose.prod.yml up` → app + postgres + redis start, /health returns 200.
8. **Full test suite**: `python -m pytest tests/test_all.py -v` → 118 tests pass.
