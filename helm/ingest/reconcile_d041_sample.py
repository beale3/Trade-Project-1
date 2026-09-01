"""
One-time reconciliation after AIQ's D-TRADE-040/041 audit
(docs/eval/d-trade-040-041-audit.md, 2026-08-31): SPLIT_TRANSITION_DATES
was extended from 3 to 30 tickers, dropping 3 of the original 150-event
sample (HTOO 2025-07-22, UPXI 2024-10-17, XHG 2024-12-09 -- confirmed the
ONLY 3 of the 150 affected, not just trusting the audit's "at least 3").

Completes the existing D-TRADE-041 ~150-event authorization rather than
re-sampling/re-pulling all 150 from scratch (per the Lead's explicit
instruction) -- keeps the 147 still-clean events' already-paid intraday
data untouched, replaces only the 3 contaminated ones with 3 newly
deterministic-sampled clean events (first 3 not already in the kept set,
ticker-then-date sorted -- same no-cherry-pick convention as
sample_events.py).
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from helm.ingest.massive import fetch_sampled_intraday
from helm.storage.raw_store import append_spend_ledger

DATA_DIR = Path(__file__).resolve().parents[2] / "helm" / "storage" / "data"
CONTAMINATED = {
    ("HTOO", pd.Timestamp("2025-07-22")),
    ("UPXI", pd.Timestamp("2024-10-17")),
    ("XHG", pd.Timestamp("2024-12-09")),
}


def main():
    old_sample = pd.read_csv(DATA_DIR / "intraday_sample.csv", parse_dates=["date"])
    clean_events = (pd.read_csv(DATA_DIR / "event_days.csv", parse_dates=["date"])
                     .sort_values(["ticker", "date"]).reset_index(drop=True))

    is_contaminated = old_sample.apply(lambda r: (r["ticker"], r["date"]) in CONTAMINATED, axis=1)
    contaminated_rows = old_sample[is_contaminated]
    assert len(contaminated_rows) == len(CONTAMINATED), (
        f"expected exactly {len(CONTAMINATED)} contaminated rows in the old sample, found {len(contaminated_rows)}")
    kept = old_sample[~is_contaminated]
    kept_keys = set(zip(kept["ticker"], kept["date"]))

    candidates = clean_events[~clean_events.apply(lambda r: (r["ticker"], r["date"]) in kept_keys, axis=1)]
    replacements = candidates.head(len(CONTAMINATED)).reset_index(drop=True)
    print(f"Kept {len(kept)} still-clean events, replacing {len(contaminated_rows)}:")
    print(contaminated_rows[["ticker", "date"]].to_string(index=False))
    print(f"With {len(replacements)} newly-sampled clean events:")
    print(replacements[["ticker", "date"]].to_string(index=False))

    new_sample = pd.concat([kept, replacements], ignore_index=True)
    assert len(new_sample) == len(old_sample), "reconciled sample size drifted from the original 150"
    new_sample.to_csv(DATA_DIR / "intraday_sample.csv", index=False)

    # Pull intraday ONLY for the 3 replacements -- not re-pulling the 147 already-paid, still-valid events.
    result = fetch_sampled_intraday(replacements)
    ledger_path = append_spend_ledger(
        result["calls"], provider="massive",
        endpoint="v2/aggs/ticker/range/5/minute (D-TRADE-041 reconciliation, AIQ audit)")
    ok = sum(1 for c in result["calls"] if c["ok"])
    print(f"Replacement pull: {ok}/{len(replacements)} succeeded, "
          f"{sum(c['rows'] for c in result['calls'])} bars. Ledger: {ledger_path}")

    # Rewrite intraday_5m.csv: drop the 3 contaminated events' bars, append the 3 replacements'.
    intraday_path = DATA_DIR / "intraday_5m.csv"
    existing = pd.read_csv(intraday_path, parse_dates=["event_date", "bar_ts"])
    still_valid = existing[~existing.apply(lambda r: (r["ticker"], r["event_date"]) in CONTAMINATED, axis=1)]

    new_frames = []
    for (ticker, event_date), df in result["data"].items():
        f = df.reset_index().rename(columns={
            "date": "bar_ts", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
        # event_date here is fetch_sampled_intraday's dict-key string (event_date.isoformat()) --
        # must become a real Timestamp before concat, or it silently coexists as a second dtype
        # in the same column and round-trips through to_csv() in an inconsistent string format
        # (caught by post-hoc verification, not assumed correct from a clean-looking print output).
        f.insert(0, "event_date", pd.Timestamp(event_date))
        f.insert(1, "ticker", ticker)
        new_frames.append(f)

    combined = pd.concat([still_valid] + new_frames, ignore_index=True) if new_frames else still_valid
    combined.to_csv(intraday_path, index=False)
    print(f"Rewrote {intraday_path}: {len(existing)} -> {len(combined)} rows "
          f"(dropped {len(existing) - len(still_valid)}, added {len(combined) - len(still_valid)})")


if __name__ == "__main__":
    main()
