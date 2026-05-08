# NTSX TQQQ Alpaca Build

## Goal
Build a local dry-run trading module for the 67% NTSX / tactical 33% TQQQ strategy that can be promoted to Alpaca paper trading and then deployed to an AWS VM.

## Tasks
- [x] Create `live_trading/` project structure -> Verify: expected files and folders exist.
- [x] Add LQD/AGG signal writer -> Verify: script writes deterministic `latest_signal.json`.
- [x] Add Alpaca rebalancer -> Verify: dry-run prints targets and order plan without submitting by default.
- [x] Add safety checks and idempotent client order IDs -> Verify: tests cover stale signals, min trades, and sell-first planning.
- [x] Add local/AWS docs and systemd examples -> Verify: README contains local setup and deployment path.
- [x] Run local verification -> Verify: unit tests and syntax checks pass.

## Done When
- [x] `python live_trading/run_after_close.py --config live_trading/config.example.toml --output live_trading/state/latest_signal.json` can compute a signal.
- [x] `python -m unittest discover live_trading/tests` passes.
- [x] The rebalancer defaults to dry-run and requires `--submit` for order placement.

## Notes
- No Alpaca credentials are committed.
- Runtime logs and live state stay under `live_trading/logs/` and `live_trading/state/`.
- Alpaca connection verification is pending until paper credentials are added to `.env.alpaca` or the shell environment.
