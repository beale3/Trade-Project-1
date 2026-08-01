# Lead open-items ledger — HELM (`trade`)

🔒 **Re-authored 2026-08-01** (LL-19 — the founding-day version was entirely pre-pivot: SaaS-era
Node/Docker toolchain items, EDGAR/Legal questions superseded by D-TRADE-020's personal-tool framing,
and a W0 SaaS wave breakdown that no longer describes anything real. None of that carries forward.)

## A · Open Director decisions (present, then WAIT — LL-38)
| # | Item | Status |
|---|---|---|
| 1 | 🔴 **P-1 — D-TRADE-010 (no-build) re-scope.** Lead's stage-plan.md recommendation (Phase-1 quant-research/design work falls outside its original intent) is flagged, NOT ruled. | **The single most-asked-and-unanswered question this session.** Blocks all HELM Phase-1 production pipeline code. |
| 2 | 🔴 **P-2 — locate/deliver the options-screener + 0DTE-backtest-engine ZIPs.** Confirmed absent from this machine (exhaustive search); exist only in the Director's claude.ai Project. | Blocks AI/ML's P1-2 (screener ingestion) specifically. |
| 3 | 🟡 Provider/tier confirm (Massive personal tier, SEC-API.io key identity) — SecOps's task, light-touch now (not the heavy commercial gate it once was). | Not urgent, not blocking. |
| 4 | 🟡 `<4.3>` regulatory light-touch check — substantially de-risked (personal use), Legal not yet spawned. | Not urgent. |
| 5 | 🟡 Historical options-chain/IV data availability at the Massive tier in use — gates only the IV-rank component (ADR-0001 R-3, de-risked). | DevOps/Data-Eng discovery, in progress. |
| 6 | 🟡 Product name (`HELM` rebrand) | Any time, no urgency. |

**Everything else from founding (roster lock, cost-model lock, B9/B7 adoption, the old provider set,
toolchain installation) is either resolved by D-TRADE-020's pivot or dropped as N/A — see
`docs/foundation/PROJECT-CONFIG.md` §2–4 for the current, correct state of each.**

## B · Browser-UI dashboard (D-TRADE-023) — actively in progress, mid-dispatch
4 seats assigned (Architect → Designer/DevOps/AI-ML, Architect paces). **None had reported back as of
this ledger's last update.** Full detail: `docs/roles/lead/activity-log.md` "In-flight work". Next Lead
action: check for their reports, consolidate (don't relay each separately — LL-65), keep driving to a
working dashboard.

## C · Standing Lead practices (protocol references in the charter)
- **Verify-don't-attest — including my own synthesis** (protocol 15 ④ / LL-34): re-derive each claim; a
  different seat (GA, not yet spawned) audits any synthesis feeding a decision.
- **Recurring validation of my own output** (protocol 17 / LL-64): route critical Lead-authored artifacts
  to GA/eval before presenting as reconciled — not yet exercised in practice (GA doesn't exist yet).
- **One report per piece of work, at completion** (protocol 15 / LL-65): hold, consolidate, present once.
- **Never self-dispatch; never unilaterally reinterpret an explicit Director ruling** — learned hard this
  session via D-TRADE-010's own history (an early "spawn to build" framing was corrected by the Director;
  every "is this authorized" question since has been asked, not assumed).
- **Sync before every write:** `git pull --rebase` before AND after. Real, frequent concurrent-seat
  activity this session — normal, expected, not a problem.
- **Secret-file hygiene:** don't trust "gitignored" without verifying — `git log -p -- <path>` before
  assuming a secret-adjacent file's history is clean (two real incidents this session, both caught).

## D · W0 (HELM Phase-1 first build wave) — planned only, NOT authorized (D-TRADE-010, P-1 above)
The old SaaS-era W0 breakdown (Node/pnpm/Docker monorepo scaffold) is **deleted, not parked** (LL-19) —
it described a stack this project no longer uses. The current Phase-1 breakdown lives in
`docs/app-design/stage-plan.md` (P1-0 through P1-5), which is the authoritative, current plan. P1-0
(the Architect's design ADR) is done (ADR-0001, ratified as D-TRADE-022). **Nothing beyond design/
planning proceeds until P-1 clears.**
