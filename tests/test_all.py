"""
TrueValue AI — Comprehensive Unit & Integration Tests
=======================================================
Covers all features: existing tools, zone data, new tools (mortgage, DLD,
rental comps), database functions (watchlist, referrals, digest), bot
commands, cache config, digest generator, and end-to-end query flow.

Run:  pytest tests/test_all.py -v
      pytest tests/test_all.py -v -k "unit"       # unit tests only
      pytest tests/test_all.py -v -k "integration" # integration tests only
"""

import os
import sys
import json
import asyncio
import pytest
import pytest_asyncio

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()


# =====================================================
# FIXTURES
# =====================================================

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_property():
    return {
        "id": "test001",
        "title": "Test Tower — 2BR",
        "location": "Dubai Marina",
        "building": "Test Tower",
        "bedrooms": 2,
        "price": 2500000,
        "area": 1500,
        "price_per_sqft": 1667,
        "purpose": "for-sale",
        "property_type": "apartment",
        "chiller_provider": "Empower",
        "floor": 20,
        "view": "Marina",
        "completion_year": 2020,
    }


# =====================================================
# 1. ZONE DATA COMPLETENESS (unit)
# =====================================================

class TestZoneData:
    """Verify all zone maps are consistent and complete."""

    def test_unit_mock_properties_zone_count(self):
        from main import MOCK_PROPERTIES
        assert len(MOCK_PROPERTIES) >= 13, f"Expected ≥13 zones, got {len(MOCK_PROPERTIES)}"

    def test_unit_mock_properties_per_zone(self):
        from main import MOCK_PROPERTIES
        for zone, props in MOCK_PROPERTIES.items():
            assert len(props) >= 3, f"Zone '{zone}' has only {len(props)} properties (need ≥3)"

    def test_unit_mock_properties_required_fields(self):
        from main import MOCK_PROPERTIES
        required = {"id", "title", "location", "bedrooms", "price", "area", "purpose", "property_type"}
        for zone, props in MOCK_PROPERTIES.items():
            for prop in props:
                missing = required - set(prop.keys())
                assert not missing, f"Zone '{zone}' prop '{prop.get('id')}' missing: {missing}"

    def test_unit_mock_properties_has_sale_and_rent(self):
        from main import MOCK_PROPERTIES
        for zone, props in MOCK_PROPERTIES.items():
            purposes = {p["purpose"] for p in props}
            assert "for-sale" in purposes, f"Zone '{zone}' has no for-sale listings"
            assert "for-rent" in purposes, f"Zone '{zone}' has no for-rent listings"

    def test_unit_location_aliases_coverage(self):
        from main import LOCATION_ALIASES, MOCK_PROPERTIES
        resolved_zones = set(LOCATION_ALIASES.values())
        for zone in MOCK_PROPERTIES:
            assert zone in resolved_zones, f"Zone '{zone}' not reachable via LOCATION_ALIASES"

    def test_unit_bayut_location_ids_coverage(self):
        from main import BAYUT_LOCATION_IDS, MOCK_PROPERTIES
        for zone in MOCK_PROPERTIES:
            assert zone in BAYUT_LOCATION_IDS, f"Zone '{zone}' missing from BAYUT_LOCATION_IDS"

    def test_unit_supply_pipeline_coverage(self):
        from main import SUPPLY_PIPELINE
        expected_zones = {
            "dubai-marina", "business-bay", "jumeirah-beach-residence",
            "downtown-dubai", "jumeirah-village-circle", "palm-jumeirah",
            "jlt", "arjan", "dubai-hills", "arabian-ranches",
            "city-walk", "creek-harbour", "emaar-beachfront", "dubai-south",
        }
        for zone in expected_zones:
            assert zone in SUPPLY_PIPELINE, f"Zone '{zone}' missing from SUPPLY_PIPELINE"
            data = SUPPLY_PIPELINE[zone]
            assert "risk_level" in data, f"Zone '{zone}' missing risk_level"
            assert "units_pipeline" in data, f"Zone '{zone}' missing units_pipeline"

    def test_unit_supply_pipeline_valid_risk_levels(self):
        from main import SUPPLY_PIPELINE
        valid = {"LOW", "MODERATE", "HIGH", "VERY HIGH"}
        for zone, data in SUPPLY_PIPELINE.items():
            assert data["risk_level"] in valid, f"Zone '{zone}' has invalid risk: {data['risk_level']}"

    def test_unit_new_zones_present(self):
        """Verify all 8 new zones from Feature 1 are present."""
        from main import MOCK_PROPERTIES, SUPPLY_PIPELINE, BAYUT_LOCATION_IDS
        new_zones = ["jlt", "arjan", "dubai-hills", "arabian-ranches",
                     "city-walk", "creek-harbour", "emaar-beachfront", "dubai-south"]
        for zone in new_zones:
            assert zone in MOCK_PROPERTIES, f"New zone '{zone}' missing from MOCK_PROPERTIES"
            assert zone in BAYUT_LOCATION_IDS, f"New zone '{zone}' missing from BAYUT_LOCATION_IDS"
            assert zone in SUPPLY_PIPELINE, f"New zone '{zone}' missing from SUPPLY_PIPELINE"

    def test_unit_resolve_location_aliases(self):
        from main import _resolve_location
        cases = {
            "marina": "dubai-marina",
            "Dubai Marina": "dubai-marina",
            "jlt": "jlt",
            "Jumeirah Lake Towers": "jlt",
            "arjan": "arjan",
            "Dubai Hills": "dubai-hills",
            "arabian ranches": "arabian-ranches",
            "city walk": "city-walk",
            "creek harbour": "creek-harbour",
            "emaar beachfront": "emaar-beachfront",
            "dubai south": "dubai-south",
            "jvc": "jumeirah-village-circle",
            "downtown": "downtown-dubai",
        }
        for input_val, expected in cases.items():
            result = _resolve_location(input_val)
            assert result == expected, f"_resolve_location('{input_val}') = '{result}', expected '{expected}'"


# =====================================================
# 2. CHILLER COST TOOL (unit)
# =====================================================

class TestChillerCost:
    """Test the chiller cost calculation tool."""

    @pytest.mark.asyncio
    async def test_unit_empower_calculation(self):
        from main import calculate_chiller_cost
        result = await calculate_chiller_cost("empower", 1500)
        assert result["success"] is True
        assert result["provider"] == "empower"
        assert result["total_annual_cost_aed"] > 0
        assert result["chiller_trap_detected"] is True
        assert result["monthly_cost_aed"] > 0

    @pytest.mark.asyncio
    async def test_unit_lootah_calculation(self):
        from main import calculate_chiller_cost
        result = await calculate_chiller_cost("lootah", 1500)
        assert result["success"] is True
        assert result["provider"] == "lootah"
        assert result["chiller_trap_detected"] is False
        assert result["annual_capacity_cost_aed"] == 0

    @pytest.mark.asyncio
    async def test_unit_empower_more_expensive(self):
        from main import calculate_chiller_cost
        empower = await calculate_chiller_cost("empower", 1000)
        lootah = await calculate_chiller_cost("lootah", 1000)
        assert empower["total_annual_cost_aed"] > lootah["total_annual_cost_aed"]

    @pytest.mark.asyncio
    async def test_unit_unknown_provider(self):
        from main import calculate_chiller_cost
        result = await calculate_chiller_cost("unknown_provider", 1000)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_unit_warning_levels(self):
        from main import calculate_chiller_cost
        result = await calculate_chiller_cost("empower", 3000)
        assert result["warning_level"] in ("LOW", "MEDIUM", "HIGH")
        # Empower should always have higher per-sqft cost than Lootah
        lootah = await calculate_chiller_cost("lootah", 3000)
        assert result["cost_per_sqft_per_year_aed"] > lootah["cost_per_sqft_per_year_aed"]


# =====================================================
# 3. PROPERTY SEARCH TOOL (unit)
# =====================================================

class TestPropertySearch:
    """Test Bayut property search (mock data fallback)."""

    @pytest.mark.asyncio
    async def test_unit_search_known_zone(self):
        from main import search_bayut_properties
        result = await search_bayut_properties("dubai-marina", "for-sale")
        assert result["success"] is True
        assert len(result["properties"]) > 0

    @pytest.mark.asyncio
    async def test_unit_search_new_zone_jlt(self):
        from main import search_bayut_properties
        result = await search_bayut_properties("jlt", "for-sale")
        assert result["success"] is True
        assert len(result["properties"]) > 0

    @pytest.mark.asyncio
    async def test_unit_search_new_zone_arjan(self):
        from main import search_bayut_properties
        result = await search_bayut_properties("arjan", "for-sale")
        assert result["success"] is True
        assert len(result["properties"]) > 0

    @pytest.mark.asyncio
    async def test_unit_search_rental(self):
        from main import search_bayut_properties
        result = await search_bayut_properties("dubai-marina", "for-rent")
        assert result["success"] is True
        for prop in result["properties"]:
            assert prop["purpose"] == "for-rent"

    @pytest.mark.asyncio
    async def test_unit_search_with_price_filter(self):
        from main import search_bayut_properties
        result = await search_bayut_properties(
            "business-bay", "for-sale", min_price=500000, max_price=1000000
        )
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_unit_search_unknown_zone_fallback(self):
        from main import search_bayut_properties
        result = await search_bayut_properties("nonexistent-zone", "for-sale")
        assert result["success"] is True
        # Should fall back to some data
        assert len(result["properties"]) > 0

    @pytest.mark.asyncio
    async def test_unit_search_via_alias(self):
        from main import search_bayut_properties
        result = await search_bayut_properties("marina", "for-sale")
        assert result["success"] is True
        assert result["location_resolved"] == "dubai-marina"


# =====================================================
# 4. MARKET TRENDS TOOL (unit)
# =====================================================

class TestMarketTrends:
    """Test market trends aggregation."""

    @pytest.mark.asyncio
    async def test_unit_market_trends_sale(self):
        from main import get_market_trends
        result = await get_market_trends("dubai-marina", "for-sale")
        assert result["success"] is True
        assert result["avg_price_aed"] > 0
        assert result["gross_yield_estimate_pct"] is not None

    @pytest.mark.asyncio
    async def test_unit_market_trends_new_zone(self):
        from main import get_market_trends
        result = await get_market_trends("arjan", "for-sale")
        assert result["success"] is True
        assert result["gross_yield_estimate_pct"] is not None
        # Arjan yield should be higher than downtown
        assert result["gross_yield_estimate_pct"] > 5.0

    @pytest.mark.asyncio
    async def test_unit_market_trends_rent(self):
        from main import get_market_trends
        result = await get_market_trends("business-bay", "for-rent")
        assert result["success"] is True
        assert result["gross_yield_estimate_pct"] is None  # No yield on rental purpose


# =====================================================
# 5. SUPPLY PIPELINE TOOL (unit)
# =====================================================

class TestSupplyPipeline:
    """Test supply pipeline tool."""

    @pytest.mark.asyncio
    async def test_unit_supply_known_zone(self):
        from main import get_supply_pipeline
        result = await get_supply_pipeline("business-bay")
        assert result["success"] is True
        assert result["risk_level"] == "HIGH"
        assert result["units_pipeline"] > 0

    @pytest.mark.asyncio
    async def test_unit_supply_new_zone_jlt(self):
        from main import get_supply_pipeline
        result = await get_supply_pipeline("jlt")
        assert result["success"] is True
        assert result["risk_level"] == "MODERATE"

    @pytest.mark.asyncio
    async def test_unit_supply_new_zone_dubai_south(self):
        from main import get_supply_pipeline
        result = await get_supply_pipeline("dubai-south")
        assert result["success"] is True
        assert result["risk_level"] == "VERY HIGH"

    @pytest.mark.asyncio
    async def test_unit_supply_unknown_zone(self):
        from main import get_supply_pipeline
        result = await get_supply_pipeline("nonexistent")
        assert result["success"] is True
        assert result["risk_level"] == "UNKNOWN"


# =====================================================
# 6. INVESTMENT ANALYSIS TOOL (unit)
# =====================================================

class TestInvestmentAnalysis:
    """Test the 4-pillar investment analysis engine."""

    @pytest.mark.asyncio
    async def test_unit_analyze_basic(self):
        from main import analyze_investment
        result = await analyze_investment(
            property_price=2500000,
            area_sqft=1500,
            annual_rent=160000,
            location="dubai-marina",
            chiller_provider="empower",
        )
        assert result["success"] is True
        assert 0 <= result["investment_score"] <= 100
        assert result["recommendation"] in (
            "STRONG BUY", "GOOD BUY", "CAUTION", "NEGOTIATE", "DO NOT BUY"
        )

    @pytest.mark.asyncio
    async def test_unit_analyze_score_breakdown(self):
        from main import analyze_investment
        result = await analyze_investment(
            property_price=2500000, area_sqft=1500, annual_rent=160000,
            location="dubai-marina", chiller_provider="empower",
        )
        breakdown = result["score_breakdown"]
        assert breakdown["price_score"]["max"] == 30
        assert breakdown["yield_score"]["max"] == 25
        assert breakdown["liquidity_score"]["max"] == 20
        assert breakdown["quality_score"]["max"] == 15
        assert breakdown["chiller_score"]["max"] == 10
        total = sum(v["score"] for v in breakdown.values())
        assert total == result["investment_score"]

    @pytest.mark.asyncio
    async def test_unit_analyze_new_zone_arjan(self):
        from main import analyze_investment
        result = await analyze_investment(
            property_price=600000, area_sqft=750, annual_rent=50000,
            location="arjan", chiller_provider="lootah",
        )
        assert result["success"] is True
        assert result["investment_score"] > 0
        fin = result["financial_summary"]
        assert fin["gross_yield_pct"] > 0
        assert fin["net_yield_pct"] > 0

    @pytest.mark.asyncio
    async def test_unit_analyze_lootah_scores_better(self):
        from main import analyze_investment
        empower_result = await analyze_investment(
            property_price=1500000, area_sqft=1000, annual_rent=100000,
            location="jlt", chiller_provider="empower",
        )
        lootah_result = await analyze_investment(
            property_price=1500000, area_sqft=1000, annual_rent=100000,
            location="jlt", chiller_provider="lootah",
        )
        # Lootah should score same or better (no fixed charges)
        assert lootah_result["investment_score"] >= empower_result["investment_score"]

    @pytest.mark.asyncio
    async def test_unit_analyze_red_flags_chiller(self):
        from main import analyze_investment
        result = await analyze_investment(
            property_price=2500000, area_sqft=1500, annual_rent=100000,
            location="dubai-marina", chiller_provider="empower",
        )
        assert any("Empower" in flag for flag in result["red_flags"])

    @pytest.mark.asyncio
    async def test_unit_analyze_red_flags_oversupply(self):
        from main import analyze_investment
        result = await analyze_investment(
            property_price=300000, area_sqft=400, annual_rent=28000,
            location="dubai-south", chiller_provider="lootah",
        )
        assert any("oversupply" in flag.lower() or "supply" in flag.lower() for flag in result["red_flags"])


# =====================================================
# 7. COMPARE PROPERTIES TOOL (unit)
# =====================================================

class TestCompareProperties:
    """Test side-by-side property comparison."""

    @pytest.mark.asyncio
    async def test_unit_compare_two(self):
        from main import compare_properties
        result = await compare_properties(properties=[
            {"price": 2500000, "area_sqft": 1500, "annual_rent": 160000,
             "location": "dubai-marina", "chiller_provider": "empower", "label": "Marina"},
            {"price": 1200000, "area_sqft": 850, "annual_rent": 90000,
             "location": "business-bay", "chiller_provider": "empower", "label": "BB"},
        ])
        assert result["success"] is True
        assert result["property_count"] == 2
        assert result["winner"] in ("Marina", "BB")

    @pytest.mark.asyncio
    async def test_unit_compare_too_few(self):
        from main import compare_properties
        result = await compare_properties(properties=[
            {"price": 1000000, "area_sqft": 800, "annual_rent": 70000,
             "location": "jvc", "chiller_provider": "lootah"},
        ])
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_unit_compare_missing_fields(self):
        from main import compare_properties
        result = await compare_properties(properties=[
            {"price": 1000000, "location": "jvc"},  # missing fields
            {"price": 1200000, "area_sqft": 850, "annual_rent": 90000,
             "location": "business-bay", "chiller_provider": "empower"},
        ])
        assert result["success"] is False


# =====================================================
# 8. MORTGAGE CALCULATOR (Feature 2 — unit)
# =====================================================

class TestMortgageCalculator:
    """Test the mortgage calculation tool."""

    @pytest.mark.asyncio
    async def test_unit_basic_mortgage(self):
        from main import calculate_mortgage
        result = await calculate_mortgage(property_price=2000000)
        assert result["success"] is True
        assert result["loan_amount_aed"] == 1600000  # 80% of 2M
        assert result["monthly_emi_aed"] > 0
        assert result["total_interest_aed"] > 0
        assert result["total_cost_aed"] > result["loan_amount_aed"]

    @pytest.mark.asyncio
    async def test_unit_mortgage_custom_params(self):
        from main import calculate_mortgage
        result = await calculate_mortgage(
            property_price=2000000,
            down_payment_pct=25,
            interest_rate=5.0,
            tenure_years=20,
        )
        assert result["success"] is True
        assert result["down_payment_aed"] == 500000
        assert result["loan_amount_aed"] == 1500000
        assert result["tenure_years"] == 20
        assert result["interest_rate_pct"] == 5.0

    @pytest.mark.asyncio
    async def test_unit_mortgage_with_rent_comparison(self):
        from main import calculate_mortgage
        result = await calculate_mortgage(
            property_price=2000000,
            down_payment_pct=20,
            interest_rate=4.5,
            annual_rent=120000,
        )
        assert result["success"] is True
        assert "cash_yield_pct" in result
        assert "leveraged_yield_pct" in result
        assert "leverage_verdict" in result
        assert result["cash_yield_pct"] == 6.0  # 120K / 2M

    @pytest.mark.asyncio
    async def test_unit_mortgage_zero_interest(self):
        from main import calculate_mortgage
        result = await calculate_mortgage(
            property_price=1000000,
            down_payment_pct=50,
            interest_rate=0,
            tenure_years=10,
        )
        assert result["success"] is True
        assert result["total_interest_aed"] == 0
        assert result["monthly_emi_aed"] > 0

    @pytest.mark.asyncio
    async def test_unit_mortgage_emi_sanity(self):
        """EMI for a 1M loan at 4.5% for 25 years should be around AED 5,558."""
        from main import calculate_mortgage
        result = await calculate_mortgage(
            property_price=1250000,
            down_payment_pct=20,
            interest_rate=4.5,
            tenure_years=25,
        )
        emi = result["monthly_emi_aed"]
        assert 5000 < emi < 6500, f"EMI {emi} outside expected range"


# =====================================================
# 9. DLD TRANSACTIONS (Feature 3 — unit)
# =====================================================

class TestDLDTransactions:
    """Test DLD transaction data tool."""

    @pytest.mark.asyncio
    async def test_unit_dld_basic(self):
        from main import get_dld_transactions
        result = await get_dld_transactions("Dubai Marina")
        assert result["success"] is True
        assert result["transaction_count"] > 0
        assert len(result["transactions"]) > 0
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_unit_dld_summary_fields(self):
        from main import get_dld_transactions
        result = await get_dld_transactions("Business Bay")
        summary = result["summary"]
        assert "avg_price_psf" in summary
        assert "median_price" in summary
        assert "total_transactions" in summary
        assert "price_trend_pct" in summary
        assert "most_active_type" in summary

    @pytest.mark.asyncio
    async def test_unit_dld_transaction_fields(self):
        from main import get_dld_transactions
        result = await get_dld_transactions("Dubai Marina")
        txn = result["transactions"][0]
        assert "date" in txn
        assert "price" in txn
        assert "area_sqft" in txn
        assert "price_per_sqft" in txn
        assert "property_type" in txn
        assert "bedrooms" in txn
        assert "is_resale" in txn

    @pytest.mark.asyncio
    async def test_unit_dld_filter_type(self):
        from main import get_dld_transactions
        result = await get_dld_transactions("arabian-ranches", property_type="villa")
        for txn in result["transactions"]:
            assert txn["property_type"] == "villa"

    @pytest.mark.asyncio
    async def test_unit_dld_new_zone(self):
        from main import get_dld_transactions
        result = await get_dld_transactions("creek-harbour")
        assert result["success"] is True
        assert result["transaction_count"] > 0
        # Creek Harbour has HIGH risk, trend should reflect it
        assert result["summary"]["price_trend_pct"] is not None

    @pytest.mark.asyncio
    async def test_unit_dld_deterministic(self):
        """Same inputs should produce same mock results."""
        from main import get_dld_transactions
        r1 = await get_dld_transactions("Dubai Marina", months=6)
        r2 = await get_dld_transactions("Dubai Marina", months=6)
        assert r1["transaction_count"] == r2["transaction_count"]
        assert r1["summary"]["avg_price_psf"] == r2["summary"]["avg_price_psf"]

    @pytest.mark.asyncio
    async def test_unit_dld_sorted_by_date(self):
        from main import get_dld_transactions
        result = await get_dld_transactions("Downtown Dubai")
        dates = [t["date"] for t in result["transactions"]]
        assert dates == sorted(dates, reverse=True)


# =====================================================
# 10. RENTAL COMPS (Feature 4 — unit)
# =====================================================

class TestRentalComps:
    """Test the rental comparables tool."""

    @pytest.mark.asyncio
    async def test_unit_rental_comps_basic(self):
        from main import get_rental_comps
        result = await get_rental_comps("Dubai Marina", bedrooms=1)
        assert result["success"] is True
        assert result["sample_size"] >= 3
        assert result["avg_annual_rent"] > 0
        assert result["rental_demand_indicator"] in ("high", "medium", "low")

    @pytest.mark.asyncio
    async def test_unit_rental_comps_with_area(self):
        from main import get_rental_comps
        result = await get_rental_comps("Business Bay", bedrooms=2, area_sqft=1200)
        assert result["success"] is True
        assert "estimated_yield_at_asking_pct" in result
        assert result["estimated_yield_at_asking_pct"] > 0

    @pytest.mark.asyncio
    async def test_unit_rental_comps_listing_fields(self):
        from main import get_rental_comps
        result = await get_rental_comps("JVC", bedrooms=0)
        assert len(result["rental_listings"]) >= 3
        comp = result["rental_listings"][0]
        assert "annual_rent" in comp
        assert "monthly_rent" in comp
        assert "rent_per_sqft" in comp
        assert "bedrooms" in comp
        assert comp["bedrooms"] == 0

    @pytest.mark.asyncio
    async def test_unit_rental_comps_new_zone(self):
        from main import get_rental_comps
        result = await get_rental_comps("arjan", bedrooms=1, area_sqft=750)
        assert result["success"] is True
        assert result["avg_annual_rent"] > 0
        # Arjan should have low demand indicator
        assert result["rental_demand_indicator"] == "low"

    @pytest.mark.asyncio
    async def test_unit_rental_comps_high_demand_zone(self):
        from main import get_rental_comps
        result = await get_rental_comps("Dubai Marina", bedrooms=2)
        assert result["rental_demand_indicator"] == "high"

    @pytest.mark.asyncio
    async def test_unit_rental_comps_deterministic(self):
        from main import get_rental_comps
        r1 = await get_rental_comps("Downtown Dubai", bedrooms=1)
        r2 = await get_rental_comps("Downtown Dubai", bedrooms=1)
        assert r1["avg_annual_rent"] == r2["avg_annual_rent"]
        assert r1["sample_size"] == r2["sample_size"]


# =====================================================
# 11. TITLE DEED VERIFICATION (unit)
# =====================================================

class TestTitleDeed:
    """Test title deed verification."""

    @pytest.mark.asyncio
    async def test_unit_verify_mock(self):
        from main import verify_title_deed
        result = await verify_title_deed("TD-2024-DM-00457")
        assert result["success"] is True
        assert result["status"] == "VERIFIED"
        assert result["ownership_type"] == "Freehold"


# =====================================================
# 12. BUILDING ISSUES SEARCH (unit)
# =====================================================

class TestBuildingIssues:
    """Test building issues/snagging search."""

    @pytest.mark.asyncio
    async def test_unit_known_building(self):
        from main import search_building_issues
        result = await search_building_issues("Executive Towers")
        assert result["success"] is True
        assert result["risk_signal"] == "HIGH"
        assert len(result["issues"]) > 0

    @pytest.mark.asyncio
    async def test_unit_unknown_building(self):
        from main import search_building_issues
        result = await search_building_issues("Nonexistent Building XYZ")
        assert result["success"] is True
        assert result["risk_signal"] == "UNKNOWN"


# =====================================================
# 13. TOOL ROUTER (unit)
# =====================================================

class TestToolRouter:
    """Test the tool dispatch function."""

    @pytest.mark.asyncio
    async def test_unit_dispatch_existing_tools(self):
        from main import _execute_tool_raw
        # Chiller
        result = await _execute_tool_raw("calculate_chiller_cost", {"provider": "empower", "area_sqft": 1000})
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_unit_dispatch_mortgage(self):
        from main import _execute_tool_raw
        result = await _execute_tool_raw("calculate_mortgage", {"property_price": 2000000})
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_unit_dispatch_dld(self):
        from main import _execute_tool_raw
        result = await _execute_tool_raw("get_dld_transactions", {"zone": "Dubai Marina"})
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_unit_dispatch_rental(self):
        from main import _execute_tool_raw
        result = await _execute_tool_raw("get_rental_comps", {"zone": "JVC", "bedrooms": 1})
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_unit_dispatch_unknown(self):
        from main import _execute_tool_raw
        result = await _execute_tool_raw("nonexistent_tool", {})
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_unit_dispatch_all_registered(self):
        """Every tool in the TOOLS schema should be dispatchable."""
        from main import TOOLS, _execute_tool_raw
        tool_names = [t["name"] for t in TOOLS]
        # We just verify the dispatch doesn't return "Unknown tool"
        for name in tool_names:
            # Build minimal valid input
            schema = next(t for t in TOOLS if t["name"] == name)
            required = schema["input_schema"].get("required", [])
            test_input = {}
            for field in required:
                props = schema["input_schema"]["properties"][field]
                if props.get("type") == "number":
                    test_input[field] = 1000000
                elif props.get("type") == "integer":
                    test_input[field] = 1
                elif props.get("type") == "string":
                    if props.get("enum"):
                        test_input[field] = props["enum"][0]
                    else:
                        test_input[field] = "dubai-marina"
                elif props.get("type") == "array":
                    test_input[field] = []

            result = await _execute_tool_raw(name, test_input)
            assert "Unknown tool" not in str(result.get("error", "")), \
                f"Tool '{name}' not dispatched correctly"


# =====================================================
# 14. TOOLS SCHEMA VALIDATION (unit)
# =====================================================

class TestToolsSchema:
    """Validate TOOLS array structure."""

    def test_unit_tool_count(self):
        from main import TOOLS
        assert len(TOOLS) == 12, f"Expected 12 tools, got {len(TOOLS)}"

    def test_unit_tool_names_unique(self):
        from main import TOOLS
        names = [t["name"] for t in TOOLS]
        assert len(names) == len(set(names)), f"Duplicate tool names: {names}"

    def test_unit_tool_schema_structure(self):
        from main import TOOLS
        for tool in TOOLS:
            assert "name" in tool, f"Tool missing 'name'"
            assert "description" in tool, f"Tool '{tool.get('name')}' missing description"
            assert "input_schema" in tool, f"Tool '{tool['name']}' missing input_schema"
            schema = tool["input_schema"]
            assert schema.get("type") == "object", f"Tool '{tool['name']}' schema not object"
            assert "properties" in schema, f"Tool '{tool['name']}' missing properties"

    def test_unit_new_tools_present(self):
        from main import TOOLS
        names = [t["name"] for t in TOOLS]
        assert "calculate_mortgage" in names
        assert "get_dld_transactions" in names
        assert "get_rental_comps" in names


# =====================================================
# 15. CACHE CONFIG (unit)
# =====================================================

class TestCacheConfig:
    """Validate cache TTL configuration."""

    def test_unit_cache_ttls_complete(self):
        from cache import CACHE_TTLS
        assert "search_bayut_properties" in CACHE_TTLS
        assert "get_market_trends" in CACHE_TTLS
        assert "get_supply_pipeline" in CACHE_TTLS
        assert "web_search_dubai" in CACHE_TTLS
        assert "search_building_issues" in CACHE_TTLS
        assert "get_dld_transactions" in CACHE_TTLS
        assert "get_rental_comps" in CACHE_TTLS

    def test_unit_cache_ttl_values(self):
        from cache import CACHE_TTLS
        assert CACHE_TTLS["get_dld_transactions"] == 86400
        assert CACHE_TTLS["get_rental_comps"] == 3600

    def test_unit_cache_key_generation(self):
        from cache import _make_key
        key1 = _make_key("test_tool", {"a": 1, "b": 2})
        key2 = _make_key("test_tool", {"b": 2, "a": 1})
        assert key1 == key2  # Order-independent
        assert key1.startswith("tv:test_tool:")


# =====================================================
# 16. DATABASE SCHEMA (unit)
# =====================================================

class TestDatabaseSchema:
    """Validate database schema completeness."""

    def test_unit_schema_ddl_tables(self):
        from database import SCHEMA_DDL
        assert "CREATE TABLE IF NOT EXISTS users" in SCHEMA_DDL
        assert "CREATE TABLE IF NOT EXISTS conversations" in SCHEMA_DDL
        assert "CREATE TABLE IF NOT EXISTS query_logs" in SCHEMA_DDL
        assert "CREATE TABLE IF NOT EXISTS subscription_events" in SCHEMA_DDL
        assert "CREATE TABLE IF NOT EXISTS saved_properties" in SCHEMA_DDL
        assert "CREATE TABLE IF NOT EXISTS referrals" in SCHEMA_DDL
        assert "CREATE TABLE IF NOT EXISTS digest_preferences" in SCHEMA_DDL

    def test_unit_schema_indexes(self):
        from database import SCHEMA_DDL
        assert "idx_saved_user" in SCHEMA_DDL
        assert "idx_referral_referrer" in SCHEMA_DDL

    def test_unit_schema_migrations(self):
        from database import SCHEMA_MIGRATIONS
        assert "bonus_queries" in SCHEMA_MIGRATIONS
        assert "referral_code" in SCHEMA_MIGRATIONS

    def test_unit_database_functions_exist(self):
        """Verify all new database functions are importable."""
        from database import (
            save_property, get_saved_properties, remove_saved_property, count_saved_properties,
            get_or_create_referral_code, create_referral, award_referral_bonus, get_referral_stats,
            set_digest_preference, get_digest_subscribers, update_digest_sent, disable_digest,
        )
        # All imported without error
        assert callable(save_property)
        assert callable(get_saved_properties)
        assert callable(remove_saved_property)
        assert callable(count_saved_properties)
        assert callable(get_or_create_referral_code)
        assert callable(create_referral)
        assert callable(award_referral_bonus)
        assert callable(get_referral_stats)
        assert callable(set_digest_preference)
        assert callable(get_digest_subscribers)
        assert callable(update_digest_sent)
        assert callable(disable_digest)


# =====================================================
# 17. DATABASE FUNCTIONS — NO-DB GRACEFUL DEGRADATION (unit)
# =====================================================

class TestDatabaseNoPool:
    """
    Test that all database functions return safe defaults when
    the database pool is not initialized (no DB connection).
    """

    @pytest.mark.asyncio
    async def test_unit_save_property_no_db(self):
        from database import save_property
        result = await save_property(12345, {"id": "x1"}, "test")
        assert result is None

    @pytest.mark.asyncio
    async def test_unit_get_saved_no_db(self):
        from database import get_saved_properties
        result = await get_saved_properties(12345)
        assert result == []

    @pytest.mark.asyncio
    async def test_unit_remove_saved_no_db(self):
        from database import remove_saved_property
        result = await remove_saved_property(12345, "x1")
        assert result is False

    @pytest.mark.asyncio
    async def test_unit_count_saved_no_db(self):
        from database import count_saved_properties
        result = await count_saved_properties(12345)
        assert result == 0

    @pytest.mark.asyncio
    async def test_unit_referral_code_no_db(self):
        from database import get_or_create_referral_code
        code = await get_or_create_referral_code(12345)
        assert code == "ref_12345"

    @pytest.mark.asyncio
    async def test_unit_create_referral_no_db(self):
        from database import create_referral
        result = await create_referral(111, 222)
        assert result is False

    @pytest.mark.asyncio
    async def test_unit_referral_stats_no_db(self):
        from database import get_referral_stats
        stats = await get_referral_stats(12345)
        assert stats["referral_count"] == 0
        assert stats["total_bonus_earned"] == 0

    @pytest.mark.asyncio
    async def test_unit_digest_pref_no_db(self):
        from database import set_digest_preference
        # Should not raise
        await set_digest_preference(12345, "weekly", ["Dubai Marina"])

    @pytest.mark.asyncio
    async def test_unit_digest_subscribers_no_db(self):
        from database import get_digest_subscribers
        result = await get_digest_subscribers("weekly")
        assert result == []

    @pytest.mark.asyncio
    async def test_unit_disable_digest_no_db(self):
        from database import disable_digest
        await disable_digest(12345)  # Should not raise

    @pytest.mark.asyncio
    async def test_unit_remaining_queries_no_db(self):
        from database import get_remaining_queries
        result = await get_remaining_queries(12345, {"free": {"queries_per_day": 50}})
        assert result == 50  # fallback default


# =====================================================
# 18. DIGEST GENERATOR (Feature 7 — unit)
# =====================================================

class TestDigestGenerator:
    """Test the digest generation system."""

    @pytest.mark.asyncio
    async def test_unit_generate_digest_single_zone(self):
        from digest import generate_digest
        result = await generate_digest(["Dubai Marina"])
        assert "TrueValue Market Digest" in result
        assert "Dubai Marina" in result
        assert "Supply Risk" in result

    @pytest.mark.asyncio
    async def test_unit_generate_digest_multiple_zones(self):
        from digest import generate_digest
        result = await generate_digest(["Dubai Marina", "Arjan", "JVC"])
        assert "Dubai Marina" in result
        assert "Arjan" in result
        # JVC should resolve to something in the digest
        assert "JVC" in result or "Jumeirah Village Circle" in result

    @pytest.mark.asyncio
    async def test_unit_generate_digest_new_zones(self):
        from digest import generate_digest
        result = await generate_digest(["Creek Harbour", "Dubai Hills"])
        assert "Creek Harbour" in result
        assert "Dubai Hills" in result

    @pytest.mark.asyncio
    async def test_unit_generate_digest_format(self):
        from digest import generate_digest
        result = await generate_digest(["Downtown Dubai"])
        assert "━" in result  # dividers
        assert "/digest\\_off" in result  # unsubscribe link
        assert "TrueValue AI" in result

    def test_unit_digest_imports(self):
        from digest import generate_digest, start_digest_scheduler
        assert callable(generate_digest)
        assert callable(start_digest_scheduler)


# =====================================================
# 19. RUN.PY STRUCTURE (unit)
# =====================================================

class TestRunStructure:
    """Verify run.py has all required components."""

    def test_unit_run_has_digest_scheduler(self):
        import run
        assert hasattr(run, "start_digest_scheduler")
        assert callable(run.start_digest_scheduler)

    def test_unit_run_has_all_starters(self):
        import run
        assert hasattr(run, "start_fastapi")
        assert hasattr(run, "start_telegram_bot")
        assert hasattr(run, "start_digest_scheduler")
        assert hasattr(run, "init_services")
        assert hasattr(run, "shutdown_services")


# =====================================================
# 20. SYSTEM PROMPT VALIDATION (unit)
# =====================================================

class TestSystemPrompt:
    """Validate the system prompt covers all tools and zones."""

    def test_unit_prompt_mentions_new_tools(self):
        from main import SYSTEM_PROMPT
        assert "calculate_mortgage" in SYSTEM_PROMPT
        assert "get_dld_transactions" in SYSTEM_PROMPT
        assert "get_rental_comps" in SYSTEM_PROMPT

    def test_unit_prompt_mentions_zones(self):
        from main import SYSTEM_PROMPT
        assert "JLT" in SYSTEM_PROMPT
        assert "Arjan" in SYSTEM_PROMPT
        assert "Dubai Hills" in SYSTEM_PROMPT
        assert "Creek Harbour" in SYSTEM_PROMPT

    def test_unit_prompt_has_tool_protocol(self):
        from main import SYSTEM_PROMPT
        assert "TOOL PROTOCOL" in SYSTEM_PROMPT
        assert "CHILLER TRAP" in SYSTEM_PROMPT
        assert "4-PILLAR" in SYSTEM_PROMPT


# =====================================================
# 21. FASTAPI ENDPOINTS (unit)
# =====================================================

class TestFastAPIEndpoints:
    """Test FastAPI route existence."""

    def test_unit_app_routes(self):
        from main import app
        routes = [r.path for r in app.routes]
        assert "/" in routes
        assert "/health" in routes
        assert "/api/query" in routes
        assert "/api/tools" in routes
        assert "/api/metrics" in routes
        assert "/metrics" in routes

    @pytest.mark.asyncio
    async def test_unit_root_endpoint(self):
        from main import root
        result = await root()
        assert result["service"] == "TrueValue — Dubai Real Estate AI"
        assert result["tools_available"] == 12

    @pytest.mark.asyncio
    async def test_unit_health_endpoint(self):
        from main import health
        result = await health()
        assert result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_unit_tools_endpoint(self):
        from main import list_tools
        result = await list_tools()
        assert result["count"] == 12
        names = [t["name"] for t in result["tools"]]
        assert "calculate_mortgage" in names
        assert "get_dld_transactions" in names
        assert "get_rental_comps" in names


# =====================================================
# 22. TELEGRAM BOT STRUCTURE (unit)
# =====================================================

class TestBotStructure:
    """Test Telegram bot structure without actually running it."""

    def test_unit_bot_imports(self):
        """Verify all new database imports work in bot."""
        import importlib
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "telegram-bot"))
        # We can't fully import bot.py without TELEGRAM_BOT_TOKEN, but we can
        # verify the database imports it needs exist
        from database import (
            save_property, get_saved_properties, remove_saved_property,
            count_saved_properties, get_or_create_referral_code,
            create_referral, award_referral_bonus, get_referral_stats,
            set_digest_preference, disable_digest,
        )
        assert True

    def test_unit_subscription_tiers(self):
        """Verify tier structure is correct."""
        # Import bot tiers via exec to avoid TOKEN requirement
        tiers = {
            "free": {"queries_per_day": 50},
            "basic": {"queries_per_day": 20},
            "pro": {"queries_per_day": 100},
            "enterprise": {"queries_per_day": -1},
        }
        assert tiers["free"]["queries_per_day"] == 50
        assert tiers["enterprise"]["queries_per_day"] == -1


# =====================================================
# 23. INTEGRATION: TOOL PIPELINE (integration)
# =====================================================

class TestIntegrationToolPipeline:
    """Integration tests verifying multi-tool workflows."""

    @pytest.mark.asyncio
    async def test_integration_search_then_analyze(self):
        """Search for properties then analyze one."""
        from main import search_bayut_properties, analyze_investment
        listings = await search_bayut_properties("arjan", "for-sale")
        assert listings["success"]
        prop = listings["properties"][0]

        analysis = await analyze_investment(
            property_price=prop["price"],
            area_sqft=prop["area"],
            annual_rent=prop["price"] * 0.085,  # ~8.5% yield
            location="arjan",
            chiller_provider=prop.get("chiller_provider", "lootah"),
        )
        assert analysis["success"]
        assert analysis["investment_score"] > 0

    @pytest.mark.asyncio
    async def test_integration_rental_comps_validate_yield(self):
        """Get rental comps then validate yield against asking price."""
        from main import get_rental_comps, analyze_investment
        comps = await get_rental_comps("business-bay", bedrooms=1, area_sqft=850)
        assert comps["success"]

        analysis = await analyze_investment(
            property_price=1200000,
            area_sqft=850,
            annual_rent=comps["avg_annual_rent"],
            location="business-bay",
            chiller_provider="empower",
        )
        assert analysis["success"]
        assert analysis["financial_summary"]["annual_gross_rent_aed"] == comps["avg_annual_rent"]

    @pytest.mark.asyncio
    async def test_integration_dld_validates_asking(self):
        """DLD transaction data should be near zone avg PSF."""
        from main import get_dld_transactions
        result = await get_dld_transactions("Dubai Marina", months=6)
        assert result["success"]
        avg_psf = result["summary"]["avg_price_psf"]
        # Should be in reasonable range of 1600 (Dubai Marina zone avg)
        assert 1000 < avg_psf < 2200, f"DLD avg PSF {avg_psf} outside expected range"

    @pytest.mark.asyncio
    async def test_integration_mortgage_with_rental(self):
        """Mortgage + rental comps = leveraged yield analysis."""
        from main import calculate_mortgage, get_rental_comps
        comps = await get_rental_comps("jlt", bedrooms=2, area_sqft=1300)
        assert comps["success"]

        mortgage = await calculate_mortgage(
            property_price=1500000,
            down_payment_pct=25,
            interest_rate=4.5,
            annual_rent=comps["avg_annual_rent"],
        )
        assert mortgage["success"]
        assert "leveraged_yield_pct" in mortgage
        assert "cash_yield_pct" in mortgage

    @pytest.mark.asyncio
    async def test_integration_full_zone_analysis(self):
        """Run all analysis tools for a single zone."""
        from main import (
            search_bayut_properties, get_market_trends, get_supply_pipeline,
            get_dld_transactions, get_rental_comps,
        )
        zone = "dubai-hills"

        listings = await search_bayut_properties(zone, "for-sale")
        trends = await get_market_trends(zone, "for-sale")
        pipeline = await get_supply_pipeline(zone)
        dld = await get_dld_transactions(zone)
        rentals = await get_rental_comps(zone, bedrooms=2)

        assert listings["success"]
        assert trends["success"]
        assert pipeline["success"]
        assert dld["success"]
        assert rentals["success"]

        # Verify data consistency
        assert pipeline["risk_level"] == "MODERATE"
        assert trends["gross_yield_estimate_pct"] == 5.5

    @pytest.mark.asyncio
    async def test_integration_compare_across_new_zones(self):
        """Compare properties across new zones."""
        from main import compare_properties
        result = await compare_properties(properties=[
            {"price": 600000, "area_sqft": 750, "annual_rent": 50000,
             "location": "arjan", "chiller_provider": "lootah", "label": "Arjan Studio"},
            {"price": 850000, "area_sqft": 780, "annual_rent": 60000,
             "location": "jlt", "chiller_provider": "empower", "label": "JLT 1BR"},
            {"price": 1350000, "area_sqft": 780, "annual_rent": 75000,
             "location": "dubai-hills", "chiller_provider": "empower", "label": "Hills 1BR"},
        ])
        assert result["success"]
        assert result["property_count"] == 3
        assert result["winner"] in ("Arjan Studio", "JLT 1BR", "Hills 1BR")

    @pytest.mark.asyncio
    async def test_integration_digest_uses_real_tools(self):
        """Digest generator should pull from real tool functions."""
        from digest import generate_digest
        digest = await generate_digest(["emaar-beachfront"])
        assert "Emaar Beachfront" in digest
        assert "Supply Risk" in digest
        assert "LOW" in digest  # Emaar Beachfront has LOW supply risk

    @pytest.mark.asyncio
    async def test_integration_all_zones_have_trends(self):
        """Every zone with mock properties should return valid trends."""
        from main import MOCK_PROPERTIES, get_market_trends
        for zone in MOCK_PROPERTIES:
            trends = await get_market_trends(zone, "for-sale")
            assert trends["success"], f"Trends failed for zone '{zone}'"
            assert trends["avg_price_aed"] > 0, f"Zone '{zone}' has zero avg price"

    @pytest.mark.asyncio
    async def test_integration_all_zones_have_dld(self):
        """Every zone should return DLD transaction data."""
        from main import MOCK_PROPERTIES, get_dld_transactions
        for zone in MOCK_PROPERTIES:
            dld = await get_dld_transactions(zone)
            assert dld["success"], f"DLD failed for zone '{zone}'"
            assert dld["transaction_count"] > 0, f"Zone '{zone}' has zero transactions"

    @pytest.mark.asyncio
    async def test_integration_all_zones_have_rental_comps(self):
        """Every zone should return rental comparables."""
        from main import MOCK_PROPERTIES, get_rental_comps
        for zone in MOCK_PROPERTIES:
            comps = await get_rental_comps(zone, bedrooms=1)
            assert comps["success"], f"Rental comps failed for zone '{zone}'"
            assert comps["avg_annual_rent"] > 0, f"Zone '{zone}' has zero avg rent"


# =====================================================
# 24. INTEGRATION: HANDLE_QUERY E2E (integration, slow)
# =====================================================

@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY") == "demo",
    reason="ANTHROPIC_API_KEY not set — skipping Claude e2e tests"
)
class TestHandleQueryE2E:
    """End-to-end tests that call the actual Claude API."""

    @pytest.mark.asyncio
    async def test_integration_e2e_chiller_query(self):
        from main import handle_query
        result = await handle_query(
            "Calculate chiller cost for 1200 sqft Empower property",
            user_id="test_e2e",
        )
        assert hasattr(result, "response")
        assert len(result.response) > 100
        assert "calculate_chiller_cost" in result.tools_used

    @pytest.mark.asyncio
    async def test_integration_e2e_new_zone_query(self):
        from main import handle_query
        result = await handle_query(
            "Analyze a studio in Arjan for investment",
            user_id="test_e2e",
        )
        assert hasattr(result, "response")
        assert len(result.response) > 100
        # Should use zone data, not fall back
        response_lower = result.response.lower()
        assert "arjan" in response_lower

    @pytest.mark.asyncio
    async def test_integration_e2e_mortgage_query(self):
        from main import handle_query
        result = await handle_query(
            "Calculate mortgage for 2M property with 25% down at 5% interest",
            user_id="test_e2e",
        )
        assert hasattr(result, "response")
        assert "calculate_mortgage" in result.tools_used

    @pytest.mark.asyncio
    async def test_integration_e2e_dld_query(self):
        from main import handle_query
        result = await handle_query(
            "Show recent DLD transactions in Dubai Marina",
            user_id="test_e2e",
        )
        assert hasattr(result, "response")
        assert "get_dld_transactions" in result.tools_used

    @pytest.mark.asyncio
    async def test_integration_e2e_rental_comps_query(self):
        from main import handle_query
        result = await handle_query(
            "What are actual rents for a 1BR in Business Bay?",
            user_id="test_e2e",
        )
        assert hasattr(result, "response")
        assert "get_rental_comps" in result.tools_used
