"""
PDF Report Generator for TrueValue AI
Builds multi-page A4 PDF reports from analysis data.
"""

import io
import re
import logging
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable,
)

from pdf_generator.styles import (
    get_report_styles, BRAND_PRIMARY, BRAND_SECONDARY, BRAND_ACCENT,
    BRAND_WARNING, BRAND_DANGER, BRAND_LIGHT_BG, BRAND_WHITE,
    BRAND_DARK_TEXT, BRAND_MUTED, BRAND_BORDER, get_score_color,
)
from pdf_generator.charts import (
    create_score_gauge, create_pillar_radar, create_yield_comparison,
)

logger = logging.getLogger("pdf_generator")

PAGE_WIDTH, PAGE_HEIGHT = A4


def _parse_score_from_text(text: str) -> dict:
    """Extract structured data from Claude's analysis text."""
    data = {
        "score": 0,
        "recommendation": "N/A",
        "gross_yield": 0.0,
        "net_yield": 0.0,
        "price_per_sqft": 0,
        "zone": "",
        "red_flags": [],
        "pillar_scores": {},
    }

    # Investment score
    score_match = re.search(r'(?:Score|score)[:\s]*(\d+)\s*/\s*100', text)
    if score_match:
        data["score"] = int(score_match.group(1))

    # Recommendation
    for rec in ["STRONG BUY", "GOOD BUY", "CAUTION", "NEGOTIATE", "DO NOT BUY"]:
        if rec in text.upper():
            data["recommendation"] = rec
            break

    # Gross yield
    gross_match = re.search(r'(\d+\.?\d*)\s*%\s*gross\s*yield', text, re.IGNORECASE)
    if gross_match:
        data["gross_yield"] = float(gross_match.group(1))

    # Net yield
    net_match = re.search(r'(\d+\.?\d*)\s*%\s*net\s*yield', text, re.IGNORECASE)
    if net_match:
        data["net_yield"] = float(net_match.group(1))

    # Price per sqft
    psf_match = re.search(r'AED\s*([\d,]+)\s*/\s*sqft', text)
    if psf_match:
        data["price_per_sqft"] = int(psf_match.group(1).replace(",", ""))

    return data


async def generate_report(
    analysis_text: str,
    query: str,
    user_name: str = "Investor",
    tools_used: list = None,
) -> bytes:
    """
    Generate a multi-page A4 PDF report from analysis text.
    Returns the PDF as bytes.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = get_report_styles()
    story = []
    parsed = _parse_score_from_text(analysis_text)

    # =====================================================
    # COVER PAGE
    # =====================================================

    # Blue header block via Table
    cover_data = [
        [Paragraph("TrueValue AI", styles["CoverTitle"])],
        [Paragraph("Institutional Property Analysis Report", styles["CoverSubtitle"])],
        [Spacer(1, 20)],
        [Paragraph(f"Prepared for: {user_name}", styles["CoverSubtitle"])],
        [Paragraph(f"Date: {datetime.now().strftime('%d %B %Y')}", styles["CoverSubtitle"])],
    ]

    cover_table = Table(cover_data, colWidths=[PAGE_WIDTH - 4 * cm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_PRIMARY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 40),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 40),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
    ]))
    story.append(Spacer(1, 3 * cm))
    story.append(cover_table)

    # Query summary
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("Analysis Query:", styles["SubHeader"]))
    story.append(Paragraph(query[:500], styles["BodyText2"]))

    if tools_used:
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(
            f"Tools Used: {', '.join(tools_used)}",
            styles["BodyText2"]
        ))

    story.append(PageBreak())

    # =====================================================
    # EXECUTIVE SUMMARY
    # =====================================================

    story.append(Paragraph("Executive Summary", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", color=BRAND_PRIMARY, thickness=2))
    story.append(Spacer(1, 0.5 * cm))

    # Score gauge chart
    try:
        gauge_img = create_score_gauge(parsed["score"])
        story.append(Image(gauge_img, width=8 * cm, height=5 * cm))
    except Exception as exc:
        logger.warning("Could not generate score gauge: %s", exc)
        story.append(Paragraph(
            f"Investment Score: {parsed['score']}/100",
            styles["ScoreText"]
        ))

    # Recommendation badge
    rec_color = get_score_color(parsed["recommendation"])
    rec_data = [[Paragraph(parsed["recommendation"], styles["RecommendationText"])]]
    rec_table = Table(rec_data, colWidths=[8 * cm])
    rec_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_LIGHT_BG),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 2, rec_color),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 1 * cm))

    # =====================================================
    # PILLAR BREAKDOWN
    # =====================================================

    story.append(Paragraph("4-Pillar Analysis", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", color=BRAND_PRIMARY, thickness=2))
    story.append(Spacer(1, 0.5 * cm))

    # Extract pillar scores from text (best effort)
    pillar_scores = {
        "Price": 20,
        "Yield": 18,
        "Liquidity": 14,
        "Quality": 10,
        "Chiller": 6,
    }

    # Try to parse from text
    for pillar, max_val in [("Price", 30), ("Yield", 25), ("Liquidity", 20), ("Quality", 15), ("Chiller", 10)]:
        match = re.search(rf'{pillar.lower()}\s*(?:score)?[:\s]*(\d+)\s*/\s*{max_val}', analysis_text, re.IGNORECASE)
        if match:
            pillar_scores[pillar] = int(match.group(1))

    try:
        radar_img = create_pillar_radar(pillar_scores)
        story.append(Image(radar_img, width=10 * cm, height=10 * cm))
    except Exception as exc:
        logger.warning("Could not generate radar chart: %s", exc)

    # Pillar details table
    pillar_max = {"Price": 30, "Yield": 25, "Liquidity": 20, "Quality": 15, "Chiller": 10}
    pillar_table_data = [
        [
            Paragraph("Pillar", styles["TableHeader"]),
            Paragraph("Score", styles["TableHeader"]),
            Paragraph("Max", styles["TableHeader"]),
            Paragraph("%", styles["TableHeader"]),
        ]
    ]

    for pillar, score in pillar_scores.items():
        mx = pillar_max.get(pillar, 10)
        pct = round(score / mx * 100) if mx > 0 else 0
        pillar_table_data.append([
            Paragraph(pillar, styles["TableCell"]),
            Paragraph(str(score), styles["TableCell"]),
            Paragraph(str(mx), styles["TableCell"]),
            Paragraph(f"{pct}%", styles["TableCell"]),
        ])

    pt = Table(pillar_table_data, colWidths=[5 * cm, 3 * cm, 3 * cm, 3 * cm])
    pt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), BRAND_WHITE),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, BRAND_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BRAND_WHITE, BRAND_LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(pt)
    story.append(Spacer(1, 1 * cm))

    # =====================================================
    # YIELD COMPARISON
    # =====================================================

    if parsed["gross_yield"] > 0 or parsed["net_yield"] > 0:
        story.append(Paragraph("Yield Analysis", styles["SectionHeader"]))
        story.append(HRFlowable(width="100%", color=BRAND_PRIMARY, thickness=2))
        story.append(Spacer(1, 0.5 * cm))

        try:
            yield_img = create_yield_comparison(
                gross=parsed["gross_yield"],
                net=parsed["net_yield"],
                benchmark=6.0,
            )
            story.append(Image(yield_img, width=12 * cm, height=5 * cm))
        except Exception as exc:
            logger.warning("Could not generate yield chart: %s", exc)

        story.append(Spacer(1, 0.5 * cm))

    # =====================================================
    # FULL ANALYSIS TEXT
    # =====================================================

    story.append(PageBreak())
    story.append(Paragraph("Detailed Analysis", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", color=BRAND_PRIMARY, thickness=2))
    story.append(Spacer(1, 0.5 * cm))

    # Split analysis into paragraphs and render
    for paragraph in analysis_text.split("\n\n"):
        clean = paragraph.strip()
        if not clean:
            continue

        # Handle headers (### or ** ... **)
        if clean.startswith("###") or clean.startswith("##"):
            clean = re.sub(r'^#+\s*', '', clean)
            story.append(Paragraph(clean, styles["SubHeader"]))
        elif clean.startswith("**") and clean.endswith("**"):
            story.append(Paragraph(clean.strip("*"), styles["SubHeader"]))
        else:
            # Clean markdown formatting for PDF
            clean = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', clean)
            clean = re.sub(r'\*(.+?)\*', r'<i>\1</i>', clean)
            clean = clean.replace("━", "-").replace("─", "-")
            # Remove emojis that ReportLab can't render
            clean = re.sub(
                r'[\U0001F300-\U0001F9FF\U00002702-\U000027B0\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF]',
                '', clean
            )
            try:
                story.append(Paragraph(clean, styles["BodyText2"]))
            except Exception:
                # Fallback: strip all XML-like tags
                plain = re.sub(r'<[^>]+>', '', clean)
                story.append(Paragraph(plain, styles["BodyText2"]))

    # =====================================================
    # DISCLAIMER
    # =====================================================

    story.append(Spacer(1, 2 * cm))
    story.append(HRFlowable(width="100%", color=BRAND_BORDER, thickness=1))
    story.append(Spacer(1, 0.3 * cm))

    disclaimer = (
        "DISCLAIMER: This report is generated by TrueValue AI for informational purposes only. "
        "It does not constitute financial advice, investment recommendation, or an offer to buy "
        "or sell property. All data is sourced from public APIs and may not reflect current market "
        "conditions. Users should conduct independent due diligence and consult qualified "
        "professionals (real estate agents, lawyers, financial advisors) before making any "
        "investment decisions. TrueValue AI assumes no liability for actions taken based on this report. "
        "Chiller cost estimates are approximations based on published tariffs and may vary from actual bills. "
        f"Report generated on {datetime.now().strftime('%d %B %Y at %H:%M UTC')}."
    )
    story.append(Paragraph(disclaimer, styles["Disclaimer"]))

    # Build the PDF
    try:
        doc.build(story)
    except Exception as exc:
        logger.error("PDF generation failed: %s", exc)
        raise

    pdf_bytes = buf.getvalue()
    buf.close()

    logger.info("PDF report generated: %d bytes", len(pdf_bytes))
    return pdf_bytes
