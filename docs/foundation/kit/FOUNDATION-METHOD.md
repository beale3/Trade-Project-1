# FOUNDATION-METHOD — the recipe for founding a team (v2)

This is the step-by-step methodology a Lead follows to found a new project's multi-agent team — local clone dirs + a remote GitHub repo + the full governance spine. It is written so a fresh Lead can execute it end-to-end from this file plus `COMPONENTS.md`. The two paste-blocks (`SCRIPT-1-found.md`, `SCRIPT-2-generate.md`) operationalize Phases 1–4; `scripts/new-team.ps1` executes the mechanical scaffold (dirs + repo + starter docs); this file is the *why* and the full checklist behind them.

> **The load-bearing principle:** the foundation must be built against the project's **real, current** structure — not assumptions. The single biggest failure mode is authoring the charter/gates/role-scripts against stale directories or ports. **Validate immediately before authoring** (Phase 2), because the environment can change under you (`FOUNDING-LESSONS.md` LL-1).

> **What v2 adds to the recipe** (each step below carries them where they land): the **two-document rule** authored at founding (one canonical design doc + one append-only working log — protocol 13) · the **symbol legend** codified in the charter (§4.5 — a fresh clone reads colours, never infers them) · **`docs/gate/oracle-boundary.md` authored at founding** (protocol 14 — every seat's certified/HUMAN split, with the admission test) · **per-role lessons blocks** (`roles/<role>.md`) wired into every bootstrap script so an agent reads its own failure-modes on spawn.

## Phase 0 — Orient (read the project as it actually is)
Before anything, read the target project's current state — do not assume it from a brief:
- **Design/product state** — the concept/spec docs, so the roster + wave plan match the real product surface.
- **Dev-environment state** — any existing scaffold (monorepo layout, apps, DB), the `DEV-ENVIRONMENT` doc if present.
- **Git state** — `git log`, `git remote -v`, `git status`; is there a remote, how many commits, is the tree clean.
- **Isolation context** — is this project required to stay separate from another (design language, memory, repos)? Capture the isolation rule verbatim.

## Phase 1 — Elicit config (ask the Director; batch the simple, one-at-a-time the judgment calls)
Capture (defaults in parentheses):
1. Project name + short slug; **product-name placeholder token** if the name is parked (pick ONE unambiguous token — see Phase 3 hygiene).
2. Repo (owner/name, default org `ShupeCapital`) + URL; branch (`main`); clone-dir scheme (`<parent>\<slug>-<role>`).
3. Decision-log prefix (`D-<SLUG>-`) + commit trailer (ask; default to the house trailer if one exists).
4. Cross-session messaging mechanism.
5. Tech stack (default: Node/TS · Fastify · Postgres/Supabase · React/Vite) — if custom, re-map the gate commands.
6. **Greenfield or port?** (picks the wave template in `COMPONENTS.md` §7).
7. One paragraph: what the product does (its domain/value).
8. External API/service providers (feeds SecOps' ToS-as-taint lens — and the per-provider terms check before anything builds on a provider).
9. **Cost model** — subscription-headroom vs **billed per-use** (platform-key) spend. This decides what FinOps governs in real dollars, and whether the metered-chokepoint components (§9.B4, the money-truth gate leg) arm. *(Remember: "cost" means money — but the Director's own time is a real cost too; never dismiss it. Principle §1.8.)*
10. Roster — start from the **maximal-superset archetype library** (`COMPONENTS.md` §2, ~45 generic seats) and **scale back** to the project's real subset; assign each seat its **model + effort** per the §2 tiering. The **core governance/build spine never comes off.** For this kit's default family (AI/content/monetization SaaS) pre-enable AI/ML + AIQ + Content + FinOps + Legal/Privacy + the Phase-0 cluster; toggle off for a non-AI project. Seat an **on-demand Principal Architect** if there's real architectural surface, and a **dedicated surface-builder** per product-surface with its own stack/repo. A whole team may be founded as a **structural MIRROR** of an existing team's roster (LL-16).
11. **Build-phase components** (`COMPONENTS.md` §9) — decide which to adopt + when each arms: B1 architecture gates · B2 quality-bar · B3 build-standards · B4 chokepoint containment (if billed per-use) · B5 key & secrets gate (if prod secrets) · B6 wave-entry + dispatch-freshness · B7 design/planning DP-1→DP-4 (if CX-heavy) · **B8 the Assurance Layer (near-universal)** · **B9 the Validation Gauntlet (fronts every NEW-opportunity project)**. **Pre-build order: B9 → B7 → build waves.**
12. Any deviation from the standard 4-lane cut.

**Deferred-config affordance (LL-24):** the Director may **defer the judgment calls** (cost model · roster scale · providers · Gauntlet run/skip) to a later "build brief." Do **not** block the foundation on them — record each in `PROJECT-CONFIG.md` as **"DIRECTOR-PENDING + the Lead's recommended default,"** so Phase 3 / Script 2 scaffolds against a concrete value and the Director overrides when the brief lands. The governance scaffolding is identical either way.

**Present, then WAIT (LL-38):** where a Phase-1 item is a genuine lock (roster shape, cost model, a bright-line), present the recommendation and **wait for the Director's explicit confirmation** — convergence in conversation is not confirmation, and a lock assumed from silence gets rebuilt.

## Phase 2 — VALIDATE the real environment (do this right before authoring, not from Phase-1 memory)
Read the live repo and record the **exact** values you will bake into every file:
- **Directory tree + workspace names** (`ls` the real `apps/*`, `packages/*`, service dirs).
- **Ports** — app ports and DB/stack ports, from the actual config files (not defaults; they may be reconfigured to avoid local collisions).
- **DB** — connection URL, engine version, migration-file convention + the baseline migration name.
- **Git** — commit hashes of the baseline, remote status.
- **Scripts present/missing** — what the gate will need (typecheck/test/gate) and what must be added.
Put these in the charter's **"Validated environment"** table with a "verified <date>" note. If any value changes after you validate, re-validate before committing.

## Phase 3 — Customize the foundation files (map every value to the REAL structure)
Author these (templates + substance in `COMPONENTS.md`):
1. **`docs/AGENT-COORDINATION.md`** — charter: isolation banner · the validated-environment table · roster (scaled) · the 4-lane cut **mapped to the real directories** · hot-file append protocol · **the full protocol set 1–14** (including the two-document rule and the oracle/escalate-boundary rule) · **the §4.5 symbol legend, verbatim** · the live board.
2. **`docs/decisions-log.md`** — `D-<SLUG>-` seed: team-founded · wave template · stack (+ any open framework/arch lock that must resolve before the core wave) · **cost model** · **project-specific compliance bright-lines as armed gates** · isolation · any money-truth/high-invariant surface. **Every row carries its propagation list** (protocol 3 — a decision is not closed until the documents it changes are updated in the same commit).
3. **The two documents (protocol 13).** Create the **canonical design doc** (statements numbered `<x.y>`, open items marked inline as first-class `NOT DECIDED` lines — an unmarked gap looks exactly like a settled decision) and the **append-only working log**. Only the Lead edits the canonical doc; every other seat appends to the log and the Lead absorbs. Even at founding, when the design is thin, create both — the discipline exists from day one or it never starts (LL-33).
4. **`docs/gate/oracle-boundary.md` (protocol 14) — authored AT FOUNDING.** One row per seat in the scaled roster: *what it certifies mechanically (the leg's ACTUAL assertion, fail-closed) · what stays HUMAN and escalates · who authors the rule / who builds the oracle (never the seat judged).* Apply the **admission test** row by row: certified **only** where a different seat can produce a reproducible negative control; the default is HUMAN. Legs arm at each seat's build wave; the duty binds from founding. GA's standing coverage-audit is seeded pointing at this table.
5. **`docs/app-design/stage-plan.md`** — the greenfield or port wave sequence + the feature/module build order derived from the design.
6. **`docs/gate/gate-spec.md`** — the gate framework with the stack's exact commands + **project-specific armed legs** (a money-truth leg where spend is billed; a compliance leg where a bright-line exists; **the §10 oracle legs**) + the adopted **§9 build-phase components** wired in. Every leg armed (fails on its defect, proven by a planted negative control) or an exit-visible SKIP — no vacuous green.
7. **`docs/roles/lead/open-items-ledger.md`** — open Director decisions + first-wave prep.
8. **`docs/dev-lessons-learned.md`** — seeded with the load-bearing principles (`COMPONENTS.md` §1).
9. **`docs/foundation/role-bootstrap-scripts.md`** — one ready-to-paste block per role, each carrying the isolation clause + the validated ports/paths + the trailer + **the pointer to its `roles/<role>.md` profile (mandate · oracle-boundary row · its lessons block)** in the spawn read-order.
10. **`roles/<role>.md` (copied from the kit, per scaled seat)** — the per-role profile: mandate + oracle-boundary split + **its lessons block**. This is the error-reduction layer: the agent reads its own documented failure-modes before its first action.
11. **`docs/foundation/README.md`** — the Director's operating guide (decisions to make, spawn order, human-only steps).

**Product-name hygiene (Phase-3 trap — LL-3):** if the name is a placeholder, keep it a single unambiguous token, and keep the **product name distinct from infrastructure identifiers** (repo path, `D-<SLUG>-` prefix, npm scope) so the eventual rebrand is one clean find-replace. When you replace the token, do it carefully — a blanket replace also hits sentences that *refer to* the token.

## Phase 4 — Scaffold + handoff (do not corrupt the new Lead's clone)
- **The mechanical scaffold is executable:** `scripts/new-team.ps1` creates the local dir tree, seeds the kit copy + starter docs, **drops the low-friction session defaults** (`.claude/settings.json` acceptEdits+allow/deny · the repo-root `CLAUDE.md` universal spine — `COMPONENTS.md` §10.5), `git init`s, creates the remote via `gh repo create <org>/<slug> --private`, and pushes. Run it (or follow its steps by hand) **after** Phase 3's files are authored so the first push is the complete foundation.
- **Greenfield + a freshly-created empty remote (LL-23):** do **not** `git clone` the empty remote — there's nothing to fetch and it's pure friction. Author the whole foundation directly into the `<slug>-lead` clone dir via file writes, then do git **once** at the end: `git init` → `git remote add origin <url>` → targeted add → commit with the trailer → `git push -u origin main`. The founding Lead may be running from the umbrella parent dir, not inside its clone — write to the target clone path explicitly, don't assume cwd. **Honor a pre-existing clone dir** (`<Slug> - <Role>` etc.) over the scaffolder's `<slug>-lead` default — validate the real convention in Phase 2 and author into the existing tree, not a second one (LL-71).
- **Config absent at Script-2 time (LL-69):** the human checkpoint between the scripts is skippable. If `PROJECT-CONFIG.md` doesn't exist when generation starts, **author it first** from the recommended defaults (DIRECTOR-PENDING), then build — never block; hold only the LOCKS + product paragraph for explicit confirmation, and fire no wave/spend/push on an unconfirmed value.
- **Offline founding (LL-71):** if `gh`/network is unavailable, `git init` + a **local** commit with the trailer, and hand the Director the one-line `gh repo create <org>/<slug> --private --source=<lead-dir> --remote=origin --push`; confirm `.gitignore` covers secrets before that push.
- **Active permissions file (LL-70):** ship the §10.5 `.claude/settings.json` as `docs/foundation/settings.json.template` + a Director "copy into place" step — a governed agent may be refused an active permissions-granting file (and §10.5 already makes full-auto a per-seat Director act).
- The receiving Lead **owns commits in its clone.** Author the foundation **staged/uncommitted** (or in a separate home) and **route the commit** to the new Lead with its own trailer — do not `git commit`/`git add` in a tree another live session owns (LL-2, one-session-per-clone).
- Confirm **no secrets** will be committed (check `.gitignore` covers `.env`, `node_modules`, local-DB temp, any API-key files).
- Hand the Director a spawn order + the human-only steps (create repo/remote if not scripted, spawn each role session, approve any spend).
- The **context-saving spawn rule** (`COMPONENTS.md` §8): when a role session is later replaced, the outgoing agent writes its full context to its activity-log FIRST **and pushes it; the incoming clone verifies the handoff commit is on origin** — a clean local tree ≠ a preserved, fetchable handoff. **Session IDs rotate** — a coordinator verifies the ACTIVE session before dispatching to it, or the dispatch is silently lost (LL-36).

## Phase 5 — Improve the kit + carry it forward
This is what makes the kit self-improving — see `INHERITANCE-AND-MIRROR.md`. In short: record what this founding taught you into `FOUNDING-LESSONS.md` (at minimum "nothing to add"), fold each fix into the affected kit file(s) **and the relevant `roles/` lessons block**, bump `KIT-VERSION.md`, push to the canonical mirror, and seed the new team's repo with the improved kit so it can found the team after it.

**The hand-back also runs the other direction:** when a *live* team's cycle produces documented lessons (its dev-lessons-learned, its audits, its decisions-log), harvest them into this kit's `FOUNDING-LESSONS.md` + `roles/` blocks at the next convenient boundary — that harvest is exactly how this v2 exists.
