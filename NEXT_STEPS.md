# TrueValue AI - Roadmap & Next Steps

**Last Updated**: February 15, 2026
**Current Status**: Local Development (MVP Complete)

## Recent Achievements (Feb 15, 2026)

✅ **Live Web Search Integration**: Brave Search API for real-time market validation
✅ **Dual-Format Analysis**: Concise (30-60s) + Full Report (1-2min) on demand
✅ **Interactive UX**: Progress indicators + action buttons (Full Report, Compare, Mortgage, Web Search)
✅ **Performance Optimization**: Reduced response time from 5 min → 60 sec via strategic tool selection
✅ **Observability Stack**: Prometheus, Grafana, Loki dashboards operational
✅ **Comprehensive Testing**: Web search test suite with 12 unit/integration tests

---

## Immediate Next Features (Week 1-2)

### 1. Production Deployment 🚀
**Priority**: CRITICAL
**Estimated Effort**: 2-3 days

**Tasks**:
- [ ] Choose cloud platform (Railway recommended - zero-config PostgreSQL)
- [ ] Containerize application (Dockerfile for main.py + bot.py)
- [ ] Configure environment variables in cloud platform
- [ ] Switch Telegram bot from polling → webhook mode
- [ ] Set up health checks and auto-restart
- [ ] Configure domain + SSL (truevalue.ae)
- [ ] Test production deployment end-to-end

**Why Now**: Currently only accessible locally - can't onboard real users

**Files to Create**:
- `Dockerfile` - Container image for services
- `railway.json` or `heroku.yml` - Platform config
- `requirements.txt` - Already exists, verify completeness
- `.dockerignore` - Exclude unnecessary files

**Deployment Architecture**:
```
Railway/Heroku Platform
├─ Web Service (FastAPI on port 8000)
├─ Worker Service (Telegram Bot)
├─ PostgreSQL Database (managed)
└─ Prometheus/Grafana Cloud (observability)
```

### 2. Database Migration (JSON → PostgreSQL) 💾
**Priority**: HIGH
**Estimated Effort**: 2-3 days

**Current Problem**:
- User data stored in `users_db.json` (lost on restart)
- Conversation history in `conversations_db.json` (no concurrent access)
- No analytics, no query history

**Migration Plan**:
```sql
-- Users table
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    tier VARCHAR(20) NOT NULL DEFAULT 'free',
    joined_at TIMESTAMP NOT NULL,
    queries_today INT DEFAULT 0,
    last_reset DATE NOT NULL,
    telegram_username VARCHAR(255),
    total_queries INT DEFAULT 0
);

-- Conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    query TEXT NOT NULL,
    response TEXT,
    created_at TIMESTAMP NOT NULL,
    response_time_ms INT,
    format VARCHAR(20), -- 'concise' or 'full'
    tools_used JSONB,
    success BOOLEAN DEFAULT TRUE
);

-- Query analytics
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    query_text TEXT,
    property_zone VARCHAR(100),
    property_type VARCHAR(50),
    price_range VARCHAR(50),
    created_at TIMESTAMP NOT NULL
);
```

**Implementation**:
- [ ] Install `asyncpg` or `sqlalchemy` with async support
- [ ] Create `database.py` with connection pool and models
- [ ] Migrate `telegram-bot/bot.py` to use PostgreSQL instead of JSON
- [ ] Write migration script to import existing users_db.json
- [ ] Add indexes for common queries (user_id, created_at)
- [ ] Update observability to track DB performance

**Benefits**:
- Persistent user data across restarts
- Query history and analytics
- Concurrent access (multiple bot instances)
- Scalable to 100K+ users

### 3. Payment Integration (Stripe) 💳
**Priority**: MEDIUM
**Estimated Effort**: 3-4 days

**Current Limitation**: All users are "free" tier - no revenue

**Subscription Tiers**:
- **Free**: 5 queries/day (current)
- **Pro**: AED 99/month, 10 queries/day, PDF reports
- **Enterprise**: AED 499/month, unlimited, API access, white-label

**Implementation**:
- [ ] Integrate Stripe SDK (`stripe` Python package)
- [ ] Create subscription products in Stripe Dashboard
- [ ] Add `/subscribe` command to Telegram bot
- [ ] Implement payment link generation
- [ ] Add Stripe webhook handler for payment confirmation
- [ ] Update user tier in DB after successful payment
- [ ] Add `/manage_subscription` command (cancel, upgrade)

**User Flow**:
```
User: /subscribe pro
Bot: "Pro Plan: AED 99/month\n✅ 10 queries/day\n✅ PDF reports\n[Pay Now Button]"
User: Clicks button → Stripe checkout page
User: Completes payment
Stripe: Webhook → Update user tier to 'pro'
Bot: "✅ Welcome to Pro! You now have 10 queries/day."
```

**Files to Modify**:
- `telegram-bot/bot.py` - Add subscription commands
- `main.py` - Add Stripe webhook endpoint (`POST /webhook/stripe`)
- `database.py` - Add subscription_id, plan_id fields to users table

---

## Medium-Term Improvements (Month 1-2)

### 4. PDF Report Generation 📄
**Priority**: HIGH (Pro tier feature)
**Estimated Effort**: 2-3 days

**Why**: Premium users expect downloadable reports for sharing with investors/partners

**Implementation**:
- [ ] Install `reportlab` or `weasyprint` for PDF generation
- [ ] Create professional PDF template (branded, multi-page)
- [ ] Add property images from web search results
- [ ] Include charts (ROI comparison, price trends)
- [ ] Store PDFs in cloud storage (AWS S3 or Cloudflare R2)
- [ ] Send PDF as Telegram document reply

**PDF Sections**:
1. Cover page with property image + key metrics
2. Executive summary (verdict + score)
3. 4-pillar analysis (full detail)
4. Market comparison table
5. Financial projections (5-year forecast)
6. Appendix (web sources, disclaimers)

**File Structure**:
```
pdf_generator/
├─ __init__.py
├─ templates/
│  ├─ cover.html
│  ├─ analysis.html
│  └─ styles.css
├─ generator.py (main logic)
└─ charts.py (matplotlib for visualizations)
```

### 5. Enhanced Bayut Integration 🏠
**Priority**: MEDIUM
**Estimated Effort**: 2 days

**Current State**: Using mock data fallback (Bayut API returns 404)

**Tasks**:
- [ ] Investigate Bayut API 404 issue (verify endpoint, API key)
- [ ] Test with different RapidAPI subscription tier if needed
- [ ] Implement proper pagination (fetch more than 20 listings)
- [ ] Add property image URLs to results
- [ ] Cache Bayut results (1-hour TTL in Redis)
- [ ] Fallback to web scraping if API permanently unavailable

**Alternative APIs** (if Bayut continues failing):
- Property Finder API
- Dubizzle API
- Zameen.com API
- Custom web scraper (last resort)

### 6. WhatsApp Business Integration 💬
**Priority**: MEDIUM
**Estimated Effort**: 3 days

**Why**: Broader reach in UAE market (WhatsApp > Telegram locally)

**Implementation**:
- [ ] Set up WhatsApp Business API account
- [ ] Install `whatsapp-python` or use Twilio WhatsApp API
- [ ] Create `whatsapp-bot/` directory mirroring `telegram-bot/`
- [ ] Reuse `main.py` query handler (shared logic)
- [ ] Implement WhatsApp-specific features:
  - Voice message transcription → query
  - Location sharing → zone detection
  - Contact card sharing for referrals

**Unified Bot Architecture**:
```python
# shared/bot_core.py
class BotCore:
    async def handle_query(self, query, user_id, platform):
        # Shared logic for Telegram + WhatsApp
        ...

# telegram-bot/bot.py
from shared.bot_core import BotCore
class TelegramBot(BotCore):
    ...

# whatsapp-bot/bot.py
from shared.bot_core import BotCore
class WhatsAppBot(BotCore):
    ...
```

### 7. Comparative Analysis Enhancement 📊
**Priority**: MEDIUM
**Estimated Effort**: 2 days

**Current Tool**: `compare_properties()` does basic side-by-side

**Enhancements**:
- [ ] Add visual comparison table (formatted text or image)
- [ ] Include price per sqft delta
- [ ] Show chiller cost difference
- [ ] Highlight best value with 🏆 emoji
- [ ] Add recommendation: "Option A wins on yield, Option B wins on location"
- [ ] Support 2-4 properties (currently only 2)

**Example Output**:
```
┌─────────────────┬──────────────┬──────────────┬──────────────┐
│                 │ Marina Gate  │ JBR Beach    │ JLT Lake View│
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Price           │ 650K         │ 780K         │ 590K 🏆      │
│ Price/sqft      │ 1,444        │ 1,560        │ 1,311 🏆     │
│ Gross Yield     │ 6.1%         │ 5.8%         │ 6.5% 🏆      │
│ Chiller/year    │ 3,272        │ 4,500        │ 0 (DEWA) 🏆  │
│ Net Yield       │ 5.1%         │ 4.6%         │ 5.8% 🏆      │
│ Oversupply Risk │ HIGH ⚠️      │ MEDIUM       │ LOW 🏆       │
│ Score           │ 62/100       │ 58/100       │ 74/100 🏆    │
└─────────────────┴──────────────┴──────────────┴──────────────┘

🏆 WINNER: JLT Lake View
   Best value, DEWA chiller (no cooling costs), lower oversupply risk
```

### 8. Voice Message Support 🎙️
**Priority**: LOW
**Estimated Effort**: 1 day

**Why**: Convenience for users on-the-go

**Implementation**:
- [ ] Install `speech_recognition` or use OpenAI Whisper API
- [ ] Add voice message handler in `telegram-bot/bot.py`
- [ ] Transcribe audio → text query
- [ ] Send back: "I heard: [transcription]. Analyzing..."
- [ ] Process as normal text query

---

## Long-Term Vision (Quarter 1-2)

### 9. Mobile App (React Native) 📱
**Priority**: MEDIUM (after payment integration proves revenue)
**Estimated Effort**: 4-6 weeks

**Why**: Better UX than Telegram, push notifications, offline mode

**Tech Stack**:
- React Native (iOS + Android from one codebase)
- Expo for rapid development
- Shared backend (FastAPI already API-ready)
- Push notifications via Firebase

**Key Features**:
- Property search with filters (zone, price, type)
- Saved searches and alerts
- Query history with re-run capability
- Offline mode (cache last 10 queries)
- Share reports via WhatsApp/email
- Dark mode

### 10. White-Label Agency Solution 🏢
**Priority**: LOW (B2B pivot)
**Estimated Effort**: 6-8 weeks

**Concept**: Sell TrueValue AI to real estate agencies as their branded AI assistant

**Features**:
- Custom branding (logo, colors, domain)
- Agency admin dashboard (usage analytics, user management)
- Lead capture integration (CRM webhooks)
- Custom pricing tiers per agency
- API access for embedding in agency websites

**Pricing**:
- AED 2,000/month per agency (unlimited agents)
- AED 5,000 setup fee
- Revenue share: 20% of any pro subscriptions sold

### 11. Multi-City Expansion 🌍
**Priority**: LOW
**Estimated Effort**: 4 weeks per city

**Target Cities**:
1. **Abu Dhabi** (UAE) - Similar market dynamics
2. **Sharjah** (UAE) - More affordable market
3. **Riyadh** (Saudi Arabia) - Huge market, similar culture
4. **Doha** (Qatar) - Small but high-value market

**Per-City Requirements**:
- New data sources (local property APIs)
- Market-specific tools (e.g., RERA → Abu Dhabi Municipality)
- Localized chiller cost logic
- Zone/district mapping
- Currency handling (AED vs SAR vs QAR)
- Legal/regulatory knowledge base

**Implementation**:
```python
# main.py system prompt becomes:
SYSTEM_PROMPT_TEMPLATE = """
You are a {city} real estate investment analyst...
[Dynamic injection of city-specific knowledge]
"""

# Tools become city-aware:
async def search_properties(location, city="dubai"):
    if city == "dubai":
        return await search_bayut(location)
    elif city == "abu_dhabi":
        return await search_propertyfinder(location)
    elif city == "riyadh":
        return await search_aqar(location)
```

### 12. API Marketplace for Developers 🔌
**Priority**: LOW (after significant user base)
**Estimated Effort**: 3-4 weeks

**Concept**: Monetize analysis engine via public API

**Pricing**:
- Free tier: 100 requests/month
- Starter: $49/month - 1,000 requests
- Pro: $199/month - 10,000 requests
- Enterprise: Custom pricing

**API Endpoints**:
```
POST /api/v1/analyze
POST /api/v1/compare
POST /api/v1/search
GET  /api/v1/market-trends/{zone}
```

**Developer Portal**:
- API key management
- Usage analytics dashboard
- Interactive API docs (Swagger)
- Rate limit monitoring
- Webhook configuration

---

## Technical Debt & Infrastructure

### Testing & Quality
**Estimated Effort**: Ongoing

**Priorities**:
- [ ] Expand test coverage (currently only `test_web_search.py`)
- [ ] Add tests for all 11 tools
- [ ] Integration tests for Telegram bot handlers
- [ ] End-to-end test suite (user query → response)
- [ ] Load testing (100 concurrent users)
- [ ] CI/CD pipeline (GitHub Actions)
  - Run tests on every commit
  - Auto-deploy to staging on merge to `main`
  - Manual approval for production deploy

### Security Hardening
**Estimated Effort**: 1 week

**Tasks**:
- [ ] Implement rate limiting per IP (not just user_id)
- [ ] Add CAPTCHA for suspicious activity
- [ ] Sanitize all user inputs (prevent injection attacks)
- [ ] Rotate API keys regularly
- [ ] Add API key encryption in database
- [ ] Implement audit logging (who accessed what, when)
- [ ] Security audit by third party
- [ ] Penetration testing

### Performance Optimization
**Estimated Effort**: 2 weeks

**Opportunities**:
- [ ] **Parallel Tool Execution**: Execute independent tools concurrently
  ```python
  # Before: Serial execution (slow)
  result1 = await search_bayut(location)
  result2 = await calculate_chiller(location)

  # After: Parallel execution (2x faster)
  results = await asyncio.gather(
      search_bayut(location),
      calculate_chiller(location)
  )
  ```

- [ ] **Redis Caching**: Cache tool results (24-hour TTL)
  - Market trends by zone
  - Property search results
  - Web search results
  - Supply pipeline data

- [ ] **Claude API Optimization**:
  - Use prompt caching (Anthropic feature) for system prompt
  - Reduce token usage via better prompt engineering
  - Consider Claude Haiku for simple queries (10x cheaper)

- [ ] **Database Indexing**:
  - Index on `(user_id, created_at)` for conversation history
  - Index on `property_zone` for analytics queries

### Documentation
**Estimated Effort**: 3 days

**To Create**:
- [ ] **API Documentation** (OpenAPI/Swagger) - Auto-generated from FastAPI
- [ ] **User Guide** (for Telegram bot) - Commands, features, tips
- [ ] **Developer Guide** - How to contribute, code structure
- [ ] **Deployment Guide** - Step-by-step for Railway/Heroku
- [ ] **Tool Documentation** - What each tool does, when to use

---

## Success Metrics (3-Month Goals)

### User Growth
- **100 active users** (daily active)
- **5 paid subscribers** (Pro tier)
- **500 total queries** processed

### Performance
- **95% query success rate**
- **<60 seconds** average response time (concise)
- **<3% error rate**

### Revenue
- **AED 500/month** from Pro subscriptions
- **Target**: Break-even on API costs by Month 2

### Engagement
- **3 queries per user per week** (average)
- **40% return rate** (users who query >1 time)
- **4.5/5 average rating** (user feedback)

---

## Resource Requirements

### Infrastructure Costs (Monthly)
- **Railway/Heroku**: ~$25/month (Hobby tier)
- **PostgreSQL**: Included in platform tier
- **Grafana Cloud**: Free tier (10K series)
- **Cloudflare R2** (PDF storage): ~$5/month
- **Claude API**: ~$100/month (at 500 queries)
- **Brave Search API**: ~$10/month
- **Total**: ~$140/month

### Development Time (Solo Developer)
- **Week 1-2**: Deployment + Database migration
- **Week 3-4**: Payment integration + PDF reports
- **Month 2**: WhatsApp integration + Enhanced comparisons
- **Month 3**: Mobile app planning + White-label POC

### Team Expansion (When to Hire)
- **1st hire** (at 50 paid users): Full-stack developer
- **2nd hire** (at 200 paid users): DevOps engineer
- **3rd hire** (at 500 paid users): Product manager

---

## Risk Mitigation

### Key Risks
1. **Claude API Cost Explosion**: If queries 10x, costs 10x
   - **Mitigation**: Implement strict rate limits, cache aggressively, consider Haiku for simple queries

2. **Bayut API Remains Broken**: Mock data not sustainable
   - **Mitigation**: Integrate 2-3 alternative APIs (Property Finder, Dubizzle)

3. **User Churn**: Free users don't convert to paid
   - **Mitigation**: Add more free tier value (limited PDF reports, query rollover)

4. **Competition**: Established players add AI features
   - **Mitigation**: Focus on speed + accuracy moat, build brand trust

5. **Regulatory Changes**: DLD restricts data usage
   - **Mitigation**: Consult legal early, stay within public data bounds

---

## Priority Matrix

| Feature | Impact | Effort | Priority | Timeline |
|---------|--------|--------|----------|----------|
| Production Deployment | 🔥 Critical | Medium | **P0** | Week 1 |
| Database Migration | High | Medium | **P0** | Week 2 |
| Payment Integration | High | High | **P1** | Week 3-4 |
| PDF Reports | Medium | Medium | **P1** | Month 2 |
| Bayut Fix | Medium | Low | **P1** | Month 2 |
| WhatsApp Integration | Medium | High | **P2** | Month 2 |
| Comparative Enhancement | Low | Low | **P2** | Month 2 |
| Mobile App | High | Very High | **P3** | Quarter 2 |
| White-Label | Medium | Very High | **P3** | Quarter 2 |
| Multi-City | Low | Very High | **P4** | Quarter 3+ |

**Legend**:
- **P0**: Must have for launch
- **P1**: Should have for MVP
- **P2**: Nice to have for v1.0
- **P3**: Future roadmap
- **P4**: Long-term vision

---

## Decision Log

### Key Decisions Made
1. **Feb 15, 2026**: Chose Brave Search over Google Custom Search (better freshness, simpler API)
2. **Feb 15, 2026**: Implemented dual-format system instead of always-full reports (performance)
3. **Feb 15, 2026**: Chose interactive buttons over inline commands (better UX)

### Decisions Pending
1. **Cloud Platform**: Railway vs Heroku vs Fly.io (need cost comparison)
2. **Database**: PostgreSQL vs MongoDB (leaning PostgreSQL for relational data)
3. **Mobile**: React Native vs Flutter (leaning React Native for code reuse)
4. **Payment**: Stripe vs local UAE payment gateway (Telr, PayTabs)

---

**Document Version**: 1.0
**Last Updated**: February 15, 2026
**Next Review**: March 1, 2026
**Owner**: Development Team

For questions or suggestions, see CONTRIBUTING.md (to be created).
