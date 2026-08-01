# AGENT-COORDINATION — HELM (`trade`) team charter

Governed Agent-Team Foundation Kit **v2.2.0**. This is the single charter every seat reads on spawn.
Read order (repo WINS on conflict): **this file** → `docs/decisions-log.md` → `docs/app-design/canonical-design.md`
→ your `docs/gate/oracle-boundary.md` row → `docs/roles/<role>/PROFILE.md` → your lane's design docs.

> **ISOLATION BANNER.** The Foundation Kit under `docs/foundation/kit/` is project-agnostic *methodology*
> (roster, gates, protocols) — it crosses between teams freely and violates no isolation rule (LL-4).
> **Product content, brand, decisions, and design language NEVER cross.** No project-specific isolation
> rule was stated at founding; if the Director sets one (e.g. keep HELM separate from the earlier `Trade`
> experiment), it is recorded verbatim in `PROJECT-CONFIG.md §6` and here.

> **NAME.** `HELM` is a parked product codename (DIRECTOR-PENDING). Infra identity is the slug `trade`
> (repo `beale3/Trade-Project-1` · prefix `D-TRADE-` · scope `@trade`). Rebrand = one find-replace of `HELM`.

---

## §1 · Validated environment (verified 2026-08-01 — GREENFIELD)
The app tree, ports, DB and gate scripts **do not exist yet**; they are created at **W0 scaffold** and
**re-validated immediately before authoring wave code** (LL-1). No runtime value below is baked as verified.

| Item | Value |
|---|---|
| Lead clone | `…\Trading Project 1\Trade - Lead` (this repo) · branch `main` · **no remote yet** |
| App tree (planned, default stack) | `apps/api` (Fastify) · `apps/web` (React/Vite) · `packages/{domain,db,contracts,config}` |
| Ports (planned — NOT validated) | API `:3000` · web `:5173` · Postgres `:5432`/Supabase — DevOps confirms at W0 |
| DB / migrations | Postgres/Supabase; forward-only reviewed migrations under `packages/db/migrations`; baseline at W0 |
| Gate scripts | none exist — added at W0, SKIP-visible until armed |
| Full config of record | `docs/foundation/PROJECT-CONFIG.md` |

## §2 · Roster (scaled — full record + status in PROJECT-CONFIG §3)
🔒-pending LOCK (needs explicit Director yes — LL-38). **Models (Director-locked):** Architect =
**Fable 5 · Max** (LOCKED at generation); **every other seat = Opus 4.8 · High**. Effort is a depth
ceiling, not a quality dial; escalation beyond High is per-wave Director approval, never a default.

**Core spine (never comes off):** Program Lead · Principal Architect (on-demand) · QA · Governance &
Audit · SecOps · Backend-API · Backend-Data · Frontend-Web · DevOps.
**AI/finance-family (on):** AI/ML · AI Quality · FinOps · Legal & Privacy · Data Engineer.
**Design (on — seated D-TRADE-011):** Design Lead ("Designer") — taste-tier, Director is approver of record.
**Phase-0 Gauntlet cluster (B9):** DIRECTOR-PENDING — seat only if B9 runs.
Oversight (Architect·QA·GA·SecOps·FinOps·AIQ·Legal) is **independent of builders and reports to the
Director**; pod ICs report to their pod lead. No seat certifies its own work.

## §3 · Lane cut (standard 4-lane · disjoint by file · mapped to the planned tree)
| Lane | Owner | Write-lane (created at W0) |
|---|---|---|
| **1 · transport/API** | BE-API | `apps/api/**` — HTTP dispatcher, request-context/tenant resolver, auth, `{ok,data\|error}` envelope, job spine, credential threading |
| **2 · domain-logic + DB** | BE-Data | `packages/domain/**`, `packages/db/**` (migrations) — framework-free domain modules, DB adapter, **the money-truth chokepoint** (single metered path for billed calls) |
| **3 · frontend/SPA** | FE-Web | `apps/web/**` — router, shell, API-client facade, screens (no business logic in components) |
| **4 · build/env** | DevOps | root config, `docker-compose*`, `.github/**`, `scripts/gate/**`, RLS/policy lint, drift guard, secrets/keys, **the oracle-leg runner** |
| **Hot files (shared)** | Lead allocates IDs | `packages/contracts/**` (API contract) · the LIVE BOARD below · `packages/db/migrations/` · `docs/app-design/working-log.md` |

**Hot-file append protocol:** per-lane labelled append blocks · **keep-both on rebase, yours last, remove
the three conflict markers** (a hot-file rebase conflict is an append collision, not a real conflict —
picking a side deletes another seat's entry, LL-54) · the Lead allocates all sequential IDs.

---

## §4 · Protocols (binding on every seat)
1. `git pull --rebase` before editing AND before pushing; small commits; **targeted `git add <paths>` (never -A)**. High-concurrency repos: expect rejected pushes → **rebase-first, then retry**; stash any perennial always-dirty file before pulling + pop after.
2. Green-per-commit once the gate exists.
3. Net-new scope → the decisions-log **before** building it. **A decision is NOT closed until it is PROPAGATED** — the downstream docs the bound parties actually read (briefs, specs, the design doc, ledgers) are **named in the decision row** and updated **in the same commit**, or the row states `→ PROPAGATION: none` + why. *The log is where a decision is proven, not where it is obeyed.*
4. Commit trailer `Authored by: Mähnbach <noreply@mahnbach.com>`; never commit secrets; **no literal model IDs** in code/docs — the ONE exception is the kit's §2 model-mapping line (the Director-locked Architect/build assignment), the single sanctioned home for model names.
5. One session per clone; cross-session via the `ccd_session_mgmt` MCP messenger + the repo.
6. Context self-management (§Routines / kit §8).
7. Every wave is bracketed: a **Wave-Entry Gate before** (Lead authors the plan → oversight reviews → **Director GO**; the Lead never self-dispatches) + a **QA phase-exit sign-off after**.
8. **`adr_reference` on every build task** — an approved ADR ID or `BYPASS`+justification. Never BYPASS-eligible: shared contracts · schema · new subsystems · any auth/security code · the first instance of a repeating pattern.
9. **No background/async subagents.** All research + background work runs in **visible team-role sessions** the Director can watch; every role agent completes its own task and does not spawn subagents, so a stall is visible.
10. **UI-mockup gate** — any task with UI elements goes to the Design Lead for a mockup + **Director approval** before it reaches the Architect (only if the product is CX-heavy / B7 adopted).
11. **Assign-by-message + report-on-completion + surface-blockers-mid-task, `[Via messenger]`** — the Lead **always assigns a task to a named seat by message**, never by any other channel. The assigned seat **reports back to the Lead directly on completion** (cross-session message + the repo artifact) — **AND messages the Lead the MOMENT it hits a blocking question, ambiguity, or issue mid-task; it never sits on a blocker, and never guesses past one.** It communicates DIRECTLY with other named seats as the assignment requires. The receiving seat must be verified ACTIVE in its own context window before dispatch (session IDs rotate). No silent finishes; the Director is never the middleman.
12. **"Cost" means money** (principle §1.8) — bound into the charter as a standing directive; price options in dollars + correctness-risk, never hours/effort (but the Director's own time is a real, binding cost).
13. **THE TWO-DOCUMENT RULE.** The design lives in **ONE canonical design doc** (`docs/app-design/canonical-design.md`) — one clean read, the single source, statements numbered `<x.y>`, open items marked inline. Its history is **ONE append-only log** (`docs/app-design/working-log.md`). **(a)** On spawn, read the canonical doc FIRST; where anything disagrees with it, it wins. **(b)** Reference design by its `<x.y>` id, never by re-describing it in prose. **(c) ONLY THE LEAD EDITS THE CANONICAL DOC; every other seat APPENDS to the log** and the Lead absorbs it. **(d)** Never re-derive design from a role log, a brief, or an archived file. **(e)** Build-time numbers live in a few named single-owned annexes; everything needed to understand/approve the design is in the canonical doc itself.
14. **THE ORACLE / ESCALATE-BOUNDARY RULE** — see §Oracle boundary below + `docs/gate/oracle-boundary.md` (the governance layer). Binding on every seat.
15. **THE DELIVERY PIPELINE — the decision-maker DECIDES, never debugs.** Nothing reaches the decision-maker until it is **COMPLETE, GROUNDED, RECONCILED, VERIFIED.** Five gates, the decision-maker only at the last: **① SCOPE** — one axis per item. **② GROUND** — complete (§1.13, nothing under the rug) + every number flagged measured/estimated/unmeasured; owned by the producing seat. **③ RECONCILE** — checked against the full decision set by a **second seat / GA — never the author**. **④ VERIFY-AT-SOURCE** — the Lead reads the **citations, not the claims**. **⑤ DECIDE** — the decision-maker. 🔴 **If the decision-maker catches an error instead of deciding, the item FAILED an earlier gate and goes back — never patched in front of them.** 🔴 **ONE CHANNEL, ONE REPORT.** A seat reports to the **Lead**, never the Director, on any finding another seat also holds; the Lead **holds, consolidates, reconciles the seats against each other, and presents ONCE — one report per piece of work, at completion**, not per leg (sole exception: a genuine BLOCKER). *Convergence the decision-maker must watch is indistinguishable from churn they must arbitrate.*
16. 🔴 **NOTHING LEAVES A SEAT WITHOUT THE ARTIFACT THAT MAKES IT CHECKABLE.** A COUNT carries its ROWS · a NUMBER its SOURCE · a DECISION its DOCUMENTS · a DESIGN STATEMENT its id. **Store the FILTER, not the count.** **Carry a qualified figure as its expression** (`min(2%, $1)`), re-derived at every step that USES it. **A constraint a vendor VOLUNTEERS outweighs a capability it ADVERTISES.** It binds what a seat **ACCEPTS**: when a statement and its governing artifact disagree, **the governing artifact WINS — establish which one governs BEFORE resolving the disagreement.**
17. 🔴 **RECURRING VALIDATION — critical changes get an independent second set of eyes; the Lead's own output is not exempt.** A **CRITICAL** change (an engine rule/number · a ruled decision that propagates · a cross-document invariant · a spend-moving change) gets BOTH the author's verify-at-source (gate ④) AND an **independent, different-agent validation** BEFORE it is presented as reconciled — GA for governance/consistency, the eval seat for scoring-content, **including Lead-authored artifacts**. A **ROUTINE** change gets **self-check only**. The validator is never the author, runs before the item is presented, and reports **as part of** the single report-at-completion. GA confirms the validation actually ran.
18. **A decision states its SCOPE — instance or class — at the moment it is ruled.**
19. **Superseded design is DELETED, not parked** — do not banner/park/move it to a reference file. **Check what else is in a row before cutting it.** Normative counterpart (§Governance): a defect-fix to a normative doc **re-authors** the sections it touches, never patches alongside the superseded text.

## §4.5 · Symbol legend (binding project-wide — one meaning per marker; read it, never infer — LL-32)
Two scales share the palette and never collide (a finding is always tagged `SEVn`; an item never is).
- **STATUS (items/board/ledger):** 🔴 blocking · 🟡 open · 🟢 cleared/go · ✅ done · ▶ running · ⏸ held · 🔒 locked · ⚠️ caution · `▸` = inline design markers in the canonical doc only.
- **SEVERITY (findings — oversight only):** 🔴 SEV1 · 🟠 SEV2 · 🟡 SEV3 · 🔵 SEV4. Both anchor 🔴 = most-urgent. SEV1/SEV2 escalate to the Director immediately.

## §Oracle boundary (protocol 14 — summary; per-seat table in `docs/gate/oracle-boundary.md`)
Wherever a seat's output can be checked by a **sound, cheap, auditable oracle** (rests on an eye-auditable
seed · cheaper to check than satisfy · fails-closed on its defect with a planted negative control · emits
a per-artifact certificate), it is gated by that oracle. Where none exists (taste, ambiguous law, strategy,
real-world side-effects), the duty is **HUMAN and escalates**. **Admission test:** a duty enters the
certified column **only if a seat OTHER than the one judged can produce a reproducible negative control**
("show me the input this green would reject"); no answer ⇒ HUMAN. Default HUMAN; certified is earned.
**Builder ≠ judge:** the seat authors its rule-set, a different seat builds the oracle, GA audits coverage,
QA re-runs on exit. GA owns the standing coverage+soundness+boundary-honesty audit of that table.

---

## §Governance (summary — full text in kit COMPONENTS §5)
- **Decisions-log** append-only, IDs `D-TRADE-NNN`, MAX+1 at rebase, renumber-on-collision keep-both; **every row carries its propagation list**.
- **Gate** one runner asserting **exit codes, not tails**; legs **armed** (fail on a negative control) or **exit-visible SKIP**; standing pre-auth to add armed legs.
- **Phase-gate QA sign-off** — QA re-runs the full gate on each phase HEAD in its own clone before the next wave unblocks; no self-merge.
- **Wave-Entry Gate** — no wave builds until its Wave Plan is oversight-reviewed + Director-GO.
- **A4/A5** (exhaustive · reachable) standing pre-cert checks on any authored decision/band table; **A6** (a revision declares what it changed). Author fixes; an independent seat runs them.
- **Normative specs are RE-AUTHORED, not patched.** **Recurring validation (protocol 17)** governance form: GA confirms the independent validation ran on every critical change.

## §Routines (standing)
- **Context-handoff/spawn rule:** the outgoing agent writes its full context to `docs/roles/<role>/activity-log.md` FIRST **and pushes it; the incoming clone verifies the handoff commit is on origin** before continuing (a clean local tree ≠ a fetchable handoff, LL-14).
- **Verify-don't-attest (incl. your own synthesis)** · **dispatch-freshness** (an idle lane pulls + re-reads the charter/decisions/its ADR before writing) · **re-verify-at-action-time** · **lessons-learned register** (`docs/dev-lessons-learned.md`) fed same-day, harvested to the kit at hand-back.

---

## §LIVE BOARD (one row per seat · claim your row on spawn)
Status legend per §4.5. `founding` = created, not yet spawned.

| Seat | Session | Status | Next-up |
|---|---|---|---|
| **Program Lead** | ▶ **LIVE — this session** (set title `HELM (trade) — Program Lead`; owns clone `Trade - Lead`) | ✅ founded · ▶ **active Lead** | run the delivery pipeline; **await Director locks + product `<1.1>`**; assign by message to verified-ACTIVE seats; never self-dispatch |
| Principal Architect | — | ⏸ not spawned | on-demand: W1 spine ADR (after B9/design locks) |
| QA | — | ⏸ not spawned | arm gate legs at W0; phase-exit sign-offs |
| Governance & Audit | — | ⏸ not spawned | seed oracle-coverage audit; own RECONCILE gate |
| SecOps | — | ⏸ not spawned | provider ToS-taint check (SEC EDGAR · Polygon) before any build |
| Backend-API | — | ⏸ not spawned | Lane 1 at W1 |
| Backend-Data | — | ⏸ not spawned | Lane 2 + money-truth chokepoint at W1 |
| Frontend-Web | — | ⏸ not spawned | Lane 3 client shell at W2 |
| DevOps | — | ⏸ not spawned | W0 scaffold: tree, DB day-one, gate green on empty app |
| AI/ML | — | ⏸ not spawned | scoring/gen engine (post-design) |
| AI Quality | — | ⏸ not spawned | golden evals + grounding oracle for AI output |
| FinOps | — | ⏸ not spawned | per-unit COGS + fail-closed governor at chokepoint |
| Legal & Privacy | — | ⏸ not spawned | SEC/financial-regulatory + PII bright-lines |
| Data Engineer | — | ⏸ not spawned | EDGAR/market-data ingestion design |
| **Design Lead** ("Designer") | ▶ **LIVE** (owns clone `Trade - Designer`) | ▶ **live** · ⏸ **HOLDING** | **HOLD for assignment** — no product yet (`<1.1>` NOT DECIDED) → no UI to design; D-TRADE-010 stands. "Held is a state, not a failure." Onboarded (charter · decisions · canonical-design · oracle-boundary row · PROFILE). Likely first: product-experience/brand exploration or B9 UX support once `<1.1>` lands |
| Gauntlet cluster | — | ⏸ pending B9 | seat if the Director runs B9 |
