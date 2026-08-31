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
- [x] **S6 — CLOSED 2026-08-30. Exposure confirmed, no evidence of malicious use, proactively and fully
      remediated.** Found in plaintext in `float-study/log_pull.txt` (outside this repo, leaked into old
      DNS-failure exception tracebacks); the Lead independently verified the old value was still live
      (HTTP 200) before rotation, the Director rotated at the provider dashboard, and the Lead verified
      the new value live (HTTP 200) after — see `activity-log.md`. Exposure site deleted entirely. No
      evidence surfaced, at any point, of third-party use of the old value — this closure states that
      plainly rather than leaving it implied. Director + SecOps sign-off both recorded in Step 3 below.
- [x] **S5 — third rotation, 2026-08-31, CLOSED. Exposure this time was the Lead's own mistake — logged
      plainly, not smoothed over.** While investigating why SDE1's D-TRADE-038 pull was hitting HTTP 401
      (a separate, unrelated blocker — see `open-items-ledger.md` item 20), the Lead ran `env | grep -i
      MASSIVE` in the Bash tool to check whether the env var was propagating, without first considering
      that grep's output would include the actual value — it did, and the live key value was printed
      directly into this session's own transcript. **Disclosed to the Director immediately, no attempt to
      hide or minimize it.** Director provided a new key (`Trade\MASSIVE_api_key.txt`) — Lead-verified:
      live (HTTP 200, value never printed this time), and via SHA-256 hash comparison (neither value
      displayed) confirmed genuinely different from the prior value. Installed to both real locations and
      re-verified live at each: the User-scope `MASSIVE_API_KEY` env var and `Trade - Lead\
      massive_api_key.txt`. **Exposure site this time is a Claude Code session transcript, not a
      deletable log file like `log_pull.txt` was** — the Lead flagged this distinction to the Director
      explicitly and did not unilaterally decide how to handle the transcript itself; rotation makes the
      exposed value harmless regardless of where it sits, and no further transcript-specific action has
      been requested.
- [x] **S5 — second rotation, 2026-08-30, CLOSED (supersedes the transcript-candidate question rather than
      resolving it).** Director provided a genuinely new key (`Trade\MASSIVE_api_key.txt`) — Lead-verified: live
      (HTTP 200, value never printed) and, via SHA-256 hash comparison against the prior value (never
      displaying either), **confirmed different from what was in `Trade - Lead\massive_api_key.txt`
      before this rotation** — this is a real new value, not the same one relocated. **Installed to both
      locations the running code actually reads and re-verified live at each:** the User-scope
      `MASSIVE_API_KEY` env var (`[Environment]::GetEnvironmentVariable` read-back → live call → HTTP 200)
      and `Trade - Lead\massive_api_key.txt` (HTTP 200). **The unresolved transcript candidate
      (`517ca982-...jsonl`, below) is explicitly NOT resolved by this — it's superseded:** whatever that
      candidate was, real or placeholder, the key it might describe is no longer the live one either way.
      Director's explicit instruction: this rotation closes S5 regardless of what the transcript
      question's answer would have been.
- [x] **S5 command-bar/rotation history — Exposure confirmed, no evidence of malicious use, proactively and fully
      remediated.** Director-reported (initially misattributed to S6, corrected same session): the
      Massive API key was pasted into a command bar the first time it was used; the Director's partner
      flagged this as bad practice at the time; Director confirms the key was rotated afterward. **Mixed
      evidentiary basis, stated plainly — not identical to S6's:** the rotation-in-response-to-the-flag
      itself is Director-attested, not independently checkable (no persistent artifact like `log_pull.txt`
      to inspect before/after). What the Lead did independently verify: (1) `massive_api_key.txt.template`
      in `Trade - Lead` has never had a real key committed to it across its git history (`git log -p`
      checked directly, despite the template's own header noting this "has happened twice already" as a
      general caution); (2) the real `massive_api_key.txt` is properly gitignored and was never committed;
      (3) the **current** key is live — one authenticated call to `api.massive.com`, value never printed,
      returned **HTTP 200**. That confirms today's value is real and working, not that it's specifically
      the post-rotation replacement — the Director's account is the source for that link. Logged, not
      hidden. SecOps's original Step 2/co-sign predated this information — re-confirmation requested
      separately (see `activity-log.md`).
- [ ] **S5 shell/transcript history check — left genuinely unresolved, but no longer blocking (superseded
      2026-08-30 by the second rotation above).** Kept open rather than marked done — the candidate below
      was never actually ruled in or out; closing S5 didn't answer this question, it made the answer stop
      mattering for current risk. Historical record only from here. Acting
      on SecOps's re-confirmation recommendation (above): checked PowerShell `ConsoleHost_history.txt`
      (0 matches), bash/zsh history (no such file exists on this machine), and Windows Run-box MRU
      (0 entries) — all clean, count/existence-only checks, nothing printed. Also scanned this project's
      23 local Claude Code session transcripts (`~/.claude/projects/C--Users-beale-Software-Dev/*.jsonl`)
      for an `apiKey=`/`MASSIVE_API_KEY=` pattern followed by a real (non-placeholder-shaped) 20+ char
      token — 2 of 3 candidate matches read as placeholder/example text (checked for "your"/"example"-class
      wording, not printed); **1 candidate does NOT read as a placeholder** —
      `517ca982-2b50-41cb-ab85-4da846eb94f2.jsonl`, line 1571, file dated 2026-08-23. Attempted to
      determine via SHA-256 hash comparison against the current on-disk key (would confirm/rule out a match
      **without ever displaying either value**) — **blocked by the permission classifier** before
      completing. Not resolved. Value never displayed at any point in this check. See the Lead's
      in-chat report for what's needed to close this.

## Step 2 — Per-secret approval (repeat for each S#)

**2026-08-30 — SecOps review, dispatched by the Lead (open-items-ledger item 13), executed this session.**
Scope as assigned: classification+blast-radius, least-privilege-at-generation, ToS-tier match, storage
location, rotation policy — for all six secrets. **Leg K re-run and "Installed" verification explicitly
OUT of scope** (leg K blocked on DevOps's gate-harness build, not yet done; "Installed" is a separate
artifact-check I wasn't asked to verify and didn't). Method: re-read `tos-taint-review.md` and
`docs/infra/supabase.md` fresh rather than relying on memory (dispatch-freshness); verified `.gitignore`
and `git ls-files` myself rather than trusting the prior "verified" note (verify-don't-attest).

| # | Classification + blast radius | Least privilege at generation | ToS-tier match | Storage | Rotation policy |
|---|---|---|---|---|---|
| **S1** service_role | **CRITICAL.** Bypasses RLS entirely — full read/write/delete on every table in project `zyscsnhiymitpfdhjuci` if leaked. No scoped/read-only variant exists for this key type (Supabase design, not a gap here). | **Structural limit, not a gap:** Supabase issues `service_role` pre-scoped to one project only — there is no finer grain to request at generation. The compensating control is entirely at *use*-time: server-only, never `apps/web`/client, never CI logs (leg T). Confirmed: no code in this repo references it yet (`<3.5>` — Supabase retained **read-only** this phase; a write path is a later, separately-gated step) — so today's actual exposure surface is zero beyond "sits in the store." | N/A (Supabase has no purchased tier concept; the applicable ToS duty is *"security and use of access credentials... with or without Customer's knowledge or consent"* is 100% ours — `tos-taint-review.md` Provider 3, re-confirmed this session). | ✅ `.gitignore` covers `.env`/`.env.*` (excl. `.env.example`); `git ls-files` confirms **no `.env*` tracked** (checked fresh, not assumed). Director-only install per `docs/infra/supabase.md`. | Owner: Director. Policy on file (`supabase.md`): *"Rotate the key if it is ever exposed"* — **exposure-triggered only, no proactive cadence set.** Given CRITICAL blast radius, I recommend the Director consider a periodic (e.g. annual) rotation on top of exposure-triggered — **recommendation, not a blocker.** |
| **S2** DB password / `DATABASE_URL` | **CRITICAL.** DB-superuser equivalent if leaked — same blast radius class as S1, different path (direct Postgres vs. REST). | Same structural note as S1 — Supabase doesn't offer a scoped DB credential; use-time confinement (migration runner + server data layer only) is the real control, and no migration runner exists in this repo yet. | Same as S1 — no tier; credential-security duty is ours entirely. | Same verification as S1 — ✅ gitignored, untracked, Director-only install. | Same as S1 — exposure-triggered only; same recommendation for a proactive cadence. |
| **S3** MCP Personal Access Token | **HIGH.** Scoped to one project already (`--project-ref=zyscsnhiymitpfdhjuci`), **read-only** (D-TRADE-014) — blast radius is data *exposure* (schema/data read), not data *loss/corruption*. Meaningfully smaller than S1/S2. | ✅ **Best practice already applied at generation** — this is the one secret in the set where least-privilege was designed in up front (read-only + single-project), not left to use-time discipline alone. Nothing further to recommend. | N/A (Supabase PAT, not a purchased tier). Read-only scope itself is the ToS-relevant control — write access opening is a separately-gated future change (D-TRADE-014), not silently expanded. | ✅ Same verification as S1/S2 — delivered via `${SUPABASE_ACCESS_TOKEN}` env-indirection in `.mcp.json` (confirmed: the committed file holds only the `${...}` placeholder, never a literal). | Owner: Director. Same exposure-triggered policy; lower urgency given read-only scope already caps the downside. |
| **S4** anon / publishable key | **LOW.** RLS-enforced by design — Supabase's own model expects this key to be client-visible; a leak doesn't bypass any control RLS already provides. | ✅ Designed for exposure — the *only* least-privilege lever left is "don't also commit it to git for no reason," which is already the leg K rule. | N/A. | ✅ Same verification — kept out of tracked files by convention even though runtime client exposure is expected/safe. | Not exposure-sensitive in the same sense as S1-S3; standard rotation only if RLS policies themselves are found unsound (a different, non-SecOps review). |
| **S5** Massive (Polygon) key | **HIGH (billed), taint LOW-MEDIUM (re-confirmed).** Blast radius if leaked = **spend abuse** (someone runs up the Director's bill) more than data exposure — Massive market data isn't sensitive in the way DB credentials are. Taint re-confirmed against `tos-taint-review.md`'s live-updated verdict (personal/individual tier matches `<1.2>`, entitlement-checked non-real-time). Classification **unchanged** by the command-bar incident below — a use-time handling mistake doesn't change what the credential *is*. | Massive issues one key per account at the plan-tier's fixed scope — no finer grain available at generation (same structural note as S1/S2, different provider). Recommend confirming only **one** live key exists (not stale duplicates from earlier research scripts) — I did not verify this myself (would require account-dashboard access, B5-restricted); flagging as a Director/DevOps check, not claiming it's done. | ✅ Matches the compliant personal/individual tier per `tos-taint-review.md`'s LOW-MEDIUM verdict — no commercial-use incompatibility found. | ✅ `.gitignore` now also covers `massive_api_key.txt` + generic `*api-key*`/`*api_key*` patterns (verified — broader than at my first review). **Updated 2026-08-30, re-review requested by the Lead:** the Step 1 note above records a **command-bar paste** on first use — a storage-adjacent vector my original review didn't check (I verified repo/git storage, not shell/terminal-history persistence). **New recommendation, not yet actioned by anyone as far as this doc shows:** whoever's terminal the paste happened in should check (and clear, if present) shell history (PowerShell `ConsoleHost_history.txt` / bash `.bash_history`) and any Claude Code session transcript where the raw value might have been echoed — the same class of check that found `log_pull.txt` for S6. I can't do this myself: the incident's own location ("the first time it was used") isn't identified in what's been reported to me, and it's very likely outside this SecOps clone's own session/filesystem scope. Flagging as an open action, not claiming it's done. | Owner: Director. Billing-abuse risk is better mitigated by FinOps's spend guard (`<3.2>`, NN-8) than by rotation cadence alone — recommend FinOps confirm the guard covers this key's calls once `helm/spend/` exists. **Updated:** exposure-triggered rotation is no longer purely theoretical for this key — matching S6's now-established pattern, the policy has **already been exercised once** (Director-attested rotation following the command-bar flag; independently verified: today's value is live, HTTP 200). |
| **S6** SEC-API.io key | **Taint LOW (confirmed), blast radius HIGH-ish (billed, quota).** This is the one secret with a **closed, verified exposure incident** (item 11): found in plaintext in `float-study/log_pull.txt`, Director rotated at the provider, Lead independently re-verified the *new* value live (HTTP 200) — real, checkable evidence, not an unverified claim. | Personal & Startups tier (D-TRADE-026/027) — no finer grain offered by the provider. **One residual gap, surfaced for completeness (protocol 15/16 — nothing under the rug):** the *old*, exposed token's actual invalidation at the provider dashboard was never independently re-confirmed (only the new token's liveness was checked post-rotation, per the Director's own "do not persist the old value" instruction during the verification call — a reasonable tradeoff, not a mistake). **Practical risk is already low** — the only place the old value was ever exposed (`log_pull.txt`) is deleted, so re-confirming its dashboard-side death is a nice-to-have, not a live threat. Not a blocker. | ✅ Matches confirmed Personal & Startups tier — redistribution-exclusion terms satisfied under `<1.2>` personal use, per `tos-taint-review.md`. | ✅ Same gitignore verification; exposure site (`log_pull.txt`) confirmed **deleted entirely**, not just excluded from tracking. | **Already exercised once, successfully** (item 11) — the working model for future exposures. Standing policy: exposure-triggered, Director-executed, Lead/SecOps-verified post-rotation via a real authenticated call (not a claim). |

**Fail-closed + loud** (all six): no code path exists yet for any of these (Phase 1 hasn't reached `helm/ingest/`
build) — this criterion is **not yet applicable/testable**, not satisfied-and-verified. Flagging honestly
rather than checking a box I can't back with evidence; re-verify once ingestion code exists (SDE1/Data-Eng
build, NN-6/NN-7).

**Post-install proof** (all six): **explicitly OUT of scope this pass** per the Lead's dispatch — leg K
re-run is blocked on DevOps's gate-harness build (not yet done). Human connectivity-verification (the
`docs/infra/supabase.md` curl pattern) is the Director's own action, not something I can attest to.

**SecOps assessment: no blocking finding on any of the six.** All residual items above are recommendations
(proactive rotation cadence for S1/S2, one-key confirmation for S5, old-token dashboard re-check for S6) —
none blocks the co-sign below. Two items are honestly marked not-yet-verifiable (fail-closed behavior,
post-install leg K) rather than checked off without evidence.

## Step 3 — Sign-off matrix (both required; Lead may not self-approve)
| Secret | Director approves | SecOps co-signs | Installed (store/`.env`) | Leg K re-run GREEN | Date |
|---|---|---|---|---|---|
| S1 service_role | ☑ | ☑ | ☐ **NOT FOUND** | ☑ | 2026-08-30 |
| S2 DB password | ☑ | ☑ | ☐ **NOT FOUND** | ☑ | 2026-08-30 |
| S3 MCP PAT | ☑ | ☑ | ☑ **FOUND** | ☑ | 2026-08-30 |
| S4 anon key | ☑ | ☑ | ☐ **NOT FOUND** | ☑ | 2026-08-30 |
| S5 Massive/Polygon | ☑ | ☑ *(on secret class, not tied to a specific value; see note below)* | ☑ **CONFIRMED (2nd rotation)** | ☑ | 2026-08-30 |
| S6 SEC-API.io (rotate first) | ☑ | ☑ | 🟡 **FOUND, wrong scope** | ☑ | 2026-08-30 |

> **DevOps artifact-check basis (2026-08-30, open-items-ledger item 13 — leg K + "Installed," this session).**
> Per B5's own rule: this is a **presence/location check only** — no secret value was ever read, printed,
> or logged. Method: `git ls-files` / filesystem existence checks across every live clone
> (`Trade - Lead`, `Trade - DevOps`, `SecOps`, `AI-ML`, `AIQ`, `Architect`, `Designer`, `FinOps`, `SDE1`)
> plus `[Environment]::GetEnvironmentVariable` at `User`/`Machine`/`Process` scope (boolean presence only).
>
> - **Leg K re-run GREEN — all six, unconditionally.** Leg K scans the full tracked repo regardless of
>   which secrets exist where; it is now built (`scripts/gate/{run.py,legs/secret_scan.py}`), self-test
>   PASSED (every K0-K6 positive control goes RED, every documented placeholder/env-indirection stays
>   GREEN, `key-denylist.md`'s own examples don't self-trip), the real tracked-repo scan is GREEN, and a
>   live end-to-end check (stage a real K5-shaped violation → RED → unstage/delete → GREEN again, nothing
>   ever committed) confirms the runner is honest, not vacuous (LL-48).
> - **S3 (MCP PAT) — FOUND.** `SUPABASE_ACCESS_TOKEN` is a persistent **User**-scope environment variable
>   (survives new sessions, not just this one) — matches D-TRADE-014's env-indirection design exactly.
> - **S5 (Massive) — PRESENT in two places, but this is a different question from "confirmed safe."** A
>   persistent **User**-scope `MASSIVE_API_KEY` env var, **and** a real (non-template) `massive_api_key.txt`
>   in the `Trade - Lead` clone specifically (not in any other clone I checked) —
>   `_resolve_massive_api_key()` checks the env var first, so this is redundant-safe *as an install*. **This
>   check ran before I rebased onto SecOps's same-day S5 REOPENING** (Step 1 above — an unresolved
>   transcript-history candidate the Lead couldn't rule in or out, blocked by a permission classifier).
>   Presence/location — what I was asked to check — is not the same question as "is the value sitting in
>   these locations the exposed one or the rotated one" — my artifact-check has no way to answer that (and
>   per B5 I never read the value to try). **Not marking this a clean "Installed" close** — see the Step 3
>   row above, deliberately marked PRESENT-not-confirmed-safe rather than a flat ☑, until S5's reopening
>   resolves.
> - **S1 / S2 / S4 (Supabase service_role / DB password / anon) — NOT FOUND anywhere I checked.** No `.env`
>   file exists in any of the nine clones above, and none of `SUPABASE_URL` / `SUPABASE_ANON_KEY` /
>   `SUPABASE_SERVICE_ROLE_KEY` / `DATABASE_URL` are set as an environment variable at any scope. **Leaving
>   these three unchecked rather than marking "Installed" without evidence** (same discipline SecOps used
>   in Step 2 for the fail-closed/post-install rows) — this is an honest gap, not a claim of completion.
>   Consistent with `<3.5>`: Supabase is read-only this phase and no code references these yet, so this is
>   low-urgency, but it is genuinely open, not closed.
> - **S6 (SEC-API.io) — FOUND, but not in this project.** The real, rotated key (`sec_api_key.txt`, 78
>   bytes) exists only in the **separate, standalone `C:\Users\beale\Software Dev\Trade\` repo** — not
>   anywhere under `Trading Project 1` (this project's clones), and no `SEC_API_KEY`/`SEC_API_TOKEN`/
>   `EDGAR_API_KEY` env var is set at any scope either. **No code in this repo currently reads it** (`grep`
>   for `SEC_API_KEY`/`sec_api_key` across `tools/` and `docs/guardrail-v2.1/` returns nothing) — canonical
>   `<2.1>`'s "Sanctioned module (leg T): Data-Eng ingestion module" doesn't exist yet (`helm/ingest/` not
>   built), so there is genuinely no consumption path in this project to check the key *against* yet.
>   **Open question for the Lead/Director, not mine to resolve unilaterally:** once `helm/ingest/` is
>   built, where should this project's copy of S6 actually live — installed fresh into a `Trading Project 1`
>   clone (Director-only, per B5), or does HELM's ingestion code deliberately reach across to the separate
>   `Trade/` repo's copy (which would be a cross-project dependency worth naming explicitly, not assuming)?
>   Flagging now so it doesn't surface as a last-minute blocker when `helm/ingest/` actually gets built.
>
> **Net: leg K itself is fully armed and re-run GREEN for all six. Of the per-secret Installed checks: S3
> cleanly closes. S5 is present but explicitly NOT closed — flagged against the live S5 reopening, not
> presented as fine. S1/S2/S4 remain genuinely open — no `.env` exists anywhere yet. S6 exists but in the
> wrong project, with an open scope question.** Not presenting this as "P-5 fully closed" — reporting
> exactly what's checkable, per protocol 15.

> **SecOps co-sign basis:** Step 2 review above (classification/blast-radius, least-privilege,
> ToS-tier match, storage, rotation policy — all six, this session). No blocking finding; residual
> recommendations noted inline, none gate the co-sign. **Installed** and **Leg K re-run GREEN** remain
> genuinely open — I did not check either (out of scope per the Lead's dispatch; leg K is blocked on
> DevOps's gate-harness build). P-5 is still not fully closed by this pass — see the note below.
>
> **2026-08-30, after SecOps's review — S5's command-bar exposure (Step 1 note above) surfaced.** SecOps's
> S5 co-sign above was given without this information. Not un-checked unilaterally by the Lead — that's
> SecOps's own signature — but flagged: worth SecOps re-confirming the S5 co-sign stands once the
> Director answers whether that key was ever rotated.
>
> **2026-08-30 — SecOps re-confirmation, requested by the Lead, delivered.** The S5 co-sign **stands
> as-is.** Reasoning: classification/least-privilege/ToS-tier-match are unaffected by a use-time handling
> mistake (they describe the credential and its terms, not a single incident). What changed is Storage
> and Rotation policy — both updated in the Step 2 row above with the new information, following the same
> treatment I already gave S6's own exposure: log it plainly, don't retract the co-sign for an incident
> that's reported as remediated with independently-checkable evidence (today's key is live, HTTP 200).
> **One thing I won't paper over:** the evidentiary basis here is weaker than S6's — S6 had a persistent
> artifact (`log_pull.txt`) the Lead could inspect before AND after; S5's rotation-in-response-to-the-flag
> is Director-attested only. I'm treating "Director attests to it" as sufficient for a co-sign (same
> standard the Director's own chat approval below relies on), not as equivalent to independently-verified —
> that distinction stays visible in the record, not smoothed into "confirmed" language.
> **One tension worth naming, not mine to resolve:** the Director's own chat approval below states *"none
> has been exposed in the command bar or anywhere insecure"* — which reads as in tension with this incident.
> I'm not adjudicating that (HUMAN/Director territory, not a SecOps oracle call) — just surfacing it per
> protocol 16 (when a statement and its governing artifact disagree, name the disagreement) so the Lead can
> reconcile rather than have it sit as an unremarked contradiction. **New recommendation added to the Storage
> column:** check/clear shell-history for the pasted value, matching the S6 precedent — not yet actioned
> anywhere I can see.
>
> **2026-08-30, after SecOps's re-confirmation — the Lead acted on SecOps's shell-history recommendation
> and found an unresolved candidate** (Step 1's new bullet above). This postdates SecOps's co-sign, which
> was given without it. S5 reopened. Not un-checking SecOps's co-sign unilaterally — that's their
> signature — but flagging it may need a second look once the candidate is resolved.
>
> **2026-08-30 — S5 CLOSED, second rotation supersedes the open question rather than answering it.**
> Director provided a genuinely new key, installed and verified live in both places the running code
> actually reads (User-scope env var + `Trade - Lead\massive_api_key.txt`) — full detail in Step 1's S5
> entry above. SecOps's co-sign, given on the prior (now-superseded) value, is not being asked to
> re-confirm again for this — the co-sign was never about a specific value, it's about the classification/
> handling of the secret class, which is unchanged. The transcript candidate remains genuinely unresolved,
> not retroactively cleared — see Step 1 for the honest distinction between "closed" and "answered."

> **2026-08-30 — Director approves all six, in chat: "all six secrets are stored properly, none has been
> exposed in the command bar or anywhere insecure."** Recorded as the Director-approves column above.
> **This does not close P-5.** SecOps co-signs, Installed, and Leg K re-run GREEN are all still open, and
> per this checklist's own rule the Lead is not eligible to fill the SecOps column — see the Lead's
> response in-chat for who is.
>
> **Reconciliation (SecOps-flagged tension, protocol 16) — this quote predates a later correction.** Later
> the same session, the Director confirmed a command-bar exposure of S5 (Massive) did happen — initially
> misattributed to S6, corrected, then closed above. The "none has been exposed" line above reflects the
> Director's understanding *at that moment in the conversation*, not the final, reconciled record — kept
> verbatim rather than edited, per this project's own append-don't-rewrite discipline; this note is the
> reconciliation, not a silent fix.

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
