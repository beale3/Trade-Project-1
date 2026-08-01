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
