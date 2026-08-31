# B5 — Key & Secrets Approval Gate (checklist) — HELM (`trade`)

**Author:** SecOps · **Date:** 2026-08-01 · **Status:** DRAFT for the Lead/Director.
**Authority:** gate-spec §9 (*"B5 key & secrets approval = HARD launch blocker"*), D-TRADE-013/-014, canonical
`<4.1>`, `docs/infra/supabase.md`.
**Rule of the gate:** **no secret is generated, installed, or wired until this checklist is signed.** It is a
**HARD launch blocker** — a green build with an unsigned B5 is not launchable.
**Co-sign rule (builder ≠ judge):** the **Director approves** every secret and **SecOps co-signs**; **the
Lead may not self-approve** a secret (oracle-boundary: the Lead's own output is not exempt). The **agent
never sees, enters, or echoes** a secret value — the Director installs it directly into the secret store /
gitignored `.env` (B5). Discovery/verification below is done by the human; the agent only checks the
*artifacts* (leg K armed, `.env` untracked), never the values.

---

## Pre-condition — arm the net before any secret exists
- [ ] **Leg K is ARMED** and its negative controls bite (see `key-denylist.md`): DevOps has planted each
      POSITIVE control and shown leg K goes **RED**, and confirmed the `.env.example` / `${…}` placeholders
      stay **GREEN**. *(A secret installed before the scanner is armed can leak into a later commit
      undetected — arm first, LL-48.)*
- [ ] **`.env` is git-ignored and untracked** (verified 2026-08-01; re-verify at install time — a clean local
      tree ≠ a safe one).
- [ ] **Leg T** sanctioned-module rules are recorded (`tos-taint-review.md`) so a key can only be *referenced*
      from its allowed module once code exists.

## Step 1 — Inventory the FULL secret set for the phase in ONE pass (LL-29)
*Discover every secret this phase will ever need before the first install — a late-surfacing secret forces a
second slow approval round. Batch it.* Current known set:

| ID | Secret | Provider | Class | Least-privilege target | Sanctioned module (leg T) |
|---|---|---|---|---|---|
| S1 | `service_role` key | Supabase | B5 CRITICAL (RLS-bypass) | server-only; **never** shipped to `apps/web` | `packages/db` / domain money-truth |
| S2 | DB password / `DATABASE_URL` | Supabase | B5 CRITICAL | migration runner + server data layer only | `packages/db` |
| S3 | Personal Access Token | Supabase MCP | B5 HIGH | **read-only**, `--project-ref=zyscsnhiymitpfdhjuci` (D-TRADE-014) | `.mcp.json` via process env only |
| S4 | anon / publishable key | Supabase | LOW (RLS-enforced) | client-side OK; out of git | `apps/web` runtime + `.env` |
| S5 | Massive (Polygon) API key | Massive | B5 HIGH (billed) | personal/individual tier — matches `<1.2>` (2026-08-01 pivot; was Business-tier-required, now re-scoped LOW-MEDIUM taint); server-only | data-layer ingestion |
| S6 | SEC-API.io key | SEC-API.io | B5 (LOW taint, still a real secret) | personal-tier subscription — confirmed 2026-08-01; server-only | Data-Eng ingestion module |

- [ ] Inventory reviewed against the design — **no secret surfaces later** without re-entering this gate.
- [x] ~~Open blockers: S5 tier, S6 issuer confirmation~~ — **CLEARED 2026-08-01** (D-TRADE-020 pivot +
      SecOps confirmation, `docs/security/tos-taint-review.md`). Residual, non-blocking: Director may
      optionally verify the exact Massive plan name on the account dashboard.
- [x] **S6 rotation — DONE 2026-08-30.** The Director rotated the SEC-API.io token at the provider
      dashboard; the Lead independently verified the old value was still live (HTTP 200) before rotation
      and the new value is live (HTTP 200) after — see `activity-log.md`. `float-study/log_pull.txt`
      (the exposure site) deleted entirely. **This closes the pre-condition, not Step 3's sign-off** —
      Director-approves + SecOps-co-signs for S6 is still unchecked below.

## Step 2 — Per-secret approval (repeat for each S#)
For every secret in the inventory:
- [ ] **Classified** (CRITICAL / HIGH / LOW) and its **blast radius** stated (what it can do if leaked).
- [ ] **Least privilege at generation:** narrowest scope, correct env, read-only where possible (S3 is
      read-only + single-project already). **Fresh, per-environment** values — no shared dev/prod secret.
- [ ] **Provider terms honoured:** the credential's use matches the ToS tier read in `tos-taint-review.md`
      (esp. S5 Business-tier; S1/S2 RLS-bypass stays server-side per Supabase's customer-credential duty).
- [ ] **Storage = secret store / gitignored `.env`** — **never** in chat, a tracked file, a commit message,
      a log, or a screenshot. The Director installs the value directly.
- [ ] **Rotation policy** set (owner + cadence; immediate rotation if ever exposed — `docs/infra/supabase.md`).
- [ ] **Fail-closed + loud:** a job that cannot authenticate with this secret **stops and says so** — no
      silent failure that eats data/evidence (SecOps lessons block).
- [ ] **Post-install proof:** after install, leg K is re-run and stays **GREEN** (no value leaked into the
      tree); connectivity verified by the **human in their own terminal** (`docs/infra/supabase.md` curl
      pattern) so the key stays local, never in chat.

## Step 3 — Sign-off matrix (both required; Lead may not self-approve)
| Secret | Director approves | SecOps co-signs | Installed (store/`.env`) | Leg K re-run GREEN | Date |
|---|---|---|---|---|---|
| S1 service_role | ☐ | ☐ | ☐ | ☐ | |
| S2 DB password | ☐ | ☐ | ☐ | ☐ | |
| S3 MCP PAT | ☐ | ☐ | ☐ | ☐ | |
| S4 anon key | ☐ | ☐ | ☐ | ☐ | |
| S5 Massive/Polygon | ☐ | ☐ | ☐ | ☐ | |
| S6 SEC-API.io (rotate first) | ☐ | ☐ | ☐ | ☐ | |

## Step 4 — Standing controls (remain true after sign-off)
- [ ] **Write access stays closed** on Supabase MCP — opening write is a **later Director-gated change** that
      **re-enters this gate** (D-TRADE-014; money-truth surface).
- [ ] **Real credentials at n=1 are still real** — dev-phase keys get production discipline (SecOps lessons).
- [ ] **Exposure → rotate immediately**, re-run leg K, and log the incident.
- [ ] **The external-user line:** the first outside user brings the full legal/privacy/hardening pack — no
      secret posture is signed as "launch-ready" until Legal (`<4.3>`) and the hardening review clear that line.

---

**Sequence note (D-TRADE-010):** filling `.env` + verifying connectivity is **infra prep and is permitted
now**; **wiring app code against these secrets is W0/W1 build** and still waits on a Director build-GO. This
checklist may be *satisfied for infra prep* ahead of build, but its Step-4 launch controls only close at
operational readiness (B10).
