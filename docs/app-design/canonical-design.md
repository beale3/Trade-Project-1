# HELM — canonical design doc (the single source of truth)

Protocol 13: this is the ONE canonical design doc. **Only the Lead edits it.** Every other seat APPENDS
to `working-log.md`; the Lead absorbs. Reference design by its `<x.y>` id, never by re-describing it.
Open points are **first-class inline `▸ NOT DECIDED` markers** (who decides + a recommendation) — silence
must never read as decided (LL-31).

> **2026-08-01 — MAJOR REVISION.** `<1.1>` locked (Director, 3-round elicitation). This re-authors §1–4
> rather than patching alongside the superseded SaaS strawman (LL-19 — a doc saying two contradictory
> things is worse than one that's simply wrong). Superseded framing (multi-tenant SaaS, money-truth
> chokepoint at SaaS scale, generative-AI signal engine) is **deleted**, not parked — see LL-19/protocol 19.
>
> **2026-08-04 — SECOND MAJOR REVISION (narrower, on top of the first).** Director, direct instruction:
> *"Ignore all Option language in the original description. Implement standard trading logic using basic
> buy/sell signals and trailing-stop rules... Do not apply any Option-related logic."* Confirmed to apply
> to HELM Phase-1 itself, not just the separate D-TRADE-023 dashboard side-tool. **The personal-tool pivot
> (D-TRADE-020) stands unchanged — only the options-vs-equity question changes.** All options framing
> (calls/puts, delta targeting, DTE windows, the 0DTE-backtest-engine reuse plan) is **deleted, not
> parked** (LL-19, protocol 19, applied a second time to this doc). Recorded as D-TRADE-028.

## 1 · Product
- **`<1.1>` What HELM is — 🔒 RE-LOCKED (Director, 2026-08-04 — supersedes only the options framing
  below; the personal-tool pivot itself, D-TRADE-020, is untouched).** HELM is a **personal trading-signal
  tool** that formalizes and empirically validates the **existing equity scanner already in this repo**:
  `tools/rolling_watchlist.py` (the rollover-watchlist + Guardrail #1 + Sykes S3 score + pump-and-dump-
  phase + pattern-detector scanner — already wired to live Massive data, already powering the D-TRADE-023
  dashboard, already the source of all 4 completed equity studies' `_gates` flags). **Options framing is
  DELETED, not parked** (LL-19/protocol 19): no calls/puts, no delta targeting, no DTE window. HELM
  recommends **plain stock buy signals** (the scanner's existing guardrail/S3/pattern triggers), exited via
  a **trailing-stop rule** — Director's direct instruction, 2026-08-04: *"Implement standard trading logic
  using basic buy/sell signals and trailing-stop rules... Do not apply any Option-related logic."*
  **Phase 1's job, updated:** the same walk-forward-CV, ships-only-if-it-clears-the-bar discipline
  (unchanged, D-TRADE-021) now applies to (a) the scanner's components not yet validated by the 4
  completed studies (the pattern detectors — bull-flag/flat-top/ABCD/micro-pullback/round-number/opening-
  range — and the pivot/red-to-green intraday alignment trigger), and (b) the **trailing-stop exit rule
  itself**, which does not yet exist — `simulate_day_trades()` currently has a FIXED stop-loss/target, not
  a trailing stop; building and validating that rule is now Phase-1-critical, not a pre-existing artifact
  to merely test. The old "directional correctness vs. an option's DTE window" label (`<3.6>`, old) no
  longer applies — ▸ **NOT DECIDED, dispatched to the Architect:** redesign the label/validation contract
  around realized stock return under the trailing-stop exit rule vs. a naive baseline (ADR-0001 revision).
  **P-2 status — MOOT, not resolved-by-search.** The "options-screener + 0DTE-backtest-engine ZIP" this
  open item asked the Director to locate never needed finding: the actual, already-built screener is
  `tools/rolling_watchlist.py`, confirmed already fully in this repo (verified 2026-08-04 against the
  Director's own pasted source — every function present; the repo copy is a strict superset, with the
  Massive-wiring this session added on top). No further search needed; nothing was ever actually missing.
- **`<1.2>` Primary user** — the Director, personally, for personal trading decisions. No other users,
  no distribution, no monetization. This is load-bearing for `<3.x>`/`<4.x>` below (no multi-tenant
  surface; no "regulated advice to others" question).
- **`<1.3>` Cost model = billed per-use** (D-TRADE-004), but at **personal scale** — a spend GUARD
  (cap + visibility), not a SaaS-grade metered-chokepoint/billing-reconciliation system. See `<3.2>`.
- **`<1.4>` Phase 2 — re-scoped, ▸ NOT DECIDED on the exact boundary, dispatched to the Architect.** The
  old plan ("reuse the 0DTE backtest engine's slippage/spread modeling" for option P&L) is **deleted** —
  there is no 0DTE engine in scope. `simulate_day_trades()` already does realistic stock-trade P&L
  simulation (stop-loss, target, daily-loss/profit-giveback halts); whether validating the new
  trailing-stop rule belongs in Phase 1 (it's now Phase-1-critical per `<1.1>`) or Phase 2 is an open
  boundary question. The from-scratch predictive breakout-occurrence model (unchanged) stays Phase 2, out
  of scope now.

## 2 · Domain / data
- **`<2.1>` External providers.**
  - **Massive (formerly Polygon.io)** — the live source for market/options data across ALL prior research
    (4 equity studies + the options screener + the 0DTE backtest). SecOps's earlier HIGH-taint finding
    (`docs/security/tos-taint-review.md`, D-TRADE-018) was scoped to **commercial/SaaS use** — the
    default/individual "Non-Professional" tier's restrictions (non-commercial, no redistribution, no
    "investment strategy" derivative works) plausibly describe exactly the right, compliant tier for
    `<1.2>`'s personal use. ▸ **NOT DECIDED — Legal/SecOps to confirm the account is actually on that
    tier and that usage stays within it** (a light confirmatory check now, not the heavy commercial-tier
    gate previously scoped).
  - **SEC-API.io — 🔒 CONFIRMED (D-TRADE-026, 2026-08-01).** `..\Trade\sec_api_key.txt` holds a live
    `SEC_API_KEY=<value>` credential, verified by a real authenticated call to `api.sec-api.io` (HTTP 200,
    real EDGAR filing data returned) and corroborated by the Director's own logged-in sec-api.io account.
    **This is a paid personal-tier subscription key, NOT free public keyless EDGAR** — FinOps/SecOps to
    reframe `docs/finops/cost-model.md` and `docs/security/tos-taint-review.md`'s EDGAR entries accordingly
    (was assumed $0-marginal/keyless under D-TRADE-019; that assumption no longer holds for this key).
  - **Historical options-chain data — DELETED (2026-08-04), not applicable.** No options in scope
    (`<1.1>`); this open item is moot, not resolved.
  - **Key handling:** real keys NEVER enter this repo — secret store only (`<4.1>`).
- **`<2.2>` Universe construction — reopened, simplified (2026-08-04).** The prior "liquid, optionable
  large/mid-cap" requirement is **deleted** with the options framing — no real-options-chain/tight-spread
  need remains. Reverts toward the cohort `tools/rolling_watchlist.py` and all 4 completed studies already
  use (low-priced, volatile, gap-and-hold microcaps; no options-chain requirement). The script itself takes
  a **user-supplied ticker list** (`--tickers`, no built-in discovery) — 🔒 **RESOLVED (D-TRADE-035,
  2026-08-30): no maintained universe list.** The Phase-1 cohort is the studies' existing event-defined
  datasets + user-supplied `--tickers` — the status quo. `helm/universe` drops from scope entirely, not
  deferred; NN-5/Data-Eng references drop with it.

## 3 · Architecture (planned; ADRs author the binding form at build time)
- **`<3.1>` Modular monolith / simple Python project** — no SaaS-scale modular-monolith machinery
  required; default stack question reopens (`<3.5>`).
- **`<3.2>` The spend guard** (replaces the SaaS-scale "money-truth chokepoint," LL-19 re-author) — a
  lightweight cap + visibility layer on provider API spend (Massive, SEC-API.io) so a runaway loop can't
  rack up a large bill. **Not** an idempotent-ledger/billing-reconciliation-oracle/fail-closed-governor
  system — that machinery was sized for multi-tenant SaaS money-truth and is now overbuilt. FinOps scopes
  the right-sized version.
- **`<3.3>` Tenant isolation — N/A, not pending.** Single user (`<1.2>`); RLS/multi-tenant machinery does
  not apply. Deleted from scope, not deferred.
- **`<3.4>` The validation engine** (re-authored from "AI/ML engine" — this is **classical statistics /
  quant research, not generative AI**). What AI/ML (#21) actually builds: the walk-forward-CV backtest
  pipeline that tests each screener component against forward directional outcomes — the same kind of
  work the 4 completed equity studies already did (linear regression, log-transforms, LOO/5-fold CV,
  seed-sensitivity checks), now with a role split: AI/ML builds/runs it, **AIQ independently re-derives
  and audits each result before a component is called "cleared"** (builder ≠ judge, same spirit as the
  studies' existing "ships only if it clears CV" discipline, now structurally enforced by a second seat
  instead of one session self-checking). "Anti-fabrication grounding" (AIQ's kit mandate) maps to: no
  lookahead bias, no data leakage, a component doesn't ship on a fit-to-test number (LL-43).
  **The clearance bar (D-TRADE-021, ratified):** a component is **CLEARED** only if it beats naive
  baseline OOS under BOTH LOO-CV and 5-fold CV (≥30 seeds), **≥90% of seeds agreeing**; **NOT CLEARED**
  otherwise; **VOID** on any leakage/contamination finding regardless. Matches the short-interest
  study's own successful precedent exactly — not a new invention.
- **`<3.5>` Stack — 🔒 CONFIRMED per ADR-0001 R2 (Architect), Lead-ratified 2026-08-04 (D-TRADE-030,
  co-signed by AI/ML + AIQ).** **Python core; Node/Fastify/React dropped entirely** (N/A). Single package
  `helm/`, disjoint-by-directory: `helm/ingest` · `helm/universe` (**conditional — likely drops, P-3,
  Director to confirm**) · `helm/screener` (**RE-SCOPED: a thin feature-extraction adapter** over
  `tools/rolling_watchlist.py` — imports the scanner, never forks it) · `helm/validation/{engine,audit}` ·
  `helm/storage` · `helm/spend`. **`tools/rolling_watchlist.py` is now a SHARED library** — imported by
  both `helm/screener` and `tools/web/` (D-TRADE-023), a single source of truth, not ingested/forked. Full
  module ownership map + import-boundary rules: `docs/adr/ADR-0001-phase1-validation-tool.md` §4-5. Supabase
  (`zyscsnhiymitpfdhjuci`) retained **read-only** this phase. D-TRADE-017's Node/Docker absence does not
  bite a Python-only Phase 1.
- **`<3.6>` The validation label + contract — 🔒 CONFIRMED per ADR-0001 R2 (Architect), Lead-ratified
  2026-08-04 (D-TRADE-030) after a full protocol-17 CRITICAL-tier review (AI/ML + AIQ both co-signed the
  actual revised text, not a summary — 4 real objections found and fixed along the way, not a rubber
  stamp).** No options label — a **TWO-LEG contract**: **Leg A** (entry-signal validation) tests each not-
  yet-validated scanner component (the 8 pattern detectors + pivot/red-to-green trigger) as a trigger →
  forward stock return vs. naive, the studies' harness verbatim, verdict → the component's `_gates` flag.
  **Leg B** (exit-rule validation) compares realized trade return under the new **trailing-stop exit**
  (§6.3: `effective_stop(t) = max(P0·(1−init_stop_pct/100), peak(t)·(1−trail_pct/100))`, monotone
  non-decreasing by construction) vs. a naive **fixed-holding-period baseline** — holding period is
  endogenous, no DTE/horizon. Both legs use the unchanged D-TRADE-021 clearance bar and the unchanged NN-1
  no-lookahead invariant. **Four verdict states** (new): `CLEARED` / `DROPPED` / `VOID` / **`UNMEASURED`**
  (a component firing below the D-TRADE-029-ratified 30-event support floor — absence is not a judgment,
  the float-study precedent). **NN-10 (new, CRITICAL):** every data-derived label/baseline parameter
  (`trail_pct`, `init_stop_pct`, the Leg-B baseline `N`) is fit train-fold-only, never from test-fold
  outcomes — closes the specific leakage vector a trailing stop introduces. **Builder≠judge extended to
  the feature layer:** AIQ's audit lane may import neither the validation engine's outputs nor
  `helm/screener`'s feature frames — it re-derives directly from `tools/rolling_watchlist.py`'s raw
  primitives. **Anti-cherry-pick:** exactly one pre-registered trailing-stop grid cell is clearance-
  eligible; the rest are sensitivity-only, never a clearance claim. Full contract, all 10 oracle legs, and
  the complete A6a/A6b revision delta: `docs/adr/ADR-0001-phase1-validation-tool.md` §6/§8/§14.
  🔒 **RESOLVED (D-TRADE-036, 2026-08-30) — P-4 LOCKED, Director-authorized Lead defaults, NOT
  AIQ-cosigned.** **OP-1:** grid `trail_pct ∈ {5,8,12}%` × `init_stop_pct ∈ {2,3}%`; primary
  clearance-eligible cell = **trail=8%, init=3%**, remaining 5 cells sensitivity-only. **OP-2:** the
  studies' existing **1d/1w/1m** set (unchanged from the ADR's recommendation). **OP-3:** a fully
  pre-registered fixed **N=5 trading days** (horizon-matched to the 1w Leg-A window), with N=1/N=21 as
  fixed-N sensitivity only — the leakage-free-simplest option per ADR-0001 §10, not the train-fold-median
  alternative. This explicitly bypassed ADR-0001 §12's own stated AIQ co-sign expectation for these three
  numbers, at the Director's direct instruction — flagged, not hidden.

## 4 · Compliance / risk (bright-lines → armed gates, D-TRADE-006)
- **`<4.1>` No secret in repo/logs** — provider keys live in the secret store only (B5).
- **`<4.2>` Provider ToS-as-taint** — a provider SDK/host used outside its sanctioned module FAILS.
- **`<4.3>` Financial/SEC regulatory surface — substantially DE-RISKED (re-scoped, not closed).**
  "Regulated investment advice / licensable investment strategy" concerns generally attach to advising
  **others** for compensation — `<1.2>` (personal use only, no distribution) makes that very unlikely to
  apply. ▸ **NOT DECIDED — still needs a light confirmatory check** (a Legal seat, or the Director's own
  read, confirming personal-use trading tools don't trigger adviser registration) — this is a MUCH
  smaller task than the pre-build hard-blocker previously scoped for a SaaS, and does not need to gate
  Phase 1 build start. The un-oracle-able duty stays §10 HUMAN either way.

## 5 · Superseded (deleted, not parked — LL-19)
The prior SaaS framing (multi-tenant chokepoint, generative AI/ML signal engine judged for fabrication,
GTM/commercial roster, B9 Gauntlet, B7 CX design gates, tenant-isolation pillar) is removed from this
document. It does not describe HELM. If a future pivot toward commercial use ever happens, it is a new
elicitation, not a resurrection of this text.

**2026-08-04 — the options framing (D-TRADE-020's `<1.1>`) is also removed, not parked.** Directional
calls/puts, 0.40-delta targeting, 25–45 DTE windows, options-chain/IV-rank data, the liquid-optionable
large/mid-cap universe requirement, and the 0DTE-backtest-engine reuse plan for Phase 2 do not describe
HELM. If options re-enter scope in the future, that is a new elicitation, not a resurrection of this text.
