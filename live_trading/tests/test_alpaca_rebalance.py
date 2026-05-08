from __future__ import annotations

import copy
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alpaca_rebalance import AccountSnapshot, PositionSnapshot, build_order_plan, safety_blockers
from common import DEFAULT_CONFIG


def config() -> dict:
    return copy.deepcopy(DEFAULT_CONFIG)


class RebalancePlannerTests(unittest.TestCase):
    def test_signal_on_buys_core_and_tqqq_when_underweight(self) -> None:
        cfg = config()
        account = AccountSnapshot(equity=100_000, cash=35_000, buying_power=35_000)
        positions = {"NTSX": PositionSnapshot("NTSX", qty=650, market_value=65_000)}
        signal = {
            "as_of": date.today().isoformat(),
            "signal_name": "lqd_agg_risk_on",
            "signal_on": True,
            "strategy": "ntsx67_tqqq33_lqd_agg_risk_on",
        }
        summary, orders = build_order_plan(account, positions, signal, cfg, rebalance_date="20260508")

        self.assertEqual(summary["target_values"], {"NTSX": 67_000.0, "TQQQ": 33_000.0})
        self.assertEqual([order.symbol for order in orders], ["NTSX", "TQQQ"])
        self.assertEqual([order.side for order in orders], ["buy", "buy"])
        self.assertEqual(orders[1].client_order_id, "ntsx-tqqq-20260508-TQQQ-buy")
        self.assertEqual(orders[1].notional, 33_000.0)

    def test_signal_off_sells_tqqq_before_buys(self) -> None:
        cfg = config()
        account = AccountSnapshot(equity=100_000, cash=0, buying_power=0)
        positions = {
            "NTSX": PositionSnapshot("NTSX", qty=650, market_value=65_000),
            "TQQQ": PositionSnapshot("TQQQ", qty=100, market_value=33_000),
        }
        signal = {
            "as_of": date.today().isoformat(),
            "signal_name": "lqd_agg_risk_on",
            "signal_on": False,
            "strategy": "ntsx67_tqqq33_lqd_agg_risk_on",
        }
        _, orders = build_order_plan(account, positions, signal, cfg, rebalance_date="20260508")

        self.assertEqual([order.side for order in orders], ["sell", "buy"])
        self.assertEqual(orders[0].symbol, "TQQQ")
        self.assertEqual(orders[0].qty, 100.0)
        self.assertEqual(orders[0].client_order_id, "ntsx-tqqq-20260508-TQQQ-sell")

    def test_minimum_trade_threshold_skips_small_drift(self) -> None:
        cfg = config()
        account = AccountSnapshot(equity=100_000, cash=100, buying_power=100)
        positions = {
            "NTSX": PositionSnapshot("NTSX", qty=670, market_value=66_900),
            "TQQQ": PositionSnapshot("TQQQ", qty=330, market_value=33_100),
        }
        signal = {
            "as_of": date.today().isoformat(),
            "signal_name": "lqd_agg_risk_on",
            "signal_on": True,
            "strategy": "ntsx67_tqqq33_lqd_agg_risk_on",
        }
        _, orders = build_order_plan(account, positions, signal, cfg, rebalance_date="20260508")

        self.assertEqual(orders, [])

    def test_stale_signal_blocks_submission(self) -> None:
        cfg = config()
        account = AccountSnapshot(equity=100_000, cash=35_000, buying_power=35_000)
        positions = {"NTSX": PositionSnapshot("NTSX", qty=670, market_value=67_000)}
        signal = {
            "as_of": (date.today() - timedelta(days=10)).isoformat(),
            "signal_name": "lqd_agg_risk_on",
            "signal_on": False,
            "strategy": "ntsx67_tqqq33_lqd_agg_risk_on",
        }
        _, orders = build_order_plan(account, positions, signal, cfg, rebalance_date="20260508")
        blockers = safety_blockers(account, positions, [], signal, cfg, orders, clock={"is_open": True}, submit=True)

        self.assertTrue(any("Signal is stale" in blocker for blocker in blockers))


if __name__ == "__main__":
    unittest.main()
