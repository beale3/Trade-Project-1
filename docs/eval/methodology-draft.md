# AI-output evaluation methodology — DRAFT PROPOSAL (AIQ)

> **Status: METHODOLOGY ONLY — not an eval set.** Authored under D-TRADE-010 (no build) while product
> `<1.1>` is `▸ NOT DECIDED` and **no AI/ML engine output exists to grade**. This file defines the *shape*
> of the eval — the rubric contract, the blind/write-once protocol, the catch-matching reason-vocabulary,
> and the freeze discipline — so that a golden set can be *instantiated cleanly the day there is a product
> plus an engine*. It fabricates **no** golden items, no thresholds, and no accuracy numbers (LL-43/LL-44).
> Owner: AI Quality (VERIFIER tier, `docs/gate/oracle-boundary.md`). For the **Lead to absorb**; the
> Director ratifies the rubric before any labelling (PROFILE §Oracle-boundary split).
>
> **INSTANTIATION IS BLOCKED ON:** `<1.1>` product paragraph · `<3.4>` engine shape + first sealed outputs
> · reason-vocabulary co-authored with AI/ML · Director rubric ratification · a named blind ground-truth
> expert. Until all five land, this stays a proposal.

---

## 0 · Why this exists now (and what it must not become)
The eval seat's honest number is worth nothing if the method is improvised after the outputs are seen.
Every failure mode the lessons register warns about — grading a stale commit (LL-41), a post-hoc story
told as a prediction (LL-44), a right-answer/wrong-reason coincidence scored as a catch (LL-42), a
fit-to-test figure quoted as accuracy (LL-43), a contaminated grader (LL-47) — is a method defect, not a
data defect. So the method is fixed **before** the first output exists. This draft is that fixing.

What it must **not** become: an eval set. There is no `<1.1>`, so there is no task the engine performs,
so any "golden item" written today would encode my guess at the product, not the product. Building it now
would be exactly the fabrication the charter forbids. Held is a state, not a failure.

## 1 · Scope split (mirrors my oracle-boundary row · VERIFIER)
- **CERTIFIED (mechanical, fail-closed):** golden-eval pass/fail on a **frozen** set at a **pinned commit**;
  the anti-fabrication grounding leg (every output cites a real source-of-record that resolves); a
  catch-matching grade against a shared reason-vocabulary. These emit a per-run certificate naming the
  commit hash, the set id, and the seal digest.
- **HUMAN + escalates (no oracle — Director holds root of trust):** *is the eval set representative* of the
  product's real distribution; what a given accuracy number *means* for the ship decision; rubric design
  itself. Model-name identifications go **direct to the Director** (the repo bars model IDs).
- **Admission test I must pass for any leg I claim as certified (LL-49):** a seat other than me can produce
  a reproducible **negative control** — "show me the input this green would reject." Any leg without a live
  negative control is demoted to HUMAN. GA audits this (independence + coverage + boundary-honesty).

## 2 · The freeze-before-measure protocol (LL-41)
1. AI/ML declares an engine build at a single **commit hash**. Nothing grades an un-pinned engine.
2. Engine outputs for the eval inputs are generated and **sealed** (content-addressed digest) **before any
   label exists**. The seal is committed; the digest is the artifact that travels with every later claim.
3. Every validation record names the hash **and** the seal digest. A record without both is void — it may
   silently be grading a stale commit.
4. Re-running later requires a *new* hash + *new* seal; a grade never carries across an engine change
   unlabelled.

## 3 · Ground-truth rubric contract (LL-40 · PROFILE mandate)
- **Rubric agreed FIRST, in writing, before a single label is drawn.** The rubric is the criterion the
  label is *against*; writing it after seeing outputs lets the outputs write the rubric.
- **Accuracy and consistency are separate claims, stated separately, always (LL-40).** Two distinct
  columns, two distinct certificates. Never a blended "quality" score.
  - *Accuracy* = engine output vs **external blind ground truth**, on lanes the engine has **never seen**.
  - *Consistency* = engine vs itself / vs format+grounding invariants (repeatability, schema-validity,
    citation-resolves). Consistency green is **not** accuracy evidence.
- **Ground truth is a domain expert (often the Director), BLIND and WRITE-ONCE (LL-40).** The expert labels
  without seeing the engine's answer or the fresh/held split; labels are committed write-once; a relabel is
  a new, dated record, never an overwrite.
- **Independent second classifier on a DIFFERENT model (PROFILE).** Two independent label passes; the
  builder's own model never sits on both sides. Inter-rater disagreement is surfaced, not averaged away.

## 4 · Pre-registration — write-once, before the run (LL-44)
- Predictions (expected pass/fail, expected catch tier per item, thresholds) are **pre-registered and
  committed BEFORE the run**. A confirmed pre-registration is a prediction; a post-hoc match is a story.
- The pre-registration file is write-once. The run reads it; the run never edits it.
- GA confirms the pre-registration commit precedes the run commit in history.

## 5 · Catch-matching, not tier-matching (LL-42)
- A grade is **catch-matched**: right answer **for the right reason**, against a **shared reason-vocabulary
  co-authored with AI/ML BEFORE the run**. Right answer + wrong reason = coincidental agreement and does
  **not** score as a catch. A tier-only grade will pass fixes that are wrong.
- A validation that finds a fix "fires" must also check it fires **for the right reason** (PROFILE lessons):
  fired-as-designed includes catch-correctness, not just the output tier.
- **Reason-vocabulary — placeholder skeleton (to be co-authored with AI/ML once `<3.4>` engine + `<1.1>`
  exist; these are structural buckets, NOT product claims):**
  | code | reason class (why an output is right/wrong) |
  |---|---|
  | `R-GROUND` | grounded in / contradicted by the cited source-of-record |
  | `R-FABRICATE` | asserts a fact with no resolvable source (anti-fabrication core) |
  | `R-STALE` | cites a real but out-of-window / superseded source |
  | `R-MISREAD` | source is real & current but the output misreads it |
  | `R-SCOPE` | answer is out of the task's declared scope |
  | `R-FORMAT` | schema/format invariant violated |
  > Codes are the *frame*; their product-specific content is filled with the builder at instantiation. The
  > grade records the code, so a right-tier/wrong-code case is visible as the coincidence it is.

## 6 · Fresh draw vs same-set re-seal (LL-43)
- **The honest accuracy number is a FRESH DRAW the fix never saw.** It is the only figure quoted as accuracy.
- **The same-set re-seal is a CONFIRMATION, never the number.** It proves the fix fired and nothing
  regressed; it is fit-to-test by construction. It is **labelled `fit-to-test (confirmation only)`** and
  **never travels unlabelled**, never quoted as accuracy.
- Every reported figure carries its provenance tag: `fresh-draw` | `fit-to-test` | `consistency-only`.

## 7 · Void-on-contamination (LL-47)
- Before trusting any grade, **audit blindness**: did the grader/expert see what it had to be blind to
  (the engine's answer, the fresh/held split, the pre-registration)? 
- On any contamination: **VOID the run without sentiment and re-draw fresh.** A grader that has seen what it
  must be blind to yields a grade worse than none. GA is notified; the void is logged.

## 8 · Builder ≠ judge (structural — protocol 14 / PROFILE)
- AI/ML authors the engine's rule-set; **AIQ builds the oracle and JUDGES**; GA audits AIQ's independence;
  QA re-runs the frozen set on phase exit. No self-validation is ever accepted as validation, and the same
  session's two modes never stand in for independence (an optimistic ceiling).

## 9 · Anti-fabrication grounding leg (certified)
- Mechanical assertion: **every engine output that states a fact resolves to a real source-of-record**
  (e.g. an EDGAR filing / market-data record per `<2.1>`, once providers land). An unresolvable or absent
  citation **FAILS** the leg. Negative control: plant an output citing a non-existent accession → leg fails.

## 10 · Open items / dependencies before instantiation
| # | needs | from | blocks |
|---|---|---|---|
| 1 | product paragraph `<1.1>` | Director | the whole eval task exists off this |
| 2 | engine shape `<3.4>` + first sealed outputs at a pinned hash | AI/ML | freeze protocol (§2), grounding leg (§9) |
| 3 | reason-vocabulary co-authored | AIQ + AI/ML | catch-matching (§5) |
| 4 | rubric ratified before labelling | Director | ground-truth contract (§3) |
| 5 | named blind ground-truth expert (often Director), write-once | Director | accuracy grade (§3, §6) |
| 6 | providers `<2.1>` (EDGAR anchor + rest) | Director/SecOps | source-of-record for grounding (§9) |

**Until items 1–2 land, AIQ HOLDS. This draft is the pre-registered method, not a measurement.**
