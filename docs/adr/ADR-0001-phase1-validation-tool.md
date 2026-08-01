# ADR-0001 — HELM Phase-1: validation-tool structure, stack, lanes & the validation contract

- **Status:** PROPOSED (A0, pre-build) — awaiting oversight co-sign + Director wave-entry GO.
- **adr_reference id:** `ADR-0001` (cite on every Phase-1 build task, protocol 8).
- **Author:** Principal Architect (Fable5·Max). **Date:** 2026-08-01.
- **Governs:** canonical `<1.1>` `<1.4>` `<2.1>` `<2.2>` `<3.1>` `<3.2>` `<3.4>` `<3.5>` `<4.1>` `<4.2>`;
  D-TRADE-018/019/020; stage-plan P1-0..P1-5; oracle-boundary rows (AI/ML · AIQ · SDE1 · Data-Eng · FinOps
  · SecOps · DevOps · QA).
- **This ADR designs; it does not build.** No code is authorized by this document. See **Preconditions**.

> **Two-doc note (protocol 13):** this ADR is design content in my write-lane (`docs/adr/**`). Where it
> recommends changes to canonical statements (`<3.5>` stack, `<3.2>` spend guard shape) or the charter §3
> lane cut, those are **recommendations for the Lead to absorb** — I do not edit the canonical doc or the
> charter. Reference is by `<x.y>` id, never re-description.

---

## 1 · Summary + context

`<1.1>` is LOCKED (D-TRADE-020): HELM is a **personal** tool that **validates an already-built options
screener**, not a SaaS. The screener runs a rules-based composite technical score (trend / momentum /
breakout / volume, with an overextension dampener) over a **liquid, optionable large/mid-cap** universe and
recommends directional calls/puts near 0.40 delta at ~25–45 DTE. **Phase 1's job is validation, not
invention** (`<1.1>`): apply the *same* walk-forward-CV, ships-only-if-it-clears discipline already proven
across four completed equity studies to each screener component, testing **directional correctness** of the
underlying over the option's DTE window — the Director's explicit choice, **not** full option P&L (`<1.4>`,
Phase 2).

**The organizing architectural claim.** The existing scanner already encodes the target end-state: each
component is guarded by a `_gates` flag whose default *is* its study verdict —
`short_interest_gates=True` (cleared, "modest but real"), `catalyst_gates=False` (tested null),
`float_gates=False` (no data behind it) [`Downloads/rolling_watchlist (3).py:330-397`; findings in
`C:\Users\beale\short-interest-study\SHORT_INTEREST_STUDY_FINDINGS.md`]. The equity studies produce those
verdicts with a fixed CV harness — `evaluate_loo()` (LOO-CV, linear fit vs. train-mean naive baseline) and
`evaluate_multiseed_kfold()` (5-fold × 30 seeds, `pct_seeds_beating_naive`) [`short-interest-study/run_analysis.py:31,70,127`].
The studies' *code* used a ≥50% seed-agreement verdict; **Phase 1 adopts the stricter ratified bar
D-TRADE-021 / `<3.4>`** (BOTH LOO ∧ ≥90% of ≥30 seeds, OOS; VOID on leakage) — see NN-2. That the
short-interest winner hit 96.7%/93.3% and the catalyst false-positive only ~68% is precisely why ≥90%.

⇒ **Phase 1 = run that harness on each *options*-screener component and set its gate flag from the verdict.**
The deliverable is not "a backtest" — it is a **per-component gate-flag verdict** that flows into the
screener's existing `_gates` pattern, so the tool "ships with the components that actually work" (`<1.1>`,
stage-plan P1-exit) *mechanically*, not by opinion. Everything below serves that claim.

**What is genuinely new vs. the equity studies** (and therefore where the architectural risk sits):
1. the **target label** changes from "forward equity return at 1d/1w/1m" to **directional correctness over
   the option's DTE window** — a new modeling contract (§6, OP-1/2/3);
2. the data substrate adds **options chains + IV history**, which are the classic look-ahead trap and are
   **not yet confirmed available point-in-time** at the tier in use (`<2.1>`, R-3);
3. builder≠judge is now **structurally enforced by a second seat** (AIQ), not a single session self-checking.

## 2 · Approach (chosen, with the roads not taken)

**Chosen:** ingest-adapt-validate as a single Python package, reusing the studies' proven CV harness verbatim
where it transfers, extending only the label layer (§6). Validation output is a structured verdict record
that drives the screener's gate flags. Results are written **file-first** (CSV/parquet, exactly as the
studies emit `cv_results*.csv`) with Supabase as an *optional read-side* reference store this phase (§7,
integration) — deferring any Supabase **write** until the Director opens write access (D-TRADE-014).

**Rejected — rebuild the screener/backtest from scratch:** violates `<1.1>` ("validation, not invention")
and discards proven, in-hand assets. **Rejected — full option-P&L simulation now:** the Director explicitly
scoped Phase 1 to directional correctness (`<1.1>`/`<1.4>`); P&L (theta, IV-crush, slippage) is Phase-2 and
reuses the 0DTE engine. **Rejected — Supabase-write as the primary result sink this phase:** write access is
closed by default (D-TRADE-014, money-truth posture) and the studies already prove file-based results are
sufficient and reproducible; taking a write-access dependency onto the Phase-1 critical path buys nothing.

## 3 · Stack confirmation (`<3.5>` — Architect's call per canonical; recommend Lead absorb)

**CONFIRM: Python core; drop Node/Fastify/React entirely; Supabase retained read-side only this phase.**
- The screener, the 0DTE engine, and all four studies are Python (pandas/numpy/scipy) — every needed library
  is installed and importable *now* (charter §1 toolchain row, verified 2026-08-01). D-TRADE-017's
  Node/Docker/pnpm/gh absence **does not bite** a Python-only Phase 1; re-verify only if a non-Python
  component is ever pulled in.
- No web/API surface exists in `<1.1>` ("a Python script/tool I can run") ⇒ `apps/api`, `apps/web`,
  `packages/{domain,db,contracts,config}` and the Fastify/React stack are **N/A, dropped** (not deferred).
- Supabase (`zyscsnhiymitpfdhjuci`) is retained as the durable store for scan/verdict history but is used
  **read-only** in Phase 1 (§7); persistence-write is a later Director-gated step.
- Dependency pinning: `pyproject.toml` **or** `requirements.txt` with pinned versions; `.env` (gitignored)
  for keys (`<4.1>`).

## 4 · Module layout & ownership map

Single package `helm/`, disjoint-by-directory (the lane cut, §5). Directories are the write-lanes.

| Module | Purpose | Owner | Oracle leg it feeds |
|---|---|---|---|
| `helm/ingest/` | provider adapters (Massive, SEC-API.io), **point-in-time** pulls; the **ONLY** place a provider SDK/host may appear (leg T boundary) | SDE1 · Data-Eng | SecOps leg T; SDE1 schema/freshness |
| `helm/universe/` | liquid-optionable universe construction (OI/volume/bid-ask, point-in-time membership) | Data-Eng | Data-Eng universe-integrity leg |
| `helm/screener/` | the ingested composite-score + components + `_gates` flags | AI/ML | gate-flag conformance leg (§8 NN-4) |
| `helm/validation/engine/` | the walk-forward-CV engine: `evaluate_loo`, `evaluate_multiseed_kfold`, the pre-registered bar, verdict records | AI/ML (build) | AI/ML CV pass/fail leg |
| `helm/validation/audit/` | **AIQ's independent re-derivation** — reads RAW data + its own harness, **must not import `engine`'s results** (builder≠judge seam) | AIQ | AIQ re-derivation leg |
| `helm/storage/` | result persistence (file-first; Supabase read-side) — name aligns with DevOps's in-flight harness draft | SDE1 | SDE1 schema-conformance |
| `helm/spend/` | the spend-guard wrapper around every `ingest` call (`<3.2>`) | FinOps · SDE1 | FinOps cap-breach leg |
| `scripts/gate/` | the gate runner + all legs; import-boundary lint | DevOps | DevOps runner honesty |
| root config | `pyproject.toml`/`requirements.txt`, `.env.example`, CI | DevOps | leg K secret-scan |

**Compiler-adjacent boundary (a DevOps import-boundary leg, §8 NN-4/NN-7):**
- `helm/screener/` may not import a provider SDK directly — only the `helm/ingest/` adapter interface.
- `helm/validation/audit/` (AIQ) may not import `helm/validation/engine` **outputs** — it re-derives from
  raw. This *is* builder≠judge, encoded as an import rule.
- provider SDK/host imports appear **only** under `helm/ingest/` (leg T).

## 5 · Lane re-cut (confirms charter §3 draft; recommend Lead absorb into §3)

Disjoint-by-directory, one owner each; AI/ML owns build lanes B+C, AIQ owns the **independent** audit lane D.

| Lane | Owner | Write-lane |
|---|---|---|
| **A · ingest + universe + store** | SDE1 · Data-Eng | `helm/ingest`, `helm/universe`, `helm/storage` |
| **B · screener** | AI/ML | `helm/screener` |
| **C · validation engine** | AI/ML | `helm/validation/engine` |
| **D · validation audit (independent)** | AIQ | `helm/validation/audit` |
| **E · infra / CI / gate / spend** | DevOps · FinOps | `scripts/gate`, `helm/spend`, root config |
| Hot files | Lead allocates | LIVE BOARD · `working-log.md` |

## 6 · Data & label contracts (I author the CONTRACT + invariants; SDE1 authors the DDL)

**6.1 Durable entities (required fields + invariants, not final DDL — SDE1's lane):**
- `scan_runs(run_id, ts, universe_version, screener_version, params_json)`
- `signals(run_id, ticker, as_of_date, component_scores_json, composite_score, direction, target_delta, target_dte)`
- `validation_runs(val_id, ts, git_commit, bar_id, universe_version, n_components, n_horizons, n_comparisons)`
  — **`git_commit` + `bar_id` pin the pre-registered bar at a commit (LL-41/44); `n_comparisons` records
  the multiple-comparison count (R-5).**
- `validation_verdicts(val_id, component, horizon_dte, loo_beats_naive, pct_seeds_beating_naive, slope_sign,
  mean_pct_improvement, robustness_json, verdict∈{cleared,dropped}, reproduced_by_aiq)` — **append-only;
  a `cleared` verdict requires `reproduced_by_aiq=TRUE` (NN-3).**
- `spend_ledger(ts, provider, endpoint, est_cost, cumulative_day)` — every provider call writes a row **even
  at $0.00** (D-TRADE-019: rate/ToS governance + reconciliation, not just dollars).

**6.2 The directional-correctness label (the one genuinely new modeling contract — CRITICAL tier):**
- Signal at underlying date `t` with composite/component scores. **Label = the underlying's realized move
  over the option's DTE window** `[t, t+DTE]`, evaluated for *directional correctness* relative to the
  scored direction (call ⇒ up, put ⇒ down). This is **underlying-move directional correctness, explicitly
  NOT option P&L** (`<1.1>`/`<1.4>`; the exact trap the Director's own 0DTE backtest surfaced once).
- **Invariant (NN-1, non-negotiable):** every feature and every label at `t` uses **only** data timestamped
  `≤ t` — options chain, IV, price, *and universe membership* — joined point-in-time exactly as the
  short-interest study joined `settlement_date ≤ sample_date` with zero look-ahead
  [`short-interest-study/SHORT_INTEREST_STUDY_FINDINGS.md:25-29`].
- **Harness reuse:** `evaluate_loo` + `evaluate_multiseed_kfold` transfer verbatim; only the target vector
  and horizons change.

## 7 · Integration impact

- **Supabase (D-TRADE-014, read-only MCP):** Phase-1 **writes results to files** (CSV/parquet, like the
  studies) and uses Supabase **read-only** for reference; a Supabase **write** path is a later
  Director-gated change — **not on the Phase-1 critical path**. (Resolves the write-access question without
  blocking.)
- **Toolchain:** Python-ready; dropping Node clears D-TRADE-017 for Phase 1.
- **Existing assets:** the options-screener ZIP and the 0DTE-engine ZIP are **location-TBD** (P-2) — the
  exact component decomposition and the reuse surface bind against that source; until located, the component
  list here is provisional (OP-4).
- **B5 secrets:** live-key use waits on the B5 approval (`<4.1>`, PROJECT-CONFIG §4).

## 8 · Constraints / non-negotiables → others' oracle legs (the core Architect deliverable)

Each is stated as a **fail-closed assertion + the negative control that must make it bite** (admission test,
oracle-boundary.md) + the seat whose leg carries it. A seat OTHER than the one judged must be able to
produce the negative control.

| # | Non-negotiable (assertion, fail-closed) | Negative control (proves it bites) | Leg owner |
|---|---|---|---|
| **NN-1** | **No look-ahead.** Every feature/label at `t` uses only data `≤ t` (price, chain, IV, universe membership), joined point-in-time | inject a feature computed from `t+k` data → leakage leg RED | AIQ re-derivation + DevOps leakage assert |
| **NN-2** | **Pre-registered bar, frozen before the run — the ratified bar governs (D-TRADE-021 / `<3.4>`):** CLEARED ⇔ beats naive OOS under **BOTH** LOO-CV **AND** 5-fold CV (≥30 seeds) with **≥90% of seeds agreeing**; NOT-CLEARED otherwise; **VOID** on any leakage/lookahead/contamination regardless. Bar pinned to a git commit BEFORE any component is evaluated | a component that wins in-sample but fails OOS is **dropped**; a nominal LOO "win" that only ~68% of seeds agree with is **dropped** (the catalyst-1d coin-flip precedent — exactly why ≥90%, not ≥50%) | AI/ML runs · AIQ verifies pre-registration · GA audits it ran |
| **NN-3** | **Builder ≠ judge.** AIQ re-derives every `cleared` verdict from RAW data, not from the engine's summary; `cleared` requires `reproduced_by_aiq=TRUE` | AIQ re-run that disagrees with AI/ML's number → component blocked | AIQ · GA audits independence |
| **NN-4** | **Gate-flag conformance.** A screener component's `_gates` flag may be `True` only if a matching `cleared` verdict record exists; a `dropped`/absent verdict with `_gates=True` FAILS | set `float_gates=True` with no `cleared` record → conformance leg RED | SDE1/DevOps conformance leg |
| **NN-5** | **Universe integrity.** Every tested name has a real, liquid options chain (OI/volume/bid-ask) point-in-time at each signal date; a name lacking it is **excluded, not imputed** | inject an illiquid/no-chain name → universe leg excludes it | Data-Eng |
| **NN-6** | **Data schema/freshness.** Ingested market/options rows conform to schema + freshness bounds; a malformed or stale row FAILS rather than silently feeding the model | plant a stale/malformed row → SDE1 leg RED | SDE1 |
| **NN-7** | **No secret in repo / provider taint.** Keys in the secret store only (leg K); provider SDK/host only under `helm/ingest/` (leg T) | plant a fake `SEC_API_KEY=`/`MASSIVE_KEY=`, or a provider import in `helm/screener/` → RED | SecOps authors (`docs/security/key-denylist.md`) · DevOps wires |
| **NN-8** | **Spend guard.** A provider call that would breach the personal daily cap is BLOCKED (`<3.2>`) | simulate over-cap → call blocked | FinOps |
| **NN-9** | **Reproducibility.** QA re-runs each component's CV end-to-end in its own clone and the numbers reproduce (deterministic given pinned seeds + data) | a non-deterministic script whose numbers move on re-run → QA FAILS it | QA |

NN-1/2/3/4 are **CRITICAL** (they define what "cleared" *means*) → frontier A6 depth + protocol-17 recurring
validation. NN-5..9 are standard.

## 9 · Preconditions to build dispatch (HARD — none is my call to waive)

- **P-1 · D-TRADE-010 re-scope.** No-build stands until the **Director** explicitly confirms Phase-1
  quant-research build is outside D-TRADE-010's intent (Lead's recommendation in stage-plan, flagged as
  *not yet ruled*). This ADR (design) proceeds; **no seat writes production code until P-1 clears.**
- **P-2 · Locate + read the two ZIPs** (options screener, 0DTE engine). Component decomposition binds
  against source (OP-4). Owner: Director/Data-Eng to supply location.
- **P-3 · Provider + data-availability confirmation.** SecOps light-touch: Massive personal-tier compliant
  + SEC-API.io key identity (`<2.1>`, D-TRADE-018). **DevOps/Data-Eng discovery: is historical
  options-chain + IV data available point-in-time at the tier in use?** — gates whether IV-rank is testable
  at all (R-3) and bounds backtest depth for every component.
- **P-4 · The CV clearance bar is already ratified (D-TRADE-021 / `<3.4>`)** — this precondition is
  **narrowed** to ratifying the **directional-correctness label FORM** (OP-1: the DTE-window target/metric),
  which D-TRADE-021 did *not* fix. That form must be pinned before the run (LL-44). "Is the label the right
  label" is HUMAN residue (Director + AI/ML + AIQ).
- **P-5 · B5 secret approval** before any live-key use.

## 10 · Open points (first-class, LL-31) & non-goals

**Open (▸ NOT DECIDED — who decides):**
- **OP-1 · directional-correctness metric FORM** (Director + AI/ML + AIQ): *Recommend BOTH, both bars fixed
  before the run:* **(a)** continuous forward-underlying-return regression over the DTE window (reuse
  `evaluate()` verbatim, directly comparable to the studies) as the CV vehicle; **(b)** a **volatility-scaled
  directional-correctness binary computed on OHLCV alone** as the Phase-1 success criterion. **Converges with
  AI/ML's independent methodology draft** (`docs/roles/ai-ml/validation-methodology-draft.md`), which
  proposed exactly this two-tier structure. The OHLCV-only form is deliberate — it removes the *label*'s
  dependence on options-chain/IV data (see OP-3, R-3). Ratify before the run (LL-44).
- **OP-2 · DTE horizons** (AI/ML): the studies used 1d/1w/1m; options are ~25–45 DTE. *Recommend* primary
  horizons at the screener's real target band (~25/35/45 DTE), 1w/1m kept as continuity references.
- **OP-3 · the "far enough" move threshold** for a ~0.40-delta option. *Recommend (converged with AI/ML):*
  a **volatility-scaled** move threshold on OHLCV (e.g. a multiple of realized/ATR vol over the DTE window) —
  computable without options data, so the label doesn't block on `<2.1>`. The delta-implied breakeven move
  (which needs the 0DTE engine's pricing assumptions) is recorded as an **upgrade path**, not invented now;
  it sits at the Phase-2 boundary.
- **OP-4 · exact component list** — provisional {trend, momentum, breakout, volume} (`<1.1>`) + IV-rank
  (stage-plan P1-3); binds against screener source (P-2). IV-rank may be **untestable** if historical IV
  is unavailable (R-3) → then it defaults `gates=False`, no data behind it (the **float precedent**).

**Non-goals (explicit):** full option-P&L simulation (theta/IV-crush/slippage) — Phase 2 (`<1.4>`); a
from-scratch predictive breakout model — Phase 2; any web/API/UI surface; any multi-tenant/RLS machinery
(`<3.3>` N/A); a SaaS-grade metered-chokepoint/billing-reconciliation system (`<3.2>` is a right-sized
guard, LL-19).

## 11 · Risks

| id | risk | sev | mitigation |
|---|---|---|---|
| R-1 | look-ahead / leakage in options+IV data | HIGH | NN-1 + AIQ independent re-derivation (NN-3) |
| R-2 | screener source not yet in hand → provisional component list | MED | P-2; OP-4 marks provisional |
| R-3 | historical options-chain/IV not available point-in-time at tier | MED *(de-risked)* | the OHLCV-only volatility-scaled label (OP-1/OP-3, converged w/ AI/ML) removes the dependency for the *label* and for trend/momentum/breakout/volume; only the **IV-rank component** still needs historical IV → if unavailable it defaults `gates=False` (float precedent). P-3 discovery still on the critical path for IV-rank + backtest depth |
| R-4 | directional correctness ≠ profitability | known/accepted | `<1.1>`/`<1.4>` Phase-2 boundary; carry the magnitude caveat into every verdict (as short-interest FINDINGS did) |
| R-5 | multiple comparisons (components × horizons × metrics) inflate false positives | MED | seed-robustness bar (NN-2) + AIQ void-on-fragility (LL-47); record `n_comparisons` (§6.1) |
| R-6 | D-TRADE-010 not re-scoped | blocks build | P-1 (Director) |

## 12 · Complexity tier & co-sign

- **Tier:** validation contract (NN-1..4 + §6.2 label) = **CRITICAL** → frontier A6/ASR depth + protocol-17
  independent validation (AIQ). Stack/layout/lane (§3–5) = **STANDARD**.
- **Co-sign required before wave-entry GO** (each confirms the non-negotiables it will carry as a leg):
  AI/ML (validation engine + label) · AIQ (re-derivation + bar) · SDE1 (ingest/store/schema) · Data-Eng
  (universe/data-availability) · DevOps (gate legs + import-boundary) · FinOps (spend guard) · QA
  (reproducibility) · SecOps (legs K/T). **Director:** GO on the wave-entry gate + P-1 + P-4.

## 13 · For a later revision (A6a/A6b forward)
Any ADR-0001 revision must **name every removed decision variable** (A6a predicate-retention) and
**partition changed inputs** into repairs vs. re-resolutions (A6b) — a threshold that silently stops being
referenced is a distinction deleted, not partitioned (LL-51).
