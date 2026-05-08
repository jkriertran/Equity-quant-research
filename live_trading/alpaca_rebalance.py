from __future__ import annotations

import argparse
import os
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests

try:
    from .common import (
        append_jsonl,
        decimal_string,
        load_config,
        load_env_file,
        read_json,
        resolve_project_path,
        today_in_timezone,
        utc_now_iso,
    )
except ImportError:  # pragma: no cover - supports `python live_trading/script.py`.
    from common import (
        append_jsonl,
        decimal_string,
        load_config,
        load_env_file,
        read_json,
        resolve_project_path,
        today_in_timezone,
        utc_now_iso,
    )


@dataclass(frozen=True)
class PositionSnapshot:
    symbol: str
    qty: float
    market_value: float
    side: str = "long"


@dataclass(frozen=True)
class AccountSnapshot:
    equity: float
    cash: float
    buying_power: float
    account_blocked: bool = False
    trade_suspended_by_user: bool = False
    trading_blocked: bool = False


@dataclass(frozen=True)
class PlannedOrder:
    client_order_id: str
    current_value: float
    estimated_value: float
    reason: str
    side: str
    symbol: str
    target_value: float
    notional: float | None = None
    qty: float | None = None

    def payload(self, order_type: str, time_in_force: str) -> dict[str, str]:
        payload = {
            "client_order_id": self.client_order_id,
            "side": self.side,
            "symbol": self.symbol,
            "time_in_force": time_in_force,
            "type": order_type,
        }
        if self.qty is not None:
            payload["qty"] = decimal_string(self.qty, 6)
        else:
            payload["notional"] = decimal_string(float(self.notional), 2)
        return payload


class AlpacaRestClient:
    def __init__(self, config: dict[str, Any]) -> None:
        load_env_file(config["alpaca"].get("env_file"))
        key_id = os.environ.get("APCA_API_KEY_ID") or os.environ.get("ALPACA_API_KEY")
        secret_key = os.environ.get("APCA_API_SECRET_KEY") or os.environ.get("ALPACA_SECRET_KEY")
        if not key_id or not secret_key:
            raise RuntimeError(
                "Missing Alpaca credentials. Set APCA_API_KEY_ID and APCA_API_SECRET_KEY "
                "or add them to the configured env_file."
            )
        self.base_url = (
            config["alpaca"]["paper_base_url"] if bool(config["alpaca"]["paper"]) else config["alpaca"]["live_base_url"]
        ).rstrip("/")
        self.timeout = int(config["alpaca"]["timeout_seconds"])
        self.headers = {
            "APCA-API-KEY-ID": key_id,
            "APCA-API-SECRET-KEY": secret_key,
            "Content-Type": "application/json",
        }

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_payload: dict[str, Any] | None = None,
        allow_404: bool = False,
    ) -> Any:
        url = f"{self.base_url}{path}"
        response = requests.request(
            method,
            url,
            headers=self.headers,
            params=params,
            json=json_payload,
            timeout=self.timeout,
        )
        if allow_404 and response.status_code == 404:
            return None
        if response.status_code >= 400:
            raise RuntimeError(f"Alpaca {method} {path} failed with {response.status_code}: {response.text[:500]}")
        if not response.text:
            return {}
        return response.json()

    def get_account(self) -> AccountSnapshot:
        raw = self.request("GET", "/v2/account")
        return AccountSnapshot(
            equity=float(raw.get("equity") or 0.0),
            cash=float(raw.get("cash") or 0.0),
            buying_power=float(raw.get("buying_power") or 0.0),
            account_blocked=bool(raw.get("account_blocked")),
            trade_suspended_by_user=bool(raw.get("trade_suspended_by_user")),
            trading_blocked=bool(raw.get("trading_blocked")),
        )

    def get_positions(self) -> dict[str, PositionSnapshot]:
        raw_positions = self.request("GET", "/v2/positions")
        positions: dict[str, PositionSnapshot] = {}
        for raw in raw_positions:
            symbol = str(raw["symbol"]).upper()
            positions[symbol] = PositionSnapshot(
                symbol=symbol,
                qty=float(raw.get("qty") or 0.0),
                market_value=float(raw.get("market_value") or 0.0),
                side=str(raw.get("side") or "long"),
            )
        return positions

    def get_open_orders(self) -> list[dict[str, Any]]:
        return list(self.request("GET", "/v2/orders", params={"status": "open", "limit": 500, "nested": "true"}))

    def get_clock(self) -> dict[str, Any]:
        return dict(self.request("GET", "/v2/clock"))

    def get_order_by_client_order_id(self, client_order_id: str) -> dict[str, Any] | None:
        query = urlencode({"client_order_id": client_order_id})
        return self.request("GET", f"/v2/orders:by_client_order_id?{query}", allow_404=True)

    def submit_order(self, payload: dict[str, str]) -> dict[str, Any]:
        return dict(self.request("POST", "/v2/orders", json_payload=payload))


def parse_date(value: str) -> date:
    return datetime.fromisoformat(value).date()


def load_signal_state(path: str | Path) -> dict[str, Any]:
    signal = read_json(path)
    required = {"as_of", "signal_name", "signal_on", "strategy"}
    missing = sorted(required - set(signal))
    if missing:
        raise RuntimeError(f"Signal file is missing required keys: {missing}")
    return signal


def target_values(equity: float, signal_on: bool, config: dict[str, Any]) -> dict[str, float]:
    core_symbol = str(config["strategy"]["core_symbol"]).upper()
    sleeve_symbol = str(config["strategy"]["sleeve_symbol"]).upper()
    core_weight = float(config["strategy"]["core_weight"])
    sleeve_weight = float(config["strategy"]["sleeve_weight_on"]) if signal_on else 0.0
    if core_weight > float(config["safety"]["max_core_weight"]) + 1e-9:
        raise RuntimeError("Core target weight exceeds configured max_core_weight.")
    if sleeve_weight > float(config["safety"]["max_sleeve_weight"]) + 1e-9:
        raise RuntimeError("Sleeve target weight exceeds configured max_sleeve_weight.")
    return {
        core_symbol: equity * core_weight,
        sleeve_symbol: equity * sleeve_weight,
    }


def minimum_trade_value(equity: float, config: dict[str, Any]) -> float:
    return max(
        float(config["execution"]["minimum_trade_dollars"]),
        equity * float(config["execution"]["minimum_trade_equity_pct"]),
    )


def build_order_plan(
    account: AccountSnapshot,
    positions: dict[str, PositionSnapshot],
    signal: dict[str, Any],
    config: dict[str, Any],
    *,
    rebalance_date: str | None = None,
) -> tuple[dict[str, Any], list[PlannedOrder]]:
    if account.equity <= 0:
        raise RuntimeError("Account equity is missing or non-positive.")

    timezone_name = str(config["execution"]["rebalance_timezone"])
    date_token = rebalance_date or today_in_timezone(timezone_name).strftime("%Y%m%d")
    targets = target_values(account.equity, bool(signal["signal_on"]), config)
    min_trade = minimum_trade_value(account.equity, config)
    orders: list[PlannedOrder] = []

    for symbol, target_value in targets.items():
        position = positions.get(symbol, PositionSnapshot(symbol=symbol, qty=0.0, market_value=0.0))
        current_value = max(position.market_value, 0.0)
        delta = target_value - current_value
        if abs(delta) < min_trade:
            continue
        side = "buy" if delta > 0 else "sell"
        estimated_value = abs(delta)
        client_order_id = f"ntsx-tqqq-{date_token}-{symbol}-{side}"
        qty: float | None = None
        notional: float | None = estimated_value
        if side == "sell" and str(config["execution"]["sell_sizing"]) == "fractional_qty":
            if current_value <= 0 or position.qty <= 0:
                continue
            sell_fraction = min(estimated_value / current_value, 1.0)
            qty = round(position.qty * sell_fraction, 6)
            notional = None
        orders.append(
            PlannedOrder(
                client_order_id=client_order_id,
                current_value=round(current_value, 2),
                estimated_value=round(estimated_value, 2),
                notional=round(notional, 2) if notional is not None else None,
                qty=qty,
                reason=f"target={target_value:.2f};current={current_value:.2f};min_trade={min_trade:.2f}",
                side=side,
                symbol=symbol,
                target_value=round(target_value, 2),
            )
        )

    orders.sort(key=lambda order: (0 if order.side == "sell" else 1, order.symbol))
    cash_target = account.equity - sum(targets.values())
    summary = {
        "account_cash": round(account.cash, 2),
        "account_equity": round(account.equity, 2),
        "cash_target": round(cash_target, 2),
        "minimum_trade": round(min_trade, 2),
        "signal_as_of": signal["as_of"],
        "signal_name": signal["signal_name"],
        "signal_on": bool(signal["signal_on"]),
        "target_values": {symbol: round(value, 2) for symbol, value in targets.items()},
    }
    return summary, orders


def safety_blockers(
    account: AccountSnapshot,
    positions: dict[str, PositionSnapshot],
    open_orders: list[dict[str, Any]],
    signal: dict[str, Any],
    config: dict[str, Any],
    orders: list[PlannedOrder],
    *,
    clock: dict[str, Any] | None,
    submit: bool,
) -> list[str]:
    blockers: list[str] = []
    kill_switch_path = resolve_project_path(config["safety"]["kill_switch_path"])
    if kill_switch_path.exists():
        blockers.append(f"Kill switch exists: {kill_switch_path}")
    if account.equity <= 0:
        blockers.append("Account equity is missing or non-positive.")
    if account.account_blocked or account.trading_blocked or account.trade_suspended_by_user:
        blockers.append("Alpaca account is blocked or suspended from trading.")
    if open_orders:
        symbols = sorted({str(order.get("symbol", "")).upper() for order in open_orders})
        blockers.append(f"Open orders already exist: {symbols}")
    approved = {str(symbol).upper() for symbol in config["safety"]["approved_symbols"]}
    unapproved = sorted(symbol for symbol in positions if symbol not in approved and abs(positions[symbol].market_value) > 1)
    if unapproved and not bool(config["safety"]["allow_unapproved_positions"]):
        blockers.append(f"Positions outside approved universe: {unapproved}")
    short_positions = sorted(symbol for symbol, position in positions.items() if position.qty < 0 or position.side == "short")
    if short_positions:
        blockers.append(f"Short positions are not allowed: {short_positions}")
    timezone_name = str(config["execution"]["rebalance_timezone"])
    signal_age = (today_in_timezone(timezone_name).date() - parse_date(str(signal["as_of"]))).days
    if signal_age < 0:
        blockers.append(f"Signal date is in the future: {signal['as_of']}")
    if signal_age > int(config["safety"]["max_signal_age_days"]):
        blockers.append(f"Signal is stale: {signal['as_of']} is {signal_age} calendar days old.")
    if submit and bool(config["execution"]["require_market_open_for_submit"]):
        if not clock:
            blockers.append("Market clock is unavailable.")
        elif not bool(clock.get("is_open")):
            blockers.append("Alpaca market clock says the market is closed.")
    if bool(config["execution"]["cash_only"]):
        sell_value = sum(order.estimated_value for order in orders if order.side == "sell")
        buy_value = sum(order.estimated_value for order in orders if order.side == "buy")
        if buy_value > account.cash + sell_value + 1.0:
            blockers.append(
                f"Planned buys ${buy_value:.2f} exceed cash plus planned sells ${account.cash + sell_value:.2f}."
            )
    return blockers


def log_path(config: dict[str, Any], label: str) -> Path:
    timezone_name = str(config["execution"]["rebalance_timezone"])
    date_token = today_in_timezone(timezone_name).strftime("%Y%m%d")
    return Path(config["paths"]["logs_dir"]) / f"{date_token}_{label}.jsonl"


def print_rebalance(summary: dict[str, Any], orders: list[PlannedOrder], blockers: list[str], *, submit: bool) -> None:
    mode = "SUBMIT" if submit else "DRY-RUN"
    signal = "ON" if summary["signal_on"] else "OFF"
    print(f"{mode} ntsx_tqqq rebalance: signal {signal} as_of={summary['signal_as_of']}")
    print(
        f"equity=${summary['account_equity']:.2f} cash=${summary['account_cash']:.2f} "
        f"minimum_trade=${summary['minimum_trade']:.2f}"
    )
    for symbol, target in summary["target_values"].items():
        print(f"target {symbol}: ${target:.2f}")
    print(f"target cash: ${summary['cash_target']:.2f}")
    if not orders:
        print("orders: none")
    else:
        print("orders:")
        for order in orders:
            size = f"qty={order.qty:.6f}" if order.qty is not None else f"notional=${order.notional:.2f}"
            print(f"  {order.client_order_id}: {order.side} {order.symbol} {size} approx=${order.estimated_value:.2f}")
    if blockers:
        print("blocked:")
        for blocker in blockers:
            print(f"  - {blocker}")


def run_rebalance(
    config: dict[str, Any],
    *,
    submit: bool,
    signal_file: str | Path | None = None,
) -> int:
    signal = load_signal_state(signal_file or config["paths"]["signal_file"])
    client = AlpacaRestClient(config)
    account = client.get_account()
    positions = client.get_positions()
    open_orders = client.get_open_orders()
    clock = client.get_clock() if submit or bool(config["execution"]["require_market_open_for_submit"]) else None
    summary, orders = build_order_plan(account, positions, signal, config)
    blockers = safety_blockers(account, positions, open_orders, signal, config, orders, clock=clock, submit=submit)
    print_rebalance(summary, orders, blockers, submit=submit)

    submitted: list[dict[str, Any]] = []
    skipped_existing: list[str] = []
    if submit and not blockers:
        for order in orders:
            existing = client.get_order_by_client_order_id(order.client_order_id)
            if existing is not None:
                skipped_existing.append(order.client_order_id)
                continue
            submitted.append(
                client.submit_order(order.payload(config["execution"]["order_type"], config["execution"]["time_in_force"]))
            )
        if skipped_existing:
            print(f"skipped existing order ids: {', '.join(skipped_existing)}")
        print(f"submitted orders: {len(submitted)}")
    elif submit and blockers:
        print("submitted orders: 0")

    log_record = {
        "blockers": blockers,
        "created_at_utc": utc_now_iso(),
        "mode": "submit" if submit else "dry_run",
        "orders": [asdict(order) for order in orders],
        "skipped_existing_client_order_ids": skipped_existing,
        "submitted_order_ids": [order.get("id") for order in submitted],
        "summary": summary,
    }
    append_jsonl(log_path(config, "rebalance"), log_record)
    return 2 if blockers else 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dry-run or submit the NTSX/TQQQ Alpaca rebalance.")
    parser.add_argument("--config", default=None, help="Path to TOML config. Defaults to live_trading/config.toml if present.")
    parser.add_argument("--signal-file", default=None, help="Override signal JSON path.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Print the order plan without submitting. This is the default.")
    mode.add_argument("--submit", action="store_true", help="Submit orders to Alpaca if all safety checks pass.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        return run_rebalance(config, submit=bool(args.submit), signal_file=args.signal_file)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
