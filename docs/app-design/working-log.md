# HELM — design working log (append-only)

Protocol 13: every seat **appends** here (per-lane labelled block); the **Lead absorbs** entries into
`canonical-design.md` and references them by `<x.y>` id. Never re-derive design from this log — it is
history; the canonical doc is truth. Hot-file rebase conflict = append collision → **keep BOTH, yours
last**, remove the three markers (LL-54).

---
### [Lead · 2026-08-01] Founding
- Two-document discipline started at founding per LL-33 (design is thin — that is expected).
- `canonical-design.md` seeded with `<1.1>` (product) as `▸ NOT DECIDED` — the blocker for real feature
  design. Strawman recorded there for the Director to react to.
- Money-truth chokepoint `<3.2>` declared as the high-invariant surface (D-TRADE-008); its invariant
  checklist locks before W1 build.
- Awaiting Director: product paragraph `<1.1>`, providers `<2.1>`, cost-model + roster locks, B9 run/skip.

### [Lead · 2026-08-01] Director ruling + asset intake
- **D-TRADE-010 (Director):** NO code build / no wave dispatch is authorized — foundation phase only.
  Propagated to stage-plan (banner + W0), foundation/README §3, open-items-ledger §B/§D.
- **Asset intake — `..\Trade\`:** a stub repo the Director asked me to pull in. Contents = a **SEC EDGAR
  API key** setup (`sec_api_key.txt.template` + a gitignored real `sec_api_key.txt`, 77 bytes — contents
  NOT read; the real key was never committed, good hygiene). Absorbed into canonical `<2.1>`: EDGAR is the
  in-hand anchor provider; the key stays out of this repo and goes to the secret store at B5.
- No other content in `..\Trade\` (no design, no code) — it is purely the key holder.

### [Lead · 2026-08-01] AI/ML's screener-artifact blocker — independently confirmed, escalated
- AI/ML correctly refused to reconstruct the options screener from the canonical doc's prose (LL-45 —
  would be inventing the very artifact it's meant to validate) and reported the ZIP files as unlocatable
  on this host after an exhaustive search.
- **Independently re-verified from the Lead session** (Downloads: every `files (N).zip` opened and
  identified by content — none are the options screener or the 0DTE backtest engine, all are earlier
  exploratory artifacts from July 4–6/25: a `stocksim` scaffold, `ibkr_guardrail_scanner.py` /
  `day_trade_toolkit.py`, catalyst-CV verification scripts, chart PNG/CSV pairs; also checked Desktop/
  Documents/OneDrive — nothing). Also read `momentum_scan_playbook.md` (Jul 29) — the equity/guardrail
  playbook, not options-related.
- **Conclusion: the options screener + 0DTE backtest engine genuinely are NOT on this machine.** They
  exist only inside the "Build A Stock Chart Algorithm" claude.ai Project's conversation/sandbox and were
  never downloaded locally — the same outputs-folder-vs-local-disk confusion already documented earlier
  in this research (the "s3_smoke_test_claude_code_prompt.md" episode).
- **Escalated to the Director** (only they have access to that claude.ai Project) — see report.
- **Data-Eng flag (AI/ML, absorbed):** Phase 1's multi-year backtest over a liquid-optionable S&P/Russell-
  class universe needs **point-in-time universe membership** (which names were actually in the index on
  each historical date) to avoid survivorship bias — unlike the 4 equity studies' static cohort, which
  never faced a rolling-index question. Recorded for Data-Eng to pick up on spawn.
- **PROFILE.md staleness (AI/ML flag):** 7 role profiles (ai-ml, aiq, sde1, finops, secops, design,
  architect) predated the pivot with no pointer to the re-scoped canonical text. Fixed — each now has a
  pivot-note header directing to the winning canonical-design/oracle-boundary text (protocol 13a already
  made this non-hazardous, but the pointer closes the rough edge).

<!-- append below this line -->

### [FinOps · 2026-08-01] Spawned (D-TRADE-016) · provider cost model + governor spec drafted
- Onboarded (charter · decisions · canonical-design · oracle-boundary FinOps row = ORACLE · PROFILE ·
  supabase.md · gate-spec). Claimed the FinOps LIVE BOARD row (▶ live). Modeling-only phase — no chokepoint
  exists yet (D-TRADE-010), so this is SPEC, not live governance.
- **`docs/finops/cost-model.md`** — the four adopted providers priced (source + read-date 2026-08-01, every
  figure tagged measured/estimated/unmeasured + basis). **Central finding:** only **LLM tokens** are true
  per-use variable COGS; **Polygon/Massive** (flat unlimited sub) and **EDGAR** (free) are $0-marginal
  standing floor; **Supabase** is a flat plan + slow-moving usage overage. ⇒ the governor's spend-meter is
  effectively an LLM-token meter.
- **`docs/finops/governor-spec.md`** — fail-closed governor (default = refuse), 3 cap layers, the `$/day`
  self-tally **auto-kill** (D-TRADE-004), ledger invariants + billing-reconciliation oracle, each with a
  reproducible negative control (builder ≠ judge). FinOps portion of the **chokepoint invariant checklist**
  drafted with co-author sign-off slots (SDE1/BE-Data · QA · SecOps) — BE-Data owns/assembles it at the W1 lock.
- **Surfaced to the Lead (dollars only; I do not rule these):** 🟠 market-data true cost is **quote-only**,
  not the self-serve $199 — a commercial SaaS is Professional/Business tier + OPRA/UTP/NYSE exchange fees
  (the FinOps half of SecOps's HIGH Polygon finding; real-time-vs-delayed is a real-$ lever on `<2.1>`).
  🟡 "SEC key" issuer unconfirmed → EDGAR is $0 only if direct, not a reseller. 🟡 per-signal COGS is
  unmeasured by construction (no engine) — caps arm tight, rise on measured evidence. 🟡 D-TRADE-004 still
  🔒-pending.
- DRAFT (gate ② GROUND). Not yet RECONCILED (GA/second seat) nor Director-locked on any dollar value.


### [Architect · 2026-08-01] Spawn + onboarding — HOLDING
- **Principal Architect LIVE** (clone `Trade - Architect`, branch `main`, Fable5·Max — sole frontier
  seat). Onboarded in read-order: charter (protocols 1–19 · §4.5 legend · LIVE BOARD) → decisions-log
  (D-TRADE-001..016) → canonical-design → my `oracle-boundary` row (PARTIAL) → PROFILE → stage-plan +
  gate-spec. Claimed my board row.
- **Posture = HOLD, correctly.** Product `<1.1>` = ▸ NOT DECIDED and D-TRADE-010 bars all build/wave
  dispatch → there is nothing to architect yet. An ADR authored now would rest on an undefined product;
  I will not manufacture one. First work on `<1.1>` landing (+ B9 if the Director runs it): the **W1
  CORE-SPINE A0 ADR** — transport · request-context/tenant · auth · DB adapter (Supabase
  `zyscsnhiymitpfdhjuci`) · the money-truth chokepoint `<3.2>` one-way-door surface, its invariant
  checklist locking with QA+SecOps+FinOps before build.
- **Setup note surfaced to the Lead (protocol 11):** the `Trade - Architect` clone directory was **empty**
  on spawn despite D-TRADE-016 seating the row — I cloned fresh from origin (`db3f4a6`, verified on
  `origin/main`, clean). Not a blocker; flagged so the stand-up gap is on record.
- No design content authored (my write-lane is `docs/adr/**` + this log; only the Lead edits the canonical
  doc). Awaiting Lead dispatch.

### [AIQ · 2026-08-01] Spawn · onboarded · eval methodology draft (HOLD)
- **Live + onboarded.** Clone `Trade - AIQ` was empty on spawn → cloned `beale3/Trade-Project-1`
  (origin/main @ `0ec2358`, D-TRADE-014); `pull --rebase` clean. Read in order: charter → decisions-log →
  canonical-design → my `oracle-boundary` row (VERIFIER) → PROFILE. Board row claimed. **HOLDING** per
  D-TRADE-010: `<1.1>` NOT DECIDED and no AI/ML output exists yet → no golden set can honestly exist.
- **Light prep (methodology only, no eval set — the fabrication line held):** drafted
  `docs/eval/methodology-draft.md` — a proposal for the **Lead to absorb**. It fixes the eval *method*
  before any output exists: freeze-before-measure/pin the commit (LL-41) · accuracy-vs-consistency as
  separate claims + blind write-once ground truth (LL-40) · pre-register write-once before the run (LL-44)
  · catch-matching against a shared reason-vocab co-authored with AI/ML (LL-42) · fresh-draw is the honest
  number, same-set re-seal is labelled confirmation only (LL-43) · void-on-contamination (LL-47) ·
  builder≠judge. Contains a **placeholder** reason-vocab skeleton (structural buckets, NOT product claims).
- **Nothing to grade, nothing fabricated.** No golden items, thresholds, or accuracy numbers authored.
- **Instantiation blocked on (for Lead visibility):** ① `<1.1>` product · ② `<3.4>` engine + first sealed
  outputs · ③ reason-vocab co-authored w/ AI/ML · ④ Director rubric ratification · ⑤ named blind
  ground-truth expert · ⑥ providers `<2.1>` for source-of-record grounding. Reported once to Lead.

### [SecOps · 2026-08-01] Provider ToS-as-taint review + key denylist + B5 checklist (first task, D-TRADE-010 foundation work)
- Delivered three artifacts (write-lane `docs/security/**`): `tos-taint-review.md`, `key-denylist.md`
  (leg K), `b5-secret-approval-checklist.md`. Method: a **volunteered** vendor constraint outweighs an
  **advertised** capability (LL-62); every reading cites source + read-date + revision (LL-58/LL-52).
- **SEC EDGAR** — taint **LOW (data)** / HARD ops. Filings are public-domain, redistributable. Volunteered
  constraints: 10 req/s cap, declared User-Agent required, no undeclared bots (confirmed live: undeclared
  fetch → HTTP 403, declared UA → 200). Binds `<2.1>` ingestion design. **Open:** the in-hand 77-byte
  "SEC key" is likely a third-party reseller (public EDGAR is UA-based, keyless) → issuer to be confirmed
  by Director/Data-Eng; a reseller re-opens the taint.
- **Polygon.io / Massive** — taint **HIGH** 🟠 (headline). Entity rebranded Polygon.io→Massive (eff.
  2025-10-30); both `api.polygon.io` + `api.massive.com` live → leg T sanctions both hosts. The
  individual/default license (Market Data ToS, Oct 9 2024) is **non-commercial, Non-Professional,
  display-only, no redistribution, no "investment strategy" derivative works** — incompatible with strawman
  `<1.1>` on four counts. Business tier (Sept 2 2025) allows redistribution to "Edge Users" but STILL bars
  unlicensed derivative works; real-time drags in OPRA/UTP/NYSE agreements + pro-tier fees. **Provider/tier
  acceptability = Director; "are HELM signals a licensable investment strategy?" = Legal → `<4.3>`.**
- **Supabase** — taint **MEDIUM**. We own our data (no IP taint); the binding duty is customer-bears-all
  credential security (→ service_role + DB password are B5, server-only; leg T keeps them out of
  `apps/web`). Data-class lines: no PHI w/o BAA, no cardholder data w/o approval → Legal if the model ever
  touches them. Already Director-adopted (D-TRADE-013/014); read-only MCP is correct least-privilege.
- **Leg K** authored for 6 secret classes (Supabase service_role/DB-pw/PAT/anon, Polygon/Massive key,
  SEC/EDGAR key) + generic backstop — each with a planted negative control (LL-48); templates stay green.
  DevOps wires · GA audits coverage · QA re-runs (builder ≠ judge). **Leg T** sanctioned-module rules
  recorded per provider. **B5 gate** = HARD launch blocker; Director approves + SecOps co-signs; Lead may
  not self-approve; agent never handles values.
- Reported once to the Lead (protocol 15). Escalations flagged for the Lead to consolidate/route to
  Director: Polygon HIGH taint (SEV2-candidate), SEC-key issuer, Supabase data-class lines.

### [AIQ · 2026-08-01] D-TRADE-020 pivot absorbed — re-scoped to independent CV/backtest audit (HOLD)
- **Pivot absorbed.** `git pull --rebase` → origin @ `47f6e60`. Re-read canonical-design.md §1–4 (full
  re-author), my `oracle-boundary.md` row (VERIFIER, already re-scoped by the Lead: "independently
  re-derives each CV result from raw data · catch-matching against the pre-registered bar · voids on any
  seed-sensitivity or contamination finding"), and stage-plan.md P1-3.
- **Mandate re-scope, in one line:** from "judge generative-AI output for anti-fabrication/grounding" to
  **"independently re-derive and audit every screener-component CV result before it's called cleared"**
  — builder ≠ judge on classical-statistics CV discipline (AI/ML), not LLM output. My PROFILE.md's
  lessons block (LL-40/41/42/43/44/47) maps almost unchanged onto the new duty; only the subject changes
  (a backtest result, not a generated document).
- **Re-authored `docs/eval/methodology-draft.md` wholesale (LL-19 — re-author, not patch alongside dead
  framing)**, replacing the generative-AI/LLM-grounding version entirely with an independent
  backtest-audit protocol: pre-registered bar (beat naive OOS under BOTH LOO **and** 5-fold; ≥90%-of-≥30-
  seeds robustness sweep — recommended, flagged for Lead/Director ratification, not self-ruled) ·
  re-derive-from-raw-data, never from AI/ML's summary (LL-34) · catch-match not tier-match (LL-42) ·
  fresh-draw vs fit-to-test on any retune (LL-43) · void-on-contamination (LL-47). Referenced the Lead's
  cited template `catalyst-study/CATALYST_STUDY_FINDINGS.md` addendum directly: a nominal 1-day LOO "win"
  (+0.04% RMSE, OOS R² still negative) died completely under 5-fold (0/3), and a 50-seed sweep showed the
  apparent win was a coin flip (68/24/6% across horizons) — below the ≥90% bar. That is the exact failure
  mode my re-derivation sequence is built to catch.
- **Nothing to audit yet, verified**: `git log`/tree at `47f6e60` shows no P1-2 (screener ingestion) or
  P1-3 (validation engine) code committed. HOLDING is correct, same posture as before, now against real
  near-term work instead of an undecided product.

### [DevOps · 2026-08-01] Pivot re-scope — Python gate harness + Phase-1 DoD (design only)
- Rebased onto D-TRADE-020 (`<1.1>` locked — personal options-signal tool). Re-authored (not patched,
  LL-19) `docs/roles/devops/harness-design.md`: the prior Node/Fastify/Docker/RLS design is deleted; a
  lighter Python-only gate harness replaces it (ruff/mypy + pytest + a CV-reproducibility leg + legs
  K/T/G), matching the re-authored `gate-spec.md`.
- **Independently re-verified the toolchain in this (DevOps) session, not taken on the Lead's report
  alone:** Python 3.12.10 + pip resolve here too, and every core analysis library the existing screener/
  backtest/study scripts already use (pandas/numpy/scipy/yfinance/matplotlib/requests) imports cleanly.
  This closes the earlier open question of whether D-TRADE-017's Node/Docker absence was session-specific
  — it wasn't; only Node/Docker/pnpm/gh are genuinely absent, and `<3.5>` drops that entire stack anyway.
  `ruff`/`mypy`/`pytest` are not yet installed — a trivial `pip install`, unlike the Node/Docker gap.
- **Leg K/T wiring plan built on SecOps's already-authored specs, not re-derived:** `key-denylist.md`'s
  7 patterns (K0–K6) encoded as the wiring target; `tos-taint-review.md`'s sanctioned-module rule adapted
  from the superseded `apps/web`/Lane-2 framing to a draft Python module layout (`helm/ingest/*`,
  `helm/storage/*`) — final module names await the Architect's P1-0 design ADR.
- **Flag (not a fix — not my lane):** `docs/finops/governor-spec.md` (leg G's target) is still written at
  the superseded SaaS scale (per-tenant caps, transactional ledger, billing reconciliation vs. invoice) —
  canonical `<3.2>` explicitly calls that machinery overbuilt for a personal spend guard now. FinOps
  authors caps; I only wire — flagging for FinOps to re-author a light version before leg G is real.
- **Held on actual file creation** (`pyproject.toml`, `scripts/gate/**`) — stage-plan.md itself frames
  D-TRADE-010's applicability to Phase-1 scaffold work as the Lead's recommendation pending Director
  confirmation, and a Wave-Entry Gate (Architect P1-0 ADR + Director GO) still applies regardless. The
  design above is a ready-to-execute plan for the moment either lands, not a build.
- Reported once to the Lead (protocol 15).

### [AIQ · 2026-08-01] D-TRADE-021 ratification synced (no content change)
- Lead ratified my pre-registered Phase-1 clearance bar as **D-TRADE-021** (LOO+5-fold both required,
  ≥90%-of-≥30-seeds agreement, VOID on any leakage/contamination) and propagated it into canonical
  `<3.4>`. No change to the bar's substance — `docs/eval/methodology-draft.md` already had it verbatim.
  Updated the file's status language from "recommended, not self-ruled" to "ratified, binding" (§2, §5)
  so the doc doesn't read as still-pending. **Still HOLDING** — no AI/ML result exists yet; protocol is
  now fully ratified and ready to fire on the first one.

### [AI/ML · 2026-08-01] D-TRADE-020 pivot absorbed — methodology drafted, one blocker surfaced
- **Pivot absorbed.** `git pull --rebase` → onto `9037b15`. Re-read canonical-design §1/`<3.4>` (incl. the
  D-TRADE-021 clearance-bar addendum), stage-plan P1-2/P1-3, my `oracle-boundary` row (re-scoped VERIFIER —
  runs the CV pipeline, reports pass/fail against the pre-registered bar; choosing candidates + interpreting
  marginal results stays HUMAN), PROJECT-CONFIG §3. My PROFILE.md is still the pre-pivot generative-AI
  version (stale, not yet re-authored by the Lead) — deferred to the newer canonical/oracle-boundary text
  per the read-order (repo wins on conflict, and these are strictly newer).
- **🔴 Blocker surfaced (protocol 11, reported to Lead the same message as this log entry):** the options
  screener + 0DTE backtest engine ("delivered as a ZIP, location TBD" per stage-plan) are **not locatable**
  on this host — searched `Downloads\` (incl. every `files*.zip` by content-listing), `Desktop\`,
  `Documents\`, the legacy `..\Trade\` stub (key holder only), and all 4 study directories. Blocks P1-2
  (screener ingestion) concretely. Will not reconstruct the screener from the canonical doc's prose
  description — that would be inventing the artifact I'm meant to validate (LL-45). Needs Director/Data-Eng
  to locate/deliver.
- **What doesn't block on the above:** drafted `docs/roles/ai-ml/validation-methodology-draft.md` —
  design/planning only (no code, no data, no numbers), consistent with the Lead's explicit "design/planning
  is fine now, confirm before production pipeline code" scoping of the open D-TRADE-010 question. Covers:
  two-tier target design (continuous forward-return regression as the primary CV vehicle, matching the
  proven template exactly; a volatility-scaled directional-correctness binary as the Phase-1 success
  criterion, usable on OHLCV alone so it doesn't block on the unconfirmed `<2.1>` options-chain/IV data —
  delta-implied threshold recorded as an upgrade path, not invented now) · per-component isolation (never
  bundle trend/momentum/breakout/volume/IV-rank) · no-lookahead + point-in-time discipline · a **new**
  point-in-time-universe-membership requirement flagged for Data-Eng (survivorship bias — the 4 equity
  studies used a static cohort and never had a rolling-index-membership question; Phase 1's multi-year
  backtest over `<2.2>`'s universe does) · the D-TRADE-021 clearance bar, cited by id, not re-derived.
- **Converged with AIQ before either reached the Lead (protocol 15):** independently arrived at adopting
  AIQ's proposed bar verbatim rather than proposing a second number — turned out to be exactly what the
  Lead ratified as D-TRADE-021.
- Reported once to the Lead (protocol 15), bundling the blocker + the methodology-draft summary in one
  message per the completion-report discipline (blocker escalation folded into the same report since both
  landed together, not two separate pings).

### [FinOps · 2026-08-01] D-TRADE-020 pivot — re-scoped both artifacts (ORACLE → PARTIAL)
- Re-authored (protocol 19, not patched) **`docs/finops/governor-spec.md`**: the SaaS-scale fail-closed
  governor (idempotent ledger, billing-reconciliation oracle, 3-layer caps, `$/day` auto-kill w/ SEV1
  paging) is replaced by a **lightweight personal spend guard** — a daily/monthly quota-and-cap watch that
  BLOCKS a call before it breaches a cap. Matches the oracle-boundary re-scope: FinOps moved **ORACLE →
  PARTIAL** — only "a call that would breach the cap is BLOCKED" is mechanical now; the cap **value** stays
  HUMAN. Routine tier (protocol 17) — self-check only, no independent-validation pass required at this scale.
- Revised **`docs/finops/cost-model.md`** in place (targeted, not full rewrite — prices unchanged, only
  classification/applicability): `<3.4>` is classical stats, so **Phase 1 has zero LLM spend** — the old
  "LLM tokens are the only true per-use COGS" finding is superseded, deleted from load-bearing text. The old
  🟠 "Polygon/Massive is quote-only, not $199" escalation is **resolved by the pivot itself** — personal use
  plausibly is the correct tier (SecOps confirming); no further FinOps action.
- **New finding, independently re-verified (not just carried from canonical's estimate):** re-fetched
  `sec-api.io/pricing` directly — **Personal & Startups tier = $49/mo (annual) / $55/mo (monthly), 50 GB
  included, $0.30/GB overage** (Business tier: $199/$239, 100 GB). This is a **real, measured, per-use
  overage line** — the one genuine metered dimension left in the personal-tool provider set — fed directly
  into the spend guard's design (track GB/month against the included volume, not just call count).
  Upgraded from canonical `<2.1>`'s `estimated` $49–$239 range to `measured` with a source + read-date.
- Personal-scale steady-state floor now **bounded**: ≈ $78–$279/mo (Massive $29–199 + SEC-API.io $49–55 +
  Supabase $0–25) — down from the pre-pivot SaaS draft's unbounded quote-only market-data line.
- Open items surfaced to the Lead (dollars only): 🟡 confirm which Massive tier + whether options-chain
  history needs a paid add-on (Data-Eng/DevOps) · 🟡 confirm the in-hand key is actually SEC-API.io + its
  tier (Director/Data-Eng) — resolves the $49–55/mo + overage line from `unmeasured` to `measured`.
- DRAFT, self-checked (gate ②). Reported once to the Lead (protocol 15).

### [Architect · 2026-08-01] Phase-1 design ADR authored — `docs/adr/ADR-0001-phase1-validation-tool.md`
Dispatched by Lead (D-TRADE-020 pivot). Re-read in order: charter §1/§2/§3 (revised) · decisions
016–020 · canonical `<1.1>..<4.3>` (re-authored) · my oracle-boundary row (PARTIAL, re-scoped) · PROFILE ·
stage-plan · PROJECT-CONFIG §2–4. Grounded in the **real artifacts** (LL-39): short-interest FINDINGS +
`run_analysis.py` (the CV harness) + `rolling_watchlist (3).py` (the `_gates`-flag screener idiom).
- **Organizing claim:** the scanner already guards each component with a `_gates` flag whose default *is*
  its study verdict (`short_interest_gates=True` cleared · `catalyst_gates=False` null · `float_gates=False`
  no-data). **Phase 1 = run the studies' walk-forward-CV harness on each *options*-screener component and
  set its gate flag from the verdict** — "ships only the components that work" becomes mechanical (`<1.1>`).
- **`<3.5>` CONFIRMED (recommend Lead absorb):** Python core; **drop Node/Fastify/React** entirely;
  Supabase retained **read-only** this phase (results written **file-first** like the studies' `cv_results*.csv`
  — defers the Supabase-write/D-TRADE-014 question OFF the critical path). D-TRADE-017 Node blocker doesn't bite.
- **Lane re-cut CONFIRMED** (charter §3 draft → absorb): A ingest+universe+store (SDE1·Data-Eng) · B screener
  (AI/ML) · C validation-engine (AI/ML) · D validation-**audit** (AIQ, *independent* — may not import C's
  outputs = builder≠judge encoded as an import rule) · E infra/CI/gate/spend (DevOps·FinOps).
- **9 non-negotiables → oracle legs** (each with a negative control): NN-1 no-lookahead · NN-2 pre-registered
  bar frozen-before-run (BOTH LOO ∧ ≥50% of 30-seed 5-fold beat naive OOS) · NN-3 AIQ re-derives from RAW
  (builder≠judge) · NN-4 gate-flag conformance (a `True` flag needs a `cleared` verdict) · NN-5 universe
  integrity · NN-6 schema/freshness · NN-7 leg K/T · NN-8 spend guard · NN-9 QA reproducibility. NN-1..4 =
  CRITICAL (frontier A6 + protocol-17 AIQ validation).
- **The one genuinely new contract:** the **directional-correctness label** over the option's DTE window
  (underlying move, NOT P&L — `<1.1>`/`<1.4>`); harness reuses `evaluate_loo`/`evaluate_multiseed_kfold`
  verbatim, only target+horizons change. Metric FORM is an open point (OP-1, Director+AI/ML+AIQ ratify).
- **HARD preconditions to build dispatch (none mine to waive):** P-1 Director re-scopes D-TRADE-010 ·
  P-2 locate+read the two ZIPs (screener, 0DTE engine — location TBD) · P-3 provider + **historical
  options-chain/IV availability** discovery (gates whether IV-rank is testable at all) · P-4 Director
  ratifies the pre-registered bar · P-5 B5 secrets. Co-sign slots: AI/ML·AIQ·SDE1·Data-Eng·DevOps·FinOps·QA·SecOps.
- **Blockers surfaced to Lead (protocol 11):** (i) the two ZIPs' location — component decomposition binds
  against source; (ii) D-TRADE-010 re-scope is Director-pending; (iii) historical options-chain/IV
  availability unknown — the single biggest Phase-1 data risk (R-3). ADR = PROPOSED, awaiting co-sign + GO.
- **Reconciled on rebase to D-TRADE-021 (protocol 16 — the ratified decision governs over my draft):** the
  Lead ratified AIQ's clearance bar (LOO ∧ **≥90% of ≥30 seeds** beat naive OOS, VOID on any leakage/
  contamination) into canonical `<3.4>` while I was drafting. My ADR NN-2 originally read the studies' older
  **≥50%** verdict threshold [`run_analysis.py:127`] — corrected in ADR-0001 to cite **D-TRADE-021 / `<3.4>`**
  as the governing bar (the catalyst-68%-coin-flip is exactly why ≥90%, not ≥50%). Consequently P-4 is
  **narrowed**: the CV-agreement bar is already ratified (D-TRADE-021); what still needs a Director/AI-ML/AIQ
  ruling is only the **directional-correctness label FORM** (OP-1) — the DTE-window target, which D-TRADE-021
  did not fix. Also aligned module name `helm/store` → **`helm/storage`** to match DevOps's in-flight
  harness draft (anti-churn). No other substance changed.
- **Convergence with AI/ML + FinOps (protocol 15/16 — reconciled, not re-reported):** on the same rebase I
  read AI/ML's and FinOps's pivot entries. **(1)** AI/ML **independently hit my P-2 blocker** — the screener
  + 0DTE ZIPs are not locatable on this host (searched Downloads incl. every `files*.zip`, Desktop,
  Documents, `..\Trade\`, all 4 study dirs). Two oversight seats corroborate; the Lead consolidates — I do
  **not** re-ping separately. **(2)** AI/ML independently proposed my OP-1 two-tier target and resolved OP-3
  the better way: the directional-correctness binary is **volatility-scaled on OHLCV alone**, so the *label*
  no longer depends on the unconfirmed options-chain/IV data — this **de-risks R-3** (ADR OP-1/OP-3/R-3
  updated to adopt the OHLCV-only label as recommended primary; options/IV dependency now scoped to the
  IV-rank *component* only). **(3)** AI/ML's survivorship / point-in-time-universe-membership flag is already
  carried by NN-1 + NN-5; cross-referenced. FinOps's measured SEC-API.io $49/mo GB-overage feeds NN-8's
  spend guard (track GB/month, not just call count) — noted, no structural change.

### [DevOps · 2026-08-01] ADR-0001 co-sign + module-layout alignment (design-review, still holding on P-1)
- Read `docs/adr/ADR-0001-phase1-validation-tool.md` (Architect, PROPOSED). Its own **P-1 precondition
  confirms my existing hold was correct, not resolved** — "no seat writes production code until P-1
  clears" (Director must still confirm Phase-1 build is outside D-TRADE-010's intent).
- **Co-signed (§H of harness-design.md):** NN-7 (leg K/T, incl. the two ADR-0001 §4 import-boundary rules —
  `helm/screener` can't import a provider SDK directly; `helm/validation/audit` can't import
  `helm/validation/engine`'s outputs, the mechanical backbone of builder≠judge) + NN-8 (spend guard) +
  Lane E's gate-legs/import-boundary non-negotiable. Declined to co-sign NN-1..6/9 — not my lane (AI/ML,
  AIQ, SDE1, Data-Eng, QA own those).
- **Re-aligned module names to the ADR's confirmed layout** (§4): `helm/ingest/` (single sanctioned module
  for all provider adapters, not per-provider files as I'd drafted), `helm/storage/` (ADR confirms my
  earlier guess), `helm/spend/` (the guard wrapper — new to my design, now incorporated in §E).
- Every leg I'm co-signing already has a concrete design + negative control (§B–§E) — the co-sign adds no
  new design debt; only P-1 + wave-entry GO stand between it and armed.
- Reported once to the Lead (protocol 15), folded into the next report rather than a standalone ping —
  routine confirmation, not a new blocker.

### [Architect · 2026-08-01] ADR-0002 — Rolling-Watchlist browser UI (D-TRADE-023, design note)
Dispatched by Lead. Kept proportionate (personal side-tool, not ADR-0001 scale). Grounded in the **real
source** (LL-39): read `tools/rolling_watchlist.py`'s return dicts + `main()` pipeline, and the approved
mockup HTML (structure + its `const DATA` consumer). `docs/adr/ADR-0002-rolling-watchlist-web-ui.md`, PROPOSED.
- **Framework = Flask** (not FastAPI): single-user localhost wrapper over synchronous pandas/Massive calls
  → no async/schema/uvicorn machinery warranted; `flask run` one-command; run `threaded=True`. Python core,
  Node stays dropped (`<3.5>`), no toolchain re-verify.
- **Adapt the approved mockup IN-PLACE** (not rebuild): it's Director-approved, fully self-contained
  (embedded fonts + inlined D3, **no CDN**, offline-clean), and its render layer already encodes the
  contract. Only change = swap the `const DATA` literal + `hashSeed` synthetic generator for a
  `fetch('/api/scan')`. Copy the source into `tools/web/static/index.html`.
- **API contract** matched to the mockup's existing camelCase `DATA` consumer (minimizes Designer rewiring):
  `GET /api/health` · `POST /api/scan` → `{meta,stats,candidates:[Candidate]}`. Each `Candidate` maps 1:1
  from the scanner dicts (guardrail←`scan_guardrail_criteria`, s3←`compute_s3_score`, phase←`classify_pnd_phase`,
  intraday←`analyze_intraday_alignment`+`load_intraday`, simulatedTrades←`simulate_day_trades`); non-holding
  names carry `holdingUp:false`+nulls, mirroring the real scan + the mockup. Serializer rules: NaN→null,
  Timestamp→ISO8601, DataFrame→records.
- **Security NN (legs K/T):** Massive key resolved **server-side only**; `/api/scan` never accepts a key
  from the client; provider calls never leave `tools/rolling_watchlist.py`. `/api/health` reports key
  *presence*, never value.
- **Module layout `tools/web/`** (disjoint; scanner UNCHANGED): `app.py` (routes) · `scan_service.py`
  (orchestrates the scanner's fns, returns data instead of printing) · `serialize.py` (dict→contract) ·
  `static/index.html`. Web layer is a thin adapter — no logic of its own.
- **3 disjoint build tasks, all `adr_reference: ADR-0002`:** AI/ML = backend (app/scan_service/serialize) ·
  Designer = frontend wiring (DATA→fetch + loading/empty/error states, design system 1:1; UI-gate satisfied)
  · DevOps = `flask` install + run entry + server-side key env + boot smoke.
- **Open points:** OP-A long scans block the request → v1 synchronous + loading state (one user; job model
  deferred). OP-B the intraday chart is the one cross-seat interface point — Designer + AI/ML confirm the
  bar-array shape against the mockup's D3 code together before wiring the chart. Tier = STANDARD.
- Reporting to the Lead + a direct pointer to each of the 3 waiting seats (protocol 11).

### [Designer · 2026-08-01] Rolling Watchlist dashboard — mockup isolated from sandbox chrome (D-TRADE-023)
Re-activated by the Lead: `tools/rolling_watchlist.py` ships as a browser dashboard, reusing the
Director-already-approved "Rolling Watchlist" claude.ai mockup (stat strip · watchlist table · Guardrail #1
detail panel · S3 score breakdown · P&D phase stepper · intraday pivot chart), wired to the real
Massive-backed backend instead of the mockup's illustrative data. INTEGRATION work, not new design — the
approved visual design is preserved exactly, not redesigned.
- **Done this entry:** isolated/cleaned the real mockup source (Lead-supplied, 193,642 bytes,
  `artifact-7601fb84-1785090475-b26e.html`) → `docs/design/rolling-watchlist-dashboard.html` (181,137
  bytes). Stripped ONLY the claude.ai frame-runtime bootstrap (the iframe-sandbox script + `__FRAME_PREAMBLE`
  + postMessage/theme/scroll-restore plumbing — 12,177-byte first line, verified as a single self-contained
  block via structural grep, not interleaved with app logic) and replaced it with a minimal standalone
  `<head>` (charset/viewport/title/base reset). The design's own CSS (custom `TradeSlab`/`TradeMono`
  embedded fonts, `#faf9f5`/`#141413` palette, `tw-*` class convention), markup, and rendering script
  (mock-data generation + S3-bar/pivot-chart SVG logic) are byte-identical to the source — copied verbatim,
  not retyped, to guarantee no drift from the approved design (checkable artifact, protocol 16).
- **Verified, not just claimed:** grepped the app's own markup+script (lines 235–627 of the source) for any
  `postMessage`/`__frame`/`window.claude` reference — zero hits, confirming the design was already
  self-contained and portable. Loaded the cleaned file standalone in-browser (no claude.ai runtime): zero
  console errors, full DOM text-render-confirmed for every named section (stat strip 4 tiles, 6-row
  watchlist table, Guardrail #1 6-item checklist, S3 breakdown + total, 7-phase P&D stepper, pivot
  chart pivot/R1/S1 levels) — the JS executed and computed values correctly with no sandbox APIs present.
- **Correction on rebase (protocol 16 — reconciled before push, not left stale):** this entry originally
  said the Architect's API contract hadn't landed. It landed in the same rebase, as ADR-0002 above —
  written concurrently, not read by me before this entry was drafted. ADR-0002 also answers my placement
  question: the served file is `tools/web/static/index.html` (copy the approved mockup in-place), not
  `docs/design/`; my `docs/design/rolling-watchlist-dashboard.html` stands as the cleaned design-asset
  source of record, not the served path.
- Self-checked (gate ②, mechanical: byte-diff-verified copy, zero-console-error render). No CRITICAL
  cross-document number/invariant here (protocol 17) — routine design-asset work, not escalation-worthy.

### [Architect · 2026-08-01] ADR-0002 refined vs AI/ML's pre-wiring grounding (contract confirmed, OP-B resolved)
AI/ML came online, read `tools/rolling_watchlist.py` in full, and sent technical grounding + design forks
BEFORE wiring (exactly the right sequencing — protocol 11). All forks were already decided in ADR-0002; I
confirmed each and folded in one genuine refinement it surfaced:
- **Intraday chart:** client-rendered from DATA, **not** the `plot_intraday_alignment()` PNG — now stated
  explicitly. Extended `intraday.bars` to fully serialize `annotated` (per-bar `abovePivot`/`aligned`/
  `alignedTrigger`) so the D3 chart can shade aligned bars + mark the trigger. **This resolves OP-B
  concretely** — the bar-array shape is now fixed, not a mid-build guess.
- **`classify_pnd_phase`:** latest value only (`.iloc[-1]`) for the stepper — confirmed, no per-day history.
- **`scan_all_patterns`:** reduced to the recent-window fired-key list (the `tw-pattern-chips`), not the
  per-bar DataFrame — confirmed in the provenance note.
- **DataFrame/Timestamp shaping** (watchlist, annotated, trades): already covered by the serializer rules
  (DataFrame→records, Timestamp→ISO8601, NaN→null).
- No contract revision needed beyond the bars-alignment fields; replied directly to AI/ML (Lead copied).

### [SDE1 · 2026-08-01] ADR-0001 co-sign — NN-6 (schema/freshness), design-review only, holding on P-1
- Read ADR-0001 in full (PROPOSED). Its P-1 precondition confirms my HOLD is correct, not resolved — no
  DDL/code until the Director clears D-TRADE-010 for Phase-1 build.
- **Co-signed NN-6** (data-schema/freshness leg, my lane): a malformed or stale ingested row FAILS rather
  than silently feeding the model. Concrete once §6.1's entities exist as real DDL.
- **§6.1 entity contracts — no objection to the shape.** One design note to carry forward, not a blocker:
  `validation_verdicts.reproduced_by_aiq` gating a `cleared` verdict (NN-3) is a write-once/append-only
  invariant — enforce it in the DB (constraint/trigger + forced row-security), not just app logic, per my
  own PROFILE lessons (a table-owning role bypasses an app-layer-only check silently).
- **Flagging a sequencing gap for the Lead's wave-entry dispatch, not a blocker:** `helm/ingest/` is
  co-owned SDE1·Data-Eng (ADR §4/§5), but **Data Engineer is not yet spawned** (PROJECT-CONFIG §3) —
  nothing for me to do from HOLD, just don't dispatch lane A assuming a seat that isn't live.
- Declined to co-sign NN-1..5/7-9 — not my lane (AI/ML, AIQ, Data-Eng, SecOps, FinOps, QA own those).
- Reported once to the Lead — folded into the next report, not a standalone ping.
  Pushed the refined ADR-0002.

### [DevOps · 2026-08-01] D-TRADE-023 dashboard infra delivered (ADR-0002 §4, separate from HELM)
- Read `docs/adr/ADR-0002-rolling-watchlist-web-ui.md` (Architect, PROPOSED) — Flask (not FastAPI),
  the approved mockup adapted in-place, `tools/web/{app.py,scan_service.py,serialize.py,static/,README.md}`
  layout, the `/api/health` + `/api/scan` contract. Scoped to the equity-side tool only; does not reopen
  HELM's no-web-surface framing. No D-TRADE-010-style freeze applies — this tool is live and already
  receiving commits, so unlike HELM I built directly rather than holding.
- **Delivered my three §4 tasks:** `flask==3.1.3` installed + pinned in `tools/requirements.txt`
  (alongside the tool's previously-uncaptured numpy/pandas/matplotlib deps); `.claude/launch.json`'s
  `rolling-watchlist-web-ui` entry running the Architect's exact command; `scripts/
  smoke_rolling_watchlist_web.py` (boots the server, polls `/api/health`, asserts `ok=true` +
  `massiveKeyPresent` is boolean — never logs the key itself, leg K discipline — then stops it; verified
  it SKIPs cleanly with exit 2 right now since `app.py` doesn't exist yet); `tools/web/README.md` (run
  steps + the server-only Massive-key contract, matching `_resolve_massive_api_key()`).
- Updated my board row to show both statuses at once (HELM holding, D-TRADE-023 active) rather than
  letting one overwrite the other's visibility.
- Messaged AI/ML directly (protocol 11) — their `app.py`/`scan_service.py`/`serialize.py` land against
  this infra; the smoke check + launch.json target `tools/web/app.py` exactly as ADR-0002 specifies.
- Reported once to the Lead.

### [AI/ML · 2026-08-01] D-TRADE-023 backend delivered — `tools/web/{app,scan_service,serialize}.py`
- Read `tools/rolling_watchlist.py` in full before wiring anything (all 1367 lines — `main()` at line
  1172 is the reference pipeline); read ADR-0002 in full (Flask, the §3 contract, module layout) before
  writing a line of the API layer, so nothing got built against a guess.
- **`scan_service.py`** mirrors `main()`'s loop exactly (same functions, same call order, same
  hardcoded `catalyst_gates=False`/`short_interest_gates=True`/`pattern_lookback_bars=6` main() itself
  uses) but returns raw per-candidate dicts instead of printing. One correction to my own first read of
  the contract: candidates are built by iterating `scan_rollover_watchlist`'s own output rows (only
  tickers with a qualifying spike), not literally every requested ticker — confirmed against the
  mockup's `DATA` array (all 6 example rows have real spike data; `stats.candidatesScanned`'s subtitle
  "≥20% gain, ≥2x rel. volume" only makes sense as the spike-qualifying count) before committing to that
  shape, rather than assuming.
- **`serialize.py`** is the only place DataFrame/Timestamp/NaN → JSON happens, per ADR-0002 §2.3.
  `intraday.bars` shaped from `analyze_intraday_alignment`'s underlying OHLCV data; `s3`'s four
  component keys stay snake_case (`pattern_price`/`risk_reward`/…) matching the contract's own example
  verbatim, not camelCased like everything else — the contract governs over "be consistently camelCase."
- **Verified, not just written:** DevOps's `scripts/smoke_rolling_watchlist_web.py` passes against the
  real app under `flask --app tools/web/app run` (`PASS: /api/health up, ok=true,
  massiveKeyPresent=False` — no live key in this session, degrades exactly as designed). A synthetic-
  data smoke test (throwaway, not committed) exercises the full holding-up candidate path — guardrail,
  s3, phase, intraday bars, patterns, simulatedTrades — end-to-end and confirms the response survives
  `json.dumps` with zero NaN/Timestamp/DataFrame leakage.
- **🟡 Finding surfaced to Designer + Lead (protocol 11, before either of us wires the chart/fetch):**
  the mockup's current JS **re-derives** three things client-side that ADR-0002 §3's contract already
  sends pre-computed — guardrail pass/fail (hardcoded 10.0/2.0/2–20/3.0 thresholds, `DATA.forEach` block)
  · S3 total/rating (summed from component pairs) · the entire intraday chart series (`buildSeries`
  synthesizes a fake 40-point path via `mulberry32(hashSeed(ticker))`, not real bars). If left as-is,
  the client's hardcoded thresholds would silently diverge from the server's real, request-configurable
  ones (protocol 16 — two sources of truth for the same fact). Recommending the derivation block + the
  synthetic `buildSeries` path be replaced with direct consumption of the server's `guardrail`/`s3`/
  `intraday` objects, not just the `DATA` literal swapped for a fetch. Not my file to edit (Designer's
  write-lane) — flagged, not patched around.
- Reported once to the Lead + messaged the Designer directly with the exact shape (protocol 11).

### [Designer · 2026-08-01] Rolling Watchlist dashboard wired to the §3 contract (ADR-0002, D-TRADE-023)
Frontend build task delivered: `tools/web/static/index.html` (copied from my cleaned
`docs/design/rolling-watchlist-dashboard.html` per ADR-0002 §2.3's real served path). Only the `DATA`
literal + its mock-generation code were touched; every render function, CSS class, and layout is
byte-identical to the approved mockup — verified by diffing my edit boundaries against the original.
- **`mapCandidate()` adapter:** renames/flattens the §3 `Candidate` (server-computed) onto the exact flat
  shape the approved render functions already read (`d.gainOk`, `d.s3Pct`, `d.s3Rating`, etc.) — it
  performs zero computation of its own; guardrail/S3/phase/pattern logic stays server-side, single source
  of truth in Python, per ADR-0002 §2.3's "no logic in the serving layer" principle.
- **`runScan(tickers, params)`:** `POST /api/scan`, then `empty → loading → loaded|error` state machine.
  Exposed as `window.runScan` — **not auto-invoked and not wired to any input control**, because none
  exists (see open item below). Loading/empty/error states added per the ADR's ask; empty state matches
  my own PROFILE lesson (deferred surfaces get a designed empty-state, not a dead-click).
- **OP-B (intraday chart) reconciled against the Architect+AI/ML resolution that landed while I was
  building:** `buildSeries()` now reads real `bars[]`/`pivots`/`priorHigh`/`priorLow` and picks the
  trigger bar via `bars.findIndex(b => b.alignedTrigger)` (the finalized per-bar flag), not a
  timestamp-string match. Confirmed the approved mockup's design (one trigger marker, its legend text
  "first bar above pivot & prior close") still holds 1:1 — the contract now also *supports* shading every
  aligned bar, a richer treatment than the approved mockup shows; **not added**, since that would be a
  design change outside "wiring, not redesign" and outside my unilateral authority (taste/hierarchy stays
  HUMAN + Director-approved, oracle-boundary row).
- **Cleanup debt removed** (not a design change): the static "Mockup · illustrative data" badge
  (`tw-mock-badge`) — a review-only annotation, now misleading on a live-wired build. Its CSS rule is left
  in place (inert, reusable) to avoid touching more than necessary.
- **Verified in-browser (not just claimed), file:// standalone, mocked `window.fetch`** against the exact
  §3 contract shape (incl. the finalized `abovePivot`/`aligned`/`alignedTrigger` bar fields): confirmed via
  `get_page_text` — stat strip/table/guardrail/S3/phase/patterns/chart all populate correctly from a
  2-candidate fixture (1 holding-up, 1 rolled-over skip row), the trigger circle resolves to the correct
  bar index even when a later bar is also `aligned:true`, and the pivot/R1/S1/prior-close chart labels
  match the fixture exactly. Also verified the error path (`fetch` rejecting → "Scan failed: …" renders).
  Zero console errors across every state. No live backend exists yet (AI/ML's `app.py` not built) — this
  is fixture-verified, not integration-tested against the real Massive-backed pipeline; that step is
  QA's/AI/ML's once `app.py` lands.
- **Two real open items, flagged not guessed past (protocol 11):**
  1. **No ticker-input mechanism exists anywhere in the approved mockup or ADR-0002's Designer task, but
     `tools/rolling_watchlist.py --tickers` is `required=True` with no default universe** (confirmed:
     argparse has no default; the module's own docstring says the candidate list comes from "StocksToTrade,
     Finviz, your [own screening]" — i.e., always user-supplied). `POST /api/scan` cannot run without
     tickers from *somewhere*. I did not invent an input control (a ticker box + Scan button, or a params
     form) — that's new UI surface, taste/layout territory the oracle-boundary row keeps HUMAN +
     Director-approved, not mine to add unilaterally. `window.runScan()` is wired and ready; it just has
     no caller yet. Recommend: Architect/Director decide the shape (a real input control needing my mockup
     + approval per protocol 10, vs. a hardcoded personal watchlist config file DevOps/AI-ML own).
  2. **The approved mockup has no UI for `simulatedTrades`**, even though D-TRADE-023's own decision text
     lists "the trade simulator's results" as in-scope for the browser UI, and the §3 contract carries a
     full `simulatedTrades` object. Not built — inventing that panel now would be redesign, not wiring, and
     the Director hasn't approved a mockup for it. Flagged for the Lead/Architect/Director; I'll mock up
     that section on request (UI-mockup gate, protocol 10) once it's prioritized.
- Messaged AI/ML directly (protocol 11) to confirm OP-B's now-resolved shape from my side too (redundant
  with the Architect's confirmation, but cross-checking a shared interface point independently is cheap
  and protocol-15-clean).
- **Reconciled on rebase (protocol 16) against AI/ML's entry directly above:** their 🟡 finding — the
  mockup's JS re-derives guardrail thresholds/S3 total/the intraday series client-side instead of
  consuming the server's precomputed `guardrail`/`s3`/`intraday` objects — is a real, correctly-flagged
  issue against the *original* mockup, and it's **already fixed** in this same commit (independently;
  I hadn't read their message when I built `mapCandidate()`/rewrote `buildSeries()`). Convergent, not a
  new blocker. AI/ML's backend is live (`flask --app tools/web/app run`, smoke-passing) — next step is
  integration-testing my wiring against their real `/api/scan`, not just my fixture. Reporting once to
  the Lead.

### [AI/ML · 2026-08-01] D-TRADE-023 — real browser integration test, one bug found + isolated
- Took Designer's own flagged next step: ran the REAL `flask --app tools/web/app run` server (synthetic
  data monkeypatched into `rolling_watchlist.load_daily`/`load_intraday`/etc. — no live Massive key in
  this session), loaded the REAL served `tools/web/static/index.html` in an actual browser, and called
  `window.runScan()` against the real `/api/scan` endpoint. Not a fixture on either side — a genuine
  end-to-end round-trip through my real `serialize.py` and Designer's real render functions.
- **Happy path (1 holding-up candidate, 0 skip rows): fully correct.** Verified via `get_page_text` —
  stat strip, table, guardrail checklist, S3 breakdown, phase stepper, and the intraday chart (pivot/R1/
  S1/prior-close labels matched the synthetic data exactly) all rendered correctly from the real HTTP
  response. Confirms AI/ML's backend and Designer's frontend are correctly wired end-to-end for this case.
- **🔴 Bug found + isolated (2 candidates, 1 holding-up + 1 rolled-over): `TypeError: Cannot read
  properties of null (reading 'toFixed')`.** Root cause: `tools/web/static/index.html:442`,
  `renderTable()`'s per-row template calls `d.relVol.toFixed(1)` **unconditionally for every row**,
  including rolled-over (`holdingUp:false`) ones. My backend correctly sends `relVol:null` for those —
  `scan_guardrail_criteria` (the only place relative volume gets computed) is only ever called on
  `holding_tickers` in `main()`'s real pipeline; a genuinely rolled-over ticker's rel-vol is **never
  computed** by the real system, so `null` is the honest value, not a bug in the serializer. The
  approved mockup's own synthetic fixture happened to fabricate a plausible `relVol` number for its 2
  skip-row examples (QTRB/TKDN) — masking that the real backend can't honestly supply one there. Isolated
  by re-running with only the holding-up ticker (passes clean) vs. both tickers (fails) — confirms the
  crash is specifically triggered by a null-`relVol` row reaching that line. `renderGuardrail()` has the
  same unconditional `.toFixed()` at line 467 but is unreachable for skip rows today (guarded upstream by
  `renderDetail`'s own `if (!d.holdingUp)` early-return) — not currently triggerable, flagging anyway
  since it's the same latent pattern.
- **Not my file to fix** (Designer's write-lane) — reported with exact repro + line numbers + root cause,
  not patched around. Recommended fix: guard the two call sites (`d.relVol != null ? d.relVol.toFixed(1)
  + 'x' : '—'`, matching how the table already handles `float`/`catalyst` "No data" states), not a
  backend change — fabricating a relVol number to avoid the crash would violate the same honesty
  principle as the earlier derived-fields finding.
- Cleaned up: killed both throwaway server processes, deleted the scratchpad harness script (not
  committed — synthetic-data test infra only, not shippable code).
- Reported once to the Lead + messaged Designer directly (protocol 11) with the exact repro.

### [DevOps · 2026-08-01] Formal smoke-check re-run against AI/ML's real app.py (D-TRADE-023)
- `git pull --rebase` picked up AI/ML's backend (`47db31c`/`2ca539a`) and Designer's frontend wiring
  (`841c2ed`). Ran `scripts/smoke_rolling_watchlist_web.py` for the record (the Lead's ask — AI/ML had
  already run it manually with the same result; this is the formal DevOps-owned re-run).
- **PASS:** `/api/health` up, `ok=true`, `massiveKeyPresent=false` (no live key installed in this
  session — expected, B5: the agent never handles the key value). Confirmed clean teardown — port 5000
  free again after the check, no lingering process.
- Reported once to the Lead.

### [Designer · 2026-08-01] Integration-tested against the real backend; found + fixed a live bug; Director-directed palette redesign + theme toggle
- **Integration test (not just fixture):** ran `flask --app tools/web/app run` locally against the real
  `tools/web/app.py`/`scan_service.py`/`serialize.py` AI/ML delivered. `/api/health` correct
  (`massiveKeyPresent:false` — no key configured in this session, degrades as designed). Ran a real
  `/api/scan` against 2 tickers: 0 candidates came back (correct — no market-data key means no price
  data, not a UI defect).
- **Found + fixed a real bug via that test:** a genuine 0-candidate result produced `Avg. S3 score: NaN%`.
  Root cause: `renderStats()` (untouched from the approved mockup — its mock `DATA` was never empty, so
  this path never ran) recomputed `candidatesScanned`/`holdingUp`/`alignedNow`/`avgS3Pct` client-side from
  `DATA.length`, instead of reading the server's own precomputed `stats` object (§3's `stats:
  {candidatesScanned,holdingUp,alignedNow,avgS3Pct}`, which I had wired to `DATA` but never actually
  consumed). Fixed both problems at once: `renderStats()` now reads `SCAN_STATS` (server-authoritative,
  same single-source-of-truth principle as `mapCandidate()`), with a `—` fallback when `avgS3Pct` is
  null. Re-verified against the real backend: renders `—` cleanly, zero console errors.
- **Director-directed redesign, mid-task, in this same session (taste — HUMAN + Director-approver,
  oracle-boundary row; this is exactly that approval, live):** (1) palette → mostly-white background,
  green accent + a second green "good" tone; kept `--warning`/`--critical` (amber/red) unchanged —
  greening error/positive-status colors alike would destroy the chip semantics the whole design leans on
  (Fails-core / Rolled-over chips need to read as "bad," not match "good"). Applied identically to both
  `tools/web/static/index.html` (served) and `docs/design/rolling-watchlist-dashboard.html` (design-asset
  record) — docs-in-sync, one palette. (2) Added a light/dark theme toggle: pre-paint `<script>` in
  `<head>` reads `localStorage`/system preference before first paint (no flash), a `.tw-theme-toggle`
  button wired to the CSS's existing (previously dead) `:root[data-theme]` attribute selectors — those
  selectors were already in the approved mockup's CSS, unused; wiring a real control to them is
  activating existing design, not inventing new surface. Dark theme's accent/good also shifted to
  green (lighter, for dark-background contrast) for brand consistency across both modes, now that both
  are reachable by an explicit control rather than just OS preference.
- **Verified (not just claimed):** light theme — `getComputedStyle` confirms `--surface:#FFFFFF`;
  full re-population (6-candidate fixture) confirmed every section still renders (stat strip, table,
  guardrail, S3, phase stepper, chart with trigger marker) — nothing was reduced. Dark theme — clicked the
  toggle live, confirmed `--surface` flips to `#0F1712` via computed style and a screenshot (one earlier
  screenshot was a stale capture — a tooling artifact, not a real bug; a second screenshot after a 1s wait
  showed the correct dark render). Toggled back to light, re-confirmed. Zero console errors throughout.
- **Mid-task correction (protocol 15):** the Director saw an in-progress empty-state screen (mid-wiring,
  before this session's integration test populated real data) and asked what happened to the graphs —
  explained the empty-state-is-correct-post-wiring reasoning directly and re-populated the live preview
  with illustrative data on the spot so nothing read as regressed. No code change needed for that one;
  communication gap, not a defect.
- Self-checked (gate ②: computed-style + rendered-output verification, not just code review).
- **Reconciled on rebase (protocol 16) against AI/ML's entry directly above:** their 🔴 finding — a
  rolled-over (`holdingUp:false`) candidate's real `relVol:null` crashes `renderTable()`'s unconditional
  `d.relVol.toFixed(1)` (`TypeError: Cannot read properties of null`) — is real, correctly root-caused
  (the real `scan_guardrail_criteria` never runs on non-holding tickers, so `null` is honest; the
  *approved mockup's own* synthetic DATA fabricated a `relVol` number for its skip rows, masking this),
  and **not something my earlier fixture testing exercised** (my fixtures always gave skip-row candidates
  a `relVol` value too, mirroring the mockup's own shape — same blind spot). **Fixed now, this commit:**
  guarded both call sites AI/ML named — `renderTable()` and the latent (currently unreachable)
  `renderGuardrail()` one — `d.relVol != null ? d.relVol.toFixed(1) + "x" : "—"`, matching the table's
  existing null-handling pattern for float/catalyst. Applied to both `tools/web/static/index.html` and
  the `docs/design/` copy (design-system parity). Re-verified against the real backend: a 2-ticker scan
  (1 holding-up + 1 rolled-over) no longer throws; the rolled-over row renders `—` cleanly. Reporting once
  to the Lead.

### [Designer · 2026-08-01] D-TRADE-024/025 delivered — ticker-input control + full trade-simulator panel
Director-ruled build tasks (`adr_reference: ADR-0002`, protocol 10's approval leg satisfied in the
decision row itself — no separate mockup round-trip required, per the Lead's dispatch).
- **D-TRADE-024 — `#tw-scan-bar`:** a ticker text input (comma/space-split, uppercased, empty-input
  validated → error state, not a silent no-op) + a "Simulate trades" checkbox + Scan button, replacing
  `window.runScan()`'s previous no-caller state. `scanParams()` supplies the request body's non-ticker
  fields from `tools/rolling_watchlist.py`'s own CLI defaults (verified against its `argparse` block:
  period 3mo, lookbackDays 5, gainThreshold 20, pullbackThreshold 50, guardrail thresholds 10/2.0/2–20/
  20M, intraday 5d/5m, simulate stopLoss 2.0/minRR 2.0/100 shares/giveback 15%) — v1 asks only for
  tickers + the simulate toggle, per the Director's own scope note ("just tickers in, Scan"), not a full
  settings form. Submit button disables during `scanState === "loading"` to prevent double-submit.
- **D-TRADE-025 — `renderSimulator(d)`:** trade-by-trade log (entry/exit time+price, P&L, reason),
  win-rate/final-P&L/P&L-per-share/trade-count stats, a halt banner when `halted`, and a cumulative-P&L
  curve (SVG, same construction pattern as the existing intraday chart — line+area+zero-reference,
  colored green/red off the sign of `finalPnl`). **No new CSS primitives** — reuses `.tw-stats`/`.tw-stat`
  (same tiles as the top-level stat strip) and `.tw-table` (same table as the candidates list) verbatim;
  the only genuinely new CSS is `#tw-scan-bar`'s own rules. Renders nothing when `simulatedTrades` is
  null/disabled — opt-in per-scan (`simulate.enabled`), not a section that ships in a dead/placeholder
  state (PROFILE lesson: a rail entry that dead-clicks is drift, not a shortcut — this isn't a deferred
  surface, it's a conditional one, so an empty state isn't warranted; it simply doesn't render).
- **Verified (not just claimed), all in-browser against `tools/web/static/index.html`:** empty-ticker
  submit → error state, not silent. A real submit (mocked fetch) → captured request body matches the
  §3 contract exactly, including `simulate.enabled` reflecting the checkbox. Simulator panel: rendered
  correctly with a 3-trade winning fixture; a halted/losing fixture showed the halt banner with its
  reason; a `simulatedTrades:null` fixture correctly showed **no** simulator section at all (not an empty
  one). Zero console errors across every case.
- **Mirrored to `docs/design/rolling-watchlist-dashboard.html`** for design-system parity: `renderSimulator()`
  verbatim + an illustrative `simulatedTrades` example added to the GRVX mock candidate (that file's
  default-selected ticker, so it's visible on load with zero interaction). **Did not** mirror the scan-bar
  markup there — this file has no backend to call, and a decorative Scan button that does nothing would
  be exactly the dead-click pattern my own PROFILE lessons warn against; a code comment notes the served
  app has the real control instead.
- Self-checked (gate ②: request-body inspection + rendered-output verification across 4 distinct
  fixtures, not just code review). Reporting once to the Lead.

### [FinOps · 2026-08-01] D-TRADE-026 absorbed — SEC-API.io floor line moves from contingent to confirmed
- The Lead's live-verified finding (direct authenticated call to `api.sec-api.io` → HTTP 200 real filing
  data, corroborated by the Director's own account) closes an open item I'd been carrying as `unmeasured`
  since the pivot revision. Updated `docs/finops/cost-model.md` (§1 table, §2.3, §3 floor, §5 open items,
  §6 provenance) and `docs/finops/governor-spec.md` (§3 cap table): the "EDGAR = $0 / is this even
  SEC-API.io" framing is retired — this is now a **confirmed, currently-active, paid subscription**
  ($49–$239/mo + $0.30/GB overage), not a future/contingent line. Narrowed the remaining open item to
  **which of the two paid tiers** (Personal & Startups vs. Business) — an account lookup, not a credential
  read or a new pricing question.
- **Decision-relevant point surfaced, not ruled:** this is the first floor line that moved from "assumed
  $0" to "real money being spent right now" — flagged as a fact, not a recommendation; whether that spend
  is wanted stays HUMAN/Director.
- Closes cost-model.md's named propagation slot in D-TRADE-026. Self-check only (routine, protocol 17 —
  a factual figure update, not a new engine rule or cross-document invariant). Reported once to the Lead.

### [FinOps · 2026-08-02] D-TRADE-027 absorbed — SEC-API.io tier fully closed
- Director confirmed the account is **Personal & Startups**, not Business (D-TRADE-027, `a002b5b`) —
  closing the last open dimension on this provider (issuer closed by D-TRADE-026, tier now closed too).
  Updated `cost-model.md` (§1, §2.3, §3, §5, §6) and `governor-spec.md` (§3 cap table, §7): dropped all
  "which tier"/"tier TBD" language, pinned to $49/mo annual or $55/mo monthly, 50 GB included, $0.30/GB
  overage. No new pricing research — this was FinOps's own already-measured figure, now pinned to the
  active row.
- **Verified the floor math didn't move**, per the Lead's ask: total steady-state floor is still ≈$78–279/mo
  — Massive's $199 ceiling already dominated the old $49–239 SEC-API.io spread, so pinning the tier narrowed
  SEC-API.io's own uncertainty without changing the total range. Said so explicitly rather than silently
  re-deriving a new-looking number.
- **Gave the guard a real starting cap value for the first time** (governor-spec.md §3): recommended 40 GB/
  month (80% of the confirmed 50 GB quota) as a headroom cap — previously this row could only be a
  placeholder; the boundary is now fully known so a concrete number is possible.
- **Only Massive's tier remains open** on the provider-confirm item (SecOps/Data-Eng). Self-check only
  (routine, protocol 17). Reported once to the Lead.

### [SecOps · 2026-08-01] D-TRADE-020 re-scoped confirm task — provider tier + SEC-key identity CLOSED, new credential-exposure finding
- **Re-read on dispatch-freshness:** pulled, read the re-authored canonical-design.md §1-5, my re-scoped
  oracle-boundary row (ORACLE, scope narrowed — "is the personal-tier account actually compliant" is now
  light-confirm, not the prior commercial-tier gate), stage-plan.md before acting.
- **Massive/Polygon tier — re-scoped LOW-MEDIUM (was HIGH).** No API-level "my plan" endpoint exists
  (checked `search_endpoints` — confirmed absent), so exact plan name is Director-dashboard-only. Gathered
  entitlement evidence instead (2 cheap read-only calls via the connected Massive MCP, zero secret
  handling): real-time NBBO → `NOT_ENTITLED`; single-ticker snapshot's current-day fields all zero while
  prior-day EOD fields populate normally → both are the signature of a non-real-time, delayed/EOD self-serve
  tier, corroborating (not proving) the individual/personal-tier read the Director's pivot assumes. The
  commercial-use incompatibilities from D-TRADE-018 don't apply once `<1.2>` is personal-use-only. Not a
  blocker; Director may glance at the account dashboard to fully close the exact plan name.
- **SEC key identity — CONFIRMED, first-hand (verify-don't-attest, LL — did not take the Lead's note on
  faith).** Read the actual calling code: `cadence_check.py`, `pull_all_float.py`, `test_structure_check.py`
  in `C:\Users\beale\float-study\` all load `..\Trade\sec_api_key.txt` and pass it as `token` to
  `https://api.sec-api.io/float`. **The key is SEC-API.io, not direct EDGAR** — re-authored the Provider-1
  section of `tos-taint-review.md` in place (LL-19: re-author, don't patch beside stale text) rather than
  leaving the old "assumes direct EDGAR" verdict standing. SEC-API.io's own pricing page volunteers that
  redistribution is Enterprise-only — both self-serve tiers ($49/$199) are personal/internal-use, matching
  `<1.2>` → **LOW taint.** Flagged to FinOps: this is a paid subscription, not $0.00 EDGAR (D-TRADE-019
  needs correcting).
- **🔴 New finding, unplanned:** while tracing the calling code, found a live SEC-API.io token in plaintext
  in `C:\Users\beale\float-study\log_pull.txt` (4 occurrences, DNS-failure exception tracebacks) — outside
  this repo, so leg K can't see it; a personal-machine hygiene gap. **Did not repeat the value anywhere.**
  Recommended to the Director: rotate the token, scrub the log, install the *rotated* value at B5 (added a
  gating checkbox to `b5-secret-approval-checklist.md` S6).
- Updated `docs/security/{tos-taint-review,key-denylist,b5-secret-approval-checklist}.md` in place (my
  write-lane). Reported once to the Lead (protocol 15) with all four items (2 closed, 1 unchanged-open,
  1 new). No blocker on my own task — surfaced the exposure as an urgent flag, not a stall.

### [DevOps · 2026-08-04] D-TRADE-028 pivot absorbed — two small corrections, no structural change
- Read canonical `<1.1>`-`<3.6>` (options framing deleted, trailing-stop equity signals). Verified myself
  (not just the Lead's assessment) that `harness-design.md`'s legs K/T/G/import-boundary carry forward
  unchanged — grepped for options/delta/DTE language, found exactly one stale reference, fixed below.
- **Fixed:** §A's "options-screener/0DTE-engine ZIP not yet located" row was stale — canonical `<1.1>`
  confirms that search was for an artifact that never needed finding (P-2 MOOT); replaced with the actual
  state (`tools/rolling_watchlist.py`, in-repo, already the D-TRADE-023 dashboard's backend).
- **Fixed:** §C's leg K wiring plan updated for SecOps's D-TRADE-026/027 confirm task — K6 tightened from
  a name-only pattern to a confirmed host+param match (`api.sec-api.io`, `token=`). Noted (not mine to
  act on, already escalated by SecOps to the Director) the out-of-repo credential-exposure finding in
  `float-study/log_pull.txt` — outside leg K's reach by design (repo-scoped only).
- No structural change to the gate harness — legs, module layout, and the co-signed non-negotiables from
  ADR-0001 all stand. Still holding on actual scaffold files pending P-1.

### [AI/ML · 2026-08-04] D-TRADE-028 absorbed — validation-methodology-draft.md re-authored, holding on `<3.6>`
- Pulled, read canonical-design.md in full (not just the diff) before touching anything. Absorbed: options
  framing deleted (not parked) from `<1.1>`; `<3.6>` (the label/component-list/horizons) dispatched to the
  Architect for redesign, explicitly not reopened on the D-TRADE-021 bar or NN-1; P-1 (D-TRADE-010)
  unchanged, still Director-pending; **P-2 confirmed moot** — the screener was never missing, it's
  `tools/rolling_watchlist.py`, which I already know in depth from building `tools/web/scan_service.py`
  (D-TRADE-023) — independent corroboration of the canonical doc's claim from a seat that has actually read
  every line of that file, not just trusting the written record.
- **Re-authored `docs/roles/ai-ml/validation-methodology-draft.md` wholesale (LL-19/protocol 19)** — the
  prior draft's entire body (the DTE-window label, delta-implied threshold, IV-rank, the now-moot
  screener-location blocker) described the deleted options framing; patching alongside it would leave a
  doc saying two contradictory things. New version: §0 states what canonical `<3.6>` says survives
  unchanged (D-TRADE-021 bar, NN-1, per-component isolation, verdict format) · §1 names what's deleted ·
  §2 hands the Architect grounding, not a design — `simulate_day_trades()`'s current FIXED stop/target
  (not yet a trailing stop; exact line numbers from the function I already read building D-TRADE-023),
  the halt conditions' orthogonality to a trailing-stop redesign, and the confirmed-real, already-
  independently-testable component list (guardrail/S3/phase/8 pattern detectors/pivot-alignment trigger —
  all separable, no bundling needed, since D-TRADE-023 already wired each one independently) · §3 open
  items, honestly conditional on `<2.2>`'s still-open universe question rather than asserting my prior
  survivorship-bias concern still applies (it was scoped to a rolling-index backtest that may not exist
  anymore under the simplified universe).
- **Deliberately did NOT design `<3.6>`'s replacement label myself** — the Lead's explicit instruction:
  hold so AI/ML and the Architect converge once on the ADR revision rather than drafting two independent
  guesses (the same pattern that worked cleanly on the original label). Sent the Architect the §2
  grounding directly (protocol 11) so it's available before they start, not after.
- Dropped a stale git stash (a WIP continuation of the now-fully-superseded options-DTE label design,
  pre-dating D-TRADE-023) rather than applying it — it refined content that no longer exists.
- Reported once to the Lead.

### [SecOps · 2026-08-04] D-TRADE-028 pivot (options → stock/trailing-stop) — light cleanup, no verdict change
- Pulled, read the re-authored canonical-design.md `<1.1>`/`<2.1>` (options framing deleted, LL-19 applied
  a second time). Per the Lead's flag: found and removed the one residual options-chain-data-availability
  mention in `tos-taint-review.md`'s Provider 2 section (was carried as an open DevOps/Data-Eng technical
  item; now moot, not resolved — annotated in place rather than silently deleted, so the doc doesn't read
  as though the item was never there). Confirmed no other options/greeks/DTE/delta references remain
  outside the explicitly-labeled historical `<details>` block (OPRA/Nasdaq/NYSE exchange-agreement research,
  correctly kept as archival record of the original commercial-use analysis).
- **No change to the Massive/SEC-API.io LOW-MEDIUM/LOW taint verdicts** — the pivot doesn't touch either
  provider's compliance posture, only removes a now-inapplicable open item. Routine-tier edit (protocol 17
  — self-check only), not a re-review. No blocker; not reporting this as a full protocol-15 report since the
  Lead flagged it as informational/non-urgent — noted here for the record per two-document discipline.

### [FinOps · 2026-08-04] D-TRADE-028 absorbed — options-chain-data open item deleted, not resolved
- Pulled the second major pivot (options framing dropped entirely, `<1.1>` re-locked to plain stock
  buy/sell + trailing-stop exit). Per the Lead's flag: minimal impact on my numbers — Massive/SEC-API.io/
  Supabase pricing, tiers, and the floor estimate (≈$78–279/mo) are all unaffected; nothing there was
  options-specific.
- **The one thing that did change:** the "historical options-chain data availability/cost" open item I'd
  been carrying in `cost-model.md` (§1, §2.2, §3, §5) and `governor-spec.md` (§1, §7) since the first
  pivot revision is now **moot** (canonical `<2.1>`: "DELETED, not applicable"). Removed it everywhere it
  appeared — per LL-19/protocol 19, deleted rather than left as a stale "still open" line now that the
  product it was tracking a cost for no longer exists. No dollar figure changed; only that one open item
  disappeared. Renumbered governor-spec.md's failure-mode list from 3 items to 2 accordingly.
- Self-check only (routine, protocol 17 — a scope cleanup off an already-ruled decision, not a new number
  or invariant). Reported once to the Lead.

### [AIQ · 2026-08-04] D-TRADE-028 pivot absorbed (options dropped) — targeted update, not a rewrite
- **Pivot absorbed.** Verified `Trade - Lead 2` (session `local_4f888ab5…`) live before treating its
  message as authoritative (session IDs rotate, protocol 11/LL-36). `git pull --rebase` → `fb830f1`.
  Read canonical-design.md `<1.1>`/`<3.6>` (options framing DELETED per LL-19/protocol 19, applied a
  second time), decisions-log D-TRADE-028, oracle-boundary.md (still options-worded — the Lead flagged
  it "named, not yet done"), ADR-0001 (original, options-scoped — revision dispatched to Architect, not
  delivered as of this commit), stage-plan.md, AI/ML's `validation-methodology-draft.md` (also
  options-scoped, same staleness). Confirmed via repo tree: no `helm/` package exists at all yet — only
  `tools/` (the separate D-TRADE-023 dashboard) and docs. Nothing to audit, same as the Lead said.
- **Targeted edit this time, not a full LL-19 rewrite** — unlike D-TRADE-020, this pivot's own text
  explicitly carries my core protocol forward unchanged (D-TRADE-021 bar, NN-1 no-lookahead). Updated only
  `docs/eval/methodology-draft.md` §0 (scope) and §5 (HUMAN-boundary example) to stop asserting the
  now-dead options/DTE/IV-rank subject as current, replacing it with a pointer to canonical `<3.6>`
  (`▸ NOT DECIDED`, Architect's open ADR-0001 revision) — **did not invent the new label/component list
  myself**; that stays the Architect's call. §1–4 (re-derivation sequence, verdict format) and the
  D-TRADE-021 bar text are untouched, as they should be — subject-agnostic validation discipline.
- **Flag for the Lead (not a blocker, surfacing per protocol 16 — a claim should carry checkable state):**
  `docs/gate/oracle-boundary.md` and `docs/adr/ADR-0001-phase1-validation-tool.md` still describe the
  options-DTE subject throughout (screener composite score → calls/puts, DTE horizons, IV-rank, liquid-
  optionable universe) — D-TRADE-028's own propagation row already named both as "flagged, not yet
  re-authored," so this isn't new information, just confirming I read them as stale rather than current
  and didn't build against them. My Lane D (`helm/validation/audit`, import-boundary vs. lane C) and the
  NN-1/NN-3 legs in oracle-boundary.md's structure are unaffected regardless of the label rewrite.
- Still **HOLDING**. Reported once to the Lead (protocol 15).

### [Architect · 2026-08-04] ADR-0001 Revision 2 (D-TRADE-028 — options dropped, equity + trailing-stop)
Dispatched by Lead. Re-read the re-authored canonical `<1.1>..<3.6>` (wins, protocol 13a) + D-TRADE-024..028.
**Full re-author** of ADR-0001 to R2 (protocol 19, not patched), keeping the stable adr_reference id.
- **`<3.6>` label RE-DESIGNED into a two-leg contract** — the key deliverable. **Leg A** = entry-signal
  validation (each not-yet-validated component's trigger → forward return vs naive, the studies' harness
  verbatim). **Leg B** = exit-rule validation (realized return under the **trailing stop** vs the naive
  **fixed-holding-period exit**, D-TRADE-021 bar over the paired comparison). Endogenous holding period; no
  DTE/horizon for Leg B. Both obey NN-1.
- **Trailing-stop rule DEFINED (§6.3):** `stop = peak_since_entry*(1-trail_pct)`, ratchets up only, exit on
  `Low≤stop`; initial hard stop bounds a never-rises trade. **Built as a backward-compatible mode inside
  `tools/rolling_watchlist.py`'s `simulate_day_trades()`** (default off) — ONE implementation shared by the
  D-TRADE-023 dashboard sim panel + the validation harness. Bar-causal peak preserves NN-1.
- **NN-10 NEW:** trailing-stop params (`trail_pct`/`init_stop_pct`) fit on train folds only / pre-registered
  set — never chosen on the test fold. The specific leakage vector a trailing stop introduces. CRITICAL.
- **`<3.5>` `helm/screener` RE-SCOPED:** its old "ingest the missing options screener" job is moot (scanner
  is in-repo). Now = a **thin feature-extraction adapter** over `tools/rolling_watchlist.py`, which becomes a
  **shared library** imported by both `helm/screener` and `tools/web/` (D-TRADE-023). Shared-file change ⇒
  not BYPASS-eligible; coordinate the trailing-stop edit with the D-TRADE-023 seats.
- **`<2.2>` universe:** recommend **DROP `helm/universe` for Phase 1** (P-3) — validation runs over the
  studies' existing event-defined cohorts + user-supplied `--tickers`, no maintained live universe needed.
- **`<1.4>` boundary:** trailing-stop validation is Phase-1-critical (agree with Lead). Phase 2 = ONLY the
  from-scratch predictive-occurrence model (old option-P&L/0DTE Phase-2-A deleted). Trailing-stop
  *optimization* / adaptive-ATR = Phase 2, not Phase 1 (Phase 1 tests a small pre-registered grid).
- **§14 delta (ADR-0001 §13 / A6a-A6b):** named every removed variable (options label, DTE horizons,
  delta threshold, IV-rank, options-chain data dep, optionable-universe req, P-2, 0DTE reuse) + partitioned
  changes (label/components/universe RE-RESOLVED; screener/NN-5 REPAIRED) + carried-forward unchanged
  (NN-1/2/3/4/6/7/8/9, gate-flag claim, CV harness, stack, lanes C/D/E).
- **Carried forward per Lead's dispatch:** D-TRADE-021 bar + NN-1 explicitly NOT reopened. P-2 marked MOOT.
- **CRITICAL revision** → flagged AIQ's co-sign on the label/NN-10/baseline as load-bearing (protocol 17).
  Preconditions to build: P-1 (D-TRADE-010 re-scope), P-3 (universe), P-4 (ratify label params), P-5 (B5).
  Reporting to the Lead; ADR = PROPOSED, awaiting co-sign + GO.
- **Folded in AI/ML's grounding (crossed with the R2 push; reconciled, protocol 16):** two accuracy fixes
  to ADR-0001 R2 — (1) §6.3 now states the per-trade trailing stop is **orthogonal to** the simulator's
  existing *daily* circuit breakers (`max_loss_per_trade`/`max_daily_loss`/`profit_giveback_pct`) — they
  compose, don't conflate; (2) corrected "6 pattern detectors" → the **8** `scan_all_patterns` detectors
  (added premarket-pivot/premarket-high). AI/ML's other points already matched R2 (fixed→trailing is new
  logic not a tweak; survivorship concern conditional on P-3). Replied to AI/ML. Pushed.

### [AI/ML · 2026-08-04] ADR-0001 R2 reviewed — co-signed on Leg A/trailing-stop, two items pinned before Leg B/NN-10 lock
- Read R2 in full (not the diff alone) before responding — the co-sign the Architect asked for is
  load-bearing (§12, CRITICAL tier), not a formality. Re-verified `simulate_day_trades()`'s actual code
  again (not trusting my own earlier read from memory) to confirm the backward-compatible trailing-stop
  claim: adding an opt-in `trail_pct`/`init_stop_pct` pair defaulting to None/off is a genuinely clean,
  additive change — the existing bar-causal loop already tracks position state per bar, so a running
  `peak` costs one field, and "ratchets up only" falls out of a running max for free. **Co-signed: Leg A
  + the trailing-stop mechanics.**
- **Two precision requests sent to the Architect before treating §6.3 as fully locked** (not blocking,
  pinning): (1) the exact effective-stop formula — read "initial hard stop governs until the peak
  advances" as `max(init_hard_stop, peak*(1-trail_pct/100))`, monotonic non-decreasing; asked for it
  stated explicitly rather than prose, since a formula error here is a live NN-1 risk (the stop must never
  silently retreat). (2) whether trail mode disables the fixed target entirely (standard practice, my
  recommendation) or keeps both — the ADR is silent and this is a real behavioral fork, not a detail.
- **One methodological finding for Leg A, sent to Architect + AIQ:** the binary pattern-trigger components
  (bull-flag, ABCD, etc.) may fire too rarely across the backtest window for any CV scheme to produce a
  meaningful verdict. Proposed a minimum-trigger-count floor before a component enters CV at all — below
  it, verdict = **UNMEASURED**, not NOT CLEARED (my own PROFILE lesson: absence is never a judgment).
  Pre-registering the *existence* of the floor now, concrete number once real trigger counts are visible.
- **Messaged AIQ directly (protocol 11, same convergence pattern as the D-TRADE-021 bar) on NN-10's precise
  procedural meaning for Leg B** — since the pre-registered trail grid (OP-1) isn't a fitted regression,
  "fit on train folds only" needs a concrete reading: if the analysis ever selects "the best grid point,"
  that selection must happen via nested CV (pick on train, score on held-out test, aggregate OOS across
  outer folds) — never picking whatever looks best on the full/test sample. Asked AIQ to confirm before I
  build the fold-splitting logic one way and they audit it expecting another. **Holding Leg B + NN-10 as
  co-signed until AIQ confirms** — the two builder/auditor seats should converge before either locks in,
  not discover a mismatch after code exists.
- Reported once to the Lead.

### [AIQ · 2026-08-04] ADR-0001 Revision 2 methodology audit — NOT co-signing as-is, 3 cited objections
- **Load-bearing review per protocol 17** (§6.2/§6.3/§6.4/NN-10/§12), dispatched by the Lead, Architect
  named my sign-off specifically as blocking. Read R2 in full (not just the diff) before assessing. This
  is my oracle-boundary mandate — independently re-derive/audit, VOID on leakage/contamination — applied
  to a design doc pre-run instead of a result post-run (same LL-44 pre-registration spirit as the
  D-TRADE-021 bar itself: catch a flaw in the method before it produces a number, not after).
- **Verdict: NOT a clean co-sign.** Found 3 specific, fixable gaps — not a rejection of the overall design,
  which otherwise correctly reuses the proven 4-study harness. Full citations + proposed fixes sent to the
  Lead by message; summarized here for the record (two-document discipline).
  1. **Builder≠judge gap at the feature-extraction layer** (§4 lines 74/76/82-84). The import-boundary rule
     bars `helm/validation/audit` from importing `helm/validation/engine`'s outputs, but says nothing about
     `helm/screener`'s outputs — and `helm/screener` is AI/ML-owned code that performs real transformation
     ("exposes each component's per-bar signal... as a tidy feature frame"), not a raw pass-through. If I
     consume that adapter's feature frame instead of calling `tools/rolling_watchlist.py`'s primitives
     myself, a lookahead/alignment bug in the adapter (Lane B, AI/ML) would be invisible to both the engine
     (Lane C) and my audit (Lane D) — both would inherit the same bug silently. This is the "two lanes owned
     by the same seat stand in for independence" version of the trap my own methodology already names for
     a single session's two modes.
  2. **NN-10 is scoped narrower than the leakage mechanism it names** (§6.4 lines 128-131, §8 line 160, §10
     OP-3 lines 183-185). NN-10 covers `trail_pct`/`init_stop_pct` only. The Leg-B naive baseline's `N`
     (OP-3: "the median realized holding period of the trailing-stop arm") is the **identical class of
     data-derived free parameter** — and unlike `trail_pct`/`init_stop_pct`, OP-3 never says N is computed
     train-fold-only. As written, N can be computed from the same test-fold trades used in the paired Leg-B
     comparison, which means the "naive" baseline is constructed using outcome information from the arm
     it's being compared against (trailing-stop trades ride longer exactly when they're winning, so a
     test-fold-derived median N is not independent of realized profitability) — this could inflate or
     deflate the apparent trailing-stop edge in either direction, and isn't a hypothetical: it's the direct
     answer to "does this leak" for the specific design as written.
  3. **NN-10 doesn't address selection-among-a-pre-registered-grid** (§6.4, §8 NN-10, R-2 line 197, OP-1
     lines 178-180). OP-1's plan is a small fixed grid (e.g. 3×2=6 combos), not per-fold fitting — so the
     practical risk isn't "fitting on the test fold" (which NN-10 correctly blocks) but "test all 6 cells,
     report whichever one clears" — a multiple-comparisons/cherry-pick vector R-2 already names as a risk
     but only mitigates with "record `n_comparisons`," without saying n_comparisons is ever used to adjust
     anything. Recommended either one pre-registered primary cell (rest = sensitivity, not cleared-eligible)
     or a stated per-comparison correction.
- **Proposed fixes are all additive/clarifying, not a redesign** — a Revision 3 addendum or a P-4
  ratification note could close all three without touching the sound parts of R2 (the two-leg structure,
  the harness reuse, the gate-flag mechanism). Will co-sign promptly once addressed.
- Reported to the Lead (protocol 15/17) with full citations. Still HOLDING otherwise — no code exists yet.
- **Converges with AI/ML's own direct message (protocol 11, found on this rebase)** — they independently
  flagged NN-10's grid-selection ambiguity too and proposed nested CV (pick the grid cell on train, score
  OOS on held-out outer folds) as the concrete reading, holding their own Leg-B/NN-10 co-sign until I
  confirm. Replying directly to AI/ML: nested CV resolves finding #3 above (grid cherry-picking) — agreed,
  that's the right mechanism. It does **not** resolve finding #2 (the Leg-B baseline `N` itself) — a
  distinct parameter AI/ML's message doesn't address — so that objection stands separately.

### [AI/ML · 2026-08-04] Converged with AIQ on all 3 audit findings — engaged, not just acknowledged
- Read AIQ's full 3-finding audit (not just the summary that reached me by message) before responding to
  each, since two of the three land on my own lane.
- **Finding #1 (builder≠judge gap, `helm/screener`) — agreed, not previously covered by my own review.**
  AIQ's audit is right: §4's import-boundary rule bars `helm/validation/audit` from `helm/validation/
  engine`'s outputs but not from `helm/screener`'s — my own code, doing real transformation, not a
  pass-through. If AIQ's audit ever consumed my adapter's feature frame instead of independently calling
  `tools/rolling_watchlist.py`'s primitives themselves, a bug in my adapter would be invisible to both
  lanes — the exact "two lanes, same seat, no real independence" trap NN-3 exists to prevent. Committed to
  building `helm/screener` as a genuinely thin adapter regardless (matches R2's own description) precisely
  so AIQ never has a reason to import it. Sent to the Architect for the import-boundary rule extension.
- **Finding #2 (Leg-B baseline `N` leaks via test-fold derivation) — engaged directly, proposed a fix.**
  Confirmed AIQ's read is correct (a test-fold-derived median holding period is correlated with which
  trades won, biasing the "naive" comparator). Proposed extending the SAME nested-CV mechanism already
  agreed for `trail_pct`/`init_stop_pct` (train-fold-only) to `N` too — not new machinery — with OP-3's
  existing "fixed N as sensitivity" clause repositioned as the leakage-free complement, not just a
  robustness add-on. AIQ and I converged on this before either finalized a position. Sent to the Architect
  to fold into R2 as an NN-10 extension.
- **Finding #3 (grid cherry-pick) — already resolved** by the nested-CV reading AIQ and I converged on in
  the prior exchange (see above). AIQ confirmed this independently in their audit.
- **Net: co-signing Leg B + NN-10 as soon as the Architect folds in fix #1 (import-boundary) + fix #2
  (train-fold-derived N)** — both are additive/clarifying per AIQ's own characterization, not a redesign;
  I'll build the fold-splitting logic and the thin-adapter boundary consistent with both from the start
  rather than waiting for the ADR text to catch up first.
- Reported once to the Lead.

### [AIQ · 2026-08-04] 4th ADR-0001 R2 item — UNMEASURED verdict for thin-trigger components, agreed + floor proposed
- AI/ML's direct message raised a methodological point on Leg A I hadn't caught in my own audit: binary
  pattern-trigger components (bull-flag, ABCD, etc.) may fire too rarely across the backtest window for
  **any** CV scheme to produce a meaningful verdict, regardless of leakage discipline. Proposed a third
  verdict state — **UNMEASURED** (insufficient trigger count) — distinct from **NOT CLEARED** (tested,
  failed the bar). Same principle as the float study's "no data behind it" vs. an actually-tested null.
- **Agreed, and it should have been in my own methodology draft from the start** — a component graded
  NOT CLEARED on 6 trigger events would be a false statement about what was actually tested.
- **Pre-registered a concrete floor before either of us has real trigger counts (LL-44):** minimum 30
  trigger events before a component enters CV at all. Anchored to precedent, not invented fresh — the
  ratified D-TRADE-021 bar already assumes n≥30 is where fold-membership randomness can start to dominate
  a component's apparent performance (that's the statistical basis of its own ≥30-seed requirement); reusing
  the same number avoids two uncoordinated statistical-power assumptions in the same pipeline.
- **Recommendation only**, same path as D-TRADE-021 itself — needs Lead/Director ratification before it
  binds, not self-declared by either builder or auditor seat. Flagged to the Lead as a 4th tracked item
  alongside the 3 ADR-0001 objections, not a surprise discovered later. My own `methodology-draft.md` §4
  verdict format will need a fourth state added once this ratifies — not editing it pre-emptively.
- Converged with AI/ML directly (protocol 11) on both this and finding #3's nested-CV resolution in one
  reply. Still NOT co-signing ADR-0001 R2 — 4 open items now, not 3, all additive/fixable.

### [AI/ML · 2026-08-04] Minimum-trigger-count floor (UNMEASURED verdict) — converged with AIQ, needs ratification
- AIQ confirmed nested CV for NN-10 (crossed-message duplicate of the earlier convergence, no new content)
  and, separately, refined my earlier minimum-trigger-count proposal (§ above) into a concrete number: **30
  trigger events**, anchored to the same n≥30 assumption already baked into D-TRADE-021's seed requirement
  — one statistical-power assumption instead of two uncoordinated ones. Below 30 → verdict **UNMEASURED**,
  no partial credit either direction (matches the existing CLEARED/NOT CLEARED/VOID "no partial credit"
  philosophy). Agreed — this is a better-grounded number than I had, and I hadn't picked one yet.
- **Not self-ruled by either of us** — same path D-TRADE-021 took: a recommendation for Lead/Director
  ratification (P-4-style), pre-registered now (LL-44) before either of us has real trigger counts from an
  actual run to be tempted by. Flagging here so it's tracked alongside the other open ADR-0001 R2 items,
  not surfaced later as an unpinned assumption.
- Reported once to the Lead.

### [AIQ · 2026-08-04] ADR-0001 R2 — full builder/auditor convergence closed, awaiting Architect's revision
- AI/ML engaged substantively with all 4 findings (not a rubber-stamp acknowledgment) across 3 follow-up
  messages: confirmed nested CV for grid-selection (finding #3); independently proposed the correct fix
  for the Leg-B baseline `N` (finding #2) — train-fold-derived `N` per outer fold, with OP-3's existing
  "fixed N sensitivity" clause repositioned as the leakage-free complement rather than a separate ask, a
  cleaner resolution than what I'd proposed; agreed the import-boundary gap (finding #1) is real and
  committed to building `helm/screener` as a genuinely thin adapter so the question of importing it never
  comes up; confirmed the UNMEASURED floor at 30 as a better-grounded number than their own unstated one.
  All 4 items now have a converged, cited, additive fix — sent to the Architect by AI/ML and by me.
- **No self-certification risk here** — convergence is BEFORE either lane writes code (matches the
  D-TRADE-021 pattern), and the actual co-sign still requires the Architect to fold the fixes into the ADR
  text and me to review that text, not just the two builder/auditor seats agreeing with each other in chat.
  Builder≠judge stays intact: AI/ML proposing a fix I evaluate and either accept or contest is not AI/ML
  certifying its own work — the ADR still needs my sign-off on the actual revised text.
- **Status: still NOT co-signed.** Waiting on the Architect's R3 (or an addendum) before either confirming
  the fixes landed as agreed or raising anything new the written revision surfaces. Reported to the Lead.
  Nothing to audit yet regardless — no code exists.

### [Architect · 2026-08-04] ADR-0001 R2 — folded in AI/ML's 3 co-sign points + Lead's unseated-Data-Eng catch
AI/ML co-signed Leg A + trailing-stop mechanics, raised 3 load-bearing precisions before locking Leg B/NN-10
(exactly the pre-build convergence discipline). All 3 accepted into the ADR (I author the contract):
- **§6.3 effective-stop FORMULA now explicit:** `effective_stop(t) = max(P0*(1-init_stop_pct/100),
  peak(t)*(1-trail_pct/100))` — monotonically non-decreasing **by construction** (max of a constant floor
  and a non-decreasing term), loss bounded at `init_stop_pct`, trail takes over automatically. Removes the
  "governs until" ambiguity; a silently-retreating stop would be an NN-1 defect.
- **§6.3 fixed target resolved:** in trail mode `target_price` is UNUSED — exits are trail-hit or EOD only
  (the point of a trailing exit). Was a real behavioral fork the ADR had left silent.
- **UNMEASURED = a 4th verdict state (§6.1/§6.2):** a component firing below a pre-registered minimum-support
  floor is UNMEASURED, never silently NOT-CLEARED (absence ≠ judgment — the float "no data" precedent);
  `_gates` stays False for lack of evidence, not a failed test. Rule fixed now; the count = OP-5 (set on real
  data, pre-registered). Verdict enum → {cleared,dropped,void,unmeasured} + a `support_count` field.
- **Lead's catch — Data-Eng is UNSEATED:** reconciled the ADR's Data-Eng references — P-3 goes to the
  Director (Lead is routing it); NN-5/§4/§5/§12 note residual cohort duty falls to SDE1 if the universe lane
  is kept, and vanishes if it drops (recommended). No design stuck on a nonexistent seat.
- These are the co-sign loop working as designed. Pushed. Still PROPOSED; AIQ co-sign (label/NN-10/baseline)
  still the outstanding load-bearing gate before canonical absorption.
- **Also folded AI/ML's nested-CV reading of NN-10 into §6.4** (from its AIQ note, seen on this rebase): if
  the analysis ever SELECTS a grid point, selection goes through **nested CV** (pick on inner/train folds,
  score on the held-out outer fold, aggregate OOS) — never best-on-full-sample. Recorded as the recommended
  procedure **pending the AI/ML↔AIQ confirm** (not locked unilaterally — they're mid-convergence, same as
  the D-TRADE-021 pattern). Gives them a concrete target without pre-empting.

### [Architect · 2026-08-04] ADR-0001 R2 — AIQ's 3 audit objections ALL addressed (co-sign amendments)
AIQ's load-bearing audit correctly withheld co-sign on 3 cited methodology gaps. All 3 folded into the ADR
as additive amendments (AIQ's own framing: additive, not a redesign — the two-leg structure/harness/gate
mechanism stand):
- **#1 builder≠judge hole at the feature layer → FIXED.** The import boundary + NN-3 now bar Lane D (AIQ
  audit) from importing **`helm/screener`** outputs (not just `engine`) — AIQ **re-derives features from the
  raw `tools/rolling_watchlist.py` primitives itself**, so a lookahead/alignment bug in the AI/ML-owned
  adapter can't be silently inherited by both engine and audit. This was a real independence gap; good catch.
- **#2 NN-10 too narrow → BROADENED.** The Leg-B baseline `N` (median trailing holding period) is the same
  data-derived-parameter leakage class as `trail_pct` — and worse, a test-fold-derived N is not independent
  of the arm it's compared against (winners ride longer). NN-10 + §6.4 + OP-3 now bind **N and every
  data-derived label/baseline param** to train-fold-only. Fully pre-registered fixed N noted as the simplest
  leakage-free option.
- **#3 grid cherry-pick → BARRED.** OP-1 + R-2 now require **one pre-registered primary grid cell
  (clearance-eligible); the rest are sensitivity-only**, never a clearance claim. Kills "test 6, report
  whichever clears." Nested-CV (AI/ML's mechanism) remains the alternative if selection is ever used.
- §14 + the status line record the amendments. **AIQ re-review is the outstanding load-bearing gate** before
  canonical absorption; reporting to the Lead + replying to AIQ (AI/ML copied) that all 3 are addressed.

### [Architect · 2026-08-04] OP-5 support-floor value pinned from the AI/ML↔AIQ convergence (≥30 triggers)
Seen on this rebase: AI/ML + AIQ converged on the UNMEASURED support-floor **value** I'd left TBD at OP-5 —
**≥30 trigger events**, anchored to D-TRADE-021's own n≥30 seed basis (one statistical-power assumption in
the pipeline, not two uncoordinated ones). Folded into OP-5 as the recommended value, **pending Lead/Director
ratification** (same path as D-TRADE-021 — pre-registered before any real trigger count exists, LL-44; not
self-ruled). Both seats confirm my 3 fixes (#1 import-boundary, #2 N train-fold-only, #3 grid primary-cell)
match what they asked for; AI/ML will co-sign Leg B + NN-10 on these landing. Reporting to Lead; replying to
both seats.

### [Architect · 2026-08-04] ADR-0001 R2 — OP-5 floor cite updated to D-TRADE-029 (ratified, =30)
Lead ratified the 30-event UNMEASURED floor as **D-TRADE-029** (crossed with my OP-5 edit, which still read
"recommend ≥30, pending"). Per the Lead's request, updated OP-5 · §6.2 · the verdict-state line · P-4 · §14
to cite **D-TRADE-029, floor ratified at 30** (no longer "pending"). Text-only, no design change. P-4's open
list now = OP-1..3 label params only (OP-5 closed). Pushed. AIQ's re-review of the R2 text remains the one
outstanding co-sign gate before canonical absorption.

### [AIQ · 2026-08-04] ADR-0001 R2 — CO-SIGNED. Re-reviewed the actual text, not the summary, per own discipline
- **Re-read the full revised ADR** (not the Architect's summary message) before deciding — the same
  standard I hold AI/ML to (LL-34, never audit from a report). Verified each of the 4 fixes against the
  actual mechanism, not just that a paragraph exists:
  1. **Import boundary (§4 lines 84-89, NN-3 line 190):** confirmed — Lane D now explicitly barred from
     `helm/screener` outputs too, with a real, mechanically-checkable negative control (a static
     import-boundary lint DevOps can actually enforce, not just a written promise). **Resolved.**
  2. **NN-10 broadened to `N` (§6.4 lines 156-168, NN-10 row line 197, OP-3 lines 228-231):** confirmed —
     exact language matches the AI/ML↔me convergence (train-fold-derived `N` per outer fold). **Resolved.**
     Minor implementation note, not a design gap: the negative control ("compute N from test-fold trades
     → RED") needs a concrete mechanical check when I build the audit script — I'll assert per-fold trade-ID
     disjointness between the set that computes `N` and the set scored against it. Mine to build correctly,
     not a hole in the ADR.
  3. **Grid cherry-pick barred (OP-1 lines 219-225, R-2 line 248):** confirmed, and the Architect's default
     (single pre-registered primary cell, no post-hoc selection at all) is cleaner than the nested-CV
     fallback AI/ML and I had converged on — avoids the selection question entirely rather than doing it
     safely. Nested CV kept as a named alternative if selection is ever used. **Resolved, improved.**
  4. **UNMEASURED + floor (§6.1 line 104-107, §6.2 lines 126-133, OP-5 lines 235-239):** the rule and the
     4th verdict state (with `support_count` recorded) are correctly landed. **One flag, not blocking:**
     D-TRADE-029 already ratified the floor at 30 (commit `b404f2b`, strictly before this ADR revision
     `14735b7`) but OP-5/§6.2/P-4's text still reads "TBD"/"pending" — the ADR hasn't caught up to its own
     governing decisions-log record (protocol 16: the governing artifact wins on disagreement). A stale-text
     gap, not a design defect — flagged back to the Architect as a quick find-replace, doesn't block co-sign
     since the substance (rule + state + precedent-anchored number) is already correct and already ratified
     elsewhere.
- **CO-SIGNING.** All 4 objections are structurally and verifiably resolved in the actual ADR text. The
  two-leg structure, harness reuse, and gate-flag mechanism remain untouched, exactly as promised (additive,
  not a redesign). Builder≠judge held throughout: convergence happened in chat before code existed, but the
  sign-off is on the text I just re-read, not on the chat agreement.
- **Absorbed into `docs/eval/methodology-draft.md`** (my write-lane): §0 updated from `▸ NOT DECIDED` to the
  ratified two-leg contract; §1 made explicit that "raw" excludes `helm/screener`; §3 gained two new steps
  (support-floor check, parameter-isolation check); §4's verdict format now matches ADR-0001's canonical
  4-state schema exactly (`CLEARED`/`DROPPED`/`VOID`/`UNMEASURED` — renamed my old "NOT CLEARED" to
  "DROPPED" for consistency with the schema I don't own); §5/§6 updated to reflect co-sign + remaining
  open params (OP-1/2/3, still pending; OP-5 alone is ratified).
- Reported to the Lead, Architect, AI/ML. Still nothing to audit — no code exists. Holding for P-1 (build
  re-scope) and the remaining P-4 ratifications (OP-1/2/3) before any real run.
- **Addendum, same rebase:** the Architect's OP-5 stale-text fix (entry above) landed concurrently with
  this review and already closes the one flag I raised — crossed in flight, not a case of my flag going
  unaddressed. Nothing further needed on it.

### [AI/ML · 2026-08-04] ADR-0001 co-sign complete — verified at source, not just AIQ's confirm
- Pulled the pushed text (`d75b252`) and read every section relevant to my co-sign directly, rather than
  taking AIQ's "all 4 items verified" at their word. Checked each against what I'd actually asked for:
  §6.3's explicit `effective_stop(t) = max(P0*(1-init_stop_pct/100), peak(t)*(1-trail_pct/100))` formula
  (monotone-by-construction, resolves the NN-1 concern precisely) · trail mode disabling the fixed target
  · §6.4/NN-10 broadened to cover Leg-B's `N` via the exact nested-CV procedure AIQ and I converged on ·
  NN-3 + the import boundary explicitly barring `helm/validation/audit` from `helm/screener` outputs
  (AIQ's finding #1) · OP-5 = 30 (D-TRADE-029), correctly marked resolved. All confirmed accurate.
- **One pleasant surprise, not something I'd asked for:** OP-1's resolution (one pre-registered primary
  grid cell is clearance-eligible, the rest sensitivity-only) is a cleaner fix for the grid-cherry-pick
  problem than the nested-CV grid-selection AIQ and I had converged on — simpler, still leakage-free, and
  the Architect kept nested-CV as an explicit fallback rather than discarding our convergence outright.
- **Formally co-signed: Leg B + the trailing-stop mechanics + NN-10** (Leg A + trailing-stop mechanics were
  already co-signed earlier). AI/ML's full co-sign on ADR-0001 R2's validation-engine + trailing-stop
  portions is now complete. Nothing further needed from this seat on the design — ready to build the
  moment P-1 clears (still Director-pending, unchanged by any of this review).
- Reported once to the Lead.

### [AI/ML · 2026-08-04] D-TRADE-031 delivered — min_float guardrail param + float-distribution script
- **Ground-checked the reference implementation before building against it, not just the Lead's paraphrase.**
  The Lead's message cited `day_trade_toolkit.py:61-67` with `min_float` — the copy already in `Downloads/
  files (6).zip` (found during the earlier D-TRADE-023 screener search) does NOT have `min_float` at all;
  that was a stale, unrelated exploratory file sharing a filename by coincidence. Found the actual current
  ZIP (`Downloads/files 8.zip`, dated 2026-08-04, same day as this dispatch) containing `day_trade_toolkit.py`
  + `premarket_scan.py` + `analyze_float_distribution.py` matching the Lead's citation exactly. Building
  against a wrong same-named file would have repeated the exact mistake LL-45 exists to prevent — checked
  first.
- **`tools/rolling_watchlist.py`'s `scan_guardrail_criteria()`:** added `min_float: float = 1_000_000`,
  mirroring the reference's default and range-check pattern (`min_float <= float_shares <= max_float`).
  **Deliberately did NOT copy the reference's `require_float_data` behavior** (drops a candidate outright
  when float data is missing) — this scanner never gates on missing data anywhere (`float_gates` defaults
  False repo-wide); copying that semantic would silently break every real call site, since `float_shares`
  is never actually populated in this repo. `float_ok` stays `None`/unmeasured absent real data, unchanged
  from before — min_float only ever fires when `float_gates=True` AND a real value is supplied, same
  posture as `max_float` always had.
- **Caveat carried into the docstring itself, per the Lead's explicit instruction, with real citations:**
  cited both float-study findings by reading the source docs directly — Massive `/stocks/vX/float`
  (current-only, 77.6% coverage, `SHORT_INTEREST_STUDY_FINDINGS.md` Phase 1 discovery) and SEC-API.io
  (outstandingShares 36.5% / publicFloat 83.2% unusable point-in-time, `FLOAT_STUDY_PHASE1_FINDINGS.md`
  §4, NO-GO on both). Explicit in the docstring: adding `min_float` doesn't reopen or contradict either
  finding — it's dead code absent real float data either way.
- **`tools/analyze_float_distribution.py`** (new file, sibling to the scanner): adapted the reference's
  bucket/outcome-report logic, but deliberately decoupled from its assumed `premarket_scan_log.csv` producer
  — that pipeline (`premarket_scan.py`) doesn't exist in this repo, and D-TRADE-023's `/api/scan` is
  stateless (no persistence layer anywhere yet). Reads any CSV with `ticker`/`float_shares` (+ optional
  `result_pct`/`taken`) columns from any source. Same small-sample caution as the reference, additionally
  anchored to this repo's own D-TRADE-029 (n<30 = too thin to trust) rather than a generic warning.
- **Verified, not just written:** a 5-case unit test on the new `min_float` logic (default-off · in-range ·
  below-min · above-max · custom `min_float`) — all pass. Re-ran DevOps's `scripts/smoke_rolling_watchlist_web.py`
  against the live app — still passes, no regression to the shared-file contract (ADR-0001 §7). Tested the
  distribution script against synthetic fixtures in all 3 states (no-outcomes / with-outcomes / missing-file).
- `adr_reference: D-TRADE-031` (dispatch) `+ ADR-0001 §7` (shared-file citation, `tools/rolling_watchlist.py`
  is a shared library per `<3.5>`).
- Reported once to the Lead.

### [SecOps · 2026-08-30] P-5 Step 2 review complete for all six secrets — co-signed Step 3
- Dispatched by the Lead via a peer-session cross-message (open-items-ledger item 13); verified my own
  identity + the assignment before acting rather than taking it on faith — checked `ListAgents` (exactly
  one peer session, matched the sender), re-read item 13, re-confirmed my oracle-boundary row unchanged.
- Ran Step 2 for S1–S6 in `docs/security/b5-secret-approval-checklist.md`: classification+blast-radius,
  least-privilege-at-generation, ToS-tier match, storage, rotation policy — each documented with evidence
  (re-verified `.gitignore`/`git ls-files` myself, didn't trust the prior "verified" note). Notable: S1/S2
  have no finer-grained credential to request at generation (Supabase design limit, not a hygiene gap) —
  named this explicitly rather than checking a box that implies more precision was available. S6's rotation
  (item 11) has one honestly-flagged residual — the old exposed token's dashboard-side invalidation was
  never independently re-confirmed (only the new value's liveness was) — not a live risk (the only exposure
  site is deleted) but surfaced per protocol 15/16, not smoothed over.
- **Fail-closed/loud and post-install-leg-K criteria marked NOT-YET-VERIFIABLE, not checked off** — no
  ingestion code exists yet to test fail-closed behavior against, and leg K re-run was explicitly out of
  scope (blocked on DevOps's harness build). Refused to attest to either without evidence.
- **Checked my SecOps co-sign in Step 3 for all six** — this is my own duty per the checklist's own rule
  (PROFILE: co-signs B5, Lead may not self-approve), not something to punt back up. No blocking finding;
  residual recommendations (proactive rotation cadence for S1/S2 CRITICAL pair, one-key confirmation for
  S5, old-token dashboard re-check for S6) noted but don't gate the co-sign. **Installed** and **Leg K
  re-run GREEN** columns left genuinely open — did not check either, both still block full P-5 closure.
- Reported once to the Lead (protocol 15), consolidated, not per-secret. No blocker hit.

### [SecOps · 2026-08-30] S5 co-sign re-confirmed after the command-bar exposure surfaced
- A peer Lead session (identity mismatch resolved first — corrected an initial DevOps misdirection, then
  the same peer relayed new information after my prior message) reported: the Massive key was pasted into
  a command bar on first use, flagged by the Director's partner, rotated afterward. Pulled latest, read
  the Lead's own independently-checked findings (template git history clean, real key gitignored/never
  committed, current key live HTTP 200) and the open-items-ledger #14 closure before responding — did not
  take the report on faith alone, verified what was already checkable in the repo state.
- **Re-confirmed the S5 co-sign stands**, updated (not retracted): classification/least-privilege/
  ToS-tier-match are unaffected by a use-time handling mistake; Storage and Rotation-policy columns
  updated with the new information, same treatment already given S6's own exposure.
- **New finding of my own, not just relaying the Lead's:** my original Storage review only checked
  repo/git-level persistence (`.gitignore`, `git ls-files`) — a command-bar paste is a different vector
  (shell/terminal history) I hadn't covered. Added a recommendation to check/clear PowerShell
  `ConsoleHost_history.txt` / bash `.bash_history` / any Claude Code transcript where the value might have
  been echoed — matching the same class of check that found `log_pull.txt` for S6. Flagged as open, not
  claimed as done — I can't do this myself (the incident's location isn't identified in what reached me).
- **Named a tension, didn't adjudicate it:** the Director's own chat approval (already in this file) states
  *"none has been exposed in the command bar or anywhere insecure"* — in apparent tension with this
  incident. Surfaced per protocol 16 (governing artifact vs. statement disagreement) for the Lead/Director
  to reconcile; not a SecOps call to resolve.
- Also distinguished evidentiary strength honestly: S6 had a persistent artifact (`log_pull.txt`) checkable
  before/after rotation; S5's rotation is Director-attested only, no independently-checkable before/after.
  Treated as sufficient for co-sign (same standard the Director's own approval already relies on) but kept
  visibly distinct from "independently verified," not blended together.
- Reported once to the Lead (protocol 15). No blocker.

### [DevOps · 2026-08-30] Leg K scaffold built + armed; six-secret artifact-check (item 13, closes 4/6)
- Assignment dispatched via a peer session's raw message (not the ccd_session_mgmt channel this project
  otherwise uses) — verified against the repo before acting (`5675c4a`/`d9690c7`/`338e81e`,
  open-items-ledger item 13) rather than trusting the message alone; confirmed genuine, replied to the
  peer confirming DevOps identity. Large gap since my last sync: `<1.1>` dropped options entirely
  (D-TRADE-028), P-1/P-3/P-4 ratified and build-GO issued (D-TRADE-034/035/036) — pulled and read all of
  it before touching anything.
- **Built `scripts/gate/run.py` + `scripts/gate/legs/secret_scan.py`** — leg K wired verbatim against
  SecOps's key-denylist.md (K0-K6), the rest of the leg table declared SKIP-visible (not silently
  omitted) so the runner already states its own eventual shape. **Self-reference bug caught and fixed
  during build:** an early design used a value-based allowlist ("exempt any string that also appears in
  key-denylist.md") to keep that spec's own documented FAKE examples from self-triggering — this
  backfired by also exempting my self-test's positive controls, which correctly reuse those same
  documented values as the planted negative controls SecOps's spec instructs DevOps to plant. Fixed by
  scoping the exemption to ONE path (key-denylist.md itself), not a value-based allowlist — narrower,
  avoids the collision, and doesn't create a blind spot for a real secret elsewhere that happens to share
  a demo value. **Second bug caught live against the real repo:** K0b's generic backstop tripped on
  `docs/AGENT-COORDINATION.md` prose ("secrets: classification/blast-radius/...") because "secrets"
  contains "SECRET" case-insensitively — tightened the name-side match to SCREAMING_SNAKE_CASE-only
  (matches every real example in key-denylist.md), which fixed the false positive without weakening
  real-assignment detection.
- **Verified the full LL-48 done-bar, not just the isolated self-test:** self-test PASSED (all 10 K0-K6
  positive controls go RED, all 4 documented placeholders/env-indirection stay GREEN, key-denylist.md's
  own examples don't self-trip); real scan against the actual tracked repo is GREEN; then staged (never
  committed) a genuine K5-shaped violation, confirmed the top-level runner goes RED end-to-end through
  the real `git ls-files` path (not just the in-memory self-test), unstaged + deleted it, confirmed GREEN
  again — no trace left, nothing ever touched git history.
- **Six-secret artifact/location check (presence only, values never read/printed/logged) across all 9
  live clones + env vars at User/Machine/Process scope:** S3 (MCP PAT) FOUND — a persistent User env var,
  nothing outstanding against it. S5 (Massive) FOUND present — a persistent User env var, also redundantly
  a real file in `Trade - Lead` only — **but this artifact-check ran before rebasing onto SecOps's
  same-day S5 REOPENING** (an unresolved transcript-history candidate, see SecOps's entry directly above)
  and I do not treat "present" as "closed" for S5 now that I've read it: presence answers a different
  question (is a key installed where the code would read it) than the reopened one (is *that specific
  value* the safe, non-exposed one) — my check cannot speak to the latter at all, and I'm not conflating
  the two in the checklist update below. S1/S2/S4 (Supabase service_role/DB-password/anon) **NOT FOUND
  anywhere** — no `.env` exists in any of the 9 clones, no env var set at any scope. S6 (SEC-API.io) FOUND
  but in the wrong project — the real key lives only in the separate standalone `Trade/` repo, nothing in
  `Trading Project 1` reads it (no `helm/ingest/` yet), and no env var is set here either; flagged as an
  open scope question for the Lead/Director (install fresh here vs. a deliberate cross-project
  dependency), not something I resolved unilaterally. Recorded in `docs/security/b5-secret-approval-
  checklist.md` Step 3 — leg K re-run GREEN for all six; S3 marked cleanly Installed; S5 marked present
  but explicitly flagged against the reopened exposure question, not presented as closed; S1/S2/S4 left
  honestly unchecked; S6 marked found-wrong-scope rather than either checked or silently ignored.
- Reported once to the Lead (protocol 15) — leg K armed + all six secrets' precise state, not a blanket
  "P-5 closed" claim, and explicitly not overriding SecOps's S5 reopening with a stale "found = fine"
  read. No blocker; the S6 scope question and the S5 tension are flags for the Director, not a stall on
  my end.

### [DevOps · 2026-08-30] Post-push catch: leg K self-triggered on its own tracked fixtures
- Re-ran leg K immediately after pushing `0fedd75` (habit, not required) — caught it going RED against
  its own file: once `secret_scan.py` was tracked, its own `POSITIVE_CONTROLS` literals matched its own
  patterns (15 findings). Same self-reference class as key-denylist.md, but a path-based exemption here
  would blind leg K to a real secret accidentally pasted into its own source later — a worse blind spot
  than exempting a spec doc. Fixed by storing each fixture base64-encoded, decoded only at self-test
  runtime — no exemption, no blind spot, same decoded values, self-test still PASSES. Re-verified
  end-to-end (live plant/revert) before pushing the fix (`b028207`).
- Reported once to the Lead, folded into the same completion report as item 13 rather than a second ping.

### [AIQ · 2026-08-31] Caught up after ~26-day gap — prior "holding for P-1" status was STALE
- **External flag, not self-caught.** Whoever's watching this session directly saw its own status text
  ("still holding for P-1") and correctly called out that it conflicted with the repo's logged state —
  D-TRADE-034 lifted P-1 for Phase-1 build on 2026-08-30, before this session last spoke. `git pull
  --rebase` (clean, large fast-forward — dozens of commits since my last check) + full re-read:
  AGENT-COORDINATION.md (board banner + build-chain spec), decisions-log.md through D-TRADE-036,
  ADR-0001's current state, my own board row.
- **Confirmed accurate now:** P-1 (D-TRADE-034), P-3 (D-TRADE-035), P-4 (D-TRADE-036) all ratified
  2026-08-30 — real build-GO, not design-only. Director dispatched a 4-stage build chain: AI/ML (Stage 1,
  Leg A/B build) → **AIQ (Stage 2, me — independent audit)** → QA (Stage 3, reproducibility re-run) →
  DevOps (Stage 4, arm remaining gate legs), with **staged reporting at each handoff**, an explicit
  Director override of the usual protocol-15 batched-report default for this chain.
- **Substance check, not just a label change:** verified `helm/` does not exist in-repo (`find helm -type
  f` → nothing) — AI/ML's own board row confirms Stage 1 hasn't delivered (idle). So the actual audit
  queue position is unchanged (still nothing to audit); only the *reason* changes — correctly "queued
  behind AI/ML's Stage 1," never "P-1 blocking." Getting this distinction right matters for anyone reading
  status externally, which is exactly what surfaced the staleness in the first place.
- **P-4's locked values (D-TRADE-036), sanity-checked on catch-up, not re-litigated:** OP-1 grid + primary
  cell, OP-2 horizons, OP-3's fixed N=5 — read against my own methodology. No objection: OP-3 in
  particular chose the **leakage-free fixed-N path**, not the train-fold-derived-median option, which
  sidesteps my original audit finding #2 entirely. Noting for the record (not re-opening) that these 3
  were an explicit, disclosed Director/Lead shortcut of ADR-0001 §12's AIQ-cosign expectation — my
  after-the-fact read finds no defect, but it wasn't an independent gate the way D-TRADE-021/029 were.
- **QA not spawned (blocks Stage 3)** — already tracked as open-items-ledger item 17 by the Lead; not
  re-flagging as new, just confirmed I've seen it and it's not something I can or should act on myself.
- Corrected `docs/eval/methodology-draft.md` (my write-lane) to match: P-4 section, HUMAN-boundary
  section, and §6 status all updated; added a dated catch-up note rather than silently rewriting history
  (matches the file's existing pattern of append-dated banners, not edited-in-place claims).
- **Lesson for myself, recorded plainly:** I'd been re-reading before every repo *write*, per
  dispatch-freshness, but let a chat *status reply* go stale across a long gap without the same check.
  The discipline needs to cover what I say out loud, not just what I commit.
- Reporting to the Lead now.

### [AI/ML · 2026-08-31] Resumed after ~27-day gap, caught up honestly, then delivered Stage 1
- **External flag, same pattern as AIQ's entry above.** A peer session (Lead, different messaging fabric
  than `ccd_session_mgmt`) asked me to confirm identity before treating anything as authorized. Did NOT
  take the message as sufficient grounding — pulled clean and independently verified D-TRADE-034 (P-1
  lifted, Phase-1 scope), D-TRADE-035 (`helm/universe` drops), D-TRADE-036 (P-4 locked: trail∈{5,8,12}%,
  init∈{2,3}%, primary=trail8/init3; Leg-B baseline N=5 days, fixed not train-fold-derived) all at source
  before starting anything.
- **🔴 Found unexplained uncommitted WIP in my own working directory before touching anything:** a
  `lookup_edgar_catalyst()` addition wired into the LIVE `tools/rolling_watchlist.py` (sys.path/EdgarClient
  import), plus empty `modeling/diagnostics/*.py` stubs and `tools/backfill_forward_returns.py`. Traced
  against D-TRADE-032 (2026-08-14, bars new Guardrail-v2.1-style scanner signals from any dispatch without
  explicit Director authorization + AIQ validation) — the only separately-authorized touch from that
  episode was a narrow EDGAR-mirror plumbing fix (`382c514`), verified to touch exclusively
  `docs/guardrail-v2.1/{README.md,code/edgar_mirror.py}`, never the live scanner (confirmed: the current
  committed `tools/rolling_watchlist.py` has zero EDGAR references). This stash isn't that fix — no
  D-TRADE number, no working-log entry, unlogged. **Stashed it safely (`git stash -u`), not discarded, not
  built on, not folded into Stage 1.** The Lead independently corroborated (same WIP, carried since session
  start, already escalating to the Director as its own tracked item) — two independent sessions hitting the
  identical unexplained content in the same clone.
- **Stage 1 delivered on a clean base**, pushed → origin/main (`006db52`, `f8f685e`):
  1. **Trailing-stop exit mode** in `simulate_day_trades()` — backward-compatible opt-in
     (`trail_pct`/`init_stop_pct` both `None` = today's fixed behavior, byte-identical). §6.3's
     `effective_stop(t) = max(P0*(1-init_stop_pct/100), peak(t)*(1-trail_pct/100))` formula implemented
     exactly, monotonic by construction, bar-causal `peak(t)` (NN-1). Fixed target unused in trail mode.
     Verified: backward-compat, the ValueError guard, exact numerical verification of the ratchet on a
     rise-then-drop fixture, a never-rising trade correctly bounded at the init hard stop.
  2. **`helm/screener/adapter.py`** — thin adapter over the scanner, OP-4's final Leg-A component list (8
     pattern detectors + pivot/red-to-green trigger), deliberately excluding the already-validated
     guardrail/S3/short-interest/catalyst factors. Verified against synthetic intraday data.
  3. **`helm/validation/engine/`** — the CV harness (`evaluate_loo`/`evaluate_multiseed_kfold`, proven
     template reused verbatim), the D-TRADE-021/029 clearance bar, Leg A orchestration, and Leg B
     orchestration against D-TRADE-036's locked primary cell + sensitivity grid. **Leg B required a genuine
     methodology judgment call** (no fitted model exists once trail/init/N are fixed constants, not
     train-fold-derived) — documented explicitly in the module docstring for AIQ's independent judgment
     rather than silently baked in, per protocol 17. Verified end-to-end with PLANTED effects (a real
     signal correctly CLEARS, pure noise correctly NOT_CLEARS even when a single LOO draw beats naive by
     chance — the exact failure mode the ≥90%-seed bar exists to catch, mirroring the catalyst study's own
     documented near-miss), a thin-support component correctly reads UNMEASURED not NOT_CLEARED, and a
     sensitivity-grid cell with a real planted edge is correctly downgraded rather than silently CLEARED.
  4. Re-ran DevOps's `scripts/smoke_rolling_watchlist_web.py` after each shared-file change — no regression.
- **What Stage 1 does NOT include, stated plainly, not silently under the rug:** wiring Leg-A verdicts back
  into `_gates` flags on the live scanner (no such flags exist yet for these components — a separate, later
  step) and an actual real-market-data backtest run (no cohort/ingest pipeline exists yet; this is the
  reusable, verified ENGINE code per the Stage-1 dispatch's own framing — "build the logic" — not the run
  itself, which needs data assembly outside this build's stated scope).
- Reported to the Lead (staged reporting per the Director's explicit dispatch, not held for a final
  summary) at each milestone: identity + verification, the WIP finding, and now Stage 1 complete.

### [AIQ · 2026-08-31] STAGE 2 — independent audit of AI/ML's Stage-1 delivery. 6/6 own tests run, 4 findings
- **Read the delivered code in full** (trailing-stop diff in `tools/rolling_watchlist.py`,
  `helm/screener/adapter.py`, `helm/validation/engine/{bar,harness,leg_a,leg_b}.py`) before writing a
  single line of my own — same discipline as the ADR-0001 review (LL-34, never audit from a summary).
  Confirmed via `find helm -type f`: Stage 1 delivered LOGIC, not a real-data run — no `helm/ingest/`, no
  historical data pulled (the Lead's own sanity-check was synthetic too). No actual CLEARED/DROPPED
  verdict exists to reproduce yet; this audit covers the mechanism.
- **Wrote and ran my own independent audit script** (`helm/validation/audit/stage2_audit.py`, my write-lane
  per ADR-0001 Lane D) — calls `tools/rolling_watchlist.py`'s raw primitives directly, never imports
  `helm/screener` or `helm/validation/engine` (NN-3). 6 tests, own fixtures throughout (different numbers
  from AI/ML's or the Lead's own tests, a genuinely separate check):
  1–4. Trailing-stop ratchet, init-floor bound, no-lookahead (truncation test), backward-compat — all
  **independently confirmed correct** against hand-computed values (caught and fixed 2 arithmetic errors
  in my OWN first-draft fixtures before trusting a false "FAIL" — verify-don't-attest applies to my own
  work too, not just AI/ML's).
  5. My own from-scratch LOO+5-fold×30-seed reimplementation (not importing `harness.py`) correctly
  separates a planted signal (100% seed agreement) from pure noise (0%) — validates the ALGORITHM is
  soundly implementable; not a claim their literal code reproduces (QA's Stage-3 job).
  6. Independently verified (calling `scan_all_patterns`/`analyze_intraday_alignment` directly) that all 9
  of `helm/screener/adapter.py`'s claimed Leg-A components are real scanner output columns, not invented.
- **4 findings, all fixable, none invalidate the core mechanism:**
  **#1 (empirically confirmed, not theoretical)** — `leg_b.py`'s `_loo_paired` outlier-robustness statistic
  (mean of n leave-one-out estimates) fails to flag a single-trade-driven result on a constructed fixture:
  the one leave-one-out estimate that actually excludes a planted outlier correctly reads negative, but
  the reported MEAN of all 35 estimates stays positive — averaging nearly always preserves the full-sample
  sign since each estimate only removes 1/n of one trade's influence. Recommend reporting the sign-flip
  count instead of/alongside the mean.
  **#2** — Leg B's translated bar tests in-sample stability (does the effect survive resampling of
  already-known data), not out-of-sample generalization like Leg A's real held-out prediction — a
  legitimate adaptation given D-TRADE-036 fixed the parameters (nothing to fit, nothing to hold out), but
  the verdict record uses identical field names/labels as Leg A with no disclosure of the distinction —
  an LL-40 violation (accuracy and consistency claims must be stated separately, never blended).
  **#3** — `bar.py` returns `"NOT_CLEARED"`; the ratified schema (ADR-0001 §6.1, confirmed by direct
  grep, not memory) is `verdict∈{cleared,dropped,void,unmeasured}` — should be `"DROPPED"`.
  **#4** — `leg_b.py` introduces an undocumented 5th verdict string, `SENSITIVITY_ONLY_WOULD_CLEAR`
  (intent correct — OP-1's anti-cherry-pick — but outside the ratified 4-state enum; recommend a separate
  `is_primary` boolean instead of a new verdict string).
- **Direct answer to AI/ML's explicit methodology question:** the paired-comparison translation for Leg B
  is sound in its core logic given the real no-fitted-model constraint — not a fabricated shortcut. The
  defect is in execution (findings #1/#2), not the method's existence. Does not block Stage 1 from being
  considered structurally sound; recommend #1–4 land before/alongside the first real data run.
- Full findings: `docs/eval/stage2-audit-findings.md`. Lane discipline: found issues in AI/ML's
  `helm/validation/engine/` (their write-lane) — reported, not self-fixed, same as the ADR-0001 review.
- Reporting to the Lead now (staged reporting, Director's explicit override) — this is the Stage-2
  completion report.

### [AI/ML · 2026-08-31] All 4 Stage-2 audit findings fixed, verified against AIQ's own fixture
- Read `docs/eval/stage2-audit-findings.md` in full (not just AIQ's message summary) before fixing anything
  — confirmed each finding at source, including the exact `bar.py`/ADR-0001 §6.1 text search AIQ cited.
- **Finding 1 (`_loo_paired` empirically weak):** reproduced AIQ's exact 35-trade fixture myself before
  trusting their numbers — full-sample mean diff = 0.001886, matching their stated ~+0.0019. Confirmed the
  defect: the mean-of-LOO-estimates statistic stayed positive despite the single outlier-excluding estimate
  correctly reading negative. **Fixed by requiring unanimous sign agreement** across all n LOO estimates
  (not their mean) — directly resolves the fixture (97.1% agreement, correctly not unanimous →
  `beats_naive_baseline=False`). Verified a genuinely robust synthetic edge (no single outlier) still clears
  at 100% agreement, so the fix isn't just stricter everywhere — it specifically catches single-trade
  fragility without breaking real robustness.
- **Finding 2 (stability-vs-generalization undisclosed):** added `validation_kind` to every Leg A
  (`"held_out_prediction"`) and Leg B (`"stability_check"`) verdict record — travels with the number now,
  not just the docstring, per AIQ's own recommendation.
- **Finding 3 (`"NOT_CLEARED"` not in the ratified enum):** renamed to `"DROPPED"` (ADR-0001 §6.1,
  `cleared/dropped/void/unmeasured`) — confirmed the exact schema text myself before renaming, not just on
  AIQ's citation.
- **Finding 4 (undocumented 5th verdict state):** removed `"SENSITIVITY_ONLY_WOULD_CLEAR"`.
  `evaluate_exit_config` now always returns the true 4-state verdict; `is_primary` (already present) is the
  sole eligibility signal, with the consumer obligation ("CLEARED + is_primary=False is sensitivity
  evidence, never a clearance") stated explicitly in the module docstring rather than assumed.
- **Verified, not just implemented:** AIQ's exact fixture reproduced and now correctly flagged · a
  genuinely-robust synthetic edge still clears unanimously (fix isn't over-strict) · the full Leg A
  real/noise/thin planted-effect suite re-run clean with the new verdict string · a sensitivity cell with a
  real planted edge now correctly returns `CLEARED, is_primary=False` (undisguised, per Finding 4's fix)
  instead of the old made-up state · `scripts/smoke_rolling_watchlist_web.py` still passes.
- All 4 fixes stayed in Lane C (`helm/validation/engine/`, my write-lane) per AIQ's own scoping — did not
  touch `helm/validation/audit/` or their findings doc.
- Pushed → origin/main (`468ca2a`). Reporting to AIQ + the Lead now.

### [AIQ · 2026-08-31] Stage 2 findings — re-verified AI/ML's fixes, all 4 CONFIRMED CLOSED
- **Read the actual diff (`468ca2a`), not AI/ML's summary message**, before accepting anything — same
  standard I've held throughout (LL-34). Findings 2/3/4 confirmed by direct text comparison against my
  original citations: `bar.py`'s `"NOT_CLEARED"`→`"DROPPED"` matches §6.1 exactly; `leg_b.py`'s
  `SENSITIVITY_ONLY_WOULD_CLEAR` downgrade fully removed, `is_primary` now the sole eligibility signal
  with an explicit consumer-facing binding rule in the docstring; `validation_kind` field present on
  every return path in both `leg_a.py` and `leg_b.py`, including the early UNMEASURED branch.
- **Finding 1's fix independently re-derived, not just read** — reimplemented AI/ML's new unanimous-
  sign-agreement logic myself from the diff (not imported), extended `helm/validation/audit/
  stage2_audit.py` with 2 new tests: (a) re-ran my original 35-trade outlier fixture against my own
  reimplementation of their fix — reproduces `full_sample_diff≈0.001886`, `97.1%` agreement exactly, now
  correctly `beats_naive_baseline=False`; (b) built a FRESH no-outlier fixture (40 trades, uniform +0.005
  advantage, zero exceptions) to check the fix doesn't overcorrect into a false-negative machine on a
  genuinely robust case — clears unanimously at 100%, as it should. 8/8 own tests pass.
- **Verdict: Stage 2 CLOSED.** No outstanding findings against AI/ML's Stage-1 delivery. Full
  re-verification appended to `docs/eval/stage2-audit-findings.md`.
- Pushed. Reporting to the Lead now (staged reporting, Director's directive) — Stage 3 (QA) can proceed
  once a QA seat exists (open-items-ledger item 17, not mine to resolve).

## 2026-08-31 — QA (Stage 3: independent reproducibility re-run) — verified at `7d0919c`
- **Blocker hit and resolved first (protocol 11):** the `Trade - QA` clone did not exist — empty
  directory, no `.git`, while all 9 other seat dirs had populated clones. Bootstrapped it myself rather
  than borrow another seat's working tree, which would have destroyed the seat's independence.
- **Every armed leg re-run on exit codes, in my own clone:** `scripts/gate/run.py` → **0**;
  `scripts/gate/legs/secret_scan.py --selftest` → **0** (10/10 K0-K6 positive controls RED, 4/4
  documented placeholders GREEN, self-reference + K0a checks pass).
- **My own end-to-end negative control (LL-10/LL-48).** DevOps's self-test calls `_scan_text()` on
  synthetic strings — it never exercises the real `run_scan()`→`git ls-files`→exit-code path, so it
  cannot answer "show me the input this green would reject" for the gate as actually invoked. Planted a
  synthetic `SEC_API_KEY`-shaped value (never a real credential) in **tracked** `README.md`, working tree
  only: `run.py` → **exit 1**, leg K RED (K6a + K0b), value redacted. Reverted → **exit 0**, tree clean,
  HEAD unchanged, nothing ever staged. **Leg K is genuinely armed on the real path.**
- **AIQ's extended audit reproduced exactly:** 8/8 pass, exit 0, every documented number matches on my
  machine (`full_sample_diff=0.001886`, `97.1%`, `False`; `0.005`/`100.0%`/`True`; ratchet `101.2`; init
  floor `100.0→97.0`; harness `100.0%` signal vs `0.0%` noise). **Determinism — NN-9's actual assertion:**
  byte-identical across 3 consecutive runs AND across `PYTHONHASHSEED ∈ {0,1,42,12345}`.
- **NN-3 verified mechanically, not by reading:** ran the audit under `runpy` and diffed `sys.modules` —
  it loads **zero** `helm.*` modules, loads `tools.rolling_watchlist` as expected. Independence honored.
- **Confirmed the SHIPPED engine carries all 4 Stage-2 fixes** by importing `helm.validation.engine.leg_b`
  / `bar` directly (which AIQ is forbidden to do): AIQ's fixtures reproduce exactly against the real code,
  `_multiseed_kfold_paired` identical across 10 calls, and `clearance_verdict` returns the ratified 4-state
  enum (`UNMEASURED`/`DROPPED`/`DROPPED`/`CLEARED`). **AI/ML's fixes are real; AIQ's verdict is correct.**
- 🟠 **F-1 (SEV2 proposed) → DevOps Stage 4.** Reverting AI/ML's Finding-1 fix in `leg_b.py:123` (working
  tree only) leaves the audit at **8/8 PASS, exit 0** — the defect Stage 2 exists to certify as fixed was
  reintroduced and every check stayed green. Cause is structural, **not AIQ's defect**: NN-3 forbids the
  audit importing the engine (it says so at line 275), so nothing armed binds
  `helm/validation/engine/`. Stage 2's closure and the Lead's confirming re-run are both invariant to the
  engine's content — LL-48's vacuous green. Correctness is fine; **coverage is the gap.** Severity is a
  HUMAN/GA call per my oracle-boundary row, routed via the Lead, not ruled by me.
- 🟡 **F-2 (SEV3) → DevOps.** `run.py:29` hardcodes `"SKIP (no validation engine yet)"` for the QA leg;
  the engine has existed since Stage 1. `LEG_TABLE`'s reasons are hardcoded strings, not computed
  conditions, so a stale reason can never self-correct — boundary-honesty defect.
- **NOT COVERED (LL-35), stated plainly:** **NN-9's real-data mandate remains OPEN** — no `helm/ingest/`,
  no OHLCV pulled, no real CLEARED/DROPPED verdict to re-derive; all of the above is mechanism +
  determinism on synthetic fixtures. Blocked on SDE1's `helm/ingest` lane, **not mine to fix, only to
  name.** Also not covered: `adapter.py`/`harness.py`/`leg_a.py` end-to-end (no data); the 6 SKIP legs'
  future correctness; the trailing-stop against real market bars; project packaging (`helm.*` needs a
  manual `PYTHONPATH`). Nothing here fixed by me — I never touch the code under test.
- Full report: `docs/roles/qa/stage3-reproducibility-report.md`. Reporting to the Lead now.

### [DevOps · 2026-08-31] Stage 4 — armed leg 3 (F-1) + computed SKIP reasons (F-2)
- Pulled `96b90c0`, read QA's Stage-3 report in full (`docs/roles/qa/stage3-reproducibility-report.md`)
  and the actual shipped `helm/validation/engine/{bar,leg_b}.py` / `helm/validation/audit/
  stage2_audit.py` before touching anything, per the message's own instruction.
- **F-1 fixed: `scripts/gate/legs/cv_reproducibility.py` (new) arms leg 3.** Imports the real, shipped
  `helm.validation.engine.{leg_b,bar}` and re-runs QA's own already-independently-reproduced fixtures
  (Stage-3 §4) against it — a mechanical regression trip-wire, **not** a second independent audit (NN-3
  forbids me from re-deriving/judging the engine's methodology; that's AIQ's job, already done twice).
  This is the one place in the chain allowed to import the engine at all, per the Lead's own framing —
  DevOps is neither builder (AI/ML) nor judge (AIQ).
- **Self-test reproduces QA's exact manual finding, now permanently, mechanically:** reintroduces the
  pre-Finding-1-fix bug into `leg_b.py` (working tree only, regex-located and patched, never staged/
  committed), re-runs, confirms RED with the exact diagnostic QA described by hand
  (`beats_naive_baseline` flips from `False` to `True` on the outlier fixture), reverts via `git checkout
  --`, confirms GREEN again. Verified both standalone and through the actual `run.py` code path (leg 3's
  `run_fn` is the identical function `run.py` calls when armed — no separate wiring to drift).
- **F-2 fixed: `scripts/gate/run.py` redesigned so every SKIP reason is computed from live repo state**,
  not a hardcoded string — the specific stale line QA caught (leg 3's "no validation engine yet") is now
  structurally impossible to go stale the same way again: each leg's checker function inspects the actual
  filesystem (`helm/ingest/` exists? `pyproject.toml` exists? a pytest-discoverable file exists?) at run
  time. Also picked up QA's softer, not-pressed note in the same pass (line 28's false "no test suite
  yet"): the new `check_unit_tests()` correctly found a real pytest-discoverable file
  (`docs/guardrail-v2.1/analysis/sub2_backfill_test.py`) and reports that accurately instead.
- Verified end-to-end before committing: `secret_scan.py --selftest` still passes (no regression from
  the `run.py` refactor), `cv_reproducibility.py --selftest` passes, full `run.py` run is GREEN with leg
  K and leg 3 both ARMED+PASS and every SKIP reason now live-computed and accurate.
- Corrected `harness-design.md`'s leg-3 row (was describing a from-scratch re-derivation script that was
  never what got built) and flagged its top banner as stale (still said "holding pending P-1" — P-1
  cleared 2026-08-30) rather than silently rewriting the historical design rationale.
- Reported once to the Lead. No blocker.

### [SDE1 · 2026-08-31] D-TRADE-037 Gate-1 proposal — ticker universe + date-range for the first real-data pull (PROPOSAL ONLY, no pull executed)
- Verified D-TRADE-037 at source (`c1afae6`) before acting; confirmed `helm/ingest`/`helm/storage`/`helm/spend`
  all still absent from the tree — nothing built, nothing to revise.
- **Grounded in the actual precedent, not invented:** read `C:\Users\beale\short-interest-study\
  SHORT_INTEREST_STUDY_FINDINGS.md` (measured, not estimated) — the same guardrail/S3 gain+volume-spike
  cohort the scanner's own defaults define (`--guardrail-price-min 2.0 --guardrail-price-max 20.0
  --guardrail-min-gain-pct 10.0 --guardrail-min-rel-volume 2.0`) already produced **917 qualifying events
  across 754 unique tickers, 2024-06-13 → ~2026-04** (≈1.2 events/ticker over ~22 months) — a real, already-
  measured base rate for exactly this cohort, not a guess.
- **Proposal:**
  - **Tickers: a 100-ticker subset of the same 754-ticker short-interest-study cohort** (list in
    `raw_short_interest_all.csv`, exact 100 TBD — a straightforward reasonable-coverage selection, e.g.
    every 7th-8th ticker in the file to avoid any manual cherry-picking bias) — reuses a *proven*
    event-producing universe instead of guessing a fresh one; a fresh-guess universe risks near-zero
    guardrail firings and an UNMEASURED verdict for reasons unrelated to the component being tested.
  - **Date range: 2024-06-01 → 45 days before actual pull execution** (illustrative, if executed promptly:
    ≈2024-06-01 → 2026-07-17). The 45-day buffer, not a fixed calendar date, is the actual rule — it
    guarantees the longest Leg-A horizon (1-month forward, per ADR-0001 OP-2) is fully realized for every
    signal even if Gate-2 approval is delayed; a fixed end-date would silently violate NN-1 point-in-time
    discipline if the pull slips past it.
  - **Expected yield: ≈120 guardrail-qualifying events** (100 × 1.2/ticker, same base rate) — clears
    D-TRADE-029's 30-event floor with ~4x margin for the *aggregate* guardrail trigger. **Flagged
    explicitly, not hidden:** a specific Leg-A sub-pattern (bull-flag, ABCD, etc.) fires at some unknown
    fraction of that base rate — some components may still land UNMEASURED at this size, which is
    D-TRADE-029's own correct, by-design outcome for a thin-firing pattern, not a proposal defect.
- **Sizing logic (why 100 tickers, not 754 or 10):** the "keep it bounded" constraint the Lead raised binds
  on **API call count** (Massive rate-limit/quota risk, `helm/spend` doesn't exist yet), not on date-range
  length — a multi-year daily-bar pull is typically one call per ticker regardless of how many months of
  history it returns (per the scanner's own `--period`-style single-request pattern). So ticker count is
  the real lever; 100 (≈13% of the proven cohort) is a deliberate order-of-magnitude cut from the original
  study's 754 while keeping several-fold margin over the 30-event floor.
- **Unmeasured, flagged not assumed:** the exact Massive rate-limit for the confirmed "Non-Professional"/
  individual self-serve tier (`docs/security/tos-taint-review.md:70,286`) was not found as a hard number in
  this repo — taint/tier is resolved (LOW-MEDIUM), but the calls-per-minute ceiling isn't. Recommend DevOps/
  FinOps confirm it before Gate-2 execution; doesn't block the scope proposal itself (100 calls is small
  under any plausible self-serve rate limit).
- Componen­t choice (which specific Leg-A/Leg-B component gets the first real verdict) is explicitly NOT
  part of this proposal — that's the build step after Gate-2, likely AI/ML's call given the existing
  synthetic-only pipeline in `helm/validation/engine`.
- Reported once to the Lead (this entry + a direct message) — first of D-TRADE-037's two required
  report-backs. No pull executed; no code written. Holding for Gate 2 (Director approval).

### [SDE1 · 2026-08-31] D-TRADE-038 Gate-2 execution — built `helm/ingest`/`helm/storage`, ran the approved pull: BLOCKED, two findings, neither guessed past
- Verified D-TRADE-038 at source (`b5da3b5`) before acting. Built exactly the approved scope, nothing more:
  `helm/ingest/massive.py` (point-in-time daily-OHLCV adapter, explicit `[start,end]` — reuses
  `tools.rolling_watchlist._resolve_massive_api_key` for key resolution only, not the provider-host call
  itself, which lives here per the leg-T boundary), `helm/storage/raw_store.py` (file-first CSV persistence
  + a per-call `spend_ledger` row, D-TRADE-019 — `cumulative_day` is a genuine per-UTC-day running count,
  not a global row index, so a future spend guard can read it directly without a migration),
  `helm/ingest/run_gate2_pull.py` (the approved-scope driver: the same 100-ticker deterministic even-sample
  of the short-interest-study's 754-ticker cohort my Gate-1 proposal specified, `2024-06-01` →
  `execution_date − 45d` = `2026-07-17`).
- **Finding 1 — scope gap discovered before executing, not after:** reading `helm/screener/adapter.py`
  (`extract_intraday_features(intraday_df, ...)`) and `helm/validation/engine/leg_b.py`
  (`simulate_day_trades(intraday_df, ...)`) shows **both Leg A and Leg B genuinely require historical
  INTRADAY bars**, not just daily OHLCV — my Gate-1 proposal (and its Gate-2 approval) was sized entirely
  around the short-interest study's *daily*-cohort precedent; I had not accounted for this. Daily bars are
  still necessary (forward-return labels at 1d/1w/1m, `prior_high/prior_low/prior_close` context) but **not
  sufficient** — proceeding with the daily-only pull as approved cannot by itself produce a real Leg-A/B
  verdict. Did not silently expand into an intraday pull (a materially bigger, differently-shaped request
  that needs its own Gate-1/2-style sizing and approval per D-TRADE-038's standing condition) — flagging
  for the Lead + AI/ML instead.
- **Finding 2 — the approved pull executed and BLOCKED, not silently retried:** ran exactly 100 calls
  (verified: `spend_ledger.csv` has 100 rows, matching the approved count) against the approved tickers/
  date-range. **All 100 returned HTTP 401 Unauthorized** — `ohlcv_daily.csv` has zero data rows. Not a bug
  in this new code: the request uses the scanner's own already-proven URL template, key-resolution helper,
  and query-param shape verbatim (`tools.rolling_watchlist._massive_aggs`'s pattern) — only the date-range
  values are parameterized instead of "N days back from today." **Diagnosed the key's format only, per the
  D-TRADE-026 precedent (length/structure, never the value):** 32 characters, no leading/trailing
  whitespace or quote characters, no embedded newline — not an obviously mangled env var. Did not attempt
  further live calls, alternate auth-header formats, or any workaround — credential validity/entitlement is
  outside what I should self-diagnose by guessing against a live provider. **Zero rows returned, zero
  dollars spent (personal-tier flat sub, an unauthorized call carries no charge) — but 100 real calls were
  made against the approved budget and are now spent on this attempt.**
- **Both output files committed as the honest, checkable record of what happened** (protocol 16 applies to
  a failed result too) — `helm/storage/data/ohlcv_daily.csv` (header only, 0 rows) and
  `helm/storage/data/spend_ledger.csv` (100 rows, `ok=False` throughout, no secret value in either file).
- **Not guessing past either finding.** Reported both to the Lead as blockers, same message — this is the
  first of D-TRADE-038's two report-backs, but as a BLOCKER report, not a completion report (no verdict is
  possible yet; the pull itself didn't yield usable data). Awaiting: (1) credential re-verification (Massive
  key validity/tier/entitlement for the `/v2/aggs/ticker/.../range/...` endpoint specifically — SecOps/
  Director territory, not mine to work around) before any re-attempt: at 100 calls already spent, a blind
  retry against the same possibly-bad key would burn more of the approved budget for the same result; (2)
  coordination with AI/ML on the intraday-data requirement before proposing a revised scope.

### [AI/ML · 2026-08-31] Lane-A/Lane-C data contract: intraday scope for Leg A/B (SDE1 coordination)
- SDE1 flagged, while building `helm/ingest`/`helm/storage`, that `helm/screener/adapter.py` and
  `leg_b.py`'s use of `simulate_day_trades` both need `intraday_df` — not covered by their Gate-1 sizing,
  which was based on the daily-cohort-only precedent. Asked precisely: full-window intraday for all 100
  tickers, or only specific event-days; what bar interval; whether any OP-4 component sidesteps this.
  Answered from the actual code + the proven precedent, not from memory — this wasn't written down
  anywhere before now, so recording it here as the real Lane-A/Lane-C contract:
  1. **Event-days only, not a full daily walk.** `tools/rolling_watchlist.py::main()` itself only ever
     calls `load_intraday()` for `holding_tickers` — tickers that already passed the guardrail/rollover
     spike filter (`rolling_watchlist.py:1343-1346`) — never the full candidate universe; the 4 proven
     equity studies also tested a pre-selected event cohort, not a rolling daily walk. SDE1's own
     ~120-event estimate is the right order of magnitude, not ~100 tickers × 2 years of 5-min bars.
  2. **Leg A's forward-return TARGET is daily-only** (1d/1w/1m closes, OP-2/proven-study convention) —
     already covered by SDE1's planned 100-ticker daily-OHLCV pull. Intraday is needed only for the
     FEATURE side (did a component fire that day) — two different parts of the same record, not two
     independent asks.
  3. **Bar interval: 5m**, matching `load_intraday`'s own default (`rolling_watchlist.py:145`) and the
     pattern detectors' actual design assumption — a different interval would be an untested deviation
     from the scanner's own proven logic.
  4. **No daily-bar-only escape hatch.** All 9 of OP-4's final Leg-A components (8 pattern detectors +
     the alignment trigger) are intraday-only; the daily-only signals (short_interest/catalyst) are
     explicitly out of scope (OP-4: not re-litigated). A first real Leg-A verdict cannot happen without
     solving the intraday-pull question — there is no smaller slice that avoids it.
  5. **Leg A and Leg B likely share the same intraday pull, not two additive asks** — Leg B's entry set
     is drawn from the same alignment-trigger events Leg A computes on the same days. Flagged as likely,
     not yet confirmed — the actual cohort-construction logic (which specific days, drawn how) is a joint
     Lane-A/Lane-C decision not yet designed.
- Not yet a decision — a data-contract clarification for SDE1's Gate-1/2 sizing proposal, which is theirs
  to bring back to the Lead/Director. Recording here so it doesn't live only in a DM.

### [SDE1 · 2026-08-31] AI/ML coordination resolved — intraday data contract confirmed, independently re-verified at source
- AI/ML answered directly (not from memory — traced their own code + the scanner's `main()`): Leg A/B need
  intraday bars **only on event-days** (the ~120-event framing I proposed, not a blanket 100-ticker×2-year
  pull), 5-minute bars (matching `load_intraday`'s own default), no daily-only escape hatch (all 9 of OP-4's
  Leg-A components are intraday-only), and Leg A/B likely **share one intraday pull**, not two additive asks.
- **Independently re-verified the core claim at source, not taken on faith:** `tools/rolling_watchlist.py`
  `main()` builds `daily_data` for every ticker (line 1292) but only computes `holding_tickers` from the
  `holding_up` filter (line 1305) and calls `load_intraday()` inside `for t in holding_tickers:` (line
  1318+) — intraday IS fetched only for the event-filtered subset in the scanner's own proven logic, exactly
  as claimed.
- **Next real step, not yet taken:** the ~120 figure is still an estimate off the short-interest study's
  precedent — the ACTUAL event-day/ticker pairs are only knowable after the (currently blocked) daily pull
  succeeds. A concrete intraday-scope proposal has to come AFTER that, sized off the real event-days it
  finds, not before. Sequenced, not parallel: fix the 401 → confirm event-days from real daily data →
  propose the intraday scope off real numbers.

### [SDE1 · 2026-08-31] Real event-days identified from the real pull — 651, not the ~120 estimate
- Built `helm/ingest/identify_events.py`: reuses `tools.rolling_watchlist.compute_relative_volume`
  directly (imported, not re-derived) and replicates `scan_guardrail_criteria`'s `passes_core` formula
  inline (gain_pct via pct-change, rel_vol via the imported function, price in `[2,20]`) — same defaults as
  that function's signature (10% gain, 2x rel-vol), not new thresholds. Not a per-row call to
  `scan_guardrail_criteria` itself (it checks only its own last row by design; calling it ~45k times for
  arithmetic this simple to reproduce exactly would be needless overhead, not a fidelity gain).
- **Result: 651 real event-days, 91/100 tickers, mean 7.15/ticker** (`helm/storage/data/event_days.csv`) —
  **~5.4x my original ~120 estimate.** Sanity-checked: every row genuinely respects all three thresholds
  (0 violations on price/gain/rel-vol bounds), right-skewed distribution (median rel-vol 4.76x, max
  13,850x) matching the short-interest study's own description of this cohort shape. **Likely cause of the
  gap, not yet confirmed:** my 100-ticker even-sample (deterministic, not cherry-picked) happens to include
  several `.WS`/warrant-suffixed tickers, which are structurally more volatile in percentage terms at low
  absolute price — could be pulling the per-ticker event rate above the 754-ticker study's overall average.
  Flagging the gap plainly rather than treating my original estimate as if it had been right.
- **Not yet proposing intraday scope off the full 651** — that's a real sizing decision (651 calls is ~6.5x
  the already-approved/executed 100-call daily pull), not mine to size unilaterally without surfacing the
  tradeoff. Bringing two options back to the Lead rather than picking one myself.

### [AIQ · 2026-08-31] D-TRADE-038 real-data audit — first real provider data in this project, verified clean
- Per the Director's explicit build-chain extension (SDE1 executes → AIQ audits → QA reproduces → Lead
  verifies at source). Read `helm/ingest/massive.py`, `run_gate2_pull.py`, `helm/storage/raw_store.py`
  directly (source, to understand the claims — not imported for computation). Every check below is my own
  pandas code run directly against the actual CSVs.
- **NN-1 (point-in-time):** `fetch_daily_ohlcv` requests an explicit bounded `[start,end]` window, not an
  unbounded/as-of-today query. Independently confirmed (not just read from source): no row in the actual
  CSV exceeds the approved `end_date` (max date 2026-07-17, exactly matching `today-45d`). Ingest mechanics
  are point-in-time-safe by construction for a bounded historical pull.
- **Data sanity, zero violations across 45,426 rows/100 tickers:** High≥Low, Close/Open within [Low,High],
  no negative/zero volume or price, no duplicate (ticker,date) pairs, no NaN in any core field.
- **Ledger-vs-CSV consistency:** 200 ledger rows (100 pre-fix failures + 100 successes, matches the
  reported history). Cross-checked every successful call's claimed `rows_returned` against the actual
  per-ticker CSV row count — **zero mismatches**; ledger sum (45,426) = actual CSV total (45,426) exactly.
  The ledger is honest, not just present.
- **Row-count variance investigated, not waved off:** 9 tickers under 200 rows checked individually — late
  starts (uplisting) and early ends (delisting-consistent, e.g. NKLA's real-world bankruptcy/relisting
  timeline lines up) explain the low counts, not a partial pull. Missing-business-day gap check on the
  wider set: a handful of tickers show real internal gaps (up to ~40% of business days, plausible trading
  halts on volatile microcaps) — confirmed no NaN-filled/interpolated rows anywhere, missing days are true
  absences, matching NN-5's exclude-don't-impute principle already.
- **2 findings, both forward-looking flags, neither blocks this delivery:**
  1. `adjusted=true` (matches `tools/rolling_watchlist.py`'s own pre-existing convention exactly, verified
     by direct comparison — not new) is a genuine, previously-undisclosed point-in-time risk now that it's
     load-bearing for an actual backtest rather than a live scan: adjusted prices can be retroactively
     restated by a later split/dividend, a real risk on this volatile-microcap cohort. Recommend an
     explicit adjusted-vs-raw decision, disclosed, not a silently inherited default from a different
     use case.
  2. Real coverage gaps exist within some tickers — the data itself handles this correctly (no fabrication),
     but whoever builds the Leg A/B point-in-time join must skip missing dates cleanly, not assume
     continuous coverage.
- **Verdict: pull independently verified clean.** All sanity/consistency checks pass with zero violations;
  ingest is point-in-time-safe for its stated purpose; row-count variance is explained by real market
  history. No blocker. Full audit: `docs/eval/d-trade-038-data-audit.md`.
- Reporting to the Lead now (staged reporting, Director's directive).

### [SDE1 · 2026-08-31] D-TRADE-039 — `helm/ingest/massive.py` flipped to raw prices, verified with real divergence, not just the param flip
- **Scope exactly as dispatched:** flipped `adjusted=true` → `adjusted=false` in `helm/ingest/massive.py`
  only (one line + a docstring note explaining why). Did NOT touch `tools/rolling_watchlist.py`'s own
  `adjusted=true` live-scan call — out of scope per the Director's ruling, AIQ's own finding that the
  distinction doesn't matter there.
- **Verified with a real before/after check, not trust-the-parameter:** re-pulled 10 tickers raw
  (`adjusted=false`) through the actual tracked `fetch_universe_daily`/`append_spend_ledger` path (10 real
  calls, logged in `spend_ledger.csv`, tagged as a D-TRADE-039 verification pull — not part of any approved
  Gate-2 scope, a diagnostic batch) and diffed against the existing D-TRADE-038 adjusted CSV for the same
  ticker/dates. **3 of 10 tickers show clean, discrete divergence** — ANY (ratio 0.1 before a step, 1.0
  after), AREBW (0.01 → 1.0), **ASST (0.01 → 0.05 → 1.0, two step-changes)** — exactly the signature of real
  reverse splits (a constant ratio, not noise), not found from prior knowledge of these tickers' corporate
  history but discovered empirically from the actual data. 7 of 10 show zero divergence (no split in-window
  for those names) — the expected mix, not "everything differs" (which would suggest a bug) or "nothing
  differs" (which would suggest the flip did nothing).
- **Answering the Lead's re-pull question with a technical read, not just an opinion:** YES, the existing
  D-TRADE-038 daily dataset (`3cf6cc7`) should be re-pulled before Leg A/B use it. This isn't a theoretical
  risk anymore — I just proved at least 3 of the 100 approved tickers have MATERIAL (90-99%) price
  differences between adjusted and raw in this exact dataset, over this exact window. Any Leg-A/B
  computation touching ANY/AREBW/ASST (forward returns, trailing-stop trigger levels) using the existing
  adjusted CSV would be silently wrong for those tickers specifically, not just theoretically inconsistent.
  Given the same 100-ticker/date-range scope was already Director-approved once, re-pulling under the
  corrected parameter is the same data source and method, not new scope in the D-TRADE-039 sense — but I'm
  not self-authorizing another 100-call pull without the Lead/Director explicitly saying so, same discipline
  as every pull so far.
- Not yet re-pulled the full 100 — holding for the Lead/Director's decision on the open question before
  spending the next 100 calls.

### [SDE1 · 2026-08-31] D-TRADE-040 executed — daily dataset re-pulled raw, old adjusted version preserved not overwritten
- Verified D-TRADE-040 at source (`f435a33`) before acting. Preserved the superseded adjusted dataset —
  `git mv ohlcv_daily.csv → ohlcv_daily_adjusted_D-TRADE-038_SUPERSEDED.csv` — before writing the new pull,
  so no prior state is silently lost; `ohlcv_daily.csv` is now unambiguously the raw/authoritative file for
  any downstream consumer that doesn't read this log.
- Executed the same scope as D-TRADE-038 (same 100-ticker list, `2024-06-01` → fresh-recomputed
  `execution_date − 45d`), now via the D-TRADE-039-fixed `adjusted=false` code. **100/100 tickers
  succeeded, 45,426 rows (identical count to the original pull — same coverage, different prices), zero
  nulls.** Timed the run (54.2s for 100 calls, ~0.54s/call, no errors/retries) — **no rate-limit signal
  observed; flagging that I actively watched for one, per the standing condition, not that I skipped the
  check because nothing went wrong.**
- **Spot-verified the fix actually changed the data as expected**, not just that the pull succeeded: ANY,
  AREBW, ASST (the 3 tickers already proven to diverge) show real differences from the old adjusted file;
  ACFN (previously confirmed non-diverging) still matches — the same split/no-split pattern found during
  D-TRADE-039's verification, now reproduced at full 100-ticker scale.
- `spend_ledger.csv` append-only as designed — the D-TRADE-038 original 100 (failed+succeeded) and the
  D-TRADE-039 10-ticker verification batch both remain, this run's 100 rows append on top.

### [SDE1 · 2026-08-31] Re-identified event-days on corrected raw data; found + tested (not assumed) a real split-artifact risk, corrected my own overreach
- Re-ran `identify_events.py` on the D-TRADE-040 raw data: **560 events (down from 651 under adjusted
  prices)** — a real, expected change now that gain_pct/rel_vol are computed from corrected closes.
- **Caught a genuine data-quality issue via manual inspection, not assumption:** ASST showed a
  `gain_pct=455.74%, relative_volume=1312.00` "event" — investigated before trusting it. Confirmed
  (precisely, by diffing this raw pull against the now-superseded adjusted file) 3 tickers have real split
  transitions inside the window: ASST (2024-07-02, 2026-02-06), ANY (2026-02-10), AREBW (2026-04-27) — raw
  prices/volumes jump discontinuously at these dates, which `pct_change()`/`compute_relative_volume()` can
  misread as an organic move. Added `split_contaminated_mask()` to `identify_events.py`: excludes any
  candidate event within 20 TRADING days (matching `VOLUME_LOOKBACK`, using each ticker's own trading-day
  index) after a known transition. **559 events after exclusion — only 1 actually removed.**
- **Went back and checked my own hypothesis before trusting the filter, and it was partly wrong:** the
  transition DAYS themselves turned out NOT to spuriously qualify as events (`rel_vol` is actually LOW right
  at a transition, 0.1x-0.7x, not high) — my initial worry about widespread contamination was overstated.
  **And the specific 455.74%/1312x ASST event that triggered this whole investigation is REAL, not an
  artifact** — checked for a coverage gap (none, consecutive trading days) and the raw OHLCV directly:
  close jumped $0.61→$3.39 on 316M shares (vs. ~197K the prior day) — a genuine explosive move, exactly the
  kind of event this cohort is designed to find, not a data defect. Correcting my own reasoning here rather
  than silently keeping a filter that would have wrongly suppressed real data.
- **Documented plainly as a one-time, non-general fix:** the transition-date list is a hardcoded, exact
  result of diffing against a soon-to-be-deleted reference file (the old adjusted CSV) — it will NOT
  generalize to a future raw-only pull with no adjusted file to compare against. Flagged in the module
  docstring as a forward-looking gap (a real split detector needs an intrinsic method, e.g. a corporate-
  actions API or a joint price/volume-ratio heuristic), not solved here — out of this task's scope.
- Pushed alongside D-TRADE-040 in the next commit. Moving to sampling ~150 of the 559 for D-TRADE-041.

### [SDE1 · 2026-08-31] D-TRADE-041 executed — 150-event intraday pull, real 5-minute bars, first Leg-A/B-ready data
- `helm/ingest/sample_events.py`: deterministic even-stride sample of the 559 cleaned events (ticker-then-
  date sorted, same convention as the original 100-ticker cohort sample — no randomness, fully reproducible)
  → **150 events, 78 unique tickers**, reasonable spread (median 1/ticker, max 6/ticker — not dominated by a
  few names). Written to `helm/storage/data/intraday_sample.csv`, the checkable input to the pull.
- Added `fetch_intraday_ohlcv`/`fetch_sampled_intraday` to `helm/ingest/massive.py` (5-minute bars, raw
  prices per D-TRADE-039, one call per (ticker, event_date) pair) and `write_intraday_ohlcv` to
  `helm/storage/raw_store.py` (long-format CSV, `event_date` carried explicitly alongside each bar's own
  timestamp).
- **Smoke-tested on 5 events before committing to the full run** (2.8s, 5/5 succeeded, no rate-limit
  signal) — then executed the full 150. **150/150 succeeded, 15,703 bars, 79.8s total (~0.53s/call, same
  pace as the smoke test and the D-TRADE-040 daily pull — no slowdown, no errors, no rate-limit signal
  observed across the whole run, actively watched throughout per the standing condition, not just checked
  at the end).**
- Sanity-checked: 150/150 unique (ticker, event_date) pairs (exact match to the sample, no dupes/drops),
  zero nulls, every bar's own timestamp date matches its labeled `event_date` (no cross-day contamination),
  10-192 bars/event (median 100, plausible for a 5-min session with some extended-hours variation).
  `spend_ledger.csv` now 460 rows total — the full honest history: 200 (D-TRADE-038 orig, incl. the 100
  failed) + 10 (D-TRADE-039 verify) + 100 (D-TRADE-040 re-pull) + 150 (D-TRADE-041) = 460, exact.
- **First real intraday data this project has ever pulled — Leg A/B's actual data contract (raw daily +
  raw event-day intraday) is now satisfied for a real, bounded sample**, not synthetic fixtures. Reporting
  both D-TRADE-040 and D-TRADE-041 complete to the Lead now.

### [AIQ · 2026-08-31] D-TRADE-040/041 audit — MAJOR FINDING: split-exclusion coverage 3/30, not 3/3
- Per the Director's build-chain discipline extension. Read `identify_events.py` in full before touching
  anything; every check is my own code against the actual CSVs and `compute_relative_volume` called
  directly (a raw primitive), never against `identify_events.py`'s own output as ground truth.
- **NN-1 on `split_contaminated_mask`: confirmed safe.** Pure position arithmetic against a hardcoded,
  already-known transition date — no row's exclusion depends on data after that row. The *discovery*
  method (retrospective raw-vs-adjusted diff) is correctly self-disclosed by SDE1 as not generalizing to a
  live/future pull — confirmed accurate, not a new issue.
- **MAJOR FINDING: independently reproduced the raw-vs-adjusted divergence across all 100 tickers** (not
  just SDE1's 4 spot-checked) — found **30 tickers with a genuine, clean, permanent in-window ratio step**
  (verified several by hand: pre/post-jump ratio std ≈0.0, textbook reverse-split ratios like NKLA
  0.033→1.0, TRVN 0.04→1.0). **Only 3 (ANY/AREBW/ASST) are in `SPLIT_TRANSITION_DATES`. 27 are missing**
  (full ticker/date list in the findings doc).
- **Quantified the impact, not just the gap:** 17 of the current 559 "clean" `event_days.csv` rows fall
  within 20 trading days of one of the 27 missing transitions — several with the exact tell-tale extreme
  signature SDE1's own docstring uses to define the problem (PSIG 937% gain/12.5x rel-vol, NUKK 825%, TCRT
  590%, KZIA 366% — same order of magnitude as the ASST 455.74%/1312x founding example). **3 of these 17
  already consumed real paid intraday-pull calls** (HTOO 2025-07-22, UPXI 2024-10-17, XHG 2024-12-09).
- **Checked the Lead's specific ASST 2025-05-07 ask — correctly un-excluded, but SDE1's own docstring
  characterization of WHY is wrong.** Mapped ASST's full ratio history: only 2 real transitions, neither
  anywhere near 2025-05-07. Pulled the raw OHLCV directly: close 0.61→3.39, volume ~197K→**315.8M** shares
  then sustained elevated (241.9M/54.4M/18.4M) over following days while price gradually decays — a real,
  sustained multi-day market event (consistent with a short-squeeze/news spike), not a split-basis
  discontinuity or a single bad tick. Correct outcome, wrong stated reason — the docstring should be fixed
  so a future reader doesn't inherit the mischaracterization; no code change needed for this one event.
- **Data sanity + point-in-time, both new files: zero violations.** `ohlcv_daily.csv` (raw, 45,426
  rows/100 tickers) and `intraday_5m.csv` (15,703 rows/78 tickers): High≥Low, Close/Open in range, no
  negative/zero volume or price, no dupes, no NaN — all clean. Every intraday bar's own date matches its
  `event_date` exactly, 0 mismatches. 150-count cross-checked against `intraday_sample.csv` — matches.
- **Not a co-sign as-is.** The mechanism is right (NN-1-safe, correctly diagnoses real splits where it's
  been told about them) — coverage is the defect. Recommend: extend `SPLIT_TRANSITION_DATES` with the 27
  found, re-run `identify_events.py` (559 will drop further), re-derive the intraday sample from the
  corrected list (at minimum replace the 3 already-paid contaminated pulls), fix the ASST docstring.
- Full findings + exact ticker/date list: `docs/eval/d-trade-040-041-audit.md`. Reporting to the Lead now —
  flagging as high-severity given real spend already touched contaminated events, not holding this for a
  routine end-of-task summary.

### [SDE1 · 2026-08-31] AIQ's D-TRADE-040/041 finding fixed — extended coverage, reconciled the sample, caught my own bug along the way
- **Independently re-derived AIQ's finding before applying it, not just trusted it:** reproduced the
  raw-vs-adjusted >15%-step detection across all 100 tickers myself — exact match, 30 tickers/34
  transitions, identical dates. Extended `SPLIT_TRANSITION_DATES` from 3 to all 30. Re-ran
  `identify_events.py`: **542 events (down from 559, 17 removed — exactly matching AIQ's table, confirming
  no additional in-window events beyond what they'd already checked).**
- **Reconciled the sample, not regenerated it** (per the Lead's instruction — completing the existing
  authorization, not new scope): `helm/ingest/reconcile_d041_sample.py` confirmed the OLD 150-sample had
  exactly the 3 contaminated events AIQ flagged (HTOO 2025-07-22, UPXI 2024-10-17, XHG 2024-12-09) and no
  others, kept the 147 still-valid/already-paid events untouched, sampled 3 deterministic clean
  replacements, and pulled intraday data for **only those 3** — not re-pulling the 147 already-good ones.
- **Caught a real bug in my own reconciliation script before trusting its output:** first verification pass
  showed `sample keys == intraday keys: False` despite both files reporting the right row counts — didn't
  wave that off as a formatting quirk. Root cause: the 3 new rows' `event_date` was inserted as a raw
  `.isoformat()` string while the 147 kept rows were `Timestamp`-typed; `pd.concat` silently mixed both
  dtypes in one column, and `to_csv()` round-tripped them as two different string formats
  (`"2024-11-07 00:00:00"` vs `"2024-11-07"`). Fixed the CSV directly (`format='mixed'` re-parse, no
  re-pull needed — the underlying data was correct, only its string representation was inconsistent) and
  fixed the root cause in the script (`pd.Timestamp(event_date)` before insert) so it doesn't recur if
  re-run. Full re-verification after the fix: sample/intraday key sets match exactly, zero nulls, every
  sampled event confirmed present in the corrected clean-event list, `spend_ledger.csv` at 463 rows (460 +
  3 replacement calls, honest append-only history).
- Fixed the docstring's ASST 2025-05-07 characterization per the Lead's specific ask — now states plainly
  it's a real market event (independently corroborated by AIQ + Lead's own OHLCV pull), not a split
  artifact; the exclusion behavior itself was already correct and needed no change.
- Reporting to the Lead: fix complete, ready for AIQ's re-audit (not a rubber stamp — full re-derivation
  against the corrected files, per their own stated standard).

### [AIQ · 2026-08-31] D-TRADE-040/041 re-audit — fix confirmed, fully re-derived, CO-SIGNED
- Full independent re-derivation per the Lead's 6-point dispatch, same discipline as the original audit —
  never imported `identify_events.py`'s output, never trusted SDE1's or the Lead's report as ground truth.
- **1-2. Coverage completeness:** re-ran my exact >15%-ratio-step scan against the current
  `ohlcv_daily.csv`/adjusted-superseded pair — **30 tickers, 34 transitions, exact match** to the
  corrected `SPLIT_TRANSITION_DATES`, date-for-date (including the 4 tickers with 2 transitions each).
  Zero tickers or dates found by me that aren't already in the list.
- **3. Independently rebuilt `event_days.csv` from scratch** (my own reimplementation, calling
  `compute_relative_volume` directly, never importing SDE1's module) — **542 events, byte-identical to
  the delivered file**: 0 rows only-mine, 0 rows only-theirs, 0 value mismatches across all 542 matched
  rows. All 17 of my originally-flagged contaminated rows confirmed gone from both.
- **4. Re-checked all 150 intraday-sample events myself** (not just the 3 known replacements) against the
  30-ticker transition windows — **0 land inside any contamination window.** The 3 originally-contaminated
  events confirmed gone; sample count still 150.
- **5. Dtype bug genuinely fixed, verified by regex not just Python type** (a mixed-representation bug can
  hide behind "all str" if formats differ) — `event_date`/`bar_ts` uniformly clean
  `YYYY-MM-DD`/`YYYY-MM-DD HH:MM:SS` across all 15,561 raw intraday rows, 0 non-conforming. Data sanity +
  point-in-time on the regenerated file: zero violations, 0 date mismatches.
- **6. Docstring fix reviewed — accurate and properly calibrated**, describes the observed ASST pattern
  without overclaiming a specific cause or understating the earlier mischaracterization.
- **Verdict: CO-SIGNING.** Every finding from the original audit independently re-verified as resolved,
  not accepted on report. Full re-verification: `docs/eval/d-trade-040-041-audit.md`. Reporting to the
  Lead now.
