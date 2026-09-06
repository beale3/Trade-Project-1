"""
AIQ independent re-derivation of the D-TRADE-042 Phase-1 CV run
(helm/validation/run_phase1_cv.py, results in docs/eval/phase1-cv-results.md).

NN-3 discipline: does NOT import helm.screener.adapter or
helm.validation.engine (bar/harness/leg_a/leg_b) -- every feature, CV
computation, and verdict below is reimplemented from scratch against the
raw primitives (tools.rolling_watchlist's scan_all_patterns,
analyze_intraday_alignment, simulate_day_trades) and the raw CSVs. Where
this script's construction choices mirror run_phase1_cv.py's own (e.g. the
Leg-B fixed-N baseline's entry price, the daily-close-to-close target), that
is because those choices are read from its docstring and reasoned about
independently, not copied as code.

Run: python helm/validation/audit/stage3_phase1_cv_audit.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, LeaveOneOut

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.rolling_watchlist import scan_all_patterns, analyze_intraday_alignment, simulate_day_trades

DATA_DIR = Path(__file__).resolve().parents[3] / "helm" / "storage" / "data"
HORIZON_TRADING_DAYS = {"1d": 1, "1w": 5, "1m": 21}
MIN_SUPPORT = 30
SEED_AGREEMENT_THRESHOLD = 90.0
LEG_A_COMPONENTS = (
    "bull_flag_breakout", "flat_top_breakout", "abcd_pattern", "micro_pullback",
    "round_number_breakout", "opening_range_breakout", "premarket_pivot_break",
    "premarket_high_break", "aligned_trigger",
)
PRIMARY_CONFIG = {"trail_pct": 8, "init_stop_pct": 3}
SENSITIVITY_CONFIGS = (
    {"trail_pct": 5, "init_stop_pct": 2}, {"trail_pct": 5, "init_stop_pct": 3},
    {"trail_pct": 8, "init_stop_pct": 2}, {"trail_pct": 12, "init_stop_pct": 2},
    {"trail_pct": 12, "init_stop_pct": 3},
)
BASELINE_N_PRIMARY = 5
BASELINE_N_SENSITIVITY = (1, 21)


# =============================================================================
# my own harness (reimplemented, matches Stage-2's already-audited version)
# =============================================================================

def my_evaluate_loo(X, y):
    X, y = np.asarray(X, dtype=float), np.asarray(y, dtype=float)
    n = len(y)
    preds_model, preds_naive = np.zeros(n), np.zeros(n)
    for train_idx, test_idx in LeaveOneOut().split(X):
        m = LinearRegression().fit(X[train_idx], y[train_idx])
        preds_model[test_idx] = m.predict(X[test_idx])
        preds_naive[test_idx] = y[train_idx].mean()
    rmse_model = float(np.sqrt(np.mean((y - preds_model) ** 2)))
    rmse_naive = float(np.sqrt(np.mean((y - preds_naive) ** 2)))
    return {"beats_naive_baseline": bool(rmse_model < rmse_naive),
            "rmse_model": rmse_model, "rmse_naive": rmse_naive}


def my_evaluate_multiseed_kfold(X, y, n_splits=5, n_seeds=30):
    X, y = np.asarray(X, dtype=float), np.asarray(y, dtype=float)
    beats = []
    for seed in range(n_seeds):
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
        rm_folds, rn_folds = [], []
        for train_idx, test_idx in kf.split(X):
            m = LinearRegression().fit(X[train_idx], y[train_idx])
            pm = m.predict(X[test_idx])
            pn = np.full(len(test_idx), y[train_idx].mean())
            rm_folds.append(np.sqrt(np.mean((y[test_idx] - pm) ** 2)))
            rn_folds.append(np.sqrt(np.mean((y[test_idx] - pn) ** 2)))
        beats.append(np.mean(rm_folds) < np.mean(rn_folds))
    return {"pct_seeds_beating_naive": round(100 * float(np.mean(beats)), 1)}


def my_loo_paired(y_treatment, y_baseline):
    n = len(y_treatment)
    full_sample_diff = float(y_treatment.mean() - y_baseline.mean())
    diffs = np.empty(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        diffs[i] = y_treatment[mask].mean() - y_baseline[mask].mean()
    if full_sample_diff > 0:
        pct_agreeing = float(np.mean(diffs > 0)) * 100
    elif full_sample_diff < 0:
        pct_agreeing = float(np.mean(diffs < 0)) * 100
    else:
        pct_agreeing = 0.0
    return {"full_sample_diff": round(full_sample_diff, 6), "pct_loo_estimates_agreeing": round(pct_agreeing, 1),
            "beats_naive_baseline": bool(full_sample_diff > 0 and pct_agreeing == 100.0)}


def my_multiseed_kfold_paired(y_treatment, y_baseline, n_splits=5, n_seeds=30):
    n = len(y_treatment)
    beats = []
    for seed in range(n_seeds):
        rng = np.random.RandomState(seed)
        idx = rng.permutation(n)
        for fold in np.array_split(idx, n_splits):
            if len(fold) == 0:
                continue
            diff = y_treatment[fold].mean() - y_baseline[fold].mean()
            beats.append(diff > 0)
    return {"pct_seeds_beating_naive": round(100 * float(np.mean(beats)), 1) if beats else 0.0}


def my_clearance_verdict(loo, kfold, n_support):
    if n_support < MIN_SUPPORT:
        return "UNMEASURED"
    cleared = loo["beats_naive_baseline"] and kfold["pct_seeds_beating_naive"] >= SEED_AGREEMENT_THRESHOLD
    return "CLEARED" if cleared else "DROPPED"


# =============================================================================
# my own data construction (reads raw CSVs + calls raw scanner primitives
# directly -- no helm.screener, no helm.validation.engine)
# =============================================================================

def load_data():
    daily = pd.read_csv(DATA_DIR / "ohlcv_daily.csv", parse_dates=["date"]).sort_values(["ticker", "date"]).reset_index(drop=True)
    intraday = pd.read_csv(DATA_DIR / "intraday_5m.csv", parse_dates=["event_date", "bar_ts"])
    sample = pd.read_csv(DATA_DIR / "intraday_sample.csv", parse_dates=["date"])
    return daily, intraday, sample


def bars_for(intraday, ticker, event_date):
    bars = intraday[(intraday["ticker"] == ticker) & (intraday["event_date"] == event_date)].copy()
    if bars.empty:
        return None
    bars = bars.set_index("bar_ts").rename(columns={
        "open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"})[
        ["Open", "High", "Low", "Close", "Volume"]].sort_index()
    return bars


def prior_day_hlc(daily, ticker, event_date):
    rows = daily[(daily["ticker"] == ticker) & (daily["date"] < event_date)]
    if rows.empty:
        return None
    p = rows.iloc[-1]
    return float(p["high"]), float(p["low"]), float(p["close"])


def forward_close_return(daily_ticker_rows, i, n_days, entry_price):
    j = i + n_days
    if j >= len(daily_ticker_rows) or entry_price <= 0:
        return None
    return (daily_ticker_rows.iloc[j]["close"] - entry_price) / entry_price * 100.0


def build_leg_a(daily, intraday, sample):
    flags_by_component = {c: [] for c in LEG_A_COMPONENTS}
    fwd_by_horizon = {h: [] for h in HORIZON_TRADING_DAYS}
    skipped = 0
    daily_by_ticker = {t: g.reset_index(drop=True) for t, g in daily.groupby("ticker")}

    for _, ev in sample.iterrows():
        ticker, event_date = ev["ticker"], ev["date"]
        bars = bars_for(intraday, ticker, event_date)
        if bars is None:
            skipped += 1; continue
        prior = prior_day_hlc(daily, ticker, event_date)
        if prior is None:
            skipped += 1; continue
        prior_high, prior_low, prior_close = prior
        rows = daily_by_ticker.get(ticker)
        idx = rows.index[rows["date"] == event_date] if rows is not None else []
        if len(idx) == 0:
            skipped += 1; continue
        i = idx[0]
        entry_close = float(rows.iloc[i]["close"])

        fwd, ok = {}, True
        for h, n_days in HORIZON_TRADING_DAYS.items():
            r = forward_close_return(rows, i, n_days, entry_close)
            if r is None:
                ok = False; break
            fwd[h] = r
        if not ok:
            skipped += 1; continue

        # my own feature extraction, calling the raw scanner primitives directly
        patterns = scan_all_patterns(bars)
        alignment = analyze_intraday_alignment(bars, prior_high, prior_low, prior_close)
        aligned_trigger = alignment["annotated"]["aligned_trigger"].reindex(patterns.index).fillna(False)

        fired_today = {c: bool(patterns[c].to_numpy().any()) for c in LEG_A_COMPONENTS if c != "aligned_trigger"}
        fired_today["aligned_trigger"] = bool(aligned_trigger.to_numpy().any())

        for c in LEG_A_COMPONENTS:
            flags_by_component[c].append(fired_today[c])
        for h in HORIZON_TRADING_DAYS:
            fwd_by_horizon[h].append(fwd[h])

    return flags_by_component, fwd_by_horizon, skipped


def build_leg_b(daily, intraday, sample, trail_pct, init_stop_pct, baseline_n_days):
    trailing_returns, fixed_returns = [], []
    skipped = 0
    daily_by_ticker = {t: g.reset_index(drop=True) for t, g in daily.groupby("ticker")}

    for _, ev in sample.iterrows():
        ticker, event_date = ev["ticker"], ev["date"]
        bars = bars_for(intraday, ticker, event_date)
        if bars is None:
            skipped += 1; continue
        prior = prior_day_hlc(daily, ticker, event_date)
        if prior is None:
            skipped += 1; continue
        prior_high, prior_low, prior_close = prior

        alignment = analyze_intraday_alignment(bars, prior_high, prior_low, prior_close)
        trigger = alignment["annotated"]["aligned_trigger"]
        if not trigger.any():
            skipped += 1; continue

        sim = simulate_day_trades(bars, trigger, trail_pct=trail_pct, init_stop_pct=init_stop_pct)
        if not sim["trades"]:
            skipped += 1; continue
        trade = sim["trades"][0]
        entry_price = trade["entry_price"]
        trailing_ret = (trade["exit_price"] - entry_price) / entry_price * 100.0

        rows = daily_by_ticker.get(ticker)
        idx = rows.index[rows["date"] == event_date] if rows is not None else []
        if len(idx) == 0:
            skipped += 1; continue
        fixed_ret = forward_close_return(rows, idx[0], baseline_n_days, entry_price)
        if fixed_ret is None:
            skipped += 1; continue

        trailing_returns.append(trailing_ret)
        fixed_returns.append(fixed_ret)

    return np.array(trailing_returns), np.array(fixed_returns), skipped


def main():
    daily, intraday, sample = load_data()
    print(f"Loaded: {len(daily)} daily rows, {len(intraday)} intraday rows, {len(sample)} sampled events\n")

    flags, fwd, skipped_a = build_leg_a(daily, intraday, sample)
    n = len(fwd["1d"])
    print(f"=== MY INDEPENDENT LEG A: n={n} usable events ({skipped_a} skipped) ===")
    results_a = []
    for c in LEG_A_COMPONENTS:
        fired = np.asarray(flags[c], dtype=bool)
        n_support = int(fired.sum())
        for h in HORIZON_TRADING_DAYS:
            y = np.asarray(fwd[h], dtype=float)
            X = fired.astype(float).reshape(-1, 1)
            if n_support < MIN_SUPPORT:
                verdict, loo, kf = "UNMEASURED", None, None
            else:
                loo = my_evaluate_loo(X, y)
                kf = my_evaluate_multiseed_kfold(X, y)
                verdict = my_clearance_verdict(loo, kf, n_support)
            results_a.append({"component": c, "horizon": h, "n_support": n_support, "n_total": n,
                               "verdict": verdict, "loo": loo, "kfold": kf})
            print(f"  {c:24s} {h:3s}  fired={n_support:3d}/{n:3d}  verdict={verdict}"
                  + (f"  (LOO rmse_model={loo['rmse_model']:.5f} rmse_naive={loo['rmse_naive']:.5f}, "
                     f"kfold={kf['pct_seeds_beating_naive']}%)" if loo else ""))

    print(f"\n=== MY LEG A SUMMARY ===")
    cleared = [r for r in results_a if r["verdict"] == "CLEARED"]
    print(f"CLEARED: {len(cleared)} -> {[(r['component'], r['horizon']) for r in cleared]}")
    print(f"DROPPED: {sum(1 for r in results_a if r['verdict']=='DROPPED')}")
    print(f"UNMEASURED: {sum(1 for r in results_a if r['verdict']=='UNMEASURED')}")

    print(f"\n=== aligned_trigger degeneracy check (my own numbers) ===")
    at_fired = np.asarray(flags["aligned_trigger"], dtype=bool)
    print(f"aligned_trigger fired: {at_fired.sum()}/{len(at_fired)} (all True: {at_fired.all()})")
    for h in HORIZON_TRADING_DAYS:
        y = np.asarray(fwd[h], dtype=float)
        X = at_fired.astype(float).reshape(-1, 1)
        loo = my_evaluate_loo(X, y)
        print(f"  {h}: rmse_model={loo['rmse_model']:.10f}  rmse_naive={loo['rmse_naive']:.10f}  "
              f"exactly_equal={loo['rmse_model']==loo['rmse_naive']}")

    print(f"\n=== MY INDEPENDENT LEG B ===")
    t_ret, f_ret, skipped_b = build_leg_b(daily, intraday, sample, trail_pct=PRIMARY_CONFIG["trail_pct"],
                                          init_stop_pct=PRIMARY_CONFIG["init_stop_pct"], baseline_n_days=BASELINE_N_PRIMARY)
    n_b = len(t_ret)
    full_diff = float(t_ret.mean() - f_ret.mean())
    loo_b = my_loo_paired(t_ret, f_ret)
    kf_b = my_multiseed_kfold_paired(t_ret, f_ret)
    verdict_b = my_clearance_verdict(loo_b, kf_b, n_b)
    print(f"Primary (trail=8/init=3 vs N=5): n={n_b} ({skipped_b} skipped)")
    print(f"  full-sample mean diff = {full_diff:.4f} pts")
    print(f"  LOO pct_agreeing = {loo_b['pct_loo_estimates_agreeing']}%  beats_naive={loo_b['beats_naive_baseline']}")
    print(f"  5-fold seed agreement = {kf_b['pct_seeds_beating_naive']}%")
    print(f"  verdict = {verdict_b}")

    print(f"\n=== MY LEG B SENSITIVITY ===")
    sens_results = []
    for cfg in SENSITIVITY_CONFIGS:
        t, f, sk = build_leg_b(daily, intraday, sample, trail_pct=cfg["trail_pct"], init_stop_pct=cfg["init_stop_pct"],
                                baseline_n_days=BASELINE_N_PRIMARY)
        loo_s = my_loo_paired(t, f); kf_s = my_multiseed_kfold_paired(t, f)
        v = my_clearance_verdict(loo_s, kf_s, len(t))
        sens_results.append((f"trail={cfg['trail_pct']}/init={cfg['init_stop_pct']} vs N=5", len(t), v))
    for n_days in BASELINE_N_SENSITIVITY:
        t, f, sk = build_leg_b(daily, intraday, sample, trail_pct=PRIMARY_CONFIG["trail_pct"],
                                init_stop_pct=PRIMARY_CONFIG["init_stop_pct"], baseline_n_days=n_days)
        loo_s = my_loo_paired(t, f); kf_s = my_multiseed_kfold_paired(t, f)
        v = my_clearance_verdict(loo_s, kf_s, len(t))
        sens_results.append((f"trail=8/init=3 vs N={n_days}", len(t), v))
    for label, n_s, v in sens_results:
        print(f"  {label:35s} n={n_s:3d}  verdict={v}")

    return results_a, {"n": n_b, "full_diff": full_diff, "loo": loo_b, "kfold": kf_b, "verdict": verdict_b}, sens_results


if __name__ == "__main__":
    main()
