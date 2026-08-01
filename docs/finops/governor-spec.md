# Fail-closed COGS governor — spec — HELM (`trade`)

**Owner:** FinOps · **Authored:** 2026-08-01 · **Arms:** W1, with the money-truth chokepoint `<3.2>`
(D-TRADE-008) — **not now** (D-TRADE-010 no-build; this is the SPEC, SKIP-visible until armed). Cost model:
BILLED PER-USE (D-TRADE-004, 🔒-pending). Reads `cost-model.md` (the variable-vs-floor split).

**What FinOps certifies vs escalates (oracle-boundary row, verbatim boundary):**
- **Certified (mechanical, this spec):** the fail-closed governor behavior · the spend-ledger invariants ·
  the `$/day` self-tally auto-kill · billing reconciliation. Each below carries a **negative control a
  different seat can reproduce** (the admission test — builder ≠ judge).
- **HUMAN + escalates → Director:** every **dollar cap/threshold value** (pricing + unit-economics
  judgment). This spec fixes the **mechanism and the decision frame**; it proposes **recommended defaults**
  clearly flagged as awaiting Director lock. A cap *number* is never ruled here.

**Status:** DRAFT — gate ② (GROUND). NOT independently validated (gate ③ GA + the co-authored checklist §5)
nor Director-locked. Presented to the Lead once, at completion.

---

## §1 · What the governor governs (from `cost-model.md` §1)

The chokepoint is the single metered path for **all** billed-provider calls; the **governor's veto** acts on
the **variable per-use spend**, which today is **LLM tokens** (plus any future genuinely-per-call provider,
and conditionally Supabase edge-fn/realtime iff the pipeline uses them). Polygon/Massive and EDGAR calls
still pass through and write a ledger row, but at `$0.00` marginal they do **not** move the auto-kill tally.
This keeps the governor honest: it throttles money, not free calls.

---

## §2 · Fail-closed semantics (the core invariant — "the default is refusal")

A priced call is **permitted only if ALL** hold; **any** failure ⇒ **REFUSE (throw), do not call the
provider**:

1. a **budget/cap row exists and is readable** for the (tenant, day) and the global day;
2. **projected post-call cumulative spend ≤ the applicable cap** at every layer (§3), using a
   **conservative pre-call cost estimate** for the variable line (max-tokens bound, not hoped-for);
3. the **meter/ledger is reachable** and the **pre-call ledger reservation row commits**;
4. the global **auto-kill is not tripped** for the current UTC day (§4).

**Fail-closed, not fail-open (profile, verbatim):** *no budget row · no cap · meter/DB unreachable · ledger
write fails* ⇒ **the call does not happen.** A governor that fails open is decoration. (This aligns with
Supabase's own "no uptime warranty" volunteered constraint, SecOps §Provider 3: if the DB is down the
money-truth path must fail-closed, never silently drop a ledger row and call anyway.)

- **Negative control (reproducible by QA/DevOps, not FinOps):** delete the cap row → a priced call **REFUSES**
  (green would reject: *"a call with no budget row"*). Point the ledger at an unreachable DB → **REFUSES**.

---

## §3 · Cap layers (mechanism fixed here; VALUES are Director-locked)

Caps are **re-derived expressions, not baked constants** (protocol 16 / LL-61); the variable term is always
the **measured** `COGS_per_signal` (`cost-model.md` §2.1), never a headline rate (LL-15).

| Layer | Rule (refuse when …) | Catches | Value | Recommended default (Director locks) |
|---|---|---|---|---|
| **L1 · per-call ceiling** | `projected_call_cost > C_call` | one runaway call (prompt-injection blow-up, an unbounded output) | `C_call` | a tight multiple of the *measured* median call cost, once measured; **until measured, a hard absolute token-count ceiling per call** |
| **L2 · per-tenant-per-day** | `tenant_day_spend + projected > C_tenant_day` | one tenant draining budget | `C_tenant_day` | derived from the per-tenant unit-economics target — **needs `<1.1>` + a revenue/price point → Director** |
| **L3 · global-per-day** | `global_day_spend + projected > K_day` → **also trips auto-kill (§4)** | total daily blast radius / a systemic bug | `K_day` | **the largest single-day spend the Director is willing to lose to a bug** — a HUMAN input, not a formula |

**Why no dollar numbers here (honest boundary):** L1–L3 values depend on `COGS_per_signal` (**unmeasured** —
no engine) and on the unit-economics target (**Director**, needs `<1.1>`). Inventing them would be a pricing
ruling I do not own. **Bootstrap rule instead:** at first-arm, set every cap **deliberately tight** (a
fail-closed philosophy — start where a runaway costs little, raise on measured evidence), using **absolute
token/count ceilings** where a dollar cap can't yet be grounded.

- **Negative control:** drive `global_day_spend` to `K_day − ε`, submit a call that would cross → **REFUSED**
  at L3; same shape at L1/L2.

---

## §4 · `$/day` self-tally auto-kill (D-TRADE-004)

A **monotonic per-UTC-day tally** of variable spend, incremented **transactionally with each priced ledger
row**. When `global_day_spend ≥ K_day`:

1. the chokepoint **HARD-STOPS all priced calls** for the remainder of the UTC day (free `$0` calls may be
   allowed to continue *only* if a separate rate-safety check passes — design flag for the checklist);
2. a **SEV1** is raised to the Director (via the Lead, protocol 15) — auto-kill is a spend event the
   decision-maker must see;
3. reset is **time-based (next UTC day) or an explicit Director raise of `K_day`** — never a silent
   auto-reset that would let a bug bleed across days.

- **Distinct from L3 refuse:** L3 refuses the *one* crossing call; the auto-kill **latches** the whole day
  off, so a storm of calls each individually under `C_call` cannot sum past `K_day`.
- **Negative control:** feed priced ledger rows until the tally reaches `K_day` → the **next** priced call is
  hard-stopped and a SEV1 emits (green would reject: *"the first call after the daily tally crosses K_day"*).
- **Idempotency guard:** a retried/duplicated call id must **not** double-increment the tally (§5 ledger
  invariant) — else the auto-kill fires on phantom spend.

---

## §5 · Spend-ledger invariants + reconciliation (FinOps-certified) — and the co-authored chokepoint checklist

### 5a · Ledger invariants (FinOps owns; the negative control is built by a different seat)

| Invariant | Meaning | Negative control (reproducible by QA/DevOps) |
|---|---|---|
| **Append-only** | no update/delete of a spend row | attempt an UPDATE/DELETE on a ledger row → **FAILS** |
| **Transactional (call ⇔ row)** | a priced provider call and its ledger row commit atomically — **no call without a row, no row without a call attempt** | plant a code path that calls the provider then writes the row non-atomically; kill between → the leg detects the orphaned call/row → **FAILS** |
| **Idempotent** | replay of the same call id ⇒ exactly one row, one tally increment | replay a call id → a 2nd row or double increment → **FAILS** |
| **Monotonic day-tally** | the `$/day` counter only advances within a UTC day, resets on the boundary | force a non-monotonic write → **FAILS** |

### 5b · Billing reconciliation oracle (FinOps-certified)

Each billing cycle: **`Σ ledger.priced_rows.cost` per provider must reconcile to that provider's invoice
within tolerance `ε`; a mismatch `> ε` FAILS** and escalates (SEV1/2 — GA/Lead set severity).

- `ε` accounts only for **provider-side rounding + month-boundary timing** (calls straddling the cutoff);
  recommended **tight** (sub-cent per line, plus a named timing window). `ε` is a value → **flagged for
  Director/GA**, not ruled here.
- The reconciliation is the **backstop the auto-kill can't be**: the auto-kill trusts our own meter; only the
  invoice check catches a **meter that under-counts** (the LL-15 failure — a tokenizer change silently making
  each call cost more than our estimate books).
- **Negative control (reproducible by GA):** inject a ledger row with a wrong cost, or drop a row that the
  invoice contains → reconciliation **FAILS** (green would reject: *"a ledger whose provider-sum ≠ the
  invoice"*).

### 5c · FinOps' contribution to the chokepoint invariant checklist (co-authored — DRAFT, sign-off slots)

The **money-truth chokepoint invariant checklist is BE-Data's artifact** (oracle-boundary: *"BE-Data authors
invariant checklist (impl + QA + SecOps + FinOps)"*), locked before W1 build. Below is the **FinOps portion**
only — the spend/governor invariants — offered for BE-Data to assemble. **I author these; I do not certify
the other lanes' portions (builder ≠ judge).**

| # | FinOps invariant (contribution) | Lane that must sign |
|---|---|---|
| F1 | Every billed-provider call routes through the single chokepoint; a call outside it FAILS (money-truth leg M) | **BE-Data** (impl) · QA (re-run) |
| F2 | Governor is fail-closed per §2 (default refuse) | BE-Data · **QA** (negative controls) |
| F3 | Ledger invariants §5a hold (append-only · transactional · idempotent · monotonic) | BE-Data · QA |
| F4 | `$/day` auto-kill §4 latches and emits SEV1 | BE-Data · QA · **FinOps** (threshold frame) |
| F5 | Reconciliation §5b runs each cycle; mismatch FAILS | **FinOps** · GA |
| F6 | Provider credentials referenced only inside the chokepoint/data layer (never `apps/web`) | **SecOps** (leg T/K) · BE-Data |
| F7 | Cap/threshold **values** are Director-locked before arming (no unlocked cap ships) | **Director** · FinOps |

**Sign-off slots (to fill at the W1 lock, protocol 17 — different-agent validation):**
`SDE1/BE-Data ▸ ___  ·  QA ▸ ___  ·  SecOps ▸ ___  ·  FinOps ▸ authored 2026-08-01  ·  GA ▸ (audits the lock ran)`

---

## §6 · Build / wiring split (builder ≠ judge, protocol 14)

- **FinOps authors** the caps, the governor rule-set, the ledger invariants, the reconciliation rule (this
  doc). **DevOps wires** the oracle legs. **QA re-runs** every negative control on phase exit. **GA audits**
  coverage + that the independent validation (protocol 17) actually ran. **BE-Data implements** the chokepoint
  and assembles the invariant checklist. **The Director locks** every dollar value.
- Nothing here arms before W1; every leg is **exit-visible SKIP** until then (gate-spec rule of green).

---
*DRAFT — self-checked (gate ②). Awaiting: co-author sign-off on §5c, GA RECONCILE, and Director locks on
D-TRADE-004 + all cap/threshold values (§3, §4, §5b). One report to the Lead at completion (protocol 15).*
