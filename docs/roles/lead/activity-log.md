# Program Lead — activity log (context-handoff artifact)

The Lead's durable context. On any session handoff, the outgoing Lead writes its full state HERE FIRST
**and pushes it**; the incoming Lead clone **verifies this commit is on origin before resuming** (a clean
local tree ≠ a fetchable handoff — LL-14). All truth lives in the repo, never in a session's context.

🔒 **Re-authored 2026-08-04, end-of-session handoff** (LL-19 — the 2026-08-01 version below was stale
after a second major product pivot; re-authored wholesale, not patched alongside it).

## Identity
- **Role:** Program Lead / Orchestrator (the single seat that edits the canonical design doc; never
  self-dispatches a wave; runs the delivery pipeline). Model **Opus 4.8 · High**.
- **Owned clone:** `…\Trading Project 1\Trade - Lead`. **A fresh Lead session opened inside the clone
  should treat this log as truth and verify against the live repo before acting** (protocol 13a — repo
  wins on conflict).
- **Session title convention:** other seats verify the ACTIVE Lead by title + owned clone before routing
  a message (session IDs rotate — LL-36). Recommend the new session set its title to
  `HELM (trade) — Program Lead` if not already set.

## State as of 2026-08-04 (end of this session — read this section first)
- **Origin:** `https://github.com/beale3/Trade-Project-1` · branch `main` · **HEAD
  `63ca4adeee4a566db3ad8d7da78c135c10a78c07`** — verify your clone matches this exact hash before acting
  (LL-14); if behind, `git pull --rebase` first.
- **Kit:** v2.3.0, synced in `docs/foundation/kit/`. Unchanged this session.
- **The product has now pivoted TWICE. Do not trust any pre-2026-08-04 memory of HELM's shape — the
  second pivot supersedes framing that was itself already a full rewrite.**
  1. **D-TRADE-020 (2026-08-01):** SaaS strawman → personal trading-signal tool. Still stands, untouched.
  2. **D-TRADE-028 (2026-08-04):** the *options* framing from D-TRADE-020 is deleted. Director, direct
     instruction: *"Ignore all Option language... implement standard trading logic using basic buy/sell
     signals and trailing-stop rules... Do not apply any Option-related logic."* Confirmed via
     AskUserQuestion to apply to HELM Phase-1 itself, not just the dashboard side-tool.
- **What HELM actually is now (Phase 1):** validate the **equity scanner already in this repo**,
  `tools/rolling_watchlist.py` — no calls/puts, no delta, no DTE. It produces plain stock buy signals
  (guardrail/S3/pattern-detector/pivot-alignment triggers), exited by a **trailing-stop rule that does
  not exist yet and is now Phase-1-critical to build**. Read `docs/app-design/canonical-design.md` in
  full — re-authored twice, wins on any conflict.
- **The full technical design for this is DONE — ADR-0001 Revision 2 is delivered, co-signed by BOTH
  required seats, and Lead-absorbed into canonical (D-TRADE-030).** This was a genuine protocol-17
  CRITICAL-tier review, not a formality: AIQ found 3 real objections against the Architect's first R2
  draft (an audit-boundary gap letting AIQ's independence be quietly defeated at the feature-adapter
  layer, a leakage vector in the exit-rule's naive baseline, an unmitigated multiple-comparisons risk in
  the trailing-stop grid), all three got fixed in the actual ADR text, and AIQ re-read the *text* (not a
  summary) before co-signing. AI/ML co-signed independently, catching two of its own precision gaps
  along the way. **Full design: `docs/adr/ADR-0001-phase1-validation-tool.md`.** Read `<3.6>` for the
  two-leg contract (Leg A = entry-signal validation, Leg B = trailing-stop-vs-fixed-holding exit-rule
  validation) before assuming you understand the shape of Phase 1.
- **P-2 is not just resolved, it never should have been a blocker.** The "missing options-screener +
  0DTE-backtest-engine ZIP" this project spent most of a day treating as an exhaustive-search blocker
  was never actually missing — the real, already-built screener is `tools/rolling_watchlist.py`, which
  had been sitting fully in this repo the entire time (confirmed function-for-function against a copy
  the Director pasted directly). Lesson for the incoming session: **when a "locate this artifact" search
  keeps failing, seriously entertain that the artifact was never what you assumed it was** — don't just
  search harder.
- **Three things now block an actual first CV run — none of them design work, all of them Director
  input:**
  - **P-1** — D-TRADE-010 (no-build) has STILL never been explicitly re-scoped by the Director, across
    two full pivots. My stage-plan.md recommendation (quant-research/design falls outside its original
    intent) is flagged, not ruled. **This is now the single most-asked-and-unanswered question across
    this entire project's history — do not treat it as settled, ask again if it's still unresolved.**
  - **P-3** — keep or drop the planned "maintained universe" module. Architect recommends drop (the
    scanner already just takes whatever tickers you give it via `--tickers`); routed to the Director
    directly since no Data-Eng seat exists to confirm it. Asked, not yet answered as of this handoff.
  - **P-4** — three pre-registration numbers (OP-1 the exact trailing-stop grid, OP-2 the entry-signal
    evaluation horizon, OP-3 the exit-rule baseline's precise form) must be locked *before* any run, per
    LL-44 — recommendations exist (see `<3.6>`/ADR-0001 §10), none are ratified. I offered to propose
    concrete numbers for a yes/no rather than open questions — that offer still stands if unanswered.
- **The D-TRADE-023 equity-dashboard side-tool (explicitly separate from HELM Phase-1, no D-TRADE-010
  freeze) is FULLY BUILT, integration-tested, and working end to end.** `tools/web/` — Flask backend
  (`app.py`/`scan_service.py`/`serialize.py`), the adapted Director-approved mockup
  (`static/index.html`, now with a real ticker-input + Scan button + a full trade-simulator results
  panel, D-TRADE-024/025), a light/dark theme toggle (Director-directed mid-session). Every seat that
  touched it ran real browser round-trips, not fixtures, and two genuine bugs were found and fixed that
  way. **To run it:** `flask --app tools/web/app run --port 5000` from this clone's root, then
  `http://127.0.0.1:5000`. **D-TRADE-031 (this session, delivered):** added a `min_float` guardrail
  parameter mirroring the existing `max_float`, plus `tools/analyze_float_distribution.py` — both
  correctly, explicitly caveated that float data has no reliable point-in-time source in this project
  (the completed float study found BOTH Massive and SEC-API.io NO-GO for this), so `min_float` is
  low-risk but currently inert, same as `max_float` already effectively was.
- **Two provider/credential facts confirmed this session, both now closed:** `..\Trade\sec_api_key.txt`
  is a real, live, currently-active **SEC-API.io** subscription key (Personal & Startups tier, $49/55 per
  month, 50GB/mo included) — verified via a real authenticated API call, not just inspection; the key
  value itself was never printed, logged, or committed (D-TRADE-026/027).
- **✅ RESOLVED 2026-08-21 — SEC-API.io credential exposure.** SecOps had found a live SEC-API.io token
  sitting in plaintext in `C:\Users\beale\float-study\log_pull.txt` (outside this repo, leaked into old
  DNS-failure exception tracebacks); a first Director claim that this was already rotated turned out to
  be stale — the Lead independently verified the old on-disk key with a real authenticated call
  (`https://api.sec-api.io/float`, one-time, value never printed/logged) and got back **HTTP 200**,
  proving the old token was still live, not dead as first stated. Director then rotated at the provider
  dashboard for real and placed the new value in `Trade/sec_api_key.txt` (confirmed by the file's changed
  mtime/size). **Lead re-verified the new key the same way — HTTP 200, confirmed live** — then deleted
  `C:\Users\beale\float-study\log_pull.txt` entirely (not a git repo; no history to worry about) per the
  Director's explicit instruction to not retain the stale credential in any form. **Note:** the *old* key
  was never stored anywhere by the Lead (per the Director's own "do not persist it" instruction during
  the verification call), so its invalidation at the provider could not be independently re-confirmed
  after rotation — only the new key's liveness was checked post-rotation. Closed in
  `open-items-ledger.md`.
- **A recurring pattern this session worth knowing about before it happens to you too:** the Director
  repeatedly pasted content from *other*, unrelated Claude conversations into this session (a claude.ai
  "Build A Stock Chart Algorithm" Project doing separate options-screener/backtest work, a UI-navigation
  help thread, an "11-Hour Options" third-party strategy backtest) while believing it was relevant/the
  same context. Every time, the content looked plausible at a glance but was importantly NOT what it
  first appeared — verify claimed artifacts against the actual local filesystem (`ls`, unzip and read
  real files, grep for real function signatures) before treating a paste as ground truth, and don't be
  afraid to ask "is this the right conversation?" directly. This cost real turns twice; asking early was
  cheaper both times than partially acting on a wrong premise.

## Decisions of record (see `docs/decisions-log.md` for full text + propagation — D-TRADE-001…031)
The load-bearing ones for a fresh Lead to know before doing anything:
- **D-TRADE-020** — personal tool, not SaaS. Still stands.
- **D-TRADE-021** — the ratified Phase-1 clearance bar (unchanged across both pivots): CLEARED only if a
  component beats naive baseline OOS under BOTH LOO-CV and 5-fold CV (≥30 seeds) with ≥90% seed
  agreement; VOID on any leakage finding.
- **D-TRADE-022** — ADR-0001 Revision 1 ratified (options-era design). **Superseded by D-TRADE-030.**
- **D-TRADE-023/024/025** — the browser-UI dashboard, fully delivered (see above).
- **D-TRADE-026/027** — SEC-API.io key + tier confirmed live/real (Personal & Startups).
- **D-TRADE-028** — **the second major pivot.** Options deleted from HELM entirely; equity buy/sell +
  trailing-stop validation instead. P-2 declared moot.
- **D-TRADE-029** — the 30-event minimum-trigger-count floor for thin-firing Leg-A components (verdict =
  UNMEASURED below it, not NOT CLEARED) — Lead-ratified against precedent, same path as D-TRADE-021.
- **D-TRADE-030** — **ADR-0001 Revision 2 ratified + absorbed into canonical `<3.5>`/`<3.6>`.** The
  current, load-bearing technical design for all of Phase 1.
- **D-TRADE-031** — `min_float` guardrail parameter + float-distribution analysis script, delivered.

## Live board summary
Full detail + Next-up per seat: `docs/AGENT-COORDINATION.md` §LIVE BOARD — **refreshed this session**
(the Architect/AI-ML/AIQ rows and the board banner were stale relative to D-TRADE-028/030/031 until this
handoff; they're current as of this commit). Read it directly rather than trusting a stale copy here.
Short version: Architect/AI-ML/AIQ all holding, nothing pending on any of the three after the ADR-0001 R2
co-sign chain closed cleanly. DevOps/FinOps/SecOps/SDE1 holding, no open asks. Designer's D-TRADE-023
work is fully delivered. QA/GA/Legal/Data-Eng never spawned — Data-Eng in particular is now likely
unnecessary given P-3's likely-drop recommendation.

## Standing Lead practices (unchanged since founding — protocol references in the charter)
- **Verify-don't-attest — including my own synthesis** (LL-34): re-derive each claim at source before
  passing it on. This session did this constantly and it caught real things — a stale ADR line-number
  citation, a wrong-zip-file citation, an OP-5 ratification that crossed in transit and needed a
  follow-up fix. Don't skip this because a report "sounds right."
- **Recurring validation of my own output** (LL-64/protocol 17): route CRITICAL changes to an independent
  seat before presenting as reconciled. GA is still not spawned — this session used AIQ for the ADR-0001
  R2 co-sign instead, which worked well and is a reasonable substitute pattern until GA exists.
  **Recommend actually spawning GA if the project keeps producing CRITICAL-tier changes** — this session
  had exactly one (ADR-0001 R2) and the ad-hoc AIQ substitution worked, but it's not GA's actual mandate.
- **One report per piece of work, at completion** (LL-65): hold, consolidate, present once.
- **Never self-dispatch a wave; never unilaterally reinterpret an explicit Director ruling.** P-1
  (D-TRADE-010) has now survived two full product pivots unanswered — resist any temptation to treat
  its long silence as implicit permission. It isn't.
- **Sync before every write:** `git pull --rebase` before editing AND before pushing, every single time,
  no exceptions — this session had extremely high concurrent-seat activity (multiple seats pushing
  within seconds of each other during the ADR-0001 review chain) and this discipline is the only thing
  that kept the repo coherent through it.
- **When in doubt about a secret file's git status, check `git log -p` on that exact path.** Three real
  credential-hygiene incidents across this project's history now (two in-repo near-misses, resolved; one
  out-of-repo live exposure, unresolved — see above). This class of problem recurs; keep checking.
- **When verifying a live credential, use it — don't just inspect it.** This session confirmed the
  SEC-API.io key was real by making an actual authenticated API call (never printing the value), not by
  reading the file and guessing. A key that "looks like a key" isn't confirmed until it's been used.

## Full log (chronological, this session)
### [Lead · 2026-08-04] Session resumed from the 2026-08-01 handoff
Verified HEAD match, absorbed the 4-seat D-TRADE-023 dispatch status, claimed the board row. Consolidated
reports from Architect (ADR-0002 landed), DevOps, AI/ML, Designer as each completed its D-TRADE-023 build
task — verified every claim at source (grepped for the actual code, not just trusted the commit
messages) before acknowledging. All three build tasks (backend, frontend, infra) delivered and
integration-tested via real browser round-trips; two real bugs found and fixed that way, not by review.

### [Lead · 2026-08-04] SEC-API.io key + tier confirmation (D-TRADE-026/027)
Director asked to confirm a key file's identity. Verified programmatically — read the key from disk,
made a real authenticated call to `api.sec-api.io` (two failed attempts first, from sending the whole
`NAME=VALUE` line instead of just the value; diagnosed and fixed), got back real EDGAR filing data.
Confirmed via a screenshot the Director shared. Recorded, then the Director confirmed the exact tier
(Personal & Startups) directly.

### [Lead · 2026-08-04] D-TRADE-023 follow-on features (D-TRADE-024/025) + the credential-exposure finding
Director asked for a real ticker-input control and a full trade-simulator panel — both dispatched to
Designer, delivered, verified at source. Separately, SecOps's routine confirm task surfaced a real
credential at rest in plaintext outside the repo (`float-study/log_pull.txt`) — escalated to the
Director immediately, recommended rotation + scrub. **No confirmation received that this happened** —
see "State as of" above, ask again on resume.

### [Lead · 2026-08-04] The second major pivot — D-TRADE-028
After several rounds of cross-session-paste confusion (see the standing-lessons note above), the
Director gave a direct, explicit instruction to drop all options framing from HELM and validate plain
stock buy/sell signals with a trailing-stop exit instead — confirmed via AskUserQuestion that this
applied to HELM Phase-1 itself, not just the dashboard. Re-authored canonical-design.md §1-3/§5 wholesale
(LL-19), recorded D-TRADE-028, dispatched an ADR-0001 revision to the Architect with the specific design
questions that needed answering, notified all 7 other live seats of their re-scoped impact. Caught and
fixed a real propagation gap afterward — `AGENT-COORDINATION.md`'s §1-3 (the first doc any seat reads)
still described the deleted options framing after the canonical-doc rewrite.

### [Lead · 2026-08-04] ADR-0001 Revision 2 — design, review, and ratification (D-TRADE-029/030)
The Architect delivered a full two-leg validation redesign. Routed AIQ's required protocol-17 co-sign
before treating it as reconciled — AIQ found 3 real, precisely-cited objections against the actual text
(not hypothetical concerns), all verified at source by the Lead before relaying to the Architect. AI/ML
independently converged with AIQ on all of them and added a 4th (a minimum-trigger-count floor for
thin-firing components), which the Lead ratified directly as D-TRADE-029 (well-precedented against the
already-ratified D-TRADE-021 bar, not escalated). The Architect folded all 4 fixes into the ADR text;
AIQ re-read the actual revised text (explicitly not just the chat convergence) before formally
co-signing; AI/ML did the same. Lead verified the final text at source, then ratified and absorbed the
whole design into canonical as D-TRADE-030. This was the most rigorous review chain of the session —
every single claimed fix was checked against the actual file content by at least two parties before
being accepted, and it caught real problems (not just theoretical ones) before any code existed.

### [Lead · 2026-08-04] D-TRADE-031 — min_float guardrail + float-distribution script
Director supplied a real reference implementation as a ZIP. Verified it directly (unzipped, read the
actual source) rather than trusting the paste. Dispatched to AI/ML with the exact spec plus the critical
caveat that this reprises a data-availability problem the project's own completed float study already
found NO-GO on twice. AI/ML delivered, and in the process caught a real citation error on the Lead's
part (a stale, different ZIP with a same-named file that didn't actually match) — verified the correct
current source before building. Delivered and verified clean.

### [Lead · 2026-08-04] This handoff
Director asked to save durably and produce a clone-generation prompt. Re-authored this log wholesale
(LL-19 — too much had changed for a patch to be honest), refreshed the stale portions of
`AGENT-COORDINATION.md`'s LIVE BOARD that a fresh session would read before this log, verified
canonical-design.md/decisions-log.md/open-items-ledger.md were already current (they were — kept in sync
throughout the session as each decision landed, not deferred to handoff time). Pushed everything.

### [Lead · 2026-08-14] Session resumed from the 2026-08-04 handoff; Guardrail v2.1 provenance + D-TRADE-032
Verified HEAD against origin (`git pull --rebase`, fast-forward, no conflicts with existing local WIP —
`tools/rolling_watchlist.py` mods + `modeling/` + `tools/backfill_forward_returns.py` untracked, none of
it mine, left untouched), claimed the board row. Read all six handoff artifacts (activity-log,
canonical-design, open-items-ledger, AGENT-COORDINATION board, ADR-0001 R2) — state matches what's recorded
below, P-1/P-3/P-4 and the `log_pull.txt` credential-rotation question are all **still unanswered**, ask
again next contact.

Independently discovered `docs/guardrail-v2.1/` — a commit (`c088e44`, same day as this session but
predating it) not referenced anywhere in activity-log/canonical-design/decisions-log/working-log: real,
self-validated spec + code work (SI-Gate/Rel-Vol/Tradability/S3/Composite revisions + an EDGAR-mirror
wrapper with a known field-mapping bug), landed via an ungrouped, non-seat session with no D-TRADE number
and no protocol-15 report. Flagged it to the Director rather than assume either way — it revises components
ADR-0001 OP-4 currently treats as settled, which would be protocol-17 CRITICAL-tier if real.

Director pasted that ungrouped session's own transcript as catch-up context — verified its claims against
the actual filesystem rather than trusting the paste directly (LL-45-class check): confirmed the commit's
"not pushed" note was stale (it *was* on origin — asked whether the Director pushed it separately) and that
the corrected Block B code shown in the paste had **not** actually been written to disk anywhere (checked
both this clone and `Trade - Lead`, both clean) — the committed file still had the original bug.

Director then gave a direct, explicit fix instruction for Block B only. Applied it against the real
`Trade/edgar_client.py` schema (independently re-verified, not just re-trusted from the paste), caught one
error the instruction didn't cover (`parents[4]` → `parents[5]`, since this file sits one directory deeper
than `rolling_watchlist.py`), and verified the fix with a real query against `Trade/edgar_index.duckdb`
(100 real AAPL filings, fields correctly populated) rather than just inspecting it. Delivered (`382c514`).

Director then ruled directly on the governance question: Guardrail v2.1 §3-§9 stays **exploratory, not
canonical** — does not enter HELM Leg A/B, does not reopen ADR-0001 OP-4, not dispatch-eligible without an
explicit D-TRADE assignment + AIQ protocol-17 validation; the Block B fix is explicitly distinguished as
already-authorized (correcting an ingestion bug in existing production code, not a build-freeze exception).
Ratified as **D-TRADE-032**, recorded in `decisions-log.md`, propagated to `guardrail-v2.1/README.md`
(status banner) and `open-items-ledger.md` (§A item 10, closed). Canonical-design.md untouched — correctly,
since this explicitly doesn't enter HELM.

**Still open, unresolved by any of this:** P-1 (D-TRADE-010), P-3 (universe drop), P-4 (OP-1/2/3
pre-registration), the `log_pull.txt` credential-rotation confirmation, and whether the Director pushed
`c088e44` themselves.

### [Lead · 2026-08-30] D-TRADE-033 — breakout_model / "Predictive Model 7.0" logged and held
Director raised a scope conflict directly: a separate, active Claude project had been building a
breakout-prediction pipeline (`config.py`/`data_pipeline.py`/`dataset_builder.py`/`features.py`/
`labeling.py`/`main.py`/`train_model.py`/`catalyst_features.py`/`test_synthetic.py`) — asked whether this
is the same work P-1 freezes, and if so what the actual reconciliation process is (log it, hold it, or
unwind it), rather than let it run invisibly the way Guardrail v2.1 did before being discovered.

First pass: searched the whole machine for the four files named in the Director's initial message — none
of `data_pipeline.py`/`features.py`/`train_model.py` existed anywhere; only pre-existing `Trade/
catalyst_features.py` (unrelated, predates this session) was real. Also checked for other live/reachable
Claude sessions (`ListAgents`) to try to identify "the Trade model training chat" the Director asked
about — none reachable. Reported both findings plainly rather than guess, and flagged that this Lead
session has itself been operating out of the `Trade - AI-ML` checkout all along despite `activity-log.md`
naming `Trade - Lead` as the Lead's own clone — a real identity mismatch worth the Director reconciling,
not something to paper over.

Answered the Director's 4 questions directly: (1) yes, same freeze — D-TRADE-010 isn't phase-scoped, and
canonical `<1.4>`/ADR-0001 §10 already name this exact pipeline as Phase 2, out of scope; if anything more
clearly frozen than Phase 1 since Phase 1 hasn't cleared P-1 either. (2) recommended the D-TRADE-032
shape — log under a new number, don't unwind real tested work, don't treat unit-test-passing as CV
clearance, hold pending both P-1 and a Phase-2-specific decision. (3) N/A. (4) could not independently
confirm what "the Trade model training chat" is.

Director then reported the code landed on disk at `Trade/` and asked to confirm visibility + assign
D-TRADE-033. **Verified directly, not attested:** all 9 files present (`Trade/`, dated 2026-08-30),
`Trade/`'s own git status checked (untracked, `.gitignore` diff reviewed — `sec_api_key.txt` still
correctly ignored, no secret-exposure risk from the change), and **ran `test_synthetic.py` independently**
— exit code 0, all 8 PASS lines matched the Director's report exactly (labeling correctness, no-lookahead
checks on features/catalyst/vwap/consolidation/parabolic-curvature, a 6-fold walk-forward smoke run). This
is unit/synthetic-level verification only, not the D-TRADE-021 OOS/CV bar — recorded as such, not
oversold. Ratified as **D-TRADE-033**: logged, held, no further build/training authorized. Recorded in
`decisions-log.md` and `open-items-ledger.md` (item 12). `Trade/` repo itself untouched — separate,
ungoverned repo from `beale3/Trade-Project-1`; no commits made there, nothing requested there beyond
confirming visibility.

<!-- append new entries below -->
