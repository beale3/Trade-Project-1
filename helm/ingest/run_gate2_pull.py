"""
D-TRADE-037/038 Gate-1/Gate-2 approved real-data pull. Executes exactly
the approved scope, no more: 100 tickers (a deterministic even-sample of
the short-interest-study's proven 754-ticker cohort), 2024-06-01 through
(execution date - 45 days). Run once per approved pull -- re-running with
a different scope requires a fresh Gate-2 approval (D-TRADE-038's standing
condition), not a code change here.
"""
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from helm.ingest.massive import fetch_universe_daily
from helm.storage.raw_store import append_spend_ledger, write_daily_ohlcv

SHORT_INTEREST_COHORT = Path(r"C:\Users\beale\short-interest-study\raw_short_interest_all.csv")
N_TICKERS = 100
START_DATE = date(2024, 6, 1)
END_BUFFER_DAYS = 45


def approved_ticker_list() -> list[str]:
    """100-ticker deterministic even-sample of the 754-ticker proven cohort (D-TRADE-037 proposal)."""
    tickers = sorted(pd.read_csv(SHORT_INTEREST_COHORT)["ticker"].unique())
    step = len(tickers) / N_TICKERS
    return [tickers[int(i * step)] for i in range(N_TICKERS)]


def main():
    end_date = date.today() - timedelta(days=END_BUFFER_DAYS)
    tickers = approved_ticker_list()
    assert len(tickers) == N_TICKERS, f"expected {N_TICKERS} tickers, got {len(tickers)}"

    print(f"Pulling {len(tickers)} tickers, {START_DATE} -> {end_date} ({END_BUFFER_DAYS}d buffer from today)")
    result = fetch_universe_daily(tickers, START_DATE, end_date)

    ohlcv_path = write_daily_ohlcv(result["data"])
    ledger_path = append_spend_ledger(result["calls"], provider="massive", endpoint="v2/aggs/ticker/range/1/day")

    ok_count = sum(1 for c in result["calls"] if c["ok"])
    total_rows = sum(c["rows"] for c in result["calls"])
    print(f"Calls made: {len(result['calls'])} (approved: {N_TICKERS})")
    print(f"Tickers with data: {ok_count}/{len(tickers)}, total rows: {total_rows}")
    print(f"Wrote: {ohlcv_path} , {ledger_path}")

    failed = [c["ticker"] for c in result["calls"] if not c["ok"]]
    if failed:
        print(f"No-data tickers ({len(failed)}): {failed}")


if __name__ == "__main__":
    main()
