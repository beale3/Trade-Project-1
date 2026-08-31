"""
Rolling Watchlist + Pivot/Red-to-Green Pattern Detector
--------------------------------------------------------
Implements the "rolling watchlist" methodology for finding penny stocks that
break the typical spike-and-die lifecycle:

  1. ROLLOVER CHECK (daily data): find stocks that had a big one-day gain
     recently and have "held up" since (haven't given back too much of the
     move). These are the ones that would still be on your watchlist.

  2. INTRADAY PATTERN CHECK (5-min data): for stocks that pass the rollover
     check, look for the "weak open red-to-green" / pivot alignment setup --
     price crossing above the prior day's close (red-to-green) while also
     trading above the standard floor-trader pivot point.

IMPORTANT DATA LIMITATIONS (read before relying on this):
  - There's no free live "gainers scanner" API wired in here. You supply the
    candidate ticker list yourself (e.g., from StocksToTrade, Finviz, your
    broker's scanner, etc.) -- this script doesn't discover them for you.
  - Daily + intraday OHLCV now come from Massive (formerly Polygon.io) via
    its /v2/aggs/ticker/.../range/... endpoint, not yfinance -- requires a
    MASSIVE_API_KEY (env var, or a massive_api_key.txt file next to this
    script or one directory up). Massive's history depth is far deeper than
    yfinance's ~60-day 5-minute cap; actual limits depend on your plan tier.
  - "Held up" and "big gainer" thresholds are configurable judgment calls
    (see --gain-threshold and --pullback-threshold) since the source
    material describes the idea qualitatively, not with exact numbers.

Usage:
    python rolling_watchlist.py --tickers OBAI,AAPL,GME --gain-threshold 20 --pullback-threshold 50
"""

import argparse
import os
import re
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _resolve_massive_api_key() -> str:
    """
    Resolves the Massive API key: env var first, then a massive_api_key.txt
    file (checked next to this script, then one directory up -- the repo
    root when this script lives under tools/). Returns None if not found
    anywhere. Caches into the environment once found, so it's read at most
    once per process.
    """
    key = os.environ.get("MASSIVE_API_KEY")
    if key:
        return key
    here = os.path.dirname(os.path.abspath(__file__))
    for candidate_dir in (here, os.path.dirname(here)):
        path = os.path.join(candidate_dir, "massive_api_key.txt")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("MASSIVE_API_KEY="):
                        value = line.split("=", 1)[1].strip()
                        if value:
                            os.environ["MASSIVE_API_KEY"] = value
                            return value
    return None


def _period_to_days(period: str) -> int:
    """Converts a yfinance-style period string ('3mo', '5d', '1y') to a day count."""
    m = re.match(r"^(\d+)(d|mo|y)$", period.strip().lower())
    if not m:
        raise ValueError(f"Unsupported period format: {period!r}")
    n, unit = int(m.group(1)), m.group(2)
    return {"d": n, "mo": n * 30, "y": n * 365}[unit]


def _interval_to_multiplier_timespan(interval: str):
    """Converts a yfinance-style interval ('5m', '1h', '1d') to Massive's (multiplier, timespan)."""
    m = re.match(r"^(\d+)(m|h|d)$", interval.strip().lower())
    if not m:
        raise ValueError(f"Unsupported interval format: {interval!r}")
    n, unit = int(m.group(1)), m.group(2)
    return n, {"m": "minute", "h": "hour", "d": "day"}[unit]


def _massive_aggs(ticker: str, days_back: int, multiplier: int, timespan: str) -> pd.DataFrame:
    """
    Fetches OHLCV bars from Massive's aggregates endpoint and returns a
    DataFrame shaped exactly like the old yfinance output (DatetimeIndex,
    columns Open/High/Low/Close/Volume) -- every downstream caller (the
    rollover check, the guardrail scanner, the S3 score, the P&D phase
    classifier, the pattern detectors, the trade simulator) needs no changes.
    """
    api_key = _resolve_massive_api_key()
    if not api_key:
        print(f"  [Massive OHLCV lookup skipped for {ticker}: MASSIVE_API_KEY not found "
              f"(env var or massive_api_key.txt)]")
        return pd.DataFrame()

    try:
        import requests
    except ImportError:
        sys.exit("requests is not installed. Run:\n  pip install requests")

    to_date = pd.Timestamp.now(tz="America/New_York").date()
    from_date = to_date - pd.Timedelta(days=days_back)

    try:
        resp = requests.get(
            f"https://api.massive.com/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/"
            f"{from_date}/{to_date}",
            params={"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": api_key},
            timeout=15,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except Exception as e:
        print(f"  [Massive OHLCV lookup failed for {ticker}: {e}]")
        return pd.DataFrame()

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    # Epoch ms UTC -> US market time, tz-naive -- so daily bars land on the
    # correct trading date and intraday bars align with the 9:30/16:00
    # session boundaries the pattern detectors use (same conversion as the
    # massive_loader.py adapter this replaces the CSV-handoff path of).
    df["date"] = (pd.to_datetime(df["t"], unit="ms", utc=True)
                   .dt.tz_convert("America/New_York").dt.tz_localize(None))
    df = df.set_index("date").sort_index()
    df = df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"})
    return df[["Open", "High", "Low", "Close", "Volume"]]


def load_daily(ticker: str, period: str = "3mo") -> pd.DataFrame:
    """Loads daily OHLCV bars from Massive (formerly yfinance)."""
    return _massive_aggs(ticker, _period_to_days(period), multiplier=1, timespan="day")


def load_intraday(ticker: str, period: str = "5d", interval: str = "5m", prepost: bool = True) -> pd.DataFrame:
    """
    Loads intraday OHLCV bars from Massive (formerly yfinance). `prepost` is
    unused -- Massive's aggs endpoint includes all session bars by default;
    kept only for call-site compatibility with the old yfinance signature.
    """
    multiplier, timespan = _interval_to_multiplier_timespan(interval)
    return _massive_aggs(ticker, _period_to_days(period), multiplier, timespan)


# ---------------------------------------------------------------------------
# 1) Rollover check -- which past gainers are still holding up
# ---------------------------------------------------------------------------

def find_recent_spike(daily_df: pd.DataFrame, lookback_days: int = 5, gain_threshold_pct: float = 20.0):
    """
    Looks at the trailing `lookback_days` trading days (not counting today)
    for a day where Close gained >= gain_threshold_pct vs. the prior close.
    Returns the MOST RECENT such spike as (index_position, date, gain_pct),
    or (None, None, None) if there isn't one.
    """
    close = daily_df["Close"]
    pct_change = close.pct_change() * 100

    n = len(daily_df)
    window_start = max(1, n - lookback_days)
    for i in range(n - 1, window_start - 1, -1):  # most recent first
        if pct_change.iloc[i] >= gain_threshold_pct:
            return i, daily_df.index[i], pct_change.iloc[i]
    return None, None, None


def check_holding_up(daily_df: pd.DataFrame, spike_idx: int, pullback_threshold_pct: float = 50.0):
    """
    "Holding up" = price hasn't retraced more than pullback_threshold_pct of
    the spike-day's gain, at any point from the spike day through today.

    Returns dict with: holding (bool), floor_price, worst_retracement_pct,
    current_retracement_pct.
    """
    close = daily_df["Close"]
    spike_close = close.iloc[spike_idx]
    pre_spike_close = close.iloc[spike_idx - 1]
    gain = spike_close - pre_spike_close

    if gain <= 0:
        return {"holding": False, "floor_price": None, "worst_retracement_pct": None,
                "current_retracement_pct": None}

    floor_price = pre_spike_close + gain * (1 - pullback_threshold_pct / 100)
    post_spike = close.iloc[spike_idx:]

    worst_price = post_spike.min()
    worst_retracement_pct = (spike_close - worst_price) / gain * 100
    current_retracement_pct = (spike_close - post_spike.iloc[-1]) / gain * 100
    holding = worst_price >= floor_price

    return {
        "holding": bool(holding),
        "floor_price": float(floor_price),
        "worst_retracement_pct": float(worst_retracement_pct),
        "current_retracement_pct": float(current_retracement_pct),
    }


def scan_rollover_watchlist(daily_data_by_ticker: dict, lookback_days: int = 5,
                             gain_threshold_pct: float = 20.0,
                             pullback_threshold_pct: float = 50.0) -> pd.DataFrame:
    """
    daily_data_by_ticker: dict of {ticker: daily OHLC DataFrame}.
    Returns a summary DataFrame, one row per ticker that HAD a qualifying
    spike in the lookback window (whether or not it's still holding up),
    sorted with the ones still holding up first.
    """
    rows = []
    for ticker, df in daily_data_by_ticker.items():
        if df is None or df.empty or len(df) < lookback_days + 2:
            continue
        idx, date, gain_pct = find_recent_spike(df, lookback_days, gain_threshold_pct)
        if idx is None:
            continue
        hold_info = check_holding_up(df, idx, pullback_threshold_pct)
        rows.append({
            "ticker": ticker,
            "spike_date": date.date() if hasattr(date, "date") else date,
            "spike_gain_pct": round(gain_pct, 1),
            "holding_up": hold_info["holding"],
            "current_retracement_pct": None if hold_info["current_retracement_pct"] is None
                                        else round(hold_info["current_retracement_pct"], 1),
            "worst_retracement_pct": None if hold_info["worst_retracement_pct"] is None
                                     else round(hold_info["worst_retracement_pct"], 1),
            "last_close": round(df["Close"].iloc[-1], 4),
        })

    if not rows:
        return pd.DataFrame(columns=["ticker", "spike_date", "spike_gain_pct", "holding_up",
                                      "current_retracement_pct", "worst_retracement_pct", "last_close"])

    result = pd.DataFrame(rows)
    return result.sort_values(["holding_up", "spike_gain_pct"], ascending=[False, False]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# News catalyst lookup
#
# A 917-observation backtest (C:/Users/beale/catalyst-study/
# CATALYST_STUDY_FINDINGS.md) tested whether this keyword-heuristic catalyst
# label predicts forward returns for this cohort. It doesn't: the one nominal
# "beats naive baseline" result (1-day horizon, leave-one-out CV) didn't
# survive an independent 5-fold CV check, and the other two horizons never
# beat naive at all. So `has_catalyst` below is real (not a stub) but
# defaults to NON-GATING everywhere it's used -- see `catalyst_gates` on
# scan_guardrail_criteria() and compute_s3_score().
# ---------------------------------------------------------------------------

CATALYST_KEYWORDS = [
    "earnings", "revenue", "guidance", "eps", "quarterly results",
    "merger", "acquisition", "acquire", "acquired", "buyout", "takeover",
    "fda", "clinical trial", "phase 1", "phase 2", "phase 3", "approval",
    "contract", "agreement", "partnership", "collaboration", "patent",
    "license", "licensing", "offering", "ipo", "uplisting", "dividend",
    "buyback", "upgrade", "downgrade", "price target", "appoint", "resign",
    "ceo", "cfo", "bankruptcy", "restructuring", "lawsuit", "settlement",
    "recall", "delisting", "reverse split", "spin-off", "joint venture",
    "government contract", "grant", "award",
]


def lookup_recent_catalyst(ticker: str, lookback_days: int = 4, api_key: str = None):
    """
    Looks for company-specific catalyst news on `ticker` in the last
    `lookback_days` calendar days, using the same endpoint and keyword
    heuristic as the catalyst-study backtest referenced above.

    Requires a Massive/Polygon API key, via the MASSIVE_API_KEY env var or
    the api_key argument. Returns None (not False) if the key is missing or
    the request fails -- "couldn't check" is a different thing from
    "checked, found nothing", and callers should not silently treat a lookup
    failure as a confirmed no-catalyst reading.
    """
    api_key = api_key or _resolve_massive_api_key()
    if not api_key:
        print(f"  [catalyst lookup skipped for {ticker}: MASSIVE_API_KEY not set]")
        return None

    try:
        import requests
    except ImportError:
        print(f"  [catalyst lookup skipped for {ticker}: requests is not installed]")
        return None

    since = (pd.Timestamp.now("UTC") - pd.Timedelta(days=lookback_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        resp = requests.get(
            "https://api.massive.com/v2/reference/news",
            params={
                "ticker": ticker,
                "published_utc.gte": since,
                "limit": 50,
                "sort": "published_utc",
                "order": "desc",
                "apiKey": api_key,
            },
            timeout=10,
        )
        resp.raise_for_status()
        articles = resp.json().get("results", [])
    except Exception as e:
        print(f"  [catalyst lookup failed for {ticker}: {e}]")
        return None

    if not articles:
        return False

    blob = " ".join(
        f"{a.get('title', '')} {a.get('description', '')} {' '.join(a.get('keywords', []) or [])}"
        for a in articles
    ).lower()
    return any(term in blob for term in CATALYST_KEYWORDS)


# ---------------------------------------------------------------------------
# Short-interest lookup
#
# Unlike the catalyst backtest above, the 917-observation short-interest
# backtest (C:/Users/beale/short-interest-study/
# SHORT_INTEREST_STUDY_FINDINGS.md) found a real (if modest) out-of-sample
# edge: log(days_to_cover) beats a naive baseline at the 1-day and 1-month
# horizons, robustly across both leave-one-out CV and 30 independent 5-fold
# CV seeds (96.7% / 93.3% of seeds agree -- not a single-seed fluke like the
# catalyst study's fragile result). Higher short interest predicted BETTER
# forward returns for this cohort, consistent with short-squeeze
# continuation. Effect size is small (~0.1-0.15% RMSE improvement), so
# `short_interest_gates` below defaults to True but this is a modest tilt,
# not a strong signal on its own.
#
# Float (`/stocks/vX/float`) was evaluated in Phase 1 and dropped before
# testing: it has no historical query (current-only) and only 77.6% ticker
# coverage even for "now" -- unusable as a point-in-time feature for this
# cohort. `float_gates` exists below for symmetry but has no data behind it
# and must stay False.
# ---------------------------------------------------------------------------

def lookup_short_interest(ticker: str, api_key: str = None):
    """
    Looks up the most recent FINRA short-interest reading for `ticker`.
    Returns a dict {"short_interest": int, "avg_daily_volume": int,
    "days_to_cover": float, "settlement_date": str} or None if unavailable
    (missing API key, request failure, or no data for this ticker).
    """
    api_key = api_key or _resolve_massive_api_key()
    if not api_key:
        print(f"  [short-interest lookup skipped for {ticker}: MASSIVE_API_KEY not set]")
        return None

    try:
        import requests
    except ImportError:
        print(f"  [short-interest lookup skipped for {ticker}: requests is not installed]")
        return None

    try:
        resp = requests.get(
            "https://api.massive.com/stocks/v1/short-interest",
            params={"ticker": ticker, "limit": 1, "sort": "settlement_date", "order": "desc",
                    "apiKey": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except Exception as e:
        print(f"  [short-interest lookup failed for {ticker}: {e}]")
        return None

    if not results:
        return None

    r = results[0]
    return {
        "short_interest": r.get("short_interest"),
        "avg_daily_volume": r.get("avg_daily_volume"),
        "days_to_cover": r.get("days_to_cover"),
        "settlement_date": r.get("settlement_date"),
    }


# ---------------------------------------------------------------------------
# Guardrail #1 stock scanner (from "How to Day Trade" by Ross Cameron)
#
# His stated criteria for a stock worth trading, checked against its MOST
# RECENT trading day:
#   1. Up >10% vs. the previous day's close
#   2. Relative volume >= 2.0x its recent average daily volume
#   3. Share price between $2 and $10 (extended tolerance up to $20)
#   4. News/catalyst today -- pass `has_catalyst` from
#      lookup_recent_catalyst() (or your own external source). Reported
#      either way; only affects passes_all if catalyst_gates=True (see
#      the note above the news-lookup section on why that defaults False).
#   5. Float <= 20 million shares (preferably) -- also not derivable from
#      OHLCV; pass `float_shares` if you have it (e.g., from a fundamentals
#      API), otherwise this check is skipped
# ---------------------------------------------------------------------------

def compute_relative_volume(daily_df: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """Today's volume / the trailing `lookback`-day average volume (excluding today)."""
    avg_volume = daily_df["Volume"].shift(1).rolling(lookback).mean()
    return daily_df["Volume"] / avg_volume


def scan_guardrail_criteria(daily_df: pd.DataFrame,
                             min_gain_pct: float = 10.0,
                             min_relative_volume: float = 2.0,
                             price_range: tuple = (2.0, 20.0),
                             preferred_price_range: tuple = (2.0, 10.0),
                             min_float: float = 1_000_000,
                             max_float: float = 20_000_000,
                             float_shares: float = None,
                             float_gates: bool = False,
                             has_catalyst: bool = None,
                             catalyst_gates: bool = False,
                             days_to_cover: float = None,
                             min_days_to_cover: float = 3.0,
                             short_interest_gates: bool = True,
                             volume_lookback: int = 20) -> dict:
    """
    Checks the LATEST day in daily_df against Guardrail #1. Returns a dict
    with each criterion's pass/fail plus an overall 'passes_core' (the 3
    price-history-derived checks) and 'passes_all' (includes each optional
    check only if its own _gates flag is True). Every optional value
    (float_shares, has_catalyst, days_to_cover) is reported in the output
    regardless of its gate -- gating and reporting are separate.

    - float_gates defaults to False: no backtest has been run (float has no
      point-in-time historical data source -- see
      C:/Users/beale/short-interest-study/SHORT_INTEREST_STUDY_FINDINGS.md
      Phase 1 -- so it was never tested, not tested-and-rejected). min_float
      (default 1M, D-TRADE-031) bounds the float range alongside max_float --
      it excludes the thinnest "nano float" names, where a single small print
      can swing price and inflate relative-volume readings (an extreme case: a
      1.5M-float stock trading a small multiple of its ENTIRE float reads as a
      huge relative-volume number but carries real execution risk on the way
      out). Grounded in a real reference implementation (day_trade_toolkit.py,
      Director-supplied 2026-08-04) that already uses this exact pattern and
      default. Like max_float, min_float is CONVENTIONAL day-trading guidance,
      not a backtested number -- and this repo's own completed float study
      already found float itself unusable as a point-in-time feature for this
      cohort on BOTH providers checked: Massive's /stocks/vX/float is
      current-only with only 77.6% ticker coverage even for "now"
      (SHORT_INTEREST_STUDY_FINDINGS.md Phase 1 discovery); SEC-API.io's
      outstandingShares/publicFloat are 36.5%/83.2% unusable respectively once
      point-in-time-joined (FLOAT_STUDY_PHASE1_FINDINGS.md SS4, NO-GO on both).
      Adding min_float is low-risk precisely because it's dead code until a
      real float_shares value + float_gates=True exist together -- it does not
      reopen or contradict the float study's verdict.
    - catalyst_gates defaults to False: tested and found non-predictive
      (C:/Users/beale/catalyst-study/CATALYST_STUDY_FINDINGS.md).
    - short_interest_gates defaults to True: tested and found predictive,
      robustly, for days_to_cover >= min_days_to_cover (roughly this
      cohort's observed top quartile) --
      C:/Users/beale/short-interest-study/SHORT_INTEREST_STUDY_FINDINGS.md.
      The effect is small; this is a modest tilt, not a strong signal.
    """
    if len(daily_df) < volume_lookback + 2:
        return {"error": "not enough history to compute relative volume"}

    close = daily_df["Close"]
    gain_pct = (close.iloc[-1] / close.iloc[-2] - 1) * 100
    rel_vol = compute_relative_volume(daily_df, volume_lookback).iloc[-1]
    price = close.iloc[-1]

    gain_ok = gain_pct >= min_gain_pct
    rel_vol_ok = rel_vol >= min_relative_volume
    price_ok = price_range[0] <= price <= price_range[1]
    price_preferred = preferred_price_range[0] <= price <= preferred_price_range[1]

    # Each optional check only counted toward passes_all if its own gate is
    # True -- the raw value is still reported below either way. Unlike the
    # reference implementation's require_float_data (which drops a candidate
    # outright when float_shares is missing), this scanner never gates on
    # missing data -- float_ok stays None/unmeasured, consistent with
    # float_gates defaulting False across this whole file.
    float_ok = (min_float <= float_shares <= max_float) if (float_gates and float_shares is not None) else None
    catalyst_ok = has_catalyst if catalyst_gates else None
    short_interest_ok = (days_to_cover >= min_days_to_cover) if (short_interest_gates and days_to_cover is not None) else None

    core_checks = [gain_ok, rel_vol_ok, price_ok]
    passes_core = all(core_checks)
    optional_checks = [c for c in (float_ok, catalyst_ok, short_interest_ok) if c is not None]
    passes_all = passes_core and all(optional_checks)

    return {
        "gain_pct": round(float(gain_pct), 2), "gain_ok": bool(gain_ok),
        "relative_volume": round(float(rel_vol), 2) if not np.isnan(rel_vol) else None,
        "relative_volume_ok": bool(rel_vol_ok) if not np.isnan(rel_vol) else False,
        "price": round(float(price), 4), "price_ok": bool(price_ok),
        "price_in_preferred_range": bool(price_preferred),
        "float_shares": float_shares, "float_ok": float_ok, "float_gates": float_gates,
        "has_catalyst": has_catalyst, "catalyst_gates": catalyst_gates,
        "days_to_cover": days_to_cover, "short_interest_ok": short_interest_ok,
        "short_interest_gates": short_interest_gates,
        "passes_core": bool(passes_core),
        "passes_all": bool(passes_all),
    }


# ---------------------------------------------------------------------------
# Sykes Sliding Scale (S3) -- from "The Complete Penny Stock Course"
#
# 100-point rubric across 7 factors (P.R.E.P.A.R.E.). Three factors are
# objectively computable from price/volume history:
#   - Risk/Reward       (0-20)
#   - Ease of Entry/Exit, via relative volume/liquidity (0-10)
#   - Past Performance / history of spiking (0-10)
# One is partially computable:
#   - Pattern/Price, via whether a bullish pattern recently fired (0-20)
# Three are inherently subjective/require external info and are NO-OP
# placeholders unless you supply them:
#   - Personal schedule (0-20) -- your own availability, not derivable
#   - Reason/Catalyst (0-10) -- pass has_catalyst if known from news
#   - Environment of the market (0-10) -- sector/market sentiment, pass
#     market_environment_score if you've assessed it yourself
#
# The total is normalized to a percentage of whatever points ARE available,
# so a partial evaluation still maps onto the book's 100-point grading table
# rather than being unfairly deflated by missing subjective inputs.
# ---------------------------------------------------------------------------

def _score_risk_reward(risk_reward_ratio: float, max_points: float = 20.0) -> float:
    if risk_reward_ratio is None or np.isnan(risk_reward_ratio) or risk_reward_ratio <= 0:
        return 0.0
    # 3:1 or better = full points, scales down linearly below that, 0 at 0:1
    return float(np.clip(risk_reward_ratio / 3.0, 0, 1) * max_points)


def _score_ease_of_entry(relative_volume: float, days_to_cover: float = None,
                          short_interest_gates: bool = False, max_points: float = 10.0) -> float:
    if relative_volume is None or np.isnan(relative_volume):
        volume_score = 0.0
    else:
        # 5.0x relative volume or better = full points
        volume_score = float(np.clip(relative_volume / 5.0, 0, 1) * max_points)

    if not (short_interest_gates and days_to_cover is not None):
        return volume_score

    # Squeeze-potential bonus -- short-interest-study/
    # SHORT_INTEREST_STUDY_FINDINGS.md found higher days_to_cover predicted
    # BETTER forward returns for this cohort, robustly across CV. Blended in
    # at 30% weight as a modest tilt, not a replacement for the
    # volume-based liquidity score the effect size doesn't justify more.
    squeeze_score = float(np.clip(np.log1p(days_to_cover) / np.log1p(10.0), 0, 1) * max_points)
    return float(np.clip(0.7 * volume_score + 0.3 * squeeze_score, 0, max_points))


def _score_past_performance(daily_df: pd.DataFrame, spike_threshold_pct: float = 15.0,
                             lookback_days: int = 252, max_points: float = 10.0) -> float:
    close = daily_df["Close"]
    pct_change = close.pct_change() * 100
    window = pct_change.iloc[-lookback_days:] if len(pct_change) > lookback_days else pct_change
    num_spikes = (window >= spike_threshold_pct).sum()
    # 3 or more prior spikes in the lookback = full points
    return float(np.clip(num_spikes / 3.0, 0, 1) * max_points)


def _score_pattern_price(patterns_fired_recently: bool, gain_pct: float, max_points: float = 20.0) -> float:
    if gain_pct is None or np.isnan(gain_pct):
        return 0.0
    # A confirmed bullish pattern trigger recently = most of the points;
    # an active, sizeable gain in progress (even without a named pattern
    # trigger) still earns partial credit.
    base = 14.0 if patterns_fired_recently else 0.0
    gain_credit = float(np.clip(gain_pct / 20.0, 0, 1)) * (max_points - 14.0)
    return min(max_points, base + gain_credit)


def compute_s3_score(daily_df: pd.DataFrame,
                      risk_reward_ratio: float = None,
                      recent_pattern_fired: bool = False,
                      personal_schedule_score: float = None,
                      has_catalyst: bool = None,
                      catalyst_gates: bool = False,
                      days_to_cover: float = None,
                      short_interest_gates: bool = True,
                      market_environment_score: float = None,
                      volume_lookback: int = 20,
                      spike_threshold_pct: float = 15.0,
                      spike_lookback_days: int = 252) -> dict:
    """
    Computes the Sykes Sliding Scale for the latest day in daily_df.
    Pass risk_reward_ratio (e.g. from a planned trade's target/stop) and
    recent_pattern_fired (e.g. any(scan_all_patterns(intraday).iloc[-1]))
    for a fuller score; the three subjective factors are optional and
    excluded from the total (not penalized) if left as None.

    has_catalyst is always reported in the output, but only contributes to
    the score if catalyst_gates=True -- defaults to False (catalyst-study
    backtest found no out-of-sample predictive power for this cohort).
    days_to_cover is blended into ease_of_entry if short_interest_gates=True
    (default) -- short-interest-study backtest found a real, if modest,
    out-of-sample edge. See CATALYST_STUDY_FINDINGS.md /
    SHORT_INTEREST_STUDY_FINDINGS.md for both backtests.
    """
    close = daily_df["Close"]
    gain_pct = (close.iloc[-1] / close.iloc[-2] - 1) * 100 if len(close) >= 2 else np.nan
    rel_vol = compute_relative_volume(daily_df, volume_lookback).iloc[-1]

    scores = {
        "pattern_price": (_score_pattern_price(recent_pattern_fired, gain_pct), 20.0),
        "risk_reward": (_score_risk_reward(risk_reward_ratio), 20.0),
        "ease_of_entry": (_score_ease_of_entry(rel_vol, days_to_cover, short_interest_gates), 10.0),
        "past_performance": (_score_past_performance(daily_df, spike_threshold_pct, spike_lookback_days), 10.0),
    }
    # Optional/subjective factors -- only counted if supplied
    if personal_schedule_score is not None:
        scores["personal_schedule"] = (float(personal_schedule_score), 20.0)
    if catalyst_gates and has_catalyst is not None:
        scores["reason_catalyst"] = (8.0 if has_catalyst else 1.0, 10.0)
    if market_environment_score is not None:
        scores["environment"] = (float(market_environment_score), 10.0)

    total_earned = sum(v for v, _ in scores.values())
    total_possible = sum(m for _, m in scores.values())
    pct = (total_earned / total_possible * 100) if total_possible > 0 else 0.0

    if pct >= 95:
        rating = "Excellent"
    elif pct >= 90:
        rating = "Very good"
    elif pct >= 80:
        rating = "Good"
    elif pct >= 75:
        rating = "Playable"
    elif pct >= 65:
        rating = "Watch"
    else:
        rating = "Poor"

    return {
        "component_scores": {k: round(v, 1) for k, (v, _) in scores.items()},
        "component_max": {k: m for k, (_, m) in scores.items()},
        "total_earned": round(total_earned, 1),
        "total_possible": total_possible,
        "score_pct": round(pct, 1),
        "rating": rating,
        "is_partial": total_possible < 100,
        "has_catalyst": has_catalyst, "catalyst_gates": catalyst_gates,
        "days_to_cover": days_to_cover, "short_interest_gates": short_interest_gates,
    }


# ---------------------------------------------------------------------------
# 7-Step Pennystocking Framework -- pump & dump lifecycle phase classifier
#
# Phases: pre_pump -> ramp -> supernova -> cliff_dive -> dip_buying ->
#         dead_pump_bounce -> long_kiss_goodnight
#
# The book is explicit that "these steps are not sequential and some may be
# omitted or repeated" -- this is a heuristic regime classifier, not a
# precise detector. Tune the thresholds to the stock/timeframe you're
# looking at.
# ---------------------------------------------------------------------------

def classify_pnd_phase(daily_df: pd.DataFrame,
                        supernova_gain_pct: float = 50.0,
                        supernova_rel_vol: float = 3.0,
                        ramp_rel_vol: float = 1.5,
                        cliff_drop_pct: float = 30.0,
                        dip_buy_min_gain_pct: float = 5.0,
                        long_kiss_min_days: int = 10,
                        peak_window: int = 10,
                        volume_lookback: int = 20) -> pd.Series:
    """
    A persistent state machine: the phase only CHANGES on specific trigger
    days (e.g. the single day of the sharp reversal, or the day a bounce
    starts); otherwise it carries the current phase forward, so a multi-day
    decline doesn't get relabeled "cliff_dive" on every single red day.
    """
    n = len(daily_df)
    gain_pct = daily_df["Close"].pct_change().values * 100
    rel_vol = compute_relative_volume(daily_df, volume_lookback).values
    rolling_peak = daily_df["Close"].rolling(peak_window, min_periods=1).max().values
    drawdown_from_peak_pct = (daily_df["Close"].values - rolling_peak) / rolling_peak * 100

    labels = [None] * n
    state = None
    days_since_cliff = None

    for i in range(n):
        if np.isnan(gain_pct[i]) or np.isnan(rel_vol[i]):
            labels[i] = "insufficient_data"
            continue

        # A fresh supernova always takes priority -- a new promotion can
        # start even after a prior cycle finished.
        if gain_pct[i] >= supernova_gain_pct and rel_vol[i] >= supernova_rel_vol:
            state = "supernova"
            days_since_cliff = None

        elif state == "supernova" and drawdown_from_peak_pct[i] <= -cliff_drop_pct and gain_pct[i] < 0:
            state = "cliff_dive"
            days_since_cliff = 0

        elif state in ("cliff_dive", "dip_buying", "dead_pump_bounce", "long_kiss_goodnight"):
            days_since_cliff = (days_since_cliff or 0) + 1

            if gain_pct[i] >= dip_buy_min_gain_pct:
                # A bounce day: first one after the cliff is "dip buying",
                # any later one is a "dead pump bounce"
                state = "dip_buying" if state == "cliff_dive" else "dead_pump_bounce"
            elif days_since_cliff >= long_kiss_min_days:
                state = "long_kiss_goodnight"
            # else: keep carrying forward the current state (still bleeding
            # out from the last cliff/bounce, not yet at the long-kiss mark)

        elif rel_vol[i] >= ramp_rel_vol and drawdown_from_peak_pct[i] >= -10 and state in (None, "pre_pump", "ramp"):
            state = "ramp"

        elif state is None:
            state = "pre_pump"

        # otherwise: no trigger fired today, keep the current state as-is

        labels[i] = state

    return pd.Series(labels, index=daily_df.index, name="pnd_phase")


# ---------------------------------------------------------------------------
# Risk-management day-trade simulator (Guardrails #5, #8, #9, #14)
#
#   #5: minimum 2:1 profit/loss ratio per trade
#   #8/#9: hard max loss per trade AND per day -- stop taking new trades
#          once either is breached
#   #14: daily goal of 10-15 cents/share; also, per Chapter 10, stop
#        trading for the day if giving back too much (default 15%) of the
#        day's peak profit
#
# This actually simulates entries/exits and tracks running $ P&L, unlike
# the pure pattern detectors above which just flag bars.
# ---------------------------------------------------------------------------

def simulate_day_trades(intraday_df: pd.DataFrame, entry_trigger: pd.Series,
                         stop_loss_pct: float = 2.0, min_risk_reward: float = 2.0,
                         shares_per_trade: int = 100,
                         max_loss_per_trade_dollars: float = None,
                         max_daily_loss_dollars: float = None,
                         profit_giveback_pct: float = 15.0,
                         trail_pct: float = None,
                         init_stop_pct: float = None) -> dict:
    """
    Walks through intraday_df bar by bar. On each bar where entry_trigger is
    True and no position is open and trading hasn't been halted for the day,
    opens a long at that bar's Close.

    Two mutually exclusive exit modes, selected by whether trail_pct is set
    (both None -- the default -- is the original fixed mode; behavior is
    byte-for-byte unchanged from before this parameter pair existed):

    FIXED mode (trail_pct is None, the default):
      - stop = entry * (1 - stop_loss_pct/100)
      - target = entry + (entry - stop) * min_risk_reward   (enforces the
        2:1 -- or whatever ratio you set -- by construction)
      Each subsequent bar checks whether High reached the target or Low hit
      the stop (stop wins on a same-bar tie, the conservative assumption).

    TRAILING mode (trail_pct is not None; init_stop_pct is then required --
    ADR-0001 SS6.3, D-TRADE-036 ratified primary cell trail_pct=8/
    init_stop_pct=3, sensitivity grid trail_pct in {5,8,12}/init_stop_pct in
    {2,3}): the fixed target is UNUSED -- letting winners run is the whole
    point of a trailing vs. fixed-R:R exit. Tracks peak(t) = the highest
    High seen from entry through bar t (inclusive; same-bar data at entry,
    not a lookahead -- NN-1), and computes a single monotonically
    non-decreasing effective stop:

        effective_stop(t) = max(P0*(1 - init_stop_pct/100),
                                 peak(t)*(1 - trail_pct/100))

    Because peak(t) never decreases, effective_stop(t) is non-decreasing by
    construction -- the stop can never silently retreat -- and it can never
    fall below the initial floor, so the loss is bounded at init_stop_pct
    regardless of what the trail does. Exits the first bar whose Low <=
    effective_stop (reason "trailing_stop"), same conservative fill-at-stop
    assumption as fixed mode.

    Either mode: any position still open at the last bar of the day is
    force-closed at that bar's Close (reason "eod_close").

    Trading halts for the rest of the day (no new entries, existing
    position still managed normally) if:
      - a single trade's loss would exceed max_loss_per_trade_dollars, or
      - cumulative daily P&L drops to/below -max_daily_loss_dollars, or
      - daily P&L has pulled back by >= profit_giveback_pct from its
        peak-so-far (only once that peak is positive)
    These are per-DAY circuit breakers and are orthogonal to -- compose
    with, do not replace -- either per-trade exit mode above; do not
    conflate a per-trade stop with the daily peak-giveback halt.

    max_loss_per_trade_dollars / max_daily_loss_dollars: pass None to
    disable that particular circuit breaker.
    """
    if trail_pct is not None and init_stop_pct is None:
        raise ValueError("init_stop_pct is required when trail_pct is set (ADR-0001 SS6.3)")

    closes = intraday_df["Close"].values
    highs = intraday_df["High"].values
    lows = intraday_df["Low"].values
    trigger = entry_trigger.reindex(intraday_df.index).fillna(False).values
    n = len(intraday_df)
    trailing_mode = trail_pct is not None

    trades = []
    position = None  # dict: entry_price, stop_price, target_price, entry_time, peak (trailing mode only)
    daily_pnl = 0.0
    peak_pnl = 0.0
    halted = False
    halt_reason = None
    pnl_curve = []

    for i in range(n):
        price, high, low = closes[i], highs[i], lows[i]

        if position is not None:
            if trailing_mode:
                # peak(t) uses only bars entry..t inclusive -- bar-causal, NN-1.
                position["peak"] = max(position["peak"], high)
                position["stop_price"] = max(position["stop_price"],
                                              position["peak"] * (1 - trail_pct / 100))

            exit_price, reason = None, None
            if low <= position["stop_price"]:
                exit_price = position["stop_price"]
                reason = "trailing_stop" if trailing_mode else "stop"
            elif position["target_price"] is not None and high >= position["target_price"]:
                exit_price, reason = position["target_price"], "target"
            elif i == n - 1:
                exit_price, reason = price, "eod_close"

            if exit_price is not None:
                pnl = (exit_price - position["entry_price"]) * shares_per_trade
                daily_pnl += pnl
                peak_pnl = max(peak_pnl, daily_pnl)
                trades.append({
                    "entry_time": position["entry_time"], "exit_time": intraday_df.index[i],
                    "entry_price": position["entry_price"], "exit_price": exit_price,
                    "pnl": pnl, "reason": reason,
                })
                position = None

                if max_loss_per_trade_dollars is not None and pnl <= -abs(max_loss_per_trade_dollars):
                    halted, halt_reason = True, f"single-trade loss ${-pnl:.2f} exceeded max_loss_per_trade"
                if max_daily_loss_dollars is not None and daily_pnl <= -abs(max_daily_loss_dollars):
                    halted, halt_reason = True, f"daily loss ${-daily_pnl:.2f} hit max_daily_loss"
                if peak_pnl > 0 and daily_pnl <= peak_pnl * (1 - profit_giveback_pct / 100):
                    halted, halt_reason = True, (f"gave back {profit_giveback_pct}% of peak profit "
                                                  f"(peak ${peak_pnl:.2f}, now ${daily_pnl:.2f})")

        elif not halted and trigger[i]:
            entry_price = price
            if trailing_mode:
                position = {
                    "entry_price": entry_price,
                    "stop_price": entry_price * (1 - init_stop_pct / 100),
                    "target_price": None,
                    "peak": high,  # this bar's own High -- same-bar data, not a lookahead
                    "entry_time": intraday_df.index[i],
                }
            else:
                stop_price = entry_price * (1 - stop_loss_pct / 100)
                risk = entry_price - stop_price
                target_price = entry_price + risk * min_risk_reward
                position = {"entry_price": entry_price, "stop_price": stop_price,
                            "target_price": target_price, "entry_time": intraday_df.index[i]}

        pnl_curve.append(daily_pnl + (0 if position is None else (price - position["entry_price"]) * shares_per_trade))

    wins = [t for t in trades if t["pnl"] > 0]
    return {
        "trades": trades,
        "num_trades": len(trades),
        "win_rate_pct": (len(wins) / len(trades) * 100) if trades else 0.0,
        "final_pnl": daily_pnl,
        "pnl_per_share": daily_pnl / shares_per_trade if shares_per_trade else 0.0,
        "pnl_curve": pnl_curve,
        "halted": halted,
        "halt_reason": halt_reason,
    }


# ---------------------------------------------------------------------------
# 2) Intraday pattern check -- pivot points + red-to-green alignment
# ---------------------------------------------------------------------------

def compute_pivot_points(prior_high: float, prior_low: float, prior_close: float) -> dict:
    """Standard floor-trader pivot points from the prior full trading day's H/L/C."""
    pp = (prior_high + prior_low + prior_close) / 3
    r1 = 2 * pp - prior_low
    s1 = 2 * pp - prior_high
    r2 = pp + (prior_high - prior_low)
    s2 = pp - (prior_high - prior_low)
    return {"pivot": pp, "r1": r1, "s1": s1, "r2": r2, "s2": s2}


def analyze_intraday_alignment(intraday_df: pd.DataFrame, prior_high: float, prior_low: float,
                                prior_close: float) -> dict:
    """
    Checks each intraday bar for the "weak open red-to-green + pivot" setup:
    bullish alignment = price above the pivot point AND above the prior
    day's close (red-to-green). Returns the pivot levels, an annotated
    DataFrame, whether the LATEST bar is aligned, and the first bar (if any)
    where alignment was newly triggered (crossed into alignment from not
    being aligned the bar before).
    """
    levels = compute_pivot_points(prior_high, prior_low, prior_close)
    out = intraday_df.copy()

    out["above_pivot"] = out["Close"] > levels["pivot"]
    out["above_prior_close"] = out["Close"] > prior_close
    out["aligned"] = out["above_pivot"] & out["above_prior_close"]
    out["aligned_trigger"] = out["aligned"] & ~out["aligned"].shift(1, fill_value=False)

    trigger_bars = out.index[out["aligned_trigger"]]
    first_trigger = trigger_bars[0] if len(trigger_bars) > 0 else None
    latest_aligned = bool(out["aligned"].iloc[-1]) if len(out) > 0 else False

    return {
        "levels": levels,
        "annotated": out,
        "latest_aligned": latest_aligned,
        "first_trigger_time": first_trigger,
        "num_trigger_bars": int(out["aligned_trigger"].sum()),
    }


# ---------------------------------------------------------------------------
# 3) Additional Warrior Trading / small-account candlestick patterns
#
# Each detector returns a boolean pd.Series aligned to the input df's index,
# True on the bar where that pattern's entry trigger fires. These are
# pattern-recognition heuristics from qualitative chart descriptions (no
# exact numeric rules were given in the source material), so thresholds are
# reasonable defaults exposed as parameters -- tune them to taste.
# ---------------------------------------------------------------------------

def detect_bull_flag_breakout(df: pd.DataFrame, pole_min_pct: float = 5.0,
                               max_flag_bars: int = 4, flag_range_ratio: float = 0.6) -> pd.Series:
    """
    Bull flag: a strong green "pole" candle, followed by 1-max_flag_bars
    small-range consolidation candles (the "flag", range <= flag_range_ratio
    x the pole's range), then a breakout candle that closes above the flag's
    high. Trigger fires on that breakout candle.
    """
    o, h, l, c = df["Open"], df["High"], df["Low"], df["Close"]
    body_pct = (c - o) / o * 100
    candle_range = h - l
    n = len(df)
    trigger = np.zeros(n, dtype=bool)

    for pole_i in range(n - 2):
        if body_pct.iloc[pole_i] < pole_min_pct:
            continue
        pole_range = candle_range.iloc[pole_i]
        if pole_range <= 0:
            continue

        # Extend the flag as long as consolidation candles stay tight
        flag_end = pole_i
        for j in range(pole_i + 1, min(pole_i + 1 + max_flag_bars, n)):
            if candle_range.iloc[j] <= flag_range_ratio * pole_range:
                flag_end = j
            else:
                break
        if flag_end == pole_i:
            continue  # no valid flag candles

        flag_high = h.iloc[pole_i + 1:flag_end + 1].max()
        breakout_i = flag_end + 1
        if breakout_i < n and c.iloc[breakout_i] > flag_high:
            trigger[breakout_i] = True

    return pd.Series(trigger, index=df.index, name="bull_flag_breakout")


def detect_flat_top_breakout(df: pd.DataFrame, lookback: int = 5, flat_tolerance_pct: float = 1.5) -> pd.Series:
    """
    Flat top: the highs of the trailing `lookback` candles cluster tightly
    (within flat_tolerance_pct of each other), forming a flat resistance
    line. Trigger fires on the first candle that closes above that level.
    """
    high, close = df["High"], df["Close"]
    n = len(df)
    trigger = np.zeros(n, dtype=bool)

    for i in range(lookback, n):
        window = high.iloc[i - lookback:i]
        flat_level = window.max()
        spread_pct = (window.max() - window.min()) / window.mean() * 100
        if spread_pct <= flat_tolerance_pct and close.iloc[i] > flat_level:
            trigger[i] = True

    return pd.Series(trigger, index=df.index, name="flat_top_breakout")


def find_swing_points(series: pd.Series, order: int = 3):
    """Local minima/maxima: a bar is a swing point if it's the extreme within +/- order bars."""
    vals = series.values
    n = len(vals)
    is_low = np.zeros(n, dtype=bool)
    is_high = np.zeros(n, dtype=bool)
    for i in range(order, n - order):
        window = vals[i - order:i + order + 1]
        if vals[i] == window.min() and np.argmin(window) == order:
            is_low[i] = True
        if vals[i] == window.max() and np.argmax(window) == order:
            is_high[i] = True
    return is_low, is_high


def detect_abcd_pattern(df: pd.DataFrame, order: int = 3) -> pd.Series:
    """
    ABCD: A (swing low) -> B (swing high) -> C (higher low than A, i.e. a
    pullback that holds above A) -> D (breakout above B). Trigger fires on
    the bar where price closes back above B after forming a valid C.
    """
    close = df["Close"]
    is_low, is_high = find_swing_points(close, order)
    n = len(df)
    trigger = np.zeros(n, dtype=bool)

    swings = [(i, "L" if is_low[i] else "H") for i in range(n) if is_low[i] or is_high[i]]

    for idx in range(len(swings) - 1):
        a_i, a_type = swings[idx]
        if a_type != "L":
            continue
        if idx + 1 >= len(swings) or swings[idx + 1][1] != "H":
            continue
        b_i = swings[idx + 1][0]
        if idx + 2 >= len(swings) or swings[idx + 2][1] != "L":
            continue
        c_i = swings[idx + 2][0]

        a_price, b_price, c_price = close.iloc[a_i], close.iloc[b_i], close.iloc[c_i]
        if not (c_price > a_price and c_price < b_price):
            continue  # C must be a HIGHER low than A, and below B

        # Look for the first close after C that breaks above B (= point D)
        for d_i in range(c_i + 1, n):
            if close.iloc[d_i] > b_price:
                trigger[d_i] = True
                break

    return pd.Series(trigger, index=df.index, name="abcd_pattern")


def detect_micro_pullback(df: pd.DataFrame, min_trend_pct: float = 1.0) -> pd.Series:
    """
    Micro pullback: a green trend candle, then ONE smaller-range candle (the
    pullback -- may be red or green), then a green candle whose close breaks
    above the pullback candle's high. Trigger fires on that 3rd candle.
    """
    o, h, l, c = df["Open"], df["High"], df["Low"], df["Close"]
    body_pct = (c - o) / o * 100
    candle_range = h - l
    n = len(df)
    trigger = np.zeros(n, dtype=bool)

    for i in range(2, n):
        trend_ok = body_pct.iloc[i - 2] >= min_trend_pct
        pullback_ok = candle_range.iloc[i - 1] < candle_range.iloc[i - 2]
        breakout_ok = c.iloc[i] > o.iloc[i] and c.iloc[i] > h.iloc[i - 1]
        if trend_ok and pullback_ok and breakout_ok:
            trigger[i] = True

    return pd.Series(trigger, index=df.index, name="micro_pullback")


def detect_round_number_breakout(df: pd.DataFrame, increment: float = 0.5, lookback: int = 10) -> pd.Series:
    """
    Whole/half dollar entries: price has been consolidating below a round
    (.00 or .50) level, then closes above it. Trigger fires on the first
    candle that closes above a round level which the trailing `lookback`
    candles' closes were all below.
    """
    close = df["Close"]
    n = len(df)
    trigger = np.zeros(n, dtype=bool)

    for i in range(lookback, n):
        prior_max = close.iloc[i - lookback:i].max()
        # Nearest round level at/above the prior window's max
        level = np.ceil(prior_max / increment) * increment
        if level <= prior_max:
            level += increment
        if close.iloc[i] > level and (close.iloc[i - lookback:i] < level).all():
            trigger[i] = True

    return pd.Series(trigger, index=df.index, name="round_number_breakout")


def _session_masks(df: pd.DataFrame, market_open_time: str = "09:30"):
    """Splits an intraday index into (premarket_mask, regular_session_mask) per calendar day."""
    open_t = pd.to_datetime(market_open_time).time()
    times = df.index.time
    regular = times >= open_t
    return ~regular, regular


def detect_opening_range_breakout(df: pd.DataFrame, market_open_time: str = "09:30",
                                   range_minutes: int = 1) -> pd.Series:
    """
    1-min opening range breakout: the range of the first `range_minutes` of
    regular trading defines the opening range. Trigger fires on the first
    bar afterward (same day) that closes above the opening range's high.
    """
    n = len(df)
    trigger = np.zeros(n, dtype=bool)
    _, regular_mask = _session_masks(df, market_open_time)

    dates = pd.Series(df.index.date, index=df.index)
    for day, day_idx in dates.groupby(dates).groups.items():
        day_positions = [df.index.get_loc(ts) for ts in day_idx if regular_mask[df.index.get_loc(ts)]]
        if not day_positions:
            continue
        open_time = df.index[day_positions[0]]
        range_end_time = open_time + pd.Timedelta(minutes=range_minutes)
        range_positions = [p for p in day_positions if df.index[p] < range_end_time]
        if not range_positions:
            continue
        opening_high = df["High"].iloc[range_positions].max()

        fired = False
        for p in day_positions:
            if df.index[p] < range_end_time:
                continue
            if not fired and df["Close"].iloc[p] > opening_high:
                trigger[p] = True
                fired = True

    return pd.Series(trigger, index=df.index, name="opening_range_breakout")


def compute_premarket_levels(df: pd.DataFrame, market_open_time: str = "09:30") -> pd.DataFrame:
    """Per calendar day: premarket_high, premarket_low, premarket_pivot (their midpoint)."""
    premarket_mask, _ = _session_masks(df, market_open_time)
    dates = pd.Series(df.index.date, index=df.index)

    rows = []
    for day, day_idx in dates.groupby(dates).groups.items():
        pm_idx = [ts for ts in day_idx if premarket_mask[df.index.get_loc(ts)]]
        if not pm_idx:
            continue
        pm_high = df.loc[pm_idx, "High"].max()
        pm_low = df.loc[pm_idx, "Low"].min()
        rows.append({"date": day, "premarket_high": pm_high, "premarket_low": pm_low,
                      "premarket_pivot": (pm_high + pm_low) / 2})
    return pd.DataFrame(rows)


def _detect_premarket_level_break(df: pd.DataFrame, level_col: str, market_open_time: str = "09:30") -> pd.Series:
    n = len(df)
    trigger = np.zeros(n, dtype=bool)
    pm_levels = compute_premarket_levels(df, market_open_time)
    if pm_levels.empty:
        return pd.Series(trigger, index=df.index)

    _, regular_mask = _session_masks(df, market_open_time)
    dates = pd.Series(df.index.date, index=df.index)
    level_by_date = pm_levels.set_index("date")[level_col].to_dict()

    for day, day_idx in dates.groupby(dates).groups.items():
        if day not in level_by_date:
            continue
        level = level_by_date[day]
        day_positions = [df.index.get_loc(ts) for ts in day_idx if regular_mask[df.index.get_loc(ts)]]
        fired = False
        for p in day_positions:
            if not fired and df["Close"].iloc[p] > level:
                trigger[p] = True
                fired = True

    return pd.Series(trigger, index=df.index)


def detect_premarket_pivot_break(df: pd.DataFrame, market_open_time: str = "09:30") -> pd.Series:
    """Break of pre-market pivot: first regular-session close above the premarket high/low midpoint."""
    s = _detect_premarket_level_break(df, "premarket_pivot", market_open_time)
    s.name = "premarket_pivot_break"
    return s


def detect_premarket_high_break(df: pd.DataFrame, market_open_time: str = "09:30") -> pd.Series:
    """Break of pre-market highs: first regular-session close above the premarket high."""
    s = _detect_premarket_level_break(df, "premarket_high", market_open_time)
    s.name = "premarket_high_break"
    return s


def scan_all_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """Runs every pattern detector and returns one boolean DataFrame, one column per pattern."""
    return pd.DataFrame({
        "bull_flag_breakout": detect_bull_flag_breakout(df),
        "flat_top_breakout": detect_flat_top_breakout(df),
        "abcd_pattern": detect_abcd_pattern(df),
        "micro_pullback": detect_micro_pullback(df),
        "round_number_breakout": detect_round_number_breakout(df),
        "opening_range_breakout": detect_opening_range_breakout(df),
        "premarket_pivot_break": detect_premarket_pivot_break(df),
        "premarket_high_break": detect_premarket_high_break(df),
    }, index=df.index)


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_intraday_alignment(annotated: pd.DataFrame, levels: dict, ticker: str, prior_close: float, outpath: str):
    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(annotated.index, annotated["Close"], color="black", linewidth=1, label="Price")
    ax.axhline(levels["pivot"], color="blue", linestyle="--", linewidth=1, label="Pivot")
    ax.axhline(levels["r1"], color="green", linestyle=":", linewidth=0.8, label="R1")
    ax.axhline(levels["s1"], color="red", linestyle=":", linewidth=0.8, label="S1")
    ax.axhline(prior_close, color="orange", linestyle="-", linewidth=1, label="Prior close")

    triggers = annotated[annotated["aligned_trigger"]]
    ax.scatter(triggers.index, triggers["Close"], marker="^", color="green", s=120,
               zorder=5, label="Alignment trigger")

    ax.set_title(f"{ticker} - Intraday Pivot / Red-to-Green Alignment")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    print(f"Chart saved to {outpath}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Rolling watchlist + pivot/red-to-green pattern detector.")
    parser.add_argument("--tickers", type=str, required=True,
                         help="Comma-separated candidate tickers to check, e.g. OBAI,AAPL,GME "
                              "(you supply these -- there's no live gainers scanner wired in)")
    parser.add_argument("--period", type=str, default="3mo", help="Daily history period to fetch")
    parser.add_argument("--lookback-days", type=int, default=5,
                         help="How many trailing trading days to look back for a qualifying spike")
    parser.add_argument("--gain-threshold", type=float, default=20.0,
                         help="Minimum single-day %% gain to count as a 'big gainer' spike (rollover check)")
    parser.add_argument("--pullback-threshold", type=float, default=50.0,
                         help="Max %% of the spike's gain that can be given back and still count as 'holding up'")
    parser.add_argument("--intraday-period", type=str, default="5d",
                         help="Intraday history period (yfinance caps 5m data at ~60d)")
    parser.add_argument("--intraday-interval", type=str, default="5m", help="Intraday bar size")
    parser.add_argument("--pattern-lookback-bars", type=int, default=6,
                         help="Trailing bars checked for the S3 score's 'recent pattern fired' input "
                              "(default 6 bars = 30min on 5m data) -- pattern triggers fire on a single "
                              "bar, so requiring literally the latest bar would read False almost all "
                              "day; this window keeps it meaningful regardless of when the scan runs")
    parser.add_argument("--out", type=str, default="watchlist_chart.png",
                         help="Chart filename for the best aligned candidate, if any")

    # Guardrail #1 scanner (informational, doesn't filter out candidates -- float/catalyst
    # usually aren't available, so treat this as a report, not a hard gate)
    parser.add_argument("--guardrail-min-gain-pct", type=float, default=10.0)
    parser.add_argument("--guardrail-min-rel-volume", type=float, default=2.0)
    parser.add_argument("--guardrail-price-min", type=float, default=2.0)
    parser.add_argument("--guardrail-price-max", type=float, default=20.0)
    parser.add_argument("--guardrail-max-float", type=float, default=20_000_000)

    # Risk-management day-trade simulator (opt-in -- actually simulates trades/P&L)
    parser.add_argument("--simulate-trades", action="store_true",
                         help="Simulate entries/exits off the pivot-alignment trigger with Ross Cameron's "
                              "risk guardrails: 2:1 min R:R, per-trade/daily loss limits, profit give-back stop")
    parser.add_argument("--stop-loss-pct", type=float, default=2.0, help="Stop-loss distance from entry, in %%")
    parser.add_argument("--min-risk-reward", type=float, default=2.0, help="Minimum profit/loss ratio (Guardrail #5)")
    parser.add_argument("--shares-per-trade", type=int, default=100)
    parser.add_argument("--max-loss-per-trade", type=float, default=None, help="$ -- Guardrail #8")
    parser.add_argument("--max-daily-loss", type=float, default=None, help="$ -- Guardrails #8/#9")
    parser.add_argument("--profit-giveback-pct", type=float, default=15.0,
                         help="Halt for the day if P&L pulls back this %% from its peak (Chapter 10)")
    args = parser.parse_args()

    tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]

    print(f"Fetching daily data for {len(tickers)} ticker(s)...")
    daily_data = {t: load_daily(t, period=args.period) for t in tickers}

    watchlist = scan_rollover_watchlist(daily_data, lookback_days=args.lookback_days,
                                         gain_threshold_pct=args.gain_threshold,
                                         pullback_threshold_pct=args.pullback_threshold)

    print("\n=== Rollover Watchlist (recent big gainers, holding-up status) ===")
    if watchlist.empty:
        print(f"No ticker had a >= {args.gain_threshold}% single-day gain in the last "
              f"{args.lookback_days} trading days.")
        return
    print(watchlist.to_string(index=False))

    holding_tickers = watchlist.loc[watchlist["holding_up"], "ticker"].tolist()
    if not holding_tickers:
        print("\nNone of the recent gainers are still holding up -- no intraday check to run.")
        return

    # Single merged loop: intraday data is fetched ONCE per ticker and reused
    # for both the S3 score's pattern/risk-reward inputs and the pivot/
    # red-to-green check (these used to be two separate loops, with the S3
    # call in the first one hardcoding recent_pattern_fired=True and
    # risk_reward_ratio=args.min_risk_reward -- constants, not per-ticker
    # measurements, before the real intraday-derived values existed yet).
    print(f"\n=== Guardrail #1 Scanner + Sykes Sliding Scale + P&D Phase + Intraday Pivot/Red-to-Green ===")
    best_candidate = None
    for t in holding_tickers:
        df = daily_data[t]
        has_catalyst = lookup_recent_catalyst(t)
        si = lookup_short_interest(t)
        days_to_cover = si["days_to_cover"] if si else None
        gr = scan_guardrail_criteria(df, min_gain_pct=args.guardrail_min_gain_pct,
                                      min_relative_volume=args.guardrail_min_rel_volume,
                                      price_range=(args.guardrail_price_min, args.guardrail_price_max),
                                      max_float=args.guardrail_max_float,
                                      has_catalyst=has_catalyst, catalyst_gates=False,
                                      days_to_cover=days_to_cover, short_interest_gates=True)
        if "error" in gr:
            print(f"  {t}: {gr['error']}")
            continue
        catalyst_note = "unknown" if gr["has_catalyst"] is None else ("yes" if gr["has_catalyst"] else "no")
        dtc_note = "unknown" if gr["days_to_cover"] is None else f"{gr['days_to_cover']:.1f}x ({'OK' if gr['short_interest_ok'] else 'no'})"
        print(f"  {t}: gain={gr['gain_pct']}% ({'OK' if gr['gain_ok'] else 'no'}), "
              f"rel_vol={gr['relative_volume']}x ({'OK' if gr['relative_volume_ok'] else 'no'}), "
              f"price=${gr['price']} ({'OK' if gr['price_ok'] else 'no'}), "
              f"catalyst={catalyst_note} (reported only -- not gating passes_all, see "
              f"catalyst-study/CATALYST_STUDY_FINDINGS.md), "
              f"days_to_cover={dtc_note} (gates passes_all -- see "
              f"short-interest-study/SHORT_INTEREST_STUDY_FINDINGS.md), "
              f"core_pass={gr['passes_core']}")

        # --- Fetch intraday once, derive the two real S3 inputs from it ---
        if len(df) >= 2:
            prior_high, prior_low, prior_close = df["High"].iloc[-2], df["Low"].iloc[-2], df["Close"].iloc[-2]
            intraday = load_intraday(t, period=args.intraday_period, interval=args.intraday_interval)
        else:
            intraday = pd.DataFrame()

        result = None
        patterns = None
        recent_pattern_fired = False
        risk_reward_ratio = None

        if not intraday.empty:
            result = analyze_intraday_alignment(intraday, prior_high, prior_low, prior_close)
            levels = result["levels"]

            patterns = scan_all_patterns(intraday)
            # "Recently fired" = within the trailing --pattern-lookback-bars
            # bars, not literally just the single latest bar. Pattern
            # triggers are momentary (True on exactly one bar), so requiring
            # the very last bar would read False almost all day except in
            # the instant right after a trigger -- a short trailing window
            # keeps this a meaningful S3 input regardless of when in the
            # session the scan happens to run.
            window = patterns.iloc[-args.pattern_lookback_bars:]
            recent_pattern_fired = bool(window.to_numpy().any())

            # Implied risk/reward from the same floor-trader pivot levels
            # used for the alignment check: reward = distance from the
            # current intraday price up to the nearest pivot level ABOVE it
            # (next resistance -- a long's target); risk = distance down to
            # the nearest pivot level BELOW it (next support -- where a long
            # would stop out). All five levels (pivot, r1, r2, s1, s2) are
            # searched on both sides rather than assuming r1/r2 sit above
            # and s1/s2 below -- current price can be anywhere relative to
            # the pivot itself depending on the day. None (not a fallback
            # constant) if there's no level left on either side to measure
            # against, or if the resulting risk is zero/negative.
            current_price = intraday["Close"].iloc[-1]
            all_levels = [levels["pivot"], levels["r1"], levels["r2"], levels["s1"], levels["s2"]]
            resistances_above = [lv for lv in all_levels if lv > current_price]
            supports_below = [lv for lv in all_levels if lv < current_price]
            if resistances_above and supports_below:
                reward = min(resistances_above) - current_price
                risk = current_price - max(supports_below)
                if risk > 0:
                    risk_reward_ratio = reward / risk

        s3 = compute_s3_score(df, risk_reward_ratio=risk_reward_ratio, recent_pattern_fired=recent_pattern_fired,
                               has_catalyst=has_catalyst, catalyst_gates=False,
                               days_to_cover=days_to_cover, short_interest_gates=True)
        note = " (partial score -- personal schedule and environment not supplied; catalyst reported but non-gating)" if s3["is_partial"] else ""
        print(f"      S3 score: {s3['score_pct']}% ({s3['total_earned']}/{s3['total_possible']}) "
              f"-> {s3['rating']}{note}")

        phase = classify_pnd_phase(df)
        print(f"      P&D phase: {phase.iloc[-1]}")

        if intraday.empty:
            print(f"  {t}: no intraday data available")
            continue

        status = "ALIGNED NOW" if result["latest_aligned"] else "not currently aligned"
        trigger_msg = f", first triggered at {result['first_trigger_time']}" if result["first_trigger_time"] else ""
        print(f"  {t}: pivot={levels['pivot']:.4f}  prior_close={prior_close:.4f}  "
              f"latest_close={intraday['Close'].iloc[-1]:.4f}  -> {status}{trigger_msg}")

        recent_fires = []
        for col in patterns.columns:
            fired_times = patterns.index[patterns[col]]
            if len(fired_times) > 0:
                recent_fires.append(f"{col}@{fired_times[-1].strftime('%m-%d %H:%M')}")
        if recent_fires:
            print(f"      patterns fired: {', '.join(recent_fires)}")

        if args.simulate_trades:
            sim = simulate_day_trades(intraday, result["annotated"]["aligned_trigger"],
                                       stop_loss_pct=args.stop_loss_pct, min_risk_reward=args.min_risk_reward,
                                       shares_per_trade=args.shares_per_trade,
                                       max_loss_per_trade_dollars=args.max_loss_per_trade,
                                       max_daily_loss_dollars=args.max_daily_loss,
                                       profit_giveback_pct=args.profit_giveback_pct)
            print(f"      simulated: {sim['num_trades']} trades, win rate {sim['win_rate_pct']:.0f}%, "
                  f"P&L ${sim['final_pnl']:.2f} (${sim['pnl_per_share']:.3f}/share)"
                  + (f"  [HALTED: {sim['halt_reason']}]" if sim["halted"] else ""))

        if result["latest_aligned"] and best_candidate is None:
            best_candidate = (t, result, prior_close)

    if best_candidate:
        t, result, prior_close = best_candidate
        plot_intraday_alignment(result["annotated"], result["levels"], t, prior_close, args.out)
    else:
        print("\nNo candidate is currently aligned (above pivot AND above prior close); no chart generated.")


if __name__ == "__main__":
    main()
