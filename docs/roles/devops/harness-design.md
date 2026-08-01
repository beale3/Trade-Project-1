# DevOps — gate-harness + W0 design-of-record (DESIGN ONLY)

> ⏸ **D-TRADE-010 stands: no build / no scaffold.** This document is a *design*, not code.
> **No `scripts/gate/**`, `.github/**`, `docker-compose*`, or app tree is created here.** It exists so the
> W0 scaffold is build-ready the instant a Director **build-GO** + a D-TRADE-010 lift land. Values below are
> **validated on this machine 2026-08-01** (LL-1: bake validated values, never framework defaults).

Author: DevOps seat (clone `Trade - DevOps`). Reviewers on build-GO: Lead (infra tradeoffs) · QA (re-runs
the harness) · GA (leg-coverage audit) · SecOps (authors the leg K denylist + leg T taint rules).

---

## §A · Validated environment (verified 2026-08-01 — this machine)
Reconnaissance only (no code built). Replaces the "planned / NOT validated" rows of `gate-spec.md` +
charter §1 **at W0**, per LL-1 / W0-6.

| Item | Validated value | Note |
|---|---|---|
| OS / arch | Windows 11 (10.0.26200) · AMD64 | dev host is Windows → CI is Linux; harness must be **OS-portable** |
| git | ✅ 2.55.0.windows.2 | present; clone identity was **unset** → set to `Mähnbach <noreply@mahnbach.com>` |
| Node.js / npm / npx | 🔴 **ABSENT** (not on PATH, not in any standard install dir) | blocks W0 stack **and** the `npx`-launched MCP connector |
| pnpm | 🔴 **ABSENT** | workspace manager for the planned monorepo — must be installed at W0-0 |
| Docker / daemon | 🔴 **ABSENT** | local Postgres via `docker-compose` (W0-2) cannot run until installed |
| gh (GitHub CLI) | 🔴 **ABSENT** | remote-create/push routes to the Director (LL-71); not required for local scaffold |
| Port 3000 (API) | ✅ FREE | bake as API port (no collision to reconfigure around) |
| Port 5173 (web) | ✅ FREE | bake as Vite web port |
| Port 5432 (Postgres) | ✅ FREE | bake as local DB port |
| Port 54321 (Supabase local) | ✅ FREE | reserved if `supabase start` local stack is used |

**Infra-floor finding (surface to Lead, dollars-relevant per LL-15):** the build toolchain is **not
installed**. Before W0 can produce a green gate, a human installs **Node LTS + pnpm + Docker Desktop**
(installers are $0; Docker Desktop needs a paid subscription only for large orgs — flag to FinOps if org
size crosses the threshold). This is a **new W0-0 pre-req** proposed below.

---

## §B · Gate-harness design (VERIFIER tier — DevOps owns the runner; builder ≠ judge)
One runner, **exit-code-honest**: it asserts each leg's child-process **exit code**, never greps a piped
tail (LL-50 / gate-spec "assert exit codes, never tails"). GA audits that the runner is armed; QA re-runs it.

### B.1 Runner shape
- **Single source of truth, OS-portable:** a Node script `scripts/gate/run.mjs`, invoked as `pnpm gate`,
  runs **identically** on the Windows dev host and Linux CI. (Chosen over a `sh`+`pwsh` pair to avoid two
  drifting implementations. Depends on Node → gated by W0-0 install.)
- **Leg registry** `scripts/gate/legs/*.mjs`, each exporting `{ id, name, armsAt, status, run(), negativeControl }`.
- **Status vocabulary (no vacuous green):** a leg is `ARMED` (proven to FAIL on a planted negative control),
  or **exit-visible `SKIP`** (its surface does not exist yet). **A SKIP prints `SKIP (surface absent)` and
  NEVER counts toward green.** The runner exits non-zero **iff any ARMED leg fails**; SKIPs never fail it,
  and a leg is *never* green from an unarmed state (gate-spec "Rule of green").
- **Output:** a table (`LEG | TIER | STATUS | RESULT`) + a machine block; the human reads the table, CI
  reads the exit code.

### B.2 The done-bar (LL-48 — the harness's first negative control)
The W0 scaffold is **not done** until BOTH hold:
1. `pnpm gate` **exits 0** on the empty app (every real leg SKIP, the W0-armed legs green on a clean tree); and
2. a **deliberately planted boundary violation** (see leg T / import-boundary) makes `pnpm gate` **exit non-zero**.
A gate never seen to fail is unproven — ship the negative-control fixture and show it bite.

### B.3 Leg schedule (which legs arm at W0 vs SKIP-visible)
Mirrors `gate-spec.md`; W0 arms only the product-agnostic legs.

| Leg | Tier | Arms | W0 status | W0 assertion |
|---|---|---|---|---|
| import-boundary (4-lane cut as code) | DevOps VERIFIER | W0 | **ARM** | a cross-lane import FAILS (encodes charter §3) |
| **K · secret-scan** | SecOps ORACLE (DevOps wires) | W0 | **ARM** | committed key pattern / key-in-logs FAILS (§C) |
| **T · provider-taint (static)** | SecOps ORACLE (DevOps wires) | W0 | **ARM** | `@supabase/supabase-js`/service_role outside its module FAILS (§D) |
| dep-audit (CI) | DevOps | W0 | **ARM** | known-vuln dependency FAILS CI |
| lint | DevOps/B3 | W0 | **ARM** | style/error lint on the (empty) tree passes; arms with real rules as code lands |
| typecheck `tsc --noEmit` | BE PARTIAL | W0 | SKIP→ARM | SKIP until a tsconfig/tree exists, then ARM same wave |
| build (workspace) | BE PARTIAL | W0 | SKIP→ARM | SKIP until buildable workspaces exist |
| test / golden-eval | QA/AIQ | spine/AI | ⏸ SKIP | no surface |
| migrate + RLS/policy-lint (4) | DevOps/BE-Data | W1 | ⏸ SKIP | no DB/migrations |
| transport smoke (5) | BE-API | W1 | ⏸ SKIP | **port validated (3000) but do not wire until W1** (LL-1) |
| tenant-isolation (6) | BE-Data | W1 | ⏸ SKIP | cross-tenant read must FAIL with RLS OFF |
| drift guard (7) | DevOps | W1 | ⏸ SKIP | contract/schema drift |
| **M · money-truth** | BE-Data ORACLE | W1 | ⏸ SKIP | billed call bypassing chokepoint `<3.2>` FAILS |
| **C · compliance** | Legal PARTIAL | after Legal `<4.3>` | ⏸ SKIP | rule unwritten = **GAP, not a pass** |
| **O · per-seat oracle legs** | per row | each build wave | ⏸ SKIP | DevOps wires each seat's leg; GA audits coverage |

---

## §C · Leg K — secret-scan (D-TRADE-006a · `<4.1>` no secret in repo/logs)
**Assertion (green means):** no committed secret pattern (SEC / market-data / **Supabase service_role /
DB password**) exists in tracked content, and no key is emitted to logs.

- **Tool:** **gitleaks**, pinned by version + checksum, run in CI (leg K) and offered as a pre-commit hook.
  Chosen for a maintained default ruleset, custom-rule support, SARIF output, and fail-closed exit code.
- **Custom rules (added to the default set) — the HELM denylist (SecOps authors the final list, DevOps wires):**
  - Supabase **service_role** key shape (legacy `service_role` JWT `eyJ…` and the newer `sb_secret_…` form),
  - `SUPABASE_SERVICE_ROLE_KEY=<value>` assignments in tracked files,
  - `DATABASE_URL=postgresql://…:<password>@…` (password-bearing),
  - `SUPABASE_ACCESS_TOKEN` / `sbp_…` PAT shape,
  - `SEC_API_KEY=…` and the Polygon key shape (once `<2.1>` providers lock).
- **Scope:** tracked working tree + history from the pushed baseline (`3d3f1aa`) forward. Key-in-**logs** is
  a runtime egress concern that arms with the app (W1); the W0 arm is the static repo scan.
- **Negative control (proves it bites — a seat OTHER than SecOps can produce it):** the runner injects a
  quarantined fixture containing a **fake** `SUPABASE_SERVICE_ROLE_KEY=eyJ…FAKE…` into a tracked path,
  runs gitleaks → **exit non-zero → leg RED**, then reverts. The fixture is a synthetic non-secret, never a
  real key, and is git-ignored/reverted so it never lands on origin.
- **`.env` hygiene — CONFIRMED 2026-08-01:** `.gitignore` blocks `.env`, `.env.*` (allowing only
  `!.env.example`), plus `*api-key*`, `sec_api_key.txt`, `*.pem`, `.claude/settings.local.json`.
  `.env.example` inspected → **placeholders only** (every secret blank; only the public `SUPABASE_URL`
  populated). No secret is tracked. ✅

---

## §D · Leg T — provider-taint, static (D-TRADE-006c · `<4.2>`)
**Assertion (green means):** `@supabase/supabase-js` **and** the service_role key are **server-data-layer-only**
(the sanctioned `packages/db` / domain data module) — **never in `apps/web`**; Polygon/EDGAR SDKs are
likewise confined to their sanctioned modules.

- **Static mechanism (part of the import-boundary lint — "the 4-lane cut as code"):**
  1. ESLint `no-restricted-imports` (or `eslint-plugin-boundaries`) forbidding `@supabase/supabase-js`
     anywhere under `apps/web/**`;
  2. a scan for `SERVICE_ROLE` / service_role-key references outside the sanctioned server module.
- **Negative control:** plant `import { createClient } from '@supabase/supabase-js'` (service_role client)
  in `apps/web/src/<x>.ts` → **leg RED**. This planted violation doubles as the harness done-bar (§B.2).
- **Runtime egress taint** (a provider host actually contacted outside its module) arms at **W1**; W0 is the
  static import/reference check only.

---

## §E · W0 first-wave DoD (build-ready checklist — from open-items-ledger §D)
Restated with validated values baked. **⏸ NOT dispatchable now (D-TRADE-010);** ready on build-GO.

| Task | Owner | DoD (concrete) |
|---|---|---|
| **W0-0 install toolchain** *(NEW pre-req)* | **Director/human** | Node LTS + pnpm + Docker Desktop installed; `node`/`pnpm`/`docker` on PATH. Blocks every leg below **and** the MCP connector. |
| W0-1 monorepo tree + workspaces | DevOps | root `package.json`, `pnpm-workspace.yaml`, `tsconfig*`, `apps/{api,web}` + `packages/{domain,db,contracts,config}` skeleton; `tsc`/build green on empty app |
| W0-2 local DB stack + baseline migration | DevOps→BE-Data | `docker-compose.yml` (Postgres on **:5432**); DB boots; `migrate` runs clean on `packages/db/migrations/0001_*` |
| W0-3 gate harness (legs SKIP-visible) + CI | DevOps | `scripts/gate/**` + `.github/workflows/**`; `pnpm gate` exits 0 on empty **and** a planted boundary violation makes it FAIL (§B.2) |
| W0-4 import-boundary lint = 4-lane cut as code | DevOps | a cross-lane import FAILS; leg T folded in (§D) |
| W0-5 secret-scan (leg K) + provider-taint (leg T) | DevOps←SecOps denylist | planted fake key → RED (§C); planted `apps/web` provider import → RED (§D) |
| W0-6 validate ports/DB → write back to gate-spec + charter | DevOps→Lead | §A values replace the "planned/NOT validated" rows (LL-1) |
| W0-7 place `.claude/settings.json` | **Director** (human-only) | placed from the committed template; `acceptEdits` active (LL-70 — a `Set-Content` may be refused; ship the template) |

**W0 exit:** `tsc`/build/CI green on the empty app; every other leg exit-visible SKIP; **planted negative
control shown to bite**; QA phase-exit sign-off. W1 unblocks only after the cost/roster locks + product
paragraph `<1.1>` land and the Architect's W1 A0 ADR.

---

## §F · Open blockers / dependencies (surfaced to the Lead, this report)
1. 🟡 **DB baseline (task a) — capture it from the Lead clone.** The connector is **Director-confirmed
   CONNECTED in `Trade - Lead`**, so the baseline is **capturable now from an interactive Lead-clone
   session** (ask Claude to list schemas/tables for `zyscsnhiymitpfdhjuci`; `--read-only`). It was **not**
   capturable from **this** non-interactive DevOps session (no `supabase` MCP tool exposed here,
   `SUPABASE_ACCESS_TOKEN` unset here, `node`/`npx` unresolvable here). Baseline still **UNKNOWN** in
   `docs/infra/supabase.md` until someone runs the introspection.
2. 🟡 **Node/`npx` unresolvable on this host/session — reconcile before W0-0.** The connector runs via
   `npx`, yet `node`/`npx` do not resolve here (checked PATH + standard dirs + nvm/fnm/volta). Either Node
   lives on a path only the Lead's interactive session loads (→ W0-0 bakes that path) or CONNECTED reflects
   `/mcp` trust without a live introspection yet. Confirm which; W0 needs a resolvable `node`/`pnpm`/`docker`
   ($0 tooling; Docker Desktop paid only at org scale — flag FinOps if so).
3. 🟡 **Runtime commit identity** — this clone's git identity was unset; set locally to
   `Mähnbach <noreply@mahnbach.com>` to match the repo convention.
