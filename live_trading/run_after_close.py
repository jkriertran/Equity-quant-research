from __future__ import annotations

try:
    from .compute_lqd_agg_signal import main
except ImportError:  # pragma: no cover - supports `python live_trading/script.py`.
    from compute_lqd_agg_signal import main


if __name__ == "__main__":
    raise SystemExit(main())

