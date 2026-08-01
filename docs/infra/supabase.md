# Supabase connection — HELM (`trade`)

Adopted DB (D-TRADE-013). This documents **how seats connect** and **who handles the secrets**. It holds
**no secret values** — those live only in a gitignored `.env` / secret store the Director installs (B5).

## Project
| Field | Value | Sensitivity |
|---|---|---|
| Project ref | `zyscsnhiymitpfdhjuci` | public |
| API URL | `https://zyscsnhiymitpfdhjuci.supabase.co` | public |
| Reachability | ✅ verified 2026-08-01 (`/auth/v1/health` responds; REST `/rest/v1/` → 401 = alive, needs apikey) | — |
| DB host (direct) | `db.zyscsnhiymitpfdhjuci.supabase.co:5432` (or the pooler from Project Settings → Database) | host public; **password SECRET** |

## Credentials — the boundary (B5 / SecOps)
| Value | Where it lives | Who installs | Agent may see? |
|---|---|---|---|
| `SUPABASE_URL` | `.env` (gitignored) | anyone | yes (public) |
| `SUPABASE_ANON_KEY` (publishable, RLS-enforced) | `.env` | Director/DevOps | avoid in chat; put straight in `.env` |
| `SUPABASE_SERVICE_ROLE_KEY` (bypasses RLS) | secret store / server-only `.env` | **Director/SecOps only** | **NO — never in chat or repo** |
| DB password / `DATABASE_URL` | secret store / `.env` | **Director/SecOps only** | **NO — never in chat or repo** |

**Rules:** `.env` is gitignored (verified) — never commit it. The service-role key and DB password are
full-access; the agent never enters or echoes them. Rotate the key if it is ever exposed. At B5 the
Director personally approves every prod secret; fresh per-env keys go **into the store, not the repo**.

## How a seat connects (once `.env` is filled)
- **App/server (BE-API/BE-Data lane):** read from `process.env` via `@supabase/supabase-js` (anon key
  client-side / RLS; service_role server-side only, inside the money-truth/domain layer) — wired at W0/W1.
- **DB migrations (BE-Data):** `DATABASE_URL` → the migration runner; forward-only reviewed migrations
  under `packages/db/migrations`; every tenant table gets RLS + policy-lint (gate legs 4/6).
- **Quick local liveness test (run in YOUR terminal — key stays local, not in chat):**
  ```bash
  curl -s "$SUPABASE_URL/rest/v1/?apikey=$SUPABASE_ANON_KEY" -o /dev/null -w "%{http_code}\n"   # 200 = connected
  ```

## MCP connector (team-wide, read-only) — D-TRADE-014
> ✅ **CONNECTED — Director-confirmed 2026-08-01.** Live in sessions launched inside the `Trade - Lead`
> clone (the `.mcp.json` is project-scoped there). Not available to the Lead's umbrella-parent session.
> First recommended use: a read-only baseline introspection (list schemas/tables) to record the DB's
> starting state in this doc.

The official **Supabase MCP server** is wired as a **project-scoped `.mcp.json`** at the repo root, so
every clone inherits it. Config (committed, secret-free — token is `${SUPABASE_ACCESS_TOKEN}` from the
environment): `npx -y @supabase/mcp-server-supabase@latest --read-only --project-ref=zyscsnhiymitpfdhjuci
--features=database,docs,debugging`.

- **`--read-only`** by default — seats can query schema/data + read docs, but **cannot mutate** the DB via
  MCP. Write access is a deliberate, later, Director-gated change (money-truth surface — never open write
  by default).
- **`--project-ref` scoped** to `zyscsnhiymitpfdhjuci` — the token's blast radius is one project.

### Director setup (interactive — this session can't run the OAuth/enable flow)
1. **Create a Personal Access Token:** Supabase dashboard → **Account → Access Tokens → Generate** (name it
   e.g. `helm-mcp-readonly`). This is a SECRET; treat it like a password.
2. **Put it in the environment** (Claude Code expands `${SUPABASE_ACCESS_TOKEN}` from the process env, not
   from `.env`). PowerShell, persistent for your user:
   ```powershell
   setx SUPABASE_ACCESS_TOKEN "sbp_your_token_here"
   ```
   Then open a **new** terminal so it takes effect. (Do not paste the token into chat or any tracked file.)
3. **Approve the project MCP server:** launch Claude Code in the `Trade - Lead` clone and run **`/mcp`** →
   approve/trust the `supabase` server (project-scoped servers require explicit approval on first use).
4. **Verify:** ask Claude "list Supabase tables" (or run the `/mcp` health view). It should connect
   read-only to project `zyscsnhiymitpfdhjuci`.

> Note: this non-interactive founding session cannot itself authenticate or use the connector — it authored
> the config; **you enable it interactively** per the steps above. Once enabled, spawned seats in this repo
> inherit the same `.mcp.json`.

## DB Baseline (pre-W0 — is the DB empty or populated?)
We must know the DB's starting state **before** W0 designs day-one migrations. Attempted 2026-08-01 via the
read-only MCP connector (D-TRADE-014).

| Field | Result (2026-08-01) |
|---|---|
| Schemas / tables | **UNKNOWN — baseline NOT captured** (blocked, see below) |
| Host reachability | ✅ alive (`/auth/v1/health` responds; REST → 401 = needs apikey) |
| Capture method | read-only Supabase MCP connector (introspect schemas/tables) — the only agent-safe route (direct DB / service_role require a SECRET the agent must never handle) |

**Where it stands:** the connector is **Director-confirmed CONNECTED in the `Trade - Lead` clone** (banner
above) — so the baseline **can be captured now from an interactive Lead-clone session**; it does not need
this DevOps clone. It was simply **not capturable from this (non-interactive DevOps) session**:
1. **No `supabase` MCP tool is exposed to this session**, and `SUPABASE_ACCESS_TOKEN` is not set in this
   session's environment (a non-interactive session cannot run the `/mcp` approve / OAuth flow).
2. **`node`/`npx` do not resolve on this host/session** (checked PATH + standard install dirs + nvm/fnm/
   volta). `.mcp.json` launches the server via `npx`, so this session could not start it regardless.

> ⚠️ **Reconcile (Director/Lead):** the connector runs via `npx`, yet this host/session cannot resolve
> `node`/`npx`. Either Node lives on a path only the Lead's interactive session loads — in which case W0-0
> must bake that exact path — or the CONNECTED status reflects `/mcp` trust without a live introspection
> yet. Confirming which matters for the W0 toolchain (`docs/roles/devops/harness-design.md §A/§F`).

**To capture the baseline now** (interactive Lead-clone session): ask Claude to *list schemas and tables for
project `zyscsnhiymitpfdhjuci`* (the connector is `--read-only`, so this cannot mutate the DB). Record the
schema/table list (or "empty") into the table above. Alternatively a human reads it from the Supabase
dashboard → Table editor and pastes the table names here — no secret required for that.

## Governance
- **SecOps:** run the Supabase **ToS-as-taint** check + own the key denylist; the provider SDK/host is
  usable only from its sanctioned module (gate leg T). Provider credentials referenced only there (B4 L2).
- **B2 pillar ②** tenant isolation via Supabase RLS — proof = a gate leg that FAILS with RLS OFF.
- **Sequence note (D-TRADE-010):** filling `.env` + verifying connectivity is DevOps/SecOps infra prep and
  is fine; **wiring app code against it is W0/W1 build** and still waits on a build-GO.
