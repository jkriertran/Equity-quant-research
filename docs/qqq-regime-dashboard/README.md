# QQQ Regime Dashboard

Static GitHub Pages copy of the QQQ macro-regime nowcasting dashboard.

## Files

- `index.html`: publishable dashboard entry point.
- `plots/`: 10 PNG chart files.
- `data/`: 35 CSV study output files plus `manifest.json`.

## Local Preview

Open `docs/qqq-regime-dashboard/index.html` in a browser.

## Regenerate

After rerunning the regime study, refresh this publishable copy with:

```bash
python3 tools/publish_qqq_regime_dashboard.py
```
