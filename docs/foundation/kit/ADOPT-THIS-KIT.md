# ADOPT-THIS-KIT — for the Lead of a team that will found subsequent teams (v2)

You (a team's Lead) are being handed this kit so your team can found **subsequent project teams**, each inheriting an improving version of the founding methodology. Read this once, then keep `FOUNDATION-METHOD.md` + `INHERITANCE-AND-MIRROR.md` as your working references.

## What you're adopting
A self-replicating, self-improving team-founder. It carries the *recipe* for founding a governed multi-agent team (not just one team's output), and it improves each generation via **linear inheritance + a canonical mirror** (`INHERITANCE-AND-MIRROR.md`). The v2 line additionally carries the matured governance a full product cycle produced: the two-document rule, the oracle/escalate-boundary layer (`COMPONENTS.md` §10) with its admission test, the matured independent-review process (§11), and **per-role lessons blocks** (`roles/`) so every spawned agent reads its own documented failure-modes first.

## One-time adoption (do this now)
1. **Register the canonical mirror.** Canonical home = `C:\Users\Shupe\New M-4 Foundation-Kit` (local) → recommended remote `ShupeCapital/agent-team-foundation-kit` (private). If the remote doesn't exist yet, ask the Director to create it (or, on the Director's go, from the canonical dir: `gh repo create ShupeCapital/agent-team-foundation-kit --private --source=. --remote=origin` then `git push -u origin master`).
2. **Seed your own repo with the kit.** Copy the canonical kit into your repo at `docs/foundation/kit/` (a file copy, not a submodule) and commit it with your trailer. This is your inherited working copy + proof-of-provenance. *(Isolation note: the kit is project-agnostic methodology — copying it in is NOT a cross-project content import; state that in your isolation banner.)*
3. **Note the standing capability** in your ledger: "This team can found subsequent teams via `docs/foundation/kit/` — procedure below."

## When the Director says "found a new team X" — the procedure
1. **Pull canonical-latest.** Canonical — not your possibly-older `docs/foundation/kit/` — is your base.
2. **Scaffold X** — run `scripts/new-team.ps1` (creates X's local dir tree + the private remote under the org + the first push), or follow its steps by hand. The Director must be `gh`-authenticated for the repo creation.
3. **Copy the kit into X's repo** at `docs/foundation/kit/`.
4. **Run the founding** (`FOUNDATION-METHOD.md` Phases 0–4): open a fresh session for X, paste `SCRIPT-1-found.md` → it captures + validates X's config → paste `SCRIPT-2-generate.md` → it generates X's customized foundation: charter (protocols 1–14 + the symbol legend) · decisions-log · the two documents · gate-spec · **`docs/gate/oracle-boundary.md`** · wave plan · per-role profiles + bootstrap scripts · the Director's README.
5. **Hand off to X's Lead** (Phase 4): X's Lead owns commits in X's clone; route the initial commit; give the Director X's spawn order and the locks awaiting explicit confirmation (present, then WAIT — LL-38).
6. **Self-improve + mirror** (`INHERITANCE-AND-MIRROR.md`, mandatory — Script 2 Step 6): append what founding X taught you to `FOUNDING-LESSONS.md` (at least "nothing to add"), fold each fix into the kit **and the relevant `roles/` lessons block**, bump `KIT-VERSION.md`, **push to the canonical mirror**, and confirm X's `docs/foundation/kit/` holds the improved version.

## The rules that keep this working
- **Canonical is authoritative** — always start a founding from canonical-latest; if your local copy disagrees, re-seed from canonical.
- **Improvement is mandatory** — every founding writes a `FOUNDING-LESSONS.md` entry and bumps the version.
- **Never found against stale values** — pull canonical first + validate the target's real dirs/ports before authoring (LL-1).
- **Respect one-session-per-clone** — the new team's Lead commits in its own clone; you route, you don't commit into its tree (LL-2).
- **The kit stays project-agnostic** — it carries process only, never a project's content/brand/design; that's what lets it cross projects without breaching any isolation rule.
- **Harvest both directions** — foundings improve the kit; your team's own live cycle (audits, lessons, review records) is harvested back into the kit too, and the kit's per-role guards are propagated into your live role profiles.

## Your current inherited version
`v2.0.0` (see `KIT-VERSION.md`) — the clean successor line: the v1 shell (four foundings, LL-1…LL-24) re-authored with a full product cycle's matured governance and its harvest (LL-25…LL-55).
