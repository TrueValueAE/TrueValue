# TrueValue AI - System Architecture

**Last Updated**: February 15, 2026

## Overview

TrueValue AI is a dual-interface real estate analysis platform combining a FastAPI-based web API with a Telegram bot frontend. The system provides AI-powered Dubai property analysis with live web search validation, comprehensive investment calculations, and dual-format output (concise/full).

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interfaces                          │
├──────────────────────────┬──────────────────────────────────────┤
│   Telegram Bot           │   HTTP API (FastAPI)                 │
│   - /start               │   - /query (POST)                    │
│   - /analyze             │   - /metrics (GET)                   │
│   - /search              │   - /health (GET)                    │
│   - Interactive Buttons  │                                      │
└──────────────┬───────────┴───────────────┬──────────────────────┘
               │                           │
               └───────────┬───────────────┘
                           │
                    ┌──────▼──────┐
                    │   main.py   │
                    │  (Orchestrator)
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │  Claude   │   │ External  │   │Observability│
    │   API     │   │   APIs    │   │   Stack   │
    │ (Sonnet)  │   │           │   │           │
    └───────────┘   └─────┬─────┘   └─────┬─────┘
                          │               │
                    ┌─────┴─────┐   ┌─────┴─────┐
                    │ Brave     │   │Prometheus │
                    │ Search    │   │ Grafana   │
                    │ RapidAPI  │   │ Loki      │
                    │ (Bayut)   │   │ Tempo     │
                    └───────────┘   └───────────┘
```

## Component Breakdown

### 1. User Interface Layer

#### Telegram Bot (`telegram-bot/bot.py`)
- **Technology**: python-telegram-bot (async)
- **Key Features**:
  - User registration and tier management (free/pro/enterprise)
  - Query rate limiting (5/10/unlimited per day)
  - Progress indicators ("🔍 Analyzing... ⏱️ 30-60s")
  - Interactive buttons (Full Report, Compare, Mortgage, Web Search)
  - Conversation context tracking
  - Message splitting for long responses (4096 char limit)

- **Commands**:
  - `/start` - User registration
  - `/analyze <query>` - Concise property analysis
  - `/search <location>` - Property search
  - `/compare <properties>` - Side-by-side comparison
  - `/help` - Usage guide

- **Data Storage**:
  - In-memory JSON (users_db.json, conversations_db.json)
  - Persists to disk on updates

#### HTTP API (`main.py`)
- **Technology**: FastAPI with uvicorn
- **Endpoints**:
  - `POST /query` - Main analysis endpoint
  - `GET /health` - Health check
  - `GET /metrics` - Prometheus metrics
  - `POST /feedback` - User feedback collection

### 2. Orchestration Layer (`main.py`)

#### Query Handler (`handle_query`)
- Receives query + user context
- Validates input and checks user tier
- Constructs system prompt with:
  - Domain expertise (Dubai real estate)
  - Tool definitions (11 tools)
  - Format detection (concise vs full)
  - Quality standards and constraints
- Manages Claude API conversation loop
- Records metrics at each step

#### Tool Execution Engine (`_execute_tool`)
- Routes tool calls to appropriate functions
- Handles errors gracefully with fallbacks
- Records execution metrics
- Returns structured JSON responses

### 3. Intelligence Layer

#### Claude API Integration
- **Model**: claude-sonnet-4.5-20250929
- **Pattern**: Iterative tool use with max 15 iterations
- **Temperature**: 0.2 (deterministic, factual)
- **Max Tokens**: 6000 (concise) / 16000 (full)
- **System Prompt**: ~4KB prompt defining expert behavior

**Tool Calling Flow**:
```
1. User query → Claude API
2. Claude responds with tool_use blocks
3. Execute tools → return results
4. Send results back to Claude
5. Claude analyzes → requests more tools OR returns final response
6. Repeat until Claude returns text response (no more tools)
```

#### Available Tools (11 total)

**Market Data Tools**:
1. `search_bayut_properties` - Property listings (RapidAPI + mock fallback)
2. `get_market_trends` - Price trends, ROI, occupancy
3. `get_supply_pipeline` - Upcoming developments by zone
4. `web_search_dubai` - Live web search via Brave Search API

**Financial Tools**:
5. `analyze_investment` - ROI, cap rate, cash flow analysis
6. `calculate_chiller_cost` - DEWA vs district cooling costs
7. `calculate_mortgage` - Monthly payments, total interest

**Building Intelligence**:
8. `search_building_issues` - Snagging reports, structural issues
9. `verify_title_deed` - Ownership, encumbrances (mock)

**Utility Tools**:
10. `compare_properties` - Side-by-side comparison matrix
11. `parse_property_details` - Extract structured data from queries

### 4. External Integrations

#### Brave Search API
- **Endpoint**: `https://api.search.brave.com/res/v1/web/search`
- **Authentication**: X-Subscription-Token header
- **Features**:
  - Auto-appends "Dubai real estate" context
  - Freshness filter (past month)
  - 10 results max per query
  - 15-second timeout
- **Fallback**: Graceful degradation with error message

#### RapidAPI (Bayut)
- **Endpoint**: `https://bayut.p.rapidapi.com/properties/list`
- **Status**: Mock data fallback (returns 404)
- **Future**: Real integration when API key provided

#### Anthropic Claude API
- **Endpoint**: `https://api.anthropic.com/v1/messages`
- **Authentication**: x-api-key header
- **Rate Limits**: Managed by user tier system
- **Retry Logic**: 3 retries with exponential backoff

### 5. Observability Stack

#### Metrics Collection (`observability.py`)
**Prometheus Counters**:
- `dubai_estate_queries_total{status, tier}` - Query volume by outcome
- `dubai_estate_tool_calls_total{tool_name, status}` - Tool usage patterns
- `dubai_estate_web_search_total{status}` - Web search success rate
- `dubai_estate_errors_total{error_type}` - Error tracking

**Prometheus Histograms**:
- `dubai_estate_query_duration_seconds` - Response time distribution
- `dubai_estate_claude_tokens{type}` - Token usage (input/output)

**Custom Logging**:
- Structured logs with context (user_id, query_id, tool_name)
- Multi-level: INFO, WARNING, ERROR
- Outputs to console + optional file

#### Monitoring Stack (Compose)
**Services** (`observability/docker-compose.yml`):
- **Prometheus**: Metrics storage and querying (port 9090)
- **Grafana**: Visualization dashboards (port 3000)
- **Loki**: Log aggregation
- **Tempo**: Distributed tracing
- **Promtail**: Log shipper

**Dashboards** (`observability/grafana/provisioning/dashboards/`):
- Dubai Estate AI Overview - KPIs, query volume, success rates
- Tool Performance - Tool call distribution, latency
- User Analytics - Tier distribution, query patterns

### 6. Data Flow

#### Concise Analysis Flow (30-60 seconds)
```
User: "Analyze 1BR in Marina Gate Tower 1, 650K AED"
  ↓
Telegram Bot: Progress indicator sent
  ↓
main.py: handle_query() called
  ↓
Claude API: Receives system prompt + query
  ↓
Claude: Requests tools (iteration 1)
  ├─ search_bayut_properties (Marina Gate, for-sale)
  └─ calculate_chiller_cost (Marina, 450 sqft)
  ↓
main.py: Execute tools, return results
  ↓
Claude: Requests tools (iteration 2)
  ├─ analyze_investment (650K, 55K rent, 450 sqft)
  └─ web_search_dubai ("Marina Gate Tower 1 reviews")
  ↓
main.py: Execute tools, return results
  ↓
Claude: Final response (concise format, 800-1200 words)
  ↓
Telegram Bot: Delete progress, send response + buttons
  ↓
User: Sees analysis with 4 action buttons
```

#### Full Report Flow (1-2 minutes)
```
User: Clicks "📊 Full Report" button
  ↓
Telegram Bot: Callback handler triggered
  ↓
Bot: Edit message → "📊 Generating full institutional report..."
  ↓
main.py: handle_query("Give me a full detailed analysis...")
  ↓
Claude: Detects "full detailed" keyword
  ↓
Claude: Executes 5-8 tools over 3-5 iterations
  ├─ All tools from concise analysis
  ├─ Additional web searches (3-4 total)
  ├─ get_supply_pipeline (zone-level data)
  └─ search_building_issues (snagging reports)
  ↓
Claude: Final response (11 sections, 2500-3500 words)
  ↓
Telegram Bot: Send multi-part response (split at 4096 chars)
```

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI 0.104.1
- **HTTP Client**: httpx (async)
- **Bot Framework**: python-telegram-bot 21.0+
- **AI**: Anthropic Claude API (Sonnet 4.5)

### External Services
- **Search**: Brave Search API
- **Real Estate Data**: RapidAPI (Bayut) - planned
- **AI**: Anthropic Claude API

### Observability
- **Metrics**: prometheus-client
- **Monitoring**: Prometheus, Grafana
- **Logging**: Loki, Promtail
- **Tracing**: Tempo (planned)

### Infrastructure
- **Local Development**: Python venv
- **Service Orchestration**: Docker Compose (observability only)
- **Deployment**: None (currently local-only)

### Data Storage
- **User Data**: JSON files (users_db.json)
- **Conversations**: JSON files (conversations_db.json)
- **Configuration**: .env files
- **Metrics**: Prometheus TSDB

## Security & Configuration

### Environment Variables (.env)
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
BRAVE_API_KEY=BSA...
TELEGRAM_BOT_TOKEN=123456:ABC...

# Optional
RAPIDAPI_KEY=your_key_here  # Bayut integration
PORT=8000                    # FastAPI port
LOG_LEVEL=INFO
```

### Security Measures
- API keys stored in .env (gitignored)
- No hardcoded secrets in code
- Input validation on all user queries
- Rate limiting by user tier
- Error messages sanitized (no API keys exposed)

### Rate Limiting
- **Free Tier**: 5 queries/day
- **Pro Tier**: 10 queries/day
- **Enterprise Tier**: Unlimited
- Reset: Daily at midnight UTC
- Enforcement: In-memory tracking (users_db.json)

## Deployment Architecture

### Current: Local Development
```
┌────────────────────────────────────┐
│   MacOS (Darwin 25.2.0)            │
│                                    │
│  ┌──────────────────────────────┐  │
│  │ Python venv                  │  │
│  │ - FastAPI (port 8000)        │  │
│  │ - Telegram Bot (polling)     │  │
│  │ - run.py (orchestrator)      │  │
│  └──────────────────────────────┘  │
│                                    │
│  ┌──────────────────────────────┐  │
│  │ Docker Compose               │  │
│  │ - Prometheus (9090)          │  │
│  │ - Grafana (3000)             │  │
│  │ - Loki (3100)                │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
         │
         │ (Internet)
         ↓
    ┌─────────────────┐
    │ External APIs   │
    │ - Claude API    │
    │ - Brave Search  │
    │ - Telegram API  │
    └─────────────────┘
```

### Planned: Cloud Deployment
```
┌──────────────────────────────────────────────────┐
│              Cloud Platform (Railway/Heroku)     │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │  Web Service (FastAPI)                     │  │
│  │  - Containerized                           │  │
│  │  - Health checks                           │  │
│  │  - Auto-scaling                            │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │  Worker Service (Telegram Bot)             │  │
│  │  - Long-polling mode                       │  │
│  │  - Separate dyno/container                 │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │  PostgreSQL Database                       │  │
│  │  - User management                         │  │
│  │  - Conversation history                    │  │
│  │  - Query logs                              │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │  Observability (Managed Services)          │  │
│  │  - Grafana Cloud                           │  │
│  │  - Prometheus (managed)                    │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## Performance Characteristics

### Response Times
- **Concise Analysis**: 30-60 seconds
  - Tool calls: 3-5
  - Web searches: 1-2
  - Claude iterations: 2-3

- **Full Report**: 1-2 minutes
  - Tool calls: 5-8
  - Web searches: 3-4
  - Claude iterations: 3-5

### Optimization Strategies
1. **Format Detection**: Automatically selects fast path for simple queries
2. **Parallel Tool Execution**: Future enhancement (currently serial)
3. **Strategic Web Search**: Only when hardcoded data insufficient
4. **Token Limits**: Lower max_tokens for concise format
5. **Early Exit**: Claude stops when confident (doesn't force max iterations)

### Bottlenecks
- **Serial Tool Execution**: Each Claude iteration waits for all tools
- **Web Search Latency**: 1-3 seconds per search
- **Claude API Latency**: 2-5 seconds per iteration
- **No Caching**: Every query runs fresh tools

### Scalability Limits (Current)
- **Concurrent Users**: Limited by single-process async
- **Data Storage**: In-memory JSON (no persistence across restarts)
- **Claude API**: Rate limits per API key (not per user)
- **No Queue System**: Long queries block bot responsiveness

## Error Handling

### Fallback Strategy
```
User Query
  ↓
Try Live API (Brave, Bayut, etc.)
  ↓
API Failed? (404, timeout, rate limit)
  ↓
Use Mock Data + Warning Message
  ↓
Continue Analysis (degraded but functional)
  ↓
Note data freshness in response
```

### Error Categories
1. **API Errors**: Fallback to mock, log warning
2. **Tool Execution Errors**: Return error to Claude, let it adapt
3. **User Input Errors**: Validate and return helpful message
4. **System Errors**: Log error, return generic failure message

### Observability of Failures
- Prometheus counter: `dubai_estate_errors_total{error_type}`
- Logs: Structured error logs with full context
- User Feedback: Graceful degradation messages

## Testing Strategy

### Test Coverage
- **Unit Tests**: `test_web_search.py` (12 tests)
  - Mock API responses
  - Edge cases (missing keys, timeouts)
  - Query context appending

- **Integration Tests**: Manual testing via Telegram
  - End-to-end query flow
  - Button interactions
  - Multi-turn conversations

### Missing Test Coverage
- No automated tests for:
  - Other tools (calculate_chiller_cost, analyze_investment, etc.)
  - Telegram bot handlers
  - Claude API integration
  - Error handling paths
  - Rate limiting logic

## Future Architecture Enhancements

### Short-term
1. **PostgreSQL Integration**: Replace JSON files
2. **Redis Caching**: Cache tool results (24-hour TTL)
3. **Webhook Mode**: Replace Telegram polling for better performance
4. **Queue System**: Celery/RQ for async job processing

### Medium-term
1. **Parallel Tool Execution**: Execute independent tools concurrently
2. **CDN for Media**: Serve property images via CDN
3. **PDF Generation**: Export full reports as PDFs
4. **Payment Integration**: Stripe for subscription management

### Long-term
1. **Multi-region Deployment**: UAE + global CDN
2. **Mobile App**: React Native with shared backend
3. **Microservices**: Split into user-service, analysis-service, data-service
4. **Real-time Updates**: WebSocket for live market data

## Monitoring & Alerts

### Key Metrics to Monitor
- Query success rate (target: >95%)
- P95 response time (target: <90s for concise, <150s for full)
- Tool failure rate per tool (track fallback usage)
- User tier distribution
- Claude API token consumption

### Recommended Alerts
- Query success rate drops below 90%
- Average response time exceeds 120 seconds
- Error rate exceeds 5%
- Claude API errors spike
- Disk usage exceeds 80% (for JSON files)

## Maintenance & Operations

### Daily
- Monitor Grafana dashboards
- Check error logs for anomalies
- Verify external API connectivity

### Weekly
- Review user feedback
- Analyze slow queries
- Update mock data with real market changes

### Monthly
- Audit API costs
- Review and update system prompt
- Security audit of dependencies
- Backup user data

### On-demand
- Restart bot if webhook/polling issues
- Clear conversation history for user privacy
- Update tool definitions for new features

---

**Document Version**: 1.0
**Architecture Version**: Feb 2026 (Post Web Search Integration)
**Maintained By**: Development Team
**Next Review**: March 2026
