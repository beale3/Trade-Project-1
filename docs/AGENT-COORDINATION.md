# AGENT-COORDINATION — HELM (`trade`) team charter

Governed Agent-Team Foundation Kit **v2.2.0**. This is the single charter every seat reads on spawn.
Read order (repo WINS on conflict): **this file** → `docs/decisions-log.md` → `docs/app-design/canonical-design.md`
→ your `docs/gate/oracle-boundary.md` row → `docs/roles/<role>/PROFILE.md` → your lane's design docs.

> **ISOLATION BANNER.** The Foundation Kit under `docs/foundation/kit/` is project-agnostic *methodology*
> (roster, gates, protocols) — it crosses between teams freely and violates no isolation rule (LL-4).
> **Product content, brand, decisions, and design language NEVER cross.** No project-specific isolation
> rule was stated at founding; if the Director sets one (e.g. keep HELM separate from the earlier `Trade`
> experiment), it is recorded verbatim in `PROJECT-CONFIG.md §6` and here.

> **NAME.** `HELM` is a parked product codename (DIRECTOR-PENDING). Infra identity is the slug `trade`
> (repo `beale3/Trade-Project-1` · prefix `D-TRADE-` · scope `@trade`). Rebrand = one find-replace of `HELM`.

---

## §1 · Validated environment (revised 2026-08-04 — D-TRADE-028 drops options entirely)
Not greenfield: the scanner (`tools/rolling_watchlist.py`) and 4 completed equity studies already exist
**in this repo/on this machine** — no missing artifact, nothing to locate (P-2 is MOOT, not resolved-by-
search). The `helm/` validation package itself doesn't exist in-repo yet.

| Item | Value |
|---|---|
| Lead clone | `…\Trading Project 1\Trade - Lead` · branch `main` · **origin LIVE** → `github.com/beale3/Trade-Project-1` |
| ✅ **Toolchain — Python is READY** (verified 2026-08-01, Lead) | `python 3.12.10` + `pip` resolve; **pandas 3.0.3, numpy 2.5.1, scipy 1.18.0, yfinance 1.5.2, matplotlib 3.11.1, requests 2.34.2 — every library the existing scripts already use — are installed and importable NOW.** D-TRADE-017's Node/Docker/pnpm/gh blocker is **superseded, not resolved** — those may still be absent but are likely unneeded for a Python-only Phase 1. Re-verify if the stack decision `<3.5>` pulls in a non-Python component. |
| App tree (Phase 1, ADR-0001 R2) | Single `helm/` package, disjoint-by-directory; `tools/rolling_watchlist.py` stays a shared library (imported by `helm/screener` AND `tools/web/`, not forked) — full layout `<3.5>` |
| DB | Supabase `zyscsnhiymitpfdhjuci` — retained as durable store for scan history/signals/backtest results (`<3.5>`); **baseline still not captured** (light task, not a blocker for Phase 1 start) |
| Gate scripts | none exist yet in-repo — designed at Phase 1 kickoff, lighter than the superseded SaaS gate-spec (B4/B7/B9 dropped, see PROJECT-CONFIG §4) |
| Existing artifacts (already in-repo/on-machine, confirmed 2026-08-04) | `tools/rolling_watchlist.py` (the scanner — guardrail/S3/PND/pattern-detectors, live-Massive-wired) · 4 completed studies in `C:\Users\beale\{regime,catalyst,short-interest,float}-study\` |
| Full config of record | `docs/foundation/PROJECT-CONFIG.md` |

## §2 · Roster (🔒 REVISED 2026-08-01, D-TRADE-020 — personal tool, no SaaS/GTM surface)
**Models (Director-locked):** Architect = **Fable 5 · Max** (LOCKED at generation); **every other seat =
Opus 4.8 · High**. Effort is a depth ceiling, not a quality dial.

**Core (kept, re-scoped):** Program Lead · Principal Architect (on-demand, design ADRs for a Python tool)
· QA (independent CV/backtest re-derivation) · Governance & Audit · SecOps (now: light provider-tier
confirmation) · **SDE1** (data ingestion + Supabase storage, was "Backend-Data/money-truth") · DevOps
(repo/CI for a Python project).
**Quant-research family (re-scoped from "AI/finance"):** AI/ML — **builds the walk-forward-CV backtest
pipeline** (classical statistics, not generative AI) · AI Quality — **independently re-derives/audits
each backtest result** (builder≠judge on the CV discipline) · FinOps — a personal spend guard, not
per-tenant billing · Data Engineer — **mandate narrowed 2026-08-04 (D-TRADE-028):** no options-chain
discovery (deleted); cohort/universe question now just confirming whether a maintained ticker list is
Phase-1-necessary at all vs. the scanner's existing user-supplied `--tickers` status quo (ADR-0001 P-3,
Architect recommends drop — Director to confirm, no Data-Eng seat exists to do it).
**N/A — dropped, not deferred (personal tool, no customers, no market to validate):** Backend-API,
Frontend-Web (no external API/web surface) · the entire GTM/commercial pod · PM/BizOps/Support/Success ·
the Phase-0 Gauntlet cluster (B9 — no market opportunity to validate).
**Design Lead ("Designer") — mandate mostly evaporates** ("a Python script/tool I can run" has no UI to
design); notified, likely stands down pending a concrete need.
**Legal & Privacy — de-risked, optional light-touch** (personal use ≠ advising others; `<4.3>` is a
confirmatory check now, not a hard pre-build blocker).
Oversight (Architect·QA·GA·SecOps·FinOps·AIQ) is **independent of builders and reports to the Director**.
No seat certifies its own work.

## §3 · Lane cut (🔒 per ADR-0001 R2, D-TRADE-028 — single `helm/` package, disjoint by directory;
`tools/rolling_watchlist.py` is now a SHARED library, not ingested)
| Lane | Owner | Write-lane |
|---|---|---|
| **A · ingest + store** | SDE1 · Data Engineer | `helm/ingest/` (provider adapters, point-in-time — the ONLY place a provider SDK/host may appear), `helm/universe/` (**CONDITIONAL, likely DROPS** — ADR-0001 P-3), `helm/storage/` (file-first results, Supabase read-side) |
| **B · screener adapter** | AI/ML | `helm/screener/` — **thin feature-extraction adapter** over `tools/rolling_watchlist.py` (imports the shared scanner, never forks its logic) |
| **C · validation engine** | AI/ML (build) | `helm/validation/engine/` — `evaluate_loo`/`evaluate_multiseed_kfold`, the D-TRADE-021 bar, the two-leg contract (entry-signal + trailing-stop exit-rule), verdict records |
| **D · validation audit (independent)** | AIQ | `helm/validation/audit/` — re-derives from RAW data; **may not import lane C's outputs** (builder≠judge encoded as an import rule, ADR-0001 §4) |
| **E · infra / CI / gate / spend** | DevOps · FinOps | `scripts/gate/**` (runner + legs + import-boundary lint), `helm/spend/` (the spend guard wrapping every ingest call), root config |
| **Shared (not a `helm/` lane)** | AI/ML builds the trailing-stop mode; coordinate with D-TRADE-023 seats | `tools/rolling_watchlist.py` — the scanner itself, imported by BOTH `helm/screener` and `tools/web/` |
| **Hot files (shared)** | Lead allocates IDs | the LIVE BOARD below · `docs/app-design/working-log.md` |

Full module-ownership map + the 10 non-negotiable oracle legs (NN-1..10): `docs/adr/ADR-0001-phase1-validation-tool.md` §4/§8.

**Hot-file append protocol:** per-lane labelled append blocks · **keep-both on rebase, yours last, remove
the three conflict markers** (a hot-file rebase conflict is an append collision, not a real conflict —
picking a side deletes another seat's entry, LL-54) · the Lead allocates all sequential IDs.

---

## §4 · Protocols (binding on every seat)
1. `git pull --rebase` before editing AND before pushing; small commits; **targeted `git add <paths>` (never -A)**. High-concurrency repos: expect rejected pushes → **rebase-first, then retry**; stash any perennial always-dirty file before pulling + pop after.
2. Green-per-commit once the gate exists.
3. Net-new scope → the decisions-log **before** building it. **A decision is NOT closed until it is PROPAGATED** — the downstream docs the bound parties actually read (briefs, specs, the design doc, ledgers) are **named in the decision row** and updated **in the same commit**, or the row states `→ PROPAGATION: none` + why. *The log is where a decision is proven, not where it is obeyed.*
4. Commit trailer `Authored by: Mähnbach <noreply@mahnbach.com>`; never commit secrets; **no literal model IDs** in code/docs — the ONE exception is the kit's §2 model-mapping line (the Director-locked Architect/build assignment), the single sanctioned home for model names.
5. One session per clone; cross-session via the `ccd_session_mgmt` MCP messenger + the repo.
6. Context self-management (§Routines / kit §8).
7. Every wave is bracketed: a **Wave-Entry Gate before** (Lead authors the plan → oversight reviews → **Director GO**; the Lead never self-dispatches) + a **QA phase-exit sign-off after**.
8. **`adr_reference` on every build task** — an approved ADR ID or `BYPASS`+justification. Never BYPASS-eligible: shared contracts · schema · new subsystems · any auth/security code · the first instance of a repeating pattern.
9. **No background/async subagents.** All research + background work runs in **visible team-role sessions** the Director can watch; every role agent completes its own task and does not spawn subagents, so a stall is visible.
10. **UI-mockup gate** — any task with UI elements goes to the Design Lead for a mockup + **Director approval** before it reaches the Architect (only if the product is CX-heavy / B7 adopted).
11. **Assign-by-message + report-on-completion + surface-blockers-mid-task, `[Via messenger]`** — the Lead **always assigns a task to a named seat by message**, never by any other channel. The assigned seat **reports back to the Lead directly on completion** (cross-session message + the repo artifact) — **AND messages the Lead the MOMENT it hits a blocking question, ambiguity, or issue mid-task; it never sits on a blocker, and never guesses past one.** It communicates DIRECTLY with other named seats as the assignment requires. The receiving seat must be verified ACTIVE in its own context window before dispatch (session IDs rotate). No silent finishes; the Director is never the middleman.
12. **"Cost" means money** (principle §1.8) — bound into the charter as a standing directive; price options in dollars + correctness-risk, never hours/effort (but the Director's own time is a real, binding cost).
13. **THE TWO-DOCUMENT RULE.** The design lives in **ONE canonical design doc** (`docs/app-design/canonical-design.md`) — one clean read, the single source, statements numbered `<x.y>`, open items marked inline. Its history is **ONE append-only log** (`docs/app-design/working-log.md`). **(a)** On spawn, read the canonical doc FIRST; where anything disagrees with it, it wins. **(b)** Reference design by its `<x.y>` id, never by re-describing it in prose. **(c) ONLY THE LEAD EDITS THE CANONICAL DOC; every other seat APPENDS to the log** and the Lead absorbs it. **(d)** Never re-derive design from a role log, a brief, or an archived file. **(e)** Build-time numbers live in a few named single-owned annexes; everything needed to understand/approve the design is in the canonical doc itself.
14. **THE ORACLE / ESCALATE-BOUNDARY RULE** — see §Oracle boundary below + `docs/gate/oracle-boundary.md` (the governance layer). Binding on every seat.
15. **THE DELIVERY PIPELINE — the decision-maker DECIDES, never debugs.** Nothing reaches the decision-maker until it is **COMPLETE, GROUNDED, RECONCILED, VERIFIED.** Five gates, the decision-maker only at the last: **① SCOPE** — one axis per item. **② GROUND** — complete (§1.13, nothing under the rug) + every number flagged measured/estimated/unmeasured; owned by the producing seat. **③ RECONCILE** — checked against the full decision set by a **second seat / GA — never the author**. **④ VERIFY-AT-SOURCE** — the Lead reads the **citations, not the claims**. **⑤ DECIDE** — the decision-maker. 🔴 **If the decision-maker catches an error instead of deciding, the item FAILED an earlier gate and goes back — never patched in front of them.** 🔴 **ONE CHANNEL, ONE REPORT.** A seat reports to the **Lead**, never the Director, on any finding another seat also holds; the Lead **holds, consolidates, reconciles the seats against each other, and presents ONCE — one report per piece of work, at completion**, not per leg (sole exception: a genuine BLOCKER). *Convergence the decision-maker must watch is indistinguishable from churn they must arbitrate.*
16. 🔴 **NOTHING LEAVES A SEAT WITHOUT THE ARTIFACT THAT MAKES IT CHECKABLE.** A COUNT carries its ROWS · a NUMBER its SOURCE · a DECISION its DOCUMENTS · a DESIGN STATEMENT its id. **Store the FILTER, not the count.** **Carry a qualified figure as its expression** (`min(2%, $1)`), re-derived at every step that USES it. **A constraint a vendor VOLUNTEERS outweighs a capability it ADVERTISES.** It binds what a seat **ACCEPTS**: when a statement and its governing artifact disagree, **the governing artifact WINS — establish which one governs BEFORE resolving the disagreement.**
17. 🔴 **RECURRING VALIDATION — critical changes get an independent second set of eyes; the Lead's own output is not exempt.** A **CRITICAL** change (an engine rule/number · a ruled decision that propagates · a cross-document invariant · a spend-moving change) gets BOTH the author's verify-at-source (gate ④) AND an **independent, different-agent validation** BEFORE it is presented as reconciled — GA for governance/consistency, the eval seat for scoring-content, **including Lead-authored artifacts**. A **ROUTINE** change gets **self-check only**. The validator is never the author, runs before the item is presented, and reports **as part of** the single report-at-completion. GA confirms the validation actually ran.
18. **A decision states its SCOPE — instance or class — at the moment it is ruled.**
19. **Superseded design is DELETED, not parked** — do not banner/park/move it to a reference file. **Check what else is in a row before cutting it.** Normative counterpart (§Governance): a defect-fix to a normative doc **re-authors** the sections it touches, never patches alongside the superseded text.

## §4.5 · Symbol legend (binding project-wide — one meaning per marker; read it, never infer — LL-32)
Two scales share the palette and never collide (a finding is always tagged `SEVn`; an item never is).
- **STATUS (items/board/ledger):** 🔴 blocking · 🟡 open · 🟢 cleared/go · ✅ done · ▶ running · ⏸ held · 🔒 locked · ⚠️ caution · `▸` = inline design markers in the canonical doc only.
- **SEVERITY (findings — oversight only):** 🔴 SEV1 · 🟠 SEV2 · 🟡 SEV3 · 🔵 SEV4. Both anchor 🔴 = most-urgent. SEV1/SEV2 escalate to the Director immediately.

## §Oracle boundary (protocol 14 — summary; per-seat table in `docs/gate/oracle-boundary.md`)
Wherever a seat's output can be checked by a **sound, cheap, auditable oracle** (rests on an eye-auditable
seed · cheaper to check than satisfy · fails-closed on its defect with a planted negative control · emits
a per-artifact certificate), it is gated by that oracle. Where none exists (taste, ambiguous law, strategy,
real-world side-effects), the duty is **HUMAN and escalates**. **Admission test:** a duty enters the
certified column **only if a seat OTHER than the one judged can produce a reproducible negative control**
("show me the input this green would reject"); no answer ⇒ HUMAN. Default HUMAN; certified is earned.
**Builder ≠ judge:** the seat authors its rule-set, a different seat builds the oracle, GA audits coverage,
QA re-runs on exit. GA owns the standing coverage+soundness+boundary-honesty audit of that table.

---

## §Governance (summary — full text in kit COMPONENTS §5)
- **Decisions-log** append-only, IDs `D-TRADE-NNN`, MAX+1 at rebase, renumber-on-collision keep-both; **every row carries its propagation list**.
- **Gate** one runner asserting **exit codes, not tails**; legs **armed** (fail on a negative control) or **exit-visible SKIP**; standing pre-auth to add armed legs.
- **Phase-gate QA sign-off** — QA re-runs the full gate on each phase HEAD in its own clone before the next wave unblocks; no self-merge.
- **Wave-Entry Gate** — no wave builds until its Wave Plan is oversight-reviewed + Director-GO.
- **A4/A5** (exhaustive · reachable) standing pre-cert checks on any authored decision/band table; **A6** (a revision declares what it changed). Author fixes; an independent seat runs them.
- **Normative specs are RE-AUTHORED, not patched.** **Recurring validation (protocol 17)** governance form: GA confirms the independent validation ran on every critical change.

## §Routines (standing)
- **Context-handoff/spawn rule:** the outgoing agent writes its full context to `docs/roles/<role>/activity-log.md` FIRST **and pushes it; the incoming clone verifies the handoff commit is on origin** before continuing (a clean local tree ≠ a fetchable handoff, LL-14).
- **Verify-don't-attest (incl. your own synthesis)** · **dispatch-freshness** (an idle lane pulls + re-reads the charter/decisions/its ADR before writing) · **re-verify-at-action-time** · **lessons-learned register** (`docs/dev-lessons-learned.md`) fed same-day, harvested to the kit at hand-back.

---

## §LIVE BOARD (one row per seat · claim your row on spawn)
Status legend per §4.5. **🔒 2026-08-01 — D-TRADE-020: `<1.1>` LOCKED, personal tool (not SaaS).
🔒 2026-08-04 — D-TRADE-028: `<1.1>` re-locked a SECOND time — options framing DELETED; HELM now
validates the in-repo equity scanner (`tools/rolling_watchlist.py`) via plain buy signals + a
trailing-stop exit rule. ADR-0001 R2 (the technical design for this) is fully co-signed (AI/ML + AIQ)
and Lead-absorbed into canonical as D-TRADE-030 — the design work is DONE.**
🔴 **2026-08-30 — BUILD-GO. D-TRADE-034: P-1 (D-TRADE-010) LIFTED for HELM Phase-1**, scoped strictly to
Phase 1 — does NOT cover Phase 2 (`breakout_model`/D-TRADE-033 stays held). **D-TRADE-035: P-3 resolved,
`helm/universe` drops entirely.** **D-TRADE-036: P-4 locked** — OP-1 grid trail∈{5,8,12}%/init∈{2,3}%
(primary cell trail=8/init=3), OP-2=1d/1w/1m, OP-3=fixed N=5 trading days (Director-authorized Lead
defaults, **not AIQ-cosigned** — flagged, not hidden). **P-5 (B5) — Director-approves + SecOps-co-signs
now both done for all 6 secrets (`6498dae`)**; still open: `Installed` + `Leg K re-run GREEN`, correctly
blocked on DevOps's not-yet-built gate-harness scaffold (scaffold work starts now that P-1 is lifted).
Every seat below may now build against ADR-0001 R2's module ownership map (§4) — this is a real wave-entry GO,
not a design-only proceed.

| Seat | Session | Status | Next-up |
|---|---|---|---|
| **Program Lead** | ▶ **LIVE — this session (resumed 2026-08-14 from the 2026-08-04 handoff)** | ✅ founded · ▶ **active Lead** | **2026-08-30: P-1/P-3/P-4 ratified (D-TRADE-034/035/036), build-GO issued for Phase 1.** SEC-API.io credential rotated + verified + `log_pull.txt` scrubbed (D-TRADE-032 line closed). `breakout_model`/D-TRADE-033 logged and held (Phase 2, separate authorization needed). **P-5 dispatched to SecOps (item 13) — delivered same session**, Director-approves + SecOps-co-signs both done for all 6 secrets; `Installed`/`Leg K` remain, blocked on DevOps. Next: get AI/ML/DevOps/AIQ/SDE1/FinOps seats actually live to start the build — only SecOps has been reachable from this session so far. |
| Principal Architect | ▶ **LIVE** (`Trade - Architect`, Fable5·Max) | ▶ live · ⏸ holding | **ADR-0001 R2 DELIVERED, CO-SIGNED, and ABSORBED** (D-TRADE-030) — the design work is DONE. Two-leg label (entry-signal + trailing-stop-vs-fixed-holding), trailing-stop as a backward-compat mode in shared `tools/rolling_watchlist.py`, NN-10 (exit-param isolation), `helm/screener`→thin adapter, `helm/universe` likely drops (P-3), 4-state verdict schema incl. UNMEASURED (D-TRADE-029, floor=30). AI/ML + AIQ both co-signed the actual revised text (AIQ found + the Architect fixed 3 real gaps before signing — protocol 17 working as intended). Now canonical `<3.5>`/`<3.6>`. **P-1/P-3/P-4 all ratified 2026-08-30 (D-TRADE-034/035/036) — build-GO issued.** Only P-5 (B5, Director+SecOps sign-off) remains before a real run. **Owes a text-only ADR-0001 update** to match: §4/§5/§9's "CONDITIONAL — likely DROPS" `helm/universe` language → plain drop, §10's "e.g." grid phrasing → the locked OP-1/2/3 numbers. **Also DELIVERED:** ADR-0002 (D-TRADE-023 web UI) — all 3 build tasks completed and shipped. Holding, nothing further pending on this seat. |
| QA | — | 🔴 **NOT SPAWNED — blocks Stage 3 of the Director's 2026-08-30 build-chain dispatch** | Independent reproducibility re-run of AIQ-audited output (pinned seeds+data, numbers must reproduce). **The Director's dispatch names QA as Stage 3; this seat doesn't exist yet** — flagged directly rather than silently substitute or skip it when the chain reaches this point. |
| Governance & Audit | — | ⏸ not spawned | audit AIQ's independent-validation discipline; RECONCILE gate |
| **SecOps** | ▶ **LIVE** (`Trade - SecOps`) | ▶ active · ✅ **P-5 Step 2 + co-sign DELIVERED 2026-08-30** (`6498dae`) | All 6 secrets: classification/blast-radius/least-privilege/ToS-tier/storage/rotation documented with fresh evidence, no blocking finding, Step 3 co-sign checked. Residual (non-blocking) recs: proactive rotation cadence for S1/S2, confirm single live S5 key, S6 old-token dashboard recheck. **Holding** — `Installed`/`Leg K` columns correctly left open pending DevOps's harness. |
| Backend-API | — | ⏸ **N/A, dropped** — no external API surface for a personal Python tool | — |
| Backend-Data = **SDE1** | ▶ **LIVE** (`Trade - SDE1`) | ▶ live · ⏸ holding | **Next real task:** data-ingestion + Supabase-storage layer for scan history/backtest results — re-scoped from "money-truth chokepoint" to normal data plumbing (`<3.2>` is now a light spend guard). Messaged with new scope. |
| Frontend-Web | — | ⏸ **N/A, dropped** — "a Python script/tool I can run" has no web surface | — |
| **DevOps** | ▶ **LIVE** (`Trade - DevOps`) | ▶ live · active | **Leg K scaffold DELIVERED 2026-08-30, Lead-verified** (Lead independently ran both `scripts/gate/run.py` and `legs/secret_scan.py --selftest` — exact match, no discrepancy) (`scripts/gate/{run.py,legs/secret_scan.py}`) — self-test PASSED (10/10 K0-K6 controls RED, 4/4 documented placeholders GREEN, key-denylist.md's own examples don't self-trip), real tracked-repo scan GREEN, and a live plant→RED→revert→GREEN end-to-end check (nothing ever committed). Caught + fixed two bugs during build: a self-reference allowlist that accidentally exempted its own self-test, and a K0b false positive on `AGENT-COORDINATION.md` prose (tightened to SCREAMING_SNAKE_CASE-only). **Six-secret artifact-check DELIVERED (item 13)** — presence/location only, no values inspected: S3 (MCP PAT) FOUND clean (persistent env var); S5 (Massive) FOUND present (persistent env var + a real file in `Trade - Lead`) **but this predates and does not resolve the same-day S5 REOPENING** (unresolved transcript-exposure candidate below — "present" ≠ "confirmed the right/safe value," a distinct question DevOps's artifact-check cannot answer); **S1/S2/S4 (Supabase) NOT FOUND anywhere** (no `.env` in any of 9 clones, no env var); S6 (SEC-API.io) FOUND but only in the separate `Trade/` repo, not `Trading Project 1` — flagged as an open scope question, not resolved unilaterally. Full findings: `docs/security/b5-secret-approval-checklist.md` Step 3. **STAGE 4 of the Director's 2026-08-30 build-chain dispatch, queued behind Stage 3 (QA — not yet spawned):** arm the gate harness's remaining SKIP legs (`scripts/gate/run.py`'s LEG_TABLE — lint/type-check, unit tests, CV reproducibility) against the actual validated build once it exists. **D-TRADE-023 (separate, no freeze):** ADR-0002's 3 deliverables DELIVERED — flask installed, `.claude/launch.json` run entry, boot smoke check (PASS against AI/ML's real `app.py`), `tools/web/README.md`. |
| **AI/ML** | ▶ **LIVE** (`Trade - AI-ML`) | **currently idle — Director dispatching build chain, 2026-08-30** | **STAGE 1 of 4, FORMALLY DISPATCHED by the Director.** Build the entry-signal (Leg A) + trailing-stop exit-rule (Leg B) logic: the trailing-stop mode in `tools/rolling_watchlist.py` (§6.3 formula, primary clearance-eligible grid cell trail=8%/init=3%, D-TRADE-036) + `helm/screener` (thin adapter) + `helm/validation/engine` (CV harness, D-TRADE-021 bar, NN-10 train-fold-only parameter isolation). `helm/universe` explicitly NOT part of this — dropped (D-TRADE-035). Report to the Lead on completion — **staged reporting requested by the Director, not batched to the end.** Prior deliverables unchanged: ADR-0001 R2 co-sign, D-TRADE-023 dashboard backend, D-TRADE-031. |
| **AI Quality** ("AIQ") | ▶ **LIVE** (`Trade - AIQ`) | **currently idle — queued as Stage 2** | **STAGE 2 of 4, FORMALLY DISPATCHED, queued behind AI/ML's delivery.** Independent audit of AI/ML's build — same builder≠judge standard as the P-5 SecOps/DevOps split just demonstrated: re-derive from raw `tools/rolling_watchlist.py` primitives, never import `helm/screener`'s or `engine`'s outputs (NN-3). Prior: ADR-0001 R2 protocol-17 co-sign delivered (3 real objections found+fixed). Will be dispatched with AI/ML's actual deliverable once Stage 1 completes. |
| **FinOps** | ▶ **LIVE** (`Trade - FinOps`) | ▶ live · ✅ pivot re-scope delivered | Re-authored `governor-spec.md` (personal spend guard, ORACLE→PARTIAL) + revised `cost-model.md` in place. New measured finding: SEC-API.io Personal tier = $49/55/mo, 50GB incl., **$0.30/GB overage** (independently re-verified, not just canonical's estimate) — the one real per-use line left; fed into the guard design. Floor now bounded ≈$78–279/mo. **Holding** — awaiting `<2.1>` tier/key confirmations (SecOps/Data-Eng) before cap values can be set; no further action until Architect's P1-0 ADR / build-GO needs the guard wired. |
| Legal & Privacy | — | ⏸ not spawned, optional | `<4.3>` substantially de-risked (personal use) — a light confirmatory check, not urgent |
| **Data Engineer** | — | ⏸ **N/A, not needed** — `helm/universe` dropped entirely (D-TRADE-035, 2026-08-30) | — (this row's prior text was stale options-era duties, corrected same commit) |
| **Design Lead** ("Designer") | ▶ **LIVE** (`Trade - Designer`) | ▶ **active** (D-TRADE-023/024/025) | **All 3 DELIVERED + verified in-browser.** v1 frontend wired + integration-tested (2 real bugs found+fixed via live round-trips). Director-directed palette redesign + light/dark toggle done. **D-TRADE-024/025 now shipped:** `#tw-scan-bar` (ticker input + Scan button + Simulate-trades checkbox, wired to `window.runScan()`, empty-input validated); full trade-simulator panel (trade log, P&L curve, win-rate/final-P&L/trade-count stats, halt banner) off `/api/scan`'s existing `simulatedTrades` — renders only when simulation was requested, no dead/placeholder state. No backend change needed for either. Every path verified with fixtures (empty-input error, real submit request-body shape, winning/halted/no-sim scenarios), zero console errors. Nothing outstanding on this dashboard. |
| Gauntlet cluster | — | ⏸ **N/A, dropped permanently** — no market opportunity to validate for a personal tool | — |
