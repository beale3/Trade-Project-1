# Gate spec — HELM (`trade`)

🔒 **Re-authored 2026-08-01 for the personal-tool pivot (D-TRADE-020, LL-19).** One runner, ordered,
**exit-code-honest**. Every leg is either **ARMED** (proven to FAIL on a planted negative control) or an
**exit-visible SKIP**. A gate that cannot fail is worse than no gate (LL-48).

## Stack commands (`<3.5>` — Python, not the superseded Node/TS/Fastify/React default)
| # | Leg | Command (planned) | Arms at | Now |
|---|---|---|---|---|
| 1 | lint/type-check | `ruff`/`mypy` or equivalent over the Python package | Phase-1 scaffold | ⏸ SKIP (no tree yet) |
| 2 | unit tests | `pytest` on indicator/scoring/backtest logic (mirrors the options screener's own existing validation — synthetic-data unit tests for indicator math) | Phase-1 scaffold | ⏸ SKIP |
| 3 | **CV reproducibility** | `run_analysis.py`-style script re-derives every reported backtest number from raw data end-to-end (the pattern already used in all 4 equity studies) | P1-3 | ⏸ SKIP |
| 4 | secret-scan | plant a fake key pattern → RED | CI, from day one | ⏸ SKIP |
| — | CI | same runner + secret-scan + dep-audit | Phase-1 scaffold | ⏸ SKIP |

**Dropped (superseded, LL-19):** `tsc`, Node build, RLS/tenant-isolation leg, transport smoke on
`apps/api`, drift guard on a service contract — none apply; no service, no multi-tenant DB, no API.

## Project-specific armed legs (re-scoped)
| Leg | Assertion | Negative control | Arms | Now |
|---|---|---|---|---|
| **G · spend guard** *(replaces leg M — money-truth chokepoint, LL-19 re-author)* | a Massive/SEC-API.io call that would breach the daily spend cap is BLOCKED before firing | plant a call sequence that would exceed the cap → BLOCKED, not silently allowed | Phase-1 data-ingestion | ⏸ SKIP |
| **K · no-secret** | a committed key pattern (Massive/Polygon, SEC-API.io, Supabase service_role/DB password) or key-in-logs FAILS | plant a fake key in a tracked file → leg RED | Phase-1 scaffold | ⏸ SKIP |
| **T · provider-taint** | a provider SDK/host used outside its sanctioned data-ingestion module FAILS | plant a Massive import outside that module → leg RED | Phase-1 scaffold | ⏸ SKIP |
| **C · compliance** | (armed only if Legal's light `<4.3>` review finds something to enforce) | — | if needed | ⏸ SKIP — very likely stays unarmed given `<4.3>`'s de-risking |
| **O · oracle legs** | the §10 per-seat oracle legs (`oracle-boundary.md`) | per row | each seat's Phase-1 task | ⏸ SKIP |

## §9 build-phase components (re-scoped — see PROJECT-CONFIG §4 for the full adopt/drop table)
**Kept, lighter:** B1 (design ADR, not full A0/A6 service architecture) · B3 (lint/test, no import-
boundary-as-4-lane-cut) · B5 (secrets discipline) · B6 (wave-entry, lightweight) · B8 (builder≠judge —
this IS the AI/ML↔AIQ CV-audit split). **Dropped:** B2 (SaaS reliability pillars, mostly N/A) · B4
(replaced by the spend guard) · B7 (no CX surface) · B9 (no market to validate).

**Rule of green (unchanged):** no leg reports green from an unarmed state — SKIP until armed and proven
to bite. QA re-runs the full gate + every CV script on each phase HEAD in its own clone before the next
phase unblocks.
