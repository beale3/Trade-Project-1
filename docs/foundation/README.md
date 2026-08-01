# Director operating guide — HELM (`trade`)

🔒 **Re-authored 2026-08-01** — the founding-day version described a SaaS project that no longer exists
(D-TRADE-020 pivoted `<1.1>` to a personal options-signal validation tool; LL-19, re-authored not patched).

## 1 · Open decisions (present, then WAIT — LL-38)
| # | Decision | Status |
|---|---|---|
| 1 | 🔴 **D-TRADE-010 re-scope** — does Phase-1 quant-research/design work count as authorized, or does the Lead's "no build" hold still apply? | **Open, asked repeatedly this session, still unanswered.** Blocks HELM Phase-1 production code. |
| 2 | 🔴 **Deliver the options-screener + 0DTE-backtest-engine ZIPs** — confirmed not on this machine; live only in your "Build A Stock Chart Algorithm" claude.ai Project. | Blocks AI/ML's screener-ingestion task specifically. |
| 3 | 🟡 Provider tier confirm, `<4.3>` light legal check, options-chain data availability | Not urgent, in progress via the team |

**Everything else from founding** (product definition, cost model, roster, B9/B7, providers, isolation) is
**resolved** — see `canonical-design.md` and `PROJECT-CONFIG.md` for the current, correct state. Do not
act on the old table that used to be here; it described a different project.

## 2 · What's actually happening right now
- **HELM Phase-1** (validate the options screener): design is done (`ADR-0001`, ratified). Blocked on the
  two items above.
- **A separate, real side-project**: `tools/rolling_watchlist.py` (the equity guardrail/S3/pump-and-dump
  scanner + trade simulator) is live in this repo, wired to real Massive market data. You directed it be
  rebuilt as a **browser dashboard** (D-TRADE-023), reusing your already-approved "Rolling Watchlist"
  mockup — **4 seats are working on this now** (Architect designing the API contract; Designer, DevOps,
  AI/ML building against it once it lands).

## 3 · Human-only steps (unchanged from founding, still accurate)
1. Session defaults: `docs/foundation/settings.json.template` → `.claude/settings.json` if not already done.
2. **You are the only one who spawns sessions and approves spend.**
3. **Approve each Wave-Entry GO** for HELM Phase-1 build — the Lead authors the plan, oversight reviews,
   you say GO. The Lead never self-dispatches.
4. Answer the two open items in §1 whenever convenient — nothing breaks if you don't; the team keeps
   working on what it can (the browser-UI dashboard, light provider/legal confirms) in the meantime.

## 4 · What's where (current)
`PROJECT-CONFIG.md` (config of record, current) · `../AGENT-COORDINATION.md` (charter — roster, live
board, protocols) · `../decisions-log.md` (D-TRADE-001…023, read from 020 forward for the current shape)
· `../app-design/canonical-design.md` (the product, current — re-authored at the pivot) ·
`../app-design/stage-plan.md` (Phase 1/2 plan) · `../adr/ADR-0001-phase1-validation-tool.md` (the Phase-1
design) · `../gate/{gate-spec,oracle-boundary}.md` (current, re-scoped) · `../roles/lead/activity-log.md`
(**the fullest current status — read this first if you want the real picture**) ·
`../roles/lead/open-items-ledger.md` (current open items) · `role-bootstrap-scripts.md` (mostly stale —
pre-pivot seat prompts; seats already spawned don't need these re-run) · `kit/` (v2.3.0).
