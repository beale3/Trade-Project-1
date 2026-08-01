# HELM — canonical design doc (the single source of truth)

Protocol 13: this is the ONE canonical design doc. **Only the Lead edits it.** Every other seat APPENDS
to `working-log.md`; the Lead absorbs. Reference design by its `<x.y>` id, never by re-describing it.
Open points are **first-class inline `▸ NOT DECIDED` markers** (who decides + a recommendation) — silence
must never read as decided (LL-31).

> **2026-08-01 — MAJOR REVISION.** `<1.1>` locked (Director, 3-round elicitation). This re-authors §1–4
> rather than patching alongside the superseded SaaS strawman (LL-19 — a doc saying two contradictory
> things is worse than one that's simply wrong). Superseded framing (multi-tenant SaaS, money-truth
> chokepoint at SaaS scale, generative-AI signal engine) is **deleted**, not parked — see LL-19/protocol 19.

## 1 · Product
- **`<1.1>` What HELM is — 🔒 LOCKED (Director, 2026-08-01).** HELM is a **personal trading-signal tool**
  (not a commercial product) that formalizes and empirically validates an **existing, already-built
  options screener**. The screener runs a rules-based composite technical score — trend (moving-average
  stack), momentum (RSI/MACD), breakout (52-week high/low, Bollinger %B), volume conviction, with an
  overextension dampener — against a universe of **liquid, optionable large/mid-cap stocks** (S&P
  500/1500 or Russell 1000-class names with real options chains and tight spreads — a deliberate
  departure from the sub-$20 momentum cohort used in the earlier equity studies), and recommends
  **directional calls/puts near 0.40 delta at ~25–45 DTE**.
  **Phase 1's job is validation, not invention:** apply the same walk-forward-CV, ships-only-if-it-
  clears-the-bar discipline already proven across 4 completed equity studies (regime → null, catalyst →
  null, short-interest → real but modest, float → no-go) to each of the screener's scoring components,
  testing whether it predicts the underlying moving far enough in the right direction within the
  option's DTE window (**directional correctness**, Director's explicit choice — NOT full option P&L;
  a deliberate, known limitation: doesn't capture theta decay/IV crush/slippage, the exact trap the
  Director's own 0DTE backtest already surfaced once — see `<1.4>`).
  Delivered as a **Python tool in this durable, versioned repo** — replacing the current routine, which
  lives in an ephemeral claude.ai Project sandbox and has already lost at least one script
  (`day_trade_toolkit.py`) to a sandbox reset.
- **`<1.2>` Primary user** — the Director, personally, for personal trading decisions. No other users,
  no distribution, no monetization. This is load-bearing for `<3.x>`/`<4.x>` below (no multi-tenant
  surface; no "regulated advice to others" question).
- **`<1.3>` Cost model = billed per-use** (D-TRADE-004), but at **personal scale** — a spend GUARD
  (cap + visibility), not a SaaS-grade metered-chokepoint/billing-reconciliation system. See `<3.2>`.
- **`<1.4>` Phase 2 (explicitly DEFERRED, not dropped):** (a) full option-P&L backtest simulation
  (entry, realistic slippage, a defined exit rule — reusing the 0DTE backtest engine's slippage/spread
  modeling) for any component that clears the Phase 1 directional-correctness bar; (b) a from-scratch
  predictive breakout-occurrence model (the original "Core Pipeline" ask — broader data, engineered
  features, a trained classifier, walk-forward backtest). Neither is in scope now.

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
  - **SEC-API.io** — the likely real identity of the in-hand `..\Trade\sec_api_key.txt` (float study
    used "SEC-API.io, account set up by the user," same week). ▸ **NOT DECIDED — confirm this key IS the
    SEC-API.io key** (Director/Data-Eng); if so it is a paid personal-tier subscription ($49–239/mo), not
    free public EDGAR — reframe cost/taint accordingly.
  - **Historical options-chain data (strikes, greeks/IV history)** — required for Phase 1 backtesting
    and **not yet confirmed available** from Massive at the tier in use. ▸ **NOT DECIDED — technical
    discovery, DevOps/Data-Eng**, not a Director call.
  - **Key handling:** real keys NEVER enter this repo — secret store only (`<4.1>`).
- **`<2.2>` Universe construction (Data Engineer lane)** — a maintained list of liquid, optionable
  large/mid-cap names (S&P 500/1500 or Russell 1000-class) with real options chains + tight spreads;
  shape TBD by Data-Eng, informed by the options screener's existing OI/volume/bid-ask filters.

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
- **`<3.5>` Stack — ▸ NOT DECIDED, reopened.** The kit default (Node/TS · Fastify · Postgres/Supabase ·
  React/Vite) was scoped for a SaaS. This is a **Python quant-research tool** — the existing screener,
  backtest engine, and all 4 studies' analysis scripts are Python (pandas/numpy/scipy). Recommend:
  **Python for the analysis/backtest/screener core**; Supabase (already connected) retained as the
  durable store for scan history/signals/backtest results (a real, useful role, not a SaaS OLTP). Node/
  Fastify/React likely drop entirely — no web frontend is needed for "a Python script/tool I can run."

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
