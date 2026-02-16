# TrueValue AI — Deployment Guide

## Architecture

TrueValue is a single Python application running three async services:

```
run.py
├── FastAPI (port 8000) — REST API + Prometheus metrics
├── Telegram Bot — polling or webhook mode
└── Digest Scheduler — hourly market digest cycle
```

External dependencies (all optional except Claude API):
- PostgreSQL — user data, watchlists, referrals, digests
- Redis — per-tool response caching
- Stripe — subscription payment processing

## Local Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Minimum .env:
# ANTHROPIC_API_KEY=sk-ant-...
# TELEGRAM_BOT_TOKEN=123456:ABC...

python run.py
```

## Docker Deployment

### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - BAYUT_API_KEY=${BAYUT_API_KEY}
      - BRAVE_API_KEY=${BRAVE_API_KEY}
      - DATABASE_URL=postgresql://truevalue:${DB_PASSWORD}@db:5432/truevalue
      - REDIS_URL=redis://redis:6379
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - BOT_MODE=${BOT_MODE:-polling}
    depends_on:
      - db
      - redis
    restart: always

  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=truevalue
      - POSTGRES_USER=truevalue
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    restart: always

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: always

volumes:
  postgres_data:
  redis_data:
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "run.py"]
```

### Build and Run

```bash
docker-compose build
docker-compose up -d
docker-compose logs -f app
```

## Cloud Deployment

### Heroku

```bash
# Procfile
web: python run.py

# Deploy
heroku create truevalue-ai
heroku addons:create heroku-postgresql:essential-0
heroku addons:create heroku-redis:mini
heroku config:set ANTHROPIC_API_KEY=sk-ant-...
heroku config:set TELEGRAM_BOT_TOKEN=123456:ABC...
heroku config:set BOT_MODE=webhook
git push heroku main
```

In webhook mode, set the Telegram webhook URL:
```bash
curl "https://api.telegram.org/bot${TOKEN}/setWebhook?url=https://your-app.herokuapp.com/webhook/telegram"
```

### Railway / Render

Both support Python apps out of the box:
1. Connect your Git repository
2. Set environment variables in the dashboard
3. Add PostgreSQL and Redis as services
4. Deploy

### AWS (ECS Fargate)

For production scale:

```
ALB (443) → ECS Service (app container)
                ├── RDS PostgreSQL
                ├── ElastiCache Redis
                └── CloudWatch (logs + metrics)
```

Estimated monthly cost:
- Fargate (1 vCPU, 2GB): ~$30
- RDS (db.t4g.micro): ~$15
- ElastiCache (cache.t4g.micro): ~$12
- Total: ~$57/month

## Webhook vs Polling Mode

| Mode | When to Use | Config |
|------|-------------|--------|
| Polling | Local development, testing | `BOT_MODE=polling` (default) |
| Webhook | Production, cloud deployment | `BOT_MODE=webhook` |

In webhook mode, only FastAPI runs. The Telegram bot receives updates via `POST /webhook/telegram`. Set the webhook URL with the Telegram Bot API.

## Database Setup

Tables are created automatically on first startup. No manual migration needed.

For a fresh PostgreSQL instance:
```bash
createdb truevalue
export DATABASE_URL=postgresql://user:pass@localhost:5432/truevalue
python run.py  # Tables created automatically
```

## Environment Variables

### Required
| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Claude API key |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from @BotFather |

### Recommended for Production
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `BOT_MODE` | `webhook` for production |
| `STRIPE_SECRET_KEY` | Stripe payment processing |

### Optional
| Variable | Description |
|----------|-------------|
| `BAYUT_API_KEY` | RapidAPI key for live Bayut data |
| `BRAVE_API_KEY` | Brave Search API for web search |
| `OPENAI_API_KEY` | OpenAI Whisper for voice messages |
| `PORT` | FastAPI port (default: 8000) |

## Monitoring

### Built-in Metrics

Prometheus metrics are exposed at `GET /metrics`. Key metrics:
- `dubai_estate_queries_total` — query count by status/tier
- `dubai_estate_tool_calls_total` — tool usage by name/status
- `dubai_estate_query_duration_seconds` — response time histogram

### Observability Stack (Optional)

```bash
cd observability
docker-compose up -d
```

Provides Grafana dashboards at http://localhost:3000 with:
- Query volume and success rates
- Tool usage distribution
- Response time percentiles
- Cost tracking

See [GRAFANA_OBSERVABILITY_GUIDE.md](GRAFANA_OBSERVABILITY_GUIDE.md) for details.

## Health Check

```bash
curl http://localhost:8000/health
# Returns: {"status": "healthy", "version": "..."}
```

## Security Checklist

- [ ] API keys stored in environment variables (never in code)
- [ ] `.env` file is gitignored
- [ ] PostgreSQL uses strong password
- [ ] Redis is not exposed to public internet
- [ ] HTTPS enabled (via reverse proxy or cloud provider)
- [ ] Telegram webhook uses HTTPS URL
- [ ] Rate limiting enabled per user tier

## Backup

### Database
```bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### Restore
```bash
psql $DATABASE_URL < backup_20260215.sql
```
