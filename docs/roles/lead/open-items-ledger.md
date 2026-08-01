# Lead open-items ledger — HELM (`trade`)

Open Director decisions, first-wave prep, and the Lead's standing practices. Status per §4.5.

## A · Open Director decisions (present, then WAIT — LL-38)
| # | Item | Recommended default (scaffolded against) | Kind |
|---|---|---|---|
| 1 | 🔴 **Product paragraph `<1.1>`** | strawman: EDGAR + market-data → AI trading signals | blocker for real design |
| 2 | 🔒 **Cost model** = BILLED PER-USE (D-TRADE-004) | arm FinOps + B4 | LOCK — needs explicit yes |
| 3 | 🔒 **Roster** = 14 seats (D-TRADE-005) | core spine + AI/ML·AIQ·FinOps·Legal·Data-Eng | LOCK — needs explicit yes |
| 4 | 🟡 **Providers `<2.1>`** | SEC EDGAR + Polygon.io | pending; SecOps ToS-taint first |
| 5 | 🟡 **B9 Gauntlet run/skip** | RUN before design/build | pending; needs `<1.1>` |
| 6 | 🟡 **B7 (CX-heavy?)** | off unless product is CX-heavy | pending |
| 7 | 🟡 **Stack Python-lane** (D-TRADE-003) | Node/TS only unless quant-heavy | reopen before W1 |
| 8 | 🟡 **Product name** (rebrand `HELM`) | parked codename | any time |
| 9 | 🟡 **Remote + isolation rule** | create `beale3/Trade-Project-1`; adopt kit-crosses/content-doesn't | Director creates remote (gh) |

## B · First-wave prep (W0 scaffold — planned only; ⏸ NOT AUTHORIZED, D-TRADE-010)
See `docs/app-design/stage-plan.md` §W0 and the §D breakdown below. **We are not building any code yet.**
W0 is retained as the documented first wave for when a build-GO eventually lands; it is **not** a start-now
step and needs no seat spawned. The actual near-term path is product definition → B9 (if run) → build-GO.

## C · Standing Lead practices (protocol references in the charter)
- **Verify-don't-attest — including my own synthesis** (protocol 15 ④ / LL-34): re-derive each claim; a
  different seat (GA) audits any synthesis feeding a decision.
- **Recurring validation of my own output** (protocol 17 / LL-64): route critical Lead-authored artifacts
  to GA/eval before presenting as reconciled.
- **One report per piece of work, at completion** (protocol 15 / LL-65): hold, consolidate, present once.
- **Dispatch-freshness**: an idle lane pulls + re-reads charter/decisions/ADR before writing.
- **Re-verify-at-action-time**; **message-at-holds**; **assign-by-message to verified-ACTIVE sessions**
  (LL-36); **no background subagents** (LL-37).
- **Never self-dispatch a wave** — author the plan, oversight reviews, the Director says GO.
- **Save a revert net before any governance change** (LL-28).

## D · W0 first-wave breakdown (DRAFT — reference only; ⏸ NOT AUTHORIZED, D-TRADE-010)
Kept as the disjoint-by-file plan for when a build-GO eventually lands. **Not dispatchable now** — we are
not building any code yet. When authorized, W0 is product-agnostic (skeleton + DB day-one + gate green on
empty app). The Lead never self-dispatches; oversight reviews and the Director GOes.

| Task | Owner | Write-paths (disjoint) | adr_ref | DoD |
|---|---|---|---|---|
| W0-1 monorepo tree + workspaces | DevOps | root `package.json`, `pnpm-workspace.yaml`, `tsconfig*`, `apps/`,`packages/` skeleton | BYPASS (scaffold) | `tsc`/build green on empty app |
| W0-2 local DB stack + baseline migration | DevOps→BE-Data | `docker-compose.yml`, `packages/db/migrations/0001_*` | ADR at W1 for schema | DB boots; migrate runs clean |
| W0-3 gate harness (legs SKIP-visible) + CI | DevOps | `scripts/gate/**`, `.github/workflows/**` | BYPASS (scaffold) | gate exits clean on empty; **a planted boundary violation makes it FAIL** (LL-48) |
| W0-4 import-boundary lint = the 4-lane cut as code | DevOps | `.eslintrc*` / boundary config | BYPASS (scaffold) | a cross-lane import FAILS |
| W0-5 secret-scan (leg K) + provider-taint static (leg T) | DevOps←SecOps denylist | CI secret-scan config, taint rule | — | planted fake key / provider import → RED |
| W0-6 validate real ports/DB, write back to gate-spec + charter | DevOps→Lead | `docs/gate/gate-spec.md`, `docs/AGENT-COORDINATION.md §1` | — | validated values replace the "planned/NOT validated" rows (LL-1) |
| W0-7 place `.claude/settings.json` | **Director** (human-only) | `.claude/settings.json` from the template | — | acceptEdits active |

**Exit:** `tsc`/build/CI green on the empty app; every other leg exit-visible SKIP; QA phase-exit sign-off;
then W1 unblocks **only after** the cost/roster locks + product paragraph land and the Architect's W1 A0 ADR.
