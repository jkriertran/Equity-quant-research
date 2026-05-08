# A Beginner-Friendly Framework for Finding Quantitative Alpha

## What This Guide Is For

This guide explains the research framework we used in the QQQ project in plain language.

The goal is to help someone understand:

- what kind of data to collect
- how to turn raw data into useful features
- why common chart indicators are not enough
- how to test whether a signal actually works
- how to avoid fooling yourself with a pretty backtest

The big idea:

> Do not start with an indicator. Start with a question about market behavior, then build data that can test that question.

In this project, our core question was:

> When QQQ pulls back, can outside market information tell us whether that pullback is a good long entry?

That is different from asking:

> Can I draw a line on a chart and guess where price goes next?

We want a repeatable process, not a visual opinion.

## Why "Off The Shelf" Chart Tools Are Not Enough

Most retail technical analysis tools are transformations of the same price series:

- MACD
- Bollinger Bands
- RSI
- moving-average crossovers
- trendlines
- chart patterns
- support and resistance lines

These tools can be useful for describing price action, but they should not be trusted just because they look intuitive on a chart.

The problem is that many of them have little to no reliable statistical significance once you test them out of sample. In plain English:

> They often look good on the historical chart you are staring at, but they usually do not keep working when tested on future unseen data.

There are a few reasons:

- They are usually built only from the asset's own price.
- Many versions can be tried until one looks good.
- Drawing lines and patterns is subjective.
- A chart can make randomness look meaningful.
- Same-close testing often assumes fills you could not actually get.
- The best-looking rule is often just the best random result among many tests.

This does not mean every indicator is useless. It means every indicator must be treated as a testable feature, not as proof.

For example:

```text
Bad use:
"MACD crossed, so it is bullish."

Better use:
"When MACD crossed under these exact rules, did next-open forward returns improve out of sample after costs?"
```

In this project, we favored tools with stronger quantitative foundations:

- momentum
- trend following
- mean reversion / pullback behavior
- volatility normalization
- rolling z-scores
- rolling percentiles
- relative strength
- cross-asset confirmation
- breadth and participation
- positioning and options-pressure data

These are still not magic. But they are easier to define, test, and compare.

## The Basic Structure of a Quant Research Dataset

A trading research dataset usually has one row per date.

For this project, each row represented one QQQ trading day.

Conceptually, the table looks like this:

| Date | What We Know Today | What Happens Later |
| --- | --- | --- |
| 2025-01-02 | QQQ return, DXY trend, breadth, options pressure | QQQ return over next 20 days |
| 2025-01-03 | QQQ return, DXY trend, breadth, options pressure | QQQ return over next 20 days |

The left side contains features.

The right side contains targets.

## The Correct Type Of Dataset To Pull

Before building features, you need to make sure the dataset is appropriate for the question.

For equity research, the most important mistake to avoid is using the wrong price series.

There are three common price concepts:

### Raw Close

Raw close is the actual closing price reported that day.

Example:

```text
QQQ closed at 500.
```

This is useful because it is close to the real price you could trade around.

But raw close can create bad return calculations when there are dividends, splits, or other corporate actions.

### Adjusted Close

Adjusted close is the closing price after historical adjustments for splits and dividend distributions.

In simple terms:

```text
Adjusted close tries to make the historical price series comparable through time.
```

Why this matters:

- A stock split should not look like a sudden 50% crash.
- A dividend payment should not look like a mysterious price drop.
- Long-term return calculations should account for distributions.

If you calculate momentum using raw closes across a split, the signal can be completely wrong.

For example:

```text
Bad:
Price fell from 100 to 50 because of a 2-for-1 split.
The model thinks the stock crashed 50%.

Better:
Use split-adjusted or adjusted data so the move is treated correctly.
```

Adjusted close is very useful for research, but remember:

```text
Adjusted close is not the exact price you traded at on that historical day.
```

For realistic execution, use raw open/high/low/close prices for fills and adjusted or total-return data for return calculations, depending on the test.

### Total Return

Total return includes price change plus distributions, usually assuming dividends are reinvested.

For equity and ETF backtests, this is often the preferred return concept if the vendor provides it cleanly.

Example:

```text
Price return:
QQQ goes from 100 to 105 = +5%

Total return:
QQQ goes from 100 to 105 and pays a 1% dividend = about +6%
```

Why total return matters:

- It measures what an investor actually earned.
- It prevents dividend-paying assets from looking worse than they were.
- It makes comparisons across assets more fair.
- It is especially important for bonds, dividend stocks, ETFs, and long holding periods.

Best practice:

```text
Use total return when evaluating performance.
Use adjusted close when total return is unavailable.
Use raw prices for realistic entries and exits.
Keep track of which one you are using.
```

For a daily QQQ study, a good starter dataset should include:

- date
- raw open
- raw high
- raw low
- raw close
- adjusted close or total-return return
- volume
- dividends
- splits
- ticker identifier
- data source
- timestamp showing when the data was pulled

For a multi-stock universe, also try to include:

- delisted securities
- historical ticker changes
- shares outstanding
- sector / industry
- market cap
- index membership history, if testing index membership

That last point matters because survivorship bias is a real problem.

If you only test today's successful companies, the backtest quietly ignores the companies that disappeared.

## Where To Get Market Data

No data source is perfect. The right choice depends on whether the work is for a class project, personal research, or professional trading.

Here are common free, low-cost, and institutional options.

### yfinance / Yahoo Finance

yfinance is popular because it is easy to use from Python and can fetch Yahoo Finance data quickly.

Pros:

- easy to install
- good for learning
- convenient for daily bars
- can download dividends and splits
- supports adjusted OHLC behavior through `auto_adjust`

Cons:

- not officially affiliated with Yahoo
- intended for personal and educational use
- can have rate limits or occasional data issues
- not ideal for production trading systems
- terms of use matter if publishing or commercializing work

Use it for:

```text
class projects
quick prototypes
learning how to build features
rough sanity checks
```

Be careful with:

```text
professional backtests
large universe research
live trading infrastructure
```

### Alpaca

Alpaca is useful if you already have an account because it combines brokerage access with market-data APIs.

Pros:

- useful API for stocks, ETFs, crypto, and options
- good for connecting research to paper trading
- free basic market-data access exists for account holders
- historical equity data is available

Cons:

- free/basic equity data has limitations
- full market coverage may require a paid plan
- options data can be limited by feed and subscription
- options history currently starts much later than long equity history

Use it for:

```text
paper-trading workflows
API practice
daily equity data
short-sample options-pressure experiments
```

Be careful with:

```text
assuming free data is the same as full SIP/OPRA data
testing options strategies with a very short sample
mixing indicative option data with real execution assumptions
```

### Alpha Vantage

Alpha Vantage is another beginner-friendly API source.

Pros:

- simple API
- has adjusted daily data
- includes split and dividend fields
- useful for small projects

Cons:

- rate limits can be restrictive
- some adjusted endpoints or richer features may be premium
- large universe research can become slow

Use it for:

```text
small equity studies
learning API ingestion
checking adjusted close, dividends, and splits
```

### FRED

FRED is excellent for macroeconomic data.

Examples:

- interest rates
- inflation
- unemployment
- credit spreads
- yield curve series
- economic activity indicators

Pros:

- high-quality macro data
- free API access
- long history
- good documentation

Cons:

- many series update weekly, monthly, or quarterly
- some series are revised after initial release
- macro data often needs release-date handling

Use it for:

```text
macro regime features
interest-rate features
credit and liquidity context
```

Be careful with:

```text
using revised data as if it was known in real time
```

For serious macro research, ALFRED point-in-time vintages are better than only using the latest revised series.

### Nasdaq Data Link

Nasdaq Data Link has both free and premium datasets.

Pros:

- broad dataset marketplace
- useful for alternative and institutional-style datasets
- API, Python, Excel, and other access methods
- some free datasets are available

Cons:

- many of the most useful datasets are paid
- each dataset has its own schema and documentation
- free data is better for exploration than professional deployment

Use it for:

```text
finding alternative datasets
fundamental data vendors
specialized breadth, flow, or macro datasets
```

### CRSP / Institutional Data

CRSP is the academic gold standard for U.S. equity research.

Pros:

- survivor-bias-free security history
- strong corporate-action handling
- returns with and without dividends
- delisting information
- stable permanent identifiers

Cons:

- usually available through universities or paid institutional access
- not as quick to start as free APIs
- requires more data-engineering discipline

Use it for:

```text
serious academic equity research
cross-sectional stock studies
long-history backtests
survivorship-bias-sensitive research
```

### Practical Data Rule

For a beginner project:

```text
Start with yfinance or Alpaca.
Validate adjusted close, dividends, and splits.
Build the research framework.
Then upgrade the data source if the signal looks promising.
```

For a serious research project:

```text
Prefer point-in-time, adjusted, survivor-bias-aware data.
Use total returns when possible.
Store raw vendor files.
Record exactly when and how the data was downloaded.
```

## What Is A Feature?

A feature is just a column that describes the market at a specific point in time.

Examples:

- QQQ is down 3% over the last 5 days.
- QQQ is 6% below its 50-day moving average.
- DXY is above its 200-day moving average.
- LQD is outperforming AGG.
- 70% of Nasdaq-100 stocks are above their 50-day moving average.
- QQQ put volume is unusually high versus call volume.

Features should be known before the trade is placed.

That point matters a lot.

If you trade at the next open, then your features can use information available after today's close. But they cannot use tomorrow's open, tomorrow's close, or any future return.

## What Is A Target?

The target is what we are trying to predict, explain, or trade.

For example:

```text
If I see a signal after today's close,
and I buy QQQ tomorrow at the open,
what is my return after 20 trading days?
```

That target is realistic because the trade happens after the information is known.

In the QQQ project, many tests used this structure:

```text
signal after close
enter next open
exit after fixed number of trading days
subtract estimated trading cost
```

This is much better than saying:

```text
The signal uses today's close and I magically buy at today's close.
```

That can accidentally create unrealistic backtests.

## The Difference Between Price Features And Exogenous Features

Price features come from the traded asset itself.

For QQQ, price features include:

- recent QQQ returns
- QQQ moving average distance
- QQQ drawdown
- QQQ RSI
- QQQ volatility

These tell us what QQQ is doing.

Exogenous features come from outside QQQ.

Examples:

- DXY tells us about the dollar.
- LQD/AGG tells us about credit risk appetite.
- Nasdaq breadth tells us whether many stocks are participating.
- Equal-weight Nasdaq-100 versus QQQ tells us about concentration.
- DIX/GEX tells us about positioning.
- QQQ options data tells us about options pressure.

These help us understand the environment around QQQ.

That is the main reason to use them.

If QQQ is falling, we want to know:

```text
Is this just a normal pullback?
Is the dollar causing stress?
Is credit weakening?
Are only mega-cap stocks holding the index up?
Are options traders aggressively buying puts?
Is market breadth collapsing?
```

Those are different situations. They may have different forward returns.

## Important Clarification About Exogenous Variables

A beginner-friendly way to think about exogenous variables is:

```text
They are outside pieces of information that describe the market environment around the asset you are trying to trade.
```

In panel data, each row usually represents:

```text
one asset on one date
```

For example:

| Date | Asset | Features Known Today | Future Target |
| --- | --- | --- | --- |
| 2025-01-02 | QQQ | QQQ pullback, DXY trend, credit strength, breadth | QQQ next 20-day return |
| 2025-01-02 | SPY | SPY pullback, DXY trend, credit strength, breadth | SPY next 20-day return |
| 2025-01-03 | QQQ | QQQ pullback, DXY trend, credit strength, breadth | QQQ next 20-day return |

The target is the future return you are trying to estimate.

The features are the columns you know before that future return happens.

Some features come from the asset itself:

```text
QQQ recent return
QQQ distance from moving average
QQQ volatility
```

Other features come from outside the asset:

```text
DXY momentum
LQD/AGG credit ratio
Nasdaq breadth
option put/call pressure
interest rates
market-wide volatility
```

Those outside features are what this guide calls exogenous variables.

They may be repeated across many assets on the same date. For example, the same DXY trend value could appear on every stock row for January 2 because DXY describes the market environment, not one individual stock.

### The Key Point

An exogenous feature should be related to the market setup, but it must not be a disguised version of the answer.

This distinction matters.

If a feature has no relationship to future returns, it will not help.

So we do want features that might have predictive information.

But we do not want features that cheat by using the future target, revised data, or information that would not have been available at the decision time.

In plain English:

```text
Good:
This feature tells me something about the market environment before I trade.

Bad:
This feature secretly contains information from after I trade.
```

For example:

```text
Bad:
Using tomorrow's QQQ return as a feature.

Bad:
Using data that was revised later but pretending it was known today.

Bad:
Using today's option volume to trade at a price before that option volume was known.
```

Better:

```text
DXY trend known by today's close.
LQD/AGG relative strength known by today's close.
Breadth data available by today's close.
Option pressure calculated after the option market closes, then traded next open.
```

### A Useful Test

Before using any exogenous variable, ask:

1. What market condition does this variable represent?
2. Was it known before the trade decision?
3. Is it measured at the same date and frequency as the target?
4. Does it need to be lagged because it is published later?
5. Is it a real outside variable, or just the future return in disguise?
6. Does the relationship make economic sense?

For QQQ pullback research, a good exogenous question is:

```text
When QQQ is weak, does the outside market environment tell us whether that weakness is buyable?
```

Examples:

```text
QQQ is weak, but credit markets are stable.
QQQ is weak, but breadth is improving.
QQQ is weak, but DXY is not breaking higher.
QQQ is weak, but options pressure is unusually one-sided.
```

The exogenous variable is not the trade by itself.

It is context that helps decide whether the setup is attractive.

## How To Generate Features From Raw Data

This is the most important part. Raw data is rarely useful by itself. You usually need to turn it into features.

Below are the main feature types we used.

## 1. Recent Return Features

Start with price.

Suppose QQQ has a closing price each day.

A 5-day return asks:

```text
How much has QQQ moved over the last 5 trading days?
```

Formula:

```text
5-day return = close today / close 5 days ago - 1
```

Useful windows:

- 1 day
- 3 days
- 5 days
- 10 days
- 20 days
- 63 days
- 126 days
- 252 days

Why these windows?

- 1-5 days capture short-term moves.
- 20 days is about one trading month.
- 63 days is about one quarter.
- 252 days is about one trading year.

In the project, these features helped define whether QQQ was pulling back, trending, or deeply oversold.

## 2. Momentum Features

Momentum asks:

```text
Has this asset been moving persistently in one direction?
```

Example:

```text
DXY 252-day momentum = DXY close today / DXY close 252 days ago - 1
```

A positive value means DXY is up over the last year.

Momentum can be used on:

- QQQ
- SPY
- DXY
- AGG
- LQD
- gold
- oil
- volatility indexes

Momentum is one of the better-known quantitative effects. It is not guaranteed, but it is much more testable than a hand-drawn trendline.

## 3. Trend-Following Features

Trend following asks:

```text
Is price above or below a moving average?
```

Example:

```text
QQQ above 200-day moving average = 1 if QQQ close > 200-day average, else 0
```

Another version:

```text
distance from moving average = close / moving average - 1
```

If QQQ is 8% below its 200-day average:

```text
distance = -0.08
```

This gives a clean numeric feature rather than a vague chart impression.

## 4. Pullback / Mean-Reversion Features

A pullback feature asks:

```text
How far has price fallen from a recent high?
```

Example:

```text
20-day drawdown = close today / highest close in last 20 days - 1
```

If QQQ was recently 500 and is now 475:

```text
475 / 500 - 1 = -5%
```

This helps define the setup:

```text
QQQ is weak enough to be interesting.
```

But we still need context:

```text
Is this pullback buyable, or is it part of a larger breakdown?
```

That is where exogenous variables come in.

## 5. Volatility Features

Volatility asks:

```text
How noisy or unstable has price been recently?
```

Simple version:

```text
20-day realized volatility = standard deviation of daily returns over 20 days
```

Why it matters:

- A 2% drop means something different in a calm market than in a crisis market.
- Signals should often be interpreted relative to volatility.

This leads to volatility-adjusted features.

Example:

```text
volatility-adjusted return = recent return / recent volatility
```

That helps compare moves across calm and volatile regimes.

## 6. Normalized Features

Normalization is one of the most important tools in this project.

Many raw values drift over time. A raw threshold that worked in one period may not mean the same thing later.

Two common normalization tools:

### Z-Score

A z-score asks:

```text
How unusual is today's value compared with its recent history?
```

Formula:

```text
z-score = (today's value - rolling average) / rolling standard deviation
```

Example:

```text
DIX z-score over 252 days
```

This tells us whether DIX is unusually high or low versus its own recent history.

### Rolling Percentile

A rolling percentile asks:

```text
Where does today's value rank versus the last N days?
```

Example:

```text
If today's DXY level is higher than 90% of the last 252 days,
its rolling percentile is 0.90.
```

This is often easier to explain than a z-score.

Useful percentiles:

- below 0.10 = unusually low
- above 0.90 = unusually high

Normalization is especially useful for:

- DIX/GEX
- volatility
- credit spreads
- breadth
- option volume
- dollar strength

## 7. Relative Strength Features

Relative strength compares one asset to another.

Example:

```text
LQD / AGG ratio
```

LQD is investment-grade corporate bonds. AGG is broad bonds.

If LQD is outperforming AGG, credit conditions may be healthier. If LQD is underperforming AGG, investors may be avoiding credit risk.

Another example:

```text
equal-weight Nasdaq-100 / QQQ
```

If equal-weight Nasdaq is outperforming QQQ, strength may be broad. If QQQ is outperforming equal-weight Nasdaq, the index may be driven by a few mega-cap names.

Relative features are useful because they often describe market structure better than a single price series.

## 8. Breadth Features

Breadth asks:

```text
How many stocks are participating?
```

Examples:

- percent of Nasdaq-100 stocks above their 20-day moving average
- percent above 50-day moving average
- percent above 200-day moving average
- advance/decline line
- new highs minus new lows

Why this matters:

```text
QQQ can look strong because a few mega-cap names are strong,
even if many stocks underneath are weak.
```

Breadth features help reveal whether the index move is broad or narrow.

## 9. Concentration Features

Concentration asks:

```text
Is the index being driven by a small number of large stocks?
```

Examples:

- top-5 weight
- top-10 weight
- equal-weight Nasdaq-100 versus QQQ
- QQQ excluding top holdings

If QQQ is up but equal-weight Nasdaq is weak, the rally may be narrow.

If QQQ is down but breadth is improving, the pullback may be less dangerous.

These are hypotheses. They still need to be tested.

## 10. Positioning Features

Positioning data tries to describe how investors or dealers are positioned.

In this project:

- DIX was used as one positioning measure.
- GEX was used as another.

Raw DIX/GEX values were tested, but we also created normalized versions:

- rolling z-scores
- rolling percentiles
- changes over 5, 20, or 63 days

The reason:

```text
A raw GEX value may not mean the same thing in every market regime.
```

Normalization helps ask:

```text
Is GEX unusually high or low compared with its own recent history?
```

## 11. Option-Pressure Features

Options data is more advanced, but the feature logic is still understandable.

Raw data:

- each QQQ option contract
- date
- call or put
- strike
- expiration
- volume
- price

From that, we generated daily features.

Examples:

### Put/Call Volume Ratio

```text
put volume / call volume
```

High values can mean more put activity relative to call activity.

### Put/Call Premium Ratio

```text
put premium traded / call premium traded
```

This weighs the dollar value of options traded, not just contract count.

### DTE Buckets

DTE means days to expiration.

We grouped option volume by time to expiration:

- 0-7 days
- 8-14 days
- 15-30 days
- 31-60 days
- 61-90 days

Why?

Short-dated option activity can mean something different from longer-dated option activity.

### ATM and OTM Volume

ATM means at-the-money.

OTM means out-of-the-money.

We measured how much option volume was near the current QQQ price versus further away.

This can help distinguish:

- ordinary hedging
- speculative put buying
- short-dated event trading
- broad options activity

Important limitation:

Our accessible Alpaca options sample currently starts in 2025 and has 336 daily feature rows. That is useful for exploratory analysis, but not enough to make strong claims.

## How To Combine Features Into A Signal

A simple signal has two parts:

```text
setup + confirmation
```

In this project:

```text
setup = QQQ is weak or pulling back
confirmation = outside market data says the setup is attractive
```

Example in plain English:

```text
QQQ has pulled back sharply,
AND
credit/risk appetite has not broken down.
```

Another example:

```text
QQQ is oversold,
AND
Nasdaq breadth is improving.
```

Another:

```text
QQQ is weak,
AND
option put pressure is unusually high or low.
```

The exact thresholds are not guessed by eye. They are generated from the training data using quantiles, fixed cutoffs, or normalized levels.

## Why We Use Simple Rules First

It is tempting to jump straight to machine learning.

But simple rules are valuable because:

- they are easier to understand
- they are easier to debug
- they are less likely to overfit
- they create a baseline
- they force us to explain the economic logic

A neural network or complex model should be compared against simple baselines.

In this project, complex models like autoencoders and TCNs were treated as regime detectors, not magic trading machines.

The question was:

```text
Does the model add anything beyond simple intermarket signals like DXY momentum or LQD/AGG?
```

That is the right standard.

## How Backtesting Should Work

A backtest should copy the real decision process as closely as possible.

### Step 1: Signal Time

Decide when the signal is known.

For daily data:

```text
Signal is known after today's close.
```

### Step 2: Entry Time

Use a realistic entry.

```text
Enter at tomorrow's open.
```

### Step 3: Exit Rule

Use a fixed rule.

Examples:

- exit after 5 trading days
- exit after 20 trading days
- exit after 60 trading days

Do not choose the exit after seeing the result.

### Step 4: Costs

Subtract trading costs.

Even small costs matter because many strategies have small average edges.

### Step 5: Avoid Overlapping Trades

If a signal fires every day for a week, do not count that as seven independent trades if all seven trades are basically the same market event.

The cleaner approach:

```text
Enter one trade.
Ignore new signals until that trade exits.
```

This gives a more honest trade count.

## Train, Validation, Test, And Walk-Forward

The biggest danger in quant research is overfitting.

Overfitting means:

```text
The rule learned the past, not the market.
```

To fight this, split history into periods.

Example:

| Period | Purpose |
| --- | --- |
| Train | Find candidate rules |
| Validation | Choose among candidates |
| Test / OOS | Evaluate final behavior |

OOS means out of sample.

It is the data the strategy did not get to use when choosing rules.

## Walk-Forward Testing

Walk-forward testing is even more realistic.

It works like this:

```text
Use the last few years to choose a rule.
Trade the next year.
Move forward.
Repeat.
```

This simulates how a strategy would be updated over time.

It also prevents a common mistake:

```text
choosing one rule using the full history, then pretending it was known all along
```

## Multiple Testing: The Hidden Trap

If you test thousands of rules, some will look good by luck.

This is one of the biggest traps in trading research.

Example:

```text
Test 10,000 random rules.
Some will look amazing.
That does not mean they are real.
```

To control this, we used:

- minimum trade counts
- validation periods
- out-of-sample periods
- walk-forward testing
- non-overlapping trades
- multiple-comparison controls
- comparisons against simple baselines

The best-looking rule is not always the best rule. The best rule is the one that survives the most honest tests.

## From Research Signal To Live Monitoring Pipeline

Finding a signal in a backtest is not the end.

It is the beginning of a production problem.

Once a signal looks promising, it needs to become a repeatable pipeline.

Think of it like this:

```text
data pull
data validation
feature generation
signal calculation
trade decision
execution
performance tracking
drift monitoring
review / retraining
```

This is similar to ML-ops, but for trading signals.

The goal is not just to create a model.

The goal is to keep asking:

```text
Is the signal still behaving like it did in the backtest?
```

### What To Monitor

At minimum, monitor:

- missing data
- delayed data
- schema changes
- extreme feature values
- feature distribution changes
- signal frequency
- trade count
- average return per trade
- win rate
- drawdown
- slippage versus assumption
- live returns versus backtest expectations

The signal can fail even if the code still runs.

That is why monitoring matters.

### Feature Drift

Feature drift means the input data no longer looks like the data used during research.

Example:

```text
DIX values are now much higher or lower than the historical range used in training.
```

Another example:

```text
QQQ option volume explodes because short-dated options become more popular.
```

If a feature drifts, thresholds from the old backtest may stop meaning the same thing.

This is one reason rolling z-scores and rolling percentiles are helpful.

They adapt better than fixed raw thresholds.

### Signal Drift

Signal drift means the strategy behavior changes.

Examples:

- the signal used to fire 20 times per year, but now fires 100 times
- average holding-period return falls below historical expectations
- drawdowns become deeper than expected
- slippage is much worse than assumed
- the signal only works in one asset but not related assets

This does not automatically mean the signal is dead.

But it means the signal needs review.

### A Simple Monitoring Table

Create a daily or weekly monitoring table like this:

| Check | Question |
| --- | --- |
| Data freshness | Did every source update on time? |
| Data quality | Are there missing or impossible values? |
| Feature drift | Are feature distributions changing? |
| Signal frequency | Is the rule firing too often or too rarely? |
| Performance drift | Are live returns matching the backtest range? |
| Execution drift | Are actual fills worse than expected? |
| Regime drift | Is the current market unlike the training sample? |

If a signal is important enough to trade, it is important enough to monitor.

## ML Techniques For Market Regime Clustering

Machine learning can help identify market regimes, but it should be used carefully.

The goal is not:

```text
Use a neural network because it sounds advanced.
```

The goal is:

```text
Group similar market environments,
then test whether those environments have different forward returns.
```

In regime research, the model usually should not directly say:

```text
Buy QQQ tomorrow.
```

It should first help answer:

```text
What kind of market are we in?
```

Then the backtest asks:

```text
Does this QQQ setup perform differently in this regime?
```

### K-Means Clustering

K-means groups days into clusters based on feature similarity.

Example features:

- QQQ recent return
- QQQ volatility
- DXY momentum
- LQD/AGG trend
- breadth percentile
- option put/call ratio percentile

Plain-English interpretation:

```text
These days look similar to each other across several market variables.
```

Pros:

- easy to understand
- fast
- good baseline

Cons:

- clusters can be unstable
- assumes simple cluster shapes
- needs scaled features

### Gaussian Mixture Models

Gaussian mixture models are like a softer version of clustering.

Instead of forcing each day into one bucket, they estimate probabilities.

Example:

```text
Today is 70% like regime A and 30% like regime B.
```

This can be useful because markets often transition gradually.

### Hidden Markov Models

Hidden Markov models are designed for sequences.

They assume the market moves through hidden states, such as:

- calm bull market
- volatile rally
- risk-off selloff
- recovery

The useful idea is that today's regime is related to yesterday's regime.

That makes them more natural for time series than ordinary clustering.

### Autoencoders

An autoencoder is a neural network that compresses data into a smaller representation, then tries to reconstruct the original input.

The compressed representation can reveal patterns.

Example:

```text
Start with 50 market features.
Compress them into 2 or 3 latent dimensions.
Cluster the compressed representation.
Test whether the clusters have different forward returns.
```

Autoencoders can be useful when you have many related features.

But they need a high bar because they can easily find patterns that look interesting but do not trade well.

### Sequence Models

Markets are sequences, not independent rows.

Sequence models try to learn from the order of observations.

Examples:

- temporal convolutional networks
- recurrent neural networks
- LSTMs / GRUs
- transformer-style time-series models

For a QQQ regime problem, a sequence model might look at the last 60 trading days of features and estimate the next-period return or regime.

The important question is:

```text
Does the sequence model add information beyond simple baselines like momentum, trend, and normalized cross-asset features?
```

If not, the simpler model is usually better.

### How To Test Regime Clusters

Do not stop after drawing a nice cluster chart.

Test the clusters:

1. Build features using only past information.
2. Fit the clustering model on the training period.
3. Assign regimes to the test period without refitting on the future.
4. Measure forward returns by regime.
5. Test whether a trading setup improves in specific regimes.
6. Compare against simple baselines.
7. Repeat through walk-forward splits.

The cluster is not alpha by itself.

The cluster only matters if it improves a decision.

## A Simple Feature-Building Recipe

For any new dataset, use this process.

### Step 1: Ask What The Dataset Represents

Examples:

```text
DXY = dollar strength
LQD/AGG = credit risk appetite
Breadth = participation
Options volume = positioning or hedging pressure
```

### Step 2: Decide The Time Grain

For this project:

```text
one row per QQQ trading day
```

Everything must be aligned to that daily calendar.

### Step 3: Convert Raw Values Into Features

For every raw series, consider:

- recent return
- moving-average distance
- rolling z-score
- rolling percentile
- relative ratio
- change over 5/20/63 days
- volatility-adjusted value

### Step 4: Check Data Availability

Ask:

- When does the data start?
- How often is it missing?
- Was it known at the time?
- Is it revised later?
- Does it need to be lagged?

### Step 5: Test It As A Confirmation Filter

Do not ask:

```text
Can this feature predict everything?
```

Ask:

```text
When QQQ is in a specific setup, does this feature improve the forward return distribution?
```

That is a much more realistic research question.

## Practical Checklist

Use this checklist before trusting any signal:

1. Can I define the signal without looking at a chart?
2. Is every feature known before the trade?
3. Is the entry price realistic?
4. Did I subtract costs?
5. Did I test out of sample?
6. Did I avoid overlapping trade inflation?
7. Did I compare against a simple baseline?
8. Did I test enough trades?
9. Did I account for trying many rules?
10. Does the result make economic sense?

If the answer is no, the signal is not ready.

## How To Vibe Code This Research With Codex

"Vibe coding" quant research does not mean skipping rigor.

It means using Codex to move faster while you stay responsible for the research question, data quality, and validation standard.

Codex is especially helpful for:

- turning a vague trading idea into a testable hypothesis
- writing data fetchers and join scripts
- creating feature-generation pipelines
- running backtests across many candidate rules
- checking for lookahead bias and unrealistic execution assumptions
- summarizing results into a report or GitHub Pages site
- converting repeated workflows into reusable skills

The important habit is to ask Codex for evidence, not just code.

Weak prompt:

```text
Find me a profitable QQQ strategy.
```

Better prompt:

```text
Build a next-open walk-forward test for QQQ pullback entries.
Use only features known after today's close.
Compare against a simple baseline.
Report trade count, non-overlap returns, costs, and out-of-sample performance.
Flag leakage risks.
```

### A Good Codex Research Loop

Use this loop:

1. State the hypothesis in plain English.
2. Ask Codex to inspect the available files and schemas.
3. Build one clean feature table.
4. Add data-quality checks.
5. Generate simple baseline rules first.
6. Backtest with realistic next-open execution.
7. Split train/test or use walk-forward testing.
8. Ask Codex to review the backtest for bias.
9. Save results as tables and plots.
10. Convert repeated steps into skills.

The point is not to let Codex "guess the answer."

The point is to make the research process reproducible.

### Skills Make Codex More Useful

A skill is a reusable instruction file that tells Codex how to behave for a specific kind of task.

Instead of explaining the same process every time, you can create a `SKILL.md` file once and reuse it.

For this kind of project, useful skills include:

- quant research framing
- market data ingestion
- data-quality auditing
- backtest review
- market regime modeling
- signal monitoring and ML-ops
- GitHub publishing

Below are complete `SKILL.md` snippets a classmate could copy into their own Codex skills folder.

They are intentionally short. A good skill should guide Codex without filling the context window with unnecessary detail.

### Skill Snippet: Quant Alpha Research

````markdown
---
name: quant-alpha-research
description: Use when turning a market hypothesis into testable datasets, features, signal rules, backtests, or research reports for equities, ETFs, cross-asset signals, options pressure, or market regimes.
---

# Quant Alpha Research

You help convert trading ideas into reproducible quantitative research.

## Workflow

1. Restate the hypothesis in plain English.
2. Define the traded asset, universe, date range, holding period, and target return.
3. Identify which data is known before the trade and which data would leak the future.
4. Build simple baseline features before complex models.
5. Prefer total-return data when available, adjusted close when total return is unavailable, and raw prices for realistic fills.
6. Create features using momentum, trend, pullback, volatility, normalization, relative strength, breadth, positioning, and exogenous variables.
7. Test with train/test or walk-forward splits.
8. Report out-of-sample performance, trade count, costs, drawdown, and robustness.
9. State caveats clearly. Never present a backtest as a guarantee.

## Guardrails

- Do not use future data in features.
- Do not optimize on the full sample and call it out-of-sample.
- Do not trust chart patterns or off-the-shelf indicators unless they survive statistical testing.
- Prefer simple, interpretable baselines before neural networks.
- Save datasets, plots, and reports to files instead of dumping large outputs into chat.

## Output

End with:

- what was tested
- what data was used
- what assumptions were made
- what passed or failed
- what should be tested next
````

### Skill Snippet: Market Data Engineer

````markdown
---
name: market-data-engineer
description: Use when pulling, validating, joining, or documenting market datasets such as OHLCV, adjusted close, total return, fundamentals, breadth, options, macro, or alternative data.
---

# Market Data Engineer

You build clean, reproducible market-data pipelines.

## Workflow

1. Identify the dataset grain: daily, intraday, option contract, ticker-date, or macro release date.
2. Confirm the required columns: date, symbol, open, high, low, close, adjusted close or total return, volume, dividends, splits, and source metadata.
3. Preserve raw vendor files before transforming them.
4. Normalize dates, symbols, time zones, and trading calendars.
5. Validate missing values, duplicate keys, impossible prices, stale rows, and schema changes.
6. Lag data when the real-world release time requires it.
7. Join datasets only after confirming that the join key and timestamp logic are correct.
8. Write a data dictionary for every generated feature file.

## Guardrails

- Never paste API keys or secrets into code, reports, or chat.
- Do not assume adjusted close and total return are the same thing.
- Do not use revised macro data as if it was available in real time.
- Do not silently forward-fill important missing data.
- Record the vendor, endpoint, pull date, and transformation script.

## Output

Produce:

- raw-data path
- cleaned-data path
- row count
- date range
- schema
- quality issues
- recommended next transformation
````

### Skill Snippet: Backtest Auditor

````markdown
---
name: backtest-auditor
description: Use when reviewing a trading backtest for lookahead bias, survivorship bias, unrealistic fills, overlapping trades, costs, overfitting, and out-of-sample validity.
---

# Backtest Auditor

You review trading backtests like a skeptical research lead.

## Checklist

1. Confirm when each feature is known.
2. Confirm entry and exit prices are realistic.
3. Prefer next-open execution when the signal is calculated after the close.
4. Check whether returns use total return, adjusted close, or raw prices.
5. Verify transaction costs, slippage, and borrow or financing assumptions.
6. Check for overlapping trade inflation.
7. Check train/test, validation, and walk-forward design.
8. Check whether many rules were tested and whether multiple-comparison risk was addressed.
9. Compare the strategy against simple baselines.
10. Separate in-sample discovery from out-of-sample evidence.

## Common Failure Modes

- buying at the same close used to create the signal
- using future constituents or surviving tickers only
- using revised data without release-date handling
- selecting the best rule from thousands of tests
- reporting high Sharpe with too few trades
- ignoring days when the signal failed to fetch data

## Output

Lead with the biggest risks first.

For each issue, include:

- severity
- why it matters
- where it appears
- how to fix or retest it
````

### Skill Snippet: Market Regime ML

````markdown
---
name: market-regime-ml
description: Use when testing clustering, autoencoders, hidden Markov models, temporal convolutional networks, or other ML models for market regime detection in trading research.
---

# Market Regime ML

You use machine learning to identify market regimes, not to create black-box trading claims.

## Workflow

1. Define the regime question in plain English.
2. Build only point-in-time features known before the trade.
3. Scale or normalize features before clustering.
4. Start with simple baselines: k-means, Gaussian mixture models, or Hidden Markov Models.
5. Use autoencoders only when feature dimensionality is high enough to justify compression.
6. Use sequence models only when the order of observations is central to the hypothesis.
7. Fit models on training data and assign regimes to test data without peeking ahead.
8. Test whether regimes improve a trading decision, not whether the chart looks interesting.
9. Compare against simple momentum, trend, volatility, and cross-asset baselines.

## Guardrails

- Do not cluster on future returns.
- Do not refit on the full sample before evaluating test results.
- Do not treat colorful cluster plots as evidence of alpha.
- Do not use neural networks without a simple baseline.

## Output

Report:

- model type
- features used
- train/test split
- number of regimes
- forward returns by regime
- whether the regime improves a specific setup
- whether it beats simple baselines
````

### Skill Snippet: Signal Monitoring ML-Ops

````markdown
---
name: signal-monitoring-mlops
description: Use when moving a research signal into scheduled production, monitoring data quality, feature drift, signal drift, execution drift, or live performance decay.
---

# Signal Monitoring ML-Ops

You turn a research signal into a monitored production workflow.

## Workflow

1. Define the daily schedule: data pull, validation, feature build, signal calculation, and report generation.
2. Add data freshness checks for every source.
3. Add schema checks for every input file.
4. Track feature distributions versus the research sample.
5. Track signal frequency versus the backtest range.
6. Track live or paper-traded fills versus assumed fills.
7. Track performance by trade, month, and regime.
8. Alert when drift or missing data makes the signal unreliable.
9. Keep a decision log explaining when the signal was changed, paused, or retired.

## Drift Checks

Monitor:

- missing rows
- stale data
- outlier values
- rolling z-score distribution
- rolling percentile distribution
- signal count
- trade count
- win rate
- average return
- drawdown
- slippage

## Guardrails

- Do not trade when required data is missing.
- Do not silently change thresholds after live underperformance.
- Do not retrain without preserving the old model and old results.
- Do not confuse paper-trading success with production execution quality.

## Output

Produce a short monitoring report with:

- green/yellow/red status
- failed checks
- latest signal state
- recent performance
- recommended action
````

### Skill Snippet: GitHub Research Publisher

````markdown
---
name: github-research-publisher
description: Use when preparing a quant research project for GitHub, GitHub Pages, a class submission, or a shareable research artifact.
---

# GitHub Research Publisher

You package research so someone else can understand and reproduce it.

## Workflow

1. Identify which files are meant to be shared.
2. Exclude secrets, raw vendor data, cache folders, and large private datasets.
3. Create or update a clear README or GitHub Pages site.
4. Include the research question, dataset description, feature logic, backtest assumptions, results, and caveats.
5. Add instructions for regenerating reports or pages.
6. Check that links, images, and charts render.
7. Commit only the intended files.
8. Push to GitHub only after confirming the repository and branch.

## Guardrails

- Never commit API keys, `.env` files, credentials, or paid vendor data.
- Do not stage the whole working tree if unrelated files exist.
- Do not publish a private research folder without confirming the target repository and visibility.
- Prefer a small shareable docs site over a messy full research dump.

## Output

Report:

- files changed
- files intentionally excluded
- local validation performed
- branch
- commit hash
- published URL or remaining blocker
````

## Useful Data-Source Links

These are good starting points for learning what each provider offers:

- [Alpaca Market Data API](https://docs.alpaca.markets/docs/about-market-data-api)
- [Alpaca Options Market Data](https://docs.alpaca.markets/docs/options-market-data)
- [yfinance documentation](https://ranaroussi.github.io/yfinance/)
- [Alpha Vantage API documentation](https://www.alphavantage.co/documentation/)
- [FRED API documentation](https://fred.stlouisfed.org/docs/api/fred/)
- [Nasdaq Data Link documentation](https://docs.data.nasdaq.com/)
- [CRSP U.S. Stock Databases](https://www.crsp.org/research/crsp-us-stock-databases/)

## Final Takeaway

Do not rely on chart patterns, MACD, Bollinger Bands, or hand-drawn lines unless they survive the same statistical testing as everything else.

The better workflow is:

```text
Start with a market hypothesis.
Collect data that describes that hypothesis.
Turn raw data into clean features.
Normalize those features.
Use simple rules first.
Backtest with realistic execution.
Validate out of sample.
Only trust what survives.
```

The strongest lesson is:

> More data is useful only when it helps describe a real market state. It does not automatically create alpha.

The best framework is not "find the perfect indicator." It is:

> Define a QQQ setup, then use economically meaningful exogenous features to decide whether that setup is worth trading.
