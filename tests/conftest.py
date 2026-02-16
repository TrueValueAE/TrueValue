"""
Test Fixtures for TrueValue AI
================================
Provides async DB fixtures, cleanup between tests, and shared test utilities.
"""

import os
import sys
import asyncio
import pytest
import pytest_asyncio

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set test environment before imports
os.environ["ENVIRONMENT"] = "test"


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_pool():
    """
    Set up a test database connection.
    Uses DATABASE_URL from environment, or skips if not available.
    """
    from database import init_db, close_db, is_db_available

    db_url = os.getenv("DATABASE_URL", "")
    if not db_url or "user:pass" in db_url:
        pytest.skip("DATABASE_URL not configured for testing")

    await init_db(db_url)
    yield
    # Clean up test data
    if is_db_available():
        from database import _pool
        if _pool:
            async with _pool.acquire() as conn:
                await conn.execute("DELETE FROM digest_preferences WHERE user_id < 0")
                await conn.execute("DELETE FROM referrals WHERE referrer_id < 0 OR referee_id < 0")
                await conn.execute("DELETE FROM saved_properties WHERE user_id < 0")
                await conn.execute("DELETE FROM subscription_events WHERE user_id < 0")
                await conn.execute("DELETE FROM query_logs WHERE user_id < 0")
                await conn.execute("DELETE FROM conversations WHERE user_id < 0")
                await conn.execute("DELETE FROM users WHERE user_id < 0")
    await close_db()


@pytest.fixture
def mock_query_response():
    """Return a mock QueryResponse for testing."""
    from main import QueryResponse
    return QueryResponse(
        response="Test analysis response",
        tools_used=["search_bayut_properties", "analyze_investment"],
        timestamp="2025-01-01T00:00:00",
    )


@pytest.fixture
def sample_property():
    """Return a sample property dict for testing."""
    return {
        "price": 2500000,
        "area_sqft": 1500,
        "annual_rent": 160000,
        "location": "dubai-marina",
        "chiller_provider": "empower",
    }
