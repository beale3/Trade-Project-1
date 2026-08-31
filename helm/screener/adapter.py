"""
Thin feature-extraction adapter over tools/rolling_watchlist.py (ADR-0001
§4, Lane B). Imports the scanner as a library, never forks its logic --
every value here is a direct read of the scanner's own detector output,
no recomputation.

Scope, per OP-4 (final component list, ratified with D-TRADE-034/036):
Leg A tests the 8 scan_all_patterns() detectors + the pivot/red-to-green
alignment trigger -- the scanner's components the 4 completed equity
studies never covered. Deliberately does NOT extract guardrail/S3/
short-interest/catalyst factors -- those are the already-validated
components OP-4 explicitly says are "not re-litigated," out of scope here.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.rolling_watchlist import scan_all_patterns, analyze_intraday_alignment

# OP-4's final Leg-A entry-signal list. Order is documentation only; every
# consumer should treat this as the source of truth for "which components,"
# not re-enumerate it independently.
LEG_A_COMPONENTS = (
    "bull_flag_breakout",
    "flat_top_breakout",
    "abcd_pattern",
    "micro_pullback",
    "round_number_breakout",
    "opening_range_breakout",
    "premarket_pivot_break",
    "premarket_high_break",
    "aligned_trigger",
)


def extract_intraday_features(intraday_df, prior_high, prior_low, prior_close):
    """
    Returns a per-bar DataFrame, one boolean column per LEG_A_COMPONENTS
    entry, indexed the same as intraday_df -- the scanner's own detector
    output, assembled into one frame, nothing computed here.
    """
    patterns = scan_all_patterns(intraday_df)
    alignment = analyze_intraday_alignment(intraday_df, prior_high, prior_low, prior_close)
    aligned_trigger = alignment["annotated"]["aligned_trigger"].reindex(patterns.index).fillna(False)

    features = patterns.copy()
    features["aligned_trigger"] = aligned_trigger
    return features[list(LEG_A_COMPONENTS)]


def daily_fired_flags(intraday_df, prior_high, prior_low, prior_close):
    """
    Reduces one trading day's per-bar features to "did component X fire on
    ANY bar this day" -- the Leg-A backtest label unit (a signal DAY, not a
    signal bar), matching OP-2's daily forward-return horizons (1d/1w/1m).

    Deliberately NOT the live dashboard's trailing-lookback-window
    convention (main()'s PATTERN_LOOKBACK_BARS / D-TRADE-023's
    recent_pattern_fired, "as of right now, this session") -- that exists
    for a live scan's current-moment read. A backtest asks a different
    question ("did this fire at all that day, so a next-day/week/month
    return can be attributed to it"), so it uses the whole day's bars, not
    a recency window. Returns {component_name: bool}.
    """
    features = extract_intraday_features(intraday_df, prior_high, prior_low, prior_close)
    return {col: bool(features[col].to_numpy().any()) for col in LEG_A_COMPONENTS}
