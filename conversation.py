"""
Conversation memory for Dubai Estate AI Bot.

Maintains per-user conversation sessions with compressed summaries
and lightweight follow-up detection. Only follow-up messages get
context injected (~200-400 extra tokens), keeping costs minimal.
"""

import re
import time
import threading
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# =====================================================
# DUBAI LOCATIONS (for fresh-request detection)
# =====================================================

DUBAI_LOCATIONS = {
    "marina", "jbr", "downtown", "business bay", "jlt", "arjan",
    "dubailand", "silicon oasis", "sports city", "motor city",
    "discovery gardens", "al furjan", "jumeirah", "palm",
    "creek harbour", "sobha hartland", "meydan", "dubai hills",
    "arabian ranches", "damac hills", "town square", "remraam",
    "international city", "al quoz", "barsha", "tecom",
    "greens", "views", "springs", "meadows", "lakes",
    "difc", "world trade centre", "zabeel", "ras al khor",
    "production city", "studio city", "mudon", "villanova",
    "tilal al ghaf", "emaar beachfront", "bluewaters",
    "city walk", "la mer", "dubai south", "expo city",
}

# =====================================================
# FOLLOW-UP DETECTION
# =====================================================

FOLLOWUP_PATTERNS = [
    # Starts with follow-up phrases
    r'^(what about|how about|and |also |instead |compare|which one|what if)',
    # Pronouns referring to prior context
    r'\b(it|that|this|these|those|the same|the other)\b',
    # Comparative/continuation words
    r'\b(better|worse|cheaper|more expensive|similar|alternatively|vs|versus)\b',
]


def contains_location(msg: str) -> bool:
    """Check if message contains a known Dubai location."""
    msg_lower = msg.lower()
    for loc in DUBAI_LOCATIONS:
        if loc in msg_lower:
            return True
    return False


def _has_property_type(msg: str) -> bool:
    """Check if message contains a property type keyword."""
    property_types = r'\b(studio|1br|2br|3br|4br|5br|1bed|2bed|3bed|4bed|5bed|apartment|villa|townhouse|penthouse|duplex)\b'
    return bool(re.search(property_types, msg.lower()))


def _has_price(msg: str) -> bool:
    """Check if message contains a price indicator."""
    return bool(re.search(r'\b(aed|under|below|above|over|budget)\b|\d{3,}k|\d[\d,]*\.\d+m|\d{6,}', msg.lower()))


def is_followup(message: str, has_session: bool) -> bool:
    """
    Detect if a message is a follow-up to prior conversation.

    Returns False if no prior session exists (nothing to follow up on).
    Uses heuristics: follow-up phrases, pronouns, comparatives, and
    message length/completeness.
    """
    if not has_session:
        return False

    msg_lower = message.lower().strip()

    # A complete fresh request has location + (property type or price)
    has_loc = contains_location(msg_lower)
    has_type = _has_property_type(msg_lower)
    has_price = _has_price(msg_lower)
    if has_loc and (has_type or has_price):
        return False

    # Explicit analysis of a new named property/tower
    if re.match(r'^(analyze|search|find|look up)\b', msg_lower) and has_loc:
        return False

    # Check follow-up signal patterns
    for pattern in FOLLOWUP_PATTERNS:
        if re.search(pattern, msg_lower):
            return True

    # Short messages without a clear location are likely follow-ups
    if len(msg_lower) < 40 and not has_loc:
        return True

    return False


# =====================================================
# SUMMARY EXTRACTION
# =====================================================

def _extract_key_facts(response: str) -> str:
    """Extract key investment facts from a response into a compact string."""
    facts = []

    # Location
    for loc in DUBAI_LOCATIONS:
        if loc.lower() in response.lower():
            facts.append(loc.title())
            break

    # Price (AED X,XXX,XXX or AED X.XM)
    price_match = re.search(r'AED\s*[\d,]+(?:\.\d+)?(?:\s*[MmKk])?', response)
    if price_match:
        facts.append(price_match.group(0).strip())

    # Investment score
    score_match = re.search(r'Score[:\s]*(\d+)/100', response, re.IGNORECASE)
    if score_match:
        facts.append(f"Score: {score_match.group(1)}/100")

    # GO / NO-GO recommendation
    if re.search(r'\bNO[- ]?GO\b', response, re.IGNORECASE):
        facts.append("NO-GO")
    elif re.search(r'\bGO\b', response):
        facts.append("GO")

    # GOOD BUY / CAUTIOUS BUY etc.
    buy_match = re.search(r'(GOOD|CAUTIOUS|STRONG|WEAK|EXCELLENT)\s+BUY', response, re.IGNORECASE)
    if buy_match:
        facts.append(buy_match.group(0).upper())

    # Chiller warning
    if re.search(r'(empower|chiller)', response, re.IGNORECASE):
        facts.append("Empower chiller")

    # Yield
    yield_match = re.search(r'(\d+\.?\d*)\s*%\s*(gross|net)?\s*yield', response, re.IGNORECASE)
    if yield_match:
        yield_str = f"{yield_match.group(1)}%"
        if yield_match.group(2):
            yield_str += f" {yield_match.group(2)}"
        facts.append(f"{yield_str} yield")

    # Oversupply warning
    if re.search(r'oversuppl', response, re.IGNORECASE):
        facts.append("oversupply risk")

    result = ", ".join(facts) if facts else response[:150].replace("\n", " ")
    return result[:250]


# =====================================================
# SESSION DATA
# =====================================================

@dataclass
class ConversationSession:
    summary: str = ""
    last_query: str = ""
    last_response_snippet: str = ""
    turn_count: int = 0
    last_activity: float = field(default_factory=time.time)


# =====================================================
# CONVERSATION STORE
# =====================================================

SESSION_TIMEOUT_SECONDS = 30 * 60  # 30 minutes
CLEANUP_INTERVAL_SECONDS = 5 * 60  # 5 minutes


class ConversationStore:
    """In-memory per-user conversation session store."""

    def __init__(self):
        self._sessions: dict[str, ConversationSession] = {}
        self._lock = threading.Lock()
        self._cleanup_timer: threading.Timer | None = None
        self._start_cleanup_loop()

    # ------ public API ------

    def has_session(self, user_id: str) -> bool:
        """Check if user has an active (non-expired) session."""
        with self._lock:
            session = self._sessions.get(user_id)
            if session is None:
                return False
            if time.time() - session.last_activity > SESSION_TIMEOUT_SECONDS:
                del self._sessions[user_id]
                return False
            return True

    def get_context(self, user_id: str) -> str | None:
        """Return the conversation summary for injection, or None."""
        with self._lock:
            session = self._sessions.get(user_id)
            if session is None:
                return None
            if time.time() - session.last_activity > SESSION_TIMEOUT_SECONDS:
                del self._sessions[user_id]
                return None
            return session.summary or None

    def update(self, user_id: str, query: str, response: str) -> None:
        """Update (or create) a session after a completed turn."""
        key_facts = _extract_key_facts(response)

        with self._lock:
            session = self._sessions.get(user_id)
            if session is None:
                session = ConversationSession()
                self._sessions[user_id] = session

            # Build / extend summary
            if session.summary:
                new_summary = f"{session.summary} | Then: {query[:80]} → {key_facts}"
            else:
                new_summary = f"Prior: {query[:80]} → {key_facts}"

            # Keep summary compact (max ~500 chars)
            if len(new_summary) > 500:
                # Trim oldest context, keep most recent turns
                parts = new_summary.split(" | ")
                while len(" | ".join(parts)) > 500 and len(parts) > 1:
                    parts.pop(0)
                new_summary = " | ".join(parts)

            session.summary = new_summary
            session.last_query = query
            session.last_response_snippet = response[:300]
            session.turn_count += 1
            session.last_activity = time.time()

    def reset(self, user_id: str) -> None:
        """Clear a user's conversation session."""
        with self._lock:
            self._sessions.pop(user_id, None)

    def active_session_count(self) -> int:
        """Return count of active sessions (for metrics)."""
        now = time.time()
        with self._lock:
            return sum(
                1 for s in self._sessions.values()
                if now - s.last_activity <= SESSION_TIMEOUT_SECONDS
            )

    # ------ cleanup ------

    def _start_cleanup_loop(self):
        """Schedule periodic cleanup of expired sessions."""
        self._cleanup_timer = threading.Timer(CLEANUP_INTERVAL_SECONDS, self._cleanup)
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()

    def _cleanup(self):
        """Remove expired sessions."""
        now = time.time()
        removed = 0
        with self._lock:
            expired = [
                uid for uid, s in self._sessions.items()
                if now - s.last_activity > SESSION_TIMEOUT_SECONDS
            ]
            for uid in expired:
                del self._sessions[uid]
                removed += 1

        if removed:
            logger.debug(f"Cleaned up {removed} expired conversation sessions")

        # Reschedule
        self._start_cleanup_loop()

    def shutdown(self):
        """Cancel the cleanup timer."""
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
