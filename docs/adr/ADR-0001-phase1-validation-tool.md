# ADR-0001 — HELM Phase-1: validation-tool structure, stack, lanes & the validation contract

- **Status:** PROPOSED · **Revision 2 (2026-08-04, D-TRADE-028)** — re-authored, not patched (LL-19/protocol 19).
  Awaiting oversight co-sign + Director wave-entry GO. R2 supersedes R1's options framing entirely; the
  §14 delta declares every removal/change (ADR-0001 §13 / A6a-A6b).
- **adr_reference id:** `ADR-0001` (unchanged — build tasks keep citing it; protocol 8).
- **Author:** Principal Architect (Fable5·Max). **R1:** 2026-08-01 (options). **R2:** 2026-08-04 (equity + trailing-stop).
- **Governs:** canonical `<1.1>` `<1.4>` `<2.1>` `<2.2>` `<3.1>` `<3.2>` `<3.4>` `<3.5>` `<3.6>` `<4.1>` `<4.2>`;
  D-TRADE-020/021/022/026/027/**028**; oracle-boundary rows (AI/ML · AIQ · SDE1 · Data-Eng · FinOps · SecOps · DevOps · QA).
- **This ADR designs; it does not build.** No code is authorized by this document. See **Preconditions**.

> **Two-doc note (protocol 13):** design content in my write-lane (`docs/adr/**`). Recommendations to
> canonical statements (`<3.5>`/`<3.6>`/`<2.2>`) or the charter §3 lane cut are **for the Lead to absorb** —
> I do not edit the canonical doc or the charter. Reference by `<x.y>` id, never re-description.

---

## 1 · Summary + context (R2)

`<1.1>` re-locked (D-TRADE-028): HELM is a **personal equity-signal tool** that validates the scanner
**already in this repo** — `tools/rolling_watchlist.py` (rollover-watchlist + Guardrail #1 + Sykes S3 +
pump-&-dump phase + intraday pattern/pivot detectors, live-Massive-wired, already powering the D-TRADE-023
dashboard and the source of all 4 studies' `_gates` flags). **All options framing is DELETED** (no
calls/puts, delta, DTE, options-chain/IV, 0DTE-engine). HELM produces **plain stock buy signals** exited by
a **trailing-stop rule**, and validates them with the *same* walk-forward-CV, ships-only-if-it-clears
discipline (D-TRADE-021, **unchanged**).

**The organizing architectural claim (unchanged, now stronger).** The scanner already encodes the target
end-state: each component is guarded by a `_gates` flag whose default *is* its study verdict —
`short_interest_gates=True` (cleared), `catalyst_gates=False` (null), `float_gates=False` (no data)
[`tools/rolling_watchlist.py:414-484`]. The studies produce those verdicts with a fixed CV harness
(`evaluate_loo` + `evaluate_multiseed_kfold`; verdict = the D-TRADE-021 bar). ⇒ **Phase 1 runs that harness
on the components the studies never covered and on the new exit rule, and sets each gate flag from the
verdict** — "ships only what works" stays mechanical.

**What is new in R2** (where the design risk now sits):
1. the **exit rule** changes from a fixed stop/target to a **trailing stop that does not yet exist** —
   `simulate_day_trades()` has only a fixed stop/target [`tools/rolling_watchlist.py:723`]. Building it +
   validating it is Phase-1-critical, not a pre-existing artifact to test (§6.2).
2. the **label** changes from options-DTE directional correctness to **realized stock return under the
   trailing-stop exit** vs a naive fixed-holding-period baseline (§6.2).
3. the **components under test** change: drop IV-rank (no options); add the scanner's not-yet-validated
   entry signals — the pattern detectors (bull-flag/flat-top/ABCD/micro-pullback/round-number/opening-range)
   and the pivot / red-to-green alignment trigger (`<1.1>(a)`).
4. the **universe** requirement (`liquid optionable large/mid-cap`) is deleted; `<2.2>` reopens (§9 P-3).

## 2 · Approach (R2)

**Chosen:** validate-in-place over the in-repo scanner, reusing the studies' CV harness where it transfers
and extending only the exit-rule + label layer. Results write **file-first** (CSV/parquet, as the studies
emit `cv_results*.csv`); Supabase read-side only this phase (§7). **The trailing-stop is built as a
backward-compatible new exit mode inside `tools/rolling_watchlist.py`'s simulator** (default off = today's
fixed behavior), so the one implementation serves both the D-TRADE-023 dashboard's simulator panel and the
validation harness — no second copy of the exit logic (§6.3).

**Rejected — reimplement the scanner inside `helm/`:** violates `<1.1>` ("validate the existing scanner")
and forks the single source of truth. **Rejected — a separate trailing-stop impl in `helm/`:** would
double the exit logic and diverge from the dashboard; keep it in the shared scanner. **Rejected — full
parameter optimization of the trailing stop in Phase 1:** a fit-to-test rabbit hole (§6.4, OP-1); Phase 1
tests a small **pre-registered** set of trail settings.

## 3 · Stack (`<3.5>` — CONFIRMED, unchanged from R1/D-TRADE-022)
**Python core; Node/Fastify/React dropped (N/A).** Single package `helm/`, disjoint-by-directory. Supabase
`zyscsnhiymitpfdhjuci` read-only this phase (file-first results). Dependency pinning via
`pyproject.toml`/`requirements.txt`; `.env` (gitignored) for keys (`<4.1>`). D-TRADE-017's Node absence
does not bite a Python-only phase.

## 4 · Module layout & ownership map (R2 — screener re-scoped, universe conditional)

| Module | Purpose | Owner | Oracle leg it feeds |
|---|---|---|---|
| `helm/ingest/` | provider adapters (Massive, SEC-API.io), **point-in-time** pulls; the **ONLY** place a provider SDK/host may appear (leg T) | SDE1 · Data-Eng | SecOps leg T; SDE1 schema/freshness |
| `helm/universe/` | **CONDITIONAL — likely DROPS for Phase 1** (§9 P-3): scanner takes `--tickers`; validation runs over the studies' existing event-defined cohorts, not a maintained live universe | Data-Eng | (drops with the lane if confirmed) |
| `helm/screener/` | **RE-SCOPED:** a thin **feature-extraction adapter** over `tools/rolling_watchlist.py` — exposes each component's per-bar signal (guardrail pass · S3 score · each pattern fire · pivot alignment) as a tidy feature frame the CV harness consumes. Imports the scanner as a library; **never forks its logic** | AI/ML | gate-flag conformance leg (NN-4) |
| `helm/validation/engine/` | walk-forward-CV: `evaluate_loo`/`evaluate_multiseed_kfold`, the D-TRADE-021 bar, the two-leg contract (§6.2), verdict records | AI/ML (build) | AI/ML CV pass/fail leg |
| `helm/validation/audit/` | **AIQ** re-derives from RAW data; **must not import `engine`'s outputs** (builder≠judge as an import rule) | AIQ | AIQ re-derivation leg |
| `helm/storage/` | file-first results; Supabase read-side | SDE1 | SDE1 schema-conformance |
| `helm/spend/` | spend-guard wrapper around every `ingest` call (`<3.2>`) | FinOps · SDE1 | FinOps cap-breach leg |
| `tools/rolling_watchlist.py` | **the scanner — SHARED LIBRARY, single source of truth**, imported by BOTH `helm/screener` and `tools/web/` (D-TRADE-023). Stays a pure library (no import side-effects; `main()` under `__main__`). The trailing-stop exit mode is added here (§6.3) — a shared-file change, coordinate with the D-TRADE-023 seats | AI/ML builds the exit mode | (feeds NN-1/NN-10 via the simulator) |
| `scripts/gate/` | gate runner + legs; import-boundary lint | DevOps | runner honesty |

**Import boundaries (a DevOps leg):** `helm/screener` reaches the scanner only through `tools/rolling_watchlist.py`'s
function API; `helm/validation/audit` may not import `engine` outputs (builder≠judge); provider SDK/host imports
only under `helm/ingest`.

## 5 · Lane re-cut (R2 — absorb into charter §3)
A ingest+store (SDE1·Data-Eng) — `helm/ingest`,`helm/storage` (**universe conditional, §9 P-3**) · B screener
adapter (AI/ML) — `helm/screener` · C validation engine (AI/ML) — `helm/validation/engine` · D validation
audit (AIQ, independent) — `helm/validation/audit` · E infra/CI/gate/spend (DevOps·FinOps). Plus the **shared**
`tools/rolling_watchlist.py` (AI/ML owns the trailing-stop addition; coordinate with D-TRADE-023).

## 6 · Data & label contracts (I author the CONTRACT + invariants; SDE1 authors DDL)

**6.1 Durable entities** (required fields + invariants, not final DDL):
- `validation_runs(val_id, ts, git_commit, bar_id, cohort_id, n_components, n_exit_configs, n_comparisons)` —
  `git_commit`+`bar_id` pin the pre-registered bar (LL-41/44); `n_comparisons` records the multiple-comparison count.
- `validation_verdicts(val_id, subject, subject_kind∈{entry_signal,exit_rule}, horizon_or_config,
  loo_beats_naive, pct_seeds_beating_naive, effect_sign, effect_size, robustness_json,
  verdict∈{cleared,dropped}, reproduced_by_aiq)` — **append-only; `cleared` requires `reproduced_by_aiq=TRUE` (NN-3)**.
- `spend_ledger(ts, provider, endpoint, est_cost, cumulative_day)` — a row per provider call even at $0.00 (D-TRADE-019).

**6.2 The validation contract — TWO legs** (the R2 re-design; CRITICAL tier). Both use the studies'
harness and the D-TRADE-021 bar; both obey NN-1 (point-in-time).
- **Leg A · entry-signal validation** (per not-yet-validated component). Feature = the component's trigger
  (binary fire, or continuous score); target = forward stock return over a **fixed evaluation horizon**.
  Does entering on component-X beat a naive baseline (no-signal / all-bars mean) OOS under the bar? This is
  the studies' regression/CV discipline applied verbatim to the pattern detectors + pivot trigger. Verdict →
  the component's `_gates` flag (NN-4).
- **Leg B · exit-rule validation** (the trailing stop). Over the entry set, compare **realized trade return
  under the trailing-stop exit** vs the **naive baseline = fixed-holding-period exit** (same entries, exit
  after a fixed N bars, no trail). Metric = realized return (report both raw and a risk-adjusted variant —
  return per unit max-adverse-excursion). The D-TRADE-021 seed-agreement bar applies to the paired
  trailing-vs-fixed comparison across CV folds/seeds. **The holding period is endogenous** (set by when the
  trail is hit) — there is no fixed DTE/horizon for Leg B; Leg A's fixed horizon is only for entry-signal ranking.
- **How it plugs into the harness:** Leg A fits `evaluate_loo`/`evaluate_multiseed_kfold` directly
  (feature,target). Leg B is a small extension — a paired strategy-return comparison per fold/seed, reusing
  the same "beats-naive-OOS across ≥90% of ≥30 seeds" machinery, RMSE-of-fit swapped for realized-return-of-strategy.

**6.3 The trailing-stop rule** (new, built in `tools/rolling_watchlist.py`'s simulator as a mode). Precise
definition: after entry at `P0`, track `peak = max(High since entry)`; **trailing stop = `peak*(1 - trail_pct/100)`**,
ratchets up only, never down; exit at the first bar whose `Low ≤ stop` (filled at the stop — the conservative
tie assumption the existing sim already uses). An **initial hard stop `P0*(1 - init_stop_pct/100)`** governs
until the peak advances enough for the trail to take over (bounds the loss on a trade that never rises).
Decision variables: `trail_pct`, `init_stop_pct`, bar interval. **Bar-causal walk (NN-1):** `peak` at bar `i`
uses only bars `≤ i` — the existing simulator's forward walk already guarantees this; the trailing extension
must preserve it. Backward-compatible: default mode = today's fixed stop/target.

**6.4 Pre-registration of exit parameters (NN-10, new).** `trail_pct`/`init_stop_pct` are **fit on training
folds only and applied out-of-sample on the test fold** (or drawn from a small pre-registered set) — they are
**never chosen by looking at test-set outcomes**. This is the specific leakage vector a trailing stop
introduces and is a first-class non-negotiable (§8).

**Serialization/serializer** rules unchanged: NaN→null, Timestamp→ISO8601, DataFrame→records.

## 7 · Integration impact (R2)
- **Supabase (D-TRADE-014, read-only):** results file-first; Supabase write is a later Director-gated step,
  off the critical path.
- **Shared scanner:** `tools/rolling_watchlist.py` is now imported by both `tools/web/` (D-TRADE-023) and
  `helm/screener`. The trailing-stop addition (§6.3) is backward-compatible but touches this shared file —
  **coordinate with AI/ML/Designer on the D-TRADE-023 build** (the dashboard's simulator panel can adopt the
  trailing mode too). Shared-contract change ⇒ **not BYPASS-eligible** (cite ADR-0001).
- **Providers:** Massive (`<2.1>`, personal-tier confirm pending, SecOps) + SEC-API.io (D-TRADE-026/027,
  confirmed live, paid personal tier — no longer assume $0). **No options-chain/IV dependency** (deleted).
- **B5 secrets:** live-key use waits on the B5 approval.

## 8 · Constraints / non-negotiables → oracle legs (R2)
Each = a fail-closed assertion + the negative control that must make it bite + the leg owner.

| # | Non-negotiable | Negative control | Leg owner |
|---|---|---|---|
| **NN-1** | **No look-ahead.** Every feature/label/simulated-bar at `t` uses only data `≤ t`, point-in-time (incl. the trailing-stop `peak`) | inject a `t+k` feature, or a peak using a future bar → leakage leg RED | AIQ re-derivation + DevOps leakage assert |
| **NN-2** | **Ratified clearance bar (D-TRADE-021 / `<3.4>`):** CLEARED ⇔ beats naive OOS under BOTH LOO **and** ≥90% of ≥30-seed 5-fold; VOID on leakage/contamination. Pinned before the run | an in-sample win that fails OOS, or a ~68%-agreement coin-flip → dropped | AI/ML runs · AIQ verifies pre-registration · GA audits |
| **NN-3** | **Builder ≠ judge.** AIQ re-derives every `cleared` verdict from RAW; `cleared` requires `reproduced_by_aiq` | AIQ re-run disagrees → component/rule blocked | AIQ · GA audits independence |
| **NN-4** | **Gate-flag conformance.** A scanner component's `_gates=True` requires a matching `cleared` verdict | set a gate `True` with no `cleared` record → conformance leg RED | SDE1/DevOps |
| **NN-5** | **Cohort integrity** *(re-scoped from options-universe):* the backtest cohort is well-defined + point-in-time; a name/bar without the required history is excluded, not imputed. **No options-chain requirement** | inject a name with insufficient history → excluded | Data-Eng |
| **NN-6** | **Data schema/freshness.** Malformed/stale ingested row FAILS | plant a stale/malformed row → SDE1 leg RED | SDE1 |
| **NN-7** | **No secret / provider taint.** Keys server-side only (leg K); provider SDK/host only under `helm/ingest` (leg T) | plant a fake key / an out-of-module provider import → RED | SecOps authors · DevOps wires |
| **NN-8** | **Spend guard.** A call breaching the daily cap is BLOCKED | simulate over-cap → blocked | FinOps |
| **NN-9** | **Reproducibility.** QA re-runs each CV end-to-end; numbers reproduce (pinned seeds+data) | a non-deterministic script whose numbers move → QA FAILS | QA |
| **NN-10** | **Exit-parameter isolation (NEW, R2):** `trail_pct`/`init_stop_pct` fit on train folds only (or a pre-registered set), never chosen on the test fold | fit the trail on the full sample / test fold → leakage leg RED | AIQ + DevOps |

NN-1/2/3/4/10 = **CRITICAL** (they define what "cleared" means + the new leakage vector) → frontier A6 depth
+ protocol-17 AIQ validation. NN-5..9 = standard.

## 9 · Preconditions to build dispatch (R2 — none mine to waive)
- **P-1 · D-TRADE-010 re-scope.** No-build stands until the Director confirms Phase-1 quant-research build is
  outside D-TRADE-010's intent (Lead's recommendation; not yet ruled). Design proceeds; **no production code until P-1**.
- **P-2 · MOOT (D-TRADE-028).** The "missing screener/0DTE ZIPs" were never missing — the scanner is
  `tools/rolling_watchlist.py`, in-repo. No artifact-location work remains.
- **P-3 · `<2.2>` universe decision** (Architect/Data-Eng): confirm the Phase-1 backtest cohort = the studies'
  existing event-defined datasets + user-supplied tickers (⇒ `helm/universe` lane **drops**), vs. a maintained
  universe (⇒ lane stays). *Recommend drop* — matches the scanner's `--tickers` status quo and the studies' cohorts.
- **P-4 · Ratify the Leg-A horizon + Leg-B baseline + the pre-registered trail set** (Director + AI/ML + AIQ)
  before the run (LL-44). The D-TRADE-021 *bar* is already ratified; what's open is the label parameters (OP-1..3).
- **P-5 · B5 secret approval** before any live-key use.

## 10 · Open points (LL-31) & non-goals (R2)
- **OP-1 · the pre-registered trailing-stop set** (Director + AI/ML + AIQ): which `{trail_pct, init_stop_pct}`
  settings Phase 1 tests. *Recommend* a small fixed grid (e.g. trail ∈ {5,8,12}%, init ∈ {2,3}%) fixed before
  the run — **not** an optimization (that's Phase 2, `<1.4>`).
- **OP-2 · Leg-A evaluation horizon** (AI/ML): the fixed forward window for entry-signal ranking. *Recommend*
  the studies' existing 1d/1w/1m set (directly comparable to the 4 completed studies).
- **OP-3 · Leg-B naive baseline** (AI/ML + AIQ): fixed-holding-period exit — *recommend* N = the median
  realized holding period of the trailing-stop arm (so the comparison is horizon-matched), plus a couple of
  fixed N as sensitivity.
- **OP-4 · component list** (final): drop IV-rank; test {each pattern detector, pivot/red-to-green trigger}
  as Leg-A entry signals + the trailing stop as Leg-B. The already-validated study components
  (short-interest kept, catalyst/float/regime as-ruled) are **not** re-litigated.
- **Non-goals:** options anything (deleted); trailing-stop **optimization** / adaptive-ATR variants (Phase 2);
  the from-scratch predictive breakout-occurrence model (Phase 2); any web/API/UI surface **inside `helm/`**
  (the D-TRADE-023 dashboard is a separate tool); multi-tenant/RLS (`<3.3>` N/A).

## 11 · Risks (R2)
| id | risk | sev | mitigation |
|---|---|---|---|
| R-1 | look-ahead/leakage — now incl. the trailing-stop peak + exit-parameter fitting | HIGH | NN-1 + NN-10 + AIQ re-derive (NN-3) |
| R-2 | multiple comparisons (components × horizons × trail settings) inflate false positives | MED-HIGH | the ≥90%-seed bar (NN-2) + AIQ void-on-fragility; record `n_comparisons` |
| R-3 | shared-file churn — trailing-stop edit to `tools/rolling_watchlist.py` collides with the live D-TRADE-023 build | MED | backward-compatible mode (default off) + coordinate with AI/ML/Designer (§7) |
| R-4 | realized-return metric is noisy on small cohorts | MED | report raw + risk-adjusted; seed-robustness bar; magnitude honesty (as short-interest FINDINGS did) |
| R-5 | D-TRADE-010 not re-scoped | blocks build | P-1 (Director) |

## 12 · Complexity tier & co-sign (R2)
- **Tier:** the two-leg label + trailing-stop + NN-10 = **CRITICAL** → frontier A6/ASR depth + protocol-17
  independent validation (AIQ). Stack/layout/lane = STANDARD.
- **Co-sign before wave-entry GO:** AI/ML (harness + trailing-stop + Leg-A/B) · **AIQ (the label design +
  NN-10 + the baseline — this is the CRITICAL methodology leg, its sign-off is load-bearing)** · SDE1
  (ingest/store/schema) · Data-Eng (cohort/universe P-3) · DevOps (legs + import-boundary + shared-file
  coordination) · FinOps (spend) · QA (reproducibility) · SecOps (legs K/T). **Director:** GO + P-1 + P-4.

## 13 · For a later revision (A6a/A6b forward)
Any revision names every removed decision variable (A6a) and partitions changed inputs into repairs vs
re-resolutions (A6b) — a silently unreferenced threshold is a distinction deleted, not partitioned (LL-51).
R2's own delta is §14.

## 14 · Revision 2 delta (D-TRADE-028 — the §13 A6a/A6b declaration)
**A6a · decision variables REMOVED (named, with reason):**
- options-DTE directional-correctness label · the OHLCV volatility-scaled directional binary (R1 OP-1) —
  removed: no options, the exit rule is now the object of study, not a directional-move label.
- DTE horizons 25/35/45 (R1 OP-2) — removed: no options; horizons are now Leg-A's fixed window + Leg-B's
  endogenous holding period.
- the delta-implied "far enough" move threshold (R1 OP-3) — removed: no delta/options pricing in scope.
- the **IV-rank** component (R1 OP-4) — removed: no options/IV data.
- the historical options-chain/IV **data dependency** (R1 R-3) — removed/moot.
- the **liquid-optionable large/mid-cap universe** requirement (R1 NN-5) — removed: no options-chain need.
- **P-2** (locate the screener/0DTE ZIPs) — removed/moot: the scanner is in-repo (`tools/rolling_watchlist.py`).
- the 0DTE-backtest-engine reuse plan (R1 Phase-2-A) — removed: no 0DTE engine in scope.

**A6b · changed inputs partitioned (repair vs re-resolution):**
- label (`<3.6>`) — **RE-RESOLVED:** DTE directional correctness → the two-leg contract (Leg A entry-signal;
  Leg B trailing-stop realized return vs fixed-holding baseline).
- component list — **RE-RESOLVED:** drop IV-rank; add pattern detectors + pivot/red-to-green trigger.
- `helm/screener` purpose — **REPAIRED (re-scoped):** "ingest the missing options screener" → thin
  feature-extraction adapter over the in-repo scanner.
- `helm/universe` — **RE-RESOLVED (conditional):** likely dropped for Phase 1 (P-3).
- NN-5 — **REPAIRED:** options-universe integrity → generic cohort integrity (no options-chain clause).

**Carried forward UNCHANGED (explicit — not silently retained):** NN-1 (no-lookahead/point-in-time),
NN-2 = the D-TRADE-021 bar, NN-3 (AIQ builder≠judge), NN-4 (gate-flag conformance), NN-6/7/8/9; the
gate-flag organizing claim; the CV harness reuse (`evaluate_loo`/`evaluate_multiseed_kfold`); stack `<3.5>`
Python core; lanes C/D/E. **NEW in R2:** NN-10 (exit-parameter isolation); the trailing-stop rule (§6.3);
Leg A/B (§6.2); `tools/rolling_watchlist.py` as a shared library.
