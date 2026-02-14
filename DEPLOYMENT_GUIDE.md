# 🚀 Deployment & Scaling Guide

## Complete Production Deployment Strategy

---

## 📋 Pre-Deployment Checklist

### Infrastructure Setup
- [ ] Domain name purchased (truevalue.ae)
- [ ] SSL certificate obtained
- [ ] Cloud provider account (AWS/DigitalOcean/Heroku)
- [ ] Database provisioned (PostgreSQL)
- [ ] Redis instance for caching
- [ ] CDN configured (Cloudflare)
- [ ] Email service (SendGrid/AWS SES)
- [ ] SMS service (Twilio)
- [ ] Monitoring tools (Datadog/New Relic)

### API Keys & Credentials
- [ ] All production API keys obtained
- [ ] Stripe account verified
- [ ] Telegram bot token (production)
- [ ] WhatsApp Business API approved
- [ ] Google Analytics/Mixpanel setup
- [ ] Sentry for error tracking

### Legal & Compliance
- [ ] Company registered in Dubai
- [ ] Terms of Service finalized
- [ ] Privacy Policy published
- [ ] Cookie consent implemented
- [ ] Data retention policy defined
- [ ] GDPR compliance verified

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        USERS                                 │
│  (Telegram, WhatsApp, Web, Mobile Apps)                     │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                   LOAD BALANCER (Nginx)                      │
│              SSL Termination, Rate Limiting                  │
└────────────┬────────────────────────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌───────────┐  ┌──────────────┐
│ Telegram  │  │   Web API    │
│   Bot     │  │  (FastAPI)   │
└─────┬─────┘  └──────┬───────┘
      │                │
      └────────┬───────┘
               ▼
     ┌──────────────────┐
     │ Claude + MCP     │
     │   Orchestrator   │
     └─────────┬────────┘
               │
     ┌─────────┴─────────┐
     │                   │
     ▼                   ▼
┌──────────┐      ┌──────────────┐
│   MCP    │      │  PostgreSQL  │
│ Servers  │      │   Database   │
│ (20+)    │      │              │
└────┬─────┘      └──────┬───────┘
     │                   │
     │    ┌──────────────┤
     │    │              │
     ▼    ▼              ▼
┌─────────────┐    ┌──────────┐
│   Redis     │    │   S3     │
│   Cache     │    │  Storage │
└─────────────┘    └──────────┘
```

---

## 🐳 Docker Deployment

### 1. Containerize All Services

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  # Main API
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db
      - redis
    restart: always

  # Telegram Bot
  telegram-bot:
    build: ./telegram-bot
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - db
      - api
    restart: always

  # MCP Server - Dubai REST
  mcp-dubai-rest:
    build: ./mcp-servers/dubai-rest
    environment:
      - DUBAI_REST_API_KEY=${DUBAI_REST_API_KEY}
    restart: always

  # MCP Server - Property Finder
  mcp-property-finder:
    build: ./mcp-servers/property-finder
    environment:
      - PROPERTY_FINDER_API_KEY=${PROPERTY_FINDER_API_KEY}
    restart: always

  # MCP Server - Bayut
  mcp-bayut:
    build: ./mcp-servers/bayut-listings
    environment:
      - BAYUT_API_KEY=${BAYUT_API_KEY}
    restart: always

  # MCP Server - Chiller Scraper
  mcp-chiller:
    build: ./mcp-servers/chiller-scraper
    restart: always

  # MCP Server - Social Intelligence
  mcp-social:
    build: ./mcp-servers/social-listener
    environment:
      - REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID}
      - REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET}
    restart: always

  # Database
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=dubai_estate
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    restart: always

  # Redis Cache
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: always

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: always

volumes:
  postgres_data:
  redis_data:
```

### 2. Build and Deploy

```bash
# Build all containers
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Scale API instances
docker-compose up -d --scale api=3
```

---

## ☁️ Cloud Deployment Options

### Option 1: AWS (Recommended for Scale)

**Services Used**:
- **ECS/Fargate**: Container orchestration
- **RDS PostgreSQL**: Managed database
- **ElastiCache Redis**: Managed cache
- **S3**: File storage (reports, images)
- **CloudFront**: CDN
- **Route 53**: DNS
- **ALB**: Load balancing
- **CloudWatch**: Monitoring

**Monthly Cost (Estimated)**:
- ECS Fargate: $150
- RDS (db.t3.medium): $100
- ElastiCache: $50
- S3 + CloudFront: $30
- **Total**: ~$330/month

**Deployment**:
```bash
# Install AWS CLI
pip install awscli

# Configure
aws configure

# Deploy with CDK/Terraform
cd infrastructure/aws
terraform init
terraform apply
```

### Option 2: DigitalOcean (Budget-Friendly)

**Services Used**:
- **Droplets**: VMs for services
- **Managed Database**: PostgreSQL
- **Spaces**: Object storage
- **App Platform**: Easy deployment

**Monthly Cost**:
- Droplet (4GB): $24
- Managed DB: $15
- Spaces: $5
- **Total**: ~$44/month

**Deployment**:
```bash
# Install doctl
brew install doctl # or download from DO

# Authenticate
doctl auth init

# Deploy
doctl apps create --spec app.yaml
```

### Option 3: Heroku (Quickest Start)

**Services Used**:
- **Dynos**: App containers
- **Heroku Postgres**: Database
- **Heroku Redis**: Cache

**Monthly Cost**:
- Standard dynos (2x): $50
- Postgres: $9
- Redis: $15
- **Total**: ~$74/month

**Deployment**:
```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create dubai-estate-api

# Deploy
git push heroku main

# Set env vars
heroku config:set ANTHROPIC_API_KEY=xxx
```

---

## 🌐 Website Deployment (Next.js)

### Tech Stack
- **Frontend**: Next.js 14 + TypeScript
- **Styling**: Tailwind CSS
- **Hosting**: Vercel (optimized for Next.js)
- **Forms**: React Hook Form
- **Payments**: Stripe Checkout
- **Analytics**: Google Analytics + Mixpanel

### Deployment to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd website
vercel --prod

# Set environment variables in Vercel dashboard
```

### Website Pages Required

1. **Homepage** (`/`)
   - Hero section
   - Features showcase
   - Pricing table
   - Testimonials
   - CTA buttons

2. **Pricing** (`/pricing`)
   - Detailed tier comparison
   - FAQ
   - Enterprise contact form

3. **How It Works** (`/how-it-works`)
   - Step-by-step guide
   - Video walkthrough
   - Screenshots

4. **Blog** (`/blog/*`)
   - SEO content
   - Dubai market insights
   - How-to guides

5. **Dashboard** (`/dashboard`)
   - User portal
   - Query history
   - Portfolio tracking
   - Settings

6. **API Docs** (`/docs`)
   - API reference
   - Code examples
   - Authentication guide

---

## 📱 Telegram Bot Deployment

### Hosting Options

**Option 1: Long-Running Server**
```bash
# On VPS or Docker container
cd telegram-bot
python3 bot.py

# Use systemd for persistence
sudo nano /etc/systemd/system/telegram-bot.service

# Service file:
[Unit]
Description=Dubai Estate Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/dubai-estate-agent/telegram-bot
ExecStart=/usr/bin/python3 /home/ubuntu/dubai-estate-agent/telegram-bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

**Option 2: Webhook Mode** (Recommended for production)
```python
# Instead of polling, use webhooks
application.run_webhook(
    listen="0.0.0.0",
    port=8443,
    url_path="telegram",
    webhook_url=f"https://api.dubaiestate.ai/telegram"
)
```

---

## 📊 Monitoring & Logging

### 1. Application Monitoring (Datadog)

```python
# Install
pip install ddtrace

# Run with tracing
ddtrace-run python bot.py

# Custom metrics
from datadog import statsd

statsd.increment('user.query')
statsd.histogram('query.response_time', elapsed_time)
```

### 2. Error Tracking (Sentry)

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0
)

# Errors automatically captured
```

### 3. Logging (ELK Stack or CloudWatch)

```python
import logging
import watchtower

# CloudWatch handler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler())

logger.info("User query processed", extra={
    "user_id": user_id,
    "query": query,
    "response_time": elapsed
})
```

---

## 🔐 Security Best Practices

### 1. Environment Variables
```bash
# Never commit secrets
# Use .env file locally
# Use cloud provider secrets manager in production

# AWS Secrets Manager
aws secretsmanager create-secret \
    --name dubai-estate/api-keys \
    --secret-string file://secrets.json
```

### 2. Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/search")
@limiter.limit("10/minute")
async def search(request: Request):
    # Your code
    pass
```

### 3. API Key Validation
```python
async def verify_api_key(api_key: str = Header(...)):
    if api_key not in valid_keys:
        raise HTTPException(401, "Invalid API key")
    return api_key
```

### 4. SQL Injection Prevention
```python
# Always use parameterized queries
cursor.execute(
    "SELECT * FROM users WHERE email = %s",
    (email,)  # Never use f-strings!
)
```

### 5. HTTPS Only
```nginx
# nginx.conf
server {
    listen 80;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ...
}
```

---

## 📈 Scaling Strategy

### Horizontal Scaling

**When to Scale**:
- CPU usage consistently > 70%
- Response time > 2 seconds
- Queue backlog growing
- User complaints about slowness

**How to Scale**:
```bash
# AWS ECS
aws ecs update-service \
    --cluster dubai-estate \
    --service api \
    --desired-count 5

# Docker Compose
docker-compose up -d --scale api=5

# Kubernetes
kubectl scale deployment api --replicas=5
```

### Vertical Scaling
```bash
# Upgrade instance size
# AWS: t3.medium → t3.large
# DigitalOcean: 2GB → 4GB droplet
```

### Database Scaling

**Read Replicas**:
```python
# Master for writes
DATABASES = {
    'default': {
        'ENGINE': 'postgresql',
        'HOST': 'master.db.amazonaws.com'
    },
    'replica': {
        'ENGINE': 'postgresql',
        'HOST': 'replica.db.amazonaws.com'
    }
}

# Route reads to replica
User.objects.using('replica').filter(...)
```

**Connection Pooling**:
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0
)
```

### Caching Strategy

**Redis Caching**:
```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379)

def get_property_data(property_id):
    # Check cache first
    cached = redis_client.get(f"property:{property_id}")
    if cached:
        return json.loads(cached)
    
    # Fetch from API
    data = fetch_from_api(property_id)
    
    # Cache for 1 hour
    redis_client.setex(
        f"property:{property_id}",
        3600,
        json.dumps(data)
    )
    return data
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

**.github/workflows/deploy.yml**:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: docker-compose build
      
      - name: Push to Docker Hub
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker-compose push
      
      - name: Deploy to AWS
        run: |
          aws ecs update-service --cluster dubai-estate --service api --force-new-deployment
```

---

## 📋 Launch Checklist

### Week Before Launch
- [ ] All services deployed to production
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Database backups automated
- [ ] Monitoring dashboards set up
- [ ] Error tracking configured
- [ ] Load testing completed
- [ ] Security audit passed

### Launch Day
- [ ] Final smoke tests
- [ ] Customer support ready
- [ ] Marketing materials ready
- [ ] Product Hunt post scheduled
- [ ] Social media posts queued
- [ ] Email list ready to send

### Week After Launch
- [ ] Monitor error rates
- [ ] Track conversion metrics
- [ ] Collect user feedback
- [ ] Fix critical bugs
- [ ] Optimize slow queries
- [ ] Scale if needed

---

## 🆘 Troubleshooting

### Common Issues

**High Memory Usage**:
```bash
# Check memory
docker stats

# Increase container memory
docker-compose up -d --scale api=2
```

**Slow Database Queries**:
```sql
-- Find slow queries
SELECT * FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Add indexes
CREATE INDEX idx_properties_location ON properties(location_id);
```

**API Rate Limits Hit**:
```python
# Implement exponential backoff
import backoff

@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=5
)
def call_api():
    return requests.get(url)
```

---

## 📞 Production Support

**On-Call Rotation**:
- Use PagerDuty or similar
- 24/7 coverage for critical issues
- Escalation policies

**Incident Response**:
1. Acknowledge alert
2. Assess severity
3. Fix or rollback
4. Post-mortem document
5. Prevent recurrence

---

**Ready to deploy? Start with Heroku for MVP, then migrate to AWS when you hit $10k MRR!** 🚀
