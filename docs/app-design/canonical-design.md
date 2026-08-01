# HELM — canonical design doc (the single source of truth)

Protocol 13: this is the ONE canonical design doc. **Only the Lead edits it.** Every other seat APPENDS
to `working-log.md`; the Lead absorbs. Reference design by its `<x.y>` id, never by re-describing it.
Open points are **first-class inline `▸ NOT DECIDED` markers** (who decides + a recommendation) — silence
must never read as decided (LL-31). Thin by design at founding (LL-33); it grows as decisions land.

## 1 · Product
- **`<1.1>` What HELM is — ▸ NOT DECIDED** (decides: **Director**; blocker for real feature design).
  *Lead's recommendation / strawman to react to:* "A SaaS that ingests **SEC EDGAR filings + market data**
  and produces **AI-assisted trading/analysis signals** for ShupeCapital." Replace or confirm; the roster,
  stack, providers and wave-3+ feature order all resolve off this.
- **`<1.2>` Primary users / value — ▸ NOT DECIDED** (decides: Director, with `<1.1>`).
- **`<1.3>` Cost model = billed per-use** (D-TRADE-004, 🔒-pending). Every billed provider call goes
  through the single metered chokepoint `<3.2>` and is capped by a fail-closed governor.

## 2 · Domain / data
- **`<2.1>` External providers — ▸ NOT DECIDED (full set)** (decides: Director; SecOps runs ToS-taint first).
  **SEC EDGAR is an in-hand asset:** the Director already holds a working SEC API key (`..\Trade\`, a
  stub repo — key gitignored, only its template committed). So EDGAR is the confirmed anchor provider;
  the open question is the *rest* of the set. *Recommendation for the remainder:* Polygon.io market data.
  **Key handling:** the real key NEVER enters this repo — it is installed to the secret store at B5
  (`<4.1>`); SecOps runs the EDGAR ToS-as-taint check before anything builds on it.
- **`<2.2>` Data ingestion (Data Engineer lane)** — EDGAR/market-data pull + normalization; shape
  designed after `<1.1>`/`<2.1>` land. ▸ NOT DECIDED (design pending).

## 3 · Architecture (planned; ADRs author the binding form at W1)
- **`<3.1>` Modular monolith**, compiler-enforced seams (B2 pillar ⑧); default stack per D-TRADE-003.
- **`<3.2>` The money-truth chokepoint** (Lane 2 / BE-Data) — the **single** metered path for billed
  provider calls; every call writes an append-only spend-ledger row, passes the fail-closed governor and
  a $/day self-tally auto-kill (D-TRADE-008, B4 L4). This is a one-way-door / high-invariant surface:
  its invariant checklist is locked (impl + QA + SecOps + FinOps) before W1 build.
- **`<3.3>` Tenant isolation** (B2 pillar ②) — RLS + threaded request-context; proof = a gate leg that
  FAILS with RLS OFF. Applies if HELM is multi-tenant. ▸ NOT DECIDED (single- vs multi-tenant — decides:
  Architect at W1, off `<1.1>`).
- **`<3.4>` AI/ML engine** — scoring/generation of signals; built by AI/ML, **judged by AIQ** (builder ≠
  judge); grounded-against-source, golden-eval gated before phase exit. Shape pending `<1.1>`.

## 4 · Compliance / risk (bright-lines → armed gates, D-TRADE-006)
- **`<4.1>` No secret in repo/logs** — SEC/market-data keys live in the secret store only (B5).
- **`<4.2>` Provider ToS-as-taint** — a provider SDK/host used outside its sanctioned module FAILS.
- **`<4.3>` Financial/SEC regulatory surface — ▸ NOT DECIDED** (decides: **Legal**, escalates to
  Director). Whether HELM outputs constitute regulated investment advice materially shapes scope; Legal
  scopes this before build. *This is exactly the un-oracle-able duty §10 keeps HUMAN.*

## 5 · Not-yet-scoped
Everything in waves W2+ derives from `<1.1>`. Until the product paragraph lands, no wave beyond **W0
scaffold** (which is product-agnostic) may be planned as build-ready.
