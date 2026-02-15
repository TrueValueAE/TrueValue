#!/usr/bin/env python3
"""
TrueValue AI — Cost Simulation
================================
Simulates 20 realistic conversations (with follow-ups)
and reports total/average cost, token usage, and tool efficiency.
"""

import asyncio
import sys
import os
import time

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

# 20 conversations — mix of single-turn, 2-turn follow-ups, and 3-turn deep dives
CONVERSATIONS = [
    # --- Single-turn quick queries ---
    {
        "name": "1. Chiller Cost Quick",
        "turns": [
            "Calculate chiller cost for a 1200 sqft apartment with Empower",
        ],
    },
    {
        "name": "2. Supply Pipeline BB",
        "turns": [
            "What's the supply pipeline risk in Business Bay?",
        ],
    },
    {
        "name": "3. Palm Jumeirah Market",
        "turns": [
            "What are current market trends for Palm Jumeirah sales?",
        ],
    },
    # --- Single-turn analysis queries ---
    {
        "name": "4. Marina 1BR Analysis",
        "turns": [
            "Analyze a 1BR in Dubai Marina for investment",
        ],
    },
    {
        "name": "5. Downtown Investment Score",
        "turns": [
            "Score a Downtown Dubai 1BR: price 2.2M, area 900 sqft, rent 130K, Empower",
        ],
    },
    {
        "name": "6. BB vs Downtown Compare",
        "turns": [
            "Compare Business Bay vs Downtown Dubai for a 2BR investment",
        ],
    },
    # --- 2-turn follow-up conversations ---
    {
        "name": "7. JVC Studio + Chiller",
        "turns": [
            "Find studio apartments in JVC under 500K",
            "What's the chiller situation there? Is it Empower or Lootah?",
        ],
    },
    {
        "name": "8. JBR Search + Snagging",
        "turns": [
            "Find 2BR apartments in JBR under 3.5M",
            "What building issues should I watch for in Sadaf tower?",
        ],
    },
    {
        "name": "9. Marina Gate Issues + Yield",
        "turns": [
            "Any snagging or building issues reported for Marina Gate Tower 1?",
            "What's the net yield after chiller costs for a 1500 sqft unit there renting at 160K?",
        ],
    },
    {
        "name": "10. Downtown Search + Compare",
        "turns": [
            "Show me 1BR apartments in Downtown Dubai under 2M",
            "Compare the best option to a similar one in Business Bay",
        ],
    },
    # --- More single-turn diverse queries ---
    {
        "name": "11. JVC Oversupply Risk",
        "turns": [
            "Is JVC a good investment? I keep hearing about oversupply",
        ],
    },
    {
        "name": "12. Empower vs Lootah",
        "turns": [
            "Explain the difference between Empower and Lootah chiller costs for a 1000 sqft apartment",
        ],
    },
    {
        "name": "13. Executive Towers BB",
        "turns": [
            "Analyze Executive Towers Business Bay 2BR: price 1.8M, area 1200 sqft, rent 110K",
        ],
    },
    # --- 2-turn conversations ---
    {
        "name": "14. Arjan Budget + Follow-up",
        "turns": [
            "What are good budget investment options in Arjan under 700K?",
            "How does the yield compare to JVC?",
        ],
    },
    {
        "name": "15. Dubai South Inquiry",
        "turns": [
            "Is Dubai South worth investing in right now?",
            "What about for a 5-year hold with Al Maktoum airport expansion?",
        ],
    },
    # --- 3-turn deep dive conversations ---
    {
        "name": "16. Marina Deep Dive",
        "turns": [
            "Search for 2BR apartments in Dubai Marina between 2M and 3M",
            "Run a full investment analysis on the best option",
            "What are the red flags I should worry about?",
        ],
    },
    {
        "name": "17. First-Time Buyer Journey",
        "turns": [
            "I have 1.5M AED budget, which zone gives best rental yield?",
            "Show me specific properties in that zone",
            "Analyze the best one for me — I want to rent it out",
        ],
    },
    # --- More single-turn queries ---
    {
        "name": "18. Title Deed Check",
        "turns": [
            "Verify title deed number TD-2024-DM-00457",
        ],
    },
    {
        "name": "19. Full Report Cayan",
        "turns": [
            "Full analysis of a 2BR in Cayan Tower Dubai Marina: price 2.6M, area 1650 sqft, rent 145K",
        ],
    },
    # --- Final multi-turn ---
    {
        "name": "20. Investor Portfolio Q",
        "turns": [
            "I want to build a 3-property portfolio under 5M total. Which zones?",
            "Compare a JVC studio, a Business Bay 1BR, and a Marina 1BR",
        ],
    },
]


async def run_simulation():
    from database import init_db
    from cache import init_cache
    await init_db()
    await init_cache()

    from main import handle_query
    from observability import metrics_tracker

    num_convs = len(CONVERSATIONS)
    total_turns = sum(len(c["turns"]) for c in CONVERSATIONS)

    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}  TrueValue AI — {num_convs}-Conversation Cost Simulation{RESET}")
    print(f"{BOLD}{'='*70}{RESET}")
    print(f"{DIM}  Model: claude-haiku-4-5-20251001 + prompt caching{RESET}")
    print(f"{DIM}  Pricing: $1/M input, $5/M output{RESET}")
    print(f"{DIM}  Conversations: {num_convs} | Total turns: {total_turns}{RESET}\n")

    all_results = []
    conv_num = 0

    for conv in CONVERSATIONS:
        conv_num += 1
        conv_name = conv["name"]
        turns = conv["turns"]

        print(f"{BLUE}{'─'*70}{RESET}")
        print(f"{BOLD}[{conv_num}/{num_convs}] {conv_name}{RESET} ({len(turns)} turn{'s' if len(turns)>1 else ''})")

        conv_input = 0
        conv_output = 0
        conv_cost = 0.0
        conv_tools = []
        conv_start = time.time()

        # Build up context across turns in this conversation
        context_summary = None

        for i, query in enumerate(turns):
            turn_label = f"  T{i+1}"
            print(f"{turn_label}: {query[:65]}{'...' if len(query)>65 else ''}")

            # Track metrics before this query
            pre_count = len(metrics_tracker.recent_queries)

            try:
                result = await handle_query(
                    query=query,
                    user_id=f"sim_user_{conv_num}",
                    conversation_context=context_summary,
                )

                # Get metrics for this turn
                post_count = len(metrics_tracker.recent_queries)
                if post_count > pre_count:
                    last = metrics_tracker.recent_queries[-1]
                    turn_input = last.input_tokens
                    turn_output = last.output_tokens
                    turn_cost = last.cost_usd
                else:
                    turn_input = turn_output = 0
                    turn_cost = 0.0

                conv_input += turn_input
                conv_output += turn_output
                conv_cost += turn_cost
                conv_tools.extend(result.tools_used)

                # Build context for follow-up turns
                context_summary = result.response[:200]

                tool_str = ', '.join(set(result.tools_used)) if result.tools_used else 'none'
                print(f"      {DIM}{turn_input:,} in / {turn_output:,} out / ${turn_cost:.4f} / [{len(result.tools_used)} tools: {tool_str}]{RESET}")

            except Exception as e:
                print(f"      {RED}ERROR: {e}{RESET}")
                context_summary = None

        conv_elapsed = time.time() - conv_start

        all_results.append({
            "name": conv_name,
            "turns": len(turns),
            "input_tokens": conv_input,
            "output_tokens": conv_output,
            "cost": conv_cost,
            "tools": len(conv_tools),
            "tool_names": conv_tools,
            "time": conv_elapsed,
        })

        print(f"  {GREEN}→ {conv_input:,} in / {conv_output:,} out / ${conv_cost:.4f} / {conv_elapsed:.1f}s{RESET}")

    # ─── FINAL REPORT ───
    print(f"\n\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}  FINAL RESULTS — {num_convs} Conversations, {total_turns} Turns{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")

    # Per-conversation table
    print(f"{'#':<3} {'Conversation':<33} {'Trn':>3} {'Input':>8} {'Output':>7} {'Cost':>9} {'Tls':>3} {'Time':>6}")
    print(f"{'─'*3} {'─'*33} {'─'*3} {'─'*8} {'─'*7} {'─'*9} {'─'*3} {'─'*6}")

    for i, r in enumerate(all_results):
        short_name = r['name'][r['name'].index('.')+2:] if '.' in r['name'] else r['name']
        print(f"{i+1:<3} {short_name:<33} {r['turns']:>3} {r['input_tokens']:>8,} {r['output_tokens']:>7,} ${r['cost']:>8.4f} {r['tools']:>3} {r['time']:>5.1f}s")

    # Totals
    total_input    = sum(r["input_tokens"] for r in all_results)
    total_output   = sum(r["output_tokens"] for r in all_results)
    total_cost     = sum(r["cost"] for r in all_results)
    total_tools    = sum(r["tools"] for r in all_results)
    total_time     = sum(r["time"] for r in all_results)
    total_turns_actual = sum(r["turns"] for r in all_results)
    num_convs_actual = len(all_results)

    print(f"{'─'*3} {'─'*33} {'─'*3} {'─'*8} {'─'*7} {'─'*9} {'─'*3} {'─'*6}")
    print(f"{'':3} {'TOTAL':<33} {total_turns_actual:>3} {total_input:>8,} {total_output:>7,} ${total_cost:>8.4f} {total_tools:>3} {total_time:>5.1f}s")

    # Summary stats
    print(f"\n{BOLD}{'─'*40}{RESET}")
    print(f"{BOLD}SUMMARY{RESET}")
    print(f"{BOLD}{'─'*40}{RESET}")
    print(f"  Conversations:       {num_convs_actual}")
    print(f"  Total turns:         {total_turns_actual}")
    print(f"  Total input tokens:  {total_input:,}")
    print(f"  Total output tokens: {total_output:,}")
    print(f"  Total cost:          ${total_cost:.4f}")
    print()
    print(f"  Avg cost/conversation: ${total_cost / num_convs_actual:.4f}")
    print(f"  Avg cost/turn:         ${total_cost / total_turns_actual:.4f}")
    print(f"  Avg input/turn:        {total_input // total_turns_actual:,} tokens")
    print(f"  Avg output/turn:       {total_output // total_turns_actual:,} tokens")
    print(f"  Avg tools/turn:        {total_tools / total_turns_actual:.1f}")
    print(f"  Total wall time:       {total_time:.0f}s ({total_time/60:.1f}min)")

    # Cost breakdown by query type
    single_turn = [r for r in all_results if r["turns"] == 1]
    multi_turn  = [r for r in all_results if r["turns"] > 1]

    if single_turn:
        st_cost = sum(r["cost"] for r in single_turn)
        st_count = len(single_turn)
        print(f"\n  Single-turn queries ({st_count}):  avg ${st_cost/st_count:.4f}/conv")
    if multi_turn:
        mt_cost = sum(r["cost"] for r in multi_turn)
        mt_turns = sum(r["turns"] for r in multi_turn)
        mt_count = len(multi_turn)
        print(f"  Multi-turn convos ({mt_count}):    avg ${mt_cost/mt_count:.4f}/conv  (avg ${mt_cost/mt_turns:.4f}/turn)")

    # Projections
    print(f"\n{BOLD}{'─'*40}{RESET}")
    print(f"{BOLD}COST PROJECTIONS{RESET}")
    print(f"{BOLD}{'─'*40}{RESET}")
    cost_per_query = total_cost / total_turns_actual
    print(f"  Per query:           ${cost_per_query:.4f}")
    print()
    print(f"  {'Volume':<22} {'Daily':>10} {'Monthly':>12}")
    print(f"  {'─'*22} {'─'*10} {'─'*12}")
    for vol in [50, 100, 250, 500, 1000]:
        daily = cost_per_query * vol
        monthly = daily * 30
        print(f"  {vol:>5} queries/day       ${daily:>8.2f}   ${monthly:>10.2f}")

    # Original cost comparison
    original_cost_per_query = 0.23  # Sonnet 4, no optimizations
    print(f"\n  vs. Original (Sonnet 4, $0.23/query):")
    print(f"  {'Volume':<22} {'Original':>10} {'Now':>10} {'Savings':>10}")
    print(f"  {'─'*22} {'─'*10} {'─'*10} {'─'*10}")
    for vol in [100, 500, 1000]:
        orig_daily = original_cost_per_query * vol
        new_daily = cost_per_query * vol
        savings_pct = (1 - new_daily / orig_daily) * 100
        print(f"  {vol:>5} queries/day       ${orig_daily:>8.2f}   ${new_daily:>8.2f}   {savings_pct:>8.1f}%")

    # Tool usage breakdown
    from collections import Counter
    all_tool_names = []
    for r in all_results:
        all_tool_names.extend(r["tool_names"])
    tool_counts = Counter(all_tool_names)

    print(f"\n{BOLD}{'─'*40}{RESET}")
    print(f"{BOLD}TOOL USAGE{RESET}")
    print(f"{BOLD}{'─'*40}{RESET}")
    for tool, count in tool_counts.most_common():
        bar = '█' * (count // 2) + '▌' * (count % 2)
        print(f"  {tool:<30} {count:>3}x  {bar}")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(run_simulation())
