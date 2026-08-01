# Oracle / escalate boundary — HELM (`trade`)

Protocol 14, authored **at founding** (the duty binds from founding; each **leg arms at that seat's build
wave**). One row per seat: **what it certifies mechanically** (the leg's ACTUAL assertion, fail-closed —
never more than the leg asserts, LL-50) · **what stays HUMAN and escalates** · **who authors the rule /
who builds the oracle** (never the seat judged) · **tier**.

**Admission test (the binding entry gate, LL-49):** a duty is in the certified column **only if a seat
OTHER than the one judged can produce a reproducible NEGATIVE CONTROL** — a concrete input that *should*
be rejected and *is*. The enforcing question: **"show me the input this green would reject."** No live
negative control ⇒ the duty is **HUMAN and escalates**. Default is HUMAN; certified is earned.
**Tiers:** ORACLE (mechanical veto) · PARTIAL (checkable sliver + human core) · VERIFIER (audits oracles)
· HUMAN (judgment only). **GA owns the standing coverage + soundness + boundary-honesty audit of this table.**

| Seat | Tier | Certified (leg's actual assertion · fail-closed) | HUMAN + escalates | Rule author / oracle builder |
|---|---|---|---|---|
| **Program Lead** | HUMAN | gate exit codes on its own commits; ID-collision checks on registers it allocates | sequencing · wave scoping · **synthesis of others' findings** (audited by GA, never self) · any lock (present-then-WAIT) | Lead authors / GA + QA judge |
| **Principal Architect** | PARTIAL | A0/A6 structural checks that are mechanical (contract/schema drift, `adr_reference` presence) | approach soundness · boundary/tradeoff judgment · "is this the right structure" | Architect authors constraints / DevOps wires · GA audits |
| **QA** | VERIFIER | re-runs every armed leg on exit codes in its own clone; reproduces the planted negative control | "is coverage sufficient for the risk" (a judgment) | QA authors coverage / QA runs (it is the verifier, not self-judged on its own code) |
| **Governance & Audit** | VERIFIER | rule-adherence / evidence checks that are mechanical (propagation-list present, register updated same-commit, validation-ran) | severity calls · "is this synthesis faithful" · boundary-honesty verdicts | GA authors / GA runs (audited by the Director on escalation) |
| **SecOps** | ORACLE | **no-secret leg K** (committed key pattern / key-in-logs FAILS); **provider-taint leg T** (provider SDK/host outside its module FAILS) | "is this credential design sound" · threat-model judgment · which providers are acceptable | SecOps authors denylist / DevOps wires · GA audits coverage |
| **Backend-API** | PARTIAL | typecheck/build/contract-conformance/authz-every-route legs on `apps/api` | API design judgment · "is this the right seam" | Architect/BE-API author contract / DevOps wires · QA judges |
| **Backend-Data** | ORACLE | **money-truth leg M** (a billed call bypassing the metered chokepoint `<3.2>` THROWS/FAILS; each call writes a spend-ledger row) — the strongest oracle in the kit (a static import-check: plant the bypass, leg fails) | schema-design tradeoffs · "is the domain model right" | BE-Data authors invariant checklist (impl+QA+SecOps+FinOps) / DevOps wires · QA+FinOps judge |
| **Frontend-Web** | PARTIAL | typecheck/build/a11y-lint on `apps/web`; import-boundary (no domain/provider imports in components) | UX craft · "does this feel right" (taste has no oracle) | FE-Web authors / DevOps wires · Design/QA judge |
| **DevOps** | VERIFIER | the gate runner itself (exit-code honesty); **wires every seat's oracle legs**; drift guard; RLS/policy-lint | infra tradeoffs · "is this pipeline sound" | DevOps authors / DevOps runs (GA audits the runner is armed) |
| **AI/ML** | HUMAN | (arms with the engine) grounding/format legs AIQ builds: output cites a real source-of-record; schema-valid | **"is the signal good / correct / persuasive"** — no oracle; golden-eval + ground-truth close it, never self | AI/ML authors rule / **AIQ builds the oracle + JUDGES** (builder ≠ judge) |
| **AI Quality** | VERIFIER | golden-eval pass/fail on a frozen set at a pinned commit; anti-fabrication grounding leg; catch-matching grade vs a shared reason-vocab | "is the eval set representative" · accuracy vs external blind ground truth (domain-expert, write-once) | AIQ authors / AIQ runs · GA audits independence (void on contamination, LL-47) |
| **FinOps** | ORACLE | **fail-closed COGS governor** (spend over cap THROWS); **billing-reconciliation** (ledger rows vs provider bill mismatch FAILS); $/day self-tally auto-kill | "is this unit-economics viable" · pricing judgment | FinOps authors caps / DevOps wires · GA audits · **real dollars (billed model, D-TRADE-004)** |
| **Legal & Privacy** | PARTIAL | **forbidden-phrase / PII scan** (a denylisted phrase or unencrypted PII field FAILS) | **"is this regulated investment advice"** `<4.3>` · "is this phrasing advice" — the honest-row model: an oracle seat keeping its judgment call HUMAN (escalates to Director) | Legal authors denylist / DevOps wires · GA audits |
| **Data Engineer** | PARTIAL | ingestion schema-conformance / freshness legs (a malformed or stale EDGAR/market-data row FAILS) | source-selection judgment · "is this data trustworthy" | Data-Eng authors / DevOps wires · QA judges |
| **Design Lead** ("Designer") | HUMAN | (once armed) a11y-conformance / contrast / design-token legs; shared-component rule (a duplicated primitive is leg-detectable where wired) | **taste · hierarchy · craft — taste has no oracle**; the **Director is approver of record on every mockup** (UI-mockup gate, protocol 10) | Design authors tokens/rules / DevOps wires a11y legs · **Director approves** · GA audits approved-mockup→build traceability |

**Residue named to HUMAN (LL-50 — an unnamed residue is a green over real exposure):** taste/craft (Design,
FE) · legal advice-vs-not (`<4.3>`) · signal quality/correctness (AI/ML — closed only by blind external
ground truth) · strategy/sequencing/scoping (Lead/Architect) · all severity and boundary-honesty calls.
Every one of these **escalates to the Director**, who holds the root of trust.

**Seeded GA coverage-audit job:** on every rule-set change and on staleness, GA audits this table for
(1) coverage — does each leg cover the defect class its row claims (a claimed cert with no leg = GAP);
(2) soundness — does each leg have a negative control that bites; (3) boundary-honesty — is any seat
claiming the certified column for a duty that is really HUMAN (the admission test as an objective failure).
