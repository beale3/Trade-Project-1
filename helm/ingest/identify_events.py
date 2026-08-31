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

OHLCV_PATH = Path(__file__).resolve().parents[2] / "helm" / "storage" / "data" / "ohlcv_daily.csv"
OUT_PATH = Path(__file__).resolve().parents[2] / "helm" / "storage" / "data" / "event_days.csv"


def identify_events_for_ticker(df: pd.DataFrame) -> pd.DataFrame:
    """
    df: one ticker's OHLCV, date-indexed, sorted ascending. Returns the
    subset of rows that pass scan_guardrail_criteria's passes_core check
    (gain_ok & rel_vol_ok & price_ok) -- the same 3 checks, same formulas,
    same defaults; the two _gates-optional checks (short_interest/catalyst)
    are correctly excluded, matching passes_core not passes_all.
    """
    gain_pct = df["close"].pct_change() * 100
    rel_vol = compute_relative_volume(df.rename(columns={"volume": "Volume"}), VOLUME_LOOKBACK)
    price = df["close"]

    gain_ok = gain_pct >= MIN_GAIN_PCT
    rel_vol_ok = rel_vol >= MIN_RELATIVE_VOLUME
    price_ok = price.between(*PRICE_RANGE)
    passes_core = gain_ok & rel_vol_ok & price_ok

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

    print(f"Total event-days: {len(events_df)}")
    print(f"Tickers with >=1 event: {events_df['ticker'].nunique()}/{all_data['ticker'].nunique()}")
    per_ticker = events_df.groupby("ticker").size()
    print(f"Events per ticker (of tickers with any): min={per_ticker.min() if len(per_ticker) else 0}, "
          f"max={per_ticker.max() if len(per_ticker) else 0}, mean={per_ticker.mean():.2f}" if len(per_ticker) else "no events")
    print(f"Wrote: {OUT_PATH}")


if __name__ == "__main__":
    main()
