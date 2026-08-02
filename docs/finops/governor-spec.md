# Personal spend guard — spec — HELM (`trade`)

**Owner:** FinOps · **Authored:** 2026-08-01 · **Re-authored:** 2026-08-01 (D-TRADE-020 pivot — re-scale,
not patch, per protocol 19 / LL-19: this replaces the prior SaaS-scale draft in place; the superseded
version is not left alongside it).

**Why re-authored, not patched:** `<1.1>` locked — HELM is a **personal trading-signal tool**, one user
(the Director), no customers, no billing surface (`<1.2>`, `<1.3>`). The re-authored canonical `<3.2>`
**replaces** the SaaS-scale "money-truth chokepoint" with a **lightweight spend guard** — a cap + visibility
layer, explicitly **not** an idempotent multi-writer ledger, a billing-reconciliation oracle, or a
multi-layer (per-call/per-tenant/global) governor. My oracle-boundary row moved **ORACLE → PARTIAL**
accordingly (`docs/gate/oracle-boundary.md`): the only thing that is now mechanically certified is *"a call
that would breach the daily cap is BLOCKED."* Everything about **what the cap should be** stays HUMAN.

**Status:** DRAFT — self-checked (gate ② GROUND). This is a **routine** change at this scale (protocol 17):
a personal spend guard is not a cross-document invariant or an engine rule, so it does **not** require the
independent-validation pass the old SaaS governor did — self-check is the right bar. Reported to the Lead
once, at completion.

---

## §1 · What this guards against (grounded in `cost-model.md`'s re-scoped reality)

At personal scale, **every adopted provider is a flat subscription or a quota-based tier, not a
metered-per-call bill** (Massive personal tier · SEC-API.io personal subscription · Supabase Free/Pro). The
validation engine `<3.4>` is **classical statistics** (walk-forward CV, regression), not generative AI — so
there is **no LLM token spend in Phase 1**, and the old "LLM tokens are the only true per-use COGS" finding
has no subject to govern right now. The realistic failure mode a personal tool needs to guard against is
narrower than a SaaS money-truth surface:

1. **Quota overrun — now a concrete, measured case, not a hypothetical.** Re-verifying SEC-API.io's own
   pricing (`cost-model.md` §2.3) found a real overage line: the Personal tier includes **50 GB/month**
   downloads, then bills **$0.30/GB** beyond it. A bulk historical pull across the whole universe, or a
   retry storm re-fetching the same data, is a realistic way to cross that boundary. Massive's paid tiers
   are flat/unlimited-call, so its equivalent risk is smaller (mainly the Free/Basic tier's rate limit, a
   ban risk rather than a billing risk).
2. **An unconfirmed paid add-on gets silently exercised** — canonical `<2.1>` flags that **historical
   options-chain data (strikes/greeks/IV history)** is not yet confirmed available at the current Massive
   tier; if it turns out to be a metered or higher-tier add-on, a backtest script could trigger it
   unknowingly.
3. **Slow creep**, not a spike — e.g., Supabase storage/egress from a growing scan-history table crossing
   into Pro-tier overage over weeks. Caught by a periodic look, not a per-call block.

**What this guard is NOT:** a certified oracle over correctness of billing (no reconciliation-vs-invoice
requirement), a multi-tenant isolation mechanism (no tenants), or a system that needs to survive concurrent
writers (one user, one process at a time in practice).

---

## §2 · The mechanical leg (PARTIAL — the only certified piece)

**Rule:** before a call to a provider that has ANY per-use/overage pricing dimension, the guard checks
**today's running count/estimated-$ for that provider against a daily cap**; if the call would **breach**
the cap, it is **BLOCKED** (the call does not fire) and a visible note is written (§4). This is checkable —
**negative control:** run the count up to the cap, fire one more call → **it is blocked, not silently
allowed** (a second seat — QA or the Director — can reproduce this by forcing the counter near the cap and
observing the block).

**What is deliberately NOT mechanized (HUMAN, escalates):** the cap **value** itself — that is pricing
judgment (oracle-boundary row, verbatim) — and "should this provider even be called right now" (a
strategy/backtest-design question, not FinOps's).

**Providers this actually applies to today:** given §1, this is mostly a **call-count/quota guard**, not a
dollar meter — most providers have $0 marginal cost *until* a quota boundary, at which point either overage
$ or a block/ban applies. The guard's cap can be expressed as **whichever bites first**: `min(quota_calls,
$_ceiling)` (LL-61 — carry as the expression, not a pre-collapsed single number), re-derived once the
specific tiers (`<2.1>`) are confirmed.

---

## §3 · Cap values (HUMAN — Director sets; FinOps recommends a starting posture, does not rule)

No specific dollar or call-count value is ruled here — that is pricing judgment. **Recommended starting
posture**, to react to:

| Cap | Recommendation | Why | Status |
|---|---|---|---|
| **GB-downloaded-this-month cap, SEC-API.io specifically** | tier is now confirmed **Personal & Startups, 50 GB/month included** (D-TRADE-027) — recommend a headroom cap around **40 GB** (80% of quota), leaving margin before the $0.30/GB overage starts, rather than capping at the exact 50 GB boundary | this is the one **measured, real, currently-active** overage line (`$0.30/GB`, `cost-model.md` §2.3) — issuer AND tier are both confirmed, so this is live spend risk now, not a future contingency | ▸ mechanism + boundary fully known — **this is now an actual value the Director can set**, not just a placeholder; 40 GB is FinOps's recommendation, not a rule |
| Daily call-count cap, Massive | mainly relevant only on the Free/Basic tier (5 calls/min) — a paid tier is flat/unlimited, so this cap matters less once the tier is confirmed | a bug shows up as "blocked/rate-limited" well before a ban | ▸ needs confirmed tier (SecOps/Data-Eng) |
| Daily $ ceiling (backstop) | small — a personal tool's daily run should cost near-$0 if both quotas above hold | catches any overage that slips past the GB/call-count watch | ▸ needs `<2.1>` confirmation |
| Monthly check-in (not a hard cap — a HUMAN habit, not a mechanical leg) | glance at the actual provider bill once a month against the guard's own tally | catches slow creep (§1.3) that a daily cap won't; this is intentionally NOT an armed oracle at this scale — the old billing-reconciliation-with-negative-control machinery is dropped as overbuilt | recommendation only |

**These are starting points, not locks** — the Director may set tighter or looser numbers; either way the
mechanism (§2) is what's certified, not any particular value.

---

## §4 · Mechanism (lightweight — no ledger, no reconciliation oracle)

- **State:** a simple running counter (calls + a rough $ estimate) per provider per day. A flat file, a
  small local store, or a single Supabase table row — implementation is DevOps/SDE1's call at build time;
  this spec does not mandate the storage technology, only the behavior.
- **Read-before-call, write-after-call.** No idempotency guarantee is required (single user, no concurrent
  writers in the normal case); if a write fails, the **conservative default is to treat the day as
  uncounted-safe-guess and block on ambiguity** rather than assume zero spend — cheap insurance, not a
  certified invariant (this is a design recommendation, not a mechanized leg).
- **Visibility, not reconciliation:** the running tally is human-readable at any time (a log line, a small
  printed summary, or a Supabase row the Director can query) so a monthly glance (§3) is easy. There is
  **no automated per-cycle reconciliation against a provider invoice** — that was the SaaS-scale
  billing-reconciliation oracle, explicitly dropped (§5).
- **On block:** the tool stops the call, logs why (which provider, which cap, today's tally), and surfaces
  it — no silent skip. For a personal tool run interactively, this can simply be a printed message; no SEV1
  paging machinery is needed (there's no Director-vs-oncall separation to page across — the Director *is*
  the one running the tool).

---

## §5 · Explicitly DROPPED from the prior SaaS-scale draft (protocol 19 — named, not silently vanished)

| Dropped | Why it doesn't fit here |
|---|---|
| Idempotent, append-only, transactional spend-ledger invariants | sized for concurrent multi-tenant writers; one user running one script at a time doesn't need it |
| Billing-reconciliation oracle (ledger-sum vs. provider invoice, armed with a negative control) | a certified oracle is overhead a human glancing at their own bill once a month replaces at zero engineering cost |
| 3-layer caps (per-call / per-tenant / global) + a latching `$/day` auto-kill with SEV1 paging | no tenants; one daily cap (§2/§3) is the whole surface; "paging" collapses to "the tool prints why it stopped" |
| BE-Data-owned chokepoint invariant checklist co-signed by SDE1/QA/SecOps/FinOps at a locked W1 gate | still useful in spirit (a light checklist before the guard goes live is fine) but doesn't need the SaaS multi-seat lock ceremony — see §6 |
| FinOps tier = ORACLE | moved to **PARTIAL** (`oracle-boundary.md`, D-TRADE-020) — only the block-on-breach behavior is mechanical; the cap value is HUMAN |

---

## §6 · Light co-check (right-sized replacement for the old checklist)

Before the guard goes live on a real key: **FinOps confirms the cap logic behaves per §2's negative
control; one other seat (QA, or the Director directly) reproduces the block.** That's the whole ceremony at
this scale — no multi-seat sign-off matrix needed for a single-user tool.

---

## §7 · Open items (dollars/mechanism only; I do not rule these)

- ▸ **Cap values need `<2.1>`'s tier confirmations.** SEC-API.io is now fully confirmed (D-TRADE-026/-027,
  §3) — that cap can be set today. **Only Massive's tier remains open**; SecOps/Data-Eng own confirming it,
  and the options-chain-data add-on status. FinOps converts the confirmed Massive quota into the
  `min(quota_calls, $_ceiling)` expression once it lands.
- 🟡 If **historical options-chain data** turns out to require a paid add-on or a higher Massive tier
  (canonical `<2.1>`, still NOT DECIDED), that's a new floor line for `cost-model.md`, not just a guard
  parameter — flag back to me when confirmed.
- Recommend the Director simply **glance at the guard's own log** during Phase 1's first few real runs to
  sanity-check the estimate against the actual provider dashboard once, before trusting the tally long-term.

---
*DRAFT — self-checked (gate ②), routine tier (protocol 17 — no independent-validation pass required at this
scale). Supersedes the SaaS-scale governor-spec content in place (protocol 19); nothing from the prior
version is parked elsewhere. One report to the Lead at completion (protocol 15).*
