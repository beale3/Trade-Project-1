# Gate spec — HELM (`trade`)

One runner, ordered, **exit-code-honest** (assert exit codes, never piped tails). Every leg is either
**ARMED** — proven to FAIL on a planted negative control — or an **exit-visible SKIP** until its surface
exists. A gate that cannot fail is worse than no gate (LL-48). Standing pre-authorization to **add** armed
legs (log the leg + count in the decisions-log); only a change to the *meaning of green* needs a decision.
Greenfield: **almost every leg is SKIP until W0** creates the tree; each arms at the wave named below.

## Stack commands (D-TRADE-003 · Node/TS · Fastify · Postgres/Supabase · React/Vite)
| # | Leg | Command (planned) | Arms at | Now |
|---|---|---|---|---|
| 1 | typecheck | `tsc --noEmit` (all workspaces) | W0 | ⏸ SKIP (no tree) |
| 2 | build | workspace build | W0 | ⏸ SKIP |
| 3 | test / eval golden set | `npm test` + AI golden-eval set | spine / AI phase | ⏸ SKIP |
| 4 | migrate + RLS/policy-lint | `migrate` + per-tenant-table lint (policies · `WITH CHECK` · `NOT NULL owner_id` · `(owner_id,id)` index · deletion-class) | W1 (DB) | ⏸ SKIP |
| 5 | transport smoke | boot `apps/api`, hit health route | W1 | ⏸ SKIP (**port not validated — do not wire until W0**, LL-1) |
| 6 | tenant-isolation | cross-tenant read **must FAIL with RLS OFF** | W1 | ⏸ SKIP |
| 7 | drift guard | contract/schema drift check | W1 | ⏸ SKIP |
| — | CI | same runner + **secret-scan** + **dep-audit** | W0 | ⏸ SKIP |

## Project-specific armed legs (D-TRADE-006 / -008 — the bright-lines)
| Leg | Assertion (what green actually means) | Negative control (proves it bites) | Arms | Now |
|---|---|---|---|---|
| **M · money-truth** | a billed provider call bypassing the single metered chokepoint `<3.2>` FAILS the build; every call writes a spend-ledger row + passes the fail-closed governor | plant a provider call outside the chokepoint → leg RED | W1 spine (B4 L4) | ⏸ SKIP |
| **K · no-secret** | a committed key pattern (SEC / market-data / **Supabase service_role / DB password**) or key-in-logs FAILS | plant a fake `SUPABASE_SERVICE_ROLE_KEY=...` or `SEC_API_KEY=...` in a tracked file → leg RED | W0 (CI secret-scan) | ⏸ SKIP |
| **T · provider-taint** | a provider SDK/host outside its sanctioned module FAILS (B4 L1/L3): **`@supabase/supabase-js` + the service_role key are server-data-layer-only** (never in `apps/web`); Polygon/EDGAR likewise | plant a `@supabase/supabase-js` service_role import in `apps/web` → leg RED | W0 static, W1 egress | ⏸ SKIP |
| **C · compliance** | (armed once Legal scopes `<4.3>`) a forbidden code-path / dependency FAILS | plant the forbidden path → leg RED | after Legal ruling | ⏸ SKIP (rule unwritten = GAP, not a pass) |
| **O · oracle legs** | the §10 per-seat oracle legs (`oracle-boundary.md`) — DevOps wires; GA audits coverage | per row | each seat's build wave | ⏸ SKIP |

## §9 build-phase components wired here
B1 A0/A6 bracket the architecture · B2 the 10 pillars / 5 one-way doors (①②④⑥⑧ HARD at MVP) · B3
build-standards (lint/import-boundary at scaffold — **import-boundary encodes the 4-lane cut as code** —
test at spine, a11y at shell, perf W2/W3) · **B4 L1–L3 arm at scaffold, L4 at spine** (billed model) ·
B5 key & secrets approval = HARD launch blocker · B6 Wave-Entry Gate · B8 assurance brackets every wave ·
B10 at operational-readiness. Full text: `docs/foundation/kit/COMPONENTS.md §9`.

**Rule of green:** no leg reports green from an unarmed state — it reports **SKIP** (exit-visible) until it
is armed and its negative control has been shown to make it RED. QA re-runs the full gate on each phase
HEAD in its own clone, on exit codes, before the next wave unblocks.
