# DevOps — gate-harness + Phase-1 repo/CI design-of-record (DESIGN ONLY)

> 🔒 **Re-authored 2026-08-01 for the personal-tool pivot (D-TRADE-020, LL-19 — re-author, not patch).**
> The prior version of this document (Node/TS · Fastify · React · Docker-Postgres · RLS/tenant-isolation ·
> the SaaS-scale money-truth chokepoint) **no longer describes HELM** and is deleted below, not parked —
> `<3.5>` drops Node/Fastify/React entirely; there is no service, no web surface, no multi-tenant DB.
>
> **Still DESIGN, not build.** The Architect's `ADR-0001-phase1-validation-tool.md` landed 2026-08-01
> (Status: PROPOSED) — its own **P-1 precondition confirms my hold was correct, not resolved**: *"No-build
> stands until the Director explicitly confirms Phase-1 quant-research build is outside D-TRADE-010's
> intent... no seat writes production code until P-1 clears."* **I hold on creating actual repo/CI files
> (`pyproject.toml`, `.github/workflows/*`, `scripts/gate/*`) until P-1 clears** — this document is a
> one-shot execution plan for the moment it does. What I *can* and do here: **co-sign the ADR's
> non-negotiables** (§12 requires it before wave-entry GO) and **re-align this design's module names to the
> now-Architect-confirmed layout** (§4 of the ADR) — both design-review actions, not build. See §F/§H.

Author: DevOps seat (clone `Trade - DevOps`). Reviewers on Phase-1 GO: Lead (infra tradeoffs) · QA
(re-runs the harness + every CV script) · GA (leg-coverage audit) · SecOps (owns leg K/T rule content,
already authored — I wire it, not re-derive it) · FinOps (owns the spend-guard cap values) · **Architect
(ADR-0001 owner — module boundaries, lane cut, the 9 non-negotiables I wire as legs)**.

---

## §A · Validated environment (re-verified 2026-08-01, THIS session — LL-1)
Independently confirmed, not taken on the Lead's word alone (verify-don't-attest, §Routines).

| Item | Validated value | Note |
|---|---|---|
| OS / arch | Windows 11 (10.0.26200) · AMD64 | dev host is Windows; CI (if any) should still be OS-portable Python |
| git | ✅ 2.55.0.windows.2, clone identity `Mähnbach <noreply@mahnbach.com>` | unchanged from prior verification |
| **Python** | ✅ **3.12.10** at `C:\Users\beale\AppData\Local\Programs\Python\Python312\python.exe`, resolves on PATH in **this** session (not just the Lead's) | closes the earlier D-TRADE-017 "is this session-specific?" open question — Python was present the whole time; only Node/Docker/pnpm/gh are genuinely absent |
| pip | ✅ 26.1.2 | — |
| **Key libs (importable now)** | pandas 3.0.3 · numpy 2.5.1 · scipy 1.18.0 · yfinance 1.5.2 · matplotlib 3.11.1 · requests 2.34.2 | matches every library the existing screener/backtest/study scripts already use — **zero new-dependency risk for the core analysis stack** |
| ruff / mypy / pytest | 🟡 **not yet installed** (`No module named ruff/mypy/pytest`) | trivial `pip install ruff mypy pytest`, $0, no PATH/admin friction unlike Node/Docker — this is the one real Phase-1-scaffold prerequisite |
| Node / npm / npx / pnpm / docker / gh | 🔴 still absent (D-TRADE-017, unchanged) | **superseded, not fixed** — `<3.5>` drops the entire Node/Docker stack; only re-verify if a non-Python piece is ever pulled in |
| Referenced external artifacts | `Downloads/rolling_watchlist (3).py` ✅ present; `{regime,catalyst,short-interest,float}-study/` ✅ all 4 present at `C:\Users\beale\*-study\`; `tools/rolling_watchlist.py` ✅ already in this repo | 🟢 **UPDATED 2026-08-04 (D-TRADE-028):** the earlier "options-screener/0DTE-engine ZIP not yet located" row is stale — canonical `<1.1>` confirms that search was for an artifact that never needed finding (P-2 is MOOT, not resolved-by-search); the real scanner has been `tools/rolling_watchlist.py`, in-repo, the whole time (also the D-TRADE-023 dashboard's backend) |
| Ports | N/A — no service, no transport leg (`<3.3>` N/A, gate-spec drops transport smoke) | dropped, not carried forward |

---

## §B · Gate-harness design (VERIFIER tier — unchanged mandate, lighter mechanism)
Same discipline as before — **exit-code-honest**, never a piped-tail grep; every leg **ARMED** (proven to
FAIL on a planted negative control) or **exit-visible SKIP**; LL-48's done-bar (a leg never seen to fail is
unproven) still governs.

### B.1 Runner shape (re-scoped: pure Python, no Node dependency)
- **Single source of truth:** `scripts/gate/run.py` (stdlib + at most `ruff`/`mypy`/`pytest` as
  subprocesses), invoked as `python scripts/gate/run.py` or a thin `gate` console-script entry point once
  `pyproject.toml` exists. No `npx`/Node dependency anywhere in the harness — the earlier design's
  cross-platform-via-Node choice is moot now that the whole stack is Python.
- **Leg registry:** `scripts/gate/legs/*.py`, each exposing `{id, name, arms_at, status, run(), negative_control}`.
- **Status vocabulary unchanged:** `ARMED` / exit-visible `SKIP` (never a vacuous green); runner exits
  non-zero **iff** any ARMED leg fails.
- **Output:** a table + machine-readable block; human reads the table, CI (if/when adopted) reads the exit code.

### B.2 The done-bar (LL-48, unchanged principle)
Not done until BOTH: (1) `gate` exits 0 on the empty/scaffold tree, every real leg SKIP or armed-and-green;
(2) a **planted violation** (a fake secret, or a provider import outside its sanctioned module) makes it
exit non-zero. Fixture is planted, shown to bite, then reverted — never left in tracked history.

### B.3 Leg schedule — re-scoped to the re-authored `gate-spec.md`
| Leg | Tier | Arms at | Assertion |
|---|---|---|---|
| lint/type-check (`ruff`+`mypy`) | DevOps/B3 | Phase-1 scaffold | style + type errors FAIL |
| unit tests (`pytest`) | DevOps/B3 | Phase-1 scaffold | indicator/scoring-math unit tests (mirrors the screener's own existing synthetic-data tests) |
| **leg 3 · CV reproducibility** | QA VERIFIER (I wire, QA runs) | P1-3 | a `run_analysis.py`-style script re-derives every reported backtest number from raw data end-to-end; a number that doesn't reproduce FAILS |
| **leg K · secret-scan** | SecOps ORACLE (DevOps wires) | Phase-1 scaffold, day one | SecOps's fully-authored 7-pattern denylist (`docs/security/key-denylist.md`) — see §C, I do not re-derive it |
| **leg T · provider-taint (static)** | SecOps ORACLE (DevOps wires) | Phase-1 scaffold | SecOps's sanctioned-module rule (`docs/security/tos-taint-review.md`) adapted to the Python module layout — see §D |
| **leg G · spend guard** | FinOps PARTIAL (DevOps wires) | Phase-1 data-ingestion | a call that would breach the daily cap is BLOCKED, not silently allowed — see §E (⚠️ FinOps's spec needs a light re-author first) |
| **leg C · compliance** | Legal HUMAN | only if Legal's light `<4.3>` review finds something to enforce | very likely stays unarmed (canonical `<4.3>` de-risked) |
| **leg O · per-seat oracle legs** | per row | each seat's Phase-1 task | DevOps wires each; GA audits coverage |

**Dropped, not carried forward (LL-19):** `tsc`, any Node/Fastify build leg, RLS/policy-lint, tenant-isolation,
transport smoke, drift guard on a service contract, Docker-based local DB. None apply — no service, no
multi-tenant DB, no API surface.

---

## §C · Leg K — secret-scan (wiring the ALREADY-AUTHORED SecOps spec, not a new design)
SecOps fully authored this (`docs/security/key-denylist.md`, K0–K6, each with a value-bearing pattern +
planted negative control + the exact placeholder that must stay GREEN). **My job is mechanical: encode it,
not re-derive it** (builder ≠ judge — SecOps authors, DevOps wires, GA audits coverage, QA re-runs).

- **Tool:** **gitleaks** (or an equivalent regex/entropy scanner scriptable in CI-less Python via a
  `pre-commit` hook + a standalone `python scripts/gate/legs/secret_scan.py` for local/CI-less runs — no
  CI service is assumed yet for a personal repo, so the leg must run **locally on demand**, not only in a
  GitHub Action). Custom rules = SecOps's K1–K6 + K0 backstop, verbatim.
- **Two structural rules from SecOps's spec, preserved exactly:** (1) value-bearing, not name-bearing — the
  `.env.example` placeholders and `.mcp.json`'s `${SUPABASE_ACCESS_TOKEN}` indirection must stay GREEN; (2)
  no `.env`/`.env.*` (except `.env.example`) is ever git-tracked, checked directly, not just via `.gitignore`.
- **Negative controls:** SecOps's planted-fake values (K1–K6, K0) — I plant each, prove RED, revert. All
  fake/format-only per their spec; never a real secret.
- **🟢 UPDATED 2026-08-04 (D-TRADE-026/027, SecOps confirm task):** K6 tightened from "issuer TBD" to a
  **confirmed** SEC-API.io key — now two patterns, not one: (a) env-name assignment (unchanged), (b) a new
  **in-URL token match** on the confirmed live host: `api\.sec-api\.io/[^\s"']*[?&]token=[A-Za-z0-9_-]{20,}`
  — both to wire, both with their own negative control. SecOps also flagged a live token found exposed in
  plaintext **outside this repo** (`C:\Users\beale\float-study\log_pull.txt`) — out of leg K's reach (repo-
  scoped only) and already escalated by SecOps to the Director for rotation; noted here for awareness, not
  mine to act on.
- **Confirmed 2026-08-01 (unchanged):** `.gitignore` blocks `.env`/`.env.*` (`!.env.example` only);
  `.env.example` is placeholders-only. ✅

## §D · Leg T — provider-taint, static (CONFIRMED module layout — ADR-0001 §4)
SecOps's rule (`tos-taint-review.md`) is written in `apps/web` / "Lane 2" terms from the superseded SaaS
cut — the **substance** (a provider SDK/credential confined to one sanctioned module) still applies. The
Architect's ADR-0001 §4 now **confirms** the concrete module names (my earlier per-provider draft below is
superseded by the single-module rule the ADR states explicitly):

| Provider | Sanctioned module (ADR-0001 §4, confirmed) | Leg T assertion |
|---|---|---|
| Massive/Polygon (`api.polygon.io` **and** `api.massive.com` — both hosts, per SecOps's rebrand finding) | `helm/ingest/` — **the ONLY place any provider SDK/host may appear** (ADR-0001 §4, verbatim) | an import of the Massive/Polygon client, or a literal call to either host, **outside** `helm/ingest/` FAILS |
| SEC-API.io / EDGAR | `helm/ingest/` (same module — ADR-0001 does not split providers into separate files, one sanctioned package for all provider adapters) | likewise confined |
| Supabase (`@supabase-py`/`postgrest`, service_role/`DATABASE_URL`) | `helm/storage/` (ADR-0001 §4 — "name aligns with DevOps's in-flight harness draft," confirming my earlier guess) | a service_role reference outside `helm/storage/` FAILS; **no `apps/web` carve-out needed — there is no web surface** |

**Two additional import-boundary rules from ADR-0001 §4 (mine to wire as gate legs, Lane E):**
1. `helm/screener/` (AI/ML's lane) **may not import a provider SDK directly** — only through the
   `helm/ingest/` adapter interface. A direct provider import in `helm/screener/` FAILS.
2. `helm/validation/audit/` (AIQ's lane) **may not import `helm/validation/engine`'s outputs** — it
   re-derives from raw data. This is builder≠judge (NN-3) encoded as an import rule, not just a review
   norm — a leg that detects an `audit` → `engine`-results import FAILS. This is the harness's most
   important non-negotiable to get right: it is the mechanical backbone of the whole CV-audit split.

**Negative control:** plant a Massive/Polygon import in, e.g., a top-level analysis script outside the
ingestion module → leg RED. Same fixture doubles as the harness done-bar (§B.2).

## §E · Leg G — spend guard (✅ RESOLVED — wired against FinOps's re-authored `governor-spec.md`)
FinOps re-authored the spec at personal scale (`ab23303`, absorbed here 2026-08-01) — the earlier flag in
this section is closed. FinOps: authors the cap logic + recommended posture. **DevOps wires §2's mechanical
leg.** Cap **values** stay Director-locked (`<2.1>` tier confirmations pending) — the mechanism below does
not need them to be built and tested.

- **Assertion (§2, unchanged from gate-spec leg G):** before a call to a provider with any per-use/overage
  pricing dimension, check **today's running count/estimated-$ for that provider against a daily cap**; a
  call that would **breach** it is **BLOCKED** (never fires) and the block is logged with why (which
  provider, which cap, today's tally) — no silent skip.
- **Cap expression, not a baked number (LL-61):** `min(quota_calls, $_ceiling)` — "whichever bites first."
  SEC-API.io's measured 50 GB/mo → $0.30/GB overage (`cost-model.md` §2.3) is the one **real, current**
  overage line; Massive's paid tiers are flat, so its cap matters mainly on the free/basic rate limit.
- **Module home — CONFIRMED by ADR-0001 §4:** `helm/spend/` — "the spend-guard wrapper around every
  `ingest` call" (owned FinOps · SDE1, DevOps wires the leg). Every call in `helm/ingest/` routes through
  the `helm/spend/` check first — this doubles as an import-boundary leg (an `ingest` provider call not
  wrapped by `helm/spend/` is a gap, not just a style issue).
- **State/storage — explicitly left to DevOps/SDE1 by the spec (§4), decided here:** a **flat JSON file**
  (e.g. `.gate/spend-tally.json`, gitignored — it's runtime state, not config) for Phase 1, keyed by
  `(provider, UTC date) → {calls, est_$}`. Chosen over a Supabase table row because it needs **zero new
  schema/migration work** to stand up and there is **no concurrency to coordinate** (single user, one
  process at a time, per §1/§4) — a Supabase row is a natural *later* upgrade (visibility from anywhere) but
  not a Phase-1 requirement. **Read-before-call, write-after-call**; on a write failure, treat the day as
  uncounted-unsafe and block rather than assume zero spend (§4's conservative-default recommendation).
- **No ledger/idempotency/reconciliation** — correctly dropped per §5; a single counter increment per call
  is sufficient at this scale.
- **Negative control (§2, the actual admission-test artifact — reproducible by QA or the Director):** drive
  the day's tally to the cap, fire one more call → **BLOCKED**, not silently allowed. I plant this as a
  scripted test (seed the tally file at `cap − 1`, assert the next call raises/blocks and does not reach
  the provider), QA re-runs it on phase exit.
- **Light co-check (§6, right-sized):** FinOps confirms the block behavior matches §2; one other seat (QA
  or the Director) reproduces it — no multi-seat sign-off matrix needed at this scale.

---

## §F · Phase-1 DoD (from stage-plan P1-4) — ready-to-execute, HELD on ADR-0001's own P-1
Restated with validated values baked (§A) and confirmed module names (ADR-0001 §4). **My reading: NOT yet
dispatchable** — see the banner at top. Ready to execute the moment **P-1 clears** (Director confirms
Phase-1 build is outside D-TRADE-010's intent) **and** wave-entry GO lands (§12, all co-signs + Director GO).

| Task | Owner | DoD (concrete) |
|---|---|---|
| P1-4a install ruff/mypy/pytest | DevOps | `pip install ruff mypy pytest` (or pin in `pyproject.toml`'s dev deps); $0, no PATH friction expected (unlike Node/Docker) |
| P1-4b repo scaffold | DevOps | `pyproject.toml` (deps = the already-confirmed pandas/numpy/scipy/yfinance/matplotlib/requests + ruff/mypy/pytest), package layout **CONFIRMED by ADR-0001 §4:** `helm/{ingest,universe,screener,validation/{engine,audit},storage,spend}` |
| P1-4c gate harness | DevOps | `scripts/gate/run.py` + `scripts/gate/legs/*.py`; exits 0 on the scaffold tree; **a planted violation makes it FAIL** (LL-48 done-bar) |
| P1-4d leg K wiring | DevOps ← SecOps spec (already authored) | SecOps's 7 patterns encoded; each of the 7 negative controls shown to bite |
| P1-4e leg T wiring | DevOps ← SecOps rule (adapted, §D) | planted cross-module provider import → RED |
| P1-4f leg G skeleton | DevOps ← FinOps's re-authored spec (delivered, §E) | flat-file tally + cap-check-and-block mechanism; cap **value** stays Director-locked, never invented here |
| P1-4g Supabase persistence for scan/backtest history | **SDE1** (not DevOps — noted for coordination only) | co-owned task per stage-plan P1-4; DevOps's role is the surrounding scaffold, not the schema |

**Exit:** `gate` green on the scaffold tree; leg K/T armed + negative controls shown to bite; leg 3
(CV-reproducibility) and leg G remain SKIP until P1-3/P1-ingestion respectively; QA phase-exit re-run.

## §G · Open items / flags surfaced to the Lead (this report)
1. 🟡 **Authorization — now precisely scoped by ADR-0001's own P-1, not just my reading.** ADR-0001
   (PROPOSED) states directly: *"No-build stands until the Director explicitly confirms Phase-1
   quant-research build is outside D-TRADE-010's intent... no seat writes production code until P-1
   clears."* This is no longer just my inference from stage-plan's hedge — the Architect's own precondition
   confirms it. I hold on creating actual files (`pyproject.toml`, `scripts/gate/**`) until P-1 clears
   **and** the ADR's wave-entry GO (§12: all co-signs + Director) lands.
2. 🟢 **RESOLVED — FinOps re-authored `governor-spec.md` at personal scale** (`ab23303`); leg G's wiring
   plan is now fully specified against it (§E), including the storage choice (flat JSON tally file).
   Cap **values** remain Director-locked pending `<2.1>` tier confirmations, but the mechanism doesn't
   need them to be built/tested against the negative control.
3. 🟢 **Toolchain, mostly resolved.** Python + every core analysis library are confirmed present and
   importable in **this** session (not just the Lead's) — D-TRADE-017's Node/Docker gap is genuinely
   superseded for Phase 1, not just claimed superseded. Only `ruff`/`mypy`/`pytest` need a trivial install.
4. 🟡 **DB baseline still open** — unchanged from my last report; Lead is routing capture to the Director/
   an interactive Lead-clone session. No action needed from me.

---

## §H · DevOps co-sign — ADR-0001 §12 (design-review action, not build)
Per ADR-0001 §12, DevOps is a required co-signer before wave-entry GO. This is a review action (confirming
I will carry these as legs once P-1 clears), not code — consistent with the hold above.

- **I co-sign carrying, as gate legs once armed:**
  - **NN-7** (no secret in repo / provider taint) — leg K (§C, SecOps's spec, ready to wire verbatim) + leg
    T (§D, now module-confirmed) + the two additional import-boundary rules (`screener`→provider-SDK,
    `audit`→`engine`-outputs) ADR-0001 §4 adds beyond the original NN-7 text.
  - **NN-8** (spend guard block-on-breach) — leg G (§E, wired against FinOps's confirmed spec).
  - **Lane E's "gate legs + import-boundary" non-negotiable (§12)** — the runner itself (§B), exit-code
    honesty, and the done-bar (§B.2).
- **I do NOT co-sign, and flag as not mine to carry:** NN-1 (no-lookahead, AIQ/DevOps-leakage-assert per
  the table — the *leakage assertion* is AIQ's re-derivation, not a DevOps leg; I wire the import-boundary
  half only, already counted under NN-7 above), NN-2/NN-3 (AI/ML·AIQ's CV-bar/re-derivation), NN-4
  (gate-flag conformance — jointly SDE1/DevOps per the ADR table; I will wire the conformance check but the
  correctness of the `_gates`↔verdict mapping is SDE1's domain to define), NN-5/NN-6 (Data-Eng/SDE1), NN-9
  (QA reproducibility).
- **Readiness note:** every leg I'm co-signing already has a concrete design (§B–§E) and a stated negative
  control — none are placeholders. The only thing standing between this co-sign and an armed leg is P-1 +
  wave-entry GO, not further design work on my end.

**DevOps ▸ co-signed 2026-08-01 (design-review, pre-P-1)**
