"""
The real Phase-1 Leg A/Leg B CV run (D-TRADE-042 dispatch), against the
D-TRADE-040/041 dataset in helm/storage/data/ (AIQ-co-signed clean,
b0ef54e). Pure local computation over already-pulled CSVs -- zero
provider-API calls (verified: no requests/Massive imports anywhere in
this module or in helm/screener, helm/validation/engine).

Data construction choices made here (not previously pinned down -- stated
plainly, not buried, since AIQ re-derives independently right after this
report and needs to know exactly what was decided and why):

- Leg A operates on the 150-event intraday-sampled subset (intraday_sample
  .csv / intraday_5m.csv), not the full 542-event set in event_days.csv --
  the other ~392 events have no intraday data, so fired_flags cannot be
  computed for them at all. n=150 is the real, hard ceiling on Leg-A's
  support count, not a choice.
- Leg A's forward-return TARGET is a daily-close-to-daily-close % return
  from the event day's close (matching OP-2 and the 4 proven studies'
  convention) -- computed from ohlcv_daily.csv, independent of intraday.
- Leg B's two arms MUST share the same entry price for a valid paired
  comparison (ADR-0001 sec-6.2: "same entries"). The trailing-stop arm is
  necessarily same-day (simulate_day_trades force-closes at EOD -- it has
  no multi-day capability, and was not asked to grow one for this run).
  D-TRADE-036's N=5-TRADING-DAY baseline is a materially longer horizon
  than a same-day simulator can represent -- resolved by computing the
  fixed-N baseline as: enter at the SAME intraday trigger-bar price the
  trailing arm used, exit at the ticker's daily close N trading days
  later (from ohlcv_daily.csv). This is the only construction consistent
  with (a) reusing simulate_day_trades as built, not extending it, and
  (b) the two arms sharing one entry price. Flagged explicitly for AIQ's
  independent judgment on whether this is the right operationalization,
  same as the Leg-B method itself was flagged at build time.
- Leg B's entry rule is the pivot/red-to-green alignment trigger
  (aligned_trigger from analyze_intraday_alignment) -- the one entry
  signal OP-4/ADR-0001 names as feeding the trade simulator (main()'s own
  reference pipeline uses it identically). An event where the trigger
  never fires contributes no paired observation (there is no trade to
  compare arms on) -- excluded, not imputed (NN-5's own exclude-not-
  impute principle, applied here to Leg B's entry construction).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import pandas as pd

from helm.screener.adapter import LEG_A_COMPONENTS, daily_fired_flags
from helm.validation.engine import leg_a, leg_b
from tools.rolling_watchlist import analyze_intraday_alignment, simulate_day_trades

DATA_DIR = Path(__file__).resolve().parents[1] / "storage" / "data"
HORIZON_TRADING_DAYS = {"1d": 1, "1w": 5, "1m": 21}


def load_data():
    daily = pd.read_csv(DATA_DIR / "ohlcv_daily.csv", parse_dates=["date"])
    daily = daily.sort_values(["ticker", "date"]).reset_index(drop=True)
    intraday = pd.read_csv(DATA_DIR / "intraday_5m.csv", parse_dates=["event_date", "bar_ts"])
    sample = pd.read_csv(DATA_DIR / "intraday_sample.csv", parse_dates=["date"])
    return daily, intraday, sample


def _bars_for(intraday, ticker, event_date):
    bars = intraday[(intraday["ticker"] == ticker) & (intraday["event_date"] == event_date)].copy()
    if bars.empty:
        return None
    bars = bars.set_index("bar_ts").rename(columns={
        "open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume",
    })[["Open", "High", "Low", "Close", "Volume"]].sort_index()
    return bars


def _prior_day_hlc(daily, ticker, event_date):
    """The trading day immediately before event_date for this ticker (NN-1: strictly prior)."""
    rows = daily[(daily["ticker"] == ticker) & (daily["date"] < event_date)]
    if rows.empty:
        return None
    prior = rows.iloc[-1]
    return float(prior["high"]), float(prior["low"]), float(prior["close"])


def _daily_row_index(daily_ticker_rows, event_date):
    idx = daily_ticker_rows.index[daily_ticker_rows["date"] == event_date]
    return idx[0] if len(idx) else None


def _forward_close_return(daily_ticker_rows, i, n_trading_days, entry_price):
    """
    % return from entry_price to the close n_trading_days after row i.
    NN-1: only reads rows strictly after i. Returns None if that many
    future trading days don't exist in the window (excluded, not imputed).
    """
    j = i + n_trading_days
    if j >= len(daily_ticker_rows):
        return None
    exit_close = daily_ticker_rows.iloc[j]["close"]
    if entry_price <= 0:
        return None
    return (exit_close - entry_price) / entry_price * 100.0


def build_leg_a_dataset(daily, intraday, sample):
    component_flags = {c: [] for c in LEG_A_COMPONENTS}
    forward_returns = {h: [] for h in HORIZON_TRADING_DAYS}
    skipped = []
    daily_by_ticker = {t: g.reset_index(drop=True) for t, g in daily.groupby("ticker")}

    for _, ev in sample.iterrows():
        ticker, event_date = ev["ticker"], ev["date"]
        bars = _bars_for(intraday, ticker, event_date)
        if bars is None:
            skipped.append((ticker, str(event_date.date()), "no intraday bars")); continue

        prior = _prior_day_hlc(daily, ticker, event_date)
        if prior is None:
            skipped.append((ticker, str(event_date.date()), "no prior-day H/L/C")); continue
        prior_high, prior_low, prior_close = prior

        rows = daily_by_ticker.get(ticker)
        i = _daily_row_index(rows, event_date) if rows is not None else None
        if i is None:
            skipped.append((ticker, str(event_date.date()), "event date not in daily series")); continue
        entry_close = float(rows.iloc[i]["close"])

        fwd = {}
        ok = True
        for h, n_days in HORIZON_TRADING_DAYS.items():
            r = _forward_close_return(rows, i, n_days, entry_close)
            if r is None:
                ok = False; break
            fwd[h] = r
        if not ok:
            skipped.append((ticker, str(event_date.date()), "insufficient forward daily history")); continue

        flags = daily_fired_flags(bars, prior_high, prior_low, prior_close)
        for c in LEG_A_COMPONENTS:
            component_flags[c].append(flags[c])
        for h in HORIZON_TRADING_DAYS:
            forward_returns[h].append(fwd[h])

    return component_flags, forward_returns, skipped


def build_leg_b_dataset(daily, intraday, sample, trail_pct, init_stop_pct, baseline_n_days):
    trailing_returns, fixed_returns = [], []
    skipped = []
    daily_by_ticker = {t: g.reset_index(drop=True) for t, g in daily.groupby("ticker")}

    for _, ev in sample.iterrows():
        ticker, event_date = ev["ticker"], ev["date"]
        bars = _bars_for(intraday, ticker, event_date)
        if bars is None:
            skipped.append((ticker, str(event_date.date()), "no intraday bars")); continue

        prior = _prior_day_hlc(daily, ticker, event_date)
        if prior is None:
            skipped.append((ticker, str(event_date.date()), "no prior-day H/L/C")); continue
        prior_high, prior_low, prior_close = prior

        alignment = analyze_intraday_alignment(bars, prior_high, prior_low, prior_close)
        trigger = alignment["annotated"]["aligned_trigger"]
        if not trigger.any():
            skipped.append((ticker, str(event_date.date()), "alignment trigger never fired")); continue

        sim = simulate_day_trades(bars, trigger, trail_pct=trail_pct, init_stop_pct=init_stop_pct)
        if not sim["trades"]:
            skipped.append((ticker, str(event_date.date()), "trigger fired but no trade recorded")); continue

        trade = sim["trades"][0]
        entry_price = trade["entry_price"]
        trailing_ret = (trade["exit_price"] - entry_price) / entry_price * 100.0

        rows = daily_by_ticker.get(ticker)
        i = _daily_row_index(rows, event_date) if rows is not None else None
        if i is None:
            skipped.append((ticker, str(event_date.date()), "event date not in daily series")); continue
        fixed_ret = _forward_close_return(rows, i, baseline_n_days, entry_price)
        if fixed_ret is None:
            skipped.append((ticker, str(event_date.date()), "insufficient forward daily history for baseline")); continue

        trailing_returns.append(trailing_ret)
        fixed_returns.append(fixed_ret)

    return np.array(trailing_returns), np.array(fixed_returns), skipped


def main():
    daily, intraday, sample = load_data()
    print(f"Loaded: {len(daily)} daily rows ({daily['ticker'].nunique()} tickers), "
          f"{len(intraday)} intraday rows, {len(sample)} sampled events")

    component_flags, forward_returns, skipped_a = build_leg_a_dataset(daily, intraday, sample)
    print(f"\nLeg A dataset: n={len(forward_returns['1d'])} usable events "
          f"({len(skipped_a)} skipped)")
    for reason in sorted(set(r for _, _, r in skipped_a)):
        n = sum(1 for _, _, rr in skipped_a if rr == reason)
        print(f"  skipped ({n}): {reason}")

    # n_total/n_not_fired now come from leg_a.evaluate_component itself (D-TRADE-044
    # armed in the engine), so the record is self-describing rather than patched
    # here by the caller.
    leg_a_results = leg_a.evaluate_all(component_flags, forward_returns)

    print("\n=== LEG A VERDICTS ===")
    for r in leg_a_results:
        print(f"  {r['component']:24s} {r['horizon']:3s}  fired={r['n_support']:3d}/{r['n_total']:3d} "
              f"(not-fired={r['n_not_fired']:3d})  verdict={r['verdict']}")

    print(f"\nBuilding Leg B dataset (primary cell trail=8%/init=3%, baseline N=5 trading days)...")
    trailing_ret, fixed_ret, skipped_b = build_leg_b_dataset(
        daily, intraday, sample, trail_pct=8, init_stop_pct=3, baseline_n_days=5)
    print(f"Leg B dataset: n={len(trailing_ret)} paired trades ({len(skipped_b)} skipped)")
    for reason in sorted(set(r for _, _, r in skipped_b)):
        n = sum(1 for _, _, rr in skipped_b if rr == reason)
        print(f"  skipped ({n}): {reason}")

    leg_b_primary = leg_b.evaluate_exit_config(trailing_ret, fixed_ret, "trail=8/init=3 vs N=5", is_primary=True)
    print("\n=== LEG B PRIMARY VERDICT ===")
    print(f"  n_support={leg_b_primary['n_support']}  verdict={leg_b_primary['verdict']}")

    leg_b_sensitivity = []
    for cfg in leg_b.SENSITIVITY_CONFIGS:
        t_ret, f_ret, _ = build_leg_b_dataset(
            daily, intraday, sample, trail_pct=cfg["trail_pct"], init_stop_pct=cfg["init_stop_pct"],
            baseline_n_days=leg_b.BASELINE_N_PRIMARY)
        label = f"trail={cfg['trail_pct']}/init={cfg['init_stop_pct']} vs N=5 (sensitivity)"
        leg_b_sensitivity.append(leg_b.evaluate_exit_config(t_ret, f_ret, label, is_primary=False))
    for n_days in leg_b.BASELINE_N_SENSITIVITY:
        t_ret, f_ret, _ = build_leg_b_dataset(
            daily, intraday, sample, trail_pct=leg_b.PRIMARY_CONFIG["trail_pct"],
            init_stop_pct=leg_b.PRIMARY_CONFIG["init_stop_pct"], baseline_n_days=n_days)
        label = f"trail=8/init=3 vs N={n_days} (sensitivity)"
        leg_b_sensitivity.append(leg_b.evaluate_exit_config(t_ret, f_ret, label, is_primary=False))

    print("\n=== LEG B SENSITIVITY (never clearance-eligible) ===")
    for r in leg_b_sensitivity:
        print(f"  {r['config']:40s} n_support={r['n_support']:3d}  verdict={r['verdict']}")

    # Headline tally, computed here so it never needs manual recomputation
    # downstream (D-TRADE-044 dispatch). States all four ratified verdict
    # states explicitly, including zero-counts, so a reader can see what was
    # checked rather than infer it from omissions.
    states = ("CLEARED", "DROPPED", "VOID", "UNMEASURED")
    leg_a_tally = {s: sum(1 for r in leg_a_results if r["verdict"] == s) for s in states}
    leg_b_all = [leg_b_primary] + leg_b_sensitivity
    leg_b_tally = {s: sum(1 for r in leg_b_all if r["verdict"] == s) for s in states}

    print("\n=== HEADLINE (D-TRADE-044 symmetric floor armed) ===")
    print(f"  Leg A ({len(leg_a_results)} tests): "
          + " / ".join(f"{leg_a_tally[s]} {s}" for s in states))
    print(f"  Leg B ({len(leg_b_all)} configs, 1 primary + {len(leg_b_sensitivity)} sensitivity): "
          + " / ".join(f"{leg_b_tally[s]} {s}" for s in states))

    results = {
        "leg_a": leg_a_results,
        "leg_b_primary": leg_b_primary,
        "leg_b_sensitivity": leg_b_sensitivity,
        "leg_a_tally": leg_a_tally,
        "leg_b_tally": leg_b_tally,
        "leg_a_skipped": [{"ticker": t, "date": d, "reason": r} for t, d, r in skipped_a],
        "leg_b_skipped": [{"ticker": t, "date": d, "reason": r} for t, d, r in skipped_b],
    }

    out_path = DATA_DIR.parent / "phase1_cv_results.json"
    import json
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results written to {out_path}")

    return results


if __name__ == "__main__":
    main()
