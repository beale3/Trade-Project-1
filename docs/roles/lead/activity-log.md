# Program Lead — activity log (context-handoff artifact)

The Lead's durable context. On any session handoff, the outgoing Lead writes its full state HERE FIRST
**and pushes it**; the incoming Lead clone **verifies this commit is on origin before resuming** (a clean
local tree ≠ a fetchable handoff — LL-14). All truth lives in the repo, never in a session's context.

🔒 **Re-authored 2026-08-01, end-of-session handoff** (LL-19 — the founding-day version below was
badly stale; re-authored wholesale, not patched alongside it).

## Identity
- **Role:** Program Lead / Orchestrator (the single seat that edits the canonical design doc; never
  self-dispatches a wave; runs the delivery pipeline). Model **Opus 4.8 · High**.
- **Owned clone:** `…\Trading Project 1\Trade - Lead`. This session has run from the umbrella parent dir,
  authoring into the clone by explicit path — the only session touching it (no one-session-per-clone
  breach, LL-2). **A fresh Lead session opened inside the clone itself should treat this log as truth
  and verify against the live repo before acting** (protocol 13a — repo wins on conflict).
- **Session title convention:** other seats verify the ACTIVE Lead by title + owned clone before routing
  a message (session IDs rotate — LL-36). Recommend the new session set its title to
  `HELM (trade) — Program Lead` if not already set.

## State as of 2026-08-01 (end of this session — read this section first)
- **Origin:** `https://github.com/beale3/Trade-Project-1` · branch `main` · **HEAD `9f938f9`** — verify
  your clone matches this exact hash before acting (LL-14); if behind, `git pull --rebase` first.
- **Kit:** v2.3.0, synced in `docs/foundation/kit/`.
- **The product pivoted hard, once, on 2026-08-01 (D-TRADE-020).** Founding `<1.1>` was a SaaS strawman;
  it is now LOCKED to something completely different: **a personal options-signal validation tool**, not
  a commercial product. Read `docs/app-design/canonical-design.md` in full — it was re-authored, not
  patched, and the old SaaS framing no longer describes anything real. Do not trust any pre-2026-08-01
  memory of this project's shape; it's wrong now.
- **What HELM actually is (Phase 1):** validate an existing, already-built options screener (composite
  trend/momentum/breakout/volume score → directional calls/puts near 0.40 delta, ~25–45 DTE) against a
  liquid-optionable-stock universe, via directional-correctness walk-forward CV — same discipline already
  proven across 4 completed equity studies on the Director's machine. Full design: `docs/adr/ADR-0001-
  phase1-validation-tool.md` (ratified as D-TRADE-022).
- **Two, and only two, things block HELM Phase-1 real build** (everything else the team resolved itself):
  - **P-1** — D-TRADE-010 (no-build) has never been explicitly re-scoped by the Director. My stage-plan.md
    recommendation (quant-research/design work falls outside its original intent) is flagged, not ruled.
    **Do not treat this as settled — ask, or wait for an explicit answer, before authorizing production
    pipeline code for Phase-1.**
  - **P-2** — the options-screener ZIP and the 0DTE-backtest-engine ZIP are confirmed **NOT on this
    machine** (I searched exhaustively — Downloads, Desktop, Documents, home root). They exist only in
    the Director's "Build A Stock Chart Algorithm" claude.ai Project and were never downloaded. AI/ML is
    holding on P1-2 (screener ingestion) until these are delivered.
- **A separate, actively in-progress side-project exists alongside HELM Phase-1:** `tools/
  rolling_watchlist.py` — the equity guardrail/S3/pump-and-dump scanner + trade simulator, brought into
  this repo (was un-versioned in Downloads) and wired to live Massive market data (D-TRADE-020 pivot
  side-effect). As of this session's end, the Director directed it be rebuilt as a **browser dashboard**
  (D-TRADE-023), reusing an already-approved "Rolling Watchlist" claude.ai mockup — **4 seats were just
  dispatched and have not yet reported back** (see "In-flight work" below). This is explicitly scoped
  separate from HELM Phase-1's own no-UI framing — don't conflate the two.
- **Two security incidents this session, both resolved, no leak reached GitHub either time:** a Massive
  API key was twice pasted into `massive_api_key.txt.template` (tracked, not gitignored) instead of
  `massive_api_key.txt` (gitignored) — caught before any commit both times via `git log -p` history
  checks. The template now has a loud "DO NOT PASTE HERE" warning. **If a key ever needs handling again,
  check `massive_api_key.txt.template`'s tracked content first** (`git diff HEAD -- <path>`) before
  assuming hygiene is fine.

## Decisions of record (see `docs/decisions-log.md` for full text + propagation — D-TRADE-001…023)
The load-bearing ones for a fresh Lead to know before doing anything:
- **D-TRADE-020** — the pivot (personal tool, not SaaS). Supersedes everything before it product-wise.
- **D-TRADE-021** — the ratified Phase-1 clearance bar: CLEARED only if a component beats naive baseline
  OOS under BOTH LOO-CV and 5-fold CV (≥30 seeds) with ≥90% seed agreement; VOID on any leakage finding.
- **D-TRADE-022** — ADR-0001 ratified: Python core, 5-lane recut (ingest/screener/validation-engine/
  validation-audit/infra), the directional-correctness label design.
- **D-TRADE-023** — the browser-UI dispatch for the equity side-tool (in progress, not yet delivered).

## Live board summary (full detail + Next-up per seat: `docs/AGENT-COORDINATION.md` §LIVE BOARD)
| Seat | State | What they're actually doing |
|---|---|---|
| Architect (Fable5·Max) | live | Delivered ADR-0001 (done, ratified). **New task just sent:** design the browser-UI backend/API contract — paces Designer/DevOps/AI-ML below. Not yet reported back. |
| SecOps | live | Delivered ToS-taint review + key denylist + B5 checklist. Re-scoped to a light personal-tier confirm; last known idle/holding. |
| SDE1 | live | Delivered pivot re-scope (data-ingestion framing). Holding on HELM Phase-1 (P-2 blocked); not tasked on the browser-UI work as of this handoff. |
| DevOps | live | Delivered the Python gate-harness re-author (design-only, held on file creation pending P-1). **New task just sent:** browser-UI web-server scaffolding — prepping, not yet reported back. |
| AI/ML | live, holding on HELM P1-2 | Delivered the validation-methodology draft; independently converged with Architect on the label design. **New task just sent (unblocked, separate from HELM hold):** wire `rolling_watchlist.py`'s functions as the browser-UI backend API. Not yet reported back. |
| AIQ | live, holding | Delivered the re-authored methodology doc + D-TRADE-021 ratification sync. Nothing to audit yet — no AI/ML CV result exists. |
| FinOps | live | Delivered the re-scoped personal spend-guard spec (governor-spec.md, cost-model.md). Idle/holding. |
| Designer | **just re-activated** (was stood down at D-TRADE-020, no UI surface existed) | **New task just sent:** adapt the real, already-fetched "Rolling Watchlist" mockup source to consume live data — see "In-flight work" below for the exact file path. Not yet reported back. |
| QA, GA, Legal, Data Engineer | never spawned | Real, unclaimed work exists for Data Engineer (universe construction) once HELM P-2 clears. QA/GA/Legal not yet needed. |

## In-flight work — pick this up first if you're the incoming session
**The browser-UI dashboard (D-TRADE-023) is mid-dispatch.** I sent 4 assignments this session and the
conversation ended (session handoff) before any of them reported back:
1. **Architect** — a short design note: backend framework choice, JSON API contract per dashboard
   section, module layout (likely `tools/web/`). **This is the pacing item** — Designer/DevOps/AI-ML are
   waiting on it.
2. **Designer** — adapt the real mockup source (fetched via WebFetch this session, saved locally at
   `C:\Users\beale\.claude\projects\C--Users-beale-Software-Dev\517ca982-2b50-41cb-ab85-4da846eb94f2\
   tool-results\artifact-7601fb84-1785090475-b26e.html`, 193KB — the ACTUAL HTML/CSS/JS of the Director's
   already-approved "Rolling Watchlist" dashboard, not a description) to consume live data instead of its
   baked-in mock data. Custom TradeSlab/TradeMono embedded fonts, `#faf9f5`/`#141413` color scheme,
   `tw-s3-*` class convention for the S3 breakdown. **Do not let anyone redesign this from scratch** —
   it's already Director-approved; this is integration work only.
3. **DevOps** — web-server scaffolding (Flask/FastAPI, TBD by Architect), dev-run tooling.
4. **AI/ML** — backend API layer wiring `rolling_watchlist.py`'s existing functions to JSON, per the
   Architect's contract.

**Next Lead action on resume:** check for reports from these 4 seats (they may have reported mid-session
via cross-session messages that need consolidating — protocol 15, ONE consolidated report, don't relay
each as it arrives) and continue driving this to a working dashboard.

## Standing Lead practices (unchanged since founding — protocol references in the charter)
- **Verify-don't-attest — including my own synthesis** (LL-34): re-derive each claim; a different seat
  audits any synthesis feeding a decision.
- **Recurring validation of my own output** (LL-64): route critical Lead-authored artifacts (like this
  log, or a canonical-doc edit) to GA/another seat before presenting as reconciled — GA is not yet
  spawned, so this hasn't been exercised in practice yet; worth doing once GA exists.
- **One report per piece of work, at completion** (LL-65): hold, consolidate, present once — don't relay
  each seat's finding onward as it arrives.
- **Never self-dispatch a wave; never unilaterally reinterpret an explicit Director ruling** (learned hard
  this session — see D-TRADE-010's history: I once said "spawn to build" prematurely and was corrected;
  since then, every "is this build authorized" question gets asked, not assumed).
- **Sync before every write:** `git pull --rebase` before editing AND before pushing. This session hit
  several real rebase/stash cycles from concurrent seat activity — normal, not a problem, just don't skip it.
- **When in doubt about a secret file's git status, check `git log -p` on that exact path** — don't trust
  that "gitignored" behavior is working without verifying (see the two Massive-key incidents above).

## Full log (chronological, this session)
### [Lead · 2026-08-01] Founding (Script 1 + Script 2)
Founded the team on Foundation Kit v2.2.0 → improved to v2.3.0 (LL-69/70/71 harvested). Scaffolded the
full governance spine against a SaaS strawman `<1.1>` (later completely superseded — see below). Seated
15 roster seats, authored the charter/decisions-log/gate-spec/oracle-boundary/stage-plan.

### [Lead · 2026-08-01] The pivot — D-TRADE-020
Director provided real context (a mature quant-research history: 4 completed equity backtests, an
options screener, a 0DTE backtest engine, a live daily trading routine). Ran a 3-round clarifying
elicitation (personal-vs-commercial → Phase-1 scope → universe → success metric → final lock). Re-
authored canonical-design.md, the charter roster/board/lane-cut, stage-plan, oracle-boundary, gate-spec —
all wholesale, not patched (LL-19). Notified all 8 then-live seats directly with their re-scoped mandate.

### [Lead · 2026-08-01] ADR-0001 + D-TRADE-021/022
Architect delivered a full Phase-1 design ADR (stack, module layout, lane recut, 9 oracle legs, the
directional-correctness label design) — independently converged with AI/ML on the label form before
either reported to me. Ratified AIQ's proposed CV clearance bar as D-TRADE-021 (Lead call, well-
precedented — matches the short-interest study's own successful methodology exactly). Absorbed ADR-0001
as D-TRADE-022. Confirmed via direct testing that Python 3.12 + all needed libraries were already
installed — the D-TRADE-017 toolchain blocker mostly evaporated for this stack.

### [Lead · 2026-08-01] Massive key wiring + two security incidents
Director asked to wire a new Massive data source into `rolling_watchlist (3).py`'s trade simulator.
Brought the script into the repo (`tools/rolling_watchlist.py`, was un-versioned in Downloads). Found and
resolved a real design conflict (the pre-existing `massive_loader.py` adapter assumed an MCP-tool+CSV
path the script doesn't support) before building — Director chose direct REST + a raw key instead.
**Twice**, the real key was pasted into the tracked `.template` file instead of the gitignored real file;
both times caught and fixed before any commit reached git history; hardened the template's instructions
after the second occurrence. Verified the full pipeline end-to-end against live data (real AAPL/NVDA
scan, real simulated trades). Fixed one unrelated pandas deprecation warning on request.

### [Lead · 2026-08-01] Browser-UI dispatch — D-TRADE-023 (session ends here, mid-flight)
Director asked to rebuild the equity-tool simulator as a browser UI instead of a desktop app, then
explicitly redirected me to dispatch this to the team rather than build it solo. Found and fetched the
Director's real, already-approved dashboard mockup source via WebFetch (a genuine, useful discovery — the
artifact was fetchable, not just describable). Recorded D-TRADE-023, re-activated the Designer seat, and
sent 4 concrete assignments (Architect, Designer, DevOps, AI/ML) — see "In-flight work" above. **None had
reported back when this handoff was written.** Director then requested this durable handoff + a clone
prompt, ending the session.

<!-- append new entries below -->
