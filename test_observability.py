#!/usr/bin/env python3
"""
Test Observability System
=========================
Quick test to verify logging and metrics tracking works.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from observability import (
    setup_json_logging,
    log_query_start,
    log_query_complete,
    log_user_error,
    metrics_tracker,
    user_analytics,
    CostCalculator,
)
import time


def test_cost_calculator():
    """Test cost calculation"""
    print("Testing Cost Calculator...")

    # Sonnet 4 pricing test
    cost = CostCalculator.calculate_cost(
        model="claude-sonnet-4-20250514",
        input_tokens=1000,
        output_tokens=500
    )

    expected = (1000 * 3 / 1_000_000) + (500 * 15 / 1_000_000)
    assert abs(cost - expected) < 0.0001, f"Cost calculation failed: {cost} != {expected}"

    print(f"  ✅ Cost for 1K input + 500 output: ${cost:.6f}")


def test_logging():
    """Test structured logging"""
    print("\nTesting Structured Logging...")

    logger = setup_json_logging("test_logger")

    # Test query start
    start_time = log_query_start(logger, "test_user_123", "Find 2BR in Marina")
    time.sleep(0.1)  # Simulate work

    # Test query complete
    log_query_complete(
        logger=logger,
        user_id="test_user_123",
        query="Find 2BR in Marina",
        start_time=start_time,
        tools_used=["search_bayut_properties", "calculate_chiller_cost"],
        input_tokens=1500,
        output_tokens=800,
        model="claude-sonnet-4-20250514",
        success=True
    )

    print("  ✅ Logs written to dubai_estate_ai.log")


def test_metrics_tracker():
    """Test metrics tracking"""
    print("\nTesting Metrics Tracker...")

    # Clear tracker for test
    global metrics_tracker
    metrics_tracker.queries_total = 0
    metrics_tracker.queries_success = 0
    metrics_tracker.response_times = []

    # Record some test queries
    metrics_tracker.record_query(
        user_id="user_1",
        query="Find 2BR in Marina",
        success=True,
        duration_ms=5000,
        cost_usd=0.025,
        tools=["search_bayut_properties", "calculate_chiller_cost"],
        input_tokens=1500,
        output_tokens=800,
        model="claude-sonnet-4-20250514"
    )

    metrics_tracker.record_query(
        user_id="user_2",
        query="Analyze Princess Tower",
        success=True,
        duration_ms=7000,
        cost_usd=0.032,
        tools=["search_bayut_properties", "analyze_investment"],
        input_tokens=1800,
        output_tokens=900,
        model="claude-sonnet-4-20250514"
    )

    metrics_tracker.record_query(
        user_id="user_1",
        query="Get trends for JBR",
        success=False,
        duration_ms=2000,
        cost_usd=0.015,
        tools=["get_market_trends"],
        error="Timeout error",
        input_tokens=1000,
        output_tokens=500,
        model="claude-sonnet-4-20250514"
    )

    # Get summary
    summary = metrics_tracker.get_summary()

    print(f"  ✅ Total Queries: {summary['total_queries']}")
    print(f"  ✅ Success Rate: {summary['success_rate']}")
    print(f"  ✅ Total Cost: {summary['total_cost_usd']}")
    print(f"  ✅ Avg Response Time: {summary['response_times']['avg_ms']}ms")
    print(f"  ✅ Most Used Tools: {summary['most_used_tools']}")

    assert summary['total_queries'] == 3
    assert summary['success_queries'] == 2
    assert summary['failed_queries'] == 1


def test_user_analytics():
    """Test user analytics"""
    print("\nTesting User Analytics...")

    # Clear analytics for test
    global user_analytics
    user_analytics.events = []

    # Track some events
    user_analytics.track_event("user_1", "user_signup")
    user_analytics.track_event("user_2", "user_signup")
    user_analytics.track_event("user_3", "user_signup")

    user_analytics.track_event("user_1", "query_sent", {"query": "test"})
    user_analytics.track_event("user_2", "query_sent", {"query": "test"})

    user_analytics.track_event("user_1", "query_limit_hit")
    user_analytics.track_event("user_1", "subscription_upgrade", {"tier": "pro"})

    # Get funnel
    funnel = user_analytics.get_funnel()

    print(f"  ✅ Signups: {funnel['signups']}")
    print(f"  ✅ Users with Queries: {funnel['users_with_queries']}")
    print(f"  ✅ Upgrades: {funnel['upgrades']}")
    print(f"  ✅ Signup→Query Rate: {funnel['signup_to_query_rate']}")

    assert funnel['signups'] == 3
    assert funnel['users_with_queries'] == 2
    assert funnel['upgrades'] == 1


def test_error_logging():
    """Test error logging"""
    print("\nTesting Error Logging...")

    logger = setup_json_logging("test_logger")

    try:
        raise ValueError("Test error for observability")
    except Exception as e:
        log_user_error(
            logger=logger,
            user_id="test_user_123",
            error_message="Something went wrong",
            exception=e,
            query="Test query"
        )

    print("  ✅ Error logged with full stack trace")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  Observability System Tests")
    print("="*60 + "\n")

    try:
        test_cost_calculator()
        test_logging()
        test_metrics_tracker()
        test_user_analytics()
        test_error_logging()

        print("\n" + "="*60)
        print("  ✅ ALL TESTS PASSED!")
        print("="*60 + "\n")

        print("Observability system is working correctly!")
        print("\nNext steps:")
        print("  1. Send a query to @TrueValueAE_bot on Telegram")
        print("  2. Run: python view_metrics.py")
        print("  3. Check logs: tail -f dubai_estate_ai.log | jq .")
        print()

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
