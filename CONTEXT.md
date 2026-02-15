# 🏢 Dubai Estate AI - Project Context

**Updated: February 15, 2026**

**Give this file to Claude Code so it understands your business domain**

---

## 🎯 What We're Building

An AI-powered **institutional-grade real estate analysis platform** for Dubai, delivered via Telegram bot with live web search validation and dual-format analysis system.

**Target Users:** Real estate agents and property investors in Dubai

**Core Value Prop:** Saves agents and buyers from expensive mistakes by analyzing hidden costs, building issues, and market conditions that traditional platforms miss — validated with real-time web data.

---

## 💰 The Problem We're Solving

### **Current State (Broken)**

When someone wants to buy property in Dubai:

1. **They search Bayut/Property Finder**
   - See: Price, bedrooms, photos
   - DON'T see: Chiller costs, building issues, market context

2. **They visit the property**
   - See: Nice finishes, good view
   - DON'T see: Fixed capacity charges will cost AED 20K/year

3. **They make an offer**
   - Think: "Good deal at AED 2.5M"
   - Reality: Overpriced by AED 150K, hidden costs destroy ROI

4. **They buy and regret**
   - Chiller bills: AED 2,000/month (expected AED 500)
   - Water leakage discovered (was reported on Reddit)
   - Can't sell (market oversupplied in that zone)

**Result:** Lost AED 100K-500K on a bad investment

---

### **Our Solution (AI-Powered Due Diligence with Live Validation)**

Agent asks bot:
```
"Analyze Marina Gate 1 studio, AED 650K"
```

Bot responds in ~60 seconds:
```
🏢 MARINA GATE 1 STUDIO
AED 650K | 500 sqft | AED 1,300/sqft

━━━━━━━━━━━━━━━━━━━━━━━━
🎯 VERDICT: ✅ STRONG BUY
Investment Score: 78/100
━━━━━━━━━━━━━━━━━━━━━━━━

💰 WHY BUY:
1. 7.35% net yield ⭐
2. Lootah chiller (saves AED 15K/year vs Empower)
3. 4% below market average
4. Established rental demand

⚠️ WATCH FOR:
- Limited liquidity (60-90 days to sell)
- Title deed verification needed
- Request building maintenance history

🌐 WEB CHECK (Live Intel)
━━━━━━━━━━━━━━━━━━━━━━━━
✅ Checked 2 recent sources:
• Market trends: Studio demand up 25% YoY
• Supply check: No major competing projects in area

💡 Impact: Validates strong yield opportunity
```

**Then interactive buttons appear:**
```
┌─────────────────┬──────────────────┐
│ 📊 Full Report  │ 📈 Compare       │
├─────────────────┼──────────────────┤
│ 💰 Mortgage     │ 🔍 Web Search    │
└─────────────────┴──────────────────┘
```

**Result:** Fast, actionable analysis with on-demand depth

---

## 🔑 Our Unique Advantages (The Moat)

### **1. Chiller Cost Analysis** ⭐⭐⭐ (BIGGEST MOAT)

**Why It Matters:**
- Dubai buildings use district cooling (chiller)
- Two providers: Empower (bad) vs Lootah (good)
- Empower charges FIXED capacity fees (AED 85/TR/month)
- Can add AED 15K-30K/year to costs
- **NOBODY ELSE TRACKS THIS**

**Example:**
```
Property: 1500 sqft, Empower chiller
- Expected cost: AED 6K/year (what buyers think)
- Actual cost: AED 22.5K/year (reality)
- Hidden cost: AED 16.5K/year
- 10-year impact: AED 165K lost ROI

With our tool: Flagged immediately as "Chiller Trap" ⭐
```

**Data Source:** Pure math calculation (no API needed - built into our tool)

---

### **2. Live Web Search Validation** ⭐⭐⭐ (NEW - Feb 2026)

**Why It Matters:**
- Hardcoded data goes stale
- Market conditions change daily
- Building issues emerge over time
- Competing supply appears

**What We Search:**
1. **Building-specific:** "[building name] reviews snagging Dubai"
2. **Market trends:** "[zone] property prices 2024 2025 trends"
3. **Supply validation:** "[zone] new launches oversupply"

**Example:**
```
Query: "Arjan studio market analysis"

Web Search finds:
• Studios now 25% of transactions (up from 22%)
• New Arthouse Hills project (Q4 2028) - future competition
• Yield premiums holding in outer zones

Impact: Validates investment thesis + identifies future risk
```

**Technology:** Brave Search API (fast, privacy-focused, no rate limits)

**Why Competitors Don't:**
- Requires AI to synthesize web results with structured data
- Integration complexity
- API costs

---

### **3. Dual-Format Analysis System** ⭐⭐ (NEW - Feb 2026)

**Why It Matters:**
- Users want different depth at different times
- Mobile users need speed first, depth later
- Progressive disclosure = better UX

**Two Formats:**

**Concise (Default - 1 minute response):**
```
🏢 Property Name
━━━━━━━━━━━━━━
🎯 VERDICT: ✅ STRONG BUY
Score: 78/100

💰 WHY BUY: [3-4 key points]
⚠️ WATCH FOR: [3 risks]
📊 4-PILLAR BREAKDOWN: [grades A/B/C]
🌐 WEB CHECK: [validated findings]
```

**Full Report (On-demand - 2 minutes):**
- 11-section institutional analysis
- Tables, comparisons, scenarios
- Exit strategy modeling
- Financing impact
- Complete due diligence

**Trigger:** Click "📊 Full Report" button

**Why Competitors Don't:**
- Most tools are one-size-fits-all
- No interactive depth control
- Either too simple OR too complex

---

### **4. Social Intelligence (Snagging Reports)** ⭐⭐

**Why It Matters:**
- New buildings often have defects (snagging)
- Owners complain on Reddit/Facebook
- These groups have REAL experiences
- Nobody aggregates this data

**Example:**
```
Building: Marina Gate 1
Reddit mentions (r/dubai):
- "Water leakage in bedroom" (3 posts)
- "Elevator broken again" (2 posts)
- "AC not working properly" (3 posts)

Our analysis: 62/100 quality score (MEDIUM concern)
```

**Data Source:**
- Reddit API (free) + PRAW library
- Web search for recent mentions
- Aggregated mock data (fallback)

---

### **5. Interactive UX with Progress Indicators** ⭐⭐ (NEW - Feb 2026)

**Why It Matters:**
- 60-second analysis feels like forever with no feedback
- Users abandon if they think it's broken
- Buttons enable progressive disclosure

**User Flow:**
1. User sends query
2. **Instant:** "🔍 Analyzing... ⏱️ This will take 30-60 seconds"
3. Bot runs analysis (user knows it's working)
4. **60 seconds:** Concise response appears with 4 action buttons
5. User clicks button for deeper analysis

**Why Competitors Don't:**
- Most bots send one message and wait
- No progress indicators
- No interactive follow-ups

---

## 📊 The Dubai Real Estate Market (Context)

### **Market Size**
- AED 500B+ annual transactions
- 100K+ property transactions/year
- 50K+ real estate agents
- 3M+ residents (70% expats)

### **Key Zones**
1. **Dubai Marina** - High-end, high liquidity, tourist area
2. **Downtown Dubai** - Premium, Burj Khalifa area
3. **Business Bay** - Business district, CAUTION: oversupply risk 2026
4. **JBR (Jumeirah Beach Residence)** - Beachfront, very liquid
5. **Palm Jumeirah** - Ultra-luxury, low supply
6. **Arjan** - Mid-market, family-oriented, high yields
7. **JVC (Jumeirah Village Circle)** - Affordable, yield trap warning
8. **International City** - Budget, high yields, lower quality

### **Typical Prices (2024-2025)**
- Studio: AED 400K-800K
- 1BR: AED 800K-1.5M
- 2BR: AED 1.5M-3M
- 3BR: AED 2.5M-5M
- Villa: AED 3M-20M+

### **Typical Yields**
- Gross: 5-8% (good)
- Net: 3-5% (after costs)
- **With chiller trap: 1-2% (bad)**
- **Outer zones (Arjan): 7-9% gross, 5-7% net**

---

## 🎭 User Personas

### **Primary: Real Estate Agent (Individual)**

**Name:** Ahmed, 32, Egyptian, Dubai-based
**Experience:** 3 years as agent
**Clients:** 5-10 active buyers at any time
**Pain Points:**
- Needs to analyze 50+ properties/week
- Clients ask: "Is this a good deal?"
- Hard to differentiate from other agents
- Loses deals to agents with better insights

**What He Needs:**
- Quick property analysis (< 1 min) ✅
- Professional reports to share with clients ✅
- Unique insights (chiller costs!) ✅
- Mobile-friendly (Telegram preferred) ✅
- Live market validation ✅ NEW

**Willingness to Pay:** AED 299/month if it helps close 1 extra deal

---

## 🏗️ Technical Architecture Context

### **Stack**
- **Backend:** FastAPI (async, fast, type-safe)
- **AI:** Claude Sonnet 4 (tool use, long context)
- **Search:** Brave Search API (live web validation)
- **Bot:** python-telegram-bot (async, reliable)
- **Observability:** Prometheus + Grafana + Loki
- **Deployment:** Local (can deploy to Heroku/Railway)

### **Why FastAPI?**
- Fast (async support)
- Easy to learn
- Great docs
- Type hints built-in
- Perfect for MVP

### **Why Telegram?**
- Where Dubai users already are
- Easy to build bot
- No app store approval needed
- Works on all devices
- Free to use
- Interactive buttons support

### **Why Claude API?**
- Best at following instructions
- Tool use (function calling)
- Long context window (handles full analysis)
- Can understand real estate nuances
- Reliable and fast

### **Why Brave Search API?**
- Fast responses (<5s)
- Privacy-focused (no tracking)
- Good coverage of global + regional content
- Simple API (no complex auth)
- Reasonable pricing

---

## 📐 Core Business Logic

### **Investment Score Formula (4-Pillar Framework)**

```python
def calculate_investment_score(property, analysis):
    total_score = 0

    # PILLAR 1: Price Score (30 points)
    price_ratio = property.price_per_sqft / zone_average_sqft
    if price_ratio <= 0.85:
        total_score += 30  # Deep value
    elif price_ratio <= 0.95:
        total_score += 25
    elif price_ratio <= 1.05:
        total_score += 20
    elif price_ratio <= 1.15:
        total_score += 12
    else:
        total_score += 5   # Overpriced

    # PILLAR 2: Yield Score (25 points)
    if analysis.gross_yield >= 8.0:
        total_score += 25
    elif analysis.gross_yield >= 7.0:
        total_score += 22
    elif analysis.gross_yield >= 6.0:
        total_score += 18
    elif analysis.gross_yield >= 5.0:
        total_score += 12
    else:
        total_score += 5

    # PILLAR 3: Liquidity Score (20 points)
    liquidity_map = {
        "downtown-dubai": 20,
        "dubai-marina": 18,
        "palm-jumeirah": 17,
        "jumeirah-beach-residence": 16,
        "business-bay": 13,
        "arjan": 10,
        "jumeirah-village-circle": 8,
    }
    total_score += liquidity_map.get(zone, 12)

    # PILLAR 4: Quality/Supply Risk Score (15 points)
    supply_risk = get_supply_risk(zone)
    quality_map = {"LOW": 15, "MODERATE": 11, "HIGH": 6, "VERY HIGH": 2}
    total_score += quality_map.get(supply_risk, 8)

    # PILLAR 5: Chiller Score (10 points)
    if analysis.chiller_warning == "LOW":
        total_score += 10
    elif analysis.chiller_warning == "MEDIUM":
        total_score += 6
    else:
        total_score += 2

    # Chiller trap penalty
    if analysis.chiller_trap_detected:
        total_score = max(0, total_score - 2)

    return min(100, total_score)
```

### **Decision Matrix**

```
Score 80-100: ✅ STRONG BUY
Score 60-79:  ✅ GOOD BUY
Score 40-59:  🟡 CAUTION
Score 20-39:  ⚠️ NEGOTIATE
Score 0-19:   ❌ DO NOT BUY
```

---

## 📱 Communication Style

### **For Concise Format (Default)**

**DO:**
- Use emojis for visual hierarchy (🏢 💰 ✅ 🟡 ⚠️ ❌)
- Use ━━━━━ dividers between sections
- Lead with verdict FIRST
- Keep each point to ONE LINE
- Use grade system (A+/A/B+/B/C)
- Put chiller trap warnings with ⭐ emoji
- End with interactive CTAs

**DON'T:**
- Write paragraphs
- Use markdown --- dividers (use ━━━━━)
- Bury the conclusion
- Include tables (save for full format)

**Example GOOD Concise Response:**
```
🏢 MARINA GATE 1 STUDIO
AED 650K | 500 sqft | AED 1,300/sqft

━━━━━━━━━━━━━━━━━━━━━━━━
🎯 VERDICT: ✅ STRONG BUY
Investment Score: 78/100
━━━━━━━━━━━━━━━━━━━━━━━━

💰 WHY BUY:
1. 7.35% net yield ⭐
2. Lootah chiller (saves AED 15K/year)
3. 4% below market
4. Strong rental demand

⚠️ WATCH FOR:
- Verify title deed
- 60-90 day sell time
- Request maintenance history

━━━━━━━━━━━━━━━━━━━━━━━━
📊 4-PILLAR BREAKDOWN
━━━━━━━━━━━━━━━━━━━━━━━━

🏛️ MACRO & MARKET: B+
✅ 4% below zone average
✅ 7.35% gross yield
🟡 Moderate supply risk

💧 LIQUIDITY & COSTS: A
✅ Lootah = AED 28/year only
✅ Net yield: 7.35%
🎯 Annual profit: AED 47,772

🏗️ TECHNICAL & QUALITY: B
✅ Established community
⚠️ Limited snagging data

⚖️ LEGAL & COMPLIANCE: B
🟡 Title verification needed

━━━━━━━━━━━━━━━━━━━━━━━━
🌐 WEB CHECK (Live Intel)
━━━━━━━━━━━━━━━━━━━━━━━━

✅ Checked 2 recent sources:
• Market: Studios up 25% in transactions
• Supply: No major competing projects

💡 Impact: Validates yield opportunity
```

### **For Full Format (On-Demand)**

**Structure:**
1. Executive Summary
2. 4-Pillar Deep Dive
3. Live Market Intelligence (web search)
4. Key Metrics Table
5. Comparative Analysis
6. Exit Strategy & Scenarios
7. Financing Impact
8. Target Tenant Profile
9. Red Flags & Mitigation
10. Decision Matrix
11. Action Items

---

## 🎯 Success Metrics

### **Technical Metrics**
- Response time: < 60 seconds ✅
- Concise format: 30-60s ✅
- Full format: 1-2 minutes ✅
- Accuracy: 85%+ confidence ✅
- Uptime: 99%+
- API cost: < AED 0.10/query ✅

### **UX Metrics (NEW - Feb 2026)**
- Progress indicator shown: 100% ✅
- Button click-through rate: Target >40%
- Full report requests: Target 20-30% of queries
- User satisfaction: Target NPS >60

### **Business Metrics**
- User retention: > 60%
- NPS score: > 50
- Conversion (free to paid): > 10%
- Churn: < 5%/month
- Time saved per analysis: ~30 minutes vs manual

---

## 🚨 Red Flags (What to Always Flag)

### **CRITICAL (Must Warn)**
1. Chiller cost > AED 15/sqft/year ⭐
2. Overpriced > 10%
3. Net yield < 2%
4. 10+ snagging reports
5. Supply ratio > 2.0 (oversupply)
6. Title deed issues

### **WARNING (Mention but Not Dealbreaker)**
1. Chiller cost AED 10-15/sqft
2. Overpriced 5-10%
3. Net yield 2-3%
4. 5-10 snagging reports
5. DOM > 60 days

---

## 💡 Domain Knowledge

### **Chiller Providers in Dubai**
- **Empower** (covers Marina, JBR, Business Bay)
  - BAD: Fixed capacity charges (AED 85/TR/month)
  - Typical: AED 15-20/sqft/year
  - **Chiller Trap: YES** ⚠️

- **Lootah** (covers some zones)
  - GOOD: Variable charges only
  - Typical: AED 8-12/sqft/year
  - **Chiller Trap: NO** ✅

- **Dubai Central** (less common)
- **Palm District Cooling** (Palm Jumeirah)

### **Service Charge Norms**
- Apartment: AED 8-15/sqft/year
- Villa: AED 5-10/sqft/year
- High-end: AED 15-25/sqft/year
- **RERA Cap:** Max AED 25/sqft for most buildings

### **Transaction Costs**
- **Buyer pays:**
  - DLD fee: 4% of price
  - Agent fee: 2% of price
  - Mortgage fee: ~1% (if financing)
  - Total: ~7% of purchase price

- **Seller pays:**
  - Agent fee: 2% of price
  - No capital gains tax (yet)

---

## ✅ Quality Standards

Every analysis must:
- [ ] Include all 4 pillars
- [ ] Flag chiller costs if >AED 10/sqft ⭐
- [ ] Run 1-2 web searches for validation (concise) or 3-4 (full)
- [ ] Give clear GO/NO-GO verdict
- [ ] Complete in <60 seconds (concise) or <2 min (full)
- [ ] Show progress indicator
- [ ] Include interactive buttons
- [ ] Be actionable (what to do next)

---

## 🎓 Teach Claude Code This

When working with Claude Code, reference this file:

```
"Read CONTEXT.md to understand the Dubai real estate domain.

Key points:
- Chiller costs are critical (our moat!) ⭐
- Target users are agents (fast, mobile-first)
- Use concise emoji format by default
- Web search validates findings (1-2 searches)
- Progress indicators prevent abandonment
- Interactive buttons enable depth on-demand
- Responses should be actionable

Build everything with this context in mind."
```

---

**Last Updated:** February 15, 2026
**Status:** Production-ready with live web search and dual-format system ✅
