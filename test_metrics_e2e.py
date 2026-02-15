#!/usr/bin/env python3
"""
End-to-end test for metrics collection
Simulates a complete query flow and verifies metrics are recorded
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_metrics_flow():
    """Test complete metrics collection flow"""

    print("=" * 60)
    print("🧪 METRICS END-TO-END TEST")
    print("=" * 60)

    # Step 1: Import main and observability
    print("\n1️⃣  Importing modules...")
    from main import handle_query
    from observability import get_prometheus_metrics

    print("   ✅ Modules imported successfully")

    # Step 2: Check baseline metrics
    print("\n2️⃣  Checking baseline metrics...")
    baseline_metrics = get_prometheus_metrics()
    baseline_queries = baseline_metrics.count('dubai_estate_queries_total')
    print(f"   📊 Baseline query counter appearances: {baseline_queries}")

    # Step 3: Execute a test query
    print("\n3️⃣  Executing test query...")
    test_query = (
        "Perform comprehensive institutional analysis on: "
        "Marina Gate Tower 1, Dubai Marina. "
        "Include all 4 pillars: Macro/Market, Liquidity, Technical, Legal. "
        "Provide GO/NO-GO recommendation with investment score."
    )
    test_user_id = "test_user_12345"

    print(f"   Query: {test_query[:80]}...")
    print(f"   User ID: {test_user_id}")

    try:
        result = await handle_query(test_query, user_id=test_user_id)
        print("   ✅ Query completed successfully!")
        print(f"   📝 Response length: {len(result.response)} chars")
        print(f"   🔧 Tools used: {len(result.tools_used)}")
        for tool in result.tools_used:
            print(f"      - {tool}")
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Check metrics after query
    print("\n4️⃣  Checking metrics after query...")
    await asyncio.sleep(1)  # Give metrics a moment to be written

    after_metrics = get_prometheus_metrics()

    # Parse metrics
    print("\n   📊 Metrics collected:")

    # Check for query counters
    query_total_lines = [line for line in after_metrics.split('\n')
                         if 'dubai_estate_queries_total' in line and not line.startswith('#')]
    if query_total_lines:
        print("   ✅ Query counters found:")
        for line in query_total_lines[:5]:
            print(f"      {line}")
    else:
        print("   ❌ No query counters found!")

    # Check for query duration
    duration_lines = [line for line in after_metrics.split('\n')
                      if 'dubai_estate_query_duration_seconds' in line and not line.startswith('#')]
    if duration_lines:
        print("   ✅ Query duration histograms found:")
        for line in duration_lines[:3]:
            print(f"      {line}")
    else:
        print("   ❌ No query duration histograms found!")

    # Check for tool usage
    tool_lines = [line for line in after_metrics.split('\n')
                  if 'dubai_estate_tool_usage_total' in line and not line.startswith('#')]
    if tool_lines:
        print("   ✅ Tool usage counters found:")
        for line in tool_lines[:5]:
            print(f"      {line}")
    else:
        print("   ❌ No tool usage counters found!")

    # Check for token metrics
    token_lines = [line for line in after_metrics.split('\n')
                   if 'dubai_estate_tokens_total' in line and not line.startswith('#')]
    if token_lines:
        print("   ✅ Token counters found:")
        for line in token_lines[:3]:
            print(f"      {line}")
    else:
        print("   ❌ No token counters found!")

    # Check for cost metrics
    cost_lines = [line for line in after_metrics.split('\n')
                  if 'dubai_estate_query_cost_usd' in line and not line.startswith('#')]
    if cost_lines:
        print("   ✅ Cost metrics found:")
        for line in cost_lines[:3]:
            print(f"      {line}")
    else:
        print("   ❌ No cost metrics found!")

    # Step 5: Check multiprocess directory
    print("\n5️⃣  Checking multiprocess directory...")
    multiproc_dir = os.path.join(os.path.dirname(__file__), 'prometheus_multiproc_dir')
    if os.path.exists(multiproc_dir):
        files = os.listdir(multiproc_dir)
        print(f"   📁 Files in directory: {len(files)}")
        for f in files:
            size = os.path.getsize(os.path.join(multiproc_dir, f))
            print(f"      {f} ({size} bytes)")
    else:
        print("   ❌ Multiprocess directory not found!")

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    has_queries = len(query_total_lines) > 0
    has_duration = len(duration_lines) > 0
    has_tools = len(tool_lines) > 0
    has_tokens = len(token_lines) > 0
    has_cost = len(cost_lines) > 0

    checks = [
        ("Query counters", has_queries),
        ("Duration histograms", has_duration),
        ("Tool usage", has_tools),
        ("Token counters", has_tokens),
        ("Cost metrics", has_cost),
    ]

    passed = sum(1 for _, status in checks if status)
    total = len(checks)

    for name, status in checks:
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")

    print(f"\n🎯 Result: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Metrics are working correctly!")
        return True
    else:
        print("⚠️  Some metrics are missing. Check configuration.")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_metrics_flow())
    sys.exit(0 if success else 1)
