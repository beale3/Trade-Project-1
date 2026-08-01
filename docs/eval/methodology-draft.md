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

---

## 0 · Scope (per D-TRADE-020 / canonical `<3.4>` / stage-plan P1-3)
AI/ML builds a **walk-forward-CV backtest pipeline** — classical statistics/quant research, not
generative AI — testing each options-screener component (trend / momentum / breakout / volume / IV-rank)
for **directional correctness** of the underlying within the option's ~25–45 DTE window, against a
liquid-optionable universe. My mandate re-scopes from "judge generative-AI output for
anti-fabrication/grounding" to **independently re-derive and audit every CV result before a component is
called "cleared"** — builder ≠ judge, now on classical-statistics CV discipline, not LLM output.

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
required, and the seed-sensitivity threshold. **Recommended bar (for Lead/Director ratification — not
self-declared binding):**
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
≥90%-of-30-seeds the correct robustness threshold, is directional-correctness-within-DTE the right success
metric) is a judgment call — **HUMAN, escalates to the Lead/Director**. I certify mechanically whether a
component DID or DID NOT clear a stated bar; I do not certify that the bar itself is correct. §2's
recommended bar is exactly that kind of recommendation, not a ruling.

## 6 · Status
**HOLDING.** No AI/ML CV result exists in-repo yet (verified against `git log`/tree at commit `47f6e60` —
P1-2 screener ingestion and P1-3 validation engine are both unstarted). This protocol is pre-registered
and ready to fire the moment AI/ML delivers a first CV result on any screener component.
