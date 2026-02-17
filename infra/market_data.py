#!/usr/bin/env python3
"""
CLI tool for fetching market data.

Usage:
    python infra/market_data.py quote AAPL
    python infra/market_data.py multiples AAPL
    python infra/market_data.py history AAPL --period 2y
    python infra/market_data.py peers AAPL MSFT GOOG
    python infra/market_data.py risk-free-rate
"""

import argparse
import json
import os
import sys
from datetime import datetime


def load_env_file():
    """Load .env file manually without requiring python-dotenv."""
    env_vars = {}
    # Search for .env in current dir and parent dirs
    search_dirs = [os.getcwd()]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    search_dirs.extend([script_dir, parent_dir])

    for directory in search_dirs:
        env_path = os.path.join(directory, ".env")
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" not in line:
                            continue
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip()
                        # Strip surrounding quotes
                        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                            value = value[1:-1]
                        env_vars[key] = value
            except OSError:
                pass
            break  # Only load the first .env found

    # Set env vars only if not already set (real env takes precedence)
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value

    return env_vars


def _safe_get(info, key):
    """Safely get a value from yfinance info dict, returning None on failure."""
    try:
        val = info.get(key)
        # yfinance sometimes returns 'None' as a string or other sentinel values
        if val is None or val == "None":
            return None
        return val
    except Exception:
        return None


def cmd_quote(args):
    """Fetch current quote data for a single ticker."""
    import yfinance

    ticker_str = args.ticker.upper()
    ticker = yfinance.Ticker(ticker_str)

    try:
        info = ticker.info
    except Exception as e:
        print(f"Error fetching data for {ticker_str}: {e}", file=sys.stderr)
        info = {}

    result = {
        "ticker": ticker_str,
        "name": _safe_get(info, "longName") or _safe_get(info, "shortName"),
        "price": _safe_get(info, "currentPrice") or _safe_get(info, "regularMarketPrice"),
        "market_cap": _safe_get(info, "marketCap"),
        "shares_outstanding": _safe_get(info, "sharesOutstanding"),
        "fifty_two_week_high": _safe_get(info, "fiftyTwoWeekHigh"),
        "fifty_two_week_low": _safe_get(info, "fiftyTwoWeekLow"),
        "beta": _safe_get(info, "beta"),
        "currency": _safe_get(info, "currency"),
        "exchange": _safe_get(info, "exchange"),
    }

    print(json.dumps(result, indent=2, default=str))


def cmd_multiples(args):
    """Fetch valuation multiples for a single ticker."""
    import yfinance

    ticker_str = args.ticker.upper()
    result = _get_multiples(ticker_str)
    print(json.dumps(result, indent=2, default=str))


def _get_multiples(ticker_str):
    """Internal helper to fetch multiples for a ticker. Returns a dict."""
    import yfinance

    ticker = yfinance.Ticker(ticker_str)

    try:
        info = ticker.info
    except Exception as e:
        print(f"Error fetching data for {ticker_str}: {e}", file=sys.stderr)
        info = {}

    return {
        "ticker": ticker_str,
        "trailing_pe": _safe_get(info, "trailingPE"),
        "forward_pe": _safe_get(info, "forwardPE"),
        "ev_ebitda": _safe_get(info, "enterpriseToEbitda"),
        "price_to_sales": _safe_get(info, "priceToSalesTrailing12Months"),
        "price_to_book": _safe_get(info, "priceToBook"),
        "dividend_yield": _safe_get(info, "dividendYield"),
        "peg_ratio": _safe_get(info, "pegRatio"),
    }


def cmd_history(args):
    """Fetch historical daily OHLCV data for a ticker."""
    import yfinance

    ticker_str = args.ticker.upper()
    ticker = yfinance.Ticker(ticker_str)

    try:
        hist = ticker.history(period=args.period)
    except Exception as e:
        print(f"Error fetching history for {ticker_str}: {e}", file=sys.stderr)
        print(json.dumps([], indent=2))
        return

    records = []
    for date, row in hist.iterrows():
        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(row.get("Open", None), 4) if row.get("Open") is not None else None,
            "high": round(row.get("High", None), 4) if row.get("High") is not None else None,
            "low": round(row.get("Low", None), 4) if row.get("Low") is not None else None,
            "close": round(row.get("Close", None), 4) if row.get("Close") is not None else None,
            "volume": int(row.get("Volume", 0)) if row.get("Volume") is not None else None,
        })

    print(json.dumps(records, indent=2, default=str))


def cmd_peers(args):
    """Fetch multiples for multiple tickers side by side."""
    results = []
    for ticker_str in args.tickers:
        ticker_str = ticker_str.upper()
        result = _get_multiples(ticker_str)
        results.append(result)

    print(json.dumps(results, indent=2, default=str))


def cmd_risk_free_rate(args):
    """Fetch the 10Y Treasury rate from FRED, or fall back to a default."""
    load_env_file()
    api_key = os.environ.get("FRED_API_KEY")

    if api_key:
        try:
            from fredapi import Fred

            fred = Fred(api_key=api_key)
            series = fred.get_series("DGS10")
            # Drop NaN values and get the most recent observation
            series = series.dropna()
            if len(series) == 0:
                raise ValueError("No data returned from FRED")

            latest_value = float(series.iloc[-1])
            latest_date = series.index[-1]

            result = {
                "rate": latest_value,
                "source": "FRED",
                "as_of": latest_date.strftime("%Y-%m-%d"),
            }
            print(json.dumps(result, indent=2, default=str))
            return

        except ImportError:
            print(
                "Warning: fredapi library not installed. Install with: pip install fredapi",
                file=sys.stderr,
            )
        except Exception as e:
            print(f"Warning: FRED API call failed: {e}", file=sys.stderr)

    # Fallback to default
    result = {
        "rate": 4.5,
        "source": "default",
        "as_of": datetime.now().strftime("%Y-%m-%d"),
        "warning": "Using default rate. Set FRED_API_KEY in environment or .env for live data.",
    }
    print(json.dumps(result, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(
        description="Fetch market data (quotes, multiples, history, peers, risk-free rate).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python infra/market_data.py quote AAPL
  python infra/market_data.py multiples AAPL
  python infra/market_data.py history AAPL --period 2y
  python infra/market_data.py peers AAPL MSFT GOOG
  python infra/market_data.py risk-free-rate
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # quote
    quote_parser = subparsers.add_parser("quote", help="Current price, mkt cap, 52wk range, beta")
    quote_parser.add_argument("ticker", help="Stock ticker symbol")
    quote_parser.set_defaults(func=cmd_quote)

    # multiples
    multiples_parser = subparsers.add_parser(
        "multiples", help="Valuation multiples (P/E, EV/EBITDA, P/S, P/B, etc.)"
    )
    multiples_parser.add_argument("ticker", help="Stock ticker symbol")
    multiples_parser.set_defaults(func=cmd_multiples)

    # history
    history_parser = subparsers.add_parser("history", help="Historical daily OHLCV data")
    history_parser.add_argument("ticker", help="Stock ticker symbol")
    history_parser.add_argument(
        "--period",
        default="2y",
        help="Data period (e.g., 1mo, 6mo, 1y, 2y, 5y, max). Default: 2y",
    )
    history_parser.set_defaults(func=cmd_history)

    # peers
    peers_parser = subparsers.add_parser("peers", help="Side-by-side multiples for multiple tickers")
    peers_parser.add_argument("tickers", nargs="+", help="Two or more ticker symbols")
    peers_parser.set_defaults(func=cmd_peers)

    # risk-free-rate
    rfr_parser = subparsers.add_parser("risk-free-rate", help="10Y Treasury rate from FRED")
    rfr_parser.set_defaults(func=cmd_risk_free_rate)

    args = parser.parse_args()

    # Load .env early for any command that might need it
    load_env_file()

    args.func(args)


if __name__ == "__main__":
    main()
