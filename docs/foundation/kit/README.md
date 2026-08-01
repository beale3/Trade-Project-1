# Governed Agent-Team Foundation Kit — a self-replicating, self-improving multi-agent team founder

**What this is.** A near-turnkey kit that founds a full multi-agent product team (a Lead + builder pods + an independent oversight spine) for a **new AI/content/monetization-shaped SaaS project**, *and* carries the methodology to found the team **after** that — improving itself at each generation. It is the matured successor to an earlier founding kit: same self-replicating shell, content re-authored from a full product cycle's worth of governance (design review → build discipline → an oracle/escalate-boundary gating layer → ground-truth calibration) and its hard-won lessons.

Three things make it more than a static template:
1. **It's the generator, not just the output.** It contains the *recipe* — capture a new project's config, validate its real directories/ports, customise the foundation files to that structure, create the local dirs + the remote repo, and hand off cleanly to the new team's Lead.
2. **It replicates and improves.** Each team founded with this kit inherits a copy, uses it to found the *next* team, records what the kit missed, folds the fix in, bumps the version, and passes the improved kit forward — **and** mirrors that improvement to one canonical copy so no improvement strands on a branch.
3. **It hard-wires error-reduction.** Every documented failure a team hit — a Lead's un-audited synthesis, a vacuous-green gate, a right-tier/wrong-reason answer — is captured as a **generic anti-pattern + its guard** in `FOUNDING-LESSONS.md` and in the affected **per-role lessons block** (`roles/`), so an agent reads its own failure-modes on spawn. Roles get *less* error-prone every generation.

## Inheritance model = linear + canonical mirror (see `INHERITANCE-AND-MIRROR.md`)
- **Linear:** every team carries its own copy in `docs/foundation/kit/` and passes an improved copy to the team it founds.
- **Canonical mirror:** one authoritative home always holds the *latest* version; every founding starts from canonical-latest and pushes its improvement back, so branches converge instead of drifting.

## File index
| File | Purpose | Read by |
|------|---------|---------|
| `README.md` | this overview | human (Director) + any Lead |
| `KIT-VERSION.md` | version + changelog | the founding Lead |
| `FOUNDATION-METHOD.md` | **the recipe** — the step-by-step founding methodology (Phases 0–5) | the founding Lead |
| `INHERITANCE-AND-MIRROR.md` | how the kit replicates + self-improves | the founding Lead |
| `COMPONENTS.md` | the genericised substance — principles, roster, lanes, **the full protocol set + the oracle/escalate-boundary governance**, gates, waves, review processes, routines | the founding Lead |
| `roles/` | one **role-profile + lessons block** per archetype — mandate, oracle-boundary split, and its documented failure-modes-and-guards | each role, on spawn |
| `SCRIPT-1-found.md` | paste-block: found the new team's Lead + elicit/validate config | pasted into the new Lead's session |
| `SCRIPT-2-generate.md` | paste-block: generate + scaffold + create dirs/repo + role scripts + handoff | pasted into the new Lead's session |
| `scripts/new-team.ps1` | the executable scaffolder — makes the local dir tree + `gh repo create` + drops the starter docs | the Director / founding Lead |
| `FOUNDING-LESSONS.md` | the self-improvement register — every documented failure as a generic anti-pattern + guard | the founding Lead |
| `ADOPT-THIS-KIT.md` | how a receiving Lead adopts + uses this kit | the team that just got founded |

## The two audiences
- **The Director (you):** spawn sessions, create repos/accounts, approve spend, make product/scope calls, and **hold the root of trust** (no oracle audits the Director; every un-oracle-able judgment escalates here). The kit does everything else.
- **A team's Lead (an agent):** inherits the kit, founds the next team, and improves it before passing it on.

## Canonical home
This directory is the **canonical mirror**. The latest version always lives here. See `INHERITANCE-AND-MIRROR.md` → *Setup* to back it with a private remote.
