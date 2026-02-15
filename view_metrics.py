#!/usr/bin/env python3
"""
View Dubai Estate AI Metrics Dashboard
======================================
Run this to see real-time metrics and analytics
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from observability import metrics_tracker, user_analytics
import json
from datetime import datetime


def print_header(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_metrics():
    """Display application metrics"""
    print_header("📊 APPLICATION METRICS")

    summary = metrics_tracker.get_summary()

    print(f"\n🔢 Query Statistics:")
    print(f"   Total Queries:      {summary['total_queries']}")
    print(f"   Successful:         {summary['success_queries']}")
    print(f"   Failed:             {summary['failed_queries']}")
    print(f"   Success Rate:       {summary['success_rate']}")
    print(f"   Error Rate:         {summary['error_rate']}")

    print(f"\n💰 Cost Tracking:")
    print(f"   Total Cost:         {summary['total_cost_usd']}")
    print(f"   Avg Cost/Query:     {summary['avg_cost_per_query']}")

    print(f"\n⚡ Performance:")
    print(f"   Avg Response Time:  {summary['response_times']['avg_ms']}ms")
    print(f"   P50 (median):       {summary['response_times']['p50_ms']}ms")
    print(f"   P95:                {summary['response_times']['p95_ms']}ms")
    print(f"   P99:                {summary['response_times']['p99_ms']}ms")

    print(f"\n👥 User Statistics:")
    print(f"   Unique Users:       {summary['unique_users']}")

    if summary['most_used_tools']:
        print(f"\n🛠️  Most Used Tools:")
        for tool, count in summary['most_used_tools'].items():
            print(f"   {tool:30s} {count:3d} times")

    if summary['errors_by_type']:
        print(f"\n❌ Errors by Type:")
        for error_type, count in summary['errors_by_type'].items():
            print(f"   {error_type:30s} {count:3d} times")

    if summary.get('top_users_by_queries'):
        print(f"\n🏆 Top Users (by queries):")
        for user_id, count in summary['top_users_by_queries'].items():
            print(f"   User {user_id:15s} {count:3d} queries")


def print_funnel():
    """Display conversion funnel"""
    print_header("🎯 CONVERSION FUNNEL")

    funnel = user_analytics.get_funnel()

    print(f"\n📈 User Journey:")
    print(f"   Signups:                  {funnel['signups']}")
    print(f"   Users with Queries:       {funnel['users_with_queries']}")
    print(f"   Users Hit Limit:          {funnel['users_hit_limit']}")
    print(f"   Upgrades:                 {funnel['upgrades']}")

    print(f"\n💡 Conversion Rates:")
    print(f"   Signup → First Query:     {funnel['signup_to_query_rate']}")
    print(f"   Limit Hit → Upgrade:      {funnel['limit_to_upgrade_rate']}")


def print_recent_activity():
    """Display recent queries"""
    print_header("🔄 RECENT ACTIVITY")

    recent = metrics_tracker.recent_queries[-10:]  # Last 10

    if not recent:
        print("\n   No recent activity")
        return

    print(f"\n   Last {len(recent)} queries:")
    for query in reversed(recent):
        status = "✅" if query.success else "❌"
        print(f"\n   {status} User {query.user_id} - {query.timestamp[:19]}")
        print(f"      Query: {query.query[:50]}...")
        print(f"      Duration: {query.duration_ms:.0f}ms | Cost: ${query.cost_usd:.4f}")
        if query.tools_used:
            print(f"      Tools: {', '.join(query.tools_used)}")
        if query.error:
            print(f"      Error: {query.error[:100]}")


def export_json():
    """Export metrics as JSON"""
    print_header("📤 EXPORTING TO JSON")

    data = {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics_tracker.get_summary(),
        "funnel": user_analytics.get_funnel(),
        "recent_queries": [
            {
                "user_id": q.user_id,
                "query": q.query,
                "success": q.success,
                "duration_ms": q.duration_ms,
                "cost_usd": q.cost_usd,
                "tools_used": q.tools_used,
                "timestamp": q.timestamp,
            }
            for q in metrics_tracker.recent_queries[-50:]  # Last 50
        ]
    }

    filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n   ✅ Metrics exported to: {filename}")


def main():
    """Main dashboard"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         Dubai Estate AI - Metrics Dashboard              ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    print_metrics()
    print_funnel()
    print_recent_activity()

    print("\n")
    print("─" * 60)
    export_choice = input("\nExport metrics to JSON? (y/n): ")
    if export_choice.lower() == 'y':
        export_json()

    print("\n" + "=" * 60)
    print("  Dashboard complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting dashboard...\n")
        sys.exit(0)
