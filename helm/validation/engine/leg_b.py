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

**Stage-2 audit fixes (AIQ, 2026-08-31)** -- the adaptation above was
confirmed methodologically sound; these fix two execution gaps AIQ found,
not the design:
  - **Finding 2 (verdict doesn't disclose stability-vs-generalization):**
    every record now carries `"validation_kind": "stability_check"` --
    Leg B asks "does the observed advantage survive being viewed through
    different partitions of the SAME already-fully-known trades," not
    "does it predict unseen data" (Leg A's `"held_out_prediction"`, see
    leg_a.py). The distinction now travels with the number, not just the
    docstring.
  - **Finding 4 (undocumented 5th verdict state):** removed
    `"SENSITIVITY_ONLY_WOULD_CLEAR"`. `evaluate_exit_config` now returns
    only the ratified 4-state verdict (CLEARED/DROPPED/VOID/UNMEASURED);
    `is_primary` (already a field on every record) is the ONLY signal for
    clearance-eligibility. **Binding rule for every consumer of this
    record: a CLEARED verdict is a real clearance claim ONLY when
    is_primary is True. A CLEARED record with is_primary=False is
    sensitivity evidence and must never be reported, gated on, or wired
    into a `_gates` flag as if it were a clearance (OP-1 anti-cherry-pick)
    -- this module does not enforce that at the type level, so whoever
    reads/persists/reports these records (validation_verdicts, a future
    report generator, QA's Stage-3 re-run) must carry it forward.**
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
    """
    Stage-2 audit fix (AIQ finding #1): the ORIGINAL statistic here was the
    MEAN of the n leave-one-out estimates -- AIQ built a concrete fixture
    (35 trades: 34 with a small consistent disadvantage for treatment,
    1 outlier with a large advantage that alone flips the full-sample mean
    positive) and showed the mean-of-LOO-estimates stays positive too,
    because each individual estimate only removes 1/n of one trade's
    influence -- n-1 of the n estimates still contain the outlier and stay
    biased the same direction as the full sample; only the single estimate
    that actually excludes the outlier flips. Averaging them together
    dilutes the one estimate that would have caught it, making the
    statistic close to redundant with just checking the full-sample sign.

    Fixed by requiring UNANIMOUS agreement: every one of the n leave-one-out
    estimates must agree in sign with the full-sample direction for the
    result to count as "beats naive" -- if excluding even ONE trade flips
    the direction, that single trade is driving the conclusion, and this
    correctly reports that as not robust. This directly resolves AIQ's
    fixture: the outlier-excluding estimate disagrees in sign, so
    beats_naive_baseline is correctly False despite the positive
    full-sample mean.
    """
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

    return {
        "n": n,
        "full_sample_diff": round(full_sample_diff, 6),
        "pct_loo_estimates_agreeing": round(pct_agreeing, 1),
        "beats_naive_baseline": bool(full_sample_diff > 0 and pct_agreeing == 100.0),
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
        # Stage-2 audit fix (AIQ finding #4): no verdict-string downgrade here
        # anymore -- the true 4-state verdict is always returned. is_primary is
        # the ONLY clearance-eligibility signal (see module docstring's binding
        # rule for consumers: CLEARED + is_primary=False is sensitivity evidence,
        # never a real clearance).

    return {
        "config": config_label, "is_primary": is_primary, "n_support": n_support,
        "verdict": verdict, "loo": loo_result, "kfold": kfold_result,
        # Stage-2 audit (AIQ finding #2): Leg B checks whether the observed
        # advantage survives resampling the SAME known trades, not whether it
        # predicts unseen ones (contrast leg_a.py's "held_out_prediction").
        "validation_kind": "stability_check",
    }
