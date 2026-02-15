"""
Chart Generation for TrueValue PDF Reports
Uses matplotlib with Agg backend (non-interactive, thread-safe).
"""

import io
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


def create_score_gauge(score: int, max_score: int = 100) -> io.BytesIO:
    """
    Create a semicircular gauge chart for the investment score.
    Returns a BytesIO PNG image.
    """
    fig, ax = plt.subplots(figsize=(4, 2.5), subplot_kw={"projection": "polar"})

    # Gauge spans from pi to 0 (left to right semicircle)
    theta_bg = np.linspace(np.pi, 0, 100)
    radii_bg = [1] * 100

    # Color zones
    colors_bg = []
    for i in range(100):
        pct = i / 100
        if pct < 0.2:
            colors_bg.append("#e53e3e")   # Red
        elif pct < 0.4:
            colors_bg.append("#ed8936")   # Orange
        elif pct < 0.6:
            colors_bg.append("#d69e2e")   # Yellow
        elif pct < 0.8:
            colors_bg.append("#48bb78")   # Light green
        else:
            colors_bg.append("#38a169")   # Green

    ax.bar(theta_bg, radii_bg, width=np.pi / 100, bottom=0.6,
           color=colors_bg, alpha=0.3, edgecolor="none")

    # Score needle
    score_pct = min(score / max_score, 1.0)
    needle_angle = np.pi * (1 - score_pct)
    ax.annotate("", xy=(needle_angle, 1.5), xytext=(needle_angle, 0.55),
                arrowprops=dict(arrowstyle="-|>", color="#1a365d", lw=2.5))

    # Score text
    ax.text(np.pi / 2, 0.15, f"{score}", ha="center", va="center",
            fontsize=28, fontweight="bold", color="#1a365d")
    ax.text(np.pi / 2, -0.2, f"/ {max_score}", ha="center", va="center",
            fontsize=10, color="#718096")

    ax.set_ylim(0, 1.7)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.axis("off")

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                transparent=True, pad_inches=0.1)
    plt.close(fig)
    buf.seek(0)
    return buf


def create_pillar_radar(scores: dict) -> io.BytesIO:
    """
    Create a radar/spider chart for the 5-pillar breakdown.
    scores = {"Price": 25, "Yield": 18, "Liquidity": 16, "Quality": 12, "Chiller": 8}
    Max values: Price=30, Yield=25, Liquidity=20, Quality=15, Chiller=10
    """
    categories = list(scores.keys())
    max_values = [30, 25, 20, 15, 10]
    values = [scores.get(cat, 0) for cat in categories]

    # Normalize to 0-1
    normalized = [v / m if m > 0 else 0 for v, m in zip(values, max_values)]

    # Close the polygon
    normalized += normalized[:1]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={"projection": "polar"})

    ax.fill(angles, normalized, color="#2b6cb0", alpha=0.25)
    ax.plot(angles, normalized, color="#2b6cb0", linewidth=2)
    ax.scatter(angles[:-1], normalized[:-1], color="#1a365d", s=50, zorder=5)

    ax.set_xticks(angles[:-1])
    labels = [f"{cat}\n{val}/{mx}" for cat, val, mx in zip(categories, values, max_values)]
    ax.set_xticklabels(labels, fontsize=8, color="#1a202c")
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"], fontsize=6, color="#a0aec0")
    ax.spines["polar"].set_color("#e2e8f0")

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf


def create_yield_comparison(gross: float, net: float, benchmark: float = 6.0) -> io.BytesIO:
    """
    Create a horizontal bar chart comparing gross yield, net yield, and benchmark.
    """
    fig, ax = plt.subplots(figsize=(5, 2))

    categories = ["Benchmark", "Net Yield", "Gross Yield"]
    values = [benchmark, net, gross]
    colors = ["#a0aec0", "#2b6cb0", "#1a365d"]

    # Color net yield red if below benchmark
    if net < benchmark:
        colors[1] = "#e53e3e"

    bars = ax.barh(categories, values, height=0.5, color=colors, edgecolor="none")

    # Add value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=10, fontweight="bold", color="#1a202c")

    ax.set_xlim(0, max(values) * 1.3)
    ax.set_xlabel("Yield %", fontsize=9, color="#718096")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color("#e2e8f0")
    ax.spines["left"].set_color("#e2e8f0")
    ax.tick_params(colors="#718096")

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf
