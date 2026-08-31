"""
The D-TRADE-021 clearance bar + D-TRADE-029's minimum-support floor
(ADR-0001 NN-2/NN-4, §14 UNMEASURED verdict). A subject (an entry-signal
component at a horizon, or an exit-rule config) gets exactly one of the
ratified 4-state schema (ADR-0001 §6.1, D-TRADE-030):
CLEARED, DROPPED, VOID, or UNMEASURED. No partial credit -- matches the
4-study precedent (short-interest kept; regime/catalyst/float dropped).

Stage-2 audit fix (AIQ, 2026-08-31, finding #3): this previously returned
the literal string "NOT_CLEARED", which is not in the ratified enum --
renamed to "DROPPED" to match §6.1 exactly. Confirmed by AIQ's direct text
search against the current ADR, not from memory.
"""

MIN_SUPPORT = 30  # D-TRADE-029, anchored to D-TRADE-021's own n>=30 seed basis
SEED_AGREEMENT_THRESHOLD = 90.0  # D-TRADE-021


def clearance_verdict(loo_result, kfold_result, n_support, leakage_detected=False):
    """
    n_support: the number of independent trigger events/observations
    backing this test -- D-TRADE-029's floor applies to THIS count, not
    the CV fold count (a component that almost never fires can't produce
    a meaningful verdict no matter how large the surrounding cohort is).
    leakage_detected: caller sets True if an NN-1 point-in-time check
    failed for this subject -- VOID overrides every other outcome.
    """
    if leakage_detected:
        return "VOID"
    if n_support < MIN_SUPPORT:
        return "UNMEASURED"

    cleared = loo_result["beats_naive_baseline"] and kfold_result["pct_seeds_beating_naive"] >= SEED_AGREEMENT_THRESHOLD
    return "CLEARED" if cleared else "DROPPED"
