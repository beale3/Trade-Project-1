"""
AIQ Stage-2 independent audit of AI/ML's Stage-1 delivery (ADR-0001 NN-1/NN-3,
D-TRADE-021, this session's 2026-08-31 catch-up). Every computation below is
this seat's own, built from scratch against the raw primitives in
tools/rolling_watchlist.py -- it does NOT import helm/screener/adapter.py or
anything under helm/validation/engine/ (NN-3: builder != judge extends to the
feature layer). Where this script's own numbers are compared to a claim in
AI/ML's delivered code, that claim was read from source (Read tool, this
session) and reasoned about independently -- never executed as part of my
verdict.

Run: python helm/validation/audit/stage2_audit.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, LeaveOneOut

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.rolling_watchlist import simulate_day_trades  # the raw primitive, not the engine

RNG_SEED = 12345  # this audit's own seed, independent of AI/ML's/the Lead's test fixtures


# =============================================================================
# PART 1 -- trailing-stop mechanics (tools/rolling_watchlist.py, direct call)
# =============================================================================

def make_intraday_df(ohlc_rows):
    idx = pd.date_range("2026-01-05 09:30", periods=len(ohlc_rows), freq="1min")
    df = pd.DataFrame(ohlc_rows, columns=["Open", "High", "Low", "Close"], index=idx)
    return df


def test_trailing_stop_ratchet():
    """
    Hand-computed fixture, independent of AI/ML's/the Lead's own test values.
    Bars (O/H/L/C), entry triggers on bar 0 at Close=100:
      bar0: H=101 L=99  C=100   (entry bar)
      bar1: H=105 L=104 C=104.5
      bar2: H=110 L=108 C=109
      bar3: H=108 L=95  C=96    <- Low breaches the ratcheted trail here
      bar4: H=97  L=90  C=91
    trail_pct=8, init_stop_pct=3 (D-TRADE-036 primary cell).

    By hand:
      init_stop = 100*(1-0.03) = 97.0
      peak(0)=101 -> eff_stop(0)=max(97.0, 101*0.92=92.92)=97.0
      peak(1)=max(101,105)=105 -> eff_stop(1)=max(97.0, 105*0.92=96.6)=97.0 (still init floor)
      peak(2)=max(105,110)=110 -> eff_stop(2)=max(97.0, 110*0.92=101.2)=101.2 (trail now governs)
      peak(3)=max(110,108)=110 -> eff_stop(3)=101.2 (unchanged, 108<110)
        low(3)=95 <= 101.2 -> EXIT at 101.2, reason=trailing_stop
    Expected: 1 trade, exit_price=101.2, pnl=(101.2-100)*shares.
    """
    df = make_intraday_df([
        (100, 101, 99, 100),
        (100, 105, 104, 104.5),
        (104.5, 110, 108, 109),
        (109, 108, 95, 96),
        (96, 97, 90, 91),
    ])
    trigger = pd.Series([True, False, False, False, False], index=df.index)
    result = simulate_day_trades(df, trigger, trail_pct=8, init_stop_pct=3, shares_per_trade=1)

    assert result["num_trades"] == 1, f"expected 1 trade, got {result['num_trades']}"
    trade = result["trades"][0]
    assert trade["reason"] == "trailing_stop", f"expected trailing_stop exit, got {trade['reason']}"
    assert abs(trade["exit_price"] - 101.2) < 1e-9, f"expected exit 101.2, got {trade['exit_price']}"
    assert abs(trade["pnl"] - 1.2) < 1e-9, f"expected pnl 1.2, got {trade['pnl']}"
    return "PASS: ratchet exits at hand-computed 101.2, matches SS6.3's formula exactly"


def test_trailing_stop_never_rises_bounded_at_init_floor():
    """
    A trade that only falls from entry should exit at EXACTLY the init hard
    stop, never below it (ADR-0001 SS6.3: 'loss is bounded at init_stop_pct
    regardless of what the trail does'). entry_price = bar0's CLOSE (100.0,
    per simulate_day_trades' own convention: price=closes[i] at trigger) --
    High is kept below entry throughout so the trail floor never rises above
    the init hard stop.
    """
    df = make_intraday_df([
        (100, 100, 99, 100.0),   # entry bar; entry_price = Close = 100.0
        (100, 99.8, 96, 97),     # High(99.8) < entry(100), low breaches init floor (97.0) here
        (97, 97, 90, 91),
    ])
    trigger = pd.Series([True, False, False], index=df.index)
    result = simulate_day_trades(df, trigger, trail_pct=8, init_stop_pct=3, shares_per_trade=1)
    trade = result["trades"][0]
    assert abs(trade["exit_price"] - 97.0) < 1e-9, f"expected exit exactly at init floor 97.0, got {trade['exit_price']}"
    assert abs(trade["pnl"] - (-3.0)) < 1e-9, f"loss should be exactly -3.0 (3% of 100), got {trade['pnl']}"
    return "PASS: never-rising trade bounded at exactly the init hard stop (100.0 -> 97.0, -3.0 pnl)"


def test_trailing_stop_no_lookahead():
    """
    NN-1: the exit decision at bar i must be IDENTICAL whether or not future
    bars (i+1, i+2, ...) exist. Truncate the same series after the bar where
    the ratchet fixture above exits (bar 3) and confirm bar 3's trade record
    is byte-identical to the untruncated run -- if peak(t) or the exit check
    ever looked ahead, truncating would change the outcome.
    """
    full = make_intraday_df([
        (100, 101, 99, 100), (100, 105, 104, 104.5), (104.5, 110, 108, 109),
        (109, 108, 95, 96), (96, 97, 90, 91),
    ])
    truncated = full.iloc[:4]  # drop bar 4 entirely
    trigger_full = pd.Series([True, False, False, False, False], index=full.index)
    trigger_trunc = trigger_full.iloc[:4]

    r_full = simulate_day_trades(full, trigger_full, trail_pct=8, init_stop_pct=3, shares_per_trade=1)
    r_trunc = simulate_day_trades(truncated, trigger_trunc, trail_pct=8, init_stop_pct=3, shares_per_trade=1)

    t_full, t_trunc = r_full["trades"][0], r_trunc["trades"][0]
    assert t_full["exit_price"] == t_trunc["exit_price"] == 101.2
    assert t_full["reason"] == t_trunc["reason"] == "trailing_stop"
    return "PASS: bar-3 exit identical with or without bar 4 present -- no lookahead"


def test_trailing_stop_backward_compat():
    """trail_pct=None (default) must reproduce the pre-existing fixed-mode math exactly."""
    df = make_intraday_df([(100, 101, 99, 100), (100, 103, 99.5, 101), (101, 101.5, 98, 99)])
    trigger = pd.Series([True, False, False], index=df.index)
    result = simulate_day_trades(df, trigger, stop_loss_pct=2.0, min_risk_reward=2.0, shares_per_trade=1)
    # hand: stop=100*0.98=98.0, risk=2.0, target=100+2*2=104.0.
    # bar1: High=103 < target(104), Low=99.5 > stop(98.0) -> neither hit, continue.
    # bar2 (last bar): High=101.5 < target, Low=98 == stop(98.0) -> stop hit first in the check order.
    assert result["trades"][0]["reason"] == "stop", f"expected stop exit, got {result['trades'][0]['reason']}"
    assert abs(result["trades"][0]["exit_price"] - 98.0) < 1e-9
    return "PASS: fixed mode (trail_pct=None) matches the pre-existing stop/target formula exactly"


# =============================================================================
# PART 2 -- independent re-implementation of the CV harness (NOT importing
# helm/validation/engine/harness.py). Same algorithm shape as the 4 studies'
# proven template; every line here is mine.
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


def test_harness_detects_planted_effect_and_rejects_noise():
    rng = np.random.RandomState(RNG_SEED)
    n = 200
    # Planted case: a real, moderate effect + noise -- fired days have a
    # higher mean forward return than non-fired days.
    fired = rng.random(n) < 0.35
    y_planted = np.where(fired, rng.normal(0.02, 0.05, n), rng.normal(0.0, 0.05, n))
    X = fired.astype(float).reshape(-1, 1)
    loo_p = my_evaluate_loo(X, y_planted)
    kf_p = my_evaluate_multiseed_kfold(X, y_planted)
    cleared_planted = loo_p["beats_naive_baseline"] and kf_p["pct_seeds_beating_naive"] >= 90.0

    # Noise case: fired is unrelated to y.
    y_noise = rng.normal(0.0, 0.05, n)
    loo_n = my_evaluate_loo(X, y_noise)
    kf_n = my_evaluate_multiseed_kfold(X, y_noise)
    cleared_noise = loo_n["beats_naive_baseline"] and kf_n["pct_seeds_beating_naive"] >= 90.0

    assert cleared_planted, f"planted effect should clear the bar, got LOO={loo_p}, kfold={kf_p}"
    assert not cleared_noise, f"pure noise should NOT clear the bar, got LOO={loo_n}, kfold={kf_n}"
    return (f"PASS: independent harness reimplementation correctly separates signal "
            f"(kfold={kf_p['pct_seeds_beating_naive']}%) from noise (kfold={kf_n['pct_seeds_beating_naive']}%) "
            f"-- confirms the ALGORITHM AI/ML describes is soundly implementable, on my own code")


# =============================================================================
# PART 3 -- Leg B methodology: empirical test of the LOO-paired outlier check
# (the specific judgment AI/ML asked for). Constructs a case designed to
# check whether leg_b.py's "mean of n leave-one-out diffs" statistic actually
# catches a single dominant outlier trade, as a robustness/outlier check
# should.
# =============================================================================

def loo_paired_as_described(y_treatment, y_baseline):
    """Reimplementation of leg_b.py's _loo_paired, from its docstring + source
    (read, not imported) -- so I can probe its behavior on a case I construct."""
    n = len(y_treatment)
    diffs = np.empty(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        diffs[i] = y_treatment[mask].mean() - y_baseline[mask].mean()
    return float(diffs.mean()), diffs


def test_leg_b_loo_outlier_sensitivity():
    """
    35 trades: 34 have a small, consistent, SLIGHTLY NEGATIVE paired
    advantage for trailing (trailing loses by a hair), 1 outlier trade has a
    huge positive advantage for trailing that, on its own, flips the
    full-sample mean positive. A genuine outlier/robustness check should flag
    this as fragile -- e.g. detect that removing the outlier flips the
    verdict. Test whether leg_b.py's actual statistic (mean of the n
    leave-one-out diffs) does that, or whether it stays on the same side
    regardless (my finding: it barely moves, because each leave-one-out
    estimate only removes 1/n of one trade's influence).
    """
    n = 35
    y_treatment = np.full(n, 0.0)
    y_baseline = np.full(n, 0.001)  # every ordinary trade: trailing loses by 0.001
    y_treatment[-1] = 0.10          # one outlier: trailing wins by a lot on trade 35
    y_baseline[-1] = 0.0

    full_sample_diff = y_treatment.mean() - y_baseline.mean()
    loo_mean_diff, individual_diffs = loo_paired_as_described(y_treatment, y_baseline)

    # The diagnostic a real outlier check should produce: does DROPPING the
    # outlier (leaving it out) flip the sign, i.e. is diffs[-1] (the estimate
    # that excludes the outlier) negative while the full sample is positive?
    outlier_dropped_diff = individual_diffs[-1]  # leaves out trade 35, the outlier
    sign_flips_when_outlier_dropped = (full_sample_diff > 0) and (outlier_dropped_diff < 0)

    # What leg_b.py's actual verdict statistic (mean of all n loo estimates)
    # reports: does IT flip, or does it just barely move off the full-sample value?
    verdict_statistic_flips = (full_sample_diff > 0) and (loo_mean_diff < 0)

    assert sign_flips_when_outlier_dropped, (
        "fixture is broken -- dropping the outlier should reveal the other 34 trades "
        "are actually negative for trailing"
    )
    result = (
        f"full-sample mean diff = {full_sample_diff:.6f} (positive, driven entirely by 1 of 35 trades)\n"
        f"  the ONE leave-one-out estimate that actually excludes the outlier = {outlier_dropped_diff:.6f} "
        f"({'correctly negative' if outlier_dropped_diff < 0 else 'WRONG'})\n"
        f"  leg_b.py's reported statistic (mean of all 35 leave-one-out estimates) = {loo_mean_diff:.6f} "
        f"({'still positive -- did NOT flag the outlier' if loo_mean_diff > 0 else 'flagged it'})"
    )
    if verdict_statistic_flips:
        return f"NO FINDING -- leg_b.py's LOO statistic did flip on this fixture:\n{result}"
    return (f"FINDING CONFIRMED -- leg_b.py's _loo_paired verdict statistic (mean of n "
            f"leave-one-out estimates) fails to flag a single-trade-driven result: {result}")


if __name__ == "__main__":
    tests = [
        test_trailing_stop_ratchet,
        test_trailing_stop_never_rises_bounded_at_init_floor,
        test_trailing_stop_no_lookahead,
        test_trailing_stop_backward_compat,
        test_harness_detects_planted_effect_and_rejects_noise,
        test_leg_b_loo_outlier_sensitivity,
    ]
    failures = 0
    for t in tests:
        try:
            print(f"[{t.__name__}] {t()}")
        except AssertionError as e:
            failures += 1
            print(f"[{t.__name__}] FAIL: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
