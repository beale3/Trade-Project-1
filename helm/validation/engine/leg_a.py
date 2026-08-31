"""
Leg A: entry-signal validation (ADR-0001 §6.2, OP-4 final component list).
Tests whether a scanner component firing on a given day predicts forward
stock return over OP-2's horizons (1d/1w/1m), beating a naive baseline
OOS, via the D-TRADE-021 bar.

Scope note: this module produces the verdict RECORD. Wiring a CLEARED
verdict back into a `_gates` flag on the live scanner (NN-4) is a
separate, later step -- tools/rolling_watchlist.py has no `_gates`
parameter for the pattern detectors today (only float/catalyst/
short_interest_gates exist), and extending the scanner's gate surface is
outside this build's stated scope ("build the entry-signal + trailing-
stop LOGIC," not "wire verdicts into the live scanner").
"""
import numpy as np

from helm.validation.engine.bar import clearance_verdict
from helm.validation.engine.harness import evaluate_loo, evaluate_multiseed_kfold

HORIZONS = ("1d", "1w", "1m")
HORIZON_TRADING_DAYS = {"1d": 1, "1w": 5, "1m": 21}


def evaluate_component(fired_flags, forward_returns, component, horizon):
    """
    fired_flags: 1-D bool array/sequence, one entry per observation day --
    did `component` fire that day (helm.screener.adapter.daily_fired_flags,
    collected across the backtest cohort).
    forward_returns: 1-D float array/sequence, same length/order -- the
    forward return over `horizon` from that day's close. Caller is
    responsible for point-in-time construction (NN-1: forward_returns[i]
    must use only data strictly after the signal date at fired_flags[i])
    and for excluding rows without enough trailing/forward history rather
    than passing NaN in.

    n_support counts TRUE firings only, not the full cohort length --
    the D-TRADE-029 floor gates on how many times this component actually
    fired, not how many days were observed.
    """
    fired = np.asarray(fired_flags, dtype=bool)
    y = np.asarray(forward_returns, dtype=float)
    if len(fired) != len(y):
        raise ValueError("fired_flags and forward_returns must be the same length")

    n_support = int(fired.sum())
    if n_support < 30:
        return {
            "component": component, "horizon": horizon, "n_support": n_support,
            "verdict": "UNMEASURED", "loo": None, "kfold": None,
        }

    X = fired.astype(float).reshape(-1, 1)
    loo_result = evaluate_loo(X, y)
    kfold_result = evaluate_multiseed_kfold(X, y)
    verdict = clearance_verdict(loo_result, kfold_result, n_support)

    return {
        "component": component, "horizon": horizon, "n_support": n_support,
        "verdict": verdict, "loo": loo_result, "kfold": kfold_result,
    }


def evaluate_all(component_flags, forward_returns_by_horizon):
    """
    component_flags: {component_name: fired_flags array}.
    forward_returns_by_horizon: {horizon: forward_returns array}, each the
    same length as every fired_flags array.
    Returns a flat list of verdict records, one per (component, horizon).
    """
    results = []
    for component, fired_flags in component_flags.items():
        for horizon in HORIZONS:
            results.append(evaluate_component(
                fired_flags, forward_returns_by_horizon[horizon], component, horizon,
            ))
    return results
