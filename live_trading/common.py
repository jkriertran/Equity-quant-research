from __future__ import annotations

import copy
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback.
    import tomli as tomllib  # type: ignore[no-redef]


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LIVE_TRADING_DIR = Path(__file__).resolve().parent

DEFAULT_CONFIG: dict[str, Any] = {
    "alerts": {
        "enabled": False,
        "webhook_url_env": "",
    },
    "alpaca": {
        "env_file": ".env.alpaca",
        "live_base_url": "https://api.alpaca.markets",
        "paper": True,
        "paper_base_url": "https://paper-api.alpaca.markets",
        "timeout_seconds": 30,
    },
    "data": {
        "source": "yfinance_adjusted",
        "symbols": ["LQD", "AGG"],
    },
    "execution": {
        "buy_sizing": "notional",
        "cash_only": True,
        "minimum_trade_dollars": 25.0,
        "minimum_trade_equity_pct": 0.0025,
        "order_type": "market",
        "rebalance_timezone": "America/New_York",
        "require_market_open_for_submit": True,
        "sell_sizing": "fractional_qty",
        "time_in_force": "day",
    },
    "paths": {
        "logs_dir": "live_trading/logs",
        "signal_file": "live_trading/state/latest_signal.json",
    },
    "safety": {
        "allow_unapproved_positions": False,
        "approved_symbols": ["NTSX", "TQQQ"],
        "kill_switch_path": "live_trading/state/KILL_SWITCH",
        "max_core_weight": 0.67,
        "max_signal_age_days": 5,
        "max_sleeve_weight": 0.33,
    },
    "signal": {
        "history_calendar_days": 600,
        "name": "lqd_agg_risk_on",
        "sma_window": 150,
    },
    "strategy": {
        "cash_weight_off": 0.33,
        "core_symbol": "NTSX",
        "core_weight": 0.67,
        "name": "ntsx67_tqqq33_lqd_agg_risk_on",
        "sleeve_symbol": "TQQQ",
        "sleeve_weight_on": 0.33,
    },
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def resolve_project_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    config = copy.deepcopy(DEFAULT_CONFIG)
    if config_path is None:
        candidate = LIVE_TRADING_DIR / "config.toml"
        if candidate.exists():
            config_path = candidate
    if config_path is not None:
        path = resolve_project_path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        with path.open("rb") as handle:
            config = deep_merge(config, tomllib.load(handle))
    return config


def load_env_file(env_file: str | Path | None) -> None:
    if not env_file:
        return
    path = resolve_project_path(env_file)
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(resolve_project_path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    output_path = resolve_project_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def append_jsonl(path: str | Path, payload: dict[str, Any]) -> Path:
    output_path = resolve_project_path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    return output_path


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def today_in_timezone(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(timezone_name))


def decimal_string(value: float, places: int = 2) -> str:
    return f"{value:.{places}f}"

