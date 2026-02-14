# Dubai Estate Institutional Real Estate Agent - Setup Guide

## 🏗️ Architecture Overview

This institutional-grade Dubai real estate agent uses OpenClaw with multiple MCP (Model Context Protocol) servers to provide comprehensive property analysis across 4 critical pillars:

1. **Macro & Market Analysis** - Supply pipeline, interest rates, oil correlation
2. **Liquidity & Exit Strategy** - Days on market, volume analysis, cash ratios
3. **Technical & Engineering** - MEP audits, chiller charges, snagging reports
4. **Legal & Regulatory** - Title verification, rental disputes, service charges

## 📁 Project Structure

```
dubai-estate-agent/
├── openclaw_config.json          # Main agent configuration
├── mcp_config.json                # MCP servers configuration
├── mcp-servers/                   # MCP server implementations
│   ├── dubai-rest/               # Dubai REST API integration
│   │   ├── index.js
│   │   └── package.json
│   ├── dld-data/                 # Dubai Land Dept Open Data
│   │   ├── index.js
│   │   └── package.json
│   ├── property-finder/          # Property Finder API
│   │   ├── index.js
│   │   └── package.json
│   ├── bayut/                    # Bayut Analytics
│   │   ├── index.js
│   │   └── package.json
│   ├── chiller-scraper/          # Empower/Lootah scraper
│   │   ├── server.py
│   │   └── requirements.txt
│   ├── social-listener/          # Reddit/FB/Maps intelligence
│   │   ├── server.py
│   │   └── requirements.txt
│   ├── economic-data/            # FRED/Trading Economics
│   │   ├── index.js
│   │   └── package.json
│   └── mollak/                   # Mollak service charge data
│       ├── server.py
│       └── requirements.txt
├── data/                          # Data cache and storage
├── reports/                       # Generated reports
├── scripts/                       # Utility scripts
└── docs/                          # Documentation
```

## 🚀 Installation Steps

### Step 1: Install OpenClaw (Claude Code)

```bash
# Install Claude Code (OpenClaw)
npm install -g @anthropic-ai/claude-code

# Verify installation
claude-code --version
```

### Step 2: Clone and Setup Project

```bash
# Create project directory
mkdir ~/dubai-estate-agent
cd ~/dubai-estate-agent

# Copy all files from this setup
# (openclaw_config.json, mcp_config.json, mcp-servers/, etc.)
```

### Step 3: Install MCP Server Dependencies

#### Node.js MCP Servers

```bash
# Dubai REST API Server
cd mcp-servers/dubai-rest
npm init -y
npm install @modelcontextprotocol/sdk axios

# DLD Open Data Server
cd ../dld-data
npm init -y
npm install @modelcontextprotocol/sdk axios cheerio

# Property Finder Server
cd ../property-finder
npm init -y
npm install @modelcontextprotocol/sdk axios

# Bayut Server
cd ../bayut
npm init -y
npm install @modelcontextprotocol/sdk axios

# Economic Data Server
cd ../economic-data
npm init -y
npm install @modelcontextprotocol/sdk axios
```

#### Python MCP Servers

```bash
# Chiller Scraper Server
cd mcp-servers/chiller-scraper
cat > requirements.txt << EOF
mcp
httpx
beautifulsoup4
lxml
EOF
pip install -r requirements.txt

# Social Intelligence Server
cd ../social-listener
cat > requirements.txt << EOF
mcp
httpx
praw
beautifulsoup4
facebook-sdk
EOF
pip install -r requirements.txt

# Mollak Integration Server
cd ../mollak
cat > requirements.txt << EOF
mcp
httpx
selenium
beautifulsoup4
EOF
pip install -r requirements.txt
```

### Step 4: Configure API Keys

Create a `.env` file in the project root:

```bash
# Dubai REST API
DUBAI_REST_API_KEY=your_api_key_here

# Property Finder
PROPERTY_FINDER_API_KEY=your_api_key_here

# Bayut
BAYUT_API_KEY=your_api_key_here

# Economic Data
FRED_API_KEY=your_fred_api_key
TRADING_ECONOMICS_KEY=your_trading_economics_key

# Social Media
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
FACEBOOK_ACCESS_TOKEN=your_facebook_token

# Mollak (Dubai Land Dept)
MOLLAK_USERNAME=your_mollak_username
MOLLAK_PASSWORD=your_mollak_password

# Google Maps (for reviews)
GOOGLE_MAPS_API_KEY=your_google_maps_key
```

### Step 5: Configure OpenClaw

Update the MCP config file paths in `mcp_config.json`:

```json
{
  "mcpServers": {
    "dubai-rest-api": {
      "command": "node",
      "args": ["/full/path/to/dubai-estate-agent/mcp-servers/dubai-rest/index.js"],
      "env": {
        "DUBAI_REST_API_KEY": "${DUBAI_REST_API_KEY}"
      }
    },
    // ... update all paths with full absolute paths
  }
}
```

### Step 6: Configure Claude Code to Use MCP Servers

Add to your Claude Code configuration file (`~/.config/claude-code/config.json` or similar):

```json
{
  "mcpServers": {
    // Copy the entire mcpServers object from mcp_config.json
  }
}
```

### Step 7: Test MCP Servers Individually

```bash
# Test Dubai REST server
cd mcp-servers/dubai-rest
export DUBAI_REST_API_KEY=your_key
node index.js

# Test Chiller Scraper
cd ../chiller-scraper
python server.py

# Test Social Listener
cd ../social-listener
export REDDIT_CLIENT_ID=your_id
export REDDIT_CLIENT_SECRET=your_secret
python server.py
```

## 🔧 Configuration Details

### OpenClaw Agent Configuration

The `openclaw_config.json` contains:

- **Research Modules**: 4 main pillars with data sources and metrics
- **Data Integrations**: API endpoints, scraping targets, social listening
- **Analysis Workflows**: Property evaluation, zone comparison, portfolio optimization
- **Risk Framework**: Red flags, confidence scoring, alerts
- **Output Templates**: Institutional reports, quick analysis formats
- **Automation**: Daily, weekly, monthly tasks

### MCP Server Capabilities

Each MCP server provides specific tools:

#### Dubai REST API Server
- `verify_title_deed` - Verify ownership
- `check_encumbrances` - Check mortgages/liens
- `ownership_history` - Get transaction history
- `property_valuation` - Official DLD valuation

#### Chiller Rates Scraper
- `get_empower_rates` - Empower chiller rates
- `get_lootah_rates` - Lootah rates
- `calculate_chiller_cost` - Annual cost calculation
- `compare_chiller_costs` - Building comparison

#### Social Intelligence Server
- `search_building_issues` - Find snagging reports
- `get_zone_reputation` - Zone sentiment analysis
- `track_developer_sentiment` - Developer reputation
- `get_common_complaints` - Aggregate complaints

## 📊 API Key Acquisition Guide

### Critical APIs

1. **Dubai REST API** (CRITICAL)
   - Website: https://dubairest.gov.ae
   - Required for: Title deed verification
   - Cost: Variable, contact for pricing

2. **Dubai Land Department Open Data** (FREE)
   - Website: https://www.dubailand.gov.ae/en/open-data
   - Required for: Transaction data, pricing trends
   - Cost: Free

3. **Property Finder API**
   - Contact: developers@propertyfinder.ae
   - Required for: Listings, market analytics
   - Cost: Commercial license required

4. **Bayut API**
   - Contact: api@bayut.com
   - Required for: Listings, trends
   - Cost: Commercial license required

5. **FRED Economic Data** (FREE)
   - Website: https://fred.stlouisfed.org/docs/api/api_key.html
   - Required for: Interest rates, economic indicators
   - Cost: Free

6. **Reddit API** (FREE)
   - Website: https://www.reddit.com/prefs/apps
   - Required for: Social intelligence
   - Cost: Free

### Optional but Recommended

7. **Google Maps API**
   - For building reviews
   - Cost: $200 free credit/month

8. **Trading Economics API**
   - For UAE economic data
   - Cost: Starts at $500/month

## 🎯 Usage Examples

### Example 1: Evaluate a Property

```javascript
// In OpenClaw/Claude Code
await evaluateProperty({
  building: "Marina Gate 1",
  unit: "2506",
  asking_price: 2500000,
  area_sqft: 1500
});
```

This will:
1. Verify title deed via Dubai REST
2. Check DOM and liquidity via Property Finder/Bayut
3. Scrape chiller rates for Marina
4. Search social media for snagging reports
5. Generate institutional report with recommendation

### Example 2: Compare Zones

```javascript
await compareZones({
  zones: ["Business Bay", "JBR", "Downtown"],
  criteria: ["liquidity", "roi", "risk"]
});
```

### Example 3: Monitor Portfolio

```javascript
await monitorPortfolio({
  properties: [/* your properties */],
  alerts: ["supply_risk", "liquidity_drop", "regulatory_change"]
});
```

## 🚨 Red Flags to Watch

The agent automatically flags:

1. **Supply Oversupply** - Completion ratio > 2.0 in zone
2. **Liquidity Crisis** - DOM > 90 days + volume drop > 40%
3. **Chiller Trap** - Fixed charges > AED 15/sqft/year
4. **Legal Disputes** - > 5 rental disputes/year in building
5. **Developer Risk** - Poor delivery track record

## 📈 Data Refresh Schedule

- **Daily**: Transactions, DOM metrics, regulatory changes, interest rates
- **Weekly**: Chiller rates, snagging reports, developer watchlist
- **Monthly**: Supply pipeline, portfolio rebalancing, market reports

## 🔒 Security & Compliance

- All API keys stored in environment variables
- No sensitive data logged
- Rate limiting on all external APIs
- Compliance with DLD data usage policies

## 🐛 Troubleshooting

### MCP Server Not Connecting

```bash
# Check if server starts manually
cd mcp-servers/dubai-rest
node index.js
# Should output: "Dubai REST API MCP server running on stdio"
```

### API Rate Limits

- Dubai REST: 100 requests/hour
- Property Finder: 1000 requests/day
- Bayut: 500 requests/day
- Reddit: 60 requests/minute

### Common Issues

1. **"API key invalid"** - Check .env file and export commands
2. **"Module not found"** - Run `npm install` or `pip install -r requirements.txt`
3. **"Permission denied"** - Check file permissions: `chmod +x server.py`

## 📚 Additional Resources

- OpenClaw Documentation: https://docs.anthropic.com/claude-code
- MCP Protocol: https://modelcontextprotocol.io
- Dubai REST API Docs: https://dubairest.gov.ae/docs
- DLD Open Data: https://www.dubailand.gov.ae/en/open-data

## 🎓 Training the Agent

To improve agent performance:

1. **Feed it historical deals** - Upload past transactions for pattern learning
2. **Update red flags** - Add zone-specific warnings based on experience
3. **Calibrate thresholds** - Adjust DOM, price, and risk thresholds
4. **Add custom metrics** - Build proprietary indicators

## 🚀 Next Steps

1. Complete API key acquisition (start with free ones)
2. Test each MCP server individually
3. Run first property evaluation
4. Set up automated daily reports
5. Build custom dashboards

## 💡 Pro Tips

1. **Start with Business Bay** - Most data available, good test case
2. **Focus on chiller costs first** - Biggest ROI killer
3. **Cross-reference Reddit + Google Maps** - Best snagging intel
4. **Monitor off-plan vs ready ratio** - Leading liquidity indicator
5. **Track developer completion rates** - Predict delays

---

## Support

For issues or questions:
- Email: your-support-email@domain.com
- GitHub Issues: github.com/yourrepo/dubai-estate-agent
- Documentation: Full docs in /docs folder
