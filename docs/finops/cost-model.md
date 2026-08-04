# Provider cost model — HELM (`trade`)

**Owner:** FinOps (FinancialOps Lead) · **Authored:** 2026-08-01 · **Revised:** 2026-08-01 (D-TRADE-020
pivot — `<1.1>` locked: HELM is a **personal trading-signal tool**, one user, no SaaS/GTM surface. This is
a **targeted revision, not a full rewrite** — the underlying provider prices haven't changed, only their
*classification and applicability* have; sections superseded by the pivot are re-authored in place per
protocol 19, not left standing alongside the new framing (LL-19).

**Cost model of record:** BILLED PER-USE (D-TRADE-004), **at personal scale** — governed by a lightweight
**spend guard** (`governor-spec.md`, re-authored), not a SaaS-grade metered chokepoint.

**Phase honesty (read this first).** This is a **model + parameter frame**, not a price sheet to decide on.
**Post-pivot reality check:** the validation engine `<3.4>` is **classical statistics** (walk-forward CV),
not generative AI — so **Phase 1 has no LLM spend at all**. Every provider actually in scope (Massive,
SEC-API.io, Supabase) is a **flat subscription or quota-based tier**, not a metered-per-call bill. The open
dollar question is now just **which Massive tier** applies (personal vs. commercial — largely resolved by
the pivot).

**2026-08-04 update (D-TRADE-028):** HELM's options framing is deleted entirely — plain stock buy/sell
signals with a trailing-stop exit, no calls/puts/DTE. The **historical options-chain-data cost question
this doc was tracking as an open item is therefore moot, not resolved** — deleted here too (LL-19/protocol
19), not left as a stale "still open" line. No dollar figure in this doc changes; only that one open item
disappears.

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

## §1 · Central finding (revised post-pivot) — nothing left in scope is truly per-call metered

**Pre-pivot finding (superseded, kept here only for traceability — LL-19):** the original model identified
LLM tokens as the one true per-use COGS among four providers. **That finding's subject is gone**: `<3.4>`
is classical statistics, not generative AI, so **Phase 1 makes zero LLM calls.** Re-derived from scratch for
the actual Phase-1 provider set:

| Provider | Marginal cost of one more API call | Classification | Governed by |
|---|---|---|---|
| **Massive (personal tier)** | **$0 within the tier's included quota** | **standing floor** (flat sub) | the spend guard's *quota* watch (`governor-spec.md`), not a $ meter |
| **SEC-API.io — Personal & Startups** (CONFIRMED, D-TRADE-026 issuer + D-TRADE-027 tier — no longer "likely," no longer free EDGAR, no longer "which tier") | **$0 within 50 GB/month, then $0.30/GB overage** — a real, active $49–$55/mo subscription right now | **standing floor + a real overage risk** (not a hypothetical) | the spend guard's GB-downloaded watch |
| **Supabase** | **≈ $0 per call**; cost accrues to slow-moving *usage* (storage, egress) | **standing floor + usage overage** | a periodic overage glance, not a per-call check |
| **LLM (Phase 1)** | **N/A — not called in Phase 1** (`<3.4>` is classical stats). Kept as a Phase-2-contingent line only; do not budget for it now | **out of scope** | re-open only if a future phase reintroduces generative AI |

**Consequence for the guard:** there is currently **no confirmed genuinely-per-call-billed provider** in
Phase 1's scope. The spend guard (`governor-spec.md`) is therefore mostly a **quota/count tripwire** (catch
a bug before it either trips overage billing or a rate-limit ban), not a dollar meter in continuous motion —
a materially lighter job than the pre-pivot model assumed, consistent with the oracle-boundary re-scope
(ORACLE → PARTIAL).

---

## §2 · Per-provider cost model

### 2.1 · LLM — OUT OF SCOPE for Phase 1 (superseded — kept only as a Phase-2-contingent note)

**Pre-pivot content deleted, not parked (protocol 19 / LL-19):** the prior draft modeled `COGS_per_signal`
as a token-rate expression on the assumption `<3.4>` was a generative-AI engine. **`<3.4>` is now locked as
classical statistics** (walk-forward CV, regression) — there is no model, no prompt, no token spend to
model. **Do not carry the old `R_in`/`R_out` estimates forward into any Phase-1 cap** — they describe a
system that isn't being built.

**Standing note for Phase 2 (`<1.4>`, explicitly deferred, not in scope):** if a future phase reintroduces
a generative-AI component, this section is re-authored from scratch at that time, re-priced at whatever
frontier rates are current then (LL-15 — a stale token-rate estimate is worse than no estimate). Nothing to
track here now.

### 2.2 · Massive (personal tier, formerly modeled as commercial SaaS) — standing floor, mostly resolved

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

🟢 **Re-scoped from the prior HIGH-taint commercial-SaaS finding — largely resolved by the pivot, not by
new pricing research.** The self-serve **individual/Non-Professional** tiers above ($29–$199) were flagged
🟠 in the pre-pivot draft because a *commercial SaaS* cannot legally hold that license (SecOps
`tos-taint-review.md`). **`<1.2>` (personal use, one user, no distribution) plausibly makes the individual
tier exactly the right, compliant, and cheapest tier** — canonical `<2.1>` notes this is Legal/SecOps's
light confirmatory check to close, not a Director tier-selection decision anymore. **I do not own that
confirmation** (provider-acceptability is SecOps's HUMAN column); the dollar consequence is simple either
way: **personal tier = $0–$199/mo flat, unlimited calls on any paid tier** — no per-exchange OPRA/UTP/NYSE
professional fees apply outside a Professional/Business subscription, which a personal user does not need.

| Real-world floor once the tier is confirmed | Value | Tag | Basis |
|---|---|---|---|
| Massive personal tier (Starter/Developer/Advanced, per data-need) | **$29 / $79 / $199** | `measured` | per-month, flat, unlimited calls |

**Deleted, not resolved (D-TRADE-028, LL-19):** the "historical options-chain data" open cost line this
table used to carry is moot — `<1.1>` drops options entirely (plain stock buy/sell + trailing-stop exit).
Nothing to price here; not carried forward as a closed item, just removed, since it never described what
HELM actually needs now.

**Cost lever, unchanged in spirit:** whichever tier is confirmed, the guard (`governor-spec.md`) watches the
**included-quota boundary**, not a live per-call meter — paid personal tiers are flat/unlimited, so the only
remaining risk is a rate-limit ban on the Basic/Free tier, not a running dollar total.

### 2.3 · SEC-API.io — Personal & Startups, CONFIRMED (D-TRADE-026 issuer + D-TRADE-027 tier)

**Re-authored, not patched (LL-19), third time — each pass closing a narrower open item, not new pricing
research.** The original draft carried this as free direct EDGAR; the next revision reframed it as
"probably SEC-API.io" (circumstantial evidence); D-TRADE-026 confirmed the issuer at source (a direct
authenticated call to `https://api.sec-api.io` returned **HTTP 200 with real EDGAR data**, corroborated by
the Director's own logged-in account). **D-TRADE-027 now closes the last open dimension: the Director
confirmed directly this account is on the Personal & Startups tier, not Business.** Nothing here required
new pricing research — this is FinOps's own already-measured `sec-api.io/pricing` figures (below), now
pinned to the one row that is actually the active subscription.

**Re-verified directly against SEC-API.io's own pricing page (`https://sec-api.io/pricing`, read
2026-08-01) rather than left as canonical's estimate** — this upgrades the figures from `estimated` to
`measured`, and surfaces a genuinely metered dimension I hadn't previously modeled:

| Tier | Price | Included data | Overage | Tag |
|---|---|---|---|---|
| Free | **$0** | first 100 calls free | — | `measured` · per-month |
| **Personal & Startups — 🔒 CONFIRMED ACTIVE TIER (D-TRADE-027)** | **$49/mo** (annual) or **$55/mo** (monthly) | 50 GB downloads/month, filings 1993–present, XBRL-to-JSON, insider trading forms | **$0.30 per GB** beyond 50 GB | `measured` · per-month + per-GB |
| Business Internal Use (not the account's tier — kept for contrast only) | **$199/mo** (annual) or **$239/mo** (monthly) | 100 GB/month + full-text search, 13F/N-PORT, real-time stream | **$0.30 per GB** beyond 100 GB | `measured` · per-month + per-GB |

🟢 **This reopens a real per-use cost line the pivot's "everything is flat now" framing (§1) almost missed:**
the **$0.30/GB overage** is genuine metered spend if a backtest script pulls unusually large data volumes
(e.g., broad historical bulk pulls across the whole universe). This is exactly the shape §1's "quota
overrun" failure mode describes — it is now a **named, measured** instance of it, not a hypothetical one.
**Direct feed to `governor-spec.md`:** the guard's quota watch tracks **GB downloaded this billing-month
against the confirmed 50 GB included volume** (not 100 GB — that was the non-active Business tier).

| SEC-API.io cost path | Value | Tag | Basis |
|---|---|---|---|
| **In-hand key — CONFIRMED Personal & Startups** | **$49/mo** (annual) or **$55/mo** (monthly) **+ $0.30/GB** beyond 50 GB | `measured` — issuer, paid status, AND tier all confirmed | per-month + per-GB · D-TRADE-026 (issuer) + D-TRADE-027 (tier) + this doc's §2.3 tier table |
| Direct public EDGAR (not the operative path for this key — kept only as a theoretical fallback if a *different*, keyless integration is ever added) | $0, 10 req/s cap, UA-gated | `measured` | per-call · SEC "Accessing EDGAR Data" + SecOps `tos-taint-review.md` §Provider 1, read 2026-08-01 |

**Fully resolved (D-TRADE-026 + D-TRADE-027) — nothing further open on this provider.** SEC-API.io is a
confirmed, currently-active **Personal & Startups** subscription: $49/mo (annual) or $55/mo (monthly), 50
GB/month included, $0.30/GB overage beyond that. Both the issuer and the tier are Director-confirmed facts,
not FinOps estimates.

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

## §3 · Standing infra floor (revised — personal scale, all lines now bounded)

The floor is what the Director pays **before a single backtest is run**. Carried as an expression (LL-61);
the starting config is a *recommendation*, not a ruling. Unlike the pre-pivot draft, **every line now has
either a measured value or a bounded range** — nothing is open-ended quote-only anymore.

```
Monthly_floor = Supabase_plan + Massive_personal_tier + SEC-API.io_personal_tier + CI  (+ Director-time, non-$ below)
```

| Line | Bootstrap (dev, current) | Steady-state (personal tool, live) | Tag |
|---|---|---|---|
| Supabase | $0 (Free — 500 MB DB is ample for scan history/signals at personal scale) | $0–$25 (Free likely sufficient; Pro only if storage/egress grows past Free's quota) | `measured` (prices) / `estimated` (which tier is actually needed) |
| Massive (market data) | $0 (Free, 5 calls/min) | **$29–$199/mo** flat, per data-need tier | `measured` (tiers); which tier confirmed still `unmeasured` |
| SEC-API.io | **already live now, CONFIRMED Personal & Startups** (D-TRADE-026 + D-TRADE-027 — not a future/bootstrap distinction; the subscription is active today, at a now-fixed tier) | **$49/mo** (annual) or **$55/mo** (monthly) + $0.30/GB beyond 50 GB — fully confirmed, nothing left open on this line | `measured` — issuer, paid status, AND tier |
| CI (GitHub Actions) | $0 (free-tier minutes) | ~$0.008/Linux-min beyond free tier — trivial at personal-project CI volume | `estimated` — not re-read this revision; verify before it enters a decision |
| **Floor total** | **≥ $49/mo right now** (SEC-API.io alone, confirmed) | **≈ $78 – $279/mo** (`Massive $29-199 + SEC-API.io $49-55 + Supabase $0-25`) — **the range is unchanged from the prior revision**, since Massive's $199 ceiling already dominated the old $49-239 SEC-API.io spread; pinning the tier narrowed SEC-API.io's own uncertainty without moving the total range. **Only Massive's tier remains open** to collapse this further | mixed |

**The decision-relevant fact for the Director:** this is the first time a floor line has moved from
"assumed $0 / future" to "**a real subscription already being paid today**." Whether that spend is wanted
is a HUMAN/pricing call I don't make — I'm surfacing that it exists, at a known range, not a hypothetical.

**Compare to the pre-pivot floor estimate:** the SaaS-scale draft couldn't even bound the market-data line
(quote-only Business tier + uncapped exchange fees). At personal scale the **entire floor is now a bounded,
mostly-measured range under $300/month** — a materially smaller and more knowable number.

**Director's own time is a real cost (§1.8 / profile), stated not dollarized:** every lock, review and
approval this model asks for (`<2.1>` tier/key confirmations, each guard cap value) consumes Director time.
It has no `$/hour` rate on record, so it is carried as a **named HUMAN input**, not a free good.

---

## §4 · What the spend guard must do given this model (hand-off to `governor-spec.md`)

1. **Track GB-downloaded-this-month against SEC-API.io's 50/100 GB included volume** — the one concrete,
   measured per-use overage line in the current provider set (§2.3).
2. **Track call-count against Massive's tier limits** (a concern mainly on the Free/Basic tier; paid tiers
   are unlimited-call flat subscriptions, §2.2).
3. **Block, don't silently proceed,** when a tracked quota would be breached (§2 of `governor-spec.md`) —
   the mechanical PARTIAL leg.
4. **No LLM meter** — there is nothing to meter in Phase 1 (§2.1).
5. **No reconciliation-vs-invoice oracle** — a monthly human glance at the Massive/SEC-API.io/Supabase
   dashboards against the guard's own tally is the right-sized replacement (§3 of `governor-spec.md`).

---

## §5 · Open items surfaced to the Lead (dollars only; I do not rule these)

- 🟡 **Confirm which Massive tier the account is on** (Free/Starter/Developer/Advanced) — Data-Eng/DevOps
  technical discovery, not a Director dollar call, but it sets the real floor number.
- 🟢 **DELETED, not resolved (D-TRADE-028):** the "historical options-chain data / paid add-on" open item
  is moot — `<1.1>` drops options entirely. No longer tracked; removed rather than left as a stale line.
- 🟢 **CLOSED by D-TRADE-026 + D-TRADE-027 — no further FinOps action.** SEC-API.io is confirmed
  Personal & Startups: $49/mo (annual) or $55/mo (monthly), 50 GB included, $0.30/GB overage. Both the
  issuer and the tier are now Director-confirmed facts, not estimates.
- 🟢 **Resolved by the pivot itself (no further FinOps action needed):** the old 🟠 "market-data is
  quote-only, not $199" escalation — that was a commercial-SaaS-tier problem; `<1.2>` personal use very
  plausibly uses the correct, cheapest, already-published tier. SecOps is confirming compliance; I have
  no open dollar question here anymore.
- **Cost model D-TRADE-004 stands, re-scoped to personal scale** — no new lock action needed per the Lead's
  message; this doc + `governor-spec.md` implement it at the right size.

---

## §6 · Provenance (source + read-date for every `measured` figure — re-verify before use)

| Figure | Source | Read-date |
|---|---|---|
| Supabase plans + overage unit prices | `https://supabase.com/pricing` | 2026-08-01 |
| Massive (Polygon) self-serve stock tiers | `https://massive.com/pricing` (`polygon.io/pricing` 301→ here) | 2026-08-01 |
| Polygon→Massive rebrand; both API hosts live | SecOps `docs/security/tos-taint-review.md` §Provider 2 (its own sources cited there) | 2026-08-01 |
| EDGAR free + 10 req/s + UA rule | SEC "Accessing EDGAR Data" + SecOps `tos-taint-review.md` §Provider 1 | 2026-08-01 |
| SEC-API.io tiers, included volume, $0.30/GB overage | `https://sec-api.io/pricing` — independently re-verified this revision (upgraded from canonical's `estimated` range to `measured`) | 2026-08-01 |
| In-hand key CONFIRMED live SEC-API.io (not free EDGAR, not a different reseller) | D-TRADE-026: Lead's direct authenticated `https://api.sec-api.io` call (HTTP 200, real filing data) + Director's own logged-in account, cross-checked, key value never read/logged | 2026-08-01 |
| Confirmed tier: Personal & Startups (not Business) | D-TRADE-027: Director confirmed directly | 2026-08-02 |
| CI per-minute rate | prior knowledge — **not re-read**, tagged `estimated` | — |
| Frontier LLM token-rate band (historical, superseded) | no longer load-bearing — Phase 1 has no LLM spend (§2.1) | — |

---
*DRAFT — self-checked (gate ②). Routine tier at this scale (protocol 17) — no independent-validation pass
required. Awaiting: `<2.1>` tier/key confirmations (SecOps/Data-Eng), and Director sign-off on the guard's
starting cap posture (`governor-spec.md` §3) when the guard is actually built. Reported to the Lead once, at
completion (protocol 15).*
