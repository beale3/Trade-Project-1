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

## Governance
- **SecOps:** run the Supabase **ToS-as-taint** check + own the key denylist; the provider SDK/host is
  usable only from its sanctioned module (gate leg T). Provider credentials referenced only there (B4 L2).
- **B2 pillar ②** tenant isolation via Supabase RLS — proof = a gate leg that FAILS with RLS OFF.
- **Sequence note (D-TRADE-010):** filling `.env` + verifying connectivity is DevOps/SecOps infra prep and
  is fine; **wiring app code against it is W0/W1 build** and still waits on a build-GO.
