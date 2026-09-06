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

D-TRADE-044 (2026-09-06, Director-ratified): the floor is now SYMMETRIC --
both sides of a comparison must carry >= MIN_SUPPORT, not just the firing
side. Surfaced by the D-TRADE-042 run (aligned_trigger fired 148/148, a
mathematically constant feature whose LOO RMSE tied the naive baseline to
the bit), proposed by AIQ, ratified by the Director. Applied retroactively,
it removes that run's only clearance -- accepted deliberately, since the
rule is principled, uniform, and moves against the result.
"""

MIN_SUPPORT = 30  # D-TRADE-029, anchored to D-TRADE-021's own n>=30 seed basis
SEED_AGREEMENT_THRESHOLD = 90.0  # D-TRADE-021


def clearance_verdict(loo_result, kfold_result, n_support, n_comparison, leakage_detected=False):
    """
    D-TRADE-044 (symmetric class-balance floor, ratified 2026-09-06): a
    comparison is only a MEASUREMENT if BOTH of its sides carry at least
    MIN_SUPPORT observations. Reuses D-TRADE-029's existing 30-count on
    both sides rather than introducing a second number.

    n_support / n_comparison -- the observation counts on the two sides:
      - Leg A: n_fired / n_not_fired. A component firing on every
        observation has a mathematically constant feature: its fitted line
        is flat, its predictions equal the naive mean exactly, and it
        cannot beat naive in either direction whether or not a real
        relationship exists. That is untestable, not tested-and-failed.
      - Leg B: the two arms of the paired comparison. Equal by
        construction (same trades, two exit rules), so this passes
        whenever the paired sample itself clears the floor.

    Both parameters are REQUIRED, deliberately -- an optional
    n_comparison defaulting to "skip the check" would let a caller
    silently bypass a ratified floor, which is exactly the vacuous-green
    hole the charter's builder-not-judge discipline exists to prevent.

    UNMEASURED is NOT a negative verdict (D-TRADE-044, recorded to prevent
    drift): it means the comparison could not be run for want of
    observations on one side. No downstream consumer may treat it as
    equivalent to DROPPED.

    leakage_detected: caller sets True if an NN-1 point-in-time check
    failed for this subject -- VOID overrides every other outcome.
    """
    if leakage_detected:
        return "VOID"
    if n_support < MIN_SUPPORT or n_comparison < MIN_SUPPORT:
        return "UNMEASURED"

    cleared = loo_result["beats_naive_baseline"] and kfold_result["pct_seeds_beating_naive"] >= SEED_AGREEMENT_THRESHOLD
    return "CLEARED" if cleared else "DROPPED"
