#!/usr/bin/env python3
"""
Projection Engine — CLI tool that takes historical financial data and produces
forward projections using guidance-aware, seasonally-adjusted methodology.

Usage:
    python infra/projection_engine.py --context input.json --output projections.json
    python infra/projection_engine.py --context input.json  # prints to stdout
"""

import argparse
import json
import statistics
import sys
from datetime import date


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_period(period_str):
    """Parse '2024Q3' into (year, quarter)."""
    year = int(period_str[:4])
    quarter = int(period_str[-1])
    return year, quarter


def next_period(year, quarter):
    """Return the next (year, quarter) after the given one."""
    if quarter == 4:
        return year + 1, 1
    return year, quarter + 1


def format_period(year, quarter):
    """Format (year, quarter) back to '2024Q3'."""
    return f"{year}Q{quarter}"


def advance_periods(last_period_str, n):
    """Generate n period labels after last_period_str."""
    y, q = parse_period(last_period_str)
    periods = []
    for _ in range(n):
        y, q = next_period(y, q)
        periods.append(format_period(y, q))
    return periods


def safe_div(a, b):
    """Division returning None when b is zero or either operand is None."""
    if a is None or b is None or b == 0:
        return None
    return a / b


def trailing_avg(series, n):
    """Average of the last n non-None values in a list."""
    vals = [v for v in series[-n:] if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)


def trailing_vals(series, n):
    """Last n values from series, filtering None."""
    return [v for v in series[-n:] if v is not None]


def is_monotonic(values):
    """Check if a sequence is monotonically increasing or decreasing.
    Returns +1 for increasing, -1 for decreasing, 0 for neither.
    Requires at least 3 values.
    """
    if len(values) < 3:
        return 0
    diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]
    if all(d > 0 for d in diffs):
        return 1
    if all(d < 0 for d in diffs):
        return -1
    return 0


def compute_seasonal_pattern(revenue, n_quarters=4):
    """Compute each quarter's share of trailing annual revenue.

    Returns a list of n_quarters fractions that sum to ~1.0, representing the
    seasonal weighting of each quarter (most recent n_quarters).
    """
    tail = trailing_vals(revenue, n_quarters)
    if len(tail) < n_quarters:
        return [1.0 / n_quarters] * n_quarters
    total = sum(tail)
    if total == 0:
        return [1.0 / n_quarters] * n_quarters
    return [v / total for v in tail]


def qoq_growth_rates(series):
    """Compute list of quarter-over-quarter growth rates, skipping None."""
    rates = []
    for i in range(1, len(series)):
        if series[i] is not None and series[i - 1] is not None and series[i - 1] != 0:
            rates.append(series[i] / series[i - 1] - 1.0)
    return rates


def yoy_growth_rates(series):
    """Compute list of year-over-year growth rates (i vs i-4), skipping None."""
    rates = []
    for i in range(4, len(series)):
        if series[i] is not None and series[i - 4] is not None and series[i - 4] != 0:
            rates.append(series[i] / series[i - 4] - 1.0)
    return rates


# ---------------------------------------------------------------------------
# Projection functions
# ---------------------------------------------------------------------------

def project_revenue(historical, guidance, n_quarters, long_term_growth, decay):
    """Project revenue using guidance growth, geometric decay, and seasonality.

    Methodology:
    - If guidance revenue_growth provided, use it for Q+1.
    - Growth decays geometrically toward long_term_growth.
    - Seasonal pattern from trailing 4Q is applied.
    """
    revenue = historical.get("revenue")
    if not revenue or len(revenue) < 4:
        return None, "insufficient data"

    # Compute seasonal pattern from trailing 4 quarters
    seasonal = compute_seasonal_pattern(revenue, 4)

    # Determine starting growth rate
    yoy_rates = yoy_growth_rates(revenue)
    guidance_growth = guidance.get("revenue_growth") if guidance else None

    if guidance_growth is not None:
        initial_growth = guidance_growth
        method = f"guidance growth ({guidance_growth:.1%}) + geometric decay to {long_term_growth:.0%} LT growth, seasonal adjustment"
    elif yoy_rates:
        initial_growth = yoy_rates[-1]
        method = f"trailing YoY growth ({initial_growth:.1%}) + geometric decay to {long_term_growth:.0%} LT growth, seasonal adjustment"
    else:
        initial_growth = long_term_growth
        method = f"long-term growth ({long_term_growth:.0%}), seasonal adjustment"

    # Compute trailing annual revenue for seasonal base
    trailing_annual = sum(trailing_vals(revenue, 4))

    projected = []
    for t in range(n_quarters):
        # Blended growth rate: decays from initial toward long-term
        growth_rate = initial_growth * (decay ** (t + 1)) + long_term_growth * (1 - decay ** (t + 1))

        # Which seasonal slot does this quarter correspond to?
        # The seasonal pattern is aligned to the last 4 quarters.
        # Quarter index within the 4Q cycle
        season_idx = t % 4

        # For the first 4 projected quarters, apply growth to trailing annual
        # and distribute by seasonal pattern.
        # For subsequent years, apply growth to the prior projected annual.
        year_idx = t // 4
        if year_idx == 0:
            base_annual = trailing_annual
        else:
            # Sum the 4 quarters from the prior projected year
            prior_start = (year_idx - 1) * 4
            prior_end = year_idx * 4
            base_annual = sum(projected[prior_start:prior_end])

        # Cumulative growth from the base year
        if year_idx == 0:
            # For year 0, we apply 1 year of growth to trailing annual
            cumulative_factor = 1 + growth_rate
        else:
            # Already folded prior years into base_annual via the loop,
            # so just apply this year's growth
            cumulative_factor = 1 + growth_rate

        annual_projection = base_annual * cumulative_factor
        quarterly_revenue = annual_projection * seasonal[season_idx]
        projected.append(round(quarterly_revenue))

    return projected, method


def project_gross_margin(historical, guidance, n_quarters):
    """Project gross margin using guidance midpoint and mean reversion.

    If a clear 3Q+ monotonic trend exists, extrapolate with 50% dampening.
    """
    revenue = historical.get("revenue")
    cost_of_revenue = historical.get("cost_of_revenue")

    if not revenue or not cost_of_revenue:
        return None, "insufficient data"

    # Compute historical gross margins
    margins = []
    for r, c in zip(revenue, cost_of_revenue):
        if r is not None and c is not None and r != 0:
            margins.append(1 - c / r)
        else:
            margins.append(None)

    valid_margins = [m for m in margins if m is not None]
    if len(valid_margins) < 2:
        return None, "insufficient data"

    trailing_4q = trailing_vals(margins, 4)
    trailing_mean = statistics.mean(trailing_4q) if trailing_4q else valid_margins[-1]

    # Determine starting value
    guidance_gm_low = guidance.get("gross_margin_low") if guidance else None
    guidance_gm_high = guidance.get("gross_margin_high") if guidance else None

    if guidance_gm_low is not None and guidance_gm_high is not None:
        start_margin = (guidance_gm_low + guidance_gm_high) / 2
        method = f"guidance midpoint ({start_margin:.1%}) mean-reverting to trailing avg ({trailing_mean:.1%})"
    elif guidance_gm_low is not None:
        start_margin = guidance_gm_low
        method = f"guidance ({start_margin:.1%}) mean-reverting to trailing avg ({trailing_mean:.1%})"
    elif guidance_gm_high is not None:
        start_margin = guidance_gm_high
        method = f"guidance ({start_margin:.1%}) mean-reverting to trailing avg ({trailing_mean:.1%})"
    else:
        start_margin = valid_margins[-1]
        method = f"trailing margin ({start_margin:.1%}) mean-reverting to trailing avg ({trailing_mean:.1%})"

    # Check for monotonic trend in last 3+ quarters
    trend_window = trailing_vals(margins, min(6, len(valid_margins)))
    trend_dir = is_monotonic(trend_window[-3:]) if len(trend_window) >= 3 else 0

    if trend_dir != 0:
        # Compute average quarterly change over the trend window
        trend_vals = trend_window[-3:]
        avg_delta = (trend_vals[-1] - trend_vals[0]) / (len(trend_vals) - 1)
        method += f", trend-adjusted ({avg_delta:+.3%}/Q with 50% dampening)"
    else:
        avg_delta = 0

    projected = []
    current = start_margin
    dampening = 0.5

    for t in range(n_quarters):
        if t == 0:
            projected.append(current)
        else:
            # Mean reversion toward trailing average
            reversion_pull = (trailing_mean - current) * 0.15

            # Trend component with dampening
            trend_component = avg_delta * (dampening ** t)

            current = current + reversion_pull + trend_component
            projected.append(current)

    # Round to 4 decimal places
    projected = [round(m, 4) for m in projected]
    return projected, method


def project_operating_margin(historical, projected_revenue, n_quarters):
    """Project operating margin with mean reversion and operating leverage.

    If revenue is growing, op margin expands slightly (0.1x revenue growth).
    """
    revenue = historical.get("revenue")
    opex = historical.get("operating_expenses")

    if not revenue or not opex:
        return None, "insufficient data"

    # Compute historical operating margin = 1 - opex/revenue
    # Note: this is opex-only margin contribution; gross margin is separate.
    # Operating margin = (revenue - COGS - opex) / revenue
    cost_of_revenue = historical.get("cost_of_revenue")
    margins = []
    for i in range(len(revenue)):
        r = revenue[i]
        o = opex[i]
        c = cost_of_revenue[i] if cost_of_revenue and i < len(cost_of_revenue) else None
        if r is not None and o is not None and r != 0:
            if c is not None:
                margins.append((r - c - o) / r)
            else:
                # Without COGS, approximate as 1 - opex/revenue
                margins.append(1 - o / r)
        else:
            margins.append(None)

    valid_margins = [m for m in margins if m is not None]
    if len(valid_margins) < 2:
        return None, "insufficient data"

    trailing_4q = trailing_vals(margins, 4)
    trailing_mean = statistics.mean(trailing_4q) if trailing_4q else valid_margins[-1]
    current = valid_margins[-1]

    # Compute revenue growth for operating leverage
    rev_growth = 0
    if projected_revenue and len(projected_revenue) >= 2 and revenue:
        last_hist_rev = revenue[-1]
        if last_hist_rev and last_hist_rev != 0:
            rev_growth = (projected_revenue[0] / last_hist_rev) - 1

    has_cogs = cost_of_revenue is not None
    method_base = "operating income / revenue" if has_cogs else "1 - opex/revenue (no COGS)"
    method = f"{method_base}, mean-reverting to trailing avg ({trailing_mean:.1%})"
    if rev_growth != 0:
        method += f", operating leverage ({0.1 * rev_growth:+.2%}/Q)"

    projected = []
    for t in range(n_quarters):
        # Mean reversion
        reversion_pull = (trailing_mean - current) * 0.15

        # Operating leverage: margin expands when revenue grows
        leverage_effect = 0.1 * rev_growth

        current = current + reversion_pull + leverage_effect
        projected.append(round(current, 4))

    return projected, method


def project_capex(historical, guidance, projected_revenue, n_quarters, periods):
    """Project CapEx using guidance range or trailing % of revenue."""
    capex = historical.get("capex")

    guidance_range = guidance.get("capex_range") if guidance else None

    if guidance_range and len(guidance_range) == 2:
        # Spread guidance evenly across next 4Q, then revert to % of revenue
        annual_capex = (guidance_range[0] + guidance_range[1]) / 2

        # Check for seasonal pattern in historical capex
        if capex and len(capex) >= 4:
            seasonal = compute_seasonal_pattern(capex, 4)
        else:
            seasonal = [0.25] * 4

        projected = []
        for t in range(n_quarters):
            if t < 4:
                # Apply guidance with seasonal distribution
                q_capex = annual_capex * seasonal[t % 4]
                projected.append(round(q_capex))
            else:
                # Revert to % of revenue
                if projected_revenue and capex and len(capex) >= 4:
                    rev = historical.get("revenue", [])
                    if rev and len(rev) >= 4:
                        trailing_rev = sum(trailing_vals(rev, 4))
                        trailing_capex = sum(trailing_vals(capex, 4))
                        if trailing_rev != 0:
                            ratio = trailing_capex / trailing_rev
                            projected.append(round(projected_revenue[t] * ratio))
                        else:
                            projected.append(round(annual_capex / 4))
                    else:
                        projected.append(round(annual_capex / 4))
                else:
                    projected.append(round(annual_capex / 4))

        method = f"guidance range ({guidance_range[0]:,.0f}-{guidance_range[1]:,.0f}) for 4Q, then trailing % of revenue"
        return projected, method

    # No guidance: use trailing capex-as-%-of-revenue
    if not capex or not projected_revenue:
        return None, "insufficient data"

    revenue = historical.get("revenue", [])
    if not revenue or len(revenue) < 4 or len(capex) < 4:
        return None, "insufficient data"

    trailing_rev = sum(trailing_vals(revenue, 4))
    trailing_capex_total = sum(trailing_vals(capex, 4))
    if trailing_rev == 0:
        return None, "insufficient data"

    ratio = trailing_capex_total / trailing_rev

    projected = []
    for t in range(n_quarters):
        q_capex = projected_revenue[t] * ratio
        projected.append(round(q_capex))

    method = f"trailing CapEx/Revenue ratio ({ratio:.1%}) applied to projected revenue"
    return projected, method


def project_depreciation(historical, projected_revenue, n_quarters):
    """Project D&A as % of PP&E or revenue (whichever is more stable)."""
    depreciation = historical.get("depreciation")
    if not depreciation:
        return None, "insufficient data"

    revenue = historical.get("revenue")
    ppe = historical.get("pp_and_e")

    # Compute D&A as % of PP&E
    ppe_ratios = []
    if ppe:
        for d_val, p_val in zip(depreciation, ppe):
            if d_val is not None and p_val is not None and p_val != 0:
                ppe_ratios.append(d_val / p_val)

    # Compute D&A as % of revenue
    rev_ratios = []
    if revenue:
        for d_val, r_val in zip(depreciation, revenue):
            if d_val is not None and r_val is not None and r_val != 0:
                rev_ratios.append(d_val / r_val)

    # Pick whichever has lower coefficient of variation (more stable)
    def cv(vals):
        if len(vals) < 2:
            return float("inf")
        mean = statistics.mean(vals)
        if mean == 0:
            return float("inf")
        return statistics.stdev(vals) / abs(mean)

    use_ppe = False
    if ppe_ratios and rev_ratios:
        if cv(ppe_ratios) < cv(rev_ratios):
            use_ppe = True
    elif ppe_ratios:
        use_ppe = True

    if use_ppe and ppe_ratios:
        ratio = statistics.mean(ppe_ratios[-4:])
        # Project PP&E simply: last value + projected capex - projected depreciation
        # Circular, so just use trailing ratio * last PP&E with slight growth
        last_ppe = [v for v in ppe if v is not None][-1]
        projected = []
        current_ppe = last_ppe
        for t in range(n_quarters):
            dep = round(current_ppe * ratio)
            projected.append(dep)
            # Rough PP&E roll-forward: assume capex ~ depreciation (steady state)
            # so PP&E stays roughly flat
        method = f"D&A as % of PP&E ({ratio:.1%}), trailing avg"
        return projected, method

    if rev_ratios and projected_revenue:
        ratio = statistics.mean(rev_ratios[-4:])
        projected = [round(projected_revenue[t] * ratio) for t in range(n_quarters)]
        method = f"D&A as % of revenue ({ratio:.1%}), trailing avg"
        return projected, method

    return None, "insufficient data"


def project_tax_rate(historical, guidance, n_quarters):
    """Use guidance tax rate if available, else trailing effective rate."""
    guidance_rate = guidance.get("tax_rate") if guidance else None

    if guidance_rate is not None:
        projected = [guidance_rate] * n_quarters
        method = f"guidance tax rate ({guidance_rate:.1%})"
        return projected, method

    # Compute effective tax rate from net_income and operating data
    revenue = historical.get("revenue")
    cost_of_revenue = historical.get("cost_of_revenue")
    opex = historical.get("operating_expenses")
    net_income = historical.get("net_income")

    if not net_income or not revenue:
        return None, "insufficient data"

    # Approximate pre-tax income and compute effective rate
    rates = []
    for i in range(len(net_income)):
        r = revenue[i] if i < len(revenue) else None
        c = cost_of_revenue[i] if cost_of_revenue and i < len(cost_of_revenue) else None
        o = opex[i] if opex and i < len(opex) else None
        ni = net_income[i]

        if r is None or ni is None or r == 0:
            continue

        # Approximate pre-tax income
        if c is not None and o is not None:
            pretax = r - c - o
        else:
            continue

        if pretax <= 0 or ni <= 0:
            continue

        eff_rate = 1 - (ni / pretax)
        if 0 < eff_rate < 0.5:  # Sanity check
            rates.append(eff_rate)

    if not rates:
        return None, "insufficient data"

    trailing = statistics.mean(rates[-4:]) if len(rates) >= 4 else statistics.mean(rates)
    projected = [round(trailing, 4)] * n_quarters
    method = f"trailing effective tax rate ({trailing:.1%})"
    return projected, method


def project_shares(historical, n_quarters):
    """Project share count using trailing buyback rate."""
    shares = historical.get("shares_outstanding")
    if not shares:
        return None, "insufficient data"

    valid = [s for s in shares if s is not None]
    if len(valid) < 2:
        return None, "insufficient data"

    # Compute average QoQ change rate
    qoq_rates = []
    for i in range(1, len(valid)):
        if valid[i - 1] != 0:
            qoq_rates.append(valid[i] / valid[i - 1] - 1)

    if not qoq_rates:
        return None, "insufficient data"

    # Use trailing 4Q average rate
    trailing_rate = statistics.mean(qoq_rates[-4:]) if len(qoq_rates) >= 4 else statistics.mean(qoq_rates)

    current = valid[-1]
    projected = []
    for t in range(n_quarters):
        current = current * (1 + trailing_rate)
        projected.append(round(current))

    direction = "buyback" if trailing_rate < 0 else "dilution"
    method = f"trailing QoQ {direction} rate ({trailing_rate:+.3%}/Q)"
    return projected, method


# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------

def run_projection(context):
    """Run the full projection pipeline given a context dict.

    Returns the output dict with projections and assumptions.
    """
    ticker = context.get("ticker", "UNKNOWN")
    n_quarters = context.get("projection_quarters", 8)
    historical = context.get("historical", {})
    guidance = context.get("guidance", {})
    periods_hist = historical.get("periods", [])

    long_term_growth = context.get("long_term_growth", 0.03)
    decay_factor = context.get("decay_factor", 0.85)

    if not periods_hist:
        raise ValueError("historical.periods is required")

    # Generate projection period labels
    last_period = periods_hist[-1]
    proj_periods = advance_periods(last_period, n_quarters)

    methods = {}
    projections = {"periods": proj_periods}

    # 1. Revenue
    proj_revenue, rev_method = project_revenue(
        historical, guidance, n_quarters, long_term_growth, decay_factor
    )
    if proj_revenue is not None:
        projections["revenue"] = proj_revenue
        methods["revenue"] = rev_method

    # 2. Gross Margin & Gross Profit
    proj_gm, gm_method = project_gross_margin(historical, guidance, n_quarters)
    if proj_gm is not None:
        projections["gross_margin"] = proj_gm
        methods["gross_margin"] = gm_method

        if proj_revenue is not None:
            projections["gross_profit"] = [
                round(proj_revenue[i] * proj_gm[i]) for i in range(n_quarters)
            ]

    # 3. Operating Margin & Operating Income
    proj_om, om_method = project_operating_margin(
        historical, proj_revenue, n_quarters
    )
    if proj_om is not None:
        projections["operating_margin"] = proj_om
        methods["operating_margin"] = om_method

        if proj_revenue is not None:
            projections["operating_income"] = [
                round(proj_revenue[i] * proj_om[i]) for i in range(n_quarters)
            ]

    # 4. CapEx
    proj_capex, capex_method = project_capex(
        historical, guidance, proj_revenue, n_quarters, proj_periods
    )
    if proj_capex is not None:
        projections["capex"] = proj_capex
        methods["capex"] = capex_method

    # 5. D&A
    proj_dep, dep_method = project_depreciation(historical, proj_revenue, n_quarters)
    if proj_dep is not None:
        projections["depreciation"] = proj_dep
        methods["depreciation"] = dep_method

    # 6. Tax Rate
    proj_tax, tax_method = project_tax_rate(historical, guidance, n_quarters)
    if proj_tax is not None:
        projections["tax_rate"] = proj_tax if any(t != proj_tax[0] for t in proj_tax) else proj_tax
        methods["tax_rate"] = tax_method

    # 7. Share Count
    proj_shares, shares_method = project_shares(historical, n_quarters)
    if proj_shares is not None:
        projections["shares_outstanding"] = proj_shares
        methods["shares_outstanding"] = shares_method

    # Derived metrics
    # Net Income = operating_income * (1 - tax_rate)
    if "operating_income" in projections and proj_tax is not None:
        projections["net_income"] = [
            round(projections["operating_income"][i] * (1 - proj_tax[i]))
            for i in range(n_quarters)
        ]
        methods["net_income"] = "operating income * (1 - tax rate)"

        # Net Margin
        if proj_revenue is not None:
            projections["net_margin"] = [
                round(safe_div(projections["net_income"][i], proj_revenue[i]), 4)
                if proj_revenue[i] else None
                for i in range(n_quarters)
            ]

    # EPS = net_income / shares_outstanding
    if "net_income" in projections and "shares_outstanding" in projections:
        projections["eps"] = [
            round(safe_div(projections["net_income"][i], projections["shares_outstanding"][i]), 2)
            if projections["shares_outstanding"][i] else None
            for i in range(n_quarters)
        ]
        methods["eps"] = "net income / shares outstanding"

    # FCF = net_income + depreciation - capex (simplified)
    if "net_income" in projections:
        dep_vals = projections.get("depreciation")
        capex_vals = projections.get("capex")
        if dep_vals is not None or capex_vals is not None:
            fcf = []
            for i in range(n_quarters):
                ni = projections["net_income"][i]
                dep = dep_vals[i] if dep_vals else 0
                cap = capex_vals[i] if capex_vals else 0
                fcf.append(round(ni + dep - cap))
            projections["fcf"] = fcf
            methods["fcf"] = "net income + depreciation - capex"

    # Build output
    output = {
        "ticker": ticker,
        "generated_at": date.today().isoformat(),
        "projection_quarters": n_quarters,
        "assumptions": {
            "long_term_growth": long_term_growth,
            "decay_factor": decay_factor,
            "methods": methods,
        },
        "projections": projections,
    }

    return output


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Financial projection engine: takes historical data and produces forward projections."
    )
    parser.add_argument(
        "--context",
        required=True,
        help="Path to input JSON file with historical data and guidance.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to write output JSON. If omitted, prints to stdout.",
    )

    args = parser.parse_args()

    # Read input
    try:
        with open(args.context, "r") as f:
            context = json.load(f)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.context}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {args.context}: {e}", file=sys.stderr)
        sys.exit(1)

    # Run projection
    try:
        result = run_projection(context)
    except Exception as e:
        print(f"Error during projection: {e}", file=sys.stderr)
        sys.exit(1)

    # Output
    output_json = json.dumps(result, indent=2)

    if args.output:
        try:
            with open(args.output, "w") as f:
                f.write(output_json)
                f.write("\n")
            print(f"Projections written to {args.output}", file=sys.stderr)
        except IOError as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
