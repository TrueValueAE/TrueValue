"""
Dubai Real Estate AI Analysis Engine
=====================================
FastAPI + Claude tool-use engine for institutional-grade Dubai property analysis.

Deploy to Heroku: git push heroku main
Run locally:      uvicorn main:app --reload
Import in bot:    from main import handle_query
"""

# =====================================================
# IMPORTS & ENVIRONMENT
# =====================================================

import os
import json
import logging
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("dubai_estate_ai")

# =====================================================
# APP INITIALISATION
# =====================================================

app = FastAPI(
    title="Dubai Real Estate AI",
    description="Institutional-grade Dubai property analysis powered by Claude",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Anthropic client
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# =====================================================
# PYDANTIC MODELS
# =====================================================

class QueryRequest(BaseModel):
    query: str
    user_id: str = "anonymous"

class QueryResponse(BaseModel):
    response: str
    tools_used: list = []
    timestamp: str

# =====================================================
# MOCK DATA — BAYUT FALLBACK
# =====================================================

MOCK_PROPERTIES = {
    "dubai-marina": [
        {
            "id": "m001",
            "title": "Marina Gate Tower 1 — 2BR",
            "location": "Dubai Marina",
            "building": "Marina Gate Tower 1",
            "bedrooms": 2,
            "price": 2500000,
            "area": 1500,
            "price_per_sqft": 1667,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 28,
            "view": "Marina",
            "completion_year": 2018,
        },
        {
            "id": "m002",
            "title": "Princess Tower — 2BR",
            "location": "Dubai Marina",
            "building": "Princess Tower",
            "bedrooms": 2,
            "price": 2600000,
            "area": 1650,
            "price_per_sqft": 1576,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 45,
            "view": "Sea / Marina",
            "completion_year": 2012,
        },
        {
            "id": "m003",
            "title": "Cayan Tower — 1BR",
            "location": "Dubai Marina",
            "building": "Cayan Tower",
            "bedrooms": 1,
            "price": 1450000,
            "area": 950,
            "price_per_sqft": 1526,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 22,
            "view": "Marina",
            "completion_year": 2013,
        },
        {
            "id": "m004",
            "title": "Marina Gate Tower 1 — 2BR (Rent)",
            "location": "Dubai Marina",
            "building": "Marina Gate Tower 1",
            "bedrooms": 2,
            "price": 160000,
            "area": 1500,
            "price_per_sqft": 107,
            "purpose": "for-rent",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 18,
            "view": "Marina",
            "completion_year": 2018,
        },
        {
            "id": "m005",
            "title": "Marinascape — Studio",
            "location": "Dubai Marina",
            "building": "Marinascape",
            "bedrooms": 0,
            "price": 850000,
            "area": 520,
            "price_per_sqft": 1635,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 10,
            "view": "Partial Marina",
            "completion_year": 2009,
        },
    ],
    "business-bay": [
        {
            "id": "bb001",
            "title": "Boulevard Point — 1BR",
            "location": "Business Bay",
            "building": "Boulevard Point",
            "bedrooms": 1,
            "price": 1200000,
            "area": 850,
            "price_per_sqft": 1412,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 15,
            "view": "Burj Khalifa",
            "completion_year": 2017,
        },
        {
            "id": "bb002",
            "title": "Executive Towers — 2BR",
            "location": "Business Bay",
            "building": "Executive Towers",
            "bedrooms": 2,
            "price": 1800000,
            "area": 1200,
            "price_per_sqft": 1500,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 20,
            "view": "Canal",
            "completion_year": 2010,
        },
        {
            "id": "bb003",
            "title": "Damac Maison — Studio",
            "location": "Business Bay",
            "building": "Damac Maison",
            "bedrooms": 0,
            "price": 750000,
            "area": 480,
            "price_per_sqft": 1563,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 8,
            "view": "City",
            "completion_year": 2016,
        },
        {
            "id": "bb004",
            "title": "Executive Towers — 2BR (Rent)",
            "location": "Business Bay",
            "building": "Executive Towers",
            "bedrooms": 2,
            "price": 110000,
            "area": 1200,
            "price_per_sqft": 92,
            "purpose": "for-rent",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 12,
            "view": "Canal",
            "completion_year": 2010,
        },
        {
            "id": "bb005",
            "title": "Bay Square — 1BR",
            "location": "Business Bay",
            "building": "Bay Square",
            "bedrooms": 1,
            "price": 1050000,
            "area": 760,
            "price_per_sqft": 1382,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Lootah",
            "floor": 6,
            "view": "City",
            "completion_year": 2014,
        },
    ],
    "jumeirah-beach-residence": [
        {
            "id": "jbr001",
            "title": "Sadaf — 2BR",
            "location": "JBR",
            "building": "Sadaf",
            "bedrooms": 2,
            "price": 3200000,
            "area": 1800,
            "price_per_sqft": 1778,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 14,
            "view": "Sea",
            "completion_year": 2007,
        },
        {
            "id": "jbr002",
            "title": "Shams — 1BR",
            "location": "JBR",
            "building": "Shams",
            "bedrooms": 1,
            "price": 1500000,
            "area": 900,
            "price_per_sqft": 1667,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 8,
            "view": "Partial Sea",
            "completion_year": 2006,
        },
        {
            "id": "jbr003",
            "title": "Murjan — 2BR",
            "location": "JBR",
            "building": "Murjan",
            "bedrooms": 2,
            "price": 3000000,
            "area": 1750,
            "price_per_sqft": 1714,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 12,
            "view": "Sea / Marina",
            "completion_year": 2006,
        },
        {
            "id": "jbr004",
            "title": "Rimal — 2BR (Rent)",
            "location": "JBR",
            "building": "Rimal",
            "bedrooms": 2,
            "price": 185000,
            "area": 1700,
            "price_per_sqft": 109,
            "purpose": "for-rent",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 10,
            "view": "Sea",
            "completion_year": 2006,
        },
        {
            "id": "jbr005",
            "title": "Al Fattan — Studio",
            "location": "JBR",
            "building": "Al Fattan",
            "bedrooms": 0,
            "price": 1100000,
            "area": 600,
            "price_per_sqft": 1833,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 5,
            "view": "Partial Sea",
            "completion_year": 2008,
        },
    ],
    "downtown-dubai": [
        {
            "id": "dt001",
            "title": "Burj Vista — 2BR",
            "location": "Downtown Dubai",
            "building": "Burj Vista",
            "bedrooms": 2,
            "price": 3500000,
            "area": 1400,
            "price_per_sqft": 2500,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 30,
            "view": "Burj Khalifa",
            "completion_year": 2017,
        },
        {
            "id": "dt002",
            "title": "The Address Boulevard — 1BR",
            "location": "Downtown Dubai",
            "building": "The Address Boulevard",
            "bedrooms": 1,
            "price": 2200000,
            "area": 900,
            "price_per_sqft": 2444,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 22,
            "view": "Burj Khalifa / Fountain",
            "completion_year": 2018,
        },
        {
            "id": "dt003",
            "title": "Forte — 2BR",
            "location": "Downtown Dubai",
            "building": "Forte",
            "bedrooms": 2,
            "price": 3200000,
            "area": 1350,
            "price_per_sqft": 2370,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 18,
            "view": "Opera / Fountain",
            "completion_year": 2020,
        },
        {
            "id": "dt004",
            "title": "Burj Vista — 2BR (Rent)",
            "location": "Downtown Dubai",
            "building": "Burj Vista",
            "bedrooms": 2,
            "price": 200000,
            "area": 1400,
            "price_per_sqft": 143,
            "purpose": "for-rent",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 25,
            "view": "Burj Khalifa",
            "completion_year": 2017,
        },
        {
            "id": "dt005",
            "title": "29 Boulevard — 1BR",
            "location": "Downtown Dubai",
            "building": "29 Boulevard",
            "bedrooms": 1,
            "price": 1600000,
            "area": 870,
            "price_per_sqft": 1839,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Empower",
            "floor": 14,
            "view": "City",
            "completion_year": 2010,
        },
    ],
    "jumeirah-village-circle": [
        {
            "id": "jvc001",
            "title": "Binghatti Stars — Studio",
            "location": "JVC",
            "building": "Binghatti Stars",
            "bedrooms": 0,
            "price": 420000,
            "area": 380,
            "price_per_sqft": 1105,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Lootah",
            "floor": 4,
            "view": "Community",
            "completion_year": 2021,
        },
        {
            "id": "jvc002",
            "title": "Prime Residency — 1BR",
            "location": "JVC",
            "building": "Prime Residency",
            "bedrooms": 1,
            "price": 580000,
            "area": 650,
            "price_per_sqft": 892,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Lootah",
            "floor": 5,
            "view": "Community",
            "completion_year": 2019,
        },
        {
            "id": "jvc003",
            "title": "Ghalia — 2BR",
            "location": "JVC",
            "building": "Ghalia",
            "bedrooms": 2,
            "price": 850000,
            "area": 1050,
            "price_per_sqft": 810,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Lootah",
            "floor": 7,
            "view": "Pool / Community",
            "completion_year": 2020,
        },
        {
            "id": "jvc004",
            "title": "Binghatti Stars — Studio (Rent)",
            "location": "JVC",
            "building": "Binghatti Stars",
            "bedrooms": 0,
            "price": 40000,
            "area": 380,
            "price_per_sqft": 105,
            "purpose": "for-rent",
            "property_type": "apartment",
            "chiller_provider": "Lootah",
            "floor": 3,
            "view": "Community",
            "completion_year": 2021,
        },
        {
            "id": "jvc005",
            "title": "Belgravia — 1BR",
            "location": "JVC",
            "building": "Belgravia",
            "bedrooms": 1,
            "price": 620000,
            "area": 700,
            "price_per_sqft": 886,
            "purpose": "for-sale",
            "property_type": "apartment",
            "chiller_provider": "Lootah",
            "floor": 6,
            "view": "Community",
            "completion_year": 2018,
        },
    ],
}

# Zone aliases for fuzzy matching
LOCATION_ALIASES = {
    "marina": "dubai-marina",
    "dubai marina": "dubai-marina",
    "dubai-marina": "dubai-marina",
    "business bay": "business-bay",
    "businessbay": "business-bay",
    "business-bay": "business-bay",
    "jbr": "jumeirah-beach-residence",
    "jumeirah beach": "jumeirah-beach-residence",
    "jumeirah beach residence": "jumeirah-beach-residence",
    "downtown": "downtown-dubai",
    "downtown dubai": "downtown-dubai",
    "downtown-dubai": "downtown-dubai",
    "jvc": "jumeirah-village-circle",
    "jumeirah village circle": "jumeirah-village-circle",
    "jumeirah-village-circle": "jumeirah-village-circle",
}

def _resolve_location(location: str) -> str:
    """Normalise location string to a mock data key."""
    return LOCATION_ALIASES.get(location.lower().strip(), location.lower().strip())

# =====================================================
# SUPPLY PIPELINE DATA
# =====================================================

SUPPLY_PIPELINE = {
    "business-bay": {
        "zone": "Business Bay",
        "risk_level": "HIGH",
        "risk_year": 2026,
        "units_pipeline": 12500,
        "current_supply": 45000,
        "notes": (
            "Massive off-plan pipeline from Damac, Ellington, and other developers. "
            "Oversupply risk is significant heading into 2026–2027. "
            "Rental yields likely to compress under new supply pressure."
        ),
        "recommendation": "Exercise caution. Prefer resale over off-plan. Negotiate hard.",
    },
    "dubai-marina": {
        "zone": "Dubai Marina",
        "risk_level": "MODERATE",
        "risk_year": 2026,
        "units_pipeline": 4200,
        "current_supply": 38000,
        "notes": (
            "Established zone with limited land. New supply mainly at Emaar Beachfront. "
            "Demand resilient due to lifestyle appeal and short-term rental market. "
            "Empower chiller trap in most towers — factor this into net yield."
        ),
        "recommendation": "Solid hold zone. Focus on mid-floor premium views for liquidity.",
    },
    "jumeirah-beach-residence": {
        "zone": "JBR",
        "risk_level": "LOW",
        "risk_year": None,
        "units_pipeline": 800,
        "current_supply": 6500,
        "notes": (
            "Limited supply growth. Established beachfront. Strong short-term rental demand. "
            "Older stock (2006–2008) — factor snagging and major maintenance into analysis. "
            "Service charge and Empower chiller costs are above-average."
        ),
        "recommendation": "Strong hold zone for rental income. Due diligence critical on old stock.",
    },
    "downtown-dubai": {
        "zone": "Downtown Dubai",
        "risk_level": "LOW",
        "risk_year": None,
        "units_pipeline": 1800,
        "current_supply": 22000,
        "notes": (
            "Flagship district. Emaar dominates — maintains scarcity. "
            "Burj Khalifa view premium very real. High service charges. "
            "Liquidity is best in class for Dubai resale market."
        ),
        "recommendation": "Safe haven asset. Accept lower yields for capital preservation.",
    },
    "jumeirah-village-circle": {
        "zone": "JVC",
        "risk_level": "HIGH",
        "risk_year": 2026,
        "units_pipeline": 28000,
        "current_supply": 52000,
        "notes": (
            "One of the most oversupplied zones in Dubai. Hundreds of projects under construction. "
            "Gross yields appear high (7–9%) but net yields shrink fast after service charges, "
            "vacancy, and management fees. Exit liquidity is weak — large buyer pool but huge seller pool."
        ),
        "recommendation": "High yield trap. Only buy if price is deeply discounted and rental demand confirmed.",
    },
    "palm-jumeirah": {
        "zone": "Palm Jumeirah",
        "risk_level": "LOW",
        "risk_year": None,
        "units_pipeline": 600,
        "current_supply": 10000,
        "notes": (
            "Trophy asset. Ultra-low supply growth. Strong UHNW demand. "
            "Signature villas command massive premiums. Apartments more liquid than villas. "
            "Short-term rental performance is exceptional."
        ),
        "recommendation": "Institutional-grade safe haven. Buy on dips.",
    },
    "dubai-south": {
        "zone": "Dubai South",
        "risk_level": "VERY HIGH",
        "risk_year": 2027,
        "units_pipeline": 45000,
        "current_supply": 18000,
        "notes": (
            "Enormous pipeline ahead of Expo legacy development. "
            "Infrastructure still maturing. Al Maktoum Airport expansion is a long-term positive "
            "but near-term oversupply will suppress prices and yields."
        ),
        "recommendation": "Speculative play only. Long hold period required (5+ years).",
    },
}

# =====================================================
# TOOL IMPLEMENTATIONS
# =====================================================

async def search_bayut_properties(
    location: str,
    purpose: str,
    min_price: int = None,
    max_price: int = None,
    property_type: str = None,
):
    """
    Search Bayut via RapidAPI.
    Falls back to realistic mock data when BAYUT_API_KEY is missing or 'demo'.
    """
    api_key = os.getenv("BAYUT_API_KEY", "demo")
    use_mock = not api_key or api_key.lower() in ("demo", "your_rapidapi_key_here", "")

    if not use_mock:
        logger.info("Calling Bayut RapidAPI for location=%s purpose=%s", location, purpose)
        try:
            params = {
                "locationExternalIDs": location,
                "purpose": purpose,
                "hitsPerPage": 10,
                "page": 0,
                "lang": "en",
                "sort": "date-desc",
            }
            if min_price:
                params["priceMin"] = min_price
            if max_price:
                params["priceMax"] = max_price
            if property_type:
                type_map = {"apartment": "4", "villa": "3", "townhouse": "18"}
                params["categoryExternalID"] = type_map.get(property_type.lower(), "4")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://bayut.p.rapidapi.com/properties/list",
                    params=params,
                    headers={
                        "X-RapidAPI-Key": api_key,
                        "X-RapidAPI-Host": "bayut.p.rapidapi.com",
                    },
                    timeout=30.0,
                )
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "source": "bayut_api",
                    "total": data.get("nbHits", 0),
                    "properties": data.get("hits", [])[:6],
                }
            else:
                logger.warning("Bayut API returned %s — falling through to mock", response.status_code)
                use_mock = True
        except Exception as exc:
            logger.warning("Bayut API call failed (%s) — falling through to mock", exc)
            use_mock = True

    # ----- Mock fallback -----
    logger.info("Using mock Bayut data for location=%s purpose=%s", location, purpose)
    resolved = _resolve_location(location)
    pool = MOCK_PROPERTIES.get(resolved, [])

    # Filter by purpose
    pool = [p for p in pool if p["purpose"] == purpose]

    # Filter by price range
    if min_price is not None:
        pool = [p for p in pool if p["price"] >= min_price]
    if max_price is not None:
        pool = [p for p in pool if p["price"] <= max_price]

    # Filter by property type
    if property_type:
        pool = [p for p in pool if p["property_type"].lower() == property_type.lower()]

    if not pool:
        # Return all mock data for the zone if filters exclude everything
        all_zone = MOCK_PROPERTIES.get(resolved, [])
        if not all_zone:
            # Generic fallback so Claude always gets something
            all_zone = MOCK_PROPERTIES.get("dubai-marina", [])
        pool = all_zone

    return {
        "success": True,
        "source": "mock_data",
        "note": "Demo data — set BAYUT_API_KEY for live listings",
        "total": len(pool),
        "location_resolved": resolved,
        "properties": pool,
    }


async def calculate_chiller_cost(provider: str, area_sqft: float):
    """
    Pure-math calculation of annual district cooling (chiller) costs.

    Empower: consumption 0.58 fils/kWh + fixed capacity charge AED 85/TR/month
    Lootah:  consumption 0.52 fils/kWh, NO fixed charges
    Rule of thumb: 1 TR per 286 sqft, 12 kWh/sqft/year
    """
    RATES = {
        "empower": {
            "consumption_fils_per_kwh": 0.58,
            "capacity_aed_per_tr_month": 85.0,
            "has_fixed_charges": True,
        },
        "lootah": {
            "consumption_fils_per_kwh": 0.52,
            "capacity_aed_per_tr_month": 0.0,
            "has_fixed_charges": False,
        },
    }

    prov = provider.lower().strip()
    if prov not in RATES:
        return {
            "success": False,
            "error": f"Unknown chiller provider '{provider}'. Supported: empower, lootah",
        }

    rate = RATES[prov]
    sqft = float(area_sqft)

    estimated_tr = sqft / 286.0                        # 1 TR per ~286 sqft
    annual_kwh   = sqft * 12.0                         # ~12 kWh per sqft per year

    consumption_cost_aed = annual_kwh * (rate["consumption_fils_per_kwh"] / 100.0)
    capacity_cost_aed    = estimated_tr * rate["capacity_aed_per_tr_month"] * 12.0
    total_annual_aed     = consumption_cost_aed + capacity_cost_aed
    cost_per_sqft        = total_annual_aed / sqft

    if cost_per_sqft > 15:
        warning_level = "HIGH"
        warning_note  = "CRITICAL: Chiller costs will significantly erode net yield. Model carefully before buying."
    elif cost_per_sqft > 10:
        warning_level = "MEDIUM"
        warning_note  = "Moderate chiller burden. Factor into net yield calculation."
    else:
        warning_level = "LOW"
        warning_note  = "Acceptable chiller cost — no major concern."

    chiller_trap = rate["has_fixed_charges"]

    return {
        "success": True,
        "provider": prov,
        "area_sqft": sqft,
        "estimated_capacity_tr": round(estimated_tr, 2),
        "annual_kwh_estimated": round(annual_kwh, 0),
        "annual_consumption_cost_aed": round(consumption_cost_aed, 2),
        "annual_capacity_cost_aed": round(capacity_cost_aed, 2),
        "total_annual_cost_aed": round(total_annual_aed, 2),
        "monthly_cost_aed": round(total_annual_aed / 12, 2),
        "cost_per_sqft_per_year_aed": round(cost_per_sqft, 2),
        "warning_level": warning_level,
        "warning_note": warning_note,
        "chiller_trap_detected": chiller_trap,
        "chiller_trap_explanation": (
            "Empower charges a FIXED monthly capacity fee regardless of whether the unit "
            "is occupied or the AC is used. This fee alone can cost AED 15,000–30,000/year "
            "on a 1,500 sqft apartment, destroying rental yields for landlords."
            if chiller_trap else
            "No fixed capacity charges — you only pay for what you consume."
        ),
    }


async def verify_title_deed(title_deed_number: str):
    """
    Verify title deed via Dubai REST API. Falls back to mock on missing key or error.
    """
    api_key = os.getenv("DUBAI_REST_API_KEY", "")
    use_mock = not api_key or api_key in ("your_dubai_rest_key_here", "demo", "")

    if not use_mock:
        logger.info("Verifying title deed %s via Dubai REST API", title_deed_number)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://dubairest.gov.ae/api/property/title-deed/{title_deed_number}",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=30.0,
                )
            if response.status_code == 200:
                return {"success": True, "source": "dubai_rest_api", "data": response.json()}
            else:
                logger.warning("Dubai REST returned %s — falling to mock", response.status_code)
                use_mock = True
        except Exception as exc:
            logger.warning("Dubai REST API error (%s) — falling to mock", exc)
            use_mock = True

    logger.info("Using mock title deed data for %s", title_deed_number)
    # Simulate a plausible verified deed
    return {
        "success": True,
        "source": "mock_data",
        "note": "Demo verification — set DUBAI_REST_API_KEY for live DLD data",
        "title_deed_number": title_deed_number,
        "status": "VERIFIED",
        "ownership_type": "Freehold",
        "encumbrances": "None registered",
        "mortgages": "No active mortgage",
        "area_sqft_registered": "Per unit floor plan",
        "dld_reference": f"DLD-{title_deed_number[-6:].upper()}",
        "last_transaction_year": 2022,
        "warnings": [],
        "recommendation": (
            "Title appears clean in mock verification. "
            "Always obtain official DLD Oqood printout and NOC from developer before transfer."
        ),
    }


async def get_market_trends(location: str, purpose: str):
    """
    Aggregate market trend data for a location.
    Pulls from Bayut (or mock) and enriches with supply pipeline data.
    """
    logger.info("Fetching market trends for location=%s purpose=%s", location, purpose)

    listings = await search_bayut_properties(location, purpose)
    resolved = _resolve_location(location)
    pipeline = SUPPLY_PIPELINE.get(resolved, {})

    props = listings.get("properties", [])
    prices = [p.get("price", 0) for p in props if p.get("price")]
    areas  = [p.get("area", 0) for p in props if p.get("area")]

    if prices and areas:
        avg_price     = sum(prices) / len(prices)
        avg_area      = sum(areas) / len(areas)
        avg_psf       = avg_price / avg_area if avg_area > 0 else 0
        price_range   = {"min": min(prices), "max": max(prices)}
    else:
        avg_price = avg_area = avg_psf = 0
        price_range = {"min": 0, "max": 0}

    # Derive yield estimate if both sale and rent data could be cross-referenced
    gross_yield_estimate = None
    if purpose == "for-sale" and avg_price > 0:
        # Rough rule: annual rent ~ 6–7% in Marina, 7–8% in BB, 5–6% in Downtown
        zone_yield_map = {
            "dubai-marina": 0.065,
            "business-bay": 0.075,
            "jumeirah-beach-residence": 0.060,
            "downtown-dubai": 0.055,
            "jumeirah-village-circle": 0.080,
            "palm-jumeirah": 0.050,
        }
        raw_yield = zone_yield_map.get(resolved, 0.065)
        gross_yield_estimate = round(raw_yield * 100, 2)

    return {
        "success": True,
        "source": listings.get("source", "unknown"),
        "location": location,
        "location_resolved": resolved,
        "purpose": purpose,
        "sample_count": len(props),
        "avg_price_aed": round(avg_price, 0),
        "avg_area_sqft": round(avg_area, 0),
        "avg_price_per_sqft_aed": round(avg_psf, 0),
        "price_range_aed": price_range,
        "gross_yield_estimate_pct": gross_yield_estimate,
        "market_activity": "Active" if len(props) >= 4 else "Limited Listings",
        "supply_pipeline": pipeline if pipeline else {"note": "No pipeline data for this zone"},
    }


async def search_building_issues(building_name: str):
    """
    Search Reddit r/dubai for snagging, defect, and maintenance reports.
    Uses PRAW if REDDIT_CLIENT_ID is set; otherwise returns curated mock data.
    """
    client_id = os.getenv("REDDIT_CLIENT_ID", "")
    use_reddit = bool(client_id and client_id not in ("your_reddit_id", ""))

    if use_reddit:
        logger.info("Searching Reddit for building issues: %s", building_name)
        try:
            import praw  # type: ignore
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
                user_agent="dubai_estate_ai/2.0",
            )
            subreddit = reddit.subreddit("dubai")
            keywords = ["snagging", "defect", "leak", "maintenance", "issue", "problem", "mould", "mold"]
            query = f"{building_name} ({' OR '.join(keywords)})"
            posts = []
            for submission in subreddit.search(query, limit=10, time_filter="year"):
                posts.append({
                    "title": submission.title,
                    "score": submission.score,
                    "url": f"https://reddit.com{submission.permalink}",
                    "date": datetime.fromtimestamp(submission.created_utc).strftime("%Y-%m-%d"),
                    "comments": submission.num_comments,
                })
            return {
                "success": True,
                "source": "reddit_praw",
                "building": building_name,
                "posts_found": len(posts),
                "results": posts,
                "risk_signal": "HIGH" if len(posts) >= 5 else "MEDIUM" if len(posts) >= 2 else "LOW",
            }
        except Exception as exc:
            logger.warning("Reddit PRAW search failed (%s) — using mock", exc)

    logger.info("Using mock building issue data for: %s", building_name)

    # Realistic snagging data profiles keyed by building name fragments
    name_lower = building_name.lower()

    if any(k in name_lower for k in ["executive tower", "executive towers"]):
        issues = [
            {"issue": "Water ingress reported on upper floors", "severity": "HIGH", "year": 2023},
            {"issue": "Lift maintenance backlogs", "severity": "MEDIUM", "year": 2023},
            {"issue": "Chiller billing disputes — residents contest Empower invoices", "severity": "HIGH", "year": 2022},
        ]
        risk = "HIGH"
    elif any(k in name_lower for k in ["sadaf", "murjan", "rimal", "shams"]):
        issues = [
            {"issue": "Aging plumbing — reports of leaks in bathrooms", "severity": "MEDIUM", "year": 2023},
            {"issue": "Facade cracks noted — building 15+ years old", "severity": "MEDIUM", "year": 2022},
            {"issue": "Elevated service charges — RERA cap disputes", "severity": "LOW", "year": 2023},
        ]
        risk = "MEDIUM"
    elif any(k in name_lower for k in ["marina gate", "cayan"]):
        issues = [
            {"issue": "Minor snagging in handover units", "severity": "LOW", "year": 2022},
            {"issue": "Empower chiller billing disputes common", "severity": "MEDIUM", "year": 2023},
        ]
        risk = "LOW"
    elif any(k in name_lower for k in ["binghatti", "prime residency", "ghalia", "belgravia"]):
        issues = [
            {"issue": "Finishing quality complaints vs. brochure", "severity": "MEDIUM", "year": 2023},
            {"issue": "Delays in handover snagging rectification", "severity": "MEDIUM", "year": 2023},
        ]
        risk = "MEDIUM"
    else:
        issues = [
            {"issue": "No significant Reddit reports found in mock dataset", "severity": "UNKNOWN", "year": 2024},
        ]
        risk = "UNKNOWN"

    return {
        "success": True,
        "source": "mock_data",
        "note": "Set REDDIT_CLIENT_ID for live Reddit search",
        "building": building_name,
        "issues_found": len(issues),
        "risk_signal": risk,
        "issues": issues,
        "recommendation": (
            "Request RERA service charge history, developer snagging reports, "
            "and building inspection records before completing purchase."
        ),
    }


async def analyze_investment(
    property_price: float,
    area_sqft: float,
    annual_rent: float,
    location: str,
    chiller_provider: str,
):
    """
    Full 4-pillar investment scoring engine (0–100 score).

    Scoring breakdown:
      Price score     (30 pts): Price per sqft vs. zone average
      Yield score     (25 pts): Gross yield vs. Dubai benchmarks
      Liquidity score (20 pts): Zone liquidity rating
      Quality score   (15 pts): Supply risk & zone maturity
      Chiller score   (10 pts): Chiller cost impact

    Recommendation bands:
      80–100: STRONG BUY
      60–79:  GOOD BUY
      40–59:  CAUTION
      20–39:  NEGOTIATE
      0–19:   DO NOT BUY
    """
    logger.info(
        "Analyzing investment: price=%.0f area=%.0f rent=%.0f location=%s chiller=%s",
        property_price, area_sqft, annual_rent, location, chiller_provider,
    )

    resolved = _resolve_location(location)

    # --- Chiller cost ---
    chiller_data = await calculate_chiller_cost(chiller_provider, area_sqft)
    annual_chiller = chiller_data.get("total_annual_cost_aed", 0) if chiller_data.get("success") else 0

    # --- Derived metrics ---
    price_per_sqft  = property_price / area_sqft if area_sqft > 0 else 0
    gross_yield_pct = (annual_rent / property_price * 100) if property_price > 0 else 0

    # Estimated service charge (AED/sqft/year by zone)
    sc_per_sqft_map = {
        "dubai-marina": 18,
        "business-bay": 16,
        "jumeirah-beach-residence": 22,
        "downtown-dubai": 25,
        "jumeirah-village-circle": 12,
        "palm-jumeirah": 30,
    }
    svc_charge_per_sqft = sc_per_sqft_map.get(resolved, 16)
    annual_service_charge = svc_charge_per_sqft * area_sqft

    net_income = annual_rent - annual_chiller - annual_service_charge
    net_yield_pct = (net_income / property_price * 100) if property_price > 0 else 0

    # ---- PILLAR 1: Price Score (30 pts) ----
    zone_avg_psf_map = {
        "dubai-marina": 1600,
        "business-bay": 1450,
        "jumeirah-beach-residence": 1750,
        "downtown-dubai": 2200,
        "jumeirah-village-circle": 950,
        "palm-jumeirah": 2800,
    }
    zone_avg_psf = zone_avg_psf_map.get(resolved, 1500)
    psf_ratio = price_per_sqft / zone_avg_psf if zone_avg_psf > 0 else 1.0

    if psf_ratio <= 0.85:
        price_score = 30      # Deep value
    elif psf_ratio <= 0.95:
        price_score = 25
    elif psf_ratio <= 1.05:
        price_score = 20
    elif psf_ratio <= 1.15:
        price_score = 12
    else:
        price_score = 5       # Overpriced

    # ---- PILLAR 2: Yield Score (25 pts) ----
    if gross_yield_pct >= 8.0:
        yield_score = 25
    elif gross_yield_pct >= 7.0:
        yield_score = 22
    elif gross_yield_pct >= 6.0:
        yield_score = 18
    elif gross_yield_pct >= 5.0:
        yield_score = 12
    elif gross_yield_pct >= 4.0:
        yield_score = 7
    else:
        yield_score = 2

    # ---- PILLAR 3: Liquidity Score (20 pts) ----
    liquidity_map = {
        "downtown-dubai": 20,
        "dubai-marina": 18,
        "palm-jumeirah": 17,
        "jumeirah-beach-residence": 16,
        "business-bay": 13,
        "jumeirah-village-circle": 8,
    }
    liquidity_score = liquidity_map.get(resolved, 12)

    # ---- PILLAR 4: Quality / Supply Risk Score (15 pts) ----
    pipeline = SUPPLY_PIPELINE.get(resolved, {})
    supply_risk = pipeline.get("risk_level", "MODERATE")
    quality_map = {"LOW": 15, "MODERATE": 11, "HIGH": 6, "VERY HIGH": 2}
    quality_score = quality_map.get(supply_risk, 8)

    # ---- PILLAR 5: Chiller Score (10 pts) ----
    chiller_warning = chiller_data.get("warning_level", "LOW") if chiller_data.get("success") else "MEDIUM"
    chiller_trap = chiller_data.get("chiller_trap_detected", False) if chiller_data.get("success") else False
    chiller_score_map = {"LOW": 10, "MEDIUM": 6, "HIGH": 2}
    chiller_score = chiller_score_map.get(chiller_warning, 6)
    if chiller_trap:
        chiller_score = max(0, chiller_score - 2)

    # ---- TOTAL ----
    total_score = price_score + yield_score + liquidity_score + quality_score + chiller_score

    if total_score >= 80:
        recommendation = "STRONG BUY"
        emoji = "GREEN LIGHT"
        summary = "Exceptional opportunity. Strong fundamentals across all pillars. Act decisively."
    elif total_score >= 60:
        recommendation = "GOOD BUY"
        emoji = "GREEN LIGHT"
        summary = "Solid investment case. Minor concerns but fundamentals are positive."
    elif total_score >= 40:
        recommendation = "CAUTION"
        emoji = "YELLOW LIGHT"
        summary = "Mixed signals. Address red flags before proceeding. Negotiate on price."
    elif total_score >= 20:
        recommendation = "NEGOTIATE"
        emoji = "ORANGE LIGHT"
        summary = "Significant concerns. Only proceed at a meaningful price discount."
    else:
        recommendation = "DO NOT BUY"
        emoji = "RED LIGHT"
        summary = "Too many red flags. Walk away unless fundamentals change dramatically."

    red_flags = []
    if chiller_trap:
        red_flags.append("Empower fixed capacity charges will erode net yield significantly")
    if supply_risk in ("HIGH", "VERY HIGH"):
        red_flags.append(f"High oversupply risk in {resolved} — rental and capital values at risk")
    if gross_yield_pct < 5.0:
        red_flags.append(f"Gross yield of {gross_yield_pct:.1f}% is below Dubai minimum threshold of 5%")
    if net_yield_pct < 3.0:
        red_flags.append(f"Net yield of {net_yield_pct:.1f}% after costs is very weak")
    if psf_ratio > 1.15:
        red_flags.append(f"Price per sqft (AED {price_per_sqft:,.0f}) is {(psf_ratio-1)*100:.0f}% above zone average")

    return {
        "success": True,
        "investment_score": total_score,
        "recommendation": recommendation,
        "signal": emoji,
        "summary": summary,
        "red_flags": red_flags,
        "score_breakdown": {
            "price_score":     {"score": price_score,     "max": 30, "note": f"AED {price_per_sqft:,.0f}/sqft vs zone avg AED {zone_avg_psf:,.0f}/sqft"},
            "yield_score":     {"score": yield_score,     "max": 25, "note": f"Gross yield {gross_yield_pct:.1f}%"},
            "liquidity_score": {"score": liquidity_score, "max": 20, "note": f"Zone: {resolved}"},
            "quality_score":   {"score": quality_score,   "max": 15, "note": f"Supply risk: {supply_risk}"},
            "chiller_score":   {"score": chiller_score,   "max": 10, "note": f"{chiller_provider} — {chiller_warning} warning"},
        },
        "financial_summary": {
            "property_price_aed":         property_price,
            "area_sqft":                  area_sqft,
            "price_per_sqft_aed":         round(price_per_sqft, 0),
            "zone_avg_psf_aed":           zone_avg_psf,
            "annual_gross_rent_aed":      annual_rent,
            "annual_chiller_cost_aed":    round(annual_chiller, 0),
            "annual_service_charge_aed":  round(annual_service_charge, 0),
            "annual_net_income_aed":      round(net_income, 0),
            "gross_yield_pct":            round(gross_yield_pct, 2),
            "net_yield_pct":              round(net_yield_pct, 2),
            "estimated_service_charge_psf": svc_charge_per_sqft,
        },
    }


async def get_supply_pipeline(zone: str):
    """
    Return oversupply risk data for a given zone.
    Uses hardcoded research data for known zones.
    """
    logger.info("Fetching supply pipeline for zone: %s", zone)
    resolved = _resolve_location(zone)
    data = SUPPLY_PIPELINE.get(resolved)

    if data:
        return {"success": True, "source": "hardcoded_research", **data}

    # Generic fallback
    return {
        "success": True,
        "source": "generic_estimate",
        "zone": zone,
        "risk_level": "UNKNOWN",
        "risk_year": None,
        "units_pipeline": None,
        "notes": (
            f"No detailed pipeline data available for '{zone}'. "
            "Recommend checking Bayut trends, Property Finder, and DLD transaction reports "
            "for supply/demand indicators."
        ),
        "recommendation": (
            "Insufficient data. Proceed with manual research via DLD or a local broker "
            "before committing capital."
        ),
    }


async def compare_properties(property_a: dict, property_b: dict):
    """
    Side-by-side investment comparison of two properties.
    Each dict should contain: price, area_sqft, annual_rent, location, chiller_provider.
    """
    logger.info("Comparing two properties")

    required_keys = ["price", "area_sqft", "annual_rent", "location", "chiller_provider"]

    def validate(prop, label):
        missing = [k for k in required_keys if k not in prop]
        if missing:
            raise ValueError(f"Property {label} missing fields: {missing}")

    try:
        validate(property_a, "A")
        validate(property_b, "B")
    except ValueError as exc:
        return {"success": False, "error": str(exc)}

    analysis_a = await analyze_investment(
        property_price=float(property_a["price"]),
        area_sqft=float(property_a["area_sqft"]),
        annual_rent=float(property_a["annual_rent"]),
        location=property_a["location"],
        chiller_provider=property_a["chiller_provider"],
    )
    analysis_b = await analyze_investment(
        property_price=float(property_b["price"]),
        area_sqft=float(property_b["area_sqft"]),
        annual_rent=float(property_b["annual_rent"]),
        location=property_b["location"],
        chiller_provider=property_b["chiller_provider"],
    )

    winner = "A" if analysis_a["investment_score"] >= analysis_b["investment_score"] else "B"
    margin = abs(analysis_a["investment_score"] - analysis_b["investment_score"])

    if margin <= 5:
        verdict = "TOO CLOSE TO CALL — further due diligence required on both"
    elif winner == "A":
        verdict = f"Property A wins by {margin} points — {analysis_a['recommendation']}"
    else:
        verdict = f"Property B wins by {margin} points — {analysis_b['recommendation']}"

    return {
        "success": True,
        "winner": winner,
        "verdict": verdict,
        "margin_points": margin,
        "property_a": {
            "score": analysis_a["investment_score"],
            "recommendation": analysis_a["recommendation"],
            "gross_yield_pct": analysis_a["financial_summary"]["gross_yield_pct"],
            "net_yield_pct": analysis_a["financial_summary"]["net_yield_pct"],
            "price_per_sqft": analysis_a["financial_summary"]["price_per_sqft_aed"],
            "annual_chiller_cost": analysis_a["financial_summary"]["annual_chiller_cost_aed"],
            "red_flags": analysis_a["red_flags"],
        },
        "property_b": {
            "score": analysis_b["investment_score"],
            "recommendation": analysis_b["recommendation"],
            "gross_yield_pct": analysis_b["financial_summary"]["gross_yield_pct"],
            "net_yield_pct": analysis_b["financial_summary"]["net_yield_pct"],
            "price_per_sqft": analysis_b["financial_summary"]["price_per_sqft_aed"],
            "annual_chiller_cost": analysis_b["financial_summary"]["annual_chiller_cost_aed"],
            "red_flags": analysis_b["red_flags"],
        },
    }


# =====================================================
# TOOL ROUTER
# =====================================================

async def _execute_tool(tool_name: str, tool_input: dict) -> dict:
    """Route a tool call to the correct async function."""
    if tool_name == "search_bayut_properties":
        return await search_bayut_properties(**tool_input)
    elif tool_name == "calculate_chiller_cost":
        return await calculate_chiller_cost(**tool_input)
    elif tool_name == "verify_title_deed":
        return await verify_title_deed(**tool_input)
    elif tool_name == "get_market_trends":
        return await get_market_trends(**tool_input)
    elif tool_name == "search_building_issues":
        return await search_building_issues(**tool_input)
    elif tool_name == "analyze_investment":
        return await analyze_investment(**tool_input)
    elif tool_name == "get_supply_pipeline":
        return await get_supply_pipeline(**tool_input)
    elif tool_name == "compare_properties":
        return await compare_properties(**tool_input)
    else:
        return {"error": f"Unknown tool: {tool_name}", "success": False}


# =====================================================
# CLAUDE TOOL DEFINITIONS
# =====================================================

TOOLS = [
    {
        "name": "search_bayut_properties",
        "description": (
            "Search Dubai property listings on Bayut (UAE's largest portal). "
            "Returns properties with price, area, building name, chiller provider and key stats. "
            "Use this to get current market listings for any Dubai zone."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Zone slug e.g. 'dubai-marina', 'business-bay', 'downtown-dubai', 'jumeirah-village-circle', 'jumeirah-beach-residence'",
                },
                "purpose": {
                    "type": "string",
                    "enum": ["for-sale", "for-rent"],
                    "description": "Whether to search sale or rental listings",
                },
                "min_price": {
                    "type": "number",
                    "description": "Minimum price in AED (optional)",
                },
                "max_price": {
                    "type": "number",
                    "description": "Maximum price in AED (optional)",
                },
                "property_type": {
                    "type": "string",
                    "enum": ["apartment", "villa", "townhouse"],
                    "description": "Property type filter (optional)",
                },
            },
            "required": ["location", "purpose"],
        },
    },
    {
        "name": "calculate_chiller_cost",
        "description": (
            "Calculate annual district cooling (chiller) costs. CRITICAL for Dubai analysis. "
            "Empower has FIXED capacity charges that can cost AED 15,000–30,000/year "
            "even when the unit is vacant — a major yield killer. "
            "Always run this before recommending a purchase in any Empower-served building."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "provider": {
                    "type": "string",
                    "enum": ["empower", "lootah"],
                    "description": "Chiller provider name",
                },
                "area_sqft": {
                    "type": "number",
                    "description": "Property area in square feet",
                },
            },
            "required": ["provider", "area_sqft"],
        },
    },
    {
        "name": "verify_title_deed",
        "description": (
            "Verify property title deed authenticity and ownership status via Dubai DLD/REST API. "
            "Essential for fraud prevention and legal due diligence before any transaction."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title_deed_number": {
                    "type": "string",
                    "description": "The DLD title deed number from the property documents",
                },
            },
            "required": ["title_deed_number"],
        },
    },
    {
        "name": "get_market_trends",
        "description": (
            "Get current market trends including average price per sqft, listing volumes, "
            "estimated gross yield, and supply pipeline risk for a Dubai zone."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Zone slug or name (e.g. 'dubai-marina', 'business-bay')",
                },
                "purpose": {
                    "type": "string",
                    "enum": ["for-sale", "for-rent"],
                    "description": "Sale or rental market",
                },
            },
            "required": ["location", "purpose"],
        },
    },
    {
        "name": "search_building_issues",
        "description": (
            "Search for reported snagging defects, maintenance issues, leaks, and resident complaints "
            "about a specific building. Uses Reddit r/dubai data. "
            "Run this as part of technical due diligence on any property under consideration."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "building_name": {
                    "type": "string",
                    "description": "Name of the building or development to search",
                },
            },
            "required": ["building_name"],
        },
    },
    {
        "name": "analyze_investment",
        "description": (
            "Run full 4-pillar investment analysis and generate a GO/NO-GO recommendation. "
            "Scores the property 0–100 across Price, Yield, Liquidity, Quality, and Chiller pillars. "
            "Returns net yield after all costs, red flags, and investment grade rating."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "property_price": {
                    "type": "number",
                    "description": "Total purchase price in AED",
                },
                "area_sqft": {
                    "type": "number",
                    "description": "Property area in square feet",
                },
                "annual_rent": {
                    "type": "number",
                    "description": "Expected annual rental income in AED",
                },
                "location": {
                    "type": "string",
                    "description": "Zone name or slug (e.g. 'dubai-marina', 'business-bay')",
                },
                "chiller_provider": {
                    "type": "string",
                    "enum": ["empower", "lootah"],
                    "description": "District cooling provider for the building",
                },
            },
            "required": ["property_price", "area_sqft", "annual_rent", "location", "chiller_provider"],
        },
    },
    {
        "name": "get_supply_pipeline",
        "description": (
            "Get oversupply risk assessment for a Dubai zone. "
            "Returns pipeline unit counts, risk level (LOW/MODERATE/HIGH/VERY HIGH), "
            "and analyst notes on how new supply may impact prices and yields."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "zone": {
                    "type": "string",
                    "description": "Zone name or slug to check supply risk for",
                },
            },
            "required": ["zone"],
        },
    },
    {
        "name": "compare_properties",
        "description": (
            "Side-by-side investment comparison of two properties. "
            "Runs full analyze_investment on both and declares a winner with scoring rationale."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "property_a": {
                    "type": "object",
                    "description": "First property details",
                    "properties": {
                        "price":            {"type": "number", "description": "Purchase price AED"},
                        "area_sqft":        {"type": "number", "description": "Area in sqft"},
                        "annual_rent":      {"type": "number", "description": "Annual rent AED"},
                        "location":         {"type": "string", "description": "Zone name"},
                        "chiller_provider": {"type": "string", "description": "empower or lootah"},
                        "label":            {"type": "string", "description": "Human label e.g. 'Marina Gate 2BR'"},
                    },
                    "required": ["price", "area_sqft", "annual_rent", "location", "chiller_provider"],
                },
                "property_b": {
                    "type": "object",
                    "description": "Second property details",
                    "properties": {
                        "price":            {"type": "number", "description": "Purchase price AED"},
                        "area_sqft":        {"type": "number", "description": "Area in sqft"},
                        "annual_rent":      {"type": "number", "description": "Annual rent AED"},
                        "location":         {"type": "string", "description": "Zone name"},
                        "chiller_provider": {"type": "string", "description": "empower or lootah"},
                        "label":            {"type": "string", "description": "Human label e.g. 'Business Bay Studio'"},
                    },
                    "required": ["price", "area_sqft", "annual_rent", "location", "chiller_provider"],
                },
            },
            "required": ["property_a", "property_b"],
        },
    },
]

# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """You are TrueValue AI — an institutional-grade Dubai real estate analyst. \
You combine data from live property portals, district cooling providers, DLD records, and \
social listening to deliver hedge-fund-quality analysis to individual investors.

## YOUR EXPERTISE DOMAINS

### Chiller Trap Awareness (Your #1 Superpower)
- Empower is the dominant district cooling provider in Dubai Marina, Downtown, Business Bay, JBR, and most premium zones
- Empower charges a FIXED monthly capacity fee (AED 85/TR/month) REGARDLESS of occupancy or AC usage
- On a 1,500 sqft apartment: ~5.25 TR capacity = AED 5,355/month fixed = AED 64,260/year just in capacity charges
- This means a landlord paying AED 64,260/year in fixed fees on a property renting for AED 130,000/year has a REAL net yield problem
- Always calculate chiller costs and surface this as a red flag when Empower is involved
- Lootah charges variable-only (no fixed component) — significantly better for buy-to-let investors

### Zone Intelligence
**Dubai Marina**: Established, liquid, strong STR (short-term rental) market. Mostly Empower. Good for capital preservation. Supply constrained.
**Business Bay**: High oversupply risk 2026. Empower dominated. Great for owner-occupiers, risky for investors without yield buffer.
**JBR**: Premium beachfront, older stock (2006–2008). Strong rental demand. High service charges and Empower costs. Old buildings need snagging diligence.
**Downtown Dubai**: Flagship district. Emaar quality = scarcity premium. Best liquidity in Dubai. Accept lower yields for safety.
**JVC (Jumeirah Village Circle)**: Yield trap. Headline yields look high (7–9%) but massive oversupply pipeline destroys net yields and exit liquidity. Tread carefully.
**Palm Jumeirah**: Trophy asset. UHNW demand. Very limited supply. Excellent for capital preservation.
**Dubai South**: Speculative long-hold. Massive pipeline. Not suitable for income investors.

### 4-Pillar Investment Framework
When analysing any property, assess:
1. **PRICE** — Is the price per sqft at, below, or above zone average? Distressed pricing = opportunity.
2. **YIELD** — Gross yield (rent/price) and especially NET yield after chiller, service charge, and vacancy.
3. **LIQUIDITY** — How easy is exit? Downtown > Marina > JBR > Business Bay > JVC for resale speed.
4. **QUALITY** — Building age, developer track record, snagging issues, supply pipeline risk.

### Red Flag Thresholds
- Chiller cost > AED 15/sqft/year: HIGH warning
- Chiller cost > AED 10/sqft/year: MEDIUM warning
- Net yield < 4%: Poor (Dubai opportunity cost is too high)
- Net yield < 3%: Critical — do not buy for investment
- Price per sqft > 15% above zone average: Overpriced flag
- Supply pipeline risk HIGH or VERY HIGH: Yield compression likely
- Building > 15 years: Mandatory snagging and major maintenance escrow check
- Service charge > AED 25/sqft/year: High — verify with RERA and factor into net yield

### Communication Style
- Use **bold** for key numbers and recommendations
- Use structured sections with clear headers
- Lead with the most important insight (chiller trap, oversupply, yield)
- Give a clear GO / NO-GO or CAUTION verdict on every investment question
- Use bullet points for red flags
- Be direct — institutional investors want clarity not hedging
- Always state net yield (after costs), not just gross yield
- When you detect a chiller trap, make it prominent — this is your signature value add

### Tool Usage Protocol
1. For property searches: use search_bayut_properties first to get real listings
2. For any investment question: ALWAYS run calculate_chiller_cost
3. For full analysis: run analyze_investment for a scored recommendation
4. For due diligence: run search_building_issues and verify_title_deed
5. For market context: run get_market_trends and get_supply_pipeline
6. For comparisons: use compare_properties tool, then add qualitative colour

Always run multiple tools when needed. A complete analysis typically uses 3–5 tools.
"""

# =====================================================
# CORE QUERY HANDLER (importable by Telegram bot)
# =====================================================

async def handle_query(query: str, user_id: str = "anonymous") -> QueryResponse:
    """
    Process a user query through Claude with iterative tool-use (max 5 iterations).
    This is a standalone async function — importable by the Telegram bot or any other consumer.
    """
    logger.info("handle_query — user_id=%s query_len=%d", user_id, len(query))

    tools_used: list[str] = []
    conversation = [{"role": "user", "content": query}]

    for iteration in range(5):
        logger.debug("Iteration %d — calling Claude", iteration + 1)

        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=conversation,
        )

        logger.debug("Stop reason: %s", response.stop_reason)

        if response.stop_reason == "end_turn":
            # Extract final text
            final_text = "".join(
                block.text for block in response.content if hasattr(block, "text")
            )
            logger.info("Query complete — tools_used=%s", tools_used)
            return QueryResponse(
                response=final_text,
                tools_used=tools_used,
                timestamp=datetime.now().isoformat(),
            )

        elif response.stop_reason == "tool_use":
            # Convert ContentBlocks to plain dicts for serialization
            assistant_content = []
            tool_results = []

            for block in response.content:
                if block.type == "text":
                    assistant_content.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })

                    # Execute the tool
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id

                    tools_used.append(tool_name)
                    logger.info("Executing tool: %s", tool_name)

                    result = await _execute_tool(tool_name, tool_input)

                    # Create tool result
                    result_str = json.dumps(result) if not isinstance(result, str) else result

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": result_str,
                    })

            # Append assistant message with tool uses
            conversation.append({"role": "assistant", "content": assistant_content})
            # Append user message with tool results
            conversation.append({"role": "user", "content": tool_results})

        else:
            logger.error("Unexpected stop_reason: %s", response.stop_reason)
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected stop reason from Claude: {response.stop_reason}",
            )

    logger.warning("Max iterations reached for user_id=%s", user_id)
    raise HTTPException(
        status_code=500,
        detail="Query required more tool iterations than allowed. Try a more specific question.",
    )


# =====================================================
# FASTAPI ENDPOINTS
# =====================================================

@app.post("/api/query", response_model=QueryResponse)
async def api_query(request: QueryRequest):
    """Main analysis endpoint — accepts a natural language query about Dubai real estate."""
    return await handle_query(query=request.query, user_id=request.user_id)


@app.get("/")
async def root():
    return {
        "service": "TrueValue — Dubai Real Estate AI",
        "version": "2.0.0",
        "status": "operational",
        "model": "claude-sonnet-4-20250514",
        "tools_available": len(TOOLS),
        "endpoints": {
            "query":  "POST /api/query",
            "health": "GET  /health",
            "tools":  "GET  /api/tools",
        },
        "signature_features": [
            "Chiller trap detection (Empower vs Lootah)",
            "4-pillar investment scoring (0–100)",
            "Supply pipeline risk by zone",
            "Building snagging intelligence",
            "Title deed verification",
            "Side-by-side property comparison",
        ],
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "anthropic_key_set": bool(os.getenv("ANTHROPIC_API_KEY")),
        "bayut_key_set": bool(os.getenv("BAYUT_API_KEY") and os.getenv("BAYUT_API_KEY") not in ("your_rapidapi_key_here", "demo")),
        "reddit_key_set": bool(os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_ID") != "your_reddit_id"),
        "dubai_rest_key_set": bool(os.getenv("DUBAI_REST_API_KEY") and os.getenv("DUBAI_REST_API_KEY") != "your_dubai_rest_key_here"),
    }


@app.get("/api/tools")
async def list_tools():
    return {
        "count": len(TOOLS),
        "tools": [
            {"name": t["name"], "description": t["description"][:120] + "..."}
            for t in TOOLS
        ],
    }


# =====================================================
# ENTRYPOINT
# =====================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info("Starting TrueValue Dubai AI on port %d", port)
    uvicorn.run(app, host="0.0.0.0", port=port)
