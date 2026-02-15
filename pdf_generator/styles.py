"""
TrueValue Brand Styles for PDF Reports
"""

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# =====================================================
# BRAND COLORS
# =====================================================

BRAND_PRIMARY = HexColor("#1a365d")      # Deep navy
BRAND_SECONDARY = HexColor("#2b6cb0")    # Medium blue
BRAND_ACCENT = HexColor("#38a169")       # Green (for positive signals)
BRAND_WARNING = HexColor("#d69e2e")      # Gold/amber
BRAND_DANGER = HexColor("#e53e3e")       # Red (for negative signals)
BRAND_LIGHT_BG = HexColor("#f7fafc")     # Light background
BRAND_DARK_TEXT = HexColor("#1a202c")     # Near-black text
BRAND_MUTED = HexColor("#718096")        # Gray text
BRAND_WHITE = HexColor("#ffffff")
BRAND_BORDER = HexColor("#e2e8f0")       # Light border

# Score color mapping
SCORE_COLORS = {
    "STRONG BUY": BRAND_ACCENT,
    "GOOD BUY": HexColor("#48bb78"),
    "CAUTION": BRAND_WARNING,
    "NEGOTIATE": HexColor("#ed8936"),
    "DO NOT BUY": BRAND_DANGER,
}


def get_score_color(recommendation: str) -> HexColor:
    """Get the brand color for a recommendation."""
    return SCORE_COLORS.get(recommendation, BRAND_MUTED)


# =====================================================
# PARAGRAPH STYLES
# =====================================================

def get_report_styles():
    """Return custom paragraph styles for the PDF report."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=28,
        textColor=BRAND_WHITE,
        alignment=TA_CENTER,
        spaceAfter=12,
    ))

    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        fontName="Helvetica",
        fontSize=14,
        textColor=HexColor("#bee3f8"),
        alignment=TA_CENTER,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=BRAND_PRIMARY,
        spaceBefore=20,
        spaceAfter=10,
        borderPadding=(0, 0, 4, 0),
    ))

    styles.add(ParagraphStyle(
        name="SubHeader",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=BRAND_SECONDARY,
        spaceBefore=12,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="BodyText2",
        fontName="Helvetica",
        fontSize=10,
        textColor=BRAND_DARK_TEXT,
        spaceBefore=4,
        spaceAfter=4,
        leading=14,
    ))

    styles.add(ParagraphStyle(
        name="ScoreText",
        fontName="Helvetica-Bold",
        fontSize=36,
        textColor=BRAND_ACCENT,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name="RecommendationText",
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=BRAND_PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="RedFlag",
        fontName="Helvetica",
        fontSize=10,
        textColor=BRAND_DANGER,
        spaceBefore=2,
        spaceAfter=2,
        leftIndent=20,
        bulletIndent=10,
    ))

    styles.add(ParagraphStyle(
        name="Disclaimer",
        fontName="Helvetica",
        fontSize=7,
        textColor=BRAND_MUTED,
        spaceBefore=8,
        spaceAfter=4,
        leading=9,
    ))

    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=BRAND_WHITE,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=9,
        textColor=BRAND_DARK_TEXT,
        alignment=TA_LEFT,
    ))

    return styles
