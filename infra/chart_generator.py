#!/usr/bin/env python3
"""
Professional financial chart generator CLI.

Usage:
    python infra/chart_generator.py {chart_type} --data '{json}' --output path.png
    python infra/chart_generator.py {chart_type} --data-file input.json --output path.png

Chart types:
    time-series      Bar chart with optional YoY growth line overlay (replaces revenue-trend, margin-trend, eps-trend)
    waterfall        Bridge chart (revenue walk, value creation, EPS bridge)
    football-field   Horizontal range bars comparing valuation methodologies
    pie              Pie/donut chart for segment breakdown (replaces segment-pie)
    scenario-bar     Grouped bar for bull/base/bear scenarios
    dcf-sensitivity  Heatmap for DCF price sensitivity

Legacy aliases (still accepted):
    revenue-trend -> time-series
    margin-trend  -> time-series
    eps-trend     -> time-series
    segment-pie   -> pie
"""

import argparse
import json
import os
import sys
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np


# ---------------------------------------------------------------------------
# Design system colors
# ---------------------------------------------------------------------------

COLORS = {
    "navy": "#1B2A4A",
    "steel_blue": "#4A6FA5",
    "gold": "#C5A55A",
    "green": "#27AE60",
    "red": "#C0392B",
    "light_gray": "#F8F9FA",
    "mid_gray": "#E9ECEF",
    "dark_gray": "#6C757D",
    "near_black": "#343A40",
}

COLOR_CYCLE = [
    COLORS["navy"],
    COLORS["steel_blue"],
    COLORS["gold"],
    COLORS["dark_gray"],
    COLORS["green"],
    COLORS["red"],
]

DEFAULT_DPI = 150
DEFAULT_FIGSIZE = (10, 6)
HEATMAP_FIGSIZE = (10, 8)
DEFAULT_OUTPUT_DIR = "reports/.charts"

TITLE_FONTSIZE = 14
LABEL_FONTSIZE = 11


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_base_style(ax, title=None):
    """Apply design system styling to an axes object."""
    ax.set_facecolor("white")
    ax.figure.set_facecolor("white")
    ax.yaxis.grid(True, color=COLORS["mid_gray"], linewidth=0.5, linestyle="-")
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLORS["mid_gray"])
    ax.spines["bottom"].set_color(COLORS["mid_gray"])
    ax.tick_params(labelsize=LABEL_FONTSIZE, colors=COLORS["dark_gray"])
    if title:
        ax.set_title(title, fontsize=TITLE_FONTSIZE, fontweight="bold",
                      color=COLORS["navy"], pad=12)


def _format_number(val):
    """Format a number with comma separators."""
    if abs(val) >= 1:
        return f"{val:,.0f}"
    return f"{val:,.2f}"


def _default_output_path(chart_type):
    """Generate a default output path from chart type and timestamp."""
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(DEFAULT_OUTPUT_DIR, f"{chart_type}_{ts}.png")


def _save(fig, output_path):
    """Save figure and close."""
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=DEFAULT_DPI, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    print(json.dumps({"status": "ok", "path": output_path}))


def _error(message):
    """Print error JSON to stderr and exit."""
    print(json.dumps({"error": message}), file=sys.stderr)
    sys.exit(1)


def _compute_yoy_growth(values):
    """Compute YoY growth percentages. Returns list same length as values,
    with None for the first 4 entries (no prior-year comp)."""
    growth = [None] * len(values)
    for i in range(4, len(values)):
        prior = values[i - 4]
        if prior and prior != 0:
            growth[i] = ((values[i] - prior) / abs(prior)) * 100
    return growth


# ---------------------------------------------------------------------------
# Chart generators
# ---------------------------------------------------------------------------

def chart_time_series(data, output_path):
    """Flexible time-series chart. Supports:
    - Bar chart with optional YoY growth overlay (single values array)
    - Multi-line chart (series dict of name -> values)
    - Bar + line combo (values + series)
    """
    periods = data.get("periods")
    values = data.get("values")
    series = data.get("series")
    label = data.get("label", "Value")
    title = data.get("title", label)

    if not periods:
        _error("time-series requires 'periods'.")
    if not values and not series:
        _error("time-series requires 'values' and/or 'series'.")

    fig, ax1 = plt.subplots(figsize=DEFAULT_FIGSIZE)
    _apply_base_style(ax1, title)
    x = np.arange(len(periods))

    # Bar chart mode (single values array)
    if values and not series:
        if len(periods) != len(values):
            _error("time-series: 'periods' and 'values' must be equal length.")
        ax1.bar(x, values, color=COLORS["steel_blue"], width=0.6, zorder=3)
        ax1.set_ylabel(label, fontsize=LABEL_FONTSIZE, color=COLORS["dark_gray"])
        ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _format_number(v)))

        # YoY growth overlay
        growth = _compute_yoy_growth(values)
        growth_vals = [(i, g) for i, g in enumerate(growth) if g is not None]
        if growth_vals:
            ax2 = ax1.twinx()
            ax2.spines["top"].set_visible(False)
            ax2.spines["left"].set_visible(False)
            ax2.spines["right"].set_color(COLORS["mid_gray"])
            ax2.spines["bottom"].set_visible(False)
            gx = [gv[0] for gv in growth_vals]
            gy = [gv[1] for gv in growth_vals]
            ax2.plot(gx, gy, color=COLORS["red"], linewidth=2, marker="o",
                     markersize=5, zorder=4, label="YoY Growth %")
            ax2.set_ylabel("YoY Growth %", fontsize=LABEL_FONTSIZE, color=COLORS["red"])
            ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
            ax2.tick_params(axis="y", colors=COLORS["red"], labelsize=LABEL_FONTSIZE)
            ax2.yaxis.grid(False)
            ax2.legend(loc="upper left", fontsize=9, framealpha=0.9)

    # Multi-line mode (series dict)
    elif series and not values:
        for idx, (name, vals) in enumerate(series.items()):
            if len(vals) != len(periods):
                _error(f"Series '{name}' length ({len(vals)}) != periods length ({len(periods)}).")
            color = COLOR_CYCLE[idx % len(COLOR_CYCLE)]
            pct_vals = [v * 100 if abs(v) <= 1 else v for v in vals]
            ax1.plot(x, pct_vals, color=color, linewidth=2, marker="o",
                    markersize=5, label=name, zorder=3)
        ax1.set_ylabel(label, fontsize=LABEL_FONTSIZE, color=COLORS["dark_gray"])
        ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
        ax1.legend(loc="best", fontsize=9, framealpha=0.9)

    # Combo mode (bars + lines)
    else:
        if len(periods) != len(values):
            _error("time-series: 'periods' and 'values' must be equal length.")
        ax1.bar(x, values, color=COLORS["steel_blue"], width=0.6, zorder=3, alpha=0.7)
        ax1.set_ylabel(label, fontsize=LABEL_FONTSIZE, color=COLORS["dark_gray"])
        ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _format_number(v)))

        ax2 = ax1.twinx()
        ax2.spines["top"].set_visible(False)
        ax2.spines["left"].set_visible(False)
        ax2.spines["right"].set_color(COLORS["mid_gray"])
        for idx, (name, vals) in enumerate(series.items()):
            color = COLOR_CYCLE[(idx + 1) % len(COLOR_CYCLE)]
            ax2.plot(x, vals, color=color, linewidth=2, marker="o",
                    markersize=5, label=name, zorder=4)
        ax2.set_ylabel("Overlay", fontsize=LABEL_FONTSIZE, color=COLORS["dark_gray"])
        ax2.yaxis.grid(False)
        ax2.legend(loc="upper left", fontsize=9, framealpha=0.9)

    ax1.set_xticks(x)
    ax1.set_xticklabels(periods, rotation=45, ha="right", fontsize=LABEL_FONTSIZE)

    _save(fig, output_path)


def chart_waterfall(data, output_path):
    """Waterfall / bridge chart. Shows incremental steps from a base to a total.

    Data format:
    {
        "labels": ["Base Revenue", "+Organic", "+Acquisitions", "-FX Impact", "Total Revenue"],
        "values": [100, 15, 8, -3, 120],
        "is_total": [true, false, false, false, true],
        "title": "Revenue Bridge ($M)"
    }
    """
    labels = data.get("labels")
    values = data.get("values")
    is_total = data.get("is_total", [False] * len(values) if values else [])
    title = data.get("title", "Waterfall")

    if not labels or not values or len(labels) != len(values):
        _error("waterfall requires 'labels' and 'values' of equal length.")
    if len(is_total) != len(values):
        is_total = [False] * len(values)
        is_total[0] = True
        is_total[-1] = True

    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    _apply_base_style(ax, title)

    n = len(values)
    x = np.arange(n)

    # Compute running cumulative for bar positioning
    cumulative = 0
    bottoms = []
    bar_values = []
    bar_colors = []

    for i in range(n):
        if is_total[i]:
            bottoms.append(0)
            bar_values.append(values[i])
            bar_colors.append(COLORS["navy"])
            cumulative = values[i]
        else:
            if values[i] >= 0:
                bottoms.append(cumulative)
                bar_values.append(values[i])
                bar_colors.append(COLORS["green"])
                cumulative += values[i]
            else:
                cumulative += values[i]
                bottoms.append(cumulative)
                bar_values.append(abs(values[i]))
                bar_colors.append(COLORS["red"])

    ax.bar(x, bar_values, bottom=bottoms, color=bar_colors, width=0.6, zorder=3,
           edgecolor="white", linewidth=0.5)

    # Value labels on bars
    for i in range(n):
        y_pos = bottoms[i] + bar_values[i]
        prefix = "" if is_total[i] else ("+" if values[i] >= 0 else "")
        ax.text(i, y_pos + (max(values) * 0.02), f"{prefix}{_format_number(values[i])}",
                ha="center", va="bottom", fontsize=9, fontweight="bold",
                color=COLORS["near_black"])

    # Connector lines between bars
    running = 0
    for i in range(n - 1):
        if is_total[i]:
            running = values[i]
        else:
            running += values[i]
        if not is_total[i + 1]:
            ax.plot([i + 0.3, i + 0.7], [running, running],
                    color=COLORS["dark_gray"], linewidth=0.8, linestyle="--", zorder=2)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=LABEL_FONTSIZE)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _format_number(v)))

    _save(fig, output_path)


def chart_football_field(data, output_path):
    """Football field chart — horizontal range bars for valuation methodologies.

    Data format:
    {
        "methodologies": ["DCF", "P/E Comps", "EV/EBITDA Comps", "Precedent Txns", "52W Range"],
        "low": [180, 170, 175, 190, 165],
        "high": [240, 220, 230, 250, 245],
        "mid": [210, 195, 202, 220, 205],
        "current_price": 200,
        "title": "Valuation Football Field"
    }
    """
    methodologies = data.get("methodologies")
    low = data.get("low")
    high = data.get("high")
    mid = data.get("mid")
    current_price = data.get("current_price")
    title = data.get("title", "Valuation Football Field")

    if not methodologies or not low or not high:
        _error("football-field requires 'methodologies', 'low', and 'high'.")
    n = len(methodologies)
    if len(low) != n or len(high) != n:
        _error("football-field: all arrays must be the same length.")

    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    ax.set_facecolor("white")
    fig.set_facecolor("white")
    ax.xaxis.grid(True, color=COLORS["mid_gray"], linewidth=0.5)
    ax.yaxis.grid(False)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLORS["mid_gray"])
    ax.spines["bottom"].set_color(COLORS["mid_gray"])

    y = np.arange(n)
    bar_height = 0.4
    colors = [COLORS["navy"], COLORS["steel_blue"], COLORS["gold"],
              COLORS["dark_gray"], COLORS["green"], COLORS["red"]]

    for i in range(n):
        color = colors[i % len(colors)]
        width = high[i] - low[i]
        ax.barh(y[i], width, left=low[i], height=bar_height,
                color=color, alpha=0.7, zorder=3, edgecolor="white")
        # Low/High labels
        ax.text(low[i] - 2, y[i], f"${low[i]:,.0f}", ha="right", va="center",
                fontsize=9, color=COLORS["dark_gray"])
        ax.text(high[i] + 2, y[i], f"${high[i]:,.0f}", ha="left", va="center",
                fontsize=9, color=COLORS["dark_gray"])
        # Mid point marker
        if mid and i < len(mid):
            ax.plot(mid[i], y[i], marker="D", color="white", markersize=6,
                    zorder=5, markeredgecolor=COLORS["near_black"], markeredgewidth=1)

    # Current price line
    if current_price is not None:
        ax.axvline(x=current_price, color=COLORS["red"], linewidth=2,
                   linestyle="--", zorder=4, label=f"Current: ${current_price:,.0f}")
        ax.legend(loc="upper right", fontsize=10, framealpha=0.9)

    ax.set_yticks(y)
    ax.set_yticklabels(methodologies, fontsize=LABEL_FONTSIZE, color=COLORS["near_black"])
    ax.set_xlabel("Implied Share Price ($)", fontsize=LABEL_FONTSIZE, color=COLORS["dark_gray"])
    ax.set_title(title, fontsize=TITLE_FONTSIZE, fontweight="bold",
                 color=COLORS["navy"], pad=12)
    ax.tick_params(labelsize=LABEL_FONTSIZE, colors=COLORS["dark_gray"])

    _save(fig, output_path)


def chart_pie(data, output_path):
    """Pie chart for segment breakdown."""
    segments = data.get("segments")
    title = data.get("title", "Segment Breakdown")
    if not segments:
        _error("pie requires 'segments' dict.")

    labels = list(segments.keys())
    sizes = list(segments.values())
    colors = COLOR_CYCLE[:len(labels)]
    while len(colors) < len(labels):
        colors.extend(COLOR_CYCLE)
    colors = colors[:len(labels)]

    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    ax.set_facecolor("white")
    fig.set_facecolor("white")

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.1f%%",
        startangle=90, pctdistance=0.75,
        textprops={"fontsize": LABEL_FONTSIZE, "color": COLORS["near_black"]},
    )
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    ax.set_title(title, fontsize=TITLE_FONTSIZE,
                 fontweight="bold", color=COLORS["navy"], pad=12)

    _save(fig, output_path)


def chart_scenario_bar(data, output_path):
    """Grouped bar chart for bull/base/bear scenario comparison."""
    metrics = data.get("metrics")
    bull = data.get("bull")
    base = data.get("base")
    bear = data.get("bear")
    if not metrics or not bull or not base or not bear:
        _error("scenario-bar requires 'metrics', 'bull', 'base', 'bear'.")
    if not (len(metrics) == len(bull) == len(base) == len(bear)):
        _error("scenario-bar: all arrays must be the same length.")

    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    _apply_base_style(ax, "Scenario Analysis: Bull / Base / Bear")

    x = np.arange(len(metrics))
    width = 0.25

    ax.bar(x - width, bull, width, color=COLORS["green"], label="Bull", zorder=3)
    ax.bar(x, base, width, color=COLORS["steel_blue"], label="Base", zorder=3)
    ax.bar(x + width, bear, width, color=COLORS["red"], label="Bear", zorder=3)

    # Value labels on bars
    for offset, vals, color in [(-width, bull, COLORS["green"]),
                                 (0, base, COLORS["steel_blue"]),
                                 (width, bear, COLORS["red"])]:
        for i, v in enumerate(vals):
            ax.text(i + offset, v + (max(max(bull), max(base), max(bear)) * 0.02),
                    _format_number(v), ha="center", va="bottom",
                    fontsize=8, color=color, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=LABEL_FONTSIZE)
    ax.set_ylabel("Value", fontsize=LABEL_FONTSIZE, color=COLORS["dark_gray"])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _format_number(v)))
    ax.legend(fontsize=9, framealpha=0.9)

    _save(fig, output_path)


def chart_dcf_sensitivity(data, output_path):
    """Heatmap for DCF price sensitivity (WACC vs terminal growth)."""
    wacc_values = data.get("wacc_values")
    growth_values = data.get("growth_values")
    prices = data.get("prices")
    current_price = data.get("current_price")
    if not wacc_values or not growth_values or not prices:
        _error("dcf-sensitivity requires 'wacc_values', 'growth_values', 'prices'.")
    if current_price is None:
        _error("dcf-sensitivity requires 'current_price'.")

    prices_arr = np.array(prices, dtype=float)
    if prices_arr.shape != (len(growth_values), len(wacc_values)):
        _error(f"prices shape {prices_arr.shape} does not match "
               f"({len(growth_values)}, {len(wacc_values)}).")

    fig, ax = plt.subplots(figsize=HEATMAP_FIGSIZE)
    ax.set_facecolor("white")
    fig.set_facecolor("white")

    from matplotlib.colors import LinearSegmentedColormap

    norm_prices = prices_arr - current_price
    max_abs = max(abs(norm_prices.min()), abs(norm_prices.max())) or 1
    normalized = norm_prices / max_abs

    cmap = LinearSegmentedColormap.from_list(
        "dcf", [COLORS["red"], "#FFFFFF", COLORS["green"]]
    )

    im = ax.imshow(normalized, cmap=cmap, vmin=-1, vmax=1, aspect="auto")

    ax.set_xticks(np.arange(len(wacc_values)))
    ax.set_xticklabels([f"{w:.1f}%" for w in wacc_values], fontsize=LABEL_FONTSIZE)
    ax.set_yticks(np.arange(len(growth_values)))
    ax.set_yticklabels([f"{g:.1f}%" for g in growth_values], fontsize=LABEL_FONTSIZE)
    ax.set_xlabel("WACC", fontsize=LABEL_FONTSIZE, color=COLORS["dark_gray"])
    ax.set_ylabel("Terminal Growth Rate", fontsize=LABEL_FONTSIZE, color=COLORS["dark_gray"])
    ax.set_title(f"DCF Sensitivity \u2014 Current Price: ${current_price:,.0f}",
                 fontsize=TITLE_FONTSIZE, fontweight="bold",
                 color=COLORS["navy"], pad=12)

    for i in range(len(growth_values)):
        for j in range(len(wacc_values)):
            price_val = prices_arr[i, j]
            text_color = "white" if abs(normalized[i, j]) > 0.6 else COLORS["near_black"]
            ax.text(j, i, f"${price_val:,.0f}", ha="center", va="center",
                    fontsize=9, fontweight="bold", color=text_color)

    ax.set_xticks(np.arange(len(wacc_values) + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(len(growth_values) + 1) - 0.5, minor=True)
    ax.grid(which="minor", color=COLORS["mid_gray"], linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    _save(fig, output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

CHART_TYPES = {
    "time-series": chart_time_series,
    "waterfall": chart_waterfall,
    "football-field": chart_football_field,
    "pie": chart_pie,
    "scenario-bar": chart_scenario_bar,
    "dcf-sensitivity": chart_dcf_sensitivity,
    # Legacy aliases
    "revenue-trend": chart_time_series,
    "margin-trend": chart_time_series,
    "eps-trend": chart_time_series,
    "segment-pie": chart_pie,
}


def main():
    parser = argparse.ArgumentParser(
        description="Generate professional financial charts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "chart_type",
        choices=sorted(set(CHART_TYPES.keys())),
        help="Type of chart to generate.",
    )
    data_group = parser.add_mutually_exclusive_group(required=True)
    data_group.add_argument(
        "--data",
        type=str,
        help="Inline JSON data string.",
    )
    data_group.add_argument(
        "--data-file",
        type=str,
        help="Path to a JSON file containing chart data.",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path (PNG). Defaults to reports/.charts/<type>_<timestamp>.png",
    )

    args = parser.parse_args()

    # Parse data
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as exc:
            _error(f"Invalid JSON in --data: {exc}")
    else:
        try:
            with open(args.data_file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            _error(f"Data file not found: {args.data_file}")
        except json.JSONDecodeError as exc:
            _error(f"Invalid JSON in data file: {exc}")

    # Resolve output path
    output_path = args.output or _default_output_path(args.chart_type)

    # Generate chart
    chart_fn = CHART_TYPES[args.chart_type]
    try:
        chart_fn(data, output_path)
    except Exception as exc:
        _error(f"Chart generation failed: {exc}")


if __name__ == "__main__":
    main()
