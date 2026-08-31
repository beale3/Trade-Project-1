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
>
> **2026-08-04 — ADR-0001 R2 landed and audited; co-signing.** The Architect delivered the two-leg
> contract (§0 below, no longer `▸ NOT DECIDED`). Load-bearing review (protocol 17) found 3 gaps — a
> builder≠judge hole at the feature-extraction layer, NN-10 not covering the Leg-B baseline `N`, and no
> bar against grid-cell cherry-picking — plus a 4th converged with AI/ML mid-review (a support floor for
> thin-firing components, verdict = UNMEASURED not DROPPED). **All 4 verified fixed in the revised text**
> (not just claimed — re-read the actual ADR, not the summary, per §1's own discipline): import boundary
> now bars Lane D from `helm/screener` outputs too (NN-3) · NN-10 broadened to every data-derived
> label/baseline parameter, train-fold-only · one pre-registered grid cell is clearance-eligible, the rest
> sensitivity-only (OP-1) · UNMEASURED added as a 4th verdict state, floor **ratified at 30 events**
> (D-TRADE-029). §3/§4 below updated to match. **One flag, not blocking:** the ADR's own OP-5/§6.2/P-4 text
> still reads "TBD"/"pending" for the floor value despite D-TRADE-029 already ratifying it — a stale-text
> gap against the governing decisions-log record (protocol 16), not a design defect; flagged back to the
> Architect for a quick fix, not held against co-sign.
>
> **2026-08-31 — CATCH-UP after a ~26-day gap; prior "holding for P-1" status was STALE, corrected.**
> Flagged externally (not self-caught) that this session's displayed status still said "holding for P-1"
> after **D-TRADE-034 lifted P-1 for Phase-1 build on 2026-08-30**. `git pull --rebase` + full re-read
> (decisions-log through D-TRADE-036, AGENT-COORDINATION board, ADR-0001) confirms: P-1/P-3/P-4 all
> ratified 2026-08-30, real build-GO issued, a 4-stage build chain dispatched (AI/ML→AIQ→QA→DevOps,
> Director-mandated staged reporting). **Substance unchanged despite the stale wording — verified no
> `helm/` directory exists in-repo, so Stage 1 (AI/ML) hasn't delivered and there is still nothing to
> audit.** The correct current reason for holding is "queued as Stage 2, behind AI/ML," not "P-1
> blocking" — a real difference for anyone reading status, not a cosmetic one. See §6 (bottom) and the
> P-4 update in §0's parameter list. Lesson for myself: an idle lane must re-read before speaking, not
> just before writing to the repo (§Routines dispatch-freshness) — I'd been doing that for repo edits but
> let a chat status reply go stale.

---

## 0 · Scope (per canonical `<3.6>` / ADR-0001 R2 §6.2, ratified two-leg contract, D-TRADE-028)
AI/ML builds a **walk-forward-CV backtest pipeline** — classical statistics/quant research, not
generative AI — testing HELM's signal components for whether they predict a real, tradeable move, via
**two legs**, both governed by the D-TRADE-021 bar and NN-1 (point-in-time):
- **Leg A · entry-signal validation** — per not-yet-validated component (the 8 `scan_all_patterns`
  detectors + the pivot/red-to-green trigger): does entering on it beat a naive baseline (no-signal /
  all-bars mean) OOS, over a fixed evaluation horizon (studies' 1d/1w/1m style, OP-2)? Verdict → the
  component's `_gates` flag.
- **Leg B · exit-rule validation** — the new trailing-stop rule: realized trade return under the trailing
  exit vs. a fixed-holding-period naive baseline, over the same entry set. Holding period is endogenous
  (no fixed horizon); metric = realized return, raw + risk-adjusted.

**My mandate is unchanged across the pivot:** independently re-derive and audit every CV result, both
legs, before a component/rule is called "cleared" — builder ≠ judge, on classical-statistics CV
discipline, not LLM output.

**P-4 parameters — ALL LOCKED (D-TRADE-036, 2026-08-30):** OP-1 grid `trail_pct∈{5,8,12}%` /
`init_stop_pct∈{2,3}%`, primary clearance-eligible cell = `(8,3)`, rest sensitivity-only · OP-2 = the
studies' 1d/1w/1m · OP-3 = a **fully pre-registered fixed N=5 trading days** (not the train-fold-derived-
median alternative — the leakage-free option I'd flagged as safer, which is what got chosen) · OP-5 = 30
events (D-TRADE-029). **Flag, not an objection:** OP-1/2/3 were Director-authorized Lead defaults,
explicitly **not AIQ-cosigned** (unlike D-TRADE-029/030's numbers) — a deliberate, disclosed shortcut of
ADR-0001 §12's stated co-sign expectation, not a hidden gap. Quick read against my own methodology on
catch-up (2026-08-30/31): the values are sound — OP-3 in particular sidesteps my original finding #2
entirely by choosing the leakage-free fixed-N path over the data-derived-median one. No objection to raise
retroactively; noting for the record that this step was HUMAN-shortcut, not independently verified by me.

**Reference discipline** (Lead-cited template): `C:\Users\beale\catalyst-study\CATALYST_STUDY_FINDINGS.md`
addendum — a nominal "beats naive" LOO-CV result at the 1-day horizon (+0.04% RMSE improvement, OOS R²
still negative) **evaporated entirely** under 5-fold CV on the same data (0/3 horizons beat naive). A
follow-up 50-seed sweep showed the apparent 1-day "win" was a **coin flip** (68% / 24% / 6% of seeds beat
naive across the three horizons) — below the ≥90%-of-seeds robustness bar the short-interest study had
already set as precedent. **That is the standard AI/ML's results must clear before I call anything
cleared**, and it is exactly the failure mode a tier-only or single-resampling check would miss.

## 1 · "Independently re-derive" means from raw data (LL-34) — never from AI/ML's summary or its adapter
I do not audit by reading AI/ML's report and checking its arithmetic. I **re-run the CV from raw data**,
in my own script, against the same pre-registered bar. A component is not "cleared" until my from-scratch
re-derivation reproduces AI/ML's headline result (or shows it doesn't survive). **"Raw" means
`tools/rolling_watchlist.py`'s primitives directly (ADR-0001 §4/NN-3, my own audit finding #1) — I do
not import `helm/screener`'s feature frame either**, even though it's not the CV engine: it's AI/ML-owned
code that transforms the raw signal, and a bug there would otherwise be invisible to both lanes. Every
feature I score is one I extracted myself from the scanner's own functions.

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
9. **Support-floor check (D-TRADE-029, before CV even runs).** For a Leg-A component, count its trigger
   events first. Below **30**, the verdict is **UNMEASURED** — I do not run CV at all, since a from-scratch
   re-derivation on a thin sample would just be noise re-derived, not a real independent check.
10. **Parameter-isolation check (NN-10, ADR-0001 §6.4/§8, my own audit finding #2).** For Leg B and any
    grid-selected Leg-A parameter: confirm `N` (and `trail_pct`/`init_stop_pct` if selection was used) was
    computed on train-fold data only, never from the test-fold trades it's scored against — I verify this
    on MY OWN re-derivation, not by trusting AI/ML's fold-splitting code. If the pre-registered grid's
    single primary cell (OP-1) was used with no selection, this check is simpler: confirm no selection
    happened at all — every cell reported, only the pre-designated primary treated as clearance-eligible.

## 4 · Verdict format (4 states, ADR-0001 §6.1, D-TRADE-029)
Each component/rule gets exactly one of: **CLEARED** (survives LOO + 5-fold + seed-sweep, independently
re-derived) · **DROPPED** (tested, fails any leg — was "NOT CLEARED" in earlier drafts, renamed to match
ADR-0001's canonical `validation_verdicts` schema) · **VOID** (contamination / non-reproducible) ·
**UNMEASURED** (below the 30-event support floor — untested for lack of evidence, never a judgment; float-
study "no data behind it" precedent). No partial credit, no state overlap — matches the 4-study precedent
(short-interest kept; regime/catalyst/float dropped) extended with the UNMEASURED distinction D-TRADE-029
adds on top of it.

## 5 · What stays HUMAN (oracle-boundary row, re-scoped)
Per `docs/gate/oracle-boundary.md`: **"is the pre-registered bar itself the right bar"** (e.g., is
≥90%-of-30-seeds the correct robustness threshold, is realized return under a trailing-stop the right
Leg-B success metric, is 30 events the right support floor) is a judgment call — **HUMAN, escalates to the
Lead/Director**. I certify mechanically whether a component/rule DID or DID NOT clear a stated bar; I do
not certify that the bar itself is correct. §2's bar and §3.9's floor both started as exactly that kind of
recommendation and were ratified against precedent (D-TRADE-021, D-TRADE-029) rather than resting on my
own authority; a future bar change would still need the same route, not a self-declared revision. OP-1/2/3
are now locked (D-TRADE-036) — see §0's flag on the not-AIQ-cosigned shortcut.

## 6 · Status (corrected on catch-up, 2026-08-31 — see working-log for the staleness note)
**CO-SIGNED ADR-0001 R2 (2026-08-04, absorbed as D-TRADE-030).** **P-1 LIFTED for Phase-1 build
(D-TRADE-034, 2026-08-30)** — build-GO issued; my prior "holding for P-1" status was stale and is
corrected here. **P-3/P-4 also resolved** (D-TRADE-035/036). Director's 2026-08-30 build-chain dispatch:
AI/ML (Stage 1) → **AIQ (Stage 2, me)** → QA (Stage 3, not yet spawned) → DevOps (Stage 4), staged
reporting at each handoff per the Director's explicit override of the batched protocol-15 default.
**Still nothing to audit** — verified no `helm/` directory exists in-repo (Stage 1 hasn't delivered yet;
AI/ML's own board row shows idle). Correctly queued behind AI/ML's delivery, not blocked on any
precondition anymore. Ready to fire the moment `helm/screener`/`helm/validation/engine` land.
