# D-TRADE-042 independent re-derivation (AIQ, 2026-09-06)

Full independent re-derivation of the real Phase-1 Leg A/Leg B CV run (`26c6faf`,
`helm/validation/run_phase1_cv.py`, reported in `docs/eval/phase1-cv-results.md`). Script:
`helm/validation/audit/stage3_phase1_cv_audit.py` — reimplements the entire pipeline from scratch (my own
harness, my own bar logic, my own feature/label construction) calling `tools.rolling_watchlist`'s raw
primitives (`scan_all_patterns`, `analyze_intraday_alignment`, `simulate_day_trades`) directly. Does not
import `helm.screener.adapter` or `helm.validation.engine` (bar/harness/leg_a/leg_b) anywhere — NN-3.

## 1 — Numbers: exact match, every figure

Ran the full 27 Leg-A tests + 8 Leg-B configs independently. **Every reported number reproduces exactly:**

- **Leg A fired-counts**, all 9 components: 40, 131, 129, 126, 109, 137, 108, 97, 148 — exact match to
  `phase1-cv-results.md`'s table.
- **The one CLEARED result** (`opening_range_breakout`@1w): my own LOO gives `rmse_model=40.98360,
  rmse_naive=41.17195` (0.46% improvement, computed independently: `(41.17195-40.98360)/41.17195*100 =
  0.46`) and 5-fold seed agreement **93.3%** — both exact matches.
- **`aligned_trigger` degeneracy**: independently confirmed **bit-for-bit exact equality**
  (`rmse_model == rmse_naive` to 10 decimal places) on all three horizons. This is not a rounding
  coincidence — mechanically, a constant regressor (aligned_trigger fires on literally every observation,
  so every LOO training fold still sees a constant column) makes OLS degenerate to an intercept-only fit
  equal to the training-fold mean, which is definitionally the naive baseline. "Beats naive" is
  mathematically impossible here regardless of any real underlying relationship — independently confirmed,
  not just reported.
- **Leg B primary**: n=149, full-sample mean diff **−22.4426** (reported −22.44), LOO **100.0%** of
  leave-one-out estimates agree (reported "100%"), 5-fold seed agreement **2.0%** (exact match), verdict
  DROPPED.
- **All 7 Leg-B sensitivity configs**: DROPPED, with n=149/149/149/149/149/150/148 — exact match to the
  reported table, including the N=1 (150) and N=21 (148) row-count differences from the primary's 149.

**Verdict on the numbers: `reproduced_by_aiq=TRUE` is warranted for `opening_range_breakout`@1w** (the one
CLEARED verdict) per D-TRADE-021/`<3.4>`'s requirement — my fully independent re-derivation, built from raw
primitives with zero code shared with `run_phase1_cv.py`, matches to the same precision on every reported
figure. NN-3 (builder≠judge) is satisfied: this was never computed by importing AI/ML's code or trusting
their JSON, only by independently rebuilding the same pipeline from source primitives and comparing outputs.

## 2 — Judgment: the `aligned_trigger` / class-balance finding

**Confirmed, and it changes how the batch should be read.** The 30-event floor (D-TRADE-029) counts firing
events, not comparison-group balance — a component that fires on literally every observation (0 in the
"not fired" class) sails through the floor at n=148 while being mathematically incapable of producing a
"beats naive" result in either direction, for either a real or a null underlying relationship. This is not
a milder version of ordinary sampling noise; it is a structurally untestable case the floor was never
designed to catch (it was anchored to guard against *thin samples*, not *zero-variance features*).

**This is not confined to `aligned_trigger` — it is a spectrum across the whole batch**, and the one
CLEARED result sits on the thin end of it: `opening_range_breakout`@1w fired on 137/148 (only **11**
non-firing observations backing the comparison), the second-most-imbalanced test in the batch after
`aligned_trigger` itself. `phase1-cv-results.md` already discloses this honestly (caveat 2 on the CLEARED
result) — I'm confirming that reading is accurate and it needs to become a mechanical check, not just prose.

**Recommendation (mine to propose, per precedent — same route as D-TRADE-021/029, not self-applied):** a
symmetric minimum-class-count floor — `UNMEASURED` unless **both** `n_fired ≥ 30` **and**
`n_not_fired ≥ 30`, reusing D-TRADE-029's existing 30-count rather than inventing a new number (same
justification: anchored to the same statistical-power basis already established). This is a natural,
narrow extension of an already-ratified rule, not a new methodology.

**Stated plainly, since this is significant: applying this proposed floor to the current results would
flip BOTH `aligned_trigger` (0 not-fired) and `opening_range_breakout`@1w (11 not-fired) to UNMEASURED.**
The batch headline would become **0 CLEARED / 25 DROPPED / 2 UNMEASURED** of 27, not 1/26/0. This is the
conservative direction (removing a marginal clearance, not manufacturing one), consistent with the
project's established preference for stringency (D-TRADE-021's ≥90%-not-≥50% precedent) — but it is a
real change to the headline result and needs Director/Lead ratification before it's applied to this run's
verdicts, exactly like D-TRADE-021/029 were ratified before binding. I am not applying it unilaterally;
flagging it with the concrete number so the decision-makers see the actual consequence, not an abstract gap.

**Whose job to spec:** mine, per the existing division of labor (AIQ authors bar/methodology rules,
ratified by Lead/Director; the Architect owns structural/module-layout/label-form questions). This is a
bar-rule addition, not a design-contract change — same category as the D-TRADE-021 bar and the D-TRADE-029
floor, both of which I originated.

## 3 — Judgment: the Leg-B fixed-N-vs-same-day construction

**Defensible as a disclosed, constraint-driven first pass — but the DROPPED verdict should not be read as
clean evidence against trailing stops as an exit-rule concept.** The construction satisfies the one
structural requirement ADR-0001 stated ("same entries" — both arms share the identical intraday entry
price) and was honestly disclosed at build time and again in the results, not buried. But it introduces a
real confound: the trailing arm is forced same-day (the simulator's genuine structural limit), while the
fixed arm gets a full 5-trading-day window. A 5-day hold captures materially more of any post-spike
continuation or reversion than a same-day exit structurally can, **independent of whether the trailing
rule itself is a good exit mechanism.** Part of −22.44pts is very likely this duration mismatch, exactly as
`run_phase1_cv.py`'s own docstring already states — I'm independently endorsing that self-assessment as
accurate, not merely accepting it.

**Practical consequence:** the DROPPED verdict, as computed, answers "does same-day trailing exposure beat
a 5-day hold" — not "does the trailing-stop exit rule beat a duration-matched alternative," which is the
question ADR-0001 §6.2 actually poses. These are different claims. The verdict should be reported with that
distinction attached (an LL-40-style separate-claims discipline: this is a *confounded* comparison, not
disqualifying, but not a clean answer to the original question either).

**On re-running under a different construction — agree with the Lead's framing: this needs sign-off
BEFORE any change, not after.** We have now seen an unfavorable (DROPPED) result under the current
construction. Changing the construction *now*, even for a well-motivated reason (fixing a real confound),
without going back through Director/AIQ ratification first, is structurally the same failure mode the
"no tuning/re-gridding to manufacture a clearance" rule exists to prevent — the fact that the motivation is
legitimate doesn't change the process risk (even unconscious). **Recommendation:**
1. The current DROPPED verdict **stands** as the mechanical result under the as-built, as-ratified
   construction — I am not voiding it (no leakage/contamination found, only a disclosed limitation).
2. Report it with the confound caveat attached explicitly (already partially done; make it a first-class
   qualifier, not a footnote) — do not present it as clean evidence trailing stops underperform.
3. **A duration-matched re-test is a new construction proposal**, requiring fresh Director (+AI/ML+AIQ)
   sign-off before any code runs — not something to go build now off this finding. I'll note, without
   pre-committing to either (that's a real design choice for the team, not mine to pick unilaterally): a
   same-day/N=0 fixed baseline would be duration-matched using only the existing single-day simulator
   (no new code), while extending `simulate_day_trades` to genuine multi-day capability would preserve
   D-TRADE-036's already-ratified N=5-trading-day baseline exactly as chosen. Both are viable; picking
   between them is the kind of judgment call that belongs in a fresh proposal, not this audit.

## Summary
- **D-TRADE-042 numbers: independently re-derived, exact match. `reproduced_by_aiq=TRUE` for
  `opening_range_breakout`@1w.**
- **`aligned_trigger` finding: confirmed real and exact. Recommend a symmetric 30/30 class-balance floor**
  (mine to propose, Director/Lead to ratify) — flagging plainly that applying it now would flip the
  batch to 0 CLEARED / 25 DROPPED / 2 UNMEASURED.
- **Leg-B construction: defensible-as-disclosed, but confounded — DROPPED verdict stands as computed, with
  the confound caveat attached; any re-construction needs fresh sign-off before running, not after seeing
  this result.**
