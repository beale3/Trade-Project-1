# ADR-0003 — HELM Phase 2: scope, the predictive-model validation bar, and entry conditions

- **Status:** PROPOSED (scoping ADR — resolves canonical `<1.4>`'s `▸ NOT DECIDED` boundary marker).
  Awaiting oversight co-sign + Director ratification. **Authoring a scope is not authorization to execute
  it** (D-TRADE-043) — this ADR authorizes **no** build/train/data-pull.
- **adr_reference id:** `ADR-0003`. **Author:** Principal Architect. **Date:** 2026-09-06.
- **Governs / resolves:** canonical `<1.4>`; D-TRADE-043 (the six required outputs); D-TRADE-033
  (`breakout_model` disposition); D-TRADE-032 (external-component rule); relates to D-TRADE-021/029/036
  (Phase-1 bar), D-TRADE-039 (raw prices), NN-1/NN-8, D-TRADE-042 (Phase-1 Leg B, the exit dependency).
- **Standing rule invoked (D-TRADE-043):** scoping/design is not gated by an open D-TRADE-010-class build
  freeze — only build/train/data-pull is. This ADR is authored under that rule, in parallel with D-TRADE-042.
- **Two-doc note (protocol 13):** design content in my write-lane (`docs/adr/**`); the canonical `<1.4>`
  resolution is a recommendation for the **Lead to absorb** on ratification. Reference by `<x.y>`/decision id.

> **Scope discipline.** This is a SCOPING ADR: it draws the Phase-2 boundary, rules the disposition of
> existing work, and sets the validation *shape* and entry *conditions*. It does **not** specify the model's
> implementation or lock the validation *numbers* — those are a pre-registration step at Phase-2 entry
> (§6 E-2), the D-TRADE-036 path.

---

## 1 · Context
Canonical `<1.4>` has carried a `▸ NOT DECIDED` Phase-2 boundary since the D-TRADE-028 equity pivot. Phase 1
(ADR-0001 R2) **validates what already exists** — the scanner's detectors (Leg A) and a new trailing-stop
exit (Leg B), against the D-TRADE-021 bar; its closing CV run is live now (D-TRADE-042). Phase 2's candidate
is the **from-scratch predictive breakout-occurrence model** (`breakout_model` / "Predictive Model 7.0"),
logged and HELD in the separate `Trade/` repo (D-TRADE-033). I read that code in full to ground this ADR
(read-only; `Trade/` is a separate ungoverned repo — no writes, no commits there).

**The one-line boundary that organizes everything below:** *Phase 1 = validate what we already have; Phase 2
= build something new to predict what the existing detectors can't — the breakout before it happens.* A
Phase-2 model's job is to generate **entry** signals; those signals, if the model clears, are **exited
through Phase-1's validated trailing-stop rule** — which is why Leg B is Phase 2's one hard dependency (§6).

## 2 · Output 1 — the Phase 2 boundary
**IN scope (Phase 2):**
- A supervised **predictive breakout-occurrence model**: predict, from day-`t` information only, whether a
  name breaks out on `t+1` (the `breakout(t)` label — next-day intraday gain ≥ threshold AND next-day
  rel-vol ≥ threshold AND today's price in-band; `Trade/labeling.py`/`config.py`).
- Over a **broad small-cap daily panel** (the classifier needs both breakout and non-breakout days), a
  new data surface vs. Phase-1's event-defined cohort (§5).
- Composed with Phase-1's validated trailing-stop **exit** for realistic P&L (§4).
- Walk-forward validated to a classifier-appropriate bar (§4), builder≠judge, NN-1, raw prices (D-TRADE-039).

**OUT of scope (not Phase 2):**
- Anything Phase 1 owns — detector/exit validation (D-TRADE-042); the D-TRADE-023 dashboard.
- Any options logic (deleted, D-TRADE-028); live trading/order execution/broker integration; any
  multi-tenant/SaaS surface (`<1.2>`/`<3.3>`).
- Automatic adoption of any externally-built component (§7) — admissible only by formal scope-assignment.
- **Execution of Phase 2 itself** — this ADR scopes; build is a separate Director decision (§6 E-4).

## 3 · Output 2 — disposition of the existing `breakout_model` work
**Ruling: REWORK — carry forward as a reference/candidate starting point, NOT as-is, NOT discard.** The code
is genuinely well-built (careful no-lookahead: `labeling.py` keeps the label strictly separate and
next-day-only; `features.py` uses only `≤t` data with `shift(1)` crossings; `train_model.py` is a proper
expanding-window walk-forward with an honest "EV is a simplified sanity check, not a real backtest" caveat).
That engineering is worth reusing. But it is **not adoptable as-is**, on four independent grounds:
1. **Data layer is ungoverned.** It reads Polygon (`api.polygon.io`) grouped-daily-bars **directly**, outside
   `helm/ingest` (leg-T boundary), and its adjusted/raw status is unverified — a live D-TRADE-039 concern.
   The data layer must be **rebuilt on `helm/ingest/massive.py`** (`adjusted=false`, point-in-time, spend-guarded).
2. **Externally-sourced features.** `consolidation_low_slope`, `parabolic_curvature`, `vwap_distance`,
   `vwap_cross_up` are "routed from the Blind Test Study side, sourced from Copilot's architecture review"
   (`config.py`) — external provenance, not validated (§7 / D-TRADE-032). Their presence in the code is not
   adoption.
3. **Catalyst features untested.** `catalyst_features.py` was "NOT tested against a live sec-api.io account"
   (`config.py`) — must be re-tested against the now-confirmed key (D-TRADE-026) before use.
4. **Validation is unit/synthetic only.** D-TRADE-033's 8 passing tests verify the code does what it says
   (labeling correctness, no-lookahead, a walk-forward smoke run) — they are **not** an OOS clearance.

Concretely: `labeling.py` and the walk-forward harness in `train_model.py` carry forward largely intact;
the data layer is rebuilt on `helm/ingest`; the feature set is admitted **feature-by-feature through
validation** (nothing ships because it is already coded); catalyst features re-tested live first.

**RULING on the Lead's flagged inference (D-TRADE-043 output 2) — CONFIRMED, not left as unruled precedent:**
**reused code does NOT inherit validation.** Passing unit/synthetic tests is evidence the code behaves as
written; it is *not* evidence the model predicts anything out-of-sample. Phase-2 authorization requires the
full independent-validation discipline (§4) — builder≠judge, AIQ independent re-derivation from raw, the OOS
bar — on the model's **real-data output**, regardless of how much code is reused. *(class — binds any Phase-2
model however much prior code it inherits.)*

## 4 · Output 3 — the validation bar for a predictive model
D-TRADE-021 was written for **detector** validation: does component X beat a naive-mean baseline on forward
*return*, under LOO + 5-fold, ≥90% of ≥30 seeds. A breakout-occurrence **classifier** is a different problem
shape (binary classification of a rare event; time-series walk-forward, not random k-fold which leaks in
time; the meaningful baseline is the base rate / not-trading, not a train-mean).

**Ruling: D-TRADE-021 applies WITH MODIFICATION — the discipline is unchanged and non-negotiable; the
concrete metric, baseline, and robustness mechanism are classifier-appropriate.** The bar shape (numbers
pre-registered + AIQ-co-signed + Director-ratified at Phase-2 entry, §6 E-2 — this ADR sets shape, not values):
- **Primary metric — OOS expected value net of realistic costs**, on the model's flagged trades **exited via
  Phase-1's validated trailing-stop rule** (NOT `train_model.py`'s current optimistic next-day-high EV). A
  model CLEARS only if flagged-trade EV beats the **no-trade / base-rate-entry baseline** out-of-sample.
  Secondary: precision at an actionable recall (so a high-precision-but-untradeable model is visible, not hidden).
- **Robustness (the ≥90%-of-≥30-seeds analogue).** Walk-forward folds are time-deterministic, so seed-shuffle
  agreement doesn't transfer directly. Replace with **two** checks: (i) **fold consistency** — the edge holds
  in the large majority of OOS walk-forward periods, not one lucky window; (ii) **model-seed sensitivity** —
  re-fit across ≥30 model random-states, the edge survives (the direct analogue, applied to the model's own
  randomness rather than the split's). **VOID** on any leakage/lookahead finding (unchanged).
- **Non-negotiable regardless of the chosen numbers:** builder≠judge (AI/ML builds/runs; **AIQ independently
  re-derives from raw primitives, never from the builder's output**), NN-1 point-in-time, D-TRADE-039 raw
  prices, the 4-state verdict schema incl. UNMEASURED (an event too rare to validate is UNMEASURED, not a
  silent negative — D-TRADE-029 spirit).

## 5 · Output 4 — data requirements
Under NN-1 (point-in-time) + D-TRADE-039 (raw/unadjusted): all price/volume via `helm/ingest/massive.py`
with `adjusted=false`. **Key finding — the existing event cohort is NOT reusable as the training panel:**
- The classifier learns to separate breakout days from **non-breakout** days; it needs a broad daily panel
  with **both classes** (mostly negatives — breakouts are rare) across the small-cap universe over a multi-year
  window. The D-TRADE-040/041 cohort is deliberately **event-defined** (qualifying spike events only) — it has
  almost no negative examples and **cannot train a classifier**.
- The event cohort **is** reusable as (a) a positive-label reference/sanity set and (b) a source of validated
  labels — not as the training panel.
- ⇒ Phase 2 needs a **fresh, broad, multi-year daily pull** (the grouped-daily-bars shape the `breakout_model`
  already uses, rebuilt on `helm/ingest`). This is **materially larger** than any pull authorized to date
  (D-TRADE-038 ~100 calls; D-TRADE-041 ~150 events) — exactly the "future pull that scales beyond this" that
  D-TRADE-038's standing condition names. **Hard data precondition:** the Massive rate-limit ceiling
  **confirmed** + `helm/spend/` (NN-8) **armed** before this pull (both still open per D-TRADE-038/041/042).
- Catalyst 8-K data: re-pull via the confirmed sec-api.io key (D-TRADE-026), peek-tested against the real
  account first (the code was built untested, `config.py`).

## 6 · Output 5 — entry conditions for Phase-2 build authorization
All must hold before any Phase-2 build/train/data-pull (this ADR authorizes none):
- **E-1 · Phase-1 closure is NOT a blanket hard prerequisite — with ONE hard dependency.** Phase 2 produces
  entry signals exited through Phase-1's **trailing-stop rule**; its EV bar (§4) exits through it. So the hard
  dependency is: **Leg B (the trailing-stop exit) built and validated (CLEARED, or at minimum fully
  characterized) — D-TRADE-042.** The rest of Phase-1 is **not** a prerequisite: a detector coming back
  NOT-CLEARED/UNMEASURED under Leg A does not block a from-scratch predictor (predicting what the existing
  detectors can't *is* Phase 2's point). If Leg B returns NOT-CLEARED/UNMEASURED, Phase 2's exit assumption is
  reopened → escalate before build.
- **E-2 · The modified bar (§4) pre-registered, AIQ-co-signed, Director-ratified** (the D-TRADE-021/036 path)
  — numbers fixed before any run (LL-44).
- **E-3 · Data preconditions (§5):** rate-limit ceiling confirmed + `helm/spend/` armed (NN-8).
- **E-4 · An explicit Director build-GO for Phase 2** (a D-TRADE-034 analogue). D-TRADE-043/034 do not cover it.
- **E-5 · builder≠judge lane assignment confirmed** (AI/ML builds; AIQ independent audit re-derives from raw)
  — the same structural split as Phase 1.

## 7 · Output 6 — treatment of externally-built components
**Ruling (reaffirming + operationalizing D-TRADE-032): OUT of scope by default; admissible ONLY via a formal
Director scope-assignment decision** naming the specific piece + its target component, **plus a protocol-17
AIQ validation**, carried by a **checkable artifact (protocol 16) through the standard chain — no prose
finding is admissible.** This covers the direction-side four-feature build sequence (VWAP distance,
consolidation stair-step, parabolic curve, and related) that the Lead confirmed is non-canonical with no HELM
visibility. **It applies equally to the versions already embedded in `breakout_model`'s `features.py`**
(consolidation/parabolic/vwap from "Copilot's architecture review") — their in-repo presence is **not**
adoption; each is subject to the same provenance re-establishment + validation before it counts as a HELM
feature. **Absence of a scope-assignment = OUT.** This is the durable rule that stops the ambiguity
D-TRADE-032/033 kept re-hitting.

## 8 · Risks
| id | risk | sev | mitigation |
|---|---|---|---|
| R-1 | reused code smuggles in un-validated features/data as "already done" | HIGH | §3 CONFIRMED ruling (reuse ≠ validation) + §7 (external-component gate) + feature-by-feature admission |
| R-2 | classifier over-fits a rare event; looks good in one window | HIGH | §4 fold-consistency + ≥30 model-seed robustness + AIQ re-derivation; VOID on leakage |
| R-3 | broad multi-year pull blows the (still-unconfirmed) rate-limit / spend cap | MED-HIGH | §5/E-3 hard precondition — ceiling confirmed + `helm/spend/` armed before the pull |
| R-4 | data-layer adjusted/raw or leg-T drift from the ungoverned `Trade/` original | MED | §3.1 — data layer rebuilt on `helm/ingest`, `adjusted=false`, not carried over |
| R-5 | Phase 2 built before Leg B validated → exit assumption unfounded | MED | E-1 hard dependency on Leg B |

## 9 · Complexity tier & co-sign
- **Tier:** §4 (the predictive-model validation bar) is a **CRITICAL** engine-rule/propagating decision →
  frontier depth + protocol-17 independent validation; **AIQ's co-sign on §4 + the §3 reuse-≠-validation
  ruling is load-bearing.** §1/§2/§5/§6/§7 are scoping judgment → Director-ratified. §5 data-architecture →
  SDE1/DevOps + FinOps input.
- **Co-sign before ratification:** **AIQ** (§4 bar + §3 ruling) · **AI/ML** (model buildability, harness/label
  reuse) · **SDE1 + DevOps** (§5 data surface, rate-limit ceiling, `helm/ingest` rebuild) · **FinOps** (the
  broad-pull spend, NN-8) · **Director** (scope ratification of §1/§2/§5/§6/§7 + resolves `<1.4>`; the E-4 GO
  is a later, separate decision).

## 10 · Open points & non-goals
- **OP-1 · the §4 bar's exact numbers** (EV-vs-baseline margin, actionable-recall level, fold-consistency %,
  model-seed count/agreement) — pre-registered at Phase-2 entry (E-2), not set here.
- **OP-2 · model family** — the `breakout_model` uses XGBoost/GradientBoosting; not locked here (an
  implementation choice for the build, subject to the same bar whatever it is).
- **Non-goals:** this ADR authorizes **no** build/train/data-pull (D-TRADE-043); does **not** lift D-TRADE-010
  for `breakout_model`; does **not** adopt any external feature; does **not** lock the §4 numbers.

## 11 · For a later revision (A6a/A6b)
A revision names every removed decision variable and partitions changed inputs into repairs vs re-resolutions
(LL-51), same discipline as ADR-0001 §13.
