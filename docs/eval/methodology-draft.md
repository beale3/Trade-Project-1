# Independent backtest-audit protocol (AIQ) — re-scoped under D-TRADE-020

> **RE-AUTHORED, not patched (LL-19 / protocol 19).** The prior version of this file was a golden-eval /
> anti-fabrication-grounding methodology for a **generative-AI signal engine** — that engine was deleted
> from scope by D-TRADE-020 (canonical `<3.4>` re-author). It does not describe HELM. This is a full
> replacement, not an addendum. If a future pivot ever reintroduces generative AI output, that framing
> gets a fresh elicitation, not a resurrection of the old text.
>
> **Status: ACTIVE PROTOCOL, pre-registered before any result exists.** Not a golden set — there is no
> fixed grading corpus to freeze here. This is the re-derivation + audit method that fires the moment
> AI/ML delivers a first CV result (stage-plan **P1-3**). Verified 2026-08-01: **no AI/ML backtest code is
> committed to this repo yet** (P1-2/P1-3 unstarted) → nothing to audit → HOLDING, same posture as before,
> now against real near-term work instead of an undecided product.
>
> **§2's bar is RATIFIED — D-TRADE-021 (Lead, 2026-08-01), propagated to canonical `<3.4>`.** No content
> change from what was drafted here; the "recommended, not self-ruled" language below is now historical —
> the bar is binding on every Phase-1 component test, not a proposal awaiting sign-off.
>
> **2026-08-04 — D-TRADE-028, second major pivot: options dropped entirely.** `<1.1>` now re-locked —
> HELM validates `tools/rolling_watchlist.py`'s plain stock buy/sell signals exited via a **new
> trailing-stop rule** (not yet built), not options directional-correctness. §0's subject description
> below (screener component / option's DTE window / liquid-optionable universe) is **SUPERSEDED** by this
> pivot — no calls/puts, no delta, no DTE window, no IV-rank component (no options data at all). The
> **replacement label/component list/horizons are `▸ NOT DECIDED`**, dispatched to the Architect (ADR-0001
> revision per canonical `<3.6>`, not yet delivered as of `fb830f1`) — I will not invent it myself.
> **Explicitly NOT reopened by D-TRADE-028 (its own text) and unchanged below:** §1–4 (the re-derivation
> sequence, the D-TRADE-021 bar, the verdict format) — this is subject-agnostic validation discipline that
> applies identically to a trailing-stop-exit stock result. Only the *subject* changes, not the *method*.

---

## 0 · Scope (per canonical `<1.1>`/`<3.4>`/`<3.6>`, stage-plan P1-3 — subject updated by D-TRADE-028)
AI/ML builds a **walk-forward-CV backtest pipeline** — classical statistics/quant research, not
generative AI — testing HELM's signal components for whether they predict a real, tradeable move. **The
exact subject-specific form (which components, what label, what horizons) is `▸ NOT DECIDED`**, pending
the Architect's ADR-0001 revision (canonical `<3.6>`): under D-TRADE-020 it was options
directional-correctness over a DTE window; under D-TRADE-028 (2026-08-04, current) it is realized stock
return under a new trailing-stop exit rule vs. a naive baseline, against `tools/rolling_watchlist.py`'s
existing guardrail/S3/pattern-detector triggers — no options, no DTE, no IV-rank. **My mandate is
unchanged across both:** independently re-derive and audit every CV result before a component is called
"cleared" — builder ≠ judge, on classical-statistics CV discipline, not LLM output. This is deliberately
written at the level of "a component's signal, whatever its native form, is one isolated predictor" so it
doesn't need to be rewritten every time the label/subject changes — only §0's context note above does.

**Reference discipline** (Lead-cited template): `C:\Users\beale\catalyst-study\CATALYST_STUDY_FINDINGS.md`
addendum — a nominal "beats naive" LOO-CV result at the 1-day horizon (+0.04% RMSE improvement, OOS R²
still negative) **evaporated entirely** under 5-fold CV on the same data (0/3 horizons beat naive). A
follow-up 50-seed sweep showed the apparent 1-day "win" was a **coin flip** (68% / 24% / 6% of seeds beat
naive across the three horizons) — below the ≥90%-of-seeds robustness bar the short-interest study had
already set as precedent. **That is the standard AI/ML's results must clear before I call anything
cleared**, and it is exactly the failure mode a tier-only or single-resampling check would miss.

## 1 · "Independently re-derive" means from raw data (LL-34) — never from AI/ML's summary
I do not audit by reading AI/ML's report and checking its arithmetic. I **re-run the CV from raw data**,
in my own script, against the same pre-registered bar. A component is not "cleared" until my from-scratch
re-derivation reproduces AI/ML's headline result (or shows it doesn't survive).

## 2 · Pre-registration — write-once, before I open AI/ML's result (LL-44)
Before touching any AI/ML output, I commit: the exact bar a component must clear, the resampling schemes
required, and the seed-sensitivity threshold. **Ratified bar (D-TRADE-021, Lead — binding on every
Phase-1 component test, propagated to canonical `<3.4>`):**
- Beats a naive out-of-sample baseline under **BOTH** LOO-CV **AND** 5-fold CV (matching stage-plan P1-3's
  explicit "LOO + 5-fold" requirement) — a result surviving only one scheme is **not cleared**
  (catalyst-study precedent, §0 above).
- **Seed-sensitivity sweep**, N ≥ 30 seeds, on whichever CV scheme is more fold-sensitive (typically
  5-fold): clears only if it beats naive on **≥90% of seeds** — the exact bar the short-interest and
  catalyst studies already used. A single-seed or single-scheme "win" is not evidence.
- No lookahead / no data leakage in the feature or label construction (this is "anti-fabrication
  grounding," re-mapped from LLM-citation-checking to classical-stats leakage-checking per `<3.4>`).

## 3 · Re-derivation + audit sequence, per screener component
1. **Freeze-and-pin (LL-41).** AI/ML's result is graded at a named commit hash; my audit record names it.
2. **Re-derive from raw data (LL-34).** Rebuild the feature, the CV split, the metric independently — I
   may reuse a fixed, already-inspected data-loading utility, but the CV logic and metric computation are
   mine, not copied from AI/ML's report.
3. **Cross-check both resampling schemes.** LOO AND 5-fold. Passing one and not the other = not cleared.
4. **Seed-sensitivity sweep** per §2 — ≥90% of ≥30 seeds beat naive, or it does not clear.
5. **Leakage/lookahead check** — no forward-looking data in the feature/label window.
6. **Catch-match, not tier-match (LL-42).** Agreeing with AI/ML on clear/no-clear is not enough if the
   *reason* differs — e.g. AI/ML clears it off one lucky seed, I show it's a coin flip: that is a
   coincidental agreement, not a catch-match, and the component does **not** clear.
7. **Fresh draw vs. fit-to-test (LL-43).** If a component fails and AI/ML retunes it, the retuned result
   is fit-to-test by construction against whatever informed the retune — labelled as such, never quoted as
   the honest number. Only a resampling draw / seed range / holdout period untouched by the retune counts.
8. **Void on contamination (LL-47).** If I see AI/ML's number or reasoning before completing my
   independent re-derivation, that check is contaminated — noted, and either re-run blind or the
   compromised independence is flagged explicitly, never silently trusted.

## 4 · Verdict format
Each component gets exactly one of: **CLEARED** (survives LOO + 5-fold + seed-sweep, independently
re-derived) · **NOT CLEARED** (fails any leg) · **VOID** (contamination / non-reproducible). No partial
credit — matches the existing 4-study precedent (short-interest kept; regime, catalyst, float dropped).

## 5 · What stays HUMAN (oracle-boundary row, re-scoped)
Per `docs/gate/oracle-boundary.md`: **"is the pre-registered bar itself the right bar"** (e.g., is
≥90%-of-30-seeds the correct robustness threshold, is whatever label the Architect's ADR-0001 revision
lands on — trailing-stop-exit realized return, per D-TRADE-028 — the right success metric) is a judgment
call — **HUMAN, escalates to the Lead/Director**. I certify mechanically whether a
component DID or DID NOT clear a stated bar; I do not certify that the bar itself is correct. §2's bar
started as exactly that kind of recommendation and was ratified by the Lead (D-TRADE-021) precisely
because it wasn't novel — it matched established precedent rather than resting on my own authority; a
future bar change would still need the same route, not a self-declared revision.

## 6 · Status
**HOLDING.** No AI/ML CV result or `helm/validation/` code exists in-repo yet (re-verified against
`git log`/tree at commit `fb830f1`, 2026-08-04, post-D-TRADE-028 — only `tools/`, the separate D-TRADE-023
dashboard side-tool, and docs exist; no `helm/` package). This protocol is pre-registered and ready to fire
the moment AI/ML delivers a first CV result, whatever the label ends up being once ADR-0001 is revised.
