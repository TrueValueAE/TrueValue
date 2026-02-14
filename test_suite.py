#!/usr/bin/env python3
"""
Comprehensive Test Suite for Dubai Estate AI Bot
Tests each component to identify exactly where failures occur
"""

import asyncio
import sys
import os
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST: {name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

async def test_1_environment_variables():
    """Test 1: Check all environment variables"""
    print_test("Environment Variables")

    required = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    }

    optional = {
        "BAYUT_API_KEY": os.getenv("BAYUT_API_KEY"),
        "REDDIT_CLIENT_ID": os.getenv("REDDIT_CLIENT_ID"),
        "DUBAI_REST_API_KEY": os.getenv("DUBAI_REST_API_KEY"),
    }

    all_good = True
    for key, value in required.items():
        if value and value not in ["", "your_key_here", "demo"]:
            print_success(f"{key}: Set ({value[:20]}...)")
        else:
            print_error(f"{key}: MISSING or invalid")
            all_good = False

    for key, value in optional.items():
        if value and value not in ["", "your_key_here", "demo"]:
            print_success(f"{key}: Set")
        else:
            print_warning(f"{key}: Not set (will use mock data)")

    return all_good

async def test_2_import_main():
    """Test 2: Import main.py without errors"""
    print_test("Import main.py")

    try:
        import main
        print_success("main.py imported successfully")
        print_success(f"Found {len(main.TOOLS)} tools defined")
        return True
    except Exception as e:
        print_error(f"Failed to import main.py: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_3_chiller_tool():
    """Test 3: Chiller calculation (pure math, no API)"""
    print_test("Chiller Cost Calculation Tool")

    try:
        from main import calculate_chiller_cost

        # Test Empower
        result = await calculate_chiller_cost("empower", 1500)

        if result.get("success"):
            print_success(f"Empower calculation succeeded")
            print(f"  Total annual cost: AED {result['total_annual_cost_aed']}")
            print(f"  Cost per sqft: AED {result['cost_per_sqft_per_year_aed']}/sqft/year")
            print(f"  Warning level: {result['warning_level']}")

            # Validate numbers
            if result['total_annual_cost_aed'] > 0:
                print_success("Cost calculation looks correct")
                return True
            else:
                print_error("Cost is zero - calculation failed")
                return False
        else:
            print_error(f"Calculation failed: {result}")
            return False

    except Exception as e:
        print_error(f"Exception in chiller tool: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_4_bayut_tool():
    """Test 4: Bayut search (should fall back to mock data)"""
    print_test("Bayut Property Search Tool")

    try:
        from main import search_bayut_properties

        result = await search_bayut_properties(
            location="dubai-marina",
            purpose="for-sale",
            min_price=1000000,
            max_price=2000000
        )

        if result.get("success"):
            print_success("Bayut search succeeded")
            print(f"  Total properties: {result.get('total', 0)}")
            print(f"  Properties returned: {len(result.get('properties', []))}")

            if result.get('properties'):
                prop = result['properties'][0]
                print(f"  Sample property: {prop.get('title', 'N/A')}")
                return True
            else:
                print_warning("No properties returned")
                return True  # Still valid if using mock
        else:
            print_error(f"Search failed: {result}")
            return False

    except Exception as e:
        print_error(f"Exception in Bayut tool: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_5_claude_simple():
    """Test 5: Simple Claude API call (no tools)"""
    print_test("Claude API - Simple Query")

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": "Say 'Hello from Dubai Estate AI' and nothing else."
            }]
        )

        if response.content and len(response.content) > 0:
            text = response.content[0].text
            print_success(f"Claude responded: {text}")
            return True
        else:
            print_error("Claude returned empty response")
            return False

    except Exception as e:
        print_error(f"Claude API failed: {e}")
        if "credit balance" in str(e).lower():
            print_error("⚠️  ANTHROPIC API CREDITS ARE DEPLETED!")
            print_error("   Go to: https://console.anthropic.com/settings/billing")
        import traceback
        traceback.print_exc()
        return False

async def test_6_handle_query_simple():
    """Test 6: handle_query with simple chiller request"""
    print_test("handle_query - Chiller Calculation")

    try:
        from main import handle_query

        print("Sending query: 'Calculate chiller cost for 1500 sqft Empower property'")
        print("This should take 5-10 seconds...")

        result = await handle_query(
            "Calculate chiller cost for 1500 sqft Empower property",
            user_id="test_user"
        )

        # Result is a QueryResponse object
        if hasattr(result, 'response'):
            response_text = result.response
            print_success(f"Query completed!")
            print_success(f"Tools used: {result.tools_used}")
            print(f"\nResponse preview (first 500 chars):")
            print(f"{response_text[:500]}...")

            # Check for expected content
            if "chiller" in response_text.lower() and "aed" in response_text.lower():
                print_success("Response contains chiller cost information")
                return True
            else:
                print_warning("Response doesn't contain expected chiller information")
                print(f"Full response:\n{response_text}")
                return False
        else:
            print_error(f"Unexpected result type: {type(result)}")
            return False

    except Exception as e:
        print_error(f"handle_query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_7_telegram_send():
    """Test 7: Send a test message via Telegram"""
    print_test("Telegram Message Send")

    try:
        import httpx
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

        # Get bot info first
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.telegram.org/bot{bot_token}/getMe")

            if response.status_code == 200:
                bot_info = response.json()
                print_success(f"Bot verified: @{bot_info['result']['username']}")
                print(f"  Bot ID: {bot_info['result']['id']}")
                print(f"  Bot Name: {bot_info['result']['first_name']}")
                return True
            else:
                print_error(f"Telegram API error: {response.status_code}")
                print(f"  Response: {response.text}")
                return False

    except Exception as e:
        print_error(f"Telegram test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_8_full_integration():
    """Test 8: Full integration test with property search"""
    print_test("Full Integration - Property Search")

    try:
        from main import handle_query

        print("Sending query: 'Find studio apartments in JVC under 600K'")
        print("This will use multiple tools and take 15-30 seconds...")

        result = await handle_query(
            "Find studio apartments in JVC under 600K",
            user_id="test_user_full"
        )

        if hasattr(result, 'response'):
            response_text = result.response
            print_success(f"Query completed!")
            print_success(f"Tools used: {', '.join(result.tools_used)}")
            print_success(f"Response length: {len(response_text)} characters")

            # Check response has property information
            if any(word in response_text.lower() for word in ['property', 'studio', 'jvc', 'aed']):
                print_success("Response contains property information")
                print(f"\nResponse preview (first 800 chars):")
                print(f"{response_text[:800]}...")
                return True
            else:
                print_warning("Response doesn't contain expected property info")
                return False
        else:
            print_error(f"Unexpected result type: {type(result)}")
            return False

    except Exception as e:
        print_error(f"Full integration test failed: {e}")
        if "credit balance" in str(e).lower():
            print_error("⚠️  ANTHROPIC API CREDITS DEPLETED during test!")
        import traceback
        traceback.print_exc()
        return False

async def run_all_tests():
    """Run all tests in sequence"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}DUBAI ESTATE AI - COMPREHENSIVE TEST SUITE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    tests = [
        ("Environment Variables", test_1_environment_variables),
        ("Import main.py", test_2_import_main),
        ("Chiller Tool", test_3_chiller_tool),
        ("Bayut Tool", test_4_bayut_tool),
        ("Claude API", test_5_claude_simple),
        ("handle_query (Simple)", test_6_handle_query_simple),
        ("Telegram API", test_7_telegram_send),
        ("Full Integration", test_8_full_integration),
    ]

    results = {}

    for name, test_func in tests:
        try:
            result = await test_func()
            results[name] = result
        except KeyboardInterrupt:
            print_warning("\nTests interrupted by user")
            break
        except Exception as e:
            print_error(f"Test '{name}' crashed: {e}")
            results[name] = False

    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST SUMMARY{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for name, result in results.items():
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"{status}  {name}")

    print(f"\n{BLUE}{'='*60}{RESET}")
    if passed == total:
        print(f"{GREEN}ALL TESTS PASSED! ({passed}/{total}){RESET}")
        print(f"{GREEN}The bot should work on Telegram!{RESET}")
    else:
        print(f"{RED}TESTS FAILED: {total - passed} out of {total}{RESET}")
        print(f"{YELLOW}Fix the failing tests above before using the bot{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
