# Lead open-items ledger — HELM (`trade`)

🔒 **Re-authored 2026-08-01** (LL-19 — the founding-day version was entirely pre-pivot: SaaS-era
Node/Docker toolchain items, EDGAR/Legal questions superseded by D-TRADE-020's personal-tool framing,
and a W0 SaaS wave breakdown that no longer describes anything real. None of that carries forward.)

## A · Open Director decisions (present, then WAIT — LL-38)
| # | Item | Status |
|---|---|---|
| 1 | ✅ **RESOLVED (D-TRADE-034, 2026-08-30) — P-1 LIFTED for HELM Phase-1 build.** Director build-GO. Explicitly does NOT cover Phase 2 — `breakout_model`/D-TRADE-033 stays held (item 12). | Closed by explicit, scoped Director authorization — the single most-asked-and-unanswered question in this project's history, now answered. |
| 2 | ✅ **P-2 — MOOT (D-TRADE-028, 2026-08-04).** No options screener to locate — HELM dropped options entirely; the actual scanner (`tools/rolling_watchlist.py`) was never missing, already fully in-repo. | Closed, not by search — by the product no longer needing that artifact. |
| 3 | 🟡 Provider/tier confirm — **Massive personal tier only** (SEC-API.io key identity resolved, D-TRADE-026) — SecOps's task, light-touch now (not the heavy commercial gate it once was). | Not urgent, not blocking. |
| 4 | 🟡 `<4.3>` regulatory light-touch check — substantially de-risked (personal use), Legal not yet spawned. | Not urgent. |
| 5 | ✅ **MOOT (D-TRADE-028).** Historical options-chain/IV data availability — no longer relevant, IV-rank dropped with options framing. | Closed by the pivot, not by discovery. |
| 6 | 🟡 Product name (`HELM` rebrand) | Any time, no urgency. |
| 7 | ✅ **DELIVERED + RATIFIED — ADR-0001 R2 (D-TRADE-030).** Full protocol-17 CRITICAL-tier review complete: AI/ML + AIQ both co-signed the actual revised text after finding and closing 4 real objections (import-boundary gap, Leg-B baseline leakage, grid cherry-pick, minimum-support floor). Absorbed into canonical `<3.5>`/`<3.6>`. | Closed. Technical design is done — what's left before a real run is P-4 below. |
| 8 | ✅ **RESOLVED (D-TRADE-035, 2026-08-30) — `helm/universe` DROPS.** Director ratified the Architect's recommendation directly. | Closed. ADR-0001 §4/§5/§9's module-table text still needs the Architect's own confirming edit (named, not yet done). |
| 10 | ✅ **RESOLVED (D-TRADE-032, 2026-08-14).** `docs/guardrail-v2.1/` (§3-§9 scoring revisions), which landed via an ungrouped session with no D-TRADE number, ruled **exploratory/non-canonical** by the Director — does not enter HELM, does not reopen ADR-0001 OP-4. Block B's EDGAR-mirror ingestion fix separately authorized and delivered (`382c514`). | Closed by Director ruling, not by search or Lead judgment call. |
| 9 | ✅ **RESOLVED (D-TRADE-036, 2026-08-30) — P-4 LOCKED.** OP-1 grid trail∈{5,8,12}%/init∈{2,3}%, primary cell trail=8/init=3; OP-2 = 1d/1w/1m (unchanged); OP-3 = fixed N=5 trading days, N=1/21 sensitivity-only. Director-authorized Lead defaults. | Closed, but **not AIQ-cosigned** — ADR-0001 §12 expected that co-sign for these specific numbers and it was explicitly bypassed by Director instruction. Worth an AIQ pass if/when that seat is live, even though it's not gating. |
| 13 | 🟡 **P-5 — B5 secret sign-off, S6 CLOSED, still not fully closed overall.** SecOps delivered `6498dae` — classification/blast-radius, least-privilege, ToS-tier match, storage, rotation policy for all 6 secrets, fresh evidence, no blocking finding; Director-approves + SecOps-co-signs both checked for S1-S6. **S6 formally closed 2026-08-30:** "exposure confirmed, no evidence of malicious use, proactively and fully remediated" (Director-requested language, matches the independently-verified record — log-file exposure, old value confirmed live pre-rotation, new value confirmed live post-rotation). **Still open: `Installed`/`Leg K re-run GREEN` (blocked on DevOps's harness)**, S1/S2 proactive-rotation recommendation, S5 one-key confirmation — see item 14 for a related new S5 finding. | Live-key use still formally blocked until Installed + Leg K close — doesn't block HELM Phase-1 design/pre-registration work. |
| 14 | ✅ **RESOLVED 2026-08-30 — S5 (Massive) command-bar exposure CLOSED.** Director confirmed the key was rotated after the flag. Lead independently verified what's checkable now: `massive_api_key.txt.template`'s git history (`Trade - Lead`) never had a real key committed; the real `massive_api_key.txt` is gitignored, never committed; the **current** key is live (HTTP 200, one authenticated call, value never printed). The rotation-in-response-to-the-flag link itself stays Director-attested — no before/after artifact existed to check independently, unlike S6. Closed with the same status language as S6, evidentiary basis stated plainly as mixed, not identical. | SecOps re-confirmation of its S5 co-sign requested (item 13's review predated this information) — dispatched, awaiting response. |
| 12 | 🟡 **HELD (D-TRADE-033, 2026-08-30) — `breakout_model` / "Predictive Model 7.0" pipeline** (`Trade/*.py`, Phase-2's from-scratch breakout-occurrence model, canonical `<1.4>`). Real code, Lead-verified: 9 files on disk, `test_synthetic.py` exit 0, 8/8 unit/synthetic tests pass — **not** the D-TRADE-021 OOS/CV clearance bar. Not authorized to build/train further. | Blocked on **both** P-1 (general) and a dedicated Phase-2 scope decision — Phase-1 hasn't itself cleared P-1 yet. |
| 11 | ✅ **RESOLVED 2026-08-21 — SEC-API.io credential exposure.** Old token independently confirmed still live (HTTP 200) before being trusted as dead; Director then rotated for real at the provider, Lead re-verified the new value live (HTTP 200), `float-study/log_pull.txt` deleted entirely. See `activity-log.md` for the full sequence. | Closed by verified rotation + deletion, not by an unverified claim. |

**Everything else from founding (roster lock, cost-model lock, B9/B7 adoption, the old provider set,
toolchain installation) is either resolved by D-TRADE-020's pivot or dropped as N/A — see
`docs/foundation/PROJECT-CONFIG.md` §2–4 for the current, correct state of each.**

## B · Browser-UI dashboard (D-TRADE-023) — actively in progress, mid-dispatch
4 seats assigned (Architect → Designer/DevOps/AI-ML, Architect paces). **None had reported back as of
this ledger's last update.** Full detail: `docs/roles/lead/activity-log.md` "In-flight work". Next Lead
action: check for their reports, consolidate (don't relay each separately — LL-65), keep driving to a
working dashboard.

## C · Standing Lead practices (protocol references in the charter)
- **Verify-don't-attest — including my own synthesis** (protocol 15 ④ / LL-34): re-derive each claim; a
  different seat (GA, not yet spawned) audits any synthesis feeding a decision.
- **Recurring validation of my own output** (protocol 17 / LL-64): route critical Lead-authored artifacts
  to GA/eval before presenting as reconciled — not yet exercised in practice (GA doesn't exist yet).
- **One report per piece of work, at completion** (protocol 15 / LL-65): hold, consolidate, present once.
- **Never self-dispatch; never unilaterally reinterpret an explicit Director ruling** — learned hard this
  session via D-TRADE-010's own history (an early "spawn to build" framing was corrected by the Director;
  every "is this authorized" question since has been asked, not assumed).
- **Sync before every write:** `git pull --rebase` before AND after. Real, frequent concurrent-seat
  activity this session — normal, expected, not a problem.
- **Secret-file hygiene:** don't trust "gitignored" without verifying — `git log -p -- <path>` before
  assuming a secret-adjacent file's history is clean (two real incidents this session, both caught).

## D · W0 (HELM Phase-1 first build wave) — planned only, NOT authorized (D-TRADE-010, P-1 above)
The old SaaS-era W0 breakdown (Node/pnpm/Docker monorepo scaffold) is **deleted, not parked** (LL-19) —
it described a stack this project no longer uses. The current Phase-1 breakdown lives in
`docs/app-design/stage-plan.md` (P1-0 through P1-5), which is the authoritative, current plan. P1-0
(the Architect's design ADR) is done (ADR-0001, ratified as D-TRADE-022). **Nothing beyond design/
planning proceeds until P-1 clears.**
