from __future__ import annotations

try:
    from .alpaca_rebalance import main
except ImportError:  # pragma: no cover - supports `python live_trading/script.py`.
    from alpaca_rebalance import main


if __name__ == "__main__":
    raise SystemExit(main())

