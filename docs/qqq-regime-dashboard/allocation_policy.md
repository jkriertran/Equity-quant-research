# QQQ Regime Allocation Policy

Generated: 2026-07-10T05:24:13Z

This is a research policy for a mock allocation index. It is not a personalized portfolio recommendation, a live trading system, or investment advice.

## Objective

Create a transparent QQQ-aware allocation benchmark that converts the regime dashboard into predefined target weights. The index should remain simple enough to audit: long-only, no leverage, weekly observations, explicit cash, and no hidden optimizer.

## Asset Universe

V1 uses six investable sleeves and keeps oil and dollar exposure as macro monitors only.

| sleeve       | asset_class            | implementation_proxy                    | role                                                                   |
|:-------------|:-----------------------|:----------------------------------------|:-----------------------------------------------------------------------|
| qqq_growth   | QQQ / Growth Equity    | QQQ                                     | Primary growth engine and benchmark-relative risk sleeve.              |
| broad_equity | SPY / Broad US Equity  | SPY                                     | Diversified equity ballast inside the equity bucket.                   |
| core_bonds   | AGG / Core Bonds       | AGG                                     | Duration and defensive ballast.                                        |
| ig_credit    | LQD / IG Credit        | LQD                                     | Moderate carry and credit beta.                                        |
| gold         | Gold                   | GLD or IAU                              | Inflation, dollar, and stress-diversifier sleeve.                      |
| cash         | Cash / Fed Funds Proxy | Treasury bills, SGOV/BIL, or cash sweep | Dry powder, volatility dampener, and high-confidence defensive sleeve. |

## Strategic Neutral Weights

The neutral policy is QQQ-centric but diversified:

- 55% total equity: 40% QQQ and 15% SPY.
- 30% bonds/credit: 20% AGG and 10% LQD.
- 15% diversifiers/liquidity: 10% gold and 5% cash.

## Regime Target Weights

Weights are deliberately conservative. They use the asset leaderboard as context, but they do not simply chase the top historical return asset inside each regime.

| regime            |   qqq_growth |   broad_equity |   core_bonds |   ig_credit |   gold |   cash |
|:------------------|-------------:|---------------:|-------------:|------------:|-------:|-------:|
| fragile_growth    |         35.0 |           10.0 |         20.0 |        10.0 |   15.0 |   10.0 |
| macro_tightening  |         35.0 |           10.0 |         20.0 |         5.0 |   15.0 |   15.0 |
| risk_off_stress   |         10.0 |            5.0 |         35.0 |        10.0 |   20.0 |   20.0 |
| risk_on_growth    |         55.0 |           15.0 |         10.0 |         5.0 |    5.0 |   10.0 |
| strategic_neutral |         40.0 |           15.0 |         20.0 |        10.0 |   10.0 |    5.0 |

## Current Policy Target

| as_of      | current_regime   | asset_class            | implementation_proxy                    |   target_weight_pct |
|:-----------|:-----------------|:-----------------------|:----------------------------------------|--------------------:|
| 2026-07-09 | risk_on_growth   | QQQ / Growth Equity    | QQQ                                     |                55.0 |
| 2026-07-09 | risk_on_growth   | SPY / Broad US Equity  | SPY                                     |                15.0 |
| 2026-07-09 | risk_on_growth   | AGG / Core Bonds       | AGG                                     |                10.0 |
| 2026-07-09 | risk_on_growth   | LQD / IG Credit        | LQD                                     |                 5.0 |
| 2026-07-09 | risk_on_growth   | Gold                   | GLD or IAU                              |                 5.0 |
| 2026-07-09 | risk_on_growth   | Cash / Fed Funds Proxy | Treasury bills, SGOV/BIL, or cash sweep |                10.0 |

## Risk Limits

| limit_name                             | value                                                                                          | rationale                                                                                                              |
|:---------------------------------------|:-----------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------|
| index_type                             | long_only_fully_invested_model_index                                                           | The first index should be transparent and benchmark-like, not a leveraged tactical strategy.                           |
| gross_exposure_max_pct                 | 100                                                                                            | No leverage in v1.                                                                                                     |
| short_exposure_max_pct                 | 0                                                                                              | No shorts in v1; inverse funds and futures can be a later study.                                                       |
| qqq_weight_max_pct                     | 60                                                                                             | Preserves the QQQ identity while preventing a single-sleeve index.                                                     |
| equity_weight_max_pct                  | 75                                                                                             | Caps combined QQQ plus SPY beta.                                                                                       |
| equity_weight_min_pct                  | 15                                                                                             | Keeps the benchmark QQQ-aware even in stress regimes.                                                                  |
| cash_weight_min_pct                    | 5                                                                                              | Every regime keeps explicit liquidity.                                                                                 |
| gold_weight_max_pct                    | 25                                                                                             | Gold is useful diversifier but volatile enough to need a cap.                                                          |
| ig_credit_weight_max_pct               | 15                                                                                             | Credit spread beta can become equity-like in stress.                                                                   |
| rebalance_frequency                    | weekly                                                                                         | Matches the primary nowcast grain.                                                                                     |
| signal_lag                             | rebalance on the next tradable session after the regime observation date                       | Avoids using the same close for both classification and execution.                                                     |
| max_one_way_turnover_per_rebalance_pct | 25                                                                                             | Keeps the mock index from becoming a churn machine during regime noise.                                                |
| boundary_blend_rule                    | if boundary_score >= 20% or confidence < 80%, use posterior-probability blended regime weights | Boundary score is classification ambiguity, so ambiguous states should smooth weights rather than force a hard switch. |
| transition_risk_rule                   | transition probability is reported but does not independently de-risk v1                       | Transition risk is a path statistic, not a direct market-risk signal.                                                  |
| drawdown_review_trigger_pct            | -15                                                                                            | A portfolio drawdown beyond this level should be highlighted before increasing equity risk.                            |

## Evidence Snapshot

Top three assets by return-to-vol inside each weekly regime:

| regime           | asset_class            |   return_to_vol |   avg_fwd_return_pct |   worst_fwd_return_pct |   rank_return_to_vol |
|:-----------------|:-----------------------|----------------:|---------------------:|-----------------------:|---------------------:|
| fragile_growth   | Cash / Fed Funds Proxy |            0.99 |                 0.49 |                   0.02 |                    1 |
| fragile_growth   | Gold                   |            0.67 |                 4.92 |                 -13.88 |                    2 |
| fragile_growth   | QQQ / Growth Equity    |            0.46 |                 6.09 |                 -43.80 |                    3 |
| macro_tightening | Cash / Fed Funds Proxy |            1.17 |                 0.58 |                   0.02 |                    1 |
| macro_tightening | QQQ / Growth Equity    |            0.54 |                 3.86 |                 -19.53 |                    2 |
| macro_tightening | AGG / Core Bonds       |            0.54 |                 0.98 |                  -5.34 |                    3 |
| risk_off_stress  | Cash / Fed Funds Proxy |            0.93 |                 0.34 |                   0.01 |                    1 |
| risk_off_stress  | Gold                   |            0.21 |                 2.24 |                 -21.04 |                    2 |
| risk_off_stress  | LQD / IG Credit        |            0.19 |                 1.48 |                 -17.55 |                    3 |
| risk_on_growth   | SPY / Broad US Equity  |            0.77 |                 4.67 |                 -15.07 |                    1 |
| risk_on_growth   | QQQ / Growth Equity    |            0.64 |                 4.86 |                 -18.39 |                    2 |
| risk_on_growth   | Oil                    |            0.52 |                 8.23 |                 -24.12 |                    3 |

## Interpretation Rules

- Boundary score controls weight smoothing, not bearishness.
- Transition probability is monitored but does not independently force de-risking in v1.
- If the current regime is ambiguous, use posterior-probability blended weights rather than a hard regime switch.
- Rebalance on the next tradable session after the regime observation date to avoid same-close lookahead.
- Treat this as a benchmark for research comparison against QQQ, SPY, 60/40, and cash.

## Next Mock Index Step

Backtest `balanced_v1` as an index level starting at 100, with weekly signal lag, one-way turnover reporting, and comparisons against QQQ buy-and-hold.
