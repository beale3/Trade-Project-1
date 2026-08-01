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
| Repo | **`beale3/Trade-Project-1`** | ✅ LIVE (D-TRADE-012; pushed by Director) |
| Branch | **`main`** | recommended |
| Clone-dir scheme | **`Trading Project 1\Trade - <Role>`** (Lead = `Trade - Lead`) | recommended (honors the pre-existing dir) |
| Decision-log prefix | **`D-TRADE-`** | recommended |
| Commit trailer | **`Authored by: Mähnbach <noreply@mahnbach.com>`** | house default (kit scaffolder default) |
| Cross-session messaging | **`ccd_session_mgmt` MCP** (`send_message` + active-session verify per LL-36); durable fallback = repo `docs/roles/<role>/activity-log.md` | recommended |

## 2 · Build shape (🔒 REVISED 2026-08-01 — D-TRADE-020, personal-tool pivot)
| Key | Value | Status |
|---|---|---|
| Greenfield vs port | **GREENFIELD**, but existing artifacts to ingest (screener, backtest engine, 4 studies) — not a blank slate | 🔒 |
| Tech stack | **Python** (pandas/numpy/scipy) for the screener/backtest/analysis core — matches all existing research + the options screener; **Supabase retained** as the durable store for scan history/signals/backtest results; **Node/Fastify/React likely drop** — no web frontend needed for "a Python script/tool I can run." `<3.5>` — Architect confirms at design time. | 🔒 reopened, D-TRADE-020 |
| Lane cut | 4-lane cut **no longer fits** a single-Python-project personal tool — re-cut at design time (likely: screener/scoring, backtest/validation, data ingestion, infra/CI) | 🟡 reopen with Architect |
| Product (one paragraph) | 🔒 **LOCKED** — see canonical `<1.1>`: a personal options-signal tool validating the existing screener via directional-correctness backtesting, on a liquid-optionable universe. Phase 2 (full P&L sim + a from-scratch predictive model) explicitly deferred. | 🔒 D-TRADE-020 |
| External providers | Massive (market/options data, all prior research) + likely SEC-API.io (EDGAR filings, `..\Trade\sec_api_key.txt`) — both **very plausibly personal-tier-compliant** now that use is confirmed personal (SecOps's earlier HIGH-taint finding was scoped to commercial use) | 🟡 light confirmatory check, not a hard blocker |
| Cost model | **BILLED PER-USE, but personal scale** — a spend GUARD (cap + visibility), not SaaS-grade metered-chokepoint/billing-reconciliation machinery | 🔒 D-TRADE-020 (re-scoped, not overturned) |

## 3 · Roster (🔒 REVISED 2026-08-01 — D-TRADE-020; roster LOCK confirmed via the personal-tool decision itself)
Personal tool ⇒ **no multi-tenant surface, no GTM/commercial pod, no Gauntlet.** Models unchanged:
**Architect = Fable 5 · Max (LOCKED); every other seat = Opus 4.8 · High.**

| Seat | Profile | Lane / role (re-scoped) | On? |
|---|---|---|---|
| Program Lead | `roles/lead` | orchestration · canonical doc · pipeline | ✅ |
| Principal Architect *(on-demand)* | `roles/architect` | stack/design ADRs for the Python tool, re-cut lanes | ✅ (spawned, holding) |
| QA Lead | `roles/qa` | independent CV/backtest re-derivation, phase-exit | ✅ (not yet spawned) |
| Governance & Audit | `roles/ga` | rule/evidence audit; audits AIQ's independent validation | ✅ (not yet spawned) |
| SecOps | `roles/secops` | provider ToS-taint (now: confirm personal-tier compliance) · key denylist | ✅ (spawned, delivered Phase-1 work) |
| Backend-API / Frontend-Web (`be-api`, `fe-web`) | — | **N/A** — no web frontend, no external API surface | ⏸ off (never spawned) |
| Backend-Data → **SDE1** | `roles/sde1`(=be-data) | data ingestion + Supabase storage layer, re-scoped from "money-truth chokepoint" to normal data plumbing | ✅ (spawned, holding) |
| DevOps | `roles/devops` | repo/CI/gate harness for a Python project; lighter than SaaS scope | ✅ (spawned, delivered Phase-1 work) |
| AI/ML | `roles/ai-ml` | **re-scoped: builds the walk-forward-CV backtest pipeline** (quant research, not generative AI) | ✅ (spawned, holding — now has real work) |
| AI Quality | `roles/aiq` | **re-scoped: independently re-derives/audits each backtest result** (builder≠judge on the CV discipline, not LLM-output grounding) | ✅ (spawned, holding — now has real work) |
| FinOps | `roles/finops` | **re-scoped down**: a personal spend guard, not per-tenant billing/fail-closed governor | ✅ (spawned, delivered Phase-1 work) |
| Legal & Privacy | `roles/legal` | **substantially de-risked** — light confirmatory check on `<4.3>`, not a hard pre-build blocker | 🟡 optional light-touch seat, not urgent |
| Data Engineer | `roles/data-eng` | build/maintain the liquid-optionable-universe list; historical options-chain data discovery | ✅ (not yet spawned — now has clear, real work) |
| Design Lead ("Designer") | `roles/design` | **mandate mostly evaporates** — "a Python script/tool I can run" has no UI surface to design | ⏸ (spawned, holding — notify + likely stand down) |
| Gauntlet cluster / GTM pod / PM / BizOps / Support / Success | — | **N/A — personal tool, no market/customers to validate or serve** | ⏸ off, permanently (not "pending") |

## 4 · Build-phase components (§9) — 🔒 REVISED, D-TRADE-020
| Comp | Adopt? | Arms |
|---|---|---|
| B1 Architecture gates A0/A6 | ✅ (lighter — a Python project, not a service architecture) | brackets design decisions |
| B2 Engineering-Quality-Bar | 🟡 **mostly N/A** — pillars ②(tenant-isolation) and most of the SaaS-reliability set don't apply; keep ⑨(cost efficiency) and basic test discipline | re-scope with Architect |
| B3 Build-Standards baseline | ✅ (lint/test, simplified for a Python project) | scaffold |
| B4 Metered-chokepoint containment L1–L4 | ❌ **dropped** — replaced by `<3.2>` the spend guard, a much lighter mechanism | — |
| B5 Key & Secrets Approval Gate | ✅ (kept — personal API keys still deserve this discipline) | before any live-key use |
| B6 Wave-Entry Gate + dispatch-freshness | ✅ (kept, lighter-weight for a personal project) | every phase |
| B7 Pre-build Design DP-1→DP-4 | ❌ **N/A** — no CX surface | — |
| B8 Assurance Layer | ✅ (kept — the builder≠judge backtest-validation split IS this) | brackets Phase 1 |
| B9 Validation Gauntlet | ❌ **N/A** — no market opportunity to validate; this is personal tooling | — |
| B10 Operational-Readiness & Assurance-Register | 🟡 **light-touch only** — no external "go-live," but a hazard register for "don't let a bad signal cause a bad trade" is still worth having | later, light |

**Order:** B1 (lightweight design ADR) → B5 (secrets) → Phase 1 build, bracketed by B8 (builder≠judge on
every backtest result) and B6 (phase-exit before Phase 2 starts).

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
