# Stage plan — HELM (`trade`) · GREENFIELD (D-TRADE-002)

Wave template = greenfield (§7). **Phase-gate between waves; parallelize only the disjoint-by-lane.** Each
wave is bracketed by a **Wave-Entry Gate** (Lead authors plan → oversight reviews → **Director GO**) and a
**QA phase-exit sign-off** before the next unblocks. The Lead never self-dispatches. **This document plans;
it does not build.**

## Pre-build order (before any wave): B9 → (B7 if adopted) → waves
- **B9 · Validation Gauntlet (G1–G8)** — 🟡 DIRECTOR-PENDING, recommended RUN. Nothing designs/builds
  until the opportunity clears viability + a signed blueprint (the only door into the build org). Needs the
  product paragraph `<1.1>`. Run as a cohort if several opportunities exist; the Skeptic mounts a kill
  attempt at each gate (→ Director). **If skipped, the Director records the skip explicitly.**
- **B7 · Design DP-1→DP-4** — only if the product proves CX-heavy (pending). If adopted, nothing builds
  (scaffold green but INERT) until all four pass + a Director build-GO.

## Waves
### W0 · Scaffold — *product-agnostic; can start once code lanes + DevOps are spawned + Director GOes*
Skeleton + DB day-one + the gate green on an empty app. **Does NOT depend on the pending product locks.**
- DevOps: monorepo tree (`apps/api`, `apps/web`, `packages/{domain,db,contracts,config}`), local DB,
  gate harness (legs SKIP-visible), CI (secret-scan + dep-audit), import-boundary lint encoding the 4-lane
  cut, `.claude/settings.json` placed by the Director from the template.
- **Validate ports/DB immediately here and write them back into `gate-spec.md` + the charter** (LL-1).
- **Arms:** B3 lint/import-boundary · B4 L1–L3 (provider-taint static) · leg K (secret-scan) · leg T (static).
- **Exit:** `tsc`/build/CI green on the empty app; every other leg exit-visible SKIP; QA sign-off.

### W1 · Core spine — *gated behind the product/cost/roster locks + Architect A0 ADR*
Transport + request-context/tenant + auth + DB adapter + `{ok,data|error}` envelope + job spine + **the
money-truth chokepoint `<3.2>`** (the one-way-door surface — invariant checklist locked by impl+QA+SecOps+
FinOps before build, D-TRADE-008).
- **Arms:** B2 pillars ①②④⑥⑧ (the 5 one-way doors) · B4 **L4 runtime money-truth** (leg M) · migrate+RLS
  lint (legs 4/6) · transport smoke (leg 5, port now validated) · FinOps fail-closed governor.
- **Exit:** all W1 legs armed + negative-controls shown to bite; QA phase-exit; A6 ASR before merge.

### W2 · Client shell — *behind W1*
`apps/web` router/shell/API-client facade + auth screens. **Arms:** a11y lint, perf budget. No business
logic in components (import-boundary leg enforces).

### W3+ · Features — *derived from `canonical-design <1.1>`; disjoint-by-lane; phase-gated*
The EDGAR/market-data ingestion (Data-Eng) + the AI/ML signal engine (built by AI/ML, **judged by AIQ**,
golden-eval + grounding gated) + the feature surfaces. **Order is NOT DECIDED until `<1.1>` lands** — no
W3+ wave is build-ready before the product paragraph is confirmed.

### Launch · B10 Operational-Readiness
Hazard/assurance register (every row carries a test-id, build fails without one) · versioned+published
SOPs (frozen dated PDFs) · immutable CI change-log · B5 key & secrets Director approval (HARD blocker).

## Phase-gate discipline
No wave builds until its Wave Plan is oversight-reviewed + Director-GO (B6); QA re-runs the full gate on
each phase HEAD in its own clone before the next unblocks; idle lanes do dispatch-freshness read-in before
writing; post-build A6 declares what changed.
