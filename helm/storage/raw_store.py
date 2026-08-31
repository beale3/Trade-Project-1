"""
File-first result persistence (ADR-0001 sec-4/6.1, Lane A). Raw ingested
market data + the spend_ledger, matching the 4 completed studies' own
CSV-first pattern (short-interest-study/raw_short_interest_all.csv) --
Supabase stays read-side only this phase (ADR-0001 sec-7).
"""
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"


def write_daily_ohlcv(data: dict, out_path: Path = None) -> Path:
    """
    data: {ticker: DataFrame(Open,High,Low,Close,Volume, DatetimeIndex)}.
    Writes one long-format CSV (date,ticker,open,high,low,close,volume) --
    a single checkable file, not one-file-per-ticker, so a reviewer can
    diff/grep the whole pull at once.
    """
    out_path = out_path or (DATA_DIR / "ohlcv_daily.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    frames = []
    for ticker, df in data.items():
        f = df.reset_index().rename(columns={
            "date": "date", "Open": "open", "High": "high",
            "Low": "low", "Close": "close", "Volume": "volume",
        })
        f.insert(1, "ticker", ticker)
        frames.append(f)

    combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(
        columns=["date", "ticker", "open", "high", "low", "close", "volume"])
    combined.to_csv(out_path, index=False)
    return out_path


def append_spend_ledger(calls: list, provider: str, endpoint: str, out_path: Path = None) -> Path:
    """
    One row per provider call, even the failed/empty ones (D-TRADE-019) --
    est_cost is $0.00 for every row (Massive personal tier, cost-model.md
    sec-1: flat sub, $0 marginal within quota). Append-only: read any
    existing file first so repeated runs accumulate rather than clobber.
    """
    out_path = out_path or (DATA_DIR / "spend_ledger.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).isoformat()
    rows = [{
        "ts": ts, "provider": provider, "endpoint": f"{endpoint}/{c['ticker']}",
        "rows_returned": c["rows"], "ok": c["ok"], "est_cost": 0.00,
    } for c in calls]
    new_df = pd.DataFrame(rows)

    if out_path.exists():
        existing = pd.read_csv(out_path)
        new_df = pd.concat([existing, new_df], ignore_index=True)

    # cumulative_day = running call count WITHIN each UTC calendar day (the
    # spend guard's future daily-cap check reads this column, not the row
    # index) -- not yet enforced anywhere (helm/spend doesn't exist, per
    # D-TRADE-038's standing condition); this just makes the number honest
    # now so a future guard can read it without a ledger migration.
    day_key = pd.to_datetime(new_df["ts"]).dt.date
    new_df["cumulative_day"] = new_df.groupby(day_key).cumcount() + 1
    new_df.to_csv(out_path, index=False)
    return out_path
