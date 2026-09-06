# D-TRADE-044 verification — symmetric class-balance floor armed in code (AIQ, 2026-09-06)

Independent verification of `7635bcc` (arms D-TRADE-044 in `helm/validation/engine/{bar,leg_a,leg_b}.py`).
Read the actual diff in full before testing anything. Wrote my own negative-control fixtures
(`helm/validation/audit/stage4_d044_verification.py`) — different numbers from both AI/ML's (140/10, 75/75)
and the Lead's own check, run directly against the real armed functions. This is mechanism verification
(protocol 14's admission test — "show me the input this green would reject"), a different task from a
real-data re-derivation (NN-3), so calling `helm.validation.engine` directly here is deliberate: I'm
testing whether the code correctly implements the ratified rule on controlled inputs, not trusting its
output as my verdict on real backtest data (that re-derivation is `stage3_phase1_cv_audit.py`, already done
independently, and cross-checked against this run's corrected numbers below without re-importing anything).

## 1 — Is this a correct, complete implementation of D-TRADE-044?
**Yes.** `bar.py::clearance_verdict` now takes `n_comparison` as a required positional parameter (not
defaulted) and returns `UNMEASURED` if either `n_support < MIN_SUPPORT` or `n_comparison < MIN_SUPPORT`
(reusing the existing `MIN_SUPPORT=30`, no new number, matching the ratified rule exactly). `leg_a.py`
computes `n_not_fired` and floors on both `n_support`/`n_not_fired` *before* running CV — correct, since
running LOO/kfold on a component that's already known-degenerate wastes cycles computing a meaningless fit.
`leg_a.py` now imports `MIN_SUPPORT` from `bar.py` instead of re-typing `30`, closing a real (if latent)
drift risk between the two floors. `leg_b.py` maps the same check onto its paired arms (see §3).

## 2 — My own independent negative-control check (8/8 pass)
Ran `stage4_d044_verification.py` directly against the real functions, my own fixtures throughout:
- **Exact boundary, 30/30 → runs, not UNMEASURED.** Confirms the rule is `≥30` (inclusive), matching "both
  sides ≥30" as stated, not a stricter `>30`.
- **29/31 → UNMEASURED, CV not run** (`loo is None`) — one side one below the floor is enough to trip it.
- **My own imbalanced-strong-signal fixture (n_fired=205, n_not_fired=15, a strong clean planted effect)
  → correctly UNMEASURED.** This is the actual admission-test case: a signal strong enough to have
  produced a false CLEAR under the old one-sided floor is correctly suppressed once the weak side is seen.
- **The identical signal strength, rebalanced to 110/110 → CLEARED.** Proves the floor isn't a blanket
  suppressor — it specifically targets imbalance, not signal strength.
- **Omitting `n_comparison` → `TypeError`**, not a silent skip — the required-parameter design decision
  holds under a direct call, not just by reading the signature.
- **`leakage_detected=True` → `VOID`, even when the floor would also fail** — confirms VOID's precedence
  is unconditional, not accidentally short-circuited by the new check.
- **Leg B, my own paired fixture at n=28 (<30) → UNMEASURED**, at exactly n=30 → runs. Confirms the Leg-B
  mapping (§3) is wired through correctly, mechanically.

All 8 pass. Combined with reading the diff, this is independently confirmed correct and complete.

## 3 — The Leg-B mapping question (mine to rule on)
**AI/ML's mapping — treat the two paired arms (trailing-return, fixed-N-return) as the "two sides" — is
correct as far as it goes, and properly disclosed rather than assumed silently. But it is effectively
vacuous as new protection, and that should be named plainly, not left implied.**

Leg A's floor targets a specific failure mode: a **group-split** (fired vs. not-fired) where one group is
too small to make the two-sample comparison meaningful. Leg B has no group-split at all — `y_treatment` and
`y_fixed` are two **parallel measurements on the same n trades** (a paired design), so `n_comparison =
len(y_f)` is *always* exactly equal to `n_support = len(y_t)` by construction. **Under this mapping, the
"symmetric" floor for Leg B reduces to nothing more than the single check D-TRADE-029 already
provided** (`n ≥ 30`) — it can never bind on an *imbalance* the way it does for Leg A, because there is no
second, independently-sized group to be imbalanced against. This is not a bug and I'm not asking for it to
be reworked: it's a faithful, honest answer to "what does 'both sides ≥30' mean when a leg has no sides,"
and the commit correctly flags it as an interpretation rather than deciding it quietly. But calling it
"the symmetric floor, mapped onto Leg B" without noting it never actually fires beyond the pre-existing
check would overstate what protection Leg B gained from D-TRADE-044 specifically.

**Is a genuinely different, non-vacuous Leg-B analogue warranted?** I considered the closest real
analogue to Leg A's degeneracy — the paired *difference* itself being at or near zero variance across all
trades (trailing and fixed returns nearly identical for every trade), which would be Leg B's version of
`aligned_trigger`'s constant-feature problem: a comparison that looks like an ordinary DROPPED but is
actually untestable. This is a real, structurally analogous risk — but (a) it's far less likely to occur in
practice than `aligned_trigger`'s case, since two genuinely different exit mechanisms producing near-
identical returns on every single trade is a much stronger coincidence than a binary trigger firing near-
universally on a pre-selected spike cohort, and (b) Leg B's existing unanimous-LOO-agreement check (my own
Stage-2 fix) already substantially covers the *spirit* of "is this comparison actually informative or is it
an artifact" for Leg B's specific paired-difference structure, in a way Leg A's plain LOO/kfold regression
never did for a constant feature. **Ruling: accept AI/ML's mapping as adequate for now — do not build a new
Leg-B-specific degenerate-variance check speculatively.** If a future Leg-B run ever shows a paired
difference at or near exactly zero across the board, that's the concrete trigger for a fresh, explicit
proposal then — not something to invent now against a risk that hasn't materialized.

## 4 — Confirmed: the headline is engine-computed, cross-checked against my own numbers
Read `helm/storage/phase1_cv_results.json` directly: **Leg A = 0 CLEARED / 12 DROPPED / 0 VOID / 15
UNMEASURED** (27 total); **Leg B = 0 CLEARED / 8 DROPPED / 0 VOID / 0 UNMEASURED** (8 total). Cross-checked
against data I had *already independently derived* in `stage3_phase1_cv_audit.py` (the 9 components'
fired/not-fired counts from my original D-TRADE-042 re-derivation) rather than treating the JSON as ground
truth: 5 components fail the floor (flat_top_breakout, abcd_pattern, micro_pullback,
opening_range_breakout, aligned_trigger) = 15 tests → UNMEASURED; the other 4 components' 12 tests were
*already* DROPPED in my original run (none of them held the one-time CLEARED result), so their status is
unchanged by the new floor. `0 + 12 + 15 = 27`. **Exact match**, derived independently, not read off the
artifact and trusted.

## Verdict
**D-TRADE-044 is correctly and completely implemented.** My own negative controls (8/8, different fixtures
from either prior check) confirm the mechanism. The Leg-B mapping is accepted as the right call for now,
with the vacuousness named explicitly rather than left as an unstated limitation. The corrected headline
(0/12/0/15 Leg A, 0/8/0/0 Leg B) is confirmed both by reading the persisted artifact and by independent
recomputation from data I derived before this rule existed.
