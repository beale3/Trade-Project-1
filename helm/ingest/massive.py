"""
Massive OHLCV point-in-time adapter (ADR-0001 sec-4, Lane A). The ONLY
place under helm/ a provider SDK/host may appear (leg T boundary) --
tools/rolling_watchlist.py's own api.massive.com calls are the pre-existing
shared-library exception the ADR grandfathers, not a second sanctioned site.

Reuses tools.rolling_watchlist._resolve_massive_api_key (key resolution,
not a provider-host call) rather than re-deriving key handling; the actual
HTTP call to api.massive.com lives here, parameterized by an explicit
[start_date, end_date] historical window -- the scanner's own _massive_aggs
only supports "N days back from today," which doesn't fit a point-in-time
historical backtest pull (D-TRADE-037/038).
"""
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.rolling_watchlist import _resolve_massive_api_key

MASSIVE_AGGS_URL = "https://api.massive.com/v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}"


def fetch_daily_ohlcv(ticker: str, start_date: date, end_date: date, api_key: str) -> pd.DataFrame:
    """
    One ticker, one call: daily OHLCV bars over [start_date, end_date]
    (inclusive), point-in-time -- every row's date is <= end_date by
    construction (NN-1). Returns an empty DataFrame on any failure or
    zero-row response rather than raising, matching the scanner's own
    graceful-skip convention (a missing ticker is a data fact, not a
    crash) -- shaped identically to tools.rolling_watchlist.load_daily's
    output (DatetimeIndex, Open/High/Low/Close/Volume).
    """
    try:
        resp = requests.get(
            MASSIVE_AGGS_URL.format(ticker=ticker, start=start_date.isoformat(), end=end_date.isoformat()),
            params={"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": api_key},
            timeout=20,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except Exception as e:
        print(f"  [Massive daily pull failed for {ticker}: {e}]")
        return pd.DataFrame()

    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    df["date"] = (pd.to_datetime(df["t"], unit="ms", utc=True)
                  .dt.tz_convert("America/New_York").dt.tz_localize(None))
    df = df.set_index("date").sort_index()
    df = df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"})
    return df[["Open", "High", "Low", "Close", "Volume"]]


def fetch_universe_daily(tickers: list[str], start_date: date, end_date: date) -> dict:
    """
    One call per ticker (D-TRADE-038's approved, bounded shape -- no
    per-ticker pagination beyond the single range call). Returns
    {"data": {ticker: DataFrame}, "calls": [{"ticker", "rows", "ok"}]} --
    the calls list is the checkable artifact for exactly how many real
    provider calls this run made (protocol 16), independent of the
    spend_ledger file helm.storage writes from it.
    """
    api_key = _resolve_massive_api_key()
    if not api_key:
        raise RuntimeError("MASSIVE_API_KEY not resolved (env var or massive_api_key.txt) -- cannot pull real data")

    data = {}
    calls = []
    for ticker in tickers:
        df = fetch_daily_ohlcv(ticker, start_date, end_date, api_key)
        calls.append({"ticker": ticker, "rows": len(df), "ok": not df.empty})
        if not df.empty:
            data[ticker] = df
    return {"data": data, "calls": calls}
