# Decisions log — HELM (`trade`)

Append-only. IDs `D-TRADE-NNN`, allocated MAX+1 by the Lead at rebase (renumber-on-collision, keep both).
Columns: **ID · date · decision · why · decided-by · → PROPAGATION**. A decision is **not closed** until
every downstream doc it binds is named in its row and updated **in the same commit** (protocol 3 / LL-25),
or the row states `→ PROPAGATION: none` + why. Rulings state **scope: instance | class** (protocol 18).
`🔒-pending` = the Lead's recommended default, awaiting the Director's explicit confirmation (LL-38); it is
scaffolded against but **not ruled** until confirmed.

| ID | date | decision | why | by | → PROPAGATION |
|---|---|---|---|---|---|
| D-TRADE-001 | 2026-08-01 | **Team founded** on Foundation Kit v2.2.0; greenfield. *(class)* | start the governed team | Lead | AGENT-COORDINATION, PROJECT-CONFIG, README, this repo skeleton — done this commit |
| D-TRADE-002 | 2026-08-01 | **Wave template = GREENFIELD** (W0→W3+, §7). *(class)* | no app code exists (validated) | Lead | app-design/stage-plan.md — done this commit |
| D-TRADE-003 | 2026-08-01 | **Stack = Node/TS · Fastify · Postgres/Supabase · React/Vite** (recommended default). *(class)* | kit default fits a SaaS surface | Lead 🔒-pending | gate-spec.md commands, AGENT-COORDINATION §3 lanes, stage-plan — done this commit. **OPEN framework lock:** a Python data/ML lane may be added if the product proves quant-heavy → reopen before W1. |
| D-TRADE-004 | 2026-08-01 | **Cost model = BILLED PER-USE** → FinOps governs real dollars; **B4 metered chokepoint arms from the spine**; a $/day self-tally auto-kill. *(class)* | market-data + LLM calls are metered | Lead 🔒-pending LOCK | PROJECT-CONFIG §2/§4, gate-spec (money-truth leg), oracle-boundary (FinOps/BE-Data rows), stage-plan W1 — done this commit; **needs explicit Director yes** |
| D-TRADE-005 | 2026-08-01 | **Roster = 14 seats** (core spine + AI/ML · AIQ · FinOps · Legal · Data-Eng). *(class)* | AI/finance SaaS family | Lead 🔒-pending LOCK | PROJECT-CONFIG §3, AGENT-COORDINATION §2/board, oracle-boundary rows, role-bootstrap-scripts — done this commit; **needs explicit Director yes** |
| D-TRADE-006 | 2026-08-01 | **Compliance bright-lines armed as gates:** (a) **no secret in repo/logs** (SEC/market-data keys) — a committed key pattern FAILS; (b) **money-truth** — a billed call bypassing the metered chokepoint FAILS; (c) **provider-ToS taint** — a provider SDK/host outside its sanctioned module FAILS. *(class)* | SEC/financial + billed-spend surface | Lead + SecOps(to confirm) | gate-spec.md legs, oracle-boundary (SecOps/FinOps/Legal rows) — done this commit; legs **arm at their build wave** (SKIP-visible until then) |
| D-TRADE-007 | 2026-08-01 | **Isolation:** kit methodology crosses; product content/brand/design never cross (LL-4). No project-specific rule stated at founding. *(class)* | isolation bars content, not process | Lead | AGENT-COORDINATION isolation banner, PROJECT-CONFIG §6 — done this commit; Director may add a specific rule → reopen |
| D-TRADE-008 | 2026-08-01 | **Money-truth surface declared:** the single metered chokepoint (Lane 2, BE-Data) is the only path for billed provider calls; every call writes an append-only spend-ledger row + passes the fail-closed governor. *(class)* | high-invariant surface, spec-complete-before-build | Lead | B2 pillar ④/⑥, B4 L4, gate-spec money-truth leg, oracle-boundary BE-Data/FinOps — done this commit |
| D-TRADE-009 | 2026-08-01 | **B9 Validation Gauntlet — recommended RUN** before any design/build (new opportunity). *(class)* | gate the opportunity before building it (LL-20) | Lead 🟡 DIRECTOR-PENDING | stage-plan pre-build order, PROJECT-CONFIG §4, foundation/README open-decisions — done this commit; **awaits Director run/skip + the product paragraph** |
| D-TRADE-010 | 2026-08-01 | **⏸ NO CODE BUILD / NO WAVE DISPATCH IS AUTHORIZED.** Current phase = **foundation only**. Every wave in `stage-plan.md` (incl. W0) is the documented PLAN, **not an available action**. Building unblocks only after the pre-build gate clears: product defined (`<1.1>`) → B9 viability/blueprint (if run) → Director build-GO. No build role needs spawning until there is build work for it. *(class)* | Director ruling — we are not building any code yet | **Director** | stage-plan.md (banner + W0 line), foundation/README.md (§3 + next-steps), open-items-ledger.md (§B, §D) — done this commit |

**Open framework/arch locks that must resolve before the core wave:** the stack Python-lane question
(D-TRADE-003), and everything downstream of the **product paragraph** (`canonical-design <1.1>`), which
is `NOT DECIDED` and blocks a real W1 feature design.
