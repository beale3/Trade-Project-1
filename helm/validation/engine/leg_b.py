"""
Leg B: exit-rule validation (ADR-0001 §6.2/§6.3, D-TRADE-036 locked
parameters). Compares realized trade return under the trailing-stop exit
vs. the fixed-holding-period baseline, same entries.

D-TRADE-036 fixed BOTH the trail grid's primary cell (trail_pct=8,
init_stop_pct=3) and the baseline N (=5 trading days) as pre-registered
constants, not data-derived/fitted parameters -- this sidesteps NN-10's
original train-fold-only requirement entirely (AIQ's 2026-08-31 catch-up
note: "OP-3 chose the leakage-free fixed-N path... sidesteps my original
audit finding #2"). No nested-CV grid/N selection is implemented here
because none is needed: PRIMARY_CONFIG/BASELINE_N_PRIMARY are fixed
constants applied identically to every trade regardless of fold. The
other 5 grid cells + N=1/N=21 are SENSITIVITY_CONFIGS/BASELINE_N_SENSITIVITY
-- reported, never clearance-eligible (OP-1's anti-cherry-pick rule).

**Methodology adaptation, flagged plainly for AIQ's independent judgment
(protocol 17) rather than silently baked in:** there is no FITTED model
in Leg B -- the exit parameters are fixed constants, so "beats naive OOS
under LOO/5-fold" cannot mean "fit on train, predict on test" the way Leg
A's regression does. Both arms' realized returns are directly computable
from the same intraday bars for every trade (this is a PAIRED comparison,
not a predictive model), so this module reuses the LOO + 5-fold x 30-seed
harness's SHAPE, adapted as follows:
  - LOO analog: leave one trade out, recompute the mean-return difference
    over the remaining n-1 trades, repeat for every trade. Checks whether
    the trailing-beats-fixed verdict is robust to any single trade (guards
    against one outlier driving the whole result) -- NOT a predictive
    holdout in the regression sense.
  - 5-fold x 30-seed analog: for 30 independent random 5-way splits of the
    trade sample, check whether trailing's mean return exceeds fixed's
    mean return WITHIN each held-out fold. pct_seeds_beating_naive reports
    the fraction of fold-evaluations (150 total) where trailing wins,
    reusing exactly the same statistic and D-TRADE-021 threshold Leg A
    uses, on genuinely different underlying arithmetic.
This is a judgment call about how to extend a regression-shaped harness to
a rule-comparison that has no model to fit -- correct if AIQ's independent
re-derivation agrees "beats naive, robustly" is the right question to ask
this way; if AIQ's audit finds this translation unsound, the METHOD is the
defect, not the trailing-stop rule or the D-TRADE-036 numbers.
"""
import numpy as np

from helm.validation.engine.bar import clearance_verdict

PRIMARY_CONFIG = {"trail_pct": 8, "init_stop_pct": 3}  # D-TRADE-036
SENSITIVITY_CONFIGS = (
    {"trail_pct": 5, "init_stop_pct": 2},
    {"trail_pct": 5, "init_stop_pct": 3},
    {"trail_pct": 8, "init_stop_pct": 2},
    {"trail_pct": 12, "init_stop_pct": 2},
    {"trail_pct": 12, "init_stop_pct": 3},
)
BASELINE_N_PRIMARY = 5  # trading days, D-TRADE-036
BASELINE_N_SENSITIVITY = (1, 21)


def _loo_paired(y_treatment, y_baseline):
    n = len(y_treatment)
    diffs = np.empty(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        diffs[i] = y_treatment[mask].mean() - y_baseline[mask].mean()
    loo_mean_diff = float(diffs.mean())
    return {
        "n": n,
        "loo_mean_diff": round(loo_mean_diff, 6),
        "beats_naive_baseline": bool(loo_mean_diff > 0),
    }


def _multiseed_kfold_paired(y_treatment, y_baseline, n_splits=5, n_seeds=30):
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
    return {
        "n_seeds": n_seeds, "n_splits": n_splits,
        "pct_seeds_beating_naive": round(100 * float(np.mean(beats)), 1) if beats else 0.0,
    }


def evaluate_exit_config(trailing_returns, fixed_returns, config_label, is_primary):
    """
    trailing_returns / fixed_returns: 1-D float arrays, same length, same
    order -- realized per-trade return under each exit rule, computed from
    the SAME entry signals (paired, not independent samples).
    is_primary: caller states this explicitly -- this function does not
    infer it from the label, so a mislabeled sensitivity cell can never
    silently read as clearance-eligible (OP-1 anti-cherry-pick).
    """
    y_t = np.asarray(trailing_returns, dtype=float)
    y_f = np.asarray(fixed_returns, dtype=float)
    if len(y_t) != len(y_f):
        raise ValueError("trailing_returns and fixed_returns must be paired (same length)")

    n_support = len(y_t)
    if n_support < 30:
        verdict = "UNMEASURED"
        loo_result = kfold_result = None
    else:
        loo_result = _loo_paired(y_t, y_f)
        kfold_result = _multiseed_kfold_paired(y_t, y_f)
        verdict = clearance_verdict(loo_result, kfold_result, n_support)
        # Sensitivity cells are reported but never a clearance claim (OP-1) --
        # downgrade a would-be CLEARED to NOT_ELIGIBLE_SENSITIVITY rather than
        # silently keep CLEARED on a cell that was never pre-registered as primary.
        if not is_primary and verdict == "CLEARED":
            verdict = "SENSITIVITY_ONLY_WOULD_CLEAR"

    return {
        "config": config_label, "is_primary": is_primary, "n_support": n_support,
        "verdict": verdict, "loo": loo_result, "kfold": kfold_result,
    }
