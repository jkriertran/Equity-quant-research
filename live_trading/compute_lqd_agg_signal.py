from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

try:
    from .common import load_config, utc_now_iso, write_json
except ImportError:  # pragma: no cover - supports `python live_trading/script.py`.
    from common import load_config, utc_now_iso, write_json


def _extract_adj_close(data: pd.DataFrame, symbol: str) -> pd.Series:
    if data.empty:
        raise RuntimeError(f"No data returned for {symbol}.")
    if isinstance(data.columns, pd.MultiIndex):
        if symbol in data.columns.get_level_values(0):
            frame = data[symbol]
            if "Adj Close" in frame:
                return frame["Adj Close"].rename(symbol)
        if "Adj Close" in data.columns.get_level_values(0):
            frame = data["Adj Close"]
            if symbol in frame:
                return frame[symbol].rename(symbol)
    if "Adj Close" in data:
        return data["Adj Close"].rename(symbol)
    if "Close" in data:
        return data["Close"].rename(symbol)
    raise RuntimeError(f"Could not find adjusted close data for {symbol}.")


def fetch_adjusted_prices(symbols: list[str], history_calendar_days: int) -> pd.DataFrame:
    end = date.today() + timedelta(days=1)
    start = end - timedelta(days=history_calendar_days)
    raw = yf.download(
        tickers=" ".join(symbols),
        start=start.isoformat(),
        end=end.isoformat(),
        auto_adjust=False,
        progress=False,
        group_by="ticker",
        threads=False,
    )
    series = [_extract_adj_close(raw, symbol).dropna() for symbol in symbols]
    latest_dates = {symbol: price.index.max().date().isoformat() for symbol, price in zip(symbols, series)}
    if len(set(latest_dates.values())) != 1:
        raise RuntimeError(f"Latest trading dates do not match: {latest_dates}")
    prices = pd.concat(series, axis=1).dropna()
    prices.index = pd.to_datetime(prices.index).tz_localize(None).normalize()
    return prices.sort_index()


def compute_signal_state(config: dict[str, Any]) -> dict[str, Any]:
    symbols = list(config["data"]["symbols"])
    if symbols != ["LQD", "AGG"]:
        raise ValueError("v1 expects data.symbols to be ['LQD', 'AGG'].")
    sma_window = int(config["signal"]["sma_window"])
    prices = fetch_adjusted_prices(symbols, int(config["signal"]["history_calendar_days"]))
    if len(prices) < sma_window:
        raise RuntimeError(f"Need at least {sma_window} rows, got {len(prices)}.")

    ratio = prices["LQD"].div(prices["AGG"])
    ratio_sma = ratio.rolling(sma_window).mean()
    valid = pd.DataFrame({"ratio": ratio, "ratio_sma": ratio_sma}).dropna()
    if valid.empty:
        raise RuntimeError("No valid LQD/AGG signal rows after SMA calculation.")

    latest = valid.iloc[-1]
    latest_date = valid.index[-1].date().isoformat()
    lqd_close = float(prices.loc[valid.index[-1], "LQD"])
    agg_close = float(prices.loc[valid.index[-1], "AGG"])
    ratio_value = float(latest["ratio"])
    sma_value = float(latest["ratio_sma"])
    signal_on = bool(ratio_value >= sma_value)

    return {
        "agg_adjusted_close": round(agg_close, 6),
        "as_of": latest_date,
        "created_at_utc": utc_now_iso(),
        "data_source": config["data"]["source"],
        "history_rows": int(len(prices)),
        "lqd_adjusted_close": round(lqd_close, 6),
        "lqd_agg_ratio": round(ratio_value, 8),
        "lqd_agg_ratio_distance": round(ratio_value / sma_value - 1.0, 8),
        "lqd_agg_ratio_sma150": round(sma_value, 8),
        "signal_name": config["signal"]["name"],
        "signal_on": signal_on,
        "sma_window": sma_window,
        "strategy": config["strategy"]["name"],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute the LQD/AGG risk-on signal.")
    parser.add_argument("--config", default=None, help="Path to TOML config. Defaults to live_trading/config.toml if present.")
    parser.add_argument("--output", default=None, help="Signal JSON path. Defaults to paths.signal_file in config.")
    parser.add_argument("--print-json", action="store_true", help="Print the full signal JSON after writing it.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        signal_state = compute_signal_state(config)
        output = Path(args.output or config["paths"]["signal_file"])
        output_path = write_json(output, signal_state)
        status = "ON" if signal_state["signal_on"] else "OFF"
        print(
            f"Wrote {output_path}: {signal_state['signal_name']} {status} "
            f"as_of={signal_state['as_of']} ratio={signal_state['lqd_agg_ratio']:.6f} "
            f"sma={signal_state['lqd_agg_ratio_sma150']:.6f}"
        )
        if args.print_json:
            print(json.dumps(signal_state, indent=2, sort_keys=True))
        return 0
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
