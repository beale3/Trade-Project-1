"""
D-TRADE-041 approved intraday pull: 5-minute bars, raw prices, for the
~150-event deterministic sample (sample_events.py) of the real, split-
artifact-filtered event-days (identify_events.py). One call per (ticker,
event_date) pair -- the Director-ruled bounded scope, not the full 559.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from helm.ingest.massive import fetch_sampled_intraday
from helm.ingest.sample_events import sample_events
from helm.storage.raw_store import append_spend_ledger, write_intraday_ohlcv


def main():
    sample = sample_events()
    print(f"Pulling intraday (5m) bars for {len(sample)} sampled events, {sample['ticker'].nunique()} tickers")

    result = fetch_sampled_intraday(sample)

    intraday_path = write_intraday_ohlcv(result["data"])
    ledger_path = append_spend_ledger(result["calls"], provider="massive", endpoint="v2/aggs/ticker/range/5/minute")

    ok_count = sum(1 for c in result["calls"] if c["ok"])
    total_rows = sum(c["rows"] for c in result["calls"])
    print(f"Calls made: {len(result['calls'])} (approved: ~150)")
    print(f"Event-days with data: {ok_count}/{len(sample)}, total bars: {total_rows}")
    print(f"Wrote: {intraday_path} , {ledger_path}")

    failed = [c["ticker"] for c in result["calls"] if not c["ok"]]
    if failed:
        print(f"No-data event-days ({len(failed)}): {failed}")


if __name__ == "__main__":
    main()
