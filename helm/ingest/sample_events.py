"""
D-TRADE-041: deterministic ~150-event sample of the 559 real,
split-artifact-filtered event-days (identify_events.py) -- the Director-
ruled scope for the first intraday pull, not the full 651/559 (D-TRADE-038's
standing condition on Massive rate-limit/helm-spend still applies).

Even-stride sample across the ticker-then-date-sorted event list (same
convention as the original 100-ticker cohort sample) -- proportional
representation across tickers, not concentrated in a few active names,
and fully deterministic/reproducible (no randomness, nothing to seed).
"""
from pathlib import Path

import pandas as pd

TARGET_N = 150
EVENTS_PATH = Path(__file__).resolve().parents[2] / "helm" / "storage" / "data" / "event_days.csv"
OUT_PATH = Path(__file__).resolve().parents[2] / "helm" / "storage" / "data" / "intraday_sample.csv"


def sample_events() -> pd.DataFrame:
    events = pd.read_csv(EVENTS_PATH, parse_dates=["date"]).sort_values(["ticker", "date"]).reset_index(drop=True)
    n = len(events)
    step = n / TARGET_N
    idx = [int(i * step) for i in range(TARGET_N)]
    return events.iloc[idx].drop_duplicates().reset_index(drop=True)


def main():
    sample = sample_events()
    sample.to_csv(OUT_PATH, index=False)
    print(f"Sampled {len(sample)} of {len(pd.read_csv(EVENTS_PATH))} events, "
          f"{sample['ticker'].nunique()} unique tickers")
    print(f"Wrote: {OUT_PATH}")


if __name__ == "__main__":
    main()
