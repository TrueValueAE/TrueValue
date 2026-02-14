# 🏢 Dubai Estate AI - Project Context

**Give this file to Claude Code so it understands your business domain**

---

## 🎯 What We're Building

An AI-powered **institutional-grade real estate analysis platform** for Dubai, delivered via Telegram bot.

**Target Users:** Real estate agents in Dubai

**Core Value Prop:** Saves agents and buyers from expensive mistakes by analyzing hidden costs and building issues that traditional platforms miss.

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

### **Our Solution (AI-Powered Due Diligence)**

Agent asks bot:
```
"Validate: Marina Gate 1, Unit 2506, AED 2.5M"
```

Bot responds in 30 seconds:
```
⛔ DO NOT BUY

Red Flags:
1. Overpriced by 6.4% (AED 150K)
2. Chiller trap: Fixed Empower charges (AED 22.5K/year)
3. Building issues: 8 snagging reports (water damage)
4. Poor ROI: 1.08% net yield

Better Option:
Princess Tower #4509 - AED 2.6M
- Better value despite 4% premium
- 47% lower chiller costs
- No major building issues
- 4.2% net yield (4x better)
```

**Result:** Saved from AED 500K mistake, found better property

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

With our tool: Flagged immediately as "Chiller Trap"
```

**Data Source:** Scrape Empower/Lootah websites for rates

**Why Competitors Don't:**
- Bayut/Property Finder don't have this data
- Agents don't know to check
- Chiller providers don't advertise the trap

---

### **2. Social Intelligence (Snagging Reports)** ⭐⭐

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

Google Maps: 3.8★ (78 reviews)
- "Nice but maintenance issues"
- "Avoid if you can"

Our analysis: 62/100 quality score (MEDIUM concern)
```

**Data Source:**
- Reddit API (free)
- Facebook Graph API (requires approval)
- Google Maps scraping (free)

**Why Competitors Don't:**
- Requires NLP to analyze social data
- Manual work to aggregate
- Legal grey area (scraping)

---

### **3. Institutional-Grade Analysis** ⭐⭐

**Why It Matters:**
- Consumers/agents get analysis usually reserved for big investors
- 4-pillar framework is professional
- Builds trust and credibility

**The 4 Pillars:**

1. **Macro & Market**
   - Supply pipeline (oversupply risk)
   - Interest rate sensitivity
   - Zone momentum
   - Oil price correlation

2. **Liquidity & Exit**
   - Days on market (can you sell?)
   - Transaction volume trends
   - Cash vs mortgage ratios
   - Resale velocity

3. **Technical & Engineering**
   - Chiller costs ⭐
   - Building quality (snagging)
   - Maintenance reserves
   - MEP systems

4. **Legal & Regulatory**
   - Title deed verification
   - Service charges
   - Rental disputes
   - Compliance issues

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
6. **Arabian Ranches** - Villas, family-oriented
7. **JVC (Jumeirah Village Circle)** - Affordable, good yields
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
- Quick property analysis (< 1 min)
- Professional reports to share with clients
- Unique insights (chiller costs!)
- Mobile-friendly (Telegram preferred)

**Willingness to Pay:** AED 299/month if it helps close 1 extra deal

---

### **Secondary: Property Buyer (Investor)**

**Name:** Sarah, 38, British, Dubai expat
**Situation:** Buying first investment property
**Budget:** AED 1-2M
**Goal:** Rental income + appreciation
**Pain Points:**
- Overwhelmed by options
- Doesn't know what questions to ask
- Afraid of hidden costs
- No local knowledge

**What She Needs:**
- Simple GO/NO-GO recommendations
- Explanation of risks
- Comparison of options
- Trust in the analysis

**Willingness to Pay:** AED 99/month during search period

---

### **Tertiary: Real Estate Agency (Team)**

**Name:** Premium Properties LLC
**Size:** 15 agents
**Revenue:** AED 5M/year
**Pain Points:**
- Need consistent analysis across team
- Want to offer premium service
- Agents have varying expertise levels
- Manual research is time-consuming

**What They Need:**
- White-label reports (their branding)
- API access for CRM integration
- Unlimited usage for team
- Priority support

**Willingness to Pay:** AED 1,999/month for 15-agent license

---

## 🏗️ Technical Architecture Context

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

### **Why Claude API?**
- Best at following instructions
- Tool use (function calling)
- Long context window
- Can understand real estate nuances
- Reliable

### **Why One File (main.py)?**
- Faster to build
- Easier to deploy
- Simpler to debug
- Can refactor later
- No over-engineering

---

## 📐 Core Business Logic

### **Investment Score Formula**

```python
def calculate_investment_score(property, analysis):
    score = 50  # Start at neutral
    
    # Price score (30 points)
    if property.price < analysis.fair_value * 0.95:
        score += 30  # Great deal
    elif property.price < analysis.fair_value * 1.05:
        score += 15  # Fair price
    else:
        score += 0   # Overpriced
    
    # Yield score (25 points)
    if analysis.net_yield > 6:
        score += 25  # Excellent
    elif analysis.net_yield > 4:
        score += 15  # Good
    elif analysis.net_yield > 3:
        score += 5   # Acceptable
    else:
        score += 0   # Poor
    
    # Liquidity score (20 points)
    if analysis.dom < 30:
        score += 20  # Very liquid
    elif analysis.dom < 60:
        score += 10  # Moderate
    else:
        score += 0   # Slow
    
    # Quality score (15 points)
    if analysis.building_issues < 3:
        score += 15  # Excellent quality
    elif analysis.building_issues < 7:
        score += 7   # Acceptable
    else:
        score += 0   # Concerning
    
    # Chiller score (10 points)
    if analysis.chiller_cost_per_sqft < 10:
        score += 10  # Good
    elif analysis.chiller_cost_per_sqft < 15:
        score += 5   # Acceptable
    else:
        score += 0   # Trap!
    
    return min(100, score)
```

### **Decision Matrix**

```
Score 80-100: ✅ STRONG BUY
Score 60-79:  ✅ GOOD BUY  
Score 40-59:  ⚠️ PROCEED WITH CAUTION
Score 20-39:  ⚠️ NEGOTIATE HARD
Score 0-19:   ⛔ DO NOT BUY
```

---

## 🎯 Success Metrics

### **Technical Metrics**
- Response time: < 30 seconds
- Accuracy: 85%+ confidence
- Uptime: 99%+
- API cost: < AED 100/1000 queries

### **Business Metrics**
- User retention: > 60%
- NPS score: > 50
- Conversion (free to paid): > 10%
- Churn: < 5%/month

### **Quality Metrics**
- Agent feedback: "Saved me from bad deal"
- User reports: "Recommendations accurate"
- Testimonials: "Better than my own research"

---

## 🚨 Red Flags (What to Always Flag)

### **CRITICAL (Must Warn)**
1. Chiller cost > AED 15/sqft/year
2. Overpriced > 10%
3. Net yield < 2%
4. 10+ snagging reports
5. Supply ratio > 2.0 (oversupply)

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
  - BAD: Fixed capacity charges
  - Typical: AED 15-20/sqft/year
  
- **Lootah** (covers some Marina areas)
  - GOOD: Variable charges only
  - Typical: AED 8-12/sqft/year

- **Dubai Central** (less common)
- **Palm District Cooling** (Palm Jumeirah)

### **Service Charge Norms**
- Apartment: AED 8-15/sqft/year
- Villa: AED 5-10/sqft/year
- High-end: AED 15-25/sqft/year

### **Transaction Costs**
- **Buyer pays:**
  - DLD fee: 4% of price
  - Agent fee: 2% of price
  - Mortgage fee: ~1% (if financing)
  - Total: ~7% of purchase price

- **Seller pays:**
  - Agent fee: 2% of price
  - No capital gains tax (yet)

### **Rental Market**
- Most leases: 12 months
- Payment: 1-4 cheques (more cheques = better for landlord)
- Agent fee: 5% of annual rent (tenant pays)
- Deposit: Usually 5-10% of annual rent

---

## 📱 Communication Style

### **For Telegram Responses**

**DO:**
- Use emojis for visual scanning (🏢 💰 ✅ ⚠️ ❌)
- Bold key numbers
- Keep sentences short
- Use bullet points
- Highlight red flags clearly
- End with clear recommendation

**DON'T:**
- Write paragraphs
- Use jargon without explanation
- Be vague ("might be a risk")
- Overwhelm with data
- Bury the conclusion

**Example GOOD Response:**
```
🏢 Marina Gate 1 #2506

💰 PRICE: AED 2.5M (6.4% OVERPRICED ❌)
📏 1,500 sqft | 🛏️ 2BR

⚠️ RED FLAGS:
1. Chiller trap: AED 22.5K/year
2. Building issues: 8 reports
3. Poor yield: 1.08% net

🎯 VERDICT: ⛔ DO NOT BUY

💡 BETTER OPTION:
Princess Tower #4509
AED 2.6M, 4.2% yield, no issues
```

**Example BAD Response:**
```
After analyzing the property located in Marina Gate 1, specifically unit number 2506, we have conducted a comprehensive evaluation across multiple dimensions including market dynamics, liquidity metrics, technical specifications, and regulatory compliance. The findings indicate several areas of concern that warrant careful consideration before proceeding with this investment opportunity. [continues for 3 paragraphs...]
```

---

## 🎓 Teach Claude Code This

When working with Claude Code, reference this file:

```
"Read CONTEXT.md to understand the Dubai real estate domain.

Key points:
- Chiller costs are critical (our moat!)
- Target users are agents (fast, mobile-first)
- Responses should be concise and actionable
- Red flags must be obvious
- We're replacing manual research with AI

Build everything with this context in mind."
```

---

## ✅ Quality Standards

Every analysis must:
- [ ] Include all 4 pillars
- [ ] Flag chiller costs if >AED 10/sqft
- [ ] Show comparable properties
- [ ] Give clear GO/NO-GO
- [ ] Complete in <30 seconds
- [ ] Be accurate (>85% confidence)
- [ ] Be actionable (what to do next)

---

**This context ensures Claude Code builds exactly what your business needs!** 🚀
