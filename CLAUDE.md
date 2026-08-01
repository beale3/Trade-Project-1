# HELM (slug `trade`) — team operating spine (auto-loaded; binding on every session)

> `HELM` is a parked product codename (DIRECTOR-PENDING). Infrastructure identity is the slug
> `trade` (repo `ShupeCapital/trade`, decision prefix `D-TRADE-`, npm scope `@trade`). Rebrand =
> one clean find-replace of `HELM` when the real name lands (LL-3).

You are ONE named role/seat on a governed multi-agent team (one session per clone).

FIRST, in order (repo WINS on any conflict): `git pull --rebase` → read `docs/AGENT-COORDINATION.md`
(charter: protocols 1–19, §4.5 symbol legend, live board — claim your row) → `docs/decisions-log.md`
→ the canonical design doc `docs/app-design/canonical-design.md` (it WINS on any conflict) → YOUR row
in `docs/gate/oracle-boundary.md` → your profile in `docs/roles/<role>/PROFILE.md` (mandate +
oracle-boundary split + lessons block) → your lane's key design docs.

Standing rules (full text in the charter):
- **No background/async subagents, ever.** You perform every assigned task yourself, in this visible
  session. A stall must be visible to the Director.
- **[Via messenger] (protocol 11):** the Lead assigns every task to a named seat by message; you report
  back to the Lead directly on completion (cross-session message + the repo artifact) — AND message the
  Lead the moment you hit a blocking question, ambiguity or issue mid-task (never sit on a blocker or
  guess past it); message other named seats DIRECTLY as the assignment requires. No silent finishes;
  the Director is never the middleman.
- **The decision-maker decides, never debugs (protocol 15).** Anything reaching the Director is COMPLETE,
  GROUNDED, RECONCILED, VERIFIED — five gates (scope → ground → reconcile → verify-at-source → decide).
  Show the COMPLETE picture — nothing under the rug; deferred ≠ excluded; flag every number
  measured/estimated/unmeasured. ONE report per piece of work, at completion (protocol 15 / LL-65).
- **Recurring validation (protocol 17).** A CRITICAL change (engine rule/number · propagating decision ·
  cross-document invariant · spend-moving change) gets an independent, different-agent validation before
  it is presented — including Lead-authored artifacts. Routine changes get self-check only.
- **Builder ≠ judge (protocol 14 / §10).** No seat certifies its own work; every certified gate leg is
  armed (fails on a planted negative control) or an exit-visible SKIP — no vacuous green.
- **Checkable artifact travels with every claim (protocol 16).** A COUNT carries its ROWS · a NUMBER its
  SOURCE · a DECISION its DOCUMENTS · a DESIGN STATEMENT its id. Store the filter, not the count. When a
  statement and its governing artifact disagree, the governing artifact WINS.
- **Two-document rule (protocol 13):** only the Lead edits the canonical design doc; every other seat
  appends to `docs/app-design/working-log.md`. Hot-file rebase conflict = append collision → keep BOTH
  entries, yours last, remove the three markers (LL-54).
- **Git:** rebase-first · targeted `git add <paths>` (never `-A`) · green-per-commit · commit trailer
  exactly `Authored by: Mähnbach <noreply@mahnbach.com>` · never commit secrets · no literal model IDs
  in the repo (the kit §2 mapping line is the ONE sanctioned exception).
- **"Cost" means money** — price options in dollars + correctness-risk, never hours/effort (but the
  Director's own time is a real cost — never dismiss it).
- **ISOLATION:** the Foundation Kit under `docs/foundation/kit/` is project-agnostic *methodology* —
  copying it here violates no isolation rule (LL-4). Product content, brand, and design language never
  cross between teams; shared process does.
