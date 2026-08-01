# INHERITANCE-AND-MIRROR — how the kit replicates and improves itself (v2)

The kit is designed so that each team founded with it can found the *next* team, and each generation is a little better than the last. The inheritance model is **linear + canonical mirror**.

## The two channels
- **Linear (the family tree).** Every team carries its own copy of the kit at `docs/foundation/kit/` in its repo. When a team founds a new team, it seeds the new repo with the kit. So the kit travels A → B → C… alongside the teams themselves.
- **Canonical mirror (the single source of truth).** One authoritative home always holds the **latest** version: **`C:\Users\Shupe\New M-4 Foundation-Kit`** (local, this directory) → **`ShupeCapital/agent-team-foundation-kit`** (private remote, recommended). Every improvement is pushed here. **This v2 line supersedes the predecessor kit** (`Software Dev\foundation-kit`, the v1.x line) — new foundings start from here, never from v1.

## Why both
Linear alone drifts — an improvement made while founding team B would never reach a later sibling founded from A's older copy. The canonical mirror fixes that: **every founding starts from canonical-latest and pushes its improvement back**, so all branches converge on one improving line instead of forking.

## The rule that reconciles them (follow this every founding)
When you (a team's Lead) are told to found a new team:
1. **Pull canonical-latest.** `git pull` the canonical mirror (or copy it fresh). This — not your own possibly-older `docs/foundation/kit/` copy — is your starting base. *(Canonical wins; your local copy is a snapshot.)*
2. **Found the new team** using `FOUNDATION-METHOD.md` + the two scripts (+ `scripts/new-team.ps1` for the mechanical scaffold).
3. **Record founding lessons** into `FOUNDING-LESSONS.md` (what the kit missed / was awkward / had to be done manually) — at minimum the "nothing to add" line.
4. **Fold each lesson's fix** into the affected kit file(s) — method, scripts, components, **and the relevant `roles/` lessons block** (the per-role blocks are the error-reduction layer; a lesson that names a role's failure-mode belongs in that role's block, not only in the register).
5. **Bump `KIT-VERSION.md`** with a row naming the driving lesson (semver per that file).
6. **Push the improved kit to the canonical mirror.**
7. **Seed the new team's repo** with the improved kit at `docs/foundation/kit/`, so the new team can found the team after it from the same (now-better) base.

**The harvest also runs from LIVE teams, not only foundings.** When a running team's cycle produces documented failures (its dev-lessons-learned, audits, decisions-log, review records), harvest them into `FOUNDING-LESSONS.md` + the `roles/` blocks at the next boundary, and propagate the per-role guards back into that team's live role profiles. That two-way flow is how this v2 exists at all — a full product-governance cycle harvested back into the kit.

The result: `v2.0.0 → v2.1.0 → …` is a single, monotonically-improving line held in canonical, and each team both inherits it and contributes to it.

## Setup (one-time, to back the canonical mirror with a remote)
This directory is already a git repo. To make it durable + off-machine (recommended), the Director (or a Lead, on the Director's go) runs, from this directory:
```
gh repo create ShupeCapital/agent-team-foundation-kit --private --source=. --remote=origin
git push -u origin master
```
Until the remote exists, this local directory *is* the canonical mirror (all teams are on one machine and can copy from it by absolute path). The remote just makes it durable.

## Guardrails
- **The kit is project-agnostic.** It carries *methodology*, never a project's content, code, brand, or design language. Copying it across projects does **not** violate any project's isolation rule — isolation bars content crossover, not shared process. (State this in each team's isolation banner so no one mistakes the kit for an "import.")
- **Improvement is mandatory, not optional.** Every founding writes at least a "nothing to add" line in `FOUNDING-LESSONS.md`. A real lesson → a real fix → a version bump. The self-improving property dies the moment a founding skips it.
- **Canonical is authoritative.** If a team's local `docs/foundation/kit/` and canonical disagree, canonical wins; re-seed the local copy from canonical.
- **Never found against stale values** — the pull-canonical-first step + `FOUNDATION-METHOD` Phase 2 (validate the real dirs/ports) both guard this (LL-1).
- **The v1 kit is retired.** It stays on disk as history; anything still useful in it has been carried into this line. Do not found from it, and do not fold improvements into it.
