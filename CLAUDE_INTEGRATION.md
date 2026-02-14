# 🤖 Claude API Integration Guide

## How to Actually Use This Platform

This guide shows you how to integrate Claude with your MCP servers for a **production application**.

---

## 🎯 Architecture Overview

```
User Query (Telegram/Web)
        ↓
Your Application (Python/Node.js)
        ↓
Claude API (with tool definitions)
        ↓
Your MCP Servers (when Claude needs data)
        ↓
Return results to user
```

## 📝 Step-by-Step Integration

### Step 1: Install Anthropic SDK

```bash
pip install anthropic
# or
npm install @anthropic-ai/sdk
```

### Step 2: Define Your Tools (from MCP Servers)

```python
# tools_config.py

DUBAI_ESTATE_TOOLS = [
    {
        "name": "search_bayut_properties",
        "description": "Search for properties on Bayut with filters",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Location name (e.g., 'dubai-marina')"
                },
                "purpose": {
                    "type": "string",
                    "enum": ["for-sale", "for-rent"],
                    "description": "Property purpose"
                },
                "min_price": {
                    "type": "number",
                    "description": "Minimum price in AED"
                },
                "max_price": {
                    "type": "number",
                    "description": "Maximum price in AED"
                },
                "property_type": {
                    "type": "string",
                    "description": "Property type (apartment, villa, etc.)"
                }
            },
            "required": ["location", "purpose"]
        }
    },
    {
        "name": "verify_title_deed",
        "description": "Verify property ownership and title deed via Dubai REST API",
        "input_schema": {
            "type": "object",
            "properties": {
                "title_deed_number": {
                    "type": "string",
                    "description": "Title deed number"
                }
            },
            "required": ["title_deed_number"]
        }
    },
    {
        "name": "calculate_chiller_cost",
        "description": "Calculate annual chiller/cooling costs for a property",
        "input_schema": {
            "type": "object",
            "properties": {
                "provider": {
                    "type": "string",
                    "enum": ["empower", "lootah"],
                    "description": "Chiller provider"
                },
                "area_sqft": {
                    "type": "number",
                    "description": "Property area in square feet"
                }
            },
            "required": ["provider", "area_sqft"]
        }
    },
    {
        "name": "search_building_issues",
        "description": "Search for snagging reports and issues from Reddit, Facebook, Google Maps",
        "input_schema": {
            "type": "object",
            "properties": {
                "building_name": {
                    "type": "string",
                    "description": "Building name"
                },
                "months_back": {
                    "type": "number",
                    "description": "How many months back to search (default: 12)"
                }
            },
            "required": ["building_name"]
        }
    },
    {
        "name": "get_market_trends",
        "description": "Get market trends and statistics for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Location name"
                },
                "purpose": {
                    "type": "string",
                    "enum": ["for-sale", "for-rent"]
                }
            },
            "required": ["location", "purpose"]
        }
    },
    # Add all 20+ tools here...
]
```

### Step 3: Create Tool Execution Layer

```python
# tool_executor.py

import httpx
import json

class MCPToolExecutor:
    """Executes MCP server tools based on Claude's requests"""
    
    def __init__(self):
        self.bayut_url = "http://localhost:8001"  # Your Bayut MCP server
        self.dubai_rest_url = "http://localhost:8002"
        self.chiller_url = "http://localhost:8003"
        self.social_url = "http://localhost:8004"
        # ... other servers
    
    async def execute_tool(self, tool_name: str, tool_input: dict):
        """Route tool execution to appropriate MCP server"""
        
        if tool_name == "search_bayut_properties":
            return await self._call_bayut(tool_input)
        
        elif tool_name == "verify_title_deed":
            return await self._call_dubai_rest(tool_input)
        
        elif tool_name == "calculate_chiller_cost":
            return await self._call_chiller_scraper(tool_input)
        
        elif tool_name == "search_building_issues":
            return await self._call_social_listener(tool_input)
        
        # ... handle all tools
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    async def _call_bayut(self, inputs):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.bayut_url}/search_properties",
                json=inputs
            )
            return response.json()
    
    async def _call_dubai_rest(self, inputs):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.dubai_rest_url}/verify_title_deed",
                json=inputs
            )
            return response.json()
    
    # ... implement other _call methods
```

### Step 4: Create Main Agent Class

```python
# agent.py

import anthropic
from tools_config import DUBAI_ESTATE_TOOLS
from tool_executor import MCPToolExecutor

class DubaiEstateAgent:
    """Main agent that orchestrates Claude + MCP servers"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.executor = MCPToolExecutor()
        self.conversation_history = []
    
    async def process_query(self, user_query: str, max_iterations: int = 5):
        """
        Process user query with Claude, executing tools as needed
        
        Args:
            user_query: User's question/request
            max_iterations: Max tool use iterations (prevent infinite loops)
        
        Returns:
            Final text response to user
        """
        
        # Add user message to conversation
        self.conversation_history.append({
            "role": "user",
            "content": user_query
        })
        
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call Claude with tools
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system="""You are a Dubai real estate expert assistant. 
                
You have access to comprehensive data sources including:
- Property listings (Bayut, Property Finder, Dubizzle)
- Title deed verification (Dubai REST API)
- Chiller cost analysis (Empower/Lootah data)
- Social intelligence (Reddit/Facebook snagging reports)
- Market trends and analytics

Provide institutional-grade analysis covering:
1. Macro & Market context
2. Liquidity & Exit strategy
3. Technical & Engineering due diligence (especially chiller costs!)
4. Legal & Regulatory compliance

Be concise but thorough. Always flag red flags clearly.
Give GO/NO-GO recommendations when analyzing specific properties.""",
                tools=DUBAI_ESTATE_TOOLS,
                messages=self.conversation_history
            )
            
            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Add Claude's response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Execute all requested tools
                tool_results = []
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        tool_id = content_block.id
                        
                        print(f"🔧 Executing tool: {tool_name}")
                        
                        # Execute tool via MCP server
                        result = await self.executor.execute_tool(
                            tool_name, 
                            tool_input
                        )
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": json.dumps(result)
                        })
                
                # Add tool results to conversation
                self.conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })
                
                # Continue loop - Claude will process results
                continue
            
            elif response.stop_reason == "end_turn":
                # Claude finished, extract final text response
                final_text = ""
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        final_text += content_block.text
                
                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_text
                })
                
                return final_text
            
            else:
                # Unexpected stop reason
                return f"Unexpected response: {response.stop_reason}"
        
        return "Max iterations reached. Query too complex."
```

### Step 5: Use in Your Application

```python
# main.py or telegram_bot.py

import asyncio
from agent import DubaiEstateAgent
import os

async def main():
    # Initialize agent
    agent = DubaiEstateAgent(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    # Example query
    query = """
    I'm looking at Marina Gate 1, Unit 2506, asking price AED 2.5M, 
    1500 sqft. Should I buy it? Give me a comprehensive analysis.
    """
    
    print("🤖 Processing query...")
    response = await agent.process_query(query)
    print("\n" + "="*50)
    print("📊 ANALYSIS:")
    print("="*50)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🚀 For Production (Telegram Bot)

```python
# telegram_bot_with_claude.py

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from agent import DubaiEstateAgent
import os

class TelegramBot:
    def __init__(self):
        self.agent = DubaiEstateAgent(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.app = Application.builder().token(
            os.getenv("TELEGRAM_BOT_TOKEN")
        ).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_message
        ))
    
    async def start(self, update: Update, context):
        await update.message.reply_text(
            "🏢 Welcome to Dubai Estate AI!\n\n"
            "Ask me anything about Dubai properties:\n"
            "• Search for properties\n"
            "• Analyze investments\n"
            "• Check chiller costs\n"
            "• Market trends\n\n"
            "Just type your question!"
        )
    
    async def handle_message(self, update: Update, context):
        user_query = update.message.text
        
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        # Process with Claude + MCP servers
        response = await self.agent.process_query(user_query)
        
        # Send response
        await update.message.reply_text(response)
    
    def run(self):
        self.app.run_polling()

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
```

---

## 🔧 Running MCP Servers

You need to run your MCP servers first:

```bash
# Terminal 1: Bayut server
cd mcp-servers/bayut-listings
node index.js

# Terminal 2: Dubai REST server
cd mcp-servers/dubai-rest
node index.js

# Terminal 3: Chiller scraper
cd mcp-servers/chiller-scraper
python3 server.py

# Terminal 4: Social listener
cd mcp-servers/social-listener
python3 server.py

# Terminal 5: Your main app
python3 telegram_bot_with_claude.py
```

**Better: Use Docker Compose** (see DEPLOYMENT_GUIDE.md)

---

## 💡 Key Points

### ✅ You Have Everything:
- MCP servers (your data sources)
- Tool definitions (how Claude calls them)
- Integration pattern (how to connect)

### ⚠️ What You Need to Add:
1. HTTP endpoints to your MCP servers (currently stdio)
2. Tool executor to route Claude's requests
3. Main agent loop (provided above)

### 🚀 Alternative: Simpler Approach

Instead of running separate MCP servers, you could:

```python
# Embed tool logic directly

async def search_bayut(location, purpose, min_price, max_price):
    # Call Bayut API directly
    response = await httpx.get(
        "https://bayut.p.rapidapi.com/properties/list",
        params={...}
    )
    return response.json()

# Then Claude calls your Python functions directly
```

This is simpler but less modular.

---

## 🎯 Recommendation

**For MVP (first 3 months):**
- Embed tool logic in your bot
- Call APIs directly from Python
- Keep it simple

**For Scale (month 6+):**
- Separate MCP servers
- Microservices architecture
- Docker deployment

---

## 📚 Resources

- [Anthropic Tool Use Docs](https://docs.anthropic.com/claude/docs/tool-use)
- [MCP Protocol Spec](https://modelcontextprotocol.io)
- Example code in this package

**You're ready to build! 🚀**
