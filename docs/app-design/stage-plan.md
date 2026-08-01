# Stage plan — HELM (`trade`) · personal options-signal validation tool

🔒 **Revised 2026-08-01 — D-TRADE-020.** Supersedes the greenfield-SaaS wave template (§7 of the kit
does not fit a single personal Python project) — re-authored, not patched (LL-19). Two phases, per
canonical `<1.1>`/`<1.4>`: **Phase 1 = validate** the existing options screener. **Phase 2 = deferred**
(full option-P&L simulation; a from-scratch predictive occurrence model).

🟡 **D-TRADE-010 (no-build) — Lead's recommended reading, NOT yet re-ruled by the Director.** D-TRADE-010
was an explicit Director correction of the Lead's own premature "spawn to build" framing; reinterpreting
it is the Director's call, not the Lead's to assert. **Recommendation:** Phase-1 quant-research work
(backtest scripts, data pipelines — no external side effects, modest API calls of the same kind already
run throughout the prior research) plausibly falls outside what D-TRADE-010 meant to block (app/service
code against an undefined product) — but this is flagged as a recommendation pending explicit Director
confirmation, not treated as decided. **A wave-entry gate still applies regardless**: the Architect's
Phase-1 design ADR (module boundaries, stack details) is authored and the Director GOes it before any
broad build starts.

## Phase 1 — Validate the existing options screener
**Inputs to ingest (real, external artifacts, not built from scratch):**
- `Downloads/rolling_watchlist (3).py` — the guardrail/S3/PND scanner (equity side; reference for the
  proven backtest methodology, not the Phase-1 subject itself)
- The options screener (delivered as a ZIP; composite -100..+100 score → calls/puts near 0.40 delta)
- The 0DTE backtest engine (ZIP; real options-pricing/slippage modeling — reusable infrastructure)
- 4 completed equity studies (`C:\Users\beale\{regime,catalyst,short-interest,float}-study\`) — the
  proven walk-forward-CV / ships-only-if-it-clears methodology this phase re-applies

**P1-0 · Design ADR (Architect) — ✅ DELIVERED** (`docs/adr/ADR-0001-phase1-validation-tool.md`, status
PROPOSED, D-TRADE-022 ratified stack/lanes/label-form). Module layout, `<3.5>`/`<3.6>` confirmed, 9
non-negotiable oracle legs (`docs/gate/oracle-boundary.md`). **Design is done; build dispatch still
needs the 5 hard preconditions below** — none of them is the Architect's or the Lead's to waive.

**🔴 Preconditions to build dispatch (ADR-0001 §9 — HARD, checked before any wave-entry GO):**
| # | Precondition | Status | Owner |
|---|---|---|---|
| P-1 | D-TRADE-010 re-scope — Director confirms Phase-1 quant-research work is outside its intent | 🟡 **open — Director** | Director |
| P-2 | Locate + deliver the options-screener + 0DTE-backtest-engine ZIPs (confirmed absent from this machine — they exist only in the claude.ai Project sandbox) | 🟡 **open — Director** | Director |
| P-3 | Historical options-chain/IV data availability at the Massive tier in use — gates the IV-rank component only (de-risked from gating the whole label, per the OHLCV-only design) | 🟡 open | DevOps/Data-Eng discovery |
| P-4 | The CV clearance bar is **already ratified** (D-TRADE-021) — narrowed to ratifying the directional-correctness label FORM (ADR OP-1), which D-TRADE-021 didn't fix | 🟢 mostly resolved — Architect+AI/ML+AIQ converged, Lead-ratified as D-TRADE-022 | Lead (done) |
| P-5 | B5 secret approval before any live-key use | 🟡 open, not urgent | Director |

**Only P-1 and P-2 are genuinely blocking and Director-only** — everything else the team has resolved
or is actively working. **Design/planning work proceeds regardless of P-1/P-2**; no seat writes
production pipeline code until P-1 clears.

**P1-1 · Universe construction (Data Engineer)** — build/maintain the liquid-optionable large/mid-cap
list (S&P 500/1500 or Russell 1000-class, real options chains, tight spreads); confirm historical
options-chain data availability from Massive at the tier in use.

**P1-2 · Ingest + adapt the screener (AI/ML)** — bring the composite-score logic into this repo; wire
it to the new universe (§P1-1) instead of an arbitrary user-supplied watchlist.

**P1-3 · The validation engine (AI/ML builds, AIQ independently audits)** — for each screener component
(trend/momentum/breakout/volume/IV-rank), walk-forward-CV test: does it predict the underlying moving
far enough in the right direction within the option's ~25–45 DTE window (directional correctness, per
`<1.1>`), beating a naive baseline out-of-sample? Same discipline as the 4 studies (pre-registered bar,
LOO + 5-fold, seed-sensitivity check before trusting a marginal result — LL-42/43/44/47). **AIQ
independently re-derives every result before it's called "cleared"** — builder ≠ judge, structurally
enforced (an improvement over the studies' single-session self-check).

**P1-4 · Data + spend infra (SDE1, DevOps)** — Supabase persistence for scan history/backtest results;
a lightweight spend guard (`<3.2>`) on Massive/SEC-API.io calls; repo/CI scaffold for the Python project.

**P1-5 · SecOps light-touch confirm** — Massive + SEC-API.io accounts are on the personal/individual
tier and usage stays within it (already very plausible per `<2.1>`, not a hard gate).

**P1 exit:** each screener component is labeled cleared/dropped exactly like short-interest (kept) vs.
regime/catalyst (dropped) in the equity studies, with a written finding — the tool ships with the
components that actually work, same as the existing scanner's `_gates` flags.

## Phase 2 — Deferred (explicitly, not dropped — `<1.4>`)
- **P2-A** Full option-P&L backtest simulation (entry, realistic slippage, a defined exit rule) for any
  component that clears Phase 1's directional-correctness bar — reuses the 0DTE backtest engine.
- **P2-B** A from-scratch predictive breakout-occurrence model (the original "Core Pipeline": broad-
  universe historical data, engineered features, a trained classifier, walk-forward backtest) — bigger,
  riskier, deferred until Phase 1 proves out the validation discipline on a concrete, bounded problem.

## What's explicitly out of scope (dropped, not deferred)
Multi-tenant isolation · the money-truth chokepoint at SaaS scale (B4) · CX design gates (B7) · the
Validation Gauntlet (B9, no market to validate) · a GTM/commercial roster. See PROJECT-CONFIG §3/§4.
