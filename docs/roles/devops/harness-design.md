# DevOps — gate-harness + Phase-1 repo/CI design-of-record (DESIGN ONLY)

> 🔒 **Re-authored 2026-08-01 for the personal-tool pivot (D-TRADE-020, LL-19 — re-author, not patch).**
> The prior version of this document (Node/TS · Fastify · React · Docker-Postgres · RLS/tenant-isolation ·
> the SaaS-scale money-truth chokepoint) **no longer describes HELM** and is deleted below, not parked —
> `<3.5>` drops Node/Fastify/React entirely; there is no service, no web surface, no multi-tenant DB.
>
> **Still DESIGN, not build.** Per `stage-plan.md`'s own flag: D-TRADE-010 (no-build) is the Director's
> ruling; the Lead's reading that Phase-1 script/scaffold work "plausibly falls outside its intent" is an
> explicit **recommendation pending Director confirmation, not decided** — and a Wave-Entry Gate (Architect's
> P1-0 design ADR + Director GO) still applies regardless. **I hold on creating actual repo/CI files
> (`pyproject.toml`, `.github/workflows/*`, `scripts/gate/*`) until one of those two lands** — this document
> makes that a one-shot action the moment either does. See §F.

Author: DevOps seat (clone `Trade - DevOps`). Reviewers on Phase-1 GO: Lead (infra tradeoffs) · QA
(re-runs the harness + every CV script) · GA (leg-coverage audit) · SecOps (owns leg K/T rule content,
already authored — I wire it, not re-derive it) · FinOps (owns the spend-guard cap values).

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
| Referenced external artifacts | `Downloads/rolling_watchlist (3).py` ✅ present; `{regime,catalyst,short-interest,float}-study/` ✅ all 4 present at `C:\Users\beale\*-study\`; the options-screener ZIP and 0DTE-backtest-engine ZIP **not yet located** (stage-plan already flags "location TBD") | read-only check, informs P1-1/P1-2 (Data-Eng/AI-ML), not my lane to ingest |
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
- **Negative controls:** SecOps's 7 planted-fake values (K1–K6, K0) — I plant each, prove RED, revert. All
  fake/format-only per their spec; never a real secret.
- **Confirmed 2026-08-01 (unchanged):** `.gitignore` blocks `.env`/`.env.*` (`!.env.example` only);
  `.env.example` is placeholders-only. ✅

## §D · Leg T — provider-taint, static (adapting SecOps's rule to the Python module layout)
SecOps's rule (`tos-taint-review.md`) is written in `apps/web` / "Lane 2" terms from the superseded SaaS
cut — the **substance** (a provider SDK/credential confined to one sanctioned module) still applies; only
the concrete module names change under `<3.5>`'s Python layout (final names await Architect's P1-0 ADR):

| Provider | Sanctioned module (draft, Architect confirms at P1-0) | Leg T assertion |
|---|---|---|
| Massive/Polygon (`api.polygon.io` **and** `api.massive.com` — both hosts, per SecOps's rebrand finding) | the data-ingestion module (e.g. `helm/ingest/market_data.py`) | an import of the Massive/Polygon client, or a literal call to either host, **outside** that module FAILS |
| SEC-API.io / EDGAR | the data-ingestion module (e.g. `helm/ingest/filings.py`) | likewise confined |
| Supabase (`@supabase-py`/`postgrest`, service_role/`DATABASE_URL`) | the storage module (e.g. `helm/storage/supabase_client.py`) | a service_role reference outside that module FAILS; **no `apps/web` carve-out needed — there is no web surface**, so the confinement is simpler than the original SaaS design (one sanctioned module per provider, not "server-only vs. client bundle") |

**Negative control:** plant a Massive/Polygon import in, e.g., a top-level analysis script outside the
ingestion module → leg RED. Same fixture doubles as the harness done-bar (§B.2).

## §E · Leg G — spend guard (⚠️ flag: FinOps's current spec is pre-pivot, needs a light re-author)
Canonical `<3.2>` and the re-authored `gate-spec.md` both describe leg G as **lightweight**: "a call that
would breach the daily cap is BLOCKED before firing" — a cap-check + block, not the SaaS-scale
append-only-ledger/idempotency/billing-reconciliation machinery.

**What exists today** (`docs/finops/governor-spec.md`) is still written at that **superseded SaaS scale**
(per-tenant caps, transactional ledger rows, billing reconciliation vs. a provider invoice, arms at "W1
with the money-truth chokepoint") — it predates D-TRADE-020 and canonical `<3.2>` explicitly calls that
machinery **"overbuilt"** for personal scale now. **I do not re-scope FinOps's spec myself (not my lane —
FinOps authors caps, I only wire); flagging this to the Lead (§F) so FinOps re-authors a right-sized
version** before I wire leg G for real. Until then, my wiring skeleton is deliberately minimal and
mechanism-only:

- **Mechanism (mine to wire once FinOps confirms the light-scale shape):** before a priced Massive/
  SEC-API.io call, read today's tally (a simple counter — a local file, or a Supabase table row, TBD with
  FinOps/SDE1), compare projected post-call spend to a single `K_day` cap (Director-locked value), **REFUSE
  (raise, don't call) if it would cross** — no per-tenant layer (single user, `<1.2>`), no billing-
  reconciliation-vs-invoice oracle (personal scale, FinOps's call whether that's still worth it).
- **Negative control:** drive the tally to `K_day − ε`, attempt a call that would cross → REFUSED, not silently allowed.

---

## §F · Phase-1 DoD (from stage-plan P1-4) — ready-to-execute, HELD pending Wave-Entry Gate
Restated with validated values baked (§A). **My reading: NOT yet dispatchable** — see the banner at top.
Ready to execute the moment either (a) Architect's P1-0 design ADR + Director GO lands, or (b) the Lead/
Director explicitly confirms light scaffold-writing is in-bounds under the current D-TRADE-010 reading.

| Task | Owner | DoD (concrete) |
|---|---|---|
| P1-4a install ruff/mypy/pytest | DevOps | `pip install ruff mypy pytest` (or pin in `pyproject.toml`'s dev deps); $0, no PATH friction expected (unlike Node/Docker) |
| P1-4b repo scaffold | DevOps | `pyproject.toml` (deps = the already-confirmed pandas/numpy/scipy/yfinance/matplotlib/requests + ruff/mypy/pytest), a package layout **per Architect's P1-0 module-boundary ADR** (draft: `helm/{ingest,screener,validate,storage}` — final names await P1-0) |
| P1-4c gate harness | DevOps | `scripts/gate/run.py` + `scripts/gate/legs/*.py`; exits 0 on the scaffold tree; **a planted violation makes it FAIL** (LL-48 done-bar) |
| P1-4d leg K wiring | DevOps ← SecOps spec (already authored) | SecOps's 7 patterns encoded; each of the 7 negative controls shown to bite |
| P1-4e leg T wiring | DevOps ← SecOps rule (adapted, §D) | planted cross-module provider import → RED |
| P1-4f leg G skeleton | DevOps ← **FinOps re-authored spec (not yet delivered, flagged below)** | cap-check-and-block mechanism; cap **value** stays Director-locked, never invented here |
| P1-4g Supabase persistence for scan/backtest history | **SDE1** (not DevOps — noted for coordination only) | co-owned task per stage-plan P1-4; DevOps's role is the surrounding scaffold, not the schema |

**Exit:** `gate` green on the scaffold tree; leg K/T armed + negative controls shown to bite; leg 3
(CV-reproducibility) and leg G remain SKIP until P1-3/P1-ingestion respectively; QA phase-exit re-run.

## §G · Open items / flags surfaced to the Lead (this report)
1. 🟡 **Authorization ambiguity (holding on it, not guessing past it).** stage-plan.md itself flags
   D-TRADE-010's applicability to Phase-1 script/scaffold work as the Lead's *recommendation*, not a
   Director ruling, and still requires the Wave-Entry Gate (Architect P1-0 ADR + Director GO). I am
   holding on creating actual files (`pyproject.toml`, `scripts/gate/**`) until one of those two lands —
   this document is the one-shot plan for when it does.
2. 🟡 **FinOps's `governor-spec.md` is pre-pivot (SaaS-scale)** — canonical `<3.2>` calls that machinery
   overbuilt for a personal spend guard. I can't wire leg G for real against a stale spec; flagging for
   FinOps to re-author a light version (not mine to rewrite — builder ≠ judge; FinOps authors caps).
3. 🟢 **Toolchain, mostly resolved.** Python + every core analysis library are confirmed present and
   importable in **this** session (not just the Lead's) — D-TRADE-017's Node/Docker gap is genuinely
   superseded for Phase 1, not just claimed superseded. Only `ruff`/`mypy`/`pytest` need a trivial install.
4. 🟡 **DB baseline still open** — unchanged from my last report; Lead is routing capture to the Director/
   an interactive Lead-clone session. No action needed from me.
