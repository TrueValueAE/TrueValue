"""
Tests for web_search_dubai tool.

Unit tests (no API key needed):
    python test_web_search.py

Integration tests (needs BRAVE_API_KEY):
    BRAVE_API_KEY=xxx python test_web_search.py --integration
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import patch, AsyncMock, MagicMock

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import web_search_dubai


class TestWebSearchDubaiUnit(unittest.TestCase):
    """Unit tests that run without an API key."""

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    # ---- Missing / invalid API key ----

    @patch.dict(os.environ, {"BRAVE_API_KEY": ""}, clear=False)
    def test_missing_api_key_returns_unavailable(self):
        result = self._run(web_search_dubai("Marina Gate reviews"))
        self.assertFalse(result["success"])
        self.assertEqual(result["source"], "web_search_unavailable")
        self.assertIn("BRAVE_API_KEY", result["error"])

    @patch.dict(os.environ, {"BRAVE_API_KEY": "demo"}, clear=False)
    def test_demo_api_key_returns_unavailable(self):
        result = self._run(web_search_dubai("Marina Gate reviews"))
        self.assertFalse(result["success"])
        self.assertEqual(result["source"], "web_search_unavailable")

    @patch.dict(os.environ, {"BRAVE_API_KEY": "your_brave_key_here"}, clear=False)
    def test_placeholder_api_key_returns_unavailable(self):
        result = self._run(web_search_dubai("test"))
        self.assertFalse(result["success"])
        self.assertEqual(result["source"], "web_search_unavailable")

    # ---- Query auto-context ----

    @patch.dict(os.environ, {"BRAVE_API_KEY": "real_key_123"}, clear=False)
    @patch("main.httpx.AsyncClient")
    def test_query_without_dubai_appends_context(self, mock_client_cls):
        """Query without 'dubai' should have 'Dubai real estate' appended."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"web": {"results": []}}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = self._run(web_search_dubai("Marina Gate Tower 1 reviews"))
        self.assertTrue(result["success"])
        self.assertIn("Dubai real estate", result["query"])

    @patch.dict(os.environ, {"BRAVE_API_KEY": "real_key_123"}, clear=False)
    @patch("main.httpx.AsyncClient")
    def test_query_with_dubai_no_double_append(self, mock_client_cls):
        """Query already containing 'dubai' should NOT get extra context."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"web": {"results": []}}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = self._run(web_search_dubai("Dubai Marina prices 2024"))
        self.assertTrue(result["success"])
        self.assertEqual(result["query"], "Dubai Marina prices 2024")

    # ---- Successful response parsing ----

    @patch.dict(os.environ, {"BRAVE_API_KEY": "real_key_123"}, clear=False)
    @patch("main.httpx.AsyncClient")
    def test_successful_response_parses_results(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "web": {
                "results": [
                    {
                        "title": "Marina Gate Tower 1 Review",
                        "url": "https://example.com/review",
                        "description": "Detailed review of Marina Gate.",
                        "age": "3 days ago",
                    },
                    {
                        "title": "Dubai Marina Prices 2024",
                        "url": "https://example.com/prices",
                        "description": "Price trends in Dubai Marina.",
                        "age": "1 week ago",
                    },
                ]
            }
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = self._run(web_search_dubai("Marina Gate", num_results=5))
        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "brave_web_search")
        self.assertEqual(result["total_results"], 2)
        self.assertEqual(result["results"][0]["title"], "Marina Gate Tower 1 Review")
        self.assertEqual(result["results"][1]["url"], "https://example.com/prices")

    # ---- Error handling ----

    @patch.dict(os.environ, {"BRAVE_API_KEY": "real_key_123"}, clear=False)
    @patch("main.httpx.AsyncClient")
    def test_rate_limit_returns_error(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.status_code = 429

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = self._run(web_search_dubai("test query"))
        self.assertFalse(result["success"])
        self.assertIn("Rate limited", result["error"])

    @patch.dict(os.environ, {"BRAVE_API_KEY": "real_key_123"}, clear=False)
    @patch("main.httpx.AsyncClient")
    def test_timeout_returns_error(self, mock_client_cls):
        import httpx

        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.TimeoutException("timed out")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = self._run(web_search_dubai("test query"))
        self.assertFalse(result["success"])
        self.assertIn("timed out", result["error"])

    @patch.dict(os.environ, {"BRAVE_API_KEY": "real_key_123"}, clear=False)
    @patch("main.httpx.AsyncClient")
    def test_api_error_status_returns_error(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = self._run(web_search_dubai("test query"))
        self.assertFalse(result["success"])
        self.assertIn("500", result["error"])

    # ---- num_results clamping ----

    @patch.dict(os.environ, {"BRAVE_API_KEY": "real_key_123"}, clear=False)
    @patch("main.httpx.AsyncClient")
    def test_num_results_clamped_to_10(self, mock_client_cls):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"web": {"results": []}}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        self._run(web_search_dubai("test", num_results=20))

        # Verify the count param was clamped to 10
        call_kwargs = mock_client.get.call_args
        self.assertEqual(call_kwargs.kwargs["params"]["count"], 10)


class TestWebSearchDubaiIntegration(unittest.TestCase):
    """Integration tests that require a real BRAVE_API_KEY."""

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def setUp(self):
        self.api_key = os.getenv("BRAVE_API_KEY", "")
        if not self.api_key or self.api_key in ("demo", "your_brave_key_here", ""):
            self.skipTest("BRAVE_API_KEY not set — skipping integration tests")

    def test_live_search_returns_results(self):
        result = self._run(web_search_dubai("Marina Gate Tower 1 reviews snagging", num_results=3))
        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "brave_web_search")
        self.assertGreater(result["total_results"], 0)
        # Each result should have title and url
        for r in result["results"]:
            self.assertIn("title", r)
            self.assertIn("url", r)

    def test_live_search_market_query(self):
        result = self._run(web_search_dubai("Business Bay oversupply 2026", num_results=3))
        self.assertTrue(result["success"])
        self.assertGreater(result["total_results"], 0)


if __name__ == "__main__":
    if "--integration" in sys.argv:
        sys.argv.remove("--integration")
        suite = unittest.TestLoader().loadTestsFromTestCase(TestWebSearchDubaiIntegration)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestWebSearchDubaiUnit)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
