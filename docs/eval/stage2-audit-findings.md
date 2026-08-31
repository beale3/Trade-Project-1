# Stage 2 audit — AI/ML's Phase-1 Stage 1 delivery (AIQ, 2026-08-31)

Independent audit per the Director's 2026-08-30 build-chain dispatch (AI/ML→AIQ→QA→DevOps), same
standard as the ADR-0001 R2 co-sign: re-derive from raw `tools/rolling_watchlist.py` primitives, never
import `helm/screener`'s or `helm/validation/engine`'s outputs (NN-3). Runnable script:
`helm/validation/audit/stage2_audit.py` (6/6 of my own independent tests pass — 4 confirm no defect, 2
produce the substantive findings below).

**Scope note:** Stage 1 delivered LOGIC, not a real-data run — no historical OHLCV was pulled (no
`helm/ingest/` exists yet), so there is no actual CLEARED/DROPPED verdict on a real component to
reproduce yet. This audit verifies the delivered MECHANISM is sound, ahead of a real run.

## What I independently re-derived and confirmed sound (no defect)

1. **Trailing-stop ratchet formula** (`tools/rolling_watchlist.py::simulate_day_trades`, trail mode) —
   hand-computed a 5-bar fixture independently (not reusing AI/ML's or the Lead's test values), confirmed
   the exit price matches `effective_stop(t) = max(P0*(1-init_stop_pct/100), peak(t)*(1-trail_pct/100))`
   exactly (101.2, computed by hand before running).
2. **Init-floor bound** — a never-rising trade exits at exactly the init hard stop (97.0 on a 100.0 entry,
   3% floor), never below it.
3. **No-lookahead (NN-1)** — ran the same fixture truncated after the exit bar vs. full-length; the exit
   bar's trade record is byte-identical either way. If `peak(t)` or the exit check ever read a future bar,
   truncating would have changed the outcome. It didn't.
4. **Backward compatibility** — `trail_pct=None` (default) reproduces the original fixed stop/target math
   exactly on an independent fixture.
5. **The CV-harness algorithm is soundly implementable** — I wrote my own LOO + 5-fold×30-seed
   reimplementation from scratch (not importing `helm/validation/engine/harness.py`) and confirmed it
   correctly clears a planted linear signal (100% seed agreement) and correctly rejects pure noise (0%
   seed agreement), matching the D-TRADE-021 bar's intent. This validates the ALGORITHM AI/ML describes;
   it is not a claim that their literal code reproduces (that's QA's Stage-3 mandate).
6. **The 9-component Leg-A list is grounded in the real scanner**, not invented — calling
   `scan_all_patterns()`/`analyze_intraday_alignment()` directly (the raw primitives, not
   `helm/screener/adapter.py`) confirms all 8 named pattern columns + `aligned_trigger` actually exist in
   the scanner's real output.

## Findings (4, all fixable — none invalidate the core mechanism above)

### Finding 1 — Leg-B's LOO-paired outlier check is empirically weak (confirmed with real numbers)
`leg_b.py::_loo_paired` reports the **mean of n leave-one-out estimates** as its outlier-robustness
statistic. I constructed a fixture designed to test this: 35 trades, 34 with a small consistent
*disadvantage* for trailing (-0.001 each), 1 outlier trade with a large *advantage* (+0.10) that alone
flips the full-sample mean positive (+0.0019). A genuine robustness check should flag this as
outlier-driven. It doesn't: the ONE leave-one-out estimate that actually excludes the outlier is correctly
negative (-0.001, revealing the other 34 trades' true direction) — but `_loo_paired`'s reported statistic
(the MEAN of all 35 leave-one-out estimates) stays positive (+0.0019), because each individual
leave-one-out estimate only removes 1/35th of one trade's influence, so averaging them together nearly
always preserves the full-sample sign unless the outlier is extreme relative to the sum of everything
else. **This statistic is close to redundant with just checking the full-sample sign — not a meaningful
outlier check as implemented.**
**Recommendation:** report the count/fraction of individual leave-one-out estimates whose sign disagrees
with the full-sample estimate (a real outlier-fragility signal), in addition to or instead of their mean.

### Finding 2 — Leg-B's verdict doesn't disclose that it tests stability, not generalization (LL-40)
AI/ML's own docstring is upfront that Leg B has no fitted model (parameters are pre-registered constants
per D-TRADE-036) — so "beats naive OOS" can't mean "fit on train, predict on test" the way Leg A's
regression does. Their adaptation (paired mean-difference checked across leave-one-out and 150 random
5-way resamples of the SAME finite trade sample) is a legitimate **in-sample stability/robustness check**:
does the observed advantage survive being viewed through different partitions of data already fully
known. It is **not** a test of generalization to new, unseen trades — there is nothing held out that
wasn't already used. That's a real, disclosed, defensible design choice given there's nothing to fit.
**The problem is presentation, not method:** Leg B's verdict record uses the identical field names
(`beats_naive_baseline`, `pct_seeds_beating_naive`) and the identical `CLEARED` label as Leg A's genuinely
predictive test, with nothing in the OUTPUT distinguishing the two claims. A downstream reader (Director,
QA, a future me) could reasonably read a Leg-B CLEARED as carrying the same evidentiary weight as a Leg-A
CLEARED, when it certifies something categorically different — exactly the accuracy-vs-consistency
conflation my own methodology (LL-40) exists to prevent.
**Recommendation:** the verdict record or its wrapping report should explicitly label Leg-B verdicts as
"stability-checked" (survives resampling of known data) vs. Leg A's "held-out-tested" (predicts unseen
data) — not a new field necessarily, but the distinction must travel with the number, not live only in a
docstring.

### Finding 3 — verdict-string schema deviation from the ratified 4-state schema
`bar.py::clearance_verdict()` returns the literal string `"NOT_CLEARED"`. The ratified canonical schema
(ADR-0001 §6.1, D-TRADE-030) is `verdict∈{cleared,dropped,void,unmeasured}` — **"DROPPED"** is the correct
tested-and-failed state. Confirmed by direct text search against the current ADR, not from memory.
**Recommendation:** rename the returned string to match the ratified enum (or the ADR's schema is
formally revised — either way, they need to agree; right now they don't).

### Finding 4 — `leg_b.py` introduces an undocumented 5th verdict state
When a sensitivity-only grid cell would otherwise clear, `leg_b.py` downgrades it to a new string,
`"SENSITIVITY_ONLY_WOULD_CLEAR"` — outside the ratified 4-state schema entirely. **The underlying intent is
correct** (OP-1's anti-cherry-pick rule: a sensitivity cell must never silently read as a clearance claim)
— but inventing an undocumented 5th state is a real schema deviation, not just a naming nit: any
downstream consumer (a gate leg, QA's reproducibility check, a future report generator) built against the
ratified 4-state enum will not recognize it.
**Recommendation:** either formally propose this as a ratified schema extension, or achieve the same
guarantee within the existing 4 states — e.g. keep the verdict as `DROPPED` (once Finding 3 is fixed) or
`CLEARED` and carry `is_primary`/`clearance_eligible` as a separate boolean field on the same record,
rather than encoding eligibility into the verdict string itself.

## Verdict on AI/ML's explicit question (Leg B's paired-comparison translation)
**The translation is methodologically sound in its core logic**, given the real constraint that D-TRADE-036
fixed the exit parameters as pre-registered constants (no fitting, so no "held-out prediction" is possible
even in principle) — reusing the harness's SHAPE while substituting a stability check for a predictive
holdout is the right kind of adaptation for that constraint, not a fabricated shortcut. **The defect is not
the method's existence, but two gaps in its execution:** the outlier-robustness statistic as implemented
is too weak to do its job (Finding 1), and the verdict schema doesn't disclose the stability-vs-
generalization distinction downstream (Finding 2). Both are fixable without redesigning Leg B.

## Not yet auditable
No real historical data has been pulled (`helm/ingest/` doesn't exist), so there is no actual verdict
record to independently re-derive against real trades yet — that audit (the one my methodology-draft.md's
full §1–4 sequence targets) happens once SDE1/Data-Eng deliver real data and AI/ML runs the engine against
it. This review covers the mechanism only.
