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
