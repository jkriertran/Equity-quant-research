# NTSX/TQQQ Alpaca Bot

This folder implements the v1 production candidate from `docs/NTSX_TQQQ_ALPACA_HANDOFF.md`.

The bot defaults to dry-run. It only submits Alpaca orders when `--submit` is passed and all safety checks pass.

## Strategy

- Hold 67% `NTSX`.
- Hold the 33% sleeve in cash when the LQD/AGG signal is off.
- Hold the 33% sleeve in `TQQQ` when the LQD/AGG signal is on.
- Signal is on when `LQD adjusted close / AGG adjusted close` is above its 150-trading-day SMA.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r live_trading/requirements.txt
cp live_trading/config.example.toml live_trading/config.toml
```

Add Alpaca paper credentials to the repo-root `.env.alpaca` file or export them in your shell:

```bash
APCA_API_KEY_ID="..."
APCA_API_SECRET_KEY="..."
```

## Daily Commands

After the close:

```bash
python live_trading/run_after_close.py --config live_trading/config.toml
```

Before the rebalance:

```bash
python live_trading/run_before_open.py --config live_trading/config.toml --dry-run
```

Paper/live order submission requires the explicit flag:

```bash
python live_trading/run_before_open.py --config live_trading/config.toml --submit
```

## Safety Controls

The rebalancer refuses to submit when:

- `live_trading/state/KILL_SWITCH` exists.
- The signal file is missing, stale, or dated in the future.
- Alpaca reports the account is blocked or suspended.
- Open orders already exist.
- Positions outside `NTSX` and `TQQQ` exist, unless allowed in config.
- Short positions exist.
- Planned buys exceed cash plus planned sells when `cash_only = true`.
- Alpaca says the market is closed and `require_market_open_for_submit = true`.

Create the kill switch with:

```bash
touch live_trading/state/KILL_SWITCH
```

Remove it only when you want the bot to trade again.

## Logs And State

- Latest signal: `live_trading/state/latest_signal.json`
- Runtime logs: `live_trading/logs/YYYYMMDD_rebalance.jsonl`
- Example signal: `live_trading/state/latest_signal.example.json`

All JSON is serialized with deterministic key ordering.

## AWS VM Deployment Sketch

1. Launch a small Ubuntu EC2 or Lightsail instance.
2. Install Python 3.11+ and Git.
3. Clone this repo into `/opt/ntsx-tqqq`.
4. Create `/opt/ntsx-tqqq/.venv` and install `live_trading/requirements.txt`.
5. Copy `config.example.toml` to `config.toml`.
6. Store Alpaca credentials in `/etc/ntsx-tqqq/alpaca.env` with `0600` permissions.
7. Update `live_trading/config.toml` so `alpaca.env_file = "/etc/ntsx-tqqq/alpaca.env"`.
8. Copy the files in `live_trading/systemd/` into `/etc/systemd/system/`.
9. Keep timers on dry-run first; switch the before-open service to `--submit` only after paper testing is clean.

The timer examples use `Timezone=America/New_York` so market-time schedules stay correct on UTC cloud hosts.

## Verification

```bash
python -m unittest discover live_trading/tests
python -m py_compile live_trading/*.py
```
