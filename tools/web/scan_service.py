"""
Orchestrates tools/rolling_watchlist.py's functions into per-candidate result
objects. Mirrors main()'s reference pipeline (rolling_watchlist.py:1172-1363)
exactly, call-for-call and parameter-for-parameter, but RETURNS data instead
of printing it. No business logic of its own -- every computation below is a
direct, unmodified call into rolling_watchlist.py (ADR-0002 SS2.3).

Returns raw Python objects (DataFrames, Series, Timestamps, NaN) -- shaping
those into the JSON contract is serialize.py's job, not this module's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools import rolling_watchlist as rw

# Matches main()'s --pattern-lookback-bars default (rolling_watchlist.py:1187-1191).
# Not exposed on the API contract's request body -- ADR-0002 SS3 doesn't surface it,
# so it stays pinned to main()'s own default rather than inventing new configurability.
PATTERN_LOOKBACK_BARS = 6


def run_scan(tickers, period="3mo", lookback_days=5, gain_threshold=20.0,
             pullback_threshold=50.0, guardrail=None, intraday=None, simulate=None):
    """
    Runs the rollover check for every requested ticker, then the full
    guardrail/S3/phase/intraday/simulate chain for each one that's still
    holding up -- exactly main()'s loop. A ticker with no qualifying spike in
    the lookback window produces no row at all (scan_rollover_watchlist never
    emits one), matching main()'s own behavior; a ticker that spiked but
    rolled over gets a row with every downstream field left None.

    Returns a list of raw per-candidate dicts, one per scan_rollover_watchlist
    row, in that function's own sort order (holding-up first, biggest spike
    first).
    """
    guardrail = guardrail or {}
    intraday_params = intraday or {}
    simulate_params = simulate or {}

    daily_data = {t: rw.load_daily(t, period=period) for t in tickers}
    watchlist_df = rw.scan_rollover_watchlist(
        daily_data, lookback_days=lookback_days,
        gain_threshold_pct=gain_threshold, pullback_threshold_pct=pullback_threshold,
    )

    candidates = []
    for row in watchlist_df.to_dict("records"):
        base = {
            "ticker": row["ticker"],
            "spike_date": row["spike_date"],
            "spike_gain_pct": row["spike_gain_pct"],
            "holding_up": bool(row["holding_up"]),
            "retracement_pct": row["current_retracement_pct"],
            "worst_retracement_pct": row["worst_retracement_pct"],
            "last_close": row["last_close"],
        }
        if not row["holding_up"]:
            candidates.append({**base, **_null_downstream()})
            continue

        candidates.append(_build_holding_candidate(
            row["ticker"], daily_data[row["ticker"]], base,
            guardrail, intraday_params, simulate_params,
        ))

    return candidates


def _null_downstream():
    return {
        "has_catalyst": None, "days_to_cover": None, "today_gain_pct": None, "rel_vol": None,
        "guardrail": None, "s3": None, "phase": None, "aligned": None, "patterns_fired": [],
        "intraday_df": None, "alignment": None, "prior_high": None, "prior_low": None,
        "prior_close": None, "simulated_trades": None,
    }


def _build_holding_candidate(ticker, df, base, guardrail_params, intraday_params, simulate_params):
    has_catalyst = rw.lookup_recent_catalyst(ticker)
    si = rw.lookup_short_interest(ticker)
    days_to_cover = si["days_to_cover"] if si else None

    gr = rw.scan_guardrail_criteria(
        df,
        min_gain_pct=guardrail_params.get("minGainPct", 10.0),
        min_relative_volume=guardrail_params.get("minRelVolume", 2.0),
        price_range=(guardrail_params.get("priceMin", 2.0), guardrail_params.get("priceMax", 20.0)),
        max_float=guardrail_params.get("maxFloat", 20_000_000),
        has_catalyst=has_catalyst, catalyst_gates=False,
        days_to_cover=days_to_cover, short_interest_gates=True,
    )
    if "error" in gr:
        # Not enough daily history for compute_relative_volume -- surface as a
        # holding-up candidate with everything past this point None, rather
        # than silently dropping a ticker the caller explicitly asked about.
        return {**base, "has_catalyst": has_catalyst, "days_to_cover": days_to_cover,
                "today_gain_pct": None, "rel_vol": None, "guardrail": None, "guardrail_error": gr["error"],
                "s3": None, "phase": None, "aligned": None, "patterns_fired": [],
                "intraday_df": None, "alignment": None, "prior_high": None, "prior_low": None,
                "prior_close": None, "simulated_trades": None}

    prior_high = prior_low = prior_close = None
    intraday_df = None
    if len(df) >= 2:
        prior_high, prior_low, prior_close = df["High"].iloc[-2], df["Low"].iloc[-2], df["Close"].iloc[-2]
        intraday_df = rw.load_intraday(
            ticker,
            period=intraday_params.get("period", "5d"),
            interval=intraday_params.get("interval", "5m"),
        )

    alignment = None
    patterns_fired = []
    recent_pattern_fired = False
    risk_reward_ratio = None

    if intraday_df is not None and not intraday_df.empty:
        alignment = rw.analyze_intraday_alignment(intraday_df, prior_high, prior_low, prior_close)
        patterns_df = rw.scan_all_patterns(intraday_df)
        window = patterns_df.iloc[-PATTERN_LOOKBACK_BARS:]
        recent_pattern_fired = bool(window.to_numpy().any())
        patterns_fired = [col for col in patterns_df.columns if bool(window[col].to_numpy().any())]

        # Same implied risk/reward derivation as main() (rolling_watchlist.py:1296-1316):
        # reward = distance up to the nearest pivot level above price, risk = distance
        # down to the nearest one below; None if either side has no level to measure against.
        current_price = intraday_df["Close"].iloc[-1]
        levels = alignment["levels"]
        all_levels = [levels["pivot"], levels["r1"], levels["r2"], levels["s1"], levels["s2"]]
        resistances_above = [lv for lv in all_levels if lv > current_price]
        supports_below = [lv for lv in all_levels if lv < current_price]
        if resistances_above and supports_below:
            reward = min(resistances_above) - current_price
            risk = current_price - max(supports_below)
            if risk > 0:
                risk_reward_ratio = reward / risk

    s3 = rw.compute_s3_score(
        df, risk_reward_ratio=risk_reward_ratio, recent_pattern_fired=recent_pattern_fired,
        has_catalyst=has_catalyst, catalyst_gates=False,
        days_to_cover=days_to_cover, short_interest_gates=True,
    )
    phase = rw.classify_pnd_phase(df).iloc[-1]

    simulated_trades = None
    if simulate_params.get("enabled") and alignment is not None:
        simulated_trades = rw.simulate_day_trades(
            intraday_df, alignment["annotated"]["aligned_trigger"],
            stop_loss_pct=simulate_params.get("stopLossPct", 2.0),
            min_risk_reward=simulate_params.get("minRiskReward", 2.0),
            shares_per_trade=simulate_params.get("sharesPerTrade", 100),
            max_loss_per_trade_dollars=simulate_params.get("maxLossPerTrade"),
            max_daily_loss_dollars=simulate_params.get("maxDailyLoss"),
            profit_giveback_pct=simulate_params.get("profitGivebackPct", 15.0),
        )

    return {
        **base,
        "has_catalyst": has_catalyst,
        "days_to_cover": days_to_cover,
        "today_gain_pct": gr["gain_pct"],
        "rel_vol": gr["relative_volume"],
        "guardrail": gr,
        "s3": s3,
        "phase": phase,
        "aligned": alignment["latest_aligned"] if alignment else None,
        "patterns_fired": patterns_fired,
        "intraday_df": intraday_df,
        "alignment": alignment,
        "prior_high": prior_high,
        "prior_low": prior_low,
        "prior_close": prior_close,
        "simulated_trades": simulated_trades,
    }
