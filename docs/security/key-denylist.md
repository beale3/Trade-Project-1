# Key denylist — gate leg K (no-secret) — HELM (`trade`)

**Author:** SecOps · **Date:** 2026-08-01 · **Discharges:** D-TRADE-006(a), gate-spec **leg K**, canonical
`<4.1>`, oracle-boundary SecOps row (ORACLE tier).
**Division of labour (builder ≠ judge, protocol 14):** **SecOps authors this rule-set.** **DevOps wires it**
into the CI secret-scan + pre-commit (the "oracle builder"). **GA audits coverage.** **QA re-runs every
planted negative control on phase exit.** I do **not** wire it (mandate: *you author denylists; DevOps
wires them*).
**Arms at:** **W0** (static, CI secret-scan) — SKIP-visible until then (gate-spec rule of green).

## What "green" actually means (fail-closed, never more than the leg asserts — LL-50)
Leg K is RED (build FAILS) when **any tracked file, or any emitted log line, contains a real credential
value** matching a pattern below. Leg K says **nothing** about whether a secret is well-designed (that is
HUMAN / the B5 gate) — only that **no secret value is present in the repo or logs.**

**A denylist without a planted violation is vacuous (LL-48).** Every pattern below ships with a **negative
control**: a concrete input the green *must* reject. DevOps plants each control in a throwaway tracked file
in CI, proves leg K goes RED, then removes it. QA reproduces this on exit. **All control values below are
deliberately FAKE** (well-known dummy/format-only strings) so planting a control never commits a real
secret.

## Two rules every pattern obeys (so the gate bites without false-positiving the scaffold)
1. **Value-bearing, not name-bearing.** A pattern fires on a **populated** assignment, not on an empty
   placeholder. The committed templates — `.env.example` (empty `KEY=` or `<...>`/`[PASSWORD]` placeholders)
   and `.mcp.json`'s `${SUPABASE_ACCESS_TOKEN}` env-indirection — **must stay GREEN**. Each pattern's
   negative-control table lists the placeholder that must NOT trip it.
2. **`.env` is never tracked.** Leg K also asserts no `.env` / `.env.<env>` (anything but `.env.example`) is
   git-tracked. `.gitignore` already excludes them (verified 2026-08-01); the leg proves it, so a future
   `git add -f .env` FAILS.

---

## The scoped secrets (all **B5** — Director installs into the secret store / gitignored `.env`; never chat, never repo)

| # | Secret | Format seen / expected | Sensitivity |
|---|---|---|---|
| K1 | **Supabase `service_role` key** | legacy JWT `eyJ…` with `"role":"service_role"`; new-style `sb_secret_…` | **CRITICAL — bypasses RLS, full DB** |
| K2 | **Supabase DB password / `DATABASE_URL`** | `postgres(ql)://postgres:<PASSWORD>@db.zyscsnhiymitpfdhjuci.supabase.co:5432/postgres` (or pooler) | **CRITICAL — DB superuser** |
| K3 | **Supabase Personal Access Token (MCP)** | `sbp_<hex>` | **HIGH — one-project blast radius (D-TRADE-014)** |
| K4 | **Supabase anon / publishable key** | legacy JWT `eyJ…` `"role":"anon"`; new `sb_publishable_…` | **LOW — RLS-enforced, client-facing; still keep out of git** |
| K5 | **Polygon / Massive API key** | ~32-char alnum (`aB3xK9…`); also `?apiKey=` / `?apikey=` on `api.polygon.io` / `api.massive.com` | **HIGH — billed provider (money-truth)** |
| K6 | **SEC / third-party EDGAR API key** | issuer TBD (77-byte file, `..\Trade\sec_api_key.txt`); public EDGAR is UA-based, no key | **HIGH — billed if a reseller** |
| K0 | **Generic backstop** | tracked `.env*` (non-example); high-entropy assignment to a `*KEY*/*SECRET*/*TOKEN*/*PASSWORD*` var | — |

---

## Patterns + planted negative controls (author's spec — DevOps encodes as regex/entropy legs)

> Notation: patterns are described precisely enough to encode; each row gives a **POSITIVE** (must go RED)
> and the **placeholder that must stay GREEN**. Patterns are **case-insensitive** on the var name and match
> in **any tracked text file** (code, md, json, yaml, env, ipynb) and in **captured log output**.

### K1 — Supabase service_role key  🔴 CRITICAL
- **Pattern a (env-name + JWT value):** an assignment to a var whose name matches
  `SUPABASE.*SERVICE.*ROLE|SERVICE_ROLE_KEY` whose value begins `eyJ` (a JWT header) — RED.
- **Pattern b (role claim, name-agnostic):** any occurrence of a JWT whose decoded payload contains
  `"role":"service_role"` — RED even if the var is renamed/obfuscated. (DevOps: base64url-decode the middle
  segment of any `eyJ…\.eyJ…\.…` token and grep the claim.)
- **Pattern c (new-style secret key):** any literal matching `sb_secret_[A-Za-z0-9]{20,}` — RED.
- **Negative controls:**
  - POSITIVE (→RED): `SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.FAKE_sig_do_not_use`
  - POSITIVE (→RED): `sb_secret_FAKEFAKEFAKEFAKEFAKE1234567890`
  - GREEN (must NOT trip): `.env.example` line `SUPABASE_SERVICE_ROLE_KEY=` (empty)

### K2 — Supabase DB password / DATABASE_URL  🔴 CRITICAL
- **Pattern:** a `postgres://` or `postgresql://` URI with a **non-empty, non-placeholder** password segment
  (`postgres(ql)://[^:@/]+:<pw>@…`) — RED. `<pw>` is real when it is **not** one of the placeholder tokens
  `[PASSWORD]`, `<password>`, `password`, `YOUR_PASSWORD`, `…`. Scope hint (raise confidence): host ends
  `.supabase.co` or `.pooler.supabase.com`.
- **Negative controls:**
  - POSITIVE (→RED): `DATABASE_URL=postgresql://postgres:Sup3rS3cr3tFAKE@db.zyscsnhiymitpfdhjuci.supabase.co:5432/postgres`
  - GREEN (must NOT trip): the `.env.example` line with the literal `[PASSWORD]` placeholder.

### K3 — Supabase Personal Access Token (MCP)  🟠 HIGH
- **Pattern:** `sbp_[A-Za-z0-9]{20,}` in any tracked file — RED. (The token is delivered via the **process
  env** `${SUPABASE_ACCESS_TOKEN}`, per `.mcp.json`; it must **never** appear as a literal.)
- **Negative controls:**
  - POSITIVE (→RED): `SUPABASE_ACCESS_TOKEN=sbp_faketoken0123456789abcdef0123456789`
  - GREEN (must NOT trip): `.mcp.json` value `"${SUPABASE_ACCESS_TOKEN}"` (env indirection, no literal).

### K4 — Supabase anon / publishable key  🔵 LOW (RLS-enforced) — warn-or-fail, SecOps recommends **FAIL** in-repo
- **Pattern a:** JWT with decoded `"role":"anon"` — flag.  **Pattern b:** `sb_publishable_[A-Za-z0-9]{20,}` — flag.
- **Rationale:** the anon key is *designed* for client exposure (RLS is the real control), so it is **not** a
  breach on the scale of K1/K2. But a key committed to git is still an ungoverned secret and complicates
  rotation → SecOps recommends leg K treat it as **FAIL in tracked files** (it belongs in `.env`, not the
  repo), while accepting it *may* legitimately ship inside a built `apps/web` bundle at runtime (out of leg
  K's scope). **Final severity of K4 is a Director/GA call** — I flag, I don't rule.
- **Negative controls:**
  - POSITIVE (→RED): `SUPABASE_ANON_KEY=sb_publishable_FAKEpublishable1234567890`
  - GREEN: `.env.example` line `SUPABASE_ANON_KEY=` (empty).

### K5 — Polygon / Massive API key  🟠 HIGH (billed)
- **Pattern a (env-name):** assignment to `POLYGON.*KEY|MASSIVE.*KEY|POLYGON_API_KEY|MASSIVE_API_KEY` with a
  value of ≥20 alnum chars — RED.
- **Pattern b (in-URL key):** `api\.(polygon|massive)\.(io|com)/[^\s"']*[?&]api[_-]?key=[A-Za-z0-9_-]{20,}`
  — RED (catches a key pasted into a URL, incl. in logs/network dumps).
- **Negative controls:**
  - POSITIVE (→RED): `POLYGON_API_KEY=aB3xK9fakeKEYfakeKEYfakeKEY0000`
  - POSITIVE (→RED): `https://api.massive.com/v2/aggs?apiKey=aB3xK9fakeKEYfakeKEY0000`
  - GREEN: `.env.example` line `POLYGON_API_KEY=` (empty).

### K6 — SEC / third-party EDGAR API key  🟠 HIGH (if a reseller)
- **Pattern:** assignment to `SEC_API_KEY|SEC_API_TOKEN|EDGAR_API_KEY` with a ≥20-char value — RED. Once the
  Director/Data-Eng **confirms the key's issuer** (open item in `tos-taint-review.md`), add that issuer's
  concrete token prefix/format here (e.g. an `sec-api.io` token shape) for a tighter match.
- **Negative controls:**
  - POSITIVE (→RED): `SEC_API_KEY=fakeSECkey0123456789abcdef0123`
  - GREEN: `.env.example` line `SEC_API_KEY=` (empty), and the existing gitignored `sec_api_key.txt` (already
    ignored; leg K asserts it is **not** tracked).

### K0 — Generic backstop  ⚙️
- **Pattern a (tracked env file):** any tracked path matching `**/.env` or `**/.env.*` **except**
  `**/.env.example` — RED (defends against `git add -f`).
- **Pattern b (high-entropy assignment):** an assignment to a var name matching
  `.*(KEY|SECRET|TOKEN|PASSWORD|PASSWD|CREDENTIAL).*` whose value has Shannon entropy above DevOps's tuned
  threshold **and** is not a known placeholder — RED. This is the catch-all for a secret we didn't
  enumerate; DevOps tunes the threshold against the scaffold so templates stay green.
- **Negative controls:**
  - POSITIVE (→RED): a tracked file literally named `.env.production` containing any line.
  - POSITIVE (→RED): `SOME_NEW_TOKEN=Zx9Q2pL7vT4mN1kR8sW3yB6dF0hJ5aE` (high-entropy, unlisted).
  - GREEN: every current `.env.example` placeholder line; `${SUPABASE_ACCESS_TOKEN}` in `.mcp.json`.

---

## Also in scope of "no-secret" (not a regex, a discipline)
- **Key-in-logs:** the leg scans **captured log output**, not just files — a `console.log(serviceRoleKey)` or
  a request-dump that echoes `?apiKey=…` FAILS. Provider clients must never log full credentials or the
  Authorization header (redact to a prefix).
- **Loud + fail-closed:** an auth failure on any provider **stops and says so** — never a silent
  under-fetch/no-op (SecOps lessons block). Out of leg K's mechanical scope but a review checkpoint at W1.

## Coverage note handed to GA (protocol 14 admission test)
Every row above ships a **reproducible negative control a seat other than SecOps can run** (DevOps plants it,
QA re-runs it) — satisfying the admission test ("show me the input this green would reject"). Rows K4 and K6
carry an **open severity/format item** (anon-key policy = Director/GA; EDGAR issuer = Director/Data-Eng);
until resolved they are marked here so an unclosed item cannot read as covered.
