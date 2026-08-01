# Program Lead — activity log (context-handoff artifact)

The Lead's durable context. On any session handoff, the outgoing Lead writes its full state HERE FIRST
**and pushes it**; the incoming Lead clone **verifies this commit is on origin before resuming** (a clean
local tree ≠ a fetchable handoff — LL-14). All truth lives in the repo, never in a session's context.

## Identity
- **Role:** Program Lead / Orchestrator (the single seat that edits the canonical design doc; never
  self-dispatches a wave). Model **Opus 4.8 · High**.
- **Live session:** this session **IS the active Lead** as of 2026-08-01. Recommended session title
  (set in the client): **`HELM (trade) — Program Lead`**. Seats verify the ACTIVE Lead via that title +
  the `Trade - Lead` clone before routing a message (session IDs rotate — LL-36).
- **Owned clone:** `…\Trading Project 1\Trade - Lead`. NOTE: this founding session has been running from
  the umbrella parent dir and authoring into the clone by explicit path (it is the only session touching
  the clone, so no one-session-per-clone breach — LL-2). When a dedicated Lead session is opened *inside*
  the clone, this session hands off via this log.

## State as of 2026-08-01 (founding complete)
- **Phase:** FOUNDATION ONLY — no code build / no wave dispatch authorized (D-TRADE-010).
- **Repo:** LIVE on origin `https://github.com/beale3/Trade-Project-1` · branch `main` · HEAD `3d3f1aa`
  (Director pushed 2026-08-01; verified 55 docs/ files + full kit on origin, SEC key not leaked). The
  placeholder `c79ceb5` is a preserved ancestor. Seats sync via `git pull --rebase`.
- **Kit:** improved to **v2.3.0** (LL-69/70/71), committed to the canonical stand-in `Software Dev\Foundation
  Kit` (`1df25ed`) and synced into `docs/foundation/kit/`.
- **Decisions:** `D-TRADE-001…011` (see decisions-log). 011 = Design Lead seated.
- **Seats:** 15 defined; **none spawned yet** except the Designer prompt is ready (holds — no product).
- **Blockers to everything downstream:** product paragraph `<1.1>` (NOT DECIDED) + the two locks (cost
  model, roster) awaiting explicit Director confirmation (LL-38).

## Open Lead actions (see docs/roles/lead/open-items-ledger.md §A)
- Await Director: product `<1.1>` · confirm 🔒 cost + 🔒 roster · providers · B9 run/skip · remote creation.
- No dispatch, no spend, no self-directed build. Present-then-WAIT on every lock.

## Log
### [Lead · 2026-08-01] Registered as the live Lead
- Director directed "set yourself as the Lead." Claimed the live board row; seeded this activity-log as the
  handoff artifact. No machine session-ID available (the session MCP rejects self-reference); identity is
  carried by the session title + owned clone.

<!-- append new entries below -->
