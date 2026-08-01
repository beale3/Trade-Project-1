# Provider cost model — HELM (`trade`)

**Owner:** FinOps (FinancialOps Lead) · **Authored:** 2026-08-01 · **Task:** pre-build provider cost model
(D-TRADE-016 FinOps light pre-build work; allowed under D-TRADE-010 — *modeling only, not governing live
spend*: no metered chokepoint exists yet). **Cost model of record:** BILLED PER-USE (D-TRADE-004,
🔒-pending Director LOCK).

**Phase honesty (read this first).** This is a **model + parameter frame**, not a price sheet to decide on.
No engine, no chokepoint, and no product `<1.1>` exist yet, so the two numbers that actually set per-unit
COGS — *tokens per signal* and *the chosen model's token rates* — are **unmeasured by construction**. What
this doc fixes is the **shape** of the cost (which providers are variable-per-use vs standing floor, and the
exact expression each COGS takes) so the governor (`governor-spec.md`) can *meter and cap* the moment the
chokepoint arms at W1.

**Status:** DRAFT — gate ② (GROUND) only. NOT yet RECONCILED (gate ③, GA/second seat) or Director-locked
(gate ⑤). Every dollar *cap/target* below is a **recommendation flagged for Director lock** — pricing and
unit-economics viability are HUMAN and escalate (my oracle-boundary row; profile mandate).

---

## Conventions (binding on every figure in this doc)

- **Confidence tag (LL-52 discipline):** every figure is tagged **`measured`** (I read it from the provider's
  own published surface at read-date) · **`estimated`** (derived/prior-knowledge, not re-read at read-date) ·
  **`unmeasured`** (no basis exists yet — must be measured before it enters a ruled decision).
- **Basis (LL-52):** every figure carries its basis — `per-month` · `per-GB-month` · `per-1M-tokens` ·
  `per-call` · `per-invocation` · `one-time`. An un-based figure gets compared across bases and misleads.
- **Qualified figures travel as their expression, not a rounded worst case (LL-61 / protocol 16):** e.g. the
  market-data floor is carried as `Massive_plan + Σ exchange_pro_fees`, re-derived where used — never
  pre-collapsed to a single number.
- **Re-verify at action time:** provider pricing is release-note-volatile. Every `measured` figure names its
  source + read-date; anything older than the decision that uses it is re-read first.
- **Not-re-derived (protocol 13d):** provider *identity / host / ToS* facts are owned by SecOps
  `docs/security/tos-taint-review.md` (read 2026-08-01) and cited here, not re-authored. This doc adds the
  **dollar** dimension only.

---

## §1 · Central finding — variable-per-use COGS vs standing infra floor

D-TRADE-004 says "billed per-use," but of the four adopted providers **only one is actually billed per call.**
Getting this split right is the whole point of the model: the fail-closed governor must veto the *variable*
spend, and the *floor* must be surfaced as a fixed monthly line — conflating them either lets real spend run
(floor treated as the cap) or throttles free calls (floor metered as if per-use).

| Provider | Marginal cost of one more API call | Classification | Governed by |
|---|---|---|---|
| **LLM (signal engine)** | **> 0 — priced per token, every call** | **VARIABLE per-use COGS** | the fail-closed governor (`governor-spec.md`) — the meter moves here |
| **Polygon / Massive** | **$0 within the plan's rate limit** (flat sub, "unlimited API calls" on paid) | **standing floor** (a subscription) | budgeting, not the per-call governor |
| **SEC EDGAR (direct)** | **$0** (free public data, rate-limited not priced) | **standing floor = $0** | rate-limit discipline (SecOps leg T), not $ |
| **Supabase** | **≈ $0 per call**; cost accrues to slow-moving *usage* (storage, egress, MAU) | **standing floor + usage overage** | budgeting + an overage watch, not the per-call governor |

**Consequence for the governor:** the per-use spend meter is, in practice, an **LLM-token meter** (plus any
*future* genuinely-per-call provider). Every billed-provider call still routes through the money-truth
chokepoint `<3.2>` and writes a spend-ledger row — for reconciliation, rate-limit governance and ToS-taint
(D-TRADE-008) — but a Polygon/EDGAR call adds a `$0.00` ledger row and does **not** move the `$/day`
auto-kill tally. **This is the LL-15 point at provider scale: govern the measured per-unit COGS, not the
headline "cost of market data."**

---

## §2 · Per-provider cost model

### 2.1 · LLM (the AI/ML signal engine `<3.4>`) — the only true per-use COGS

Model **unchosen** (blocked on product `<1.1>` + D-TRADE-010 no-build; a Python/ML lane is also still open,
D-TRADE-003). No literal model IDs are recorded here (protocol 4). The COGS is therefore given as an
**expression over parameters**, not a number:

```
COGS_per_signal = Σ_over_model_calls_in_the_pipeline [ (in_tokens / 1e6) · R_in  +  (out_tokens / 1e6) · R_out ]
```

| Parameter | Value | Tag | Basis |
|---|---|---|---|
| `R_in`  (input token rate)  | frontier tier ≈ **$1 – $5 / 1M** | `estimated` | per-1M-tokens · market survey, read 2026-08-01 (see provenance) |
| `R_out` (output token rate) | frontier tier ≈ **$15 – $75 / 1M** | `estimated` | per-1M-tokens · same |
| `in_tokens` / `out_tokens` per signal | **UNKNOWN** | `unmeasured` | per-call · no engine/prompt exists (`<3.4>` pending) |
| model-calls per signal (chain depth) | **UNKNOWN** | `unmeasured` | per-signal · pipeline undesigned |

**Why this stays an expression, not a number (LL-15, verbatim risk):** a model swap that holds `R_out`
constant can still change `COGS_per_signal` by tens of percent through a different **tokenizer** (same text →
more tokens) and through **output length** (a chattier model at the same rate costs more per signal). The
governor therefore caps and reconciles the **measured** `COGS_per_signal` from a real pipeline trace — it
never trusts the headline `$/1M` rate. **First measurement obligation:** the day the engine has a runnable
prompt, FinOps + AI/ML capture a real token trace and replace both `unmeasured` rows with `measured` ones
*before* any cap value is proposed to the Director.

### 2.2 · Polygon / Massive — market data (standing floor; the headline price is NOT the SaaS price)

> Provider identity is in transition — **Polygon.io, Inc. rebranded to "Massive" (effective 2025-10-30);
> `api.polygon.io` and `api.massive.com` are both live.** Owned by SecOps `tos-taint-review.md` §Provider 2
> (read 2026-08-01); cited, not re-derived.

**Self-serve, individual / Non-Professional pricing** (massive.com/pricing, read 2026-08-01):

| Tier | Price | Rate limit | History | Marginal $/call | Tag |
|---|---|---|---|---|---|
| Stocks Basic (Free) | **$0** | 5 calls/min | 2 yr | $0 | `measured` · per-month |
| Stocks Starter | **$29** | unlimited | 5 yr | **$0** (flat) | `measured` · per-month |
| Stocks Developer | **$79** | unlimited | 10 yr | **$0** (flat) | `measured` · per-month |
| Stocks Advanced | **$199** | unlimited | 20+ yr (+ Financials & Ratios) | **$0** (flat) | `measured` · per-month |
| add-ons (Financials & Ratios standalone · NYSE Order Imbalances · partner datasets) | $29 · $49 · **$99/dataset** | — | — | — | `measured` · per-month |

🟠 **The headline $29–$199 is the wrong number for HELM, and this is the FinOps half of a finding SecOps
routed here.** Those tiers are **Non-Professional, individual, display-only** licenses. A commercial SaaS for
ShupeCapital is a **Professional** subscriber on the **Business** tier, whose price is **contact-sales
(quote-only)** and which, for **real-time** equities/options, **adds per-exchange market-data fees** —
**OPRA · Nasdaq/UTP · NYSE** professional subscriber fees, billed per the SRO schedules, **not** shown on the
self-serve page.

| Real market-data floor for a commercial SaaS | Value | Tag | Basis |
|---|---|---|---|
| Massive **Business/Professional** plan | **quote-only** | `unmeasured` | per-month · contact-sales; self-serve $199 does **not** apply |
| OPRA / Nasdaq-UTP / NYSE professional exchange fees (real-time) | **quote-only, can dominate the plan fee** | `unmeasured` | per-exchange, often per-professional-user-month · SRO schedules |
| Real market-data floor (carry as expression, LL-61) | `Massive_Business_plan + Σ exchange_pro_fees` | `unmeasured` | per-month |

**Cost lever (routed back to the Director for `<2.1>`, in dollars):** choosing **delayed / end-of-day /
reference data** instead of **real-time** removes most of the OPRA/UTP/NYSE surface and its professional
fees; and if the near-term need is *filings/fundamentals*, **EDGAR (§2.3) covers it at $0** and market-data
licensing can be deferred until a feature actually needs live quotes. Real-time vs delayed is a real-dollar
decision — I state the lever; the Director decides `<2.1>`.

### 2.3 · SEC EDGAR — filings (standing floor = $0, but confirm the key's issuer)

Direct public EDGAR (`data.sec.gov` / submissions / XBRL frames): **free, no API key, no per-call charge**;
fair-access cap **10 requests/second per IP**, mandatory declared `User-Agent`; a 403 + ~10-min IP block on
breach (sources: SEC "Accessing EDGAR Data" + SecOps `tos-taint-review.md` §Provider 1, read 2026-08-01).

| EDGAR cost path | Value | Tag | Basis |
|---|---|---|---|
| Direct public EDGAR | **$0** | `measured` | per-call · public-domain, UA-gated not key-gated |
| **If the in-hand "SEC key" is a third-party reseller** (SecOps flags the 77-byte key ≠ public EDGAR's UA model → likely an `sec-api.io`-class reseller) | **reseller subscription — quote/tier-priced** | `unmeasured` | per-month + likely per-query caps · reseller ToS + pricing govern |

🟡 **Cost-relevant open item (echoes SecOps blocker-candidate, in dollars):** if the key authenticates a
reseller, EDGAR stops being $0 and gains a subscription + query-cap cost. **Confirm the issuer before EDGAR
enters the floor as $0.** I did not read the key (B5).

### 2.4 · Supabase — DB / backend (standing plan + slow-moving usage overage)

Adopted (D-TRADE-013/014). Pricing (supabase.com/pricing, read 2026-08-01):

| Plan | Base | Includes | Tag |
|---|---|---|---|
| Free | **$0** | 500 MB DB · 5 GB egress · 50k MAU · 1 GB storage · 500k edge-fn invocations · 200 realtime conns · 2M realtime msgs | `measured` · per-month |
| Pro | **$25** | Micro compute ($10 value) · 8 GB DB · 250 GB egress · 100k MAU · 100 GB storage · 2M edge-fn · 500 realtime conns · 5M realtime msgs | `measured` · per-month |
| Team | **$599** | Pro quotas + SOC2/ISO controls | `measured` · per-month |

**Overage unit prices (Pro/Team — usage-based, `measured`, per basis shown):**

| Metric | Overage | Basis |
|---|---|---|
| Database size | **$0.125** | per-GB-month |
| Egress (bandwidth) | **$0.09** | per-GB |
| Cached egress | **$0.03** | per-GB |
| Monthly active users | **$0.00325** | per-MAU |
| File storage | **$0.0213** | per-GB-month |
| Edge-function invocations | **$2 / 1M** = $0.000002 | per-invocation |
| Realtime connections | **$10 / 1000** = $0.01 | per-connection |
| Realtime messages | **$2.50 / 1M** = $0.0000025 | per-message |
| PITR (point-in-time recovery add-on) | **$100** per 7 days retention | per-month |

**Classification:** Supabase cost is **≈ $0 per API call**; it accrues to *storage/egress/MAU*, which move
on the scale of the whole app over a month, not per signal. So it is **floor + a monthly overage watch**, not
a per-call governor input. The edge-fn and realtime *are* per-event priced — if the design puts the signal
pipeline behind edge functions, that per-invocation line re-enters the per-use meter and the governor tracks
it too (a design-dependent hook, flagged for the W1 chokepoint checklist).

---

## §3 · Standing infra floor (part of the cost model — mandate + LL "surface the floor with the per-use spend")

The floor is what HELM pays **before a single signal is produced**. Carried as an expression (LL-61); the
starting config is a *recommendation* for the Director, not a ruling.

```
Monthly_floor = Supabase_plan + Massive_plan + EDGAR_cost + CI + Hosting  (+ Director-time, non-$ below)
```

| Line | Bootstrap (dev/pre-build) | Build-time (commercial SaaS) | Tag |
|---|---|---|---|
| Supabase | $0 (Free) | **$25** (Pro — needed for money-truth durability / RLS posture) | `measured` (prices) / `estimated` (which tier) |
| Massive (market data) | $0 (Free, 5 calls/min) | **`Massive_Business_plan + Σ exchange_pro_fees`** (quote-only) | `unmeasured` |
| EDGAR | $0 | $0 **or** reseller sub if the key is a reseller | `measured` / `unmeasured` |
| CI (GitHub Actions) | $0 (free-tier minutes) | ~$0.008/Linux-min beyond free tier | `estimated` — not re-read 2026-08-01; verify before it enters a decision |
| Hosting / compute | — | **UNKNOWN** (host unchosen, D-TRADE-010) | `unmeasured` |
| **Floor total** | **≈ $0 measured** | **`$25 + quote-only market-data + CI + hosting`** — *not collapsible to one number yet* | mixed |

**Director's own time is a real cost (§1.8 / profile), stated not dollarized:** every lock, review and
approval this model asks for (the cost-model lock, `<2.1>` provider/tier decision, the Legal `<4.3>` routing,
each governor cap value) consumes Director time. It has no `$/hour` rate on record, so it is carried as a
**named HUMAN input**, not a free good — flagged, not hidden.

---

## §4 · What the governor must do given this model (hand-off to `governor-spec.md`)

1. **Meter the variable line (LLM tokens) per call**, in real measured `COGS_per_signal`, not headline rate.
2. **Fail closed:** no cap row / meter unreachable / ledger write fails ⇒ the call does **not** happen.
3. **`$/day` self-tally auto-kill** on the global variable spend (D-TRADE-004).
4. **Reconcile** the ledger's summed `$` per provider against the provider invoice each cycle; mismatch FAILS.
5. **Record every billed-provider call** (incl. the `$0.00` Polygon/EDGAR rows) for reconciliation + rate
   governance, while the auto-kill tally moves only on priced calls.
6. Treat **Supabase edge-fn / realtime** as a conditional per-use line **iff** the design routes the pipeline
   through them (checklist item for the W1 chokepoint lock).

---

## §5 · Open items surfaced to the Lead (dollars only; I do not rule these)

- 🟠 **Market-data true cost is quote-only, not $199** — commercial SaaS = Professional/Business tier +
  OPRA/UTP/NYSE fees. Real-time-vs-delayed is a real-dollar lever on `<2.1>`. (FinOps half of SecOps's HIGH
  Polygon finding.) → **Director** decides provider/tier; **Legal** decides the `<4.3>` derivative-works
  question that gates whether the tier is even usable.
- 🟡 **"SEC key" issuer unconfirmed** — direct EDGAR = $0; a reseller key = a subscription cost. → confirm
  issuer (SecOps/Data-Eng/Director) before EDGAR is booked at $0.
- 🟡 **Per-signal COGS is unmeasured by construction** — no cap value can be *ruled* until a real engine token
  trace exists. The governor is built to **meter and cap**, not to predict; caps arm tight and rise on
  evidence.
- 🟡 **Cost-model lock D-TRADE-004 is 🔒-pending** — this whole model presumes the billed-per-use lock; it
  needs the explicit Director yes.

---

## §6 · Provenance (source + read-date for every `measured` figure — re-verify before use)

| Figure | Source | Read-date |
|---|---|---|
| Supabase plans + overage unit prices | `https://supabase.com/pricing` | 2026-08-01 |
| Massive (Polygon) self-serve stock tiers | `https://massive.com/pricing` (`polygon.io/pricing` 301→ here) | 2026-08-01 |
| Polygon→Massive rebrand; both API hosts live; Professional/exchange-fee structure | SecOps `docs/security/tos-taint-review.md` §Provider 2 (its own sources cited there) | 2026-08-01 |
| EDGAR free + 10 req/s + UA rule | SEC "Accessing EDGAR Data" + SecOps `tos-taint-review.md` §Provider 1 | 2026-08-01 |
| Frontier LLM token-rate band | public LLM-pricing market survey (no model IDs recorded, protocol 4) | 2026-08-01 |
| CI per-minute rate | prior knowledge — **not re-read**, tagged `estimated` | — |

---
*DRAFT — self-checked (gate ②). Awaiting: GA/second-seat RECONCILE (gate ③), the W1 chokepoint invariant
lock (with SDE1/BE-Data + QA + SecOps), and Director locks on D-TRADE-004 + every cap value. Reported to the
Lead once, at completion (protocol 15).*
