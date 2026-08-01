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
- **`<2.1>` External providers — ▸ NOT DECIDED (full set) · SecOps ToS-taint DONE** (decides: Director +
  Legal `<4.3>`; source `docs/security/tos-taint-review.md`, D-TRADE-018). The taint review changes the
  provider picture materially:
  - **SEC EDGAR — LOW taint** (data is public-domain/redistributable) but HARD ops constraints: 10 req/s,
    declared User-Agent required (public EDGAR is **keyless/UA-based**). ⚠️ The in-hand 77-byte "SEC API
    key" is therefore **NOT public EDGAR** — likely a third-party reseller whose ToS re-opens the taint.
    **▸ NOT DECIDED — the key issuer must be confirmed** (Director / Data-Eng) before the EDGAR-LOW verdict holds.
  - **Polygon.io / "Massive" — HIGH taint 🟠 (SEV2-candidate).** Entity rebranded Polygon.io→Massive
    (eff 2025-10-30). The default/individual Market Data ToS is **non-commercial, Non-Professional,
    display-only, no redistribution, no "investment strategy" derivative works — INCOMPATIBLE with the
    strawman `<1.1>` on four counts.** Business tier permits redistribution but still bars unlicensed
    derivative works; real-time drags in OPRA/UTP/NYSE agreements + pro fees. **▸ NOT DECIDED — needs a
    Director provider/tier decision AND a Legal `<4.3>` ruling before it can be `<2.1>`.**
  - **Supabase — MEDIUM.** We own our data (no IP taint); binding duty = customer bears ALL credential
    security → service_role + DB pwd are B5/server-only (leg T). Read-only single-project MCP is correct
    least-privilege. Data-class lines (no PHI w/o BAA, no cardholder data w/o approval) → Legal if the
    model ever touches them (billing may).
  - **Key handling:** real keys NEVER enter this repo — B5 secret store (`<4.1>`).
  *Near-term recommendation (SecOps):* EDGAR-only (public-domain filings/fundamentals) de-risks the
  licensing wall; add licensed market-data (Business tier) only once `<1.1>` + `<4.3>` justify the cost.
- **`<2.2>` Data ingestion (Data Engineer lane)** — EDGAR/market-data pull + normalization; shape
  designed after `<1.1>`/`<2.1>` land. ▸ NOT DECIDED (design pending).

## 3 · Architecture (planned; ADRs author the binding form at W1)
- **`<3.1>` Modular monolith**, compiler-enforced seams (B2 pillar ⑧); default stack per D-TRADE-003.
- **`<3.2>` The money-truth chokepoint** (Lane 2 / BE-Data) — the **single** metered path for billed
  provider calls; every call writes an append-only spend-ledger row, passes the fail-closed governor and
  a $/day self-tally auto-kill (D-TRADE-008, B4 L4). This is a one-way-door / high-invariant surface:
  its invariant checklist is locked (impl + QA + SecOps + FinOps) before W1 build.
  **Cost shape (D-TRADE-019, FinOps):** only **LLM tokens are true per-use variable COGS**; market-data
  (flat sub) and EDGAR (free, *if* the key issuer is confirmed public) are $0-marginal — the `$/day`
  auto-kill is effectively an LLM-token meter, but every provider call still routes through the
  chokepoint and ledgers (rate/ToS governance, not just cost). Per-signal COGS is unmeasured until
  AI/ML has a real token trace — caps start tight, widen on evidence.
- **`<3.3>` Tenant isolation** (B2 pillar ②) — RLS + threaded request-context; proof = a gate leg that
  FAILS with RLS OFF. Applies if HELM is multi-tenant. ▸ NOT DECIDED (single- vs multi-tenant — decides:
  Architect at W1, off `<1.1>`).
- **`<3.4>` AI/ML engine** — scoring/generation of signals; built by AI/ML, **judged by AIQ** (builder ≠
  judge); grounded-against-source, golden-eval gated before phase exit. Shape pending `<1.1>`.

## 4 · Compliance / risk (bright-lines → armed gates, D-TRADE-006)
- **`<4.1>` No secret in repo/logs** — SEC/market-data keys live in the secret store only (B5).
- **`<4.2>` Provider ToS-as-taint** — a provider SDK/host used outside its sanctioned module FAILS.
- **`<4.3>` Financial/SEC regulatory surface — ▸ NOT DECIDED · now a HARD pre-build gate** (decides:
  **Legal**, escalates to Director). Whether HELM's AI signals constitute **regulated investment advice /
  a licensable investment strategy** materially shapes scope — and SecOps's `<2.1>` finding makes it
  load-bearing NOW: the market-data licensing tier (Polygon/Massive) turns on whether HELM's output is a
  "derivative work / investment strategy." **Legal must rule this before `<2.1>`/`<1.1>` lock or any
  build.** Legal & Privacy is **not yet spawned** — spawning it is on the critical path. *The un-oracle-able
  duty §10 keeps HUMAN.*

## 5 · Not-yet-scoped
Everything in waves W2+ derives from `<1.1>`. Until the product paragraph lands, no wave beyond **W0
scaffold** (which is product-agnostic) may be planned as build-ready.
