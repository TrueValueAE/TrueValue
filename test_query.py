#!/usr/bin/env python3
"""
TrueValue AI — CLI Test Harness
================================
Test queries directly without Telegram or a running server.

Usage:
  python test_query.py "Analyze a 1BR in Dubai Marina for investment"
  python test_query.py                          # interactive REPL mode
  python test_query.py --cost-only "query"      # just show token/cost stats
"""

import asyncio
import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

# Colors
GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
BLUE   = '\033[94m'
DIM    = '\033[2m'
BOLD   = '\033[1m'
RESET  = '\033[0m'

_initialized = False

async def _init_once():
    """Initialize database and cache (required by handle_query)."""
    global _initialized
    if _initialized:
        return
    from database import init_db
    from cache import init_cache
    await init_db()
    await init_cache()
    _initialized = True


async def run_query(query: str, user_id: str = "cli_test", show_response: bool = True):
    """Run a single query and print results with metrics."""
    await _init_once()
    from main import handle_query
    from observability import CostCalculator

    model = "claude-haiku-4-5-20251001"

    print(f"\n{BLUE}{'━'*60}{RESET}")
    print(f"{BOLD}Query:{RESET} {query}")
    print(f"{BLUE}{'━'*60}{RESET}")

    wall_start = time.time()
    result = await handle_query(query=query, user_id=user_id)
    wall_elapsed = time.time() - wall_start

    # Extract metrics from the observability tracker
    from observability import metrics_tracker
    recent = metrics_tracker.recent_queries
    last = recent[-1] if recent else None

    input_tokens  = last.input_tokens if last else 0
    output_tokens = last.output_tokens if last else 0
    cost_usd      = last.cost_usd if last else 0.0

    # Print response
    if show_response:
        print(f"\n{result.response}\n")

    # Print metrics summary
    print(f"{BLUE}{'━'*60}{RESET}")
    print(f"{BOLD}METRICS{RESET}")
    print(f"{BLUE}{'━'*60}{RESET}")
    print(f"  Model:         {model}")
    print(f"  Tools used:    {', '.join(result.tools_used) if result.tools_used else 'none'}")
    print(f"  Tool calls:    {len(result.tools_used)}")
    print(f"  Input tokens:  {input_tokens:,}")
    print(f"  Output tokens: {output_tokens:,}")
    print(f"  Total tokens:  {input_tokens + output_tokens:,}")
    print(f"  Cost:          ${cost_usd:.6f}")
    print(f"  Wall time:     {wall_elapsed:.1f}s")
    print(f"  Response len:  {len(result.response):,} chars")
    print(f"{BLUE}{'━'*60}{RESET}")

    return result


async def run_comparison(queries: list[str]):
    """Run multiple queries and compare metrics."""
    await _init_once()
    from observability import metrics_tracker

    results = []
    for q in queries:
        r = await run_query(q, show_response=False)
        last = metrics_tracker.recent_queries[-1] if metrics_tracker.recent_queries else None
        results.append({
            "query": q[:50],
            "tools": len(r.tools_used),
            "input": last.input_tokens if last else 0,
            "output": last.output_tokens if last else 0,
            "cost": last.cost_usd if last else 0,
            "time": last.duration_ms / 1000 if last else 0,
        })

    print(f"\n{BOLD}COMPARISON{RESET}")
    print(f"{'Query':<52} {'Tools':>5} {'Input':>8} {'Output':>8} {'Cost':>10} {'Time':>6}")
    print(f"{'─'*52} {'─'*5} {'─'*8} {'─'*8} {'─'*10} {'─'*6}")
    for r in results:
        print(f"{r['query']:<52} {r['tools']:>5} {r['input']:>8,} {r['output']:>8,} ${r['cost']:>9.6f} {r['time']:>5.1f}s")

    total_cost = sum(r["cost"] for r in results)
    total_input = sum(r["input"] for r in results)
    avg_cost = total_cost / len(results) if results else 0
    print(f"\n  Total cost:    ${total_cost:.6f}")
    print(f"  Avg cost:      ${avg_cost:.6f}")
    print(f"  Avg input:     {total_input // len(results):,} tokens")


async def interactive_repl():
    """Interactive REPL for testing queries."""
    await _init_once()

    print(f"\n{BOLD}TrueValue AI — Interactive Test Console{RESET}")
    print(f"{DIM}Type a query and press Enter. Commands:{RESET}")
    print(f"{DIM}  !bench   — run benchmark suite (5 standard queries){RESET}")
    print(f"{DIM}  !metrics — show session metrics summary{RESET}")
    print(f"{DIM}  !quit    — exit{RESET}")
    print()

    while True:
        try:
            query = input(f"{GREEN}>{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not query:
            continue
        if query in ("!quit", "!exit", "!q"):
            print("Bye!")
            break
        if query == "!bench":
            await run_comparison([
                "Calculate chiller cost for 1500 sqft Empower property",
                "Analyze a 1BR in Dubai Marina for investment",
                "Compare Business Bay vs JVC for a studio",
                "What's the supply pipeline risk in Business Bay?",
                "Find 2BR apartments in Downtown Dubai under 3M",
            ])
            continue
        if query == "!metrics":
            from observability import metrics_tracker
            summary = metrics_tracker.get_summary()
            print(f"\n{BOLD}Session Metrics:{RESET}")
            for k, v in summary.items():
                print(f"  {k}: {v}")
            print()
            continue

        await run_query(query)


async def main():
    args = sys.argv[1:]

    # Flags
    cost_only = "--cost-only" in args
    args = [a for a in args if not a.startswith("--")]

    if args:
        query = " ".join(args)
        await run_query(query, show_response=not cost_only)
    else:
        await interactive_repl()


if __name__ == "__main__":
    asyncio.run(main())
