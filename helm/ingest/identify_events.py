"""
Identifies guardrail-qualifying event-days from the real daily-OHLCV pull
(D-TRADE-038) -- the cohort definition Leg A/B's intraday pull needs to be
sized against (AI/ML coordination, working-log.md 2026-08-31: "event-days
only," matching the short-interest study's own cohort construction).

Reuses tools.rolling_watchlist.compute_relative_volume directly (imported,
not re-derived) and scan_guardrail_criteria's own passes_core formula
(gain_pct = pct-change, rel_vol = compute_relative_volume, price in
[2, 20]) -- replicated inline rather than called per-row-per-ticker in a
Python loop (that function checks only ITS LAST row by design; calling it
~45k times would be slow for arithmetic this simple to reproduce exactly).
Same default thresholds as scan_guardrail_criteria's signature: 10% gain,
2x relative volume, $2-$20 price -- not new numbers.

D-TRADE-040/041 addition: raw (unadjusted) prices have a real, discovered
side effect -- a stock split makes the raw close/volume series jump
discontinuously at the split-effective date, which pct_change()/
compute_relative_volume() read as a spurious enormous "gain" + "volume
spike". SPLIT_TRANSITION_DATES below is a ONE-TIME, exact list found by
diffing this raw pull against the now-superseded adjusted dataset
(ohlcv_daily_adjusted_D-TRADE-038_SUPERSEDED.csv) -- this comparison-based
method only works because that reference file still exists; it is NOT a
general split detector and won't generalize to a future raw-only pull
with no adjusted reference to diff against (flagged as a forward-looking
gap, not solved here -- out of this task's scope).

AIQ's independent D-TRADE-040/041 audit (docs/eval/d-trade-040-041-audit.md,
2026-08-31) found the first version of this list covered only 3 of 30
tickers with a genuine in-window transition (>15% relative step in the
raw/adjusted close ratio between consecutive trading days, confirmed clean
and permanent -- not reverting) -- independently re-reproduced by SDE1
against all 100 tickers before extending this list, exact match to AIQ's
27 additions (34 total transitions across 30 tickers). NOT every ticker
with raw-vs-adjusted divergence belongs here -- some (e.g. RCON) have a
constant ratio throughout the whole pulled window, meaning the split
predates the pull's start; those introduce no IN-WINDOW pct_change()/
rel-vol artifact and correctly need no entry (AIQ's audit sec-2).

Excludes any event within 20 TRADING days after a transition (matching
VOLUME_LOOKBACK -- the rolling relative-volume window stays contaminated
by the pre/post-split volume-scale mismatch for that long), using each
ticker's own trading-day index, not calendar days.

ASST 2025-05-07 (gain_pct=455.74%, relative_volume=1312.00) is correctly
NOT excluded -- it is nowhere near either of ASST's two real transitions.
It is a REAL market event, not a split artifact (AIQ + Lead independently
verified: close 0.61->3.39, volume 197K->315.8M shares, price then decays
gradually over several days while volume stays elevated -- a sustained
pattern, not a single corrupted tick or a split-basis jump). An earlier
version of this docstring mischaracterized it as an artifact; corrected.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.rolling_watchlist import compute_relative_volume

MIN_GAIN_PCT = 10.0
MIN_RELATIVE_VOLUME = 2.0
PRICE_RANGE = (2.0, 20.0)
VOLUME_LOOKBACK = 20

SPLIT_TRANSITION_DATES = {
    "ANY": [pd.Timestamp("2026-02-10")],
    "AREBW": [pd.Timestamp("2026-04-27")],
    "ASST": [pd.Timestamp("2024-07-02"), pd.Timestamp("2026-02-06")],
    "BKYI": [pd.Timestamp("2026-04-30")],
    "BTM": [pd.Timestamp("2026-02-23")],
    "ENSC": [pd.Timestamp("2024-12-06")],
    "GWH": [pd.Timestamp("2024-08-26")],
    "HTOO": [pd.Timestamp("2025-07-14")],
    "HYZN": [pd.Timestamp("2024-09-11")],
    "ILLR": [pd.Timestamp("2026-06-23")],
    "KZIA": [pd.Timestamp("2024-10-28"), pd.Timestamp("2025-04-17")],
    "LESL": [pd.Timestamp("2025-09-29")],
    "LUCY": [pd.Timestamp("2024-07-18")],
    "LYEL": [pd.Timestamp("2025-06-02")],
    "MSS": [pd.Timestamp("2026-04-24")],
    "NKLA": [pd.Timestamp("2024-06-25")],
    "NUKK": [pd.Timestamp("2024-10-24")],
    "PHGE": [pd.Timestamp("2024-08-26"), pd.Timestamp("2025-11-25")],
    "POLA": [pd.Timestamp("2024-11-19")],
    "PSIG": [pd.Timestamp("2025-10-13")],
    "SGN": [pd.Timestamp("2024-11-18")],
    "SNSE": [pd.Timestamp("2025-06-17")],
    "SRFM": [pd.Timestamp("2024-08-19")],
    "TCRT": [pd.Timestamp("2024-07-18")],
    "TRVN": [pd.Timestamp("2024-08-13")],
    "UPXI": [pd.Timestamp("2024-10-03")],
    "VATE": [pd.Timestamp("2024-08-09")],
    "WORX": [pd.Timestamp("2026-04-10")],
    "XHG": [pd.Timestamp("2024-11-08"), pd.Timestamp("2025-05-09")],
    "ZEPP": [pd.Timestamp("2024-09-16")],
}

OHLCV_PATH = Path(__file__).resolve().parents[2] / "helm" / "storage" / "data" / "ohlcv_daily.csv"
OUT_PATH = Path(__file__).resolve().parents[2] / "helm" / "storage" / "data" / "event_days.csv"


def split_contaminated_mask(dates: pd.Series, ticker: str) -> pd.Series:
    """
    True for any date within [transition, transition + VOLUME_LOOKBACK
    trading days] for this ticker's known split transitions -- counted on
    THIS ticker's own trading-day index (dates are already trading-day-only,
    so this is exact, not a calendar-day approximation).
    """
    mask = pd.Series(False, index=dates.index)
    for transition in SPLIT_TRANSITION_DATES.get(ticker, []):
        after = dates >= transition
        # position of the transition day itself within this ticker's index
        if not after.any():
            continue
        start_pos = dates[after].index.min()
        end_pos = start_pos + VOLUME_LOOKBACK
        mask |= dates.index.to_series().between(start_pos, end_pos) & after
    return mask


def identify_events_for_ticker(df: pd.DataFrame) -> pd.DataFrame:
    """
    df: one ticker's OHLCV, date-indexed, sorted ascending. Returns the
    subset of rows that pass scan_guardrail_criteria's passes_core check
    (gain_ok & rel_vol_ok & price_ok) -- the same 3 checks, same formulas,
    same defaults; the two _gates-optional checks (short_interest/catalyst)
    are correctly excluded, matching passes_core not passes_all -- AND that
    are not split-transition artifacts (see module docstring).
    """
    gain_pct = df["close"].pct_change() * 100
    rel_vol = compute_relative_volume(df.rename(columns={"volume": "Volume"}), VOLUME_LOOKBACK)
    price = df["close"]
    ticker = df["ticker"].iloc[0]

    gain_ok = gain_pct >= MIN_GAIN_PCT
    rel_vol_ok = rel_vol >= MIN_RELATIVE_VOLUME
    price_ok = price.between(*PRICE_RANGE)
    not_split_artifact = ~split_contaminated_mask(df["date"], ticker)
    passes_core = gain_ok & rel_vol_ok & price_ok & not_split_artifact

    out = df.loc[passes_core, ["date", "ticker"]].copy()
    out["gain_pct"] = gain_pct[passes_core].round(2)
    out["relative_volume"] = rel_vol[passes_core].round(2)
    out["close"] = price[passes_core]
    return out


def main():
    all_data = pd.read_csv(OHLCV_PATH, parse_dates=["date"])
    events = []
    for ticker, g in all_data.groupby("ticker", sort=False):
        g = g.sort_values("date").reset_index(drop=True)
        events.append(identify_events_for_ticker(g))

    events_df = pd.concat(events, ignore_index=True) if events else pd.DataFrame()
    events_df.to_csv(OUT_PATH, index=False)

    n_split_tickers = len(SPLIT_TRANSITION_DATES)
    print(f"Split-artifact exclusion active for {n_split_tickers} tickers: {list(SPLIT_TRANSITION_DATES)}")
    print(f"Total event-days: {len(events_df)}")
    print(f"Tickers with >=1 event: {events_df['ticker'].nunique()}/{all_data['ticker'].nunique()}")
    per_ticker = events_df.groupby("ticker").size()
    print(f"Events per ticker (of tickers with any): min={per_ticker.min() if len(per_ticker) else 0}, "
          f"max={per_ticker.max() if len(per_ticker) else 0}, mean={per_ticker.mean():.2f}" if len(per_ticker) else "no events")
    print(f"Wrote: {OUT_PATH}")


if __name__ == "__main__":
    main()
