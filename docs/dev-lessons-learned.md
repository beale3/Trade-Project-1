# Dev lessons-learned — HELM (`trade`)

Fed same-day by all seats; harvested into the kit's `FOUNDING-LESSONS.md` + the role lessons blocks at
the founding hand-back (this two-way flow is how the kit improves). Seeded with the load-bearing
principles (kit COMPONENTS §1) so they are live from day one.

## Load-bearing principles (COMPONENTS §1)
1. **All durable state lives in the repo**, never in a session's context — every agent is disposable/refreshable.
2. **One session per clone, one clone per session** (shared worktrees corrupt git state).
3. **Independent review beats self-review — builder ≠ judge.** No seat certifies its own work (→ §10).
4. **Spec-complete-before-build** for high-invariant work (transactions, crash-safety, gate-semantics, auth/tenant-iso, migrations, money-truth): lock the complete invariant checklist (implementer + QA) BEFORE building.
5. **Armed assertions / no vacuous green** — every gate leg FAILS on the exact defect it guards, proven by a planted negative control.
6. **Coverage is earned with evidence, never inference** — a rule not yet written is a GAP, not an assumed pass.
7. **Disjoint-file lanes + hot-file append protocol** for the few shared coordination files.
8. **Govern the cost that's real** — real per-**unit** COGS, not the headline rate; the infra floor is part of the cost model. **"Cost" means money** — never price a recommendation in effort/schedule/seats, only dollars + correctness-risk. (But the Director's own time is a real, binding cost.)
9. **Pre-authorize the routine; reserve decisions for the meaningful.**
10. **Build against the real, current structure** — validate dirs/ports right before authoring.
11. **Verify, don't attest — including your own compilation.** A synthesiser's own summary is the least-audited artifact; a different seat audits any synthesis that feeds a decision.
12. **Same tier ≠ same reason.** Grade and gate on the reason, not just the verdict (§11).
13. **Completeness by default — nothing under the rug.** Deferred ≠ excluded; every number flagged measured/estimated/unmeasured; dropped items surface with their reason; presented proactively.
14. **A consistency check passes a uniformly-wrong fact — only a source citation catches it.** External facts carry source + read-date + the revision observed, or they are a GAP.
15. **Residuals are declared, classified, owned — and most are tasks in disguise.** The forcing test: *what would it take to check this?* A lookup ⇒ it is a task you have not done, not a residual.

## Founding entries
### [Lead · 2026-08-01]
- Founded on kit v2.2.0. Script 2 run without Script-1 answers → proceeded on the LL-24 deferred-config
  path; all judgment calls recorded DIRECTOR-PENDING in `PROJECT-CONFIG.md`; locks (cost, roster) held for
  explicit confirmation (LL-38). Candidate kit lesson harvested in STEP 6 — see `FOUNDING-LESSONS.md`.
- `.claude/settings.json` could not be auto-authored (harness classifier blocks writing an active
  permissions file) → shipped as `docs/foundation/settings.json.template` for the Director to place. This
  is a mechanics lesson for the kit (STEP 6).

<!-- append below -->
