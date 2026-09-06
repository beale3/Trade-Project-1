# ADR-0003 review — §3 ruling + §4 validation bar (AIQ load-bearing co-sign, 2026-09-06)

Read the full ADR (not a summary) before responding — same standard as the ADR-0001 R2 review. Verified
the factual grounding myself where it touches my mandate (the `<3.2>` reuse-vs-validation claim and the
bar-design logic), not just accepted the Lead's citation-check.

## §3 — "reused code does NOT inherit validation" — CO-SIGN, no objections
The ruling correctly distinguishes two different claims that are easy to conflate: **reusable engineering**
(the label definition in `labeling.py`, the expanding-window walk-forward structure in `train_model.py` —
genuinely well-built, no-lookahead, per the ADR's own citations) vs. **an inherited validation claim**
(whether the model actually predicts OOS) — and correctly rules that passing unit/synthetic tests is
evidence of the former only, never the latter, "regardless of how much code is reused." This is the same
distinction my own Stage-2 audit relied on (a fixed, already-inspected utility is safe to reuse; a
validation *claim* is never inherited). §7's admission mechanism (Director scope-assignment + protocol-17
AIQ validation + a checkable artifact, no prose finding admissible) is concrete enough for a scoping-level
ADR that correctly defers implementation numbers elsewhere. No gaps found.

## §4 — the modified validation bar — CO-SIGN THE SHAPE, 2 precision items for E-2, 1 cross-reference

**The core design decision is sound and well-reasoned, not just adequate.** Correctly identifies that
random k-fold shuffling leaks time-order for a walk-forward classifier (a real, non-obvious risk many
naive ports of a CV discipline miss) and decomposes the original single ≥90%-of-≥30-seeds check into two
*orthogonal* robustness checks appropriate for the new model class: **fold-consistency** (robustness to
*which OOS time-window* is tested — the walk-forward analogue of "which rows land in which fold") and
**model-seed sensitivity** (robustness to *training randomness* — a source of instability the original
regression-based bar never had to address, since `LinearRegression` has no seed). This isn't a weakening of
the original discipline; it's a more precise decomposition for a harder problem. Endorsed.

**Item 1 — the primary-metric baseline needs to resolve to ONE baseline, not stay "no-trade /
base-rate-entry."** As written, it's genuinely ambiguous whether "no-trade" (strategy EV=0, holding cash —
the real-world decision-relevant comparator: deploy this model or don't) and "base-rate-entry" (trading
indiscriminately at the population base rate — closer to the studies' train-mean-naive analogue) are the
same baseline described two ways, two baselines the model must beat *both* of, or two candidates where the
ADR hasn't picked. These give materially different bars. **Recommend: "no-trade" (EV=0) as the single
primary clearance baseline** (it's the one that answers the actual decision question — matches how Leg B's
comparison is meant to inform "should this be deployed," not an academic beats-random-guessing test) **with
base-rate-entry retained as a named secondary/diagnostic**, mirroring how the ADR already separates primary
EV from secondary precision-at-recall. This needs resolving before E-2 pre-registration, not left implicit
into the numbers-setting step — the *baseline choice itself* is bar shape, not a number.

**Item 2 — make the fold-consistency AND model-seed-sensitivity relationship explicit (both required, not
either).** D-TRADE-021's precedent is an explicit AND (LOO **and** 5-fold, both required) — the ADR's
phrasing lists the two classifier-analogue checks as "(i)... (ii)..." without stating the same AND
explicitly. I read the intent as AND, consistent with precedent and with not weakening the discipline, but
a CRITICAL-tier bar should say so in words at E-2, not rely on a reader's inference.

**Item 3 — cross-reference to today's D-TRADE-042 finding, not a new objection but a needed update.** E-1
frames the Leg-B hard dependency as: Phase 2 needs Leg B "CLEARED, or at minimum fully characterized," and
escalates only "if Leg B returns NOT-CLEARED/UNMEASURED." **My independent re-derivation of D-TRADE-042
today found Leg B's actual DROPPED verdict rests on a materially confounded construction** (same-day
trailing-stop exposure compared against a 5-trading-day fixed hold — not a duration-matched comparison;
full detail: `docs/eval/d-trade-042-cv-reaudit.md` §3). This is exactly the "fully characterized" case E-1
already anticipates in spirit, but the escalation clause as literally worded ("if NOT-CLEARED/UNMEASURED")
doesn't clearly cover "DROPPED-but-confounded" — and Phase 2's own exit-mechanism assumption (§1, §4: flagged
trades "exited via Phase-1's validated trailing-stop rule") is exactly the assumption this confound puts in
question. **Recommend E-1's escalation trigger explicitly include "Leg B DROPPED under a disclosed
methodology confound," not only a clean NOT-CLEARED/UNMEASURED** — otherwise a technically-DROPPED-but-
uninterpretable Leg B could read as satisfying "fully characterized" when the honest state is "we don't yet
know if trailing stops work, only that this particular confounded test didn't favor them."

## Verdict
**Co-signing §3 and §4's overall shape and approach — this is sound, load-bearing methodology, not a
redesign candidate.** Three items to close before/at E-2 (baseline choice, explicit AND, and E-1's
escalation wording reflecting today's Leg-B finding) — all additive clarifications, consistent with the
ADR's own stated self-scoping (shape now, numbers at E-2). Not blocking ratification of the ADR as a
scoping document; these need to land before E-2's numbers are actually pre-registered.
