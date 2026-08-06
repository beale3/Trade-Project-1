"""
Analyze where your logged trades' outcomes cluster by float range.

D-TRADE-031, adapted from a Director-supplied reference implementation
(analyze_float_distribution.py, 2026-08-04) that assumed a specific
producer pipeline (premarket_scan.py -> premarket_scan_log.csv) which
does not exist in this repo. This adaptation is deliberately decoupled
from that origin: it reads any CSV with the right columns, from any
source -- a manually-maintained trade log today, or a future scan-
history persistence layer (none exists in this repo yet; the D-TRADE-023
dashboard's /api/scan is stateless).

WHY THIS EXISTS: min_float/max_float in tools/rolling_watchlist.py's
scan_guardrail_criteria() are CONVENTIONAL day-trading guidance, not
numbers backtested against real outcomes -- and this repo's own
completed float study already found float itself unusable as a
point-in-time feature on both providers checked:
  - Massive /stocks/vX/float: current-only, only 77.6% ticker coverage
    even for "now" (C:/Users/beale/short-interest-study/
    SHORT_INTEREST_STUDY_FINDINGS.md, Phase 1 discovery).
  - SEC-API.io: outstandingShares 36.5% unusable, publicFloat 83.2%
    unusable once point-in-time-joined (C:/Users/beale/float-study/
    FLOAT_STUDY_PHASE1_FINDINGS.md SS4 -- NO-GO on both, as scoped).
This script does not reopen that verdict or invent a data source that
doesn't exist -- it answers a narrower, honest question: IF you have
real float_shares + outcome data logged (from wherever), does the
min/max float band scan_guardrail_criteria() uses line up with where
trades actually work? Absent that data, it still reports whatever float
distribution the log does contain -- useful on its own, no outcome
analysis required.

INPUT: a CSV with at minimum `ticker` and `float_shares` columns (any
producer -- there's no specific format this repo's tools currently
write). To unlock the win-rate-by-float-bucket breakdown, add two more
columns yourself after each trade closes:
    result_pct   -- realized return on that trade, e.g. 4.2 or -2.1
    taken        -- TRUE/FALSE, whether the trade was actually entered

RUN: `python tools/analyze_float_distribution.py [path_to_log.csv]`
(defaults to `float_scan_log.csv` in the current directory -- no such
file is created by anything in this repo yet; point it at your own log).
"""

import sys

import pandas as pd

DEFAULT_LOG_PATH = "float_scan_log.csv"

# Float buckets to analyze -- edit these to test different boundary theories.
# The "current scanner range" label tracks scan_guardrail_criteria()'s
# min_float=1_000_000/max_float=20_000_000 defaults (D-TRADE-031).
FLOAT_BUCKETS = [
    (0, 1_000_000, "< 1M (nano, below min_float)"),
    (1_000_000, 20_000_000, "1M - 20M (current scanner range)"),
    (20_000_000, 50_000_000, "20M - 50M (above max_float)"),
    (50_000_000, float("inf"), "> 50M"),
]


def bucket_for(float_shares: float) -> str:
    if pd.isna(float_shares):
        return "no float data"
    for low, high, label in FLOAT_BUCKETS:
        if low <= float_shares < high:
            return label
    return "unbucketed"


def load_log(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        sys.exit(
            f"ERROR: {path} not found. This repo has no built-in pipeline that produces this "
            f"file yet -- point this script at your own manually-maintained log (ticker, "
            f"float_shares, and optionally result_pct/taken columns), see the module docstring."
        )
    if "float_shares" not in df.columns:
        sys.exit(f"ERROR: {path} has no float_shares column -- see the module docstring for the "
                  f"expected shape.")
    return df


def report_distribution(df: pd.DataFrame):
    df = df.copy()
    df["float_bucket"] = df["float_shares"].apply(bucket_for)

    print(f"\n=== Float distribution of {len(df)} candidates ===")
    counts = df["float_bucket"].value_counts()
    for label in [b[2] for b in FLOAT_BUCKETS] + ["no float data"]:
        n = counts.get(label, 0)
        pct = 100.0 * n / len(df) if len(df) else 0
        print(f"  {label:35s} {n:>4d} candidates ({pct:5.1f}%)")


def report_outcomes(df: pd.DataFrame):
    if "result_pct" not in df.columns:
        print("\nNo 'result_pct' column found -- add it to your log after each trade closes to "
              "unlock the win-rate-by-float-bucket breakdown. Skipping.")
        return

    df = df.copy()
    if "taken" in df.columns:
        df = df[df["taken"].astype(str).str.upper() == "TRUE"]
    df = df.dropna(subset=["result_pct"])

    if df.empty:
        print("\nNo trades with a recorded result_pct yet -- nothing to analyze.")
        return

    df["float_bucket"] = df["float_shares"].apply(bucket_for)

    print(f"\n=== Outcomes by float bucket ({len(df)} closed trades) ===")
    print(f"{'Bucket':35s} {'N':>4s} {'Win%':>7s} {'AvgRet%':>9s} {'Best':>8s} {'Worst':>8s}")
    for label in [b[2] for b in FLOAT_BUCKETS] + ["no float data"]:
        subset = df[df["float_bucket"] == label]
        if subset.empty:
            continue
        win_rate = 100.0 * (subset["result_pct"] > 0).mean()
        avg_ret = subset["result_pct"].mean()
        best = subset["result_pct"].max()
        worst = subset["result_pct"].min()
        print(f"{label:35s} {len(subset):>4d} {win_rate:>6.1f}% {avg_ret:>8.2f}% "
              f"{best:>7.2f}% {worst:>7.2f}%")

    print("\nRead this with real caution on small samples -- a bucket with 3-4 trades isn't "
          "statistically meaningful, no matter how good or bad the numbers look. This repo's own "
          "D-TRADE-021 clearance bar treats n<30 as too thin to trust (D-TRADE-029) -- the same "
          "caution applies here: don't move min_float/max_float in scan_guardrail_criteria() off "
          "a bucket with a handful of trades in it.")


if __name__ == "__main__":
    log_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LOG_PATH
    data = load_log(log_path)
    report_distribution(data)
    report_outcomes(data)
