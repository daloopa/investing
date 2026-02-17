#!/usr/bin/env python3
"""
Professional financial chart generator CLI.

Usage:
    python infra/chart_generator.py {chart_type} --data '{json}' --output path.png
    python infra/chart_generator.py {chart_type} --data-file input.json --output path.png

Chart types:
    revenue-trend    Bar chart with YoY growth line overlay
    margin-trend     Multi-line chart for margin percentages
    segment-pie      Pie chart for segment breakdown
    segment-stack    Stacked bar chart over time
    eps-trend        Bar chart with YoY growth line overlay
    scenario-bar     Grouped bar for bull/base/bear scenarios
    dcf-sensitivity  Heatmap for DCF price sensitivity
    price-history    Stock price line with volume bars (uses yfinance)
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
# Style constants
# ---------------------------------------------------------------------------

COLORS = {
    "navy": "#1B2A4A",
    "steel_blue": "#4A90D9",
    "green": "#2ECC71",
    "red": "#E74C3C",
    "gray": "#95A5A6",
    "gold": "#F39C12",
}

COLOR_CYCLE = [
    COLORS["navy"],
    COLORS["steel_blue"],
    COLORS["green"],
    COLORS["gold"],
    COLORS["red"],
    COLORS["gray"],
]

DEFAULT_DPI = 150
DEFAULT_FIGSIZE = (10, 6)
HEATMAP_FIGSIZE = (10, 8)
DEFAULT_OUTPUT_DIR = "reports/.charts"

TITLE_FONTSIZE = 12
LABEL_FONTSIZE = 10


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_base_style(ax, title=None):
    """Apply consistent base styling to an axes object."""
    ax.set_facecolor("white")
    ax.figure.set_facecolor("white")
    ax.yaxis.grid(True, color="#E0E0E0", linewidth=0.5, linestyle="-")
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.tick_params(labelsize=LABEL_FONTSIZE, colors="#333333")
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

def chart_revenue_trend(data, output_path):
    """Bar chart of revenue with YoY growth line on secondary y-axis."""
    periods = data.get("periods")
    values = data.get("values")
    label = data.get("label", "Revenue ($M)")
    if not periods or not values or len(periods) != len(values):
        _error("revenue-trend requires 'periods' and 'values' of equal length.")

    fig, ax1 = plt.subplots(figsize=DEFAULT_FIGSIZE)
    _apply_base_style(ax1, label)

    x = np.arange(len(periods))
    ax1.bar(x, values, color=COLORS["steel_blue"], width=0.6, zorder=3)
    ax1.set_xticks(x)
    ax1.set_xticklabels(periods, rotation=45, ha="right", fontsize=LABEL_FONTSIZE)
    ax1.set_ylabel(label, fontsize=LABEL_FONTSIZE, color="#333333")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _format_number(v)))

    # YoY growth overlay
    growth = _compute_yoy_growth(values)
    growth_vals = [(i, g) for i, g in enumerate(growth) if g is not None]
    if growth_vals:
        ax2 = ax1.twinx()
        ax2.spines["top"].set_visible(False)
        ax2.spines["left"].set_visible(False)
        ax2.spines["right"].set_color("#CCCCCC")
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

    _save(fig, output_path)


def chart_margin_trend(data, output_path):
    """Multi-line chart for margin percentages over time."""
    periods = data.get("periods")
    series = data.get("series")
    if not periods or not series:
        _error("margin-trend requires 'periods' and 'series'.")

    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    _apply_base_style(ax, "Margin Trends")

    x = np.arange(len(periods))
    for idx, (name, vals) in enumerate(series.items()):
        if len(vals) != len(periods):
            _error(f"Series '{name}' length ({len(vals)}) != periods length ({len(periods)}).")
        color = COLOR_CYCLE[idx % len(COLOR_CYCLE)]
        pct_vals = [v * 100 if abs(v) <= 1 else v for v in vals]
        ax.plot(x, pct_vals, color=color, linewidth=2, marker="o",
                markersize=5, label=name, zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(periods, rotation=45, ha="right", fontsize=LABEL_FONTSIZE)
    ax.set_ylabel("Margin %", fontsize=LABEL_FONTSIZE, color="#333333")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.1f}%"))
    ax.legend(loc="best", fontsize=9, framealpha=0.9)

    _save(fig, output_path)


def chart_segment_pie(data, output_path):
    """Pie chart for segment breakdown."""
    segments = data.get("segments")
    if not segments:
        _error("segment-pie requires 'segments' dict.")

    labels = list(segments.keys())
    sizes = list(segments.values())
    colors = COLOR_CYCLE[:len(labels)]
    # Extend colors if needed
    while len(colors) < len(labels):
        colors.extend(COLOR_CYCLE)
    colors = colors[:len(labels)]

    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    ax.set_facecolor("white")
    fig.set_facecolor("white")

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.1f%%",
        startangle=90, pctdistance=0.75,
        textprops={"fontsize": LABEL_FONTSIZE, "color": "#333333"},
    )
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    ax.set_title("Segment Breakdown", fontsize=TITLE_FONTSIZE,
                 fontweight="bold", color=COLORS["navy"], pad=12)

    _save(fig, output_path)


def chart_segment_stack(data, output_path):
    """Stacked bar chart for segments over time."""
    periods = data.get("periods")
    segments = data.get("segments")
    if not periods or not segments:
        _error("segment-stack requires 'periods' and 'segments'.")

    fig, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)
    _apply_base_style(ax, "Segment Breakdown Over Time")

    x = np.arange(len(periods))
    bottom = np.zeros(len(periods))

    for idx, (name, vals) in enumerate(segments.items()):
        if len(vals) != len(periods):
            _error(f"Segment '{name}' length ({len(vals)}) != periods length ({len(periods)}).")
        color = COLOR_CYCLE[idx % len(COLOR_CYCLE)]
        arr = np.array(vals, dtype=float)
        ax.bar(x, arr, bottom=bottom, color=color, width=0.6,
               label=name, zorder=3)
        bottom += arr

    ax.set_xticks(x)
    ax.set_xticklabels(periods, rotation=45, ha="right", fontsize=LABEL_FONTSIZE)
    ax.set_ylabel("Value", fontsize=LABEL_FONTSIZE, color="#333333")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: _format_number(v)))
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=9,
              framealpha=0.9, borderaxespad=0)

    _save(fig, output_path)


def chart_eps_trend(data, output_path):
    """Bar chart of EPS with YoY growth line on secondary y-axis."""
    periods = data.get("periods")
    values = data.get("values")
    label = data.get("label", "EPS ($)")
    if not periods or not values or len(periods) != len(values):
        _error("eps-trend requires 'periods' and 'values' of equal length.")

    fig, ax1 = plt.subplots(figsize=DEFAULT_FIGSIZE)
    _apply_base_style(ax1, label)

    x = np.arange(len(periods))
    ax1.bar(x, values, color=COLORS["navy"], width=0.6, zorder=3)
    ax1.set_xticks(x)
    ax1.set_xticklabels(periods, rotation=45, ha="right", fontsize=LABEL_FONTSIZE)
    ax1.set_ylabel(label, fontsize=LABEL_FONTSIZE, color="#333333")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.2f}"))

    # YoY growth overlay
    growth = _compute_yoy_growth(values)
    growth_vals = [(i, g) for i, g in enumerate(growth) if g is not None]
    if growth_vals:
        ax2 = ax1.twinx()
        ax2.spines["top"].set_visible(False)
        ax2.spines["left"].set_visible(False)
        ax2.spines["right"].set_color("#CCCCCC")
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
    ax.set_ylabel("Value", fontsize=LABEL_FONTSIZE, color="#333333")
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

    # Build color array: green if above current price, red if below
    from matplotlib.colors import LinearSegmentedColormap

    # Normalize relative to current price
    norm_prices = prices_arr - current_price
    max_abs = max(abs(norm_prices.min()), abs(norm_prices.max())) or 1
    normalized = norm_prices / max_abs  # -1 to 1

    # Create custom colormap: red -> white -> green
    cmap = LinearSegmentedColormap.from_list(
        "dcf", [COLORS["red"], "#FFFFFF", COLORS["green"]]
    )

    im = ax.imshow(normalized, cmap=cmap, vmin=-1, vmax=1, aspect="auto")

    # Labels
    ax.set_xticks(np.arange(len(wacc_values)))
    ax.set_xticklabels([f"{w:.1f}%" for w in wacc_values], fontsize=LABEL_FONTSIZE)
    ax.set_yticks(np.arange(len(growth_values)))
    ax.set_yticklabels([f"{g:.1f}%" for g in growth_values], fontsize=LABEL_FONTSIZE)
    ax.set_xlabel("WACC", fontsize=LABEL_FONTSIZE, color="#333333")
    ax.set_ylabel("Terminal Growth Rate", fontsize=LABEL_FONTSIZE, color="#333333")
    ax.set_title(f"DCF Sensitivity — Current Price: ${current_price:,.0f}",
                 fontsize=TITLE_FONTSIZE, fontweight="bold",
                 color=COLORS["navy"], pad=12)

    # Annotate each cell with the price
    for i in range(len(growth_values)):
        for j in range(len(wacc_values)):
            price_val = prices_arr[i, j]
            text_color = "white" if abs(normalized[i, j]) > 0.6 else "#333333"
            ax.text(j, i, f"${price_val:,.0f}", ha="center", va="center",
                    fontsize=9, fontweight="bold", color=text_color)

    # Thin grid lines between cells
    ax.set_xticks(np.arange(len(wacc_values) + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(len(growth_values) + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="#E0E0E0", linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    _save(fig, output_path)


def chart_price_history(data, output_path):
    """Stock price line chart with volume bars. Fetches data via yfinance."""
    ticker = data.get("ticker")
    period = data.get("period", "2y")
    if not ticker:
        _error("price-history requires 'ticker'.")

    try:
        import yfinance as yf
    except ImportError:
        _error("yfinance is required for price-history. Install with: pip install yfinance")

    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    if hist.empty:
        _error(f"No price data returned for {ticker} over period '{period}'.")

    fig, (ax_price, ax_vol) = plt.subplots(
        2, 1, figsize=DEFAULT_FIGSIZE, sharex=True,
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.05}
    )
    fig.set_facecolor("white")

    dates = hist.index
    close = hist["Close"]
    volume = hist["Volume"]

    # Price line
    ax_price.plot(dates, close, color=COLORS["navy"], linewidth=1.5, zorder=3)
    ax_price.fill_between(dates, close, alpha=0.08, color=COLORS["steel_blue"])
    _apply_base_style(ax_price, f"{ticker.upper()} — Price History ({period})")
    ax_price.set_ylabel("Price ($)", fontsize=LABEL_FONTSIZE, color="#333333")
    ax_price.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}"))

    # Volume bars
    bar_colors = [COLORS["green"] if close.iloc[i] >= close.iloc[max(0, i - 1)]
                  else COLORS["red"] for i in range(len(close))]
    ax_vol.bar(dates, volume, color=bar_colors, alpha=0.6, width=1.5, zorder=3)
    _apply_base_style(ax_vol)
    ax_vol.set_ylabel("Volume", fontsize=LABEL_FONTSIZE, color="#333333")
    ax_vol.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"{v / 1e6:.0f}M" if v >= 1e6 else _format_number(v))
    )

    # Clean up x-axis
    fig.autofmt_xdate(rotation=30, ha="right")

    _save(fig, output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

CHART_TYPES = {
    "revenue-trend": chart_revenue_trend,
    "margin-trend": chart_margin_trend,
    "segment-pie": chart_segment_pie,
    "segment-stack": chart_segment_stack,
    "eps-trend": chart_eps_trend,
    "scenario-bar": chart_scenario_bar,
    "dcf-sensitivity": chart_dcf_sensitivity,
    "price-history": chart_price_history,
}


def main():
    parser = argparse.ArgumentParser(
        description="Generate professional financial charts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "chart_type",
        choices=sorted(CHART_TYPES.keys()),
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
