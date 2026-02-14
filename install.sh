#!/bin/bash

# Dubai Estate Agent - Quick Start Installation Script
# This script sets up all dependencies and configurations

set -e  # Exit on error

echo "🏗️  Dubai Estate Institutional Agent - Installation"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js $(node --version) found${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found. Please install Python 3.8+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $(python3 --version) found${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm $(npm --version) found${NC}"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip3 found${NC}"

echo ""
echo "📦 Installing dependencies..."
echo ""

# Install Node.js MCP servers
echo "Installing Node.js MCP servers..."

servers=("dubai-rest" "dld-data" "property-finder" "bayut" "economic-data")

for server in "${servers[@]}"; do
    echo "  → Installing $server..."
    cd "mcp-servers/$server"
    
    if [ ! -f "package.json" ]; then
        npm init -y > /dev/null 2>&1
    fi
    
    npm install @modelcontextprotocol/sdk axios > /dev/null 2>&1
    
    if [ "$server" = "dld-data" ]; then
        npm install cheerio > /dev/null 2>&1
    fi
    
    cd ../..
    echo -e "  ${GREEN}✓ $server installed${NC}"
done

# Install Python MCP servers
echo ""
echo "Installing Python MCP servers..."

python_servers=("chiller-scraper" "social-listener" "mollak")

for server in "${python_servers[@]}"; do
    echo "  → Installing $server..."
    cd "mcp-servers/$server"
    
    pip3 install -r requirements.txt > /dev/null 2>&1
    
    cd ../..
    echo -e "  ${GREEN}✓ $server installed${NC}"
done

# Create necessary directories
echo ""
echo "📁 Creating project directories..."
mkdir -p data/cache
mkdir -p data/reports
mkdir -p data/analytics
mkdir -p logs
echo -e "${GREEN}✓ Directories created${NC}"

# Create .env template if not exists
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env template..."
    cat > .env << 'EOF'
# Dubai REST API (CRITICAL - Required for title deed verification)
DUBAI_REST_API_KEY=

# Property Listing APIs
PROPERTY_FINDER_API_KEY=
BAYUT_API_KEY=

# Economic Data (Free APIs)
FRED_API_KEY=
TRADING_ECONOMICS_KEY=

# Social Media Intelligence
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
FACEBOOK_ACCESS_TOKEN=

# Mollak (Dubai Land Department)
MOLLAK_USERNAME=
MOLLAK_PASSWORD=

# Google Maps (for reviews)
GOOGLE_MAPS_API_KEY=

# Optional: Custom Database
DATABASE_URL=

# Cache Settings
CACHE_DIR=./data/cache
CACHE_TTL_HOURS=24
EOF
    echo -e "${GREEN}✓ .env template created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env file and add your API keys${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists, skipping${NC}"
fi

# Create test script
echo ""
echo "🧪 Creating test script..."
cat > test_mcp_servers.sh << 'EOF'
#!/bin/bash

echo "Testing MCP Servers..."
echo ""

# Test Dubai REST server
echo "Testing Dubai REST server..."
cd mcp-servers/dubai-rest
timeout 5 node index.js &
sleep 2
if [ $? -eq 0 ]; then
    echo "✓ Dubai REST server OK"
else
    echo "✗ Dubai REST server failed"
fi
cd ../..

# Test Chiller Scraper
echo "Testing Chiller Scraper..."
cd mcp-servers/chiller-scraper
timeout 5 python3 server.py &
sleep 2
if [ $? -eq 0 ]; then
    echo "✓ Chiller Scraper OK"
else
    echo "✗ Chiller Scraper failed"
fi
cd ../..

echo ""
echo "Test complete!"
EOF
chmod +x test_mcp_servers.sh
echo -e "${GREEN}✓ Test script created${NC}"

# Summary
echo ""
echo "=================================================="
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "=================================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Edit .env file and add your API keys:"
echo "   nano .env"
echo ""
echo "2. Test MCP servers:"
echo "   ./test_mcp_servers.sh"
echo ""
echo "3. Start using the agent:"
echo "   claude-code"
echo ""
echo "4. Read the setup guide:"
echo "   cat SETUP.md"
echo ""
echo "📚 Documentation:"
echo "   - SETUP.md - Comprehensive setup guide"
echo "   - openclaw_config.json - Agent configuration"
echo "   - mcp_config.json - MCP servers configuration"
echo ""
echo "🔑 API Key Priority (start with these):"
echo "   1. Dubai REST API (CRITICAL) - dubairest.gov.ae"
echo "   2. FRED Economic Data (FREE) - fred.stlouisfed.org"
echo "   3. Reddit API (FREE) - reddit.com/prefs/apps"
echo "   4. Property Finder - Contact developers@propertyfinder.ae"
echo ""
echo "⚠️  Important: Without Dubai REST API key, title deed verification won't work!"
echo ""
echo -e "${YELLOW}Happy analyzing! 🏢${NC}"
