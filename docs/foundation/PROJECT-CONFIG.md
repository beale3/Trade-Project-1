# PROJECT-CONFIG — HELM (`trade`) · config of record

Founded on Governed Agent-Team Foundation Kit **v2.2.0** · captured/validated **2026-08-01** by the Lead.
Judgment calls the Director had not confirmed at Script-2 time are recorded as **DIRECTOR-PENDING +
the Lead's recommended default** (LL-24) so the scaffold stands against a concrete value; the Director
overrides when the build brief lands. Two items are **LOCKS** (roster, cost model) that need an explicit
"yes" before any wave dispatches (LL-38) — recorded here as pending-lock, not as ruled.

> **Provenance note.** The Director pasted Script 2 without answering Script 1's elicitation. Per LL-24
> the foundation proceeds on recommended defaults; nothing irreversible (no wave dispatch, no spend, no
> remote push) happens on an unconfirmed value.

## 1 · Identity
| Key | Value | Status |
|---|---|---|
| Product name | **HELM** (parked codename) | 🟡 DIRECTOR-PENDING — rename = one find-replace of `HELM` (LL-3) |
| Infra slug | **`trade`** | recommended (matches existing `Trade - Lead` clone dir) |
| Repo | **`beale3/Trade-Project-1`** (private) | recommended · **remote NOT yet created** (gh unavailable this session) |
| Branch | **`main`** | recommended |
| Clone-dir scheme | **`Trading Project 1\Trade - <Role>`** (Lead = `Trade - Lead`) | recommended (honors the pre-existing dir) |
| Decision-log prefix | **`D-TRADE-`** | recommended |
| Commit trailer | **`Authored by: Mähnbach <noreply@mahnbach.com>`** | house default (kit scaffolder default) |
| Cross-session messaging | **`ccd_session_mgmt` MCP** (`send_message` + active-session verify per LL-36); durable fallback = repo `docs/roles/<role>/activity-log.md` | recommended |

## 2 · Build shape
| Key | Value | Status |
|---|---|---|
| Greenfield vs port | **GREENFIELD** | 🔒 validated (no app code exists) → greenfield wave template (§7) |
| Tech stack | **Node/TS · Fastify · Postgres/Supabase · React/Vite** | recommended default · 🟡 may add a **Python data/ML lane** if the product proves quant-heavy (depends on item Product) |
| Lane cut | **standard 4-lane**, no deviation | recommended |
| Product (one paragraph) | 🟡 **DIRECTOR-PENDING** — strawman: *"A SaaS that ingests SEC EDGAR filings + market data and produces AI-assisted trading/analysis signals for ShupeCapital."* Recorded as a first-class `NOT DECIDED` line in the canonical design doc `<1.1>`. | blocker for real design; scaffold uses the strawman |
| External providers | 🟡 **DIRECTOR-PENDING** — recommended taint set: **SEC EDGAR API** (`sec_api_key` already present) + **Polygon.io** market data | SecOps runs the per-provider ToS-as-taint check before anything builds on a provider |
| Cost model | 🔒-pending **LOCK** — recommended **BILLED PER-USE** (market-data calls + any LLM analysis are metered) → FinOps governs real dollars, **B4 metered chokepoint arms from the spine** | needs explicit Director yes (LL-38) |

## 3 · Roster (recommended ~14 seats — 🔒-pending LOCK, needs explicit yes)
Core spine (never comes off) + the AI/finance-family seats. Models per §2 lock: **Architect = Fable 5 ·
Max (LOCKED); every other seat = Opus 4.8 · High.** Escalation beyond High is per-wave Director approval.

| Seat | Profile | Lane / role | On? |
|---|---|---|---|
| Program Lead | `roles/lead` | orchestration · canonical doc · pipeline | ✅ core |
| Principal Architect *(on-demand)* | `roles/architect` | ADRs/ASRs · A0/A6 · Fable 5·Max | ✅ core |
| QA Lead | `roles/qa` | coverage + phase-exit · runs armed legs | ✅ core |
| Governance & Audit | `roles/ga` | rule/evidence audit · oracle coverage-audit · RECONCILE gate | ✅ core |
| SecOps | `roles/secops` | keys · provider ToS-taint · bright-lines | ✅ core |
| Backend (API & Platform) | `roles/be-api` | Lane 1 transport · money-moving chokepoint | ✅ core |
| Backend (Data & Domain) | `roles/be-data` | Lane 2 domain+DB · money-truth ledger | ✅ core |
| Frontend (Web) | `roles/fe-web` | Lane 3 SPA | ✅ core |
| DevOps | `roles/devops` | Lane 4 build/env · wires oracle legs | ✅ core |
| AI/ML | `roles/ai-ml` | builds the scoring/gen engine (judged by AIQ) | ✅ AI-family |
| AI Quality | `roles/aiq` | golden evals · grounding · judges AI/ML | ✅ AI-family |
| FinOps | `roles/finops` | per-unit COGS · fail-closed governor | ✅ (billed model) |
| Legal & Privacy | `roles/legal` | SEC/financial-regulatory + PII surface | ✅ (heavy here — do not drop) |
| Data Engineer | `roles/data-eng` | market-data / EDGAR ingestion | ✅ AI/data-family |
| **Gauntlet cluster** (Market Research · Competitive Intel · Product Strategy · Viability Analyst · Skeptic→Director · Delivery/PMO) | *(no kit profile)* | product Phase-0 (B9) | 🟡 DIRECTOR-PENDING — seat only if B9 runs; needs the product defined |
| Design Lead · PM · other GTM/Ops seats | `roles/design`,`roles/pm`,… | CX / product / GTM | ⏸ off until a surface appears (add the moment it does — LL-17) |

## 4 · Build-phase components (§9) — adopt + arming schedule
| Comp | Adopt? | Arms |
|---|---|---|
| B1 Architecture gates A0/A6 | ✅ | brackets the architecture (A0 pre-build, A6 pre-merge) |
| B2 Engineering-Quality-Bar (10 pillars / 5 one-way doors) | ✅ | pillars arm as their surface appears; 5 doors HARD at MVP |
| B3 Build-Standards baseline | ✅ | lint/import-boundary at scaffold; test at spine; a11y at shell; perf W2/W3 |
| B4 Metered-chokepoint containment L1–L4 | ✅ (billed per-use) | L1–L3 at scaffold, L4 at spine |
| B5 Key & Secrets Approval Gate | ✅ (prod API keys) | HARD launch blocker |
| B6 Wave-Entry Gate + dispatch-freshness | ✅ | every wave |
| B7 Pre-build Design DP-1→DP-4 | 🟡 DIRECTOR-PENDING (only if CX-heavy) | before build if adopted |
| B8 Assurance Layer | ✅ | brackets every wave (front red-team + back adversarial-verify) |
| B9 Validation Gauntlet (G1–G8) | 🟡 DIRECTOR-PENDING — **recommended: RUN** (new opportunity) | product Phase-0, before any design/build |
| B10 Operational-Readiness & Assurance-Register | ✅ | launch/operational-readiness phase |

**Pre-build order:** B9 → (B7 if adopted) → build waves. B8 brackets every wave; B1 brackets the architecture.

## 5 · Validated environment (Phase 2 — read from the live repo 2026-08-01)
Greenfield: the app tree, ports, DB, and gate scripts **do not exist yet** — they are created at **W0
scaffold** and **must be re-validated immediately before authoring wave code** (LL-1). Nothing below is
baked as a "verified" runtime value; planned defaults are labelled as such.

| Item | Value (verified 2026-08-01) |
|---|---|
| Lead clone | `C:\Users\beale\Software Dev\Trading Project 1\Trade - Lead` (this repo) |
| Git baseline | fresh `git init` at founding commit (no prior product history); **no remote** |
| App tree | **none yet** — planned (default stack): `apps/api` (Fastify) · `apps/web` (React/Vite) · `packages/{domain,db,contracts,config}` |
| Ports | **none yet** — planned defaults (DevOps confirms at W0): API `:3000` · web `:5173` · Postgres `:5432`/Supabase. **NOT validated — do not bake into a gate leg until W0.** |
| DB / migrations | **Supabase project `zyscsnhiymitpfdhjuci`** (D-TRADE-013, reachability verified 2026-08-01) — `https://zyscsnhiymitpfdhjuci.supabase.co`; forward-only reviewed migrations under `packages/db/migrations`, RLS+policy-lint per tenant table; baseline at W0. Connection details: `docs/infra/supabase.md` |
| Gate scripts | **none exist** — `tsc`/`build`/`test`/`migrate`/RLS-lint/smoke/drift all to be added at W0 (SKIP-visible until armed) |
| Secrets present | (1) `..\Trade\sec_api_key.txt` (SEC EDGAR key); (2) **Supabase keys** (anon · service_role) + **DB password** for project `zyscsnhiymitpfdhjuci` — service_role + DB password are full-access, **B5, Director/SecOps into gitignored `.env`/store only, never chat or repo**. `.env`/`.env.*` gitignored (verified). |

## 6 · Isolation rule
The target project stated **no explicit isolation rule** (no design docs existed at founding). Standing
rule adopted (LL-4): the Foundation Kit at `docs/foundation/kit/` is project-agnostic *methodology* and
crosses freely; **product content, brand, decisions, and design language never cross** between teams.
If the Director sets a specific isolation constraint (e.g. keep HELM separate from the earlier `Trade`
experiment), it is recorded verbatim here and in the charter banner.

## 7 · Canonical-mirror note
The kit's canonical mirror `C:\Users\Shupe\New M-4 Foundation-Kit` is **absent on this machine**. The two
local copies (`Software Dev\Foundation Kit` and `Software Dev\Trading Project 1`) agree at kit commit
`29d0cad` (v2.2.0) and are treated as authoritative. The Phase-5 self-improvement push (STEP 6) mirrors
to `Software Dev\Foundation Kit` (the local canonical stand-in) until the Director restores/creates the
canonical remote `ShupeCapital/agent-team-foundation-kit`.
