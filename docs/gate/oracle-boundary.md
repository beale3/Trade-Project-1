# Oracle / escalate boundary — HELM (`trade`)

Protocol 14, authored **at founding**, 🔒 **re-authored 2026-08-01 for the personal-tool pivot
(D-TRADE-020, LL-19 — re-author, not patch).** One row per seat: **what it certifies mechanically**
(the leg's ACTUAL assertion, fail-closed) · **what stays HUMAN and escalates** · **who authors the rule /
who builds the oracle** (never the seat judged) · **tier**.

**Admission test (LL-49):** a duty is certified **only if a seat OTHER than the one judged can produce a
reproducible NEGATIVE CONTROL** — "show me the input this green would reject." No live negative control
⇒ HUMAN. Default HUMAN; certified is earned. **Tiers:** ORACLE (mechanical veto) · PARTIAL (checkable
sliver + human core) · VERIFIER (audits oracles) · HUMAN (judgment only). **GA owns the standing
coverage + soundness + boundary-honesty audit of this table.**

| Seat | Tier | Certified (leg's actual assertion · fail-closed) | HUMAN + escalates | Rule author / oracle builder |
|---|---|---|---|---|
| **Program Lead** | HUMAN | gate exit codes on its own commits; ID-collision checks on registers it allocates | sequencing · wave scoping · **synthesis of others' findings** (audited by GA) · any lock (present-then-WAIT) | Lead authors / GA + QA judge |
| **Principal Architect** | PARTIAL | Phase-1 design-ADR structural checks (module-boundary conformance, `adr_reference` presence) | approach soundness · "is this the right module split" | Architect authors constraints / DevOps wires · GA audits |
| **QA** | VERIFIER | re-runs every armed leg on exit codes in its own clone; **re-runs every backtest CV script end-to-end and confirms the numbers reproduce** | "is coverage sufficient for the risk" | QA authors coverage / QA runs |
| **Governance & Audit** | VERIFIER | rule-adherence / evidence checks (propagation-list present, register updated same-commit, AIQ's independent validation confirmed to have run) | severity calls · boundary-honesty verdicts | GA authors / GA runs |
| **SecOps** | ORACLE (scope narrowed) | **no-secret leg K** (committed key pattern / key-in-logs FAILS); **provider-taint leg T** (provider SDK/host outside its module FAILS) | "is the personal-tier account actually compliant" (light confirm, not the prior commercial-tier gate) | SecOps authors denylist / DevOps wires |
| Backend-API | **N/A, dropped** — no external API surface | — | — | — |
| **SDE1** (data ingestion + Supabase storage) | PARTIAL | schema-conformance / freshness legs on ingested market/options data; a malformed or stale row FAILS | "is the universe construction right" · data-source-selection judgment | SDE1 authors / DevOps wires · QA judges |
| Frontend-Web | **N/A, dropped** — no web surface for a Python script/tool | — | — | — |
| **DevOps** | VERIFIER | the gate runner (exit-code honesty); wires every seat's oracle legs; secret-scan | infra tradeoffs | DevOps authors / DevOps runs |
| **AI/ML** | VERIFIER *(re-scoped from HUMAN)* | **runs the walk-forward-CV pipeline and reports pass/fail against the pre-registered bar** (beats naive baseline OOS) — mechanical once the bar is set; a component that doesn't clear CV FAILS by construction | choosing which candidate components to test at all (judgment); interpreting a marginal/fragile result (LL-42/47) | AI/ML authors the pipeline / **AIQ independently re-derives + audits every result** (builder ≠ judge) |
| **AI Quality** | VERIFIER | independently re-derives each CV result from raw data (not from AI/ML's summary — LL-34); catch-matching against the pre-registered bar; voids on any seed-sensitivity or contamination finding (LL-47) | "is the pre-registered bar itself the right bar" | AIQ authors / AIQ runs · GA audits independence |
| **FinOps** | PARTIAL *(re-scoped from ORACLE, SaaS-scale)* | the personal spend guard: a call that would breach the daily cap is BLOCKED (mechanical) | "is the cap itself set sensibly" · pricing judgment | FinOps authors the cap / DevOps wires |
| Legal & Privacy | HUMAN *(de-risked — not urgently seated)* | — (no mechanical leg needed for a light confirmatory check) | `<4.3>` — is a personal trading tool exempt from adviser-registration concerns (very likely yes, but stays HUMAN) | Director/light-touch Legal review |
| **Data Engineer** | PARTIAL | universe-construction + options-chain-data-availability legs (a name without a real, liquid options chain is excluded — mechanical filter) | which universe-construction criteria are right | Data-Eng authors / DevOps wires · QA judges |
| **Design Lead** ("Designer") | HUMAN | — (mandate mostly evaporates; no UI surface to certify) | any future UI surface, if one is ever wanted | — |

**Residue named to HUMAN:** `<4.3>` regulatory read · which candidate screener components are worth
testing at all · whether the pre-registered directional-correctness bar is the right bar (vs. full P&L,
Phase 2) · all severity and boundary-honesty calls. Every one of these **escalates to the Director**.

**Seeded GA coverage-audit job (unchanged):** on every rule-set change and on staleness, GA audits this
table for coverage, soundness, and boundary-honesty — including confirming the AI/ML↔AIQ builder≠judge
split is actually being exercised, not just documented.
