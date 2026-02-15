#!/usr/bin/env python3
"""
Comprehensive test suite for conversation memory.

Run: python test_conversation.py
     python test_conversation.py --integration   (includes live API tests)
"""

import sys
import os
import time
import asyncio

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conversation import (
    ConversationStore,
    is_followup,
    contains_location,
    _extract_key_facts,
    _has_property_type,
    _has_price,
)

# =====================================================
# TEST HELPERS
# =====================================================

passed = 0
failed = 0
skipped = 0


def check(description: str, condition: bool):
    global passed, failed
    if condition:
        passed += 1
        print(f"   ✅ {description}")
    else:
        failed += 1
        print(f"   ❌ {description}")


def skip(description: str, reason: str = ""):
    global skipped
    skipped += 1
    print(f"   ⏭️  {description} — skipped{': ' + reason if reason else ''}")


# =====================================================
# A. FOLLOW-UP DETECTION TESTS
# =====================================================

def test_followup_detection():
    print("\n📋 A. Follow-up Detection (11 tests)")

    # FOLLOWUP cases (with active session)
    check('"What about JBR?" + session → FOLLOWUP',
          is_followup("What about JBR?", has_session=True))

    check('"How about Marina?" + session → FOLLOWUP',
          is_followup("How about Marina?", has_session=True))

    check('"Which one is better?" + session → FOLLOWUP',
          is_followup("Which one is better?", has_session=True))

    check('"Compare these two" + session → FOLLOWUP',
          is_followup("Compare these two", has_session=True))

    check('"Is it worth it?" + session → FOLLOWUP',
          is_followup("Is it worth it?", has_session=True))

    check('"Also check the chiller costs" + session → FOLLOWUP',
          is_followup("Also check the chiller costs", has_session=True))

    check('"And the ROI?" + session → FOLLOWUP',
          is_followup("And the ROI?", has_session=True))

    # NO session → always FRESH
    check('"What about JBR?" + NO session → FRESH',
          not is_followup("What about JBR?", has_session=False))

    # FRESH cases (complete requests even with session)
    check('"Find 2BR apartments in Marina under 2M" + session → FRESH',
          not is_followup("Find 2BR apartments in Marina under 2M", has_session=True))

    check('"Analyze Burj Vista Tower 2 in Downtown" + session → FRESH',
          not is_followup("Analyze Burj Vista Tower 2 in Downtown", has_session=True))

    check('"Search studios in JLT under 500K" + session → FRESH',
          not is_followup("Search studios in JLT under 500K", has_session=True))


# =====================================================
# B. SESSION MANAGEMENT TESTS
# =====================================================

def test_session_management():
    print("\n📋 B. Session Management (7 tests)")

    store = ConversationStore()

    # New user has no session
    check("New user → no session",
          not store.has_session("user1"))

    check("New user → get_context returns None",
          store.get_context("user1") is None)

    # After one turn
    store.update("user1", "Analyze Marina Gate Tower 1",
                 "Marina Gate Tower 1 in Dubai Marina. AED 2,500,000. Score: 62/100. GOOD BUY. Empower chiller. 6.4% gross yield.")

    check("After one turn → session exists",
          store.has_session("user1"))

    ctx = store.get_context("user1")
    check("After one turn → summary contains key facts",
          ctx is not None and "Marina" in ctx and "62/100" in ctx)

    # After 3 turns
    store.update("user1", "What about JBR?",
                 "JBR Walk area. AED 1,800,000. Score: 58/100. CAUTIOUS BUY. Higher supply risk.")
    store.update("user1", "Which has better ROI?",
                 "Marina Gate offers 6.4% yield vs JBR at 5.8%. Marina is the better investment.")

    ctx3 = store.get_context("user1")
    check("After 3 turns → summary stays compact (under 500 chars)",
          ctx3 is not None and len(ctx3) <= 500)

    # Reset
    store.reset("user1")
    check("reset() → session cleared",
          not store.has_session("user1"))

    # Fresh request replaces old session
    store.update("user2", "Analyze Downtown", "Downtown area. AED 3M. Score: 70/100.")
    store.update("user2", "Find studios in Arjan under 600K", "Arjan studios. AED 550,000.")
    ctx_replaced = store.get_context("user2")
    check("Fresh request updates session → summary includes both turns",
          ctx_replaced is not None and "Arjan" in ctx_replaced)

    store.shutdown()


# =====================================================
# C. SUMMARY EXTRACTION TESTS
# =====================================================

def test_summary_extraction():
    print("\n📋 C. Summary Extraction (8 tests)")

    check('Score extraction: "Score: 72/100"',
          "72/100" in _extract_key_facts("Investment Score: 72/100 — moderate"))

    check('Price extraction: "AED 2,500,000"',
          "AED 2,500,000" in _extract_key_facts("The price is AED 2,500,000 for this unit"))

    check('GO recommendation extracted',
          "GO" in _extract_key_facts("Final recommendation: GO — strong fundamentals"))

    check('NO-GO recommendation extracted',
          "NO-GO" in _extract_key_facts("Final recommendation: NO-GO — too much risk"))

    check('Empower chiller warning extracted',
          "Empower chiller" in _extract_key_facts("Note: Empower chiller costs are high in this area"))

    check('Location extracted',
          "Marina" in _extract_key_facts("Dubai Marina is a top location for investors"))

    check('Yield extracted',
          "yield" in _extract_key_facts("Expected 6.4% gross yield for this property"))

    # Summary stays compact after many turns
    store = ConversationStore()
    for i in range(5):
        store.update("user_compact", f"Query about area {i}",
                     f"Area {i} in Dubai Marina. AED {i},000,000. Score: {60+i}/100. GOOD BUY.")
    ctx = store.get_context("user_compact")
    check("Summary stays under 500 chars after 5 turns",
          ctx is not None and len(ctx) <= 500)

    store.shutdown()


# =====================================================
# D. SESSION TIMEOUT TESTS
# =====================================================

def test_session_timeout():
    print("\n📋 D. Session Timeout (2 tests)")

    store = ConversationStore()

    # Active session at 29 min
    store.update("user_timeout", "Analyze Marina", "Marina analysis. Score: 70/100.")
    store._sessions["user_timeout"].last_activity = time.time() - (29 * 60)
    check("Session at 29 min → still active",
          store.has_session("user_timeout"))

    # Expired session at 31 min
    store._sessions["user_timeout"].last_activity = time.time() - (31 * 60)
    check("Session at 31 min → expired",
          not store.has_session("user_timeout"))

    store.shutdown()


# =====================================================
# E. HELPER FUNCTION TESTS
# =====================================================

def test_helpers():
    print("\n📋 E. Helper Functions (6 tests)")

    check("contains_location('marina') → True",
          contains_location("marina"))
    check("contains_location('xyz') → False",
          not contains_location("xyz"))
    check("_has_property_type('2BR apartment') → True",
          _has_property_type("2BR apartment"))
    check("_has_property_type('nice place') → False",
          not _has_property_type("nice place"))
    check("_has_price('under 2M') → True",
          _has_price("under 2M"))
    check("_has_price('good area') → False",
          not _has_price("good area"))


# =====================================================
# F. END-TO-END INTEGRATION TESTS (requires API key)
# =====================================================

async def test_integration():
    print("\n📋 F. End-to-End Integration (requires ANTHROPIC_API_KEY)")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        skip("Basic follow-up", "ANTHROPIC_API_KEY not set")
        skip("Multi-turn conversation", "ANTHROPIC_API_KEY not set")
        skip("Fresh request after conversation", "ANTHROPIC_API_KEY not set")
        skip("Reset command", "ANTHROPIC_API_KEY not set")
        skip("Session timeout simulation", "ANTHROPIC_API_KEY not set")
        skip("Metrics recording", "ANTHROPIC_API_KEY not set")
        return

    from main import handle_query
    from observability import followup_detected_total, conversation_resets_total, active_conversations

    store = ConversationStore()
    uid = "integration_test_user"

    # Test 1: Basic follow-up
    print("   🔄 Running integration test 1 (basic follow-up)...")
    try:
        r1 = await handle_query("Analyze Marina Gate Tower 1 in Dubai Marina", user_id=uid)
        resp1 = r1.response if hasattr(r1, 'response') else str(r1)
        store.update(uid, "Analyze Marina Gate Tower 1 in Dubai Marina", resp1)

        ctx = store.get_context(uid) if is_followup("What about JBR?", store.has_session(uid)) else None
        r2 = await handle_query("What about JBR?", user_id=uid, conversation_context=ctx)
        resp2 = r2.response if hasattr(r2, 'response') else str(r2)
        store.update(uid, "What about JBR?", resp2)

        # Response should reference prior context (Marina) or JBR comparison
        has_context = "marina" in resp2.lower() or "jbr" in resp2.lower()
        check("Basic follow-up — response has relevant context", has_context)
    except Exception as e:
        check(f"Basic follow-up — failed: {e}", False)

    # Test 2: Multi-turn
    print("   🔄 Running integration test 2 (multi-turn)...")
    try:
        ctx = store.get_context(uid) if is_followup("Which one has better ROI?", store.has_session(uid)) else None
        r3 = await handle_query("Which one has better ROI?", user_id=uid, conversation_context=ctx)
        resp3 = r3.response if hasattr(r3, 'response') else str(r3)
        store.update(uid, "Which one has better ROI?", resp3)
        check("Multi-turn — response addresses ROI comparison",
              "roi" in resp3.lower() or "yield" in resp3.lower() or "return" in resp3.lower())
    except Exception as e:
        check(f"Multi-turn — failed: {e}", False)

    # Test 3: Fresh request after conversation
    print("   🔄 Running integration test 3 (fresh request)...")
    try:
        fresh_q = "Find studios in Arjan under 600K"
        is_fu = is_followup(fresh_q, store.has_session(uid))
        check("Fresh request classified as fresh", not is_fu)
    except Exception as e:
        check(f"Fresh request detection — failed: {e}", False)

    # Test 4: Reset
    print("   🔄 Running integration test 4 (reset)...")
    try:
        store.reset(uid)
        check("Reset — no session after reset", not store.has_session(uid))
        # Follow-up after reset should be treated as fresh
        check("After reset — follow-up query treated as fresh",
              not is_followup("What about JBR?", store.has_session(uid)))
    except Exception as e:
        check(f"Reset — failed: {e}", False)

    # Test 5: Timeout simulation
    print("   🔄 Running integration test 5 (timeout)...")
    try:
        store.update(uid, "test query", "test response with Score: 50/100")
        store._sessions[uid].last_activity = time.time() - (31 * 60)
        check("Timeout — session expired after 31 min", not store.has_session(uid))
    except Exception as e:
        check(f"Timeout — failed: {e}", False)

    store.shutdown()


# =====================================================
# MAIN
# =====================================================

def main():
    print("=" * 60)
    print("🧪 CONVERSATION MEMORY — COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    test_followup_detection()
    test_session_management()
    test_summary_extraction()
    test_session_timeout()
    test_helpers()

    run_integration = "--integration" in sys.argv
    if run_integration:
        asyncio.run(test_integration())
    else:
        print("\n📋 F. End-to-End Integration")
        print("   ⏭️  Skipped (run with --integration flag)")

    print("\n" + "=" * 60)
    total = passed + failed
    print(f"🎯 Result: {passed}/{total} tests passed", end="")
    if skipped:
        print(f" ({skipped} skipped)", end="")
    print()
    if failed:
        print(f"   ❌ {failed} test(s) FAILED")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
