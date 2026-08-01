# Provider ToS-as-taint review — HELM (`trade`)

**Author:** SecOps (SecurityOps Lead) · **Date read/authored:** 2026-08-01 · **Task:** first pre-build
ToS-taint review under D-TRADE-010 (allowed foundation work — no code build).

> **2026-08-01 — UPDATE (D-TRADE-020 personal-tool pivot; Lead's re-scoped confirm task).** Two things
> changed since the original review below: (1) the Director's product pivot **de-risks** the Polygon/
> Massive HIGH finding — see the new verdict note in Provider 2; (2) **I confirmed, first-hand, that the
> in-hand key is a SEC-API.io token, not direct public EDGAR** — Provider 1 below is **re-authored** (not
> patched-beside) to reflect this; the direct-EDGAR fair-access facts are kept only as background context,
> not as the operative taint verdict. **A new credential-exposure finding surfaced during this
> confirmation** — see the flag at the end of Provider 1. Method unchanged: LL-58/62 citation discipline;
> verify-don't-attest (I did not take the Lead's SEC-API.io note on faith — I found the three scripts that
> load the key and call `api.sec-api.io` myself, in `C:\Users\beale\float-study\`).
**Method (binding on this doc):**
- A constraint the vendor **VOLUNTEERS** (what it says it CANNOT / WILL NOT do, or forbids *you* from
  doing) **outweighs any capability it ADVERTISES** (protocol 16 / LL-62). This review reads the
  *prohibitions*, not the feature list.
- Every reading is **a claim with a basis**: source URL · read-date · document revision (LL-52 / LL-58).
  A terms check without its citation cannot be re-verified at action time.
- **Boundary honesty:** the *mechanical* output of this seat is the **sanctioned-module rule for gate leg T**
  and the **key patterns for gate leg K** (authored here, wired by DevOps, audited by GA, re-run by QA —
  builder ≠ judge). **"Which providers are acceptable" and "is this credential/terms-reading design sound"
  stay HUMAN and escalate to the Director** (my oracle-boundary row). Verdicts below are **recommendations
  to the Director**, not rulings.

Taint scale used: **HIGH** (a volunteered constraint materially collides with the strawman product
`<1.1>` / requires a Director or Legal decision before build) · **MEDIUM** (bounded duty pushed onto us;
mechanically confinable) · **LOW** (operational-only; data itself is unencumbered).

---

## Provider 1 · SEC-API.io (the actual in-hand key) — taint: **LOW** (personal-use reseller tier)

> **Re-authored 2026-08-01** — the original version of this section assumed the in-hand key was for
> direct public EDGAR. That assumption was wrong; corrected below (LL-19: re-author, don't patch beside
> stale text). The prior open item ("confirm which service the key authenticates") is now **CLOSED**.

**Identity — CONFIRMED first-hand, not by citation of the Lead's note (verify-don't-attest):** I read
`C:\Users\beale\float-study\cadence_check.py`, `pull_all_float.py`, and `test_structure_check.py` — all
three load `C:\Users\beale\Software Dev\Trade\sec_api_key.txt` and pass its contents as the `token` param
to `https://api.sec-api.io/float`. **The in-hand key is a SEC-API.io token — a paid commercial reseller
built on top of EDGAR data, not direct/free public EDGAR access.** I did not read or copy the key value
itself (B5); identity was established from the *code that calls it*, not the secret.

**Sources (read 2026-08-01):**
- SEC-API.io pricing page — `https://sec-api.io/pricing` (tier/usage/redistribution table).
- `C:\Users\beale\float-study\FLOAT_STUDY_PHASE1_FINDINGS.md` §0 (prior first-party research on the same
  question, corroborates: *"SEC-API.io doesn't expose an account/plan-info endpoint … [to] check this
  directly"* — same limitation I independently hit trying to confirm Massive's tier, see Provider 2).
- SEC.gov fair-access facts (kept as background — SEC-API.io's underlying data is still EDGAR filings,
  and the direct-EDGAR facts below remain true of the *source*, just not of *this key's* access path):
  `https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data` (Last-Modified: Fri,
  31 Jul 2026 21:31:25 GMT); live-confirmed 10 req/s cap + mandatory declared User-Agent + no undeclared
  bots (undeclared fetch → 403, declared UA → 200); filings themselves are public-domain U.S. government
  works, no redistribution restriction *on the underlying filing content*.

**What SEC-API.io VOLUNTEERS (verbatim, pricing page):**
- Tier usage column: **"Personal & Startups: `Personal. For startups: business internal.`"** ·
  **"Business Internal Use: `Business internal only.`"** · **"Enterprise & Institutions: `Business internal
  + redistribution and reselling.`"**
- *"If you're looking for a redistribution license, multiple API keys per account, priority level 1
  support, or unlimited data volume, please contact us"* — redistribution is an **Enterprise-only**
  add-on; **neither** self-serve tier ($49–55/mo Personal, $199–239/mo Business-Internal) includes it.
- Rate limits scale by tier (Query API: 20 req/s Personal → 40 req/s Business-Internal → custom
  Enterprise); a Terms of Service page exists at `/policies/terms-of-service` (JS-rendered; substantive
  clauses not machine-readable via WebFetch — noted as a residual gap, not chased further given the
  Lead's "light confirmatory check" scope).

**Taint verdict — LOW, matching Massive's pattern.** Whichever self-serve tier is active (Personal or
Business-Internal — **exact tier still UNCONFIRMED**, same limitation the float study hit: SEC-API.io
exposes no plan-info endpoint, and I will not guess), **both sub-Enterprise tiers explicitly exclude
redistribution** — the vendor's own tier-gating volunteers that personal/internal use is the compliant,
paid-for lane, and reselling requires a contract neither tier holds. This is compatible with `<1.2>`
(personal use only, no distribution). **Cost note for FinOps (D-TRADE-019 reframe):** this is a **paid
personal-tier subscription ($49–239/mo)**, not the $0.00-marginal free EDGAR FinOps's cost-model assumed —
flagging for FinOps to correct, not ruling on the dollar figure myself.

**Leg T rule (SEC-API.io):** the SEC-API.io key and all calls to `api.sec-api.io` are permitted **only**
from the sanctioned Data-Eng ingestion module; a call to that host from any other module **FAILS**. (The
direct-EDGAR UA/rate discipline above is retained as a **secondary** rule only if a future build ever adds
*direct* `sec.gov` calls alongside SEC-API.io — not currently in play.)

---

### 🔴 Credential-exposure finding (surfaced during this confirmation — flag to Director, not mine to fix)
While tracing which scripts call the key (to establish identity above), I found that
**`C:\Users\beale\float-study\log_pull.txt` contains a live SEC-API.io token value in plaintext**, 4
occurrences, inside failed-DNS-resolution exception tracebacks (`requests` couldn't resolve `api.sec-api.io`
at pull time, so the exception text — which includes the full request URL with the `token=` query param —
got written to the log verbatim). **I am not repeating the value here or anywhere else** (B5 discipline
applies even to values I encounter incidentally, not just ones I'm handed).
- **Scope:** local filesystem only, `C:\Users\beale\float-study\`, **outside this git repo** — leg K
  (which scans this repo's tracked files) does not and cannot see it; this is a personal-machine hygiene
  gap, not a repo violation.
- **Why it matters (my mandate — key/credential security, not scoped only to the repo):** a plaintext
  token sitting in a log file is a real, live secret at rest with no access control beyond the filesystem
  — "real credentials at n=1 are still real credentials" (SecOps lessons block).
- **Recommendation to the Director (I don't hold B5 authority to act on this myself):** (1) treat the
  SEC-API.io token as exposed and **rotate it**; (2) delete or redact the `token=` value from
  `log_pull.txt` (and check other study folders' logs for the same pattern — I only found it in
  float-study; regime/catalyst/short-interest do not reference SEC-API.io at all, confirmed by search).

---

## Provider 2 · Polygon.io / Massive — taint: **re-scoped LOW-MEDIUM** (was HIGH; personal-tool pivot de-risks it — see update below)

> **2026-08-01 UPDATE (D-TRADE-020 pivot + Lead's re-scoped confirm task).** The HIGH verdict below was
> **scoped to commercial/SaaS use** (canonical `<2.1>`, per the Lead). `<1.1>`/`<1.2>` now lock HELM as
> **personal use only, no distribution** — which is *exactly* the individual/"Non-Professional" tier's own
> definition (§3 below: *"any natural person who receives market data solely for their own personal,
> non-business use"*). The four incompatibility counts I found (commercial use, Professional status,
> redistribution, "investment strategy" derivative works) **do not apply to a tool the Director alone runs
> for the Director's own trading decisions.** The original research (verbatim ToS text, the rebrand/dual-host
> fact, the OPRA/UTP/NYSE schedules) **stays valid** — only the applicability verdict changes.
>
> **What I confirmed for the Lead's re-scoped task ("is the account actually on that tier") — via the live
> Massive MCP connector, read-only, zero secret handling:**
> - No self-serve "my plan/subscription" endpoint exists in Massive's API (`search_endpoints` returned no
>   account/entitlement lookup) — **mechanical tier confirmation is not obtainable via the API itself**, same
>   limitation SEC-API.io has (see Provider 1). This is a real boundary, not an oversight on my part.
> - **Technical entitlement evidence gathered (2 cheap, single-ticker calls):** `/v2/last/nbbo/AAPL`
>   (real-time NBBO) returned **`NOT_ENTITLED`**; `/v2/snapshot/…/AAPL` returned populated **previous-day**
>   EOD fields but **all-zero current-day/intraday** fields. Both are the signature of a **non-real-time,
>   delayed/EOD-class self-serve tier** — i.e., **not** a real-time Developer/Advanced tier and not a
>   business/enterprise contract (which would carry real-time entitlement). This is genuine corroboration,
>   not proof of the exact plan name.
> - **What remains HUMAN-only:** the account's literal plan name / billing type (individual vs any
>   business paperwork) lives on the Massive account dashboard, reachable only by the Director's own login
>   — no API surface exposes it. **Recommendation: a 30-second Director glance at massive.com → Account →
>   Billing** would fully close this; the entitlement evidence above already substantially corroborates the
>   individual-tier read and I do not consider this a blocker to Phase 1 start.
> - **Verdict: re-scoped to LOW-MEDIUM.** LOW on the applicability question (personal use matches the
>   individual tier's own definition); MEDIUM residual only because the *exact* plan name is
>   Director-confirm-only, not because any incompatibility was found. **`<4.3>`** (is this regulated
>   advice/a licensable strategy) stays the Director/Legal's light-touch call per the canonical re-scope —
>   not reopened by me.

<details><summary>Original HIGH-taint research (commercial-use framing) — kept for its verbatim ToS text and citations; verdict above supersedes the headline call below</summary>

**(Historical framing note: the analysis and quotes below were written when `<1.1>` was an undecided
commercial-SaaS strawman. The ToS text, rebrand facts, and exchange-agreement findings are still accurate
and still inform leg T; only the "HIGH taint, build-blocking" framing is superseded by the update above.)**

**Sources (read 2026-08-01):**
- **Polygon.io, Inc. Market Data Terms of Service — "Last Updated: October 9, 2024"** — full PDF read
  verbatim: `https://massive.com/terms/market_data_terms.pdf` (this is what `polygon.io/terms` now serves).
- **Massive for Businesses Terms of Service — "Last Updated: September 2, 2025"** —
  `https://massive.com/legal/businesses-terms-of-service` (`polygon.io/legal/businesses-terms-of-service`
  **301-redirects** here).
- Rebrand announcement — "Polygon.io is now Massive," effective **2025-10-30 16:00 ET**
  (`https://massive.com/blog/polygon-is-now-massive`).

**Entity/host in transition (a taint fact in itself):** Polygon.io, Inc. **rebranded to "Massive"**
(effective 2025-10-30). `polygon.io/terms` and `polygon.io/legal/*` now **301 → `massive.com/*`**. The legal
entity is still **"Polygon.io, Inc."** in the Market Data ToS (and "Polygon, LLC" in the NYSE schedule).
**Both API hosts are live in parallel: `api.polygon.io` AND `api.massive.com`.** ⇒ leg T must sanction
**both** hosts, and the ingestion module must **pin whichever host is chosen** so the taint surface is one
place, not two.

**What Polygon VOLUNTEERS (verbatim — the individual/default Market Data ToS, Oct 9 2024):**
- §1 Permission: license is *"exclusively for your personal, non-business, and non-commercial purposes. For
  the avoidance of doubt, you may not use the Market Data for any business or commercial purpose, and you may
  not use the Market Data to build an application intended for use by end users other than you."*
- §2: *"any and all Market Data is strictly for display use only"* (absent a subsequent agreement).
- §3 Subscriber Classification: data is provided on your warranty that you are a **"Non-Professional"** —
  *"any natural person who receives market data solely for their own personal, non-business use."* A
  **"Professional"** includes anyone *"engaged as an 'investment advisor'"* or registered with the SEC/CFTC.
  *"Any use of Market Data for business, professional, or other commercial purposes is incompatible with
  Non-Professional status."* → **an organization / a SaaS cannot hold this license.**
- §5(c): you may not *"Redistribute, display, disseminate, … sell, resell, rebrand, or otherwise transfer the
  Market Data—or any … analytics, research, or other works based on, referring to, or derived from the Market
  Data ('Derived Works') — to any third party or use the Market Data for business or commercial purposes."*
- §5(d): you may not *"create derivative works (including … any index … investment product, financial
  contract … settlement value or **investment strategy**) based on the Market Data unless you are licensed to
  do so."*
- Real-time equities/options auto-incorporate **exchange subscriber agreements** — OPRA, **Nasdaq/UTP**,
  **NYSE** — as binding schedules; the SROs are **third-party beneficiaries who may enforce directly** and
  recover attorney's fees (NYSE Sched. 2 §3). NYSE §5: *"Subscriber shall not furnish Market Data to any
  other person or entity."*
- §9 liability capped at **USD 1000**; §10 on termination you must **delete all Market Data in your
  possession.**

**What the Business tier (Sept 2 2025) changes — and does NOT:**
- §6.1(e) permits redistribution/display **to "Edge Users"** (defined as *"users of Customer's products and
  services"*), under a license to *"access, receive, process, transmit, store, and use the Information …
  solely for its use in websites or software applications owned or licensed by Customer."* → a commercial
  SaaS surface becomes possible **on this tier**.
- **BUT** §6.1(j) **still prohibits** creating derivative works — *"any index … investment product, financial
  contract … or investment strategy … unless licensed to do so."*
- §2.5(a): *"Customer may be required by the applicable Third-Party Provider … to enter into Third-Party
  Agreements"* for Third-Party Data (i.e. the exchange/SRO agreements + possible professional-tier fees).
- Credential duty on Customer: *"Customer must prevent any Credential Compromise, and otherwise ensure that
  its account and API Credentials are not used or modified by anyone other than Customer or its Authorized
  Users."* → the Polygon/Massive key is a B5 secret; leg K + B5 discharge this.

**Taint verdict — HIGH (🟠 SEV2-candidate; severity is GA/Lead's call, not mine).** The strawman product
`<1.1>` — *"a SaaS that … produces AI-assisted trading/analysis signals for ShupeCapital"* — collides with
the **individual/default** Polygon license on **four independent counts**: (1) commercial use, (2)
Professional status (ShupeCapital / an investment context is Professional), (3) redistribution to third
parties (a SaaS's users are third parties), (4) *"investment strategy"* derivative works. Building HELM on a
**personal Polygon key would breach the terms four times over.** This is the exact case where a **volunteered
constraint outweighs the advertised "comprehensive market-data API"** (LL-62).
- The **Business tier removes counts (1)–(3)** but **not (4)**: whether "AI-assisted trading signals" are a
  licensable *"investment strategy / investment product"* derivative work is a **Legal judgment** that ties
  directly to `<4.3>` (regulated-advice line) — **HUMAN, escalates to Director via Legal.**
- **"Which providers are acceptable" is my HUMAN-escalate column** — I do **not** rule Polygon in or out.
  I surface the terms so the Director decides `<2.1>` with the constraint in hand.

**Recommendation to the Director (superseded by the pivot — kept for record only):** ~~before Polygon/
Massive is confirmed in `<2.1>`, resolve, in this order — (a) tier: only the Business tier can support a
commercial SaaS…~~ **No longer operative** — see the update at the top of this section. The one part that
survives the pivot: real-time-vs-delayed remains a real cost/entitlement fact (confirmed above: this
account is delayed-tier, not real-time), and options-chain-data availability at this tier is still an open
**technical** (not taint) question for DevOps/Data-Eng per canonical `<2.1>`.

</details>

**Leg T rule (Polygon/Massive):** the Polygon/Massive SDK/client **and its API key** are usable **only**
from the sanctioned server-side data layer (the money-truth/ingestion module, Lane 2) — **never** in
`apps/web`, never client-exposed. A `polygon`/`massive` SDK import, or a call to `api.polygon.io` /
`api.massive.com`, from any module outside the sanctioned data layer (esp. `apps/web`) **FAILS** (matches
gate-spec leg T). *Display-only + no-derivative-works posture cannot be fully mechanized by leg T — it is a
Legal/design constraint carried in `<4.3>` and enforced by review, with host-confinement as the mechanical
floor.*

---

## Provider 3 · Supabase — taint: **MEDIUM** (credential-duty on us; mechanically confinable)

**Sources (read 2026-08-01):**
- Supabase **Terms of Service** — `https://supabase.com/terms` (version header present; no explicit date in
  body at read).
- Supabase **Acceptable Use Policy** — `https://supabase.com/aup` — **"Effective Date: June 1, 2026
  (Version 1)."**
- Prior team record: D-TRADE-013 (project adopted) / D-TRADE-014 (MCP read-only). Reachability verified
  2026-08-01 (`docs/infra/supabase.md`).

**What Supabase VOLUNTEERS (the constraints that bind us):**
- **Credential security is 100% the customer's duty:** Customer is responsible for *"the security and use of
  Customer's and its Authorized Users' access credentials"* and for *"all access to and use of the Services
  … through … its … access credentials, **with or without Customer's knowledge or consent**."* → a leaked
  `service_role` key is entirely on us; **leg K + the B5 gate are how we discharge this duty.**
- **Prohibited use** (ToS §Acceptable Use): reverse-engineering; *"competitive analysis … [or] development …
  of a competing software service"*; *"bypass or breach any security device or protection."*
- **Data-classification lines:** *"Customer may not store or process protected health information (as defined
  in HIPAA) … unless Customer signs a Business Associate Agreement,"* and cannot store payment cardholder
  data *"without Supabase's prior written approval."* → binds Legal/`<4.3>` **if** HELM ever stores such
  data (a financial app may touch cardholder data at billing — flag to Legal + FinOps).
- **Favorable constraint:** Supabase *"will not use, nor allow any third-party to use, Customer Data …
  Customer's AI Input, or any AI Output to train … any … model, without Customer's prior written consent."*
- **Disclaimers:** IP provided *"as is"*; **no uptime warranty** (*"[no warranty] … will … operate without
  interruption"*); liability capped at **12 months' fees**; *"Supabase will have no liability for … a Service
  Suspension."* → availability is not guaranteed; the money-truth path must fail-closed if the DB is down,
  not silently drop ledger rows.
- **AUP (June 1 2026 v1)** additionally forbids: DoS, unauthorized scraping / robots.txt violation, proxy or
  rate-limit bypass, crypto-mining on Edge Functions, disposable-email + bulk-registration abuse, carding /
  storing stolen financial data, port-scanning outside a disclosure program.

**Taint verdict — MEDIUM.** We own our Customer Data, so there is **no redistribution/IP taint** on HELM's
own content. The real, binding taint is a **credential-security duty pushed entirely onto us** plus two
**data-classification lines** (PHI/BAA, cardholder-data/approval) for Legal. Provider acceptability is not in
question — the Director already adopted Supabase (D-TRADE-013/014). The service_role key + DB password are
RLS-bypassing, full-access → **B5 secrets, server-only.** The MCP connector is already scoped **read-only +
single-project** (D-TRADE-014), which is the right least-privilege posture; **opening write is a later
Director-gated change** and must re-enter the B5 gate.

**Leg T rule (Supabase):** `@supabase/supabase-js` **and the `service_role` key / `DATABASE_URL`** are
importable/referenced **only** in the server-side data layer (`packages/db`, the `packages/domain`
money-truth path) — **never** in `apps/web`. The **anon/publishable key (RLS-enforced)** is the **only**
Supabase credential permitted client-side. A `service_role` import or reference in `apps/web` **FAILS**
(matches gate-spec leg T negative control). See the key denylist for leg K patterns.

---

## Cross-provider summary (for the Lead's consolidation) — updated 2026-08-01 post-pivot

| Provider | Entity/host state | Volunteered constraint that dominates | Taint | Decision owner |
|---|---|---|---|---|
| **SEC-API.io** (confirmed identity of the in-hand key) | stable; no plan-info API | redistribution is **Enterprise-only**; both self-serve tiers ($49/$199) are internal/personal-use only — matches `<1.2>` | **LOW** | closed by me; exact sub-tier is a Director-optional glance, not a blocker |
| Polygon / Massive | rebrand complete (polygon.io→massive; both hosts live); **entitlement-confirmed delayed/non-real-time tier** | individual "Non-Professional" tier = personal/non-business use, matches `<1.2>` exactly; real-time/exchange-fee/derivative-works constraints only bite under commercial use, which is now off the table | **LOW-MEDIUM** (was HIGH — commercial-use scoping only) | closed by me for applicability; exact plan-name is Director-optional glance |
| Supabase | stable; already adopted | **customer bears all credential-security risk**; PHI/cardholder-data lines; no uptime warranty | **MEDIUM** | mechanical (leg K/T + B5); PHI/card line → **Legal** (unchanged by pivot) |

**Bright-line propagation (D-TRADE-006):** this review authors the **leg T sanctioned-module rules** and
feeds the **leg K key patterns** (see `key-denylist.md`). Legs arm at their build wave (leg K/T static at
**W0**, egress at **W1**) — SKIP-visible until then (gate-spec). **DevOps wires; GA audits coverage; QA
re-runs the planted negative controls** (builder ≠ judge).

**Escalations flagged to the Lead (protocol 15 — the Lead consolidates & escalates; I do not go around the
Lead) — updated post-pivot:**
1. ✅ **CLOSED — Polygon/Massive taint re-scoped LOW-MEDIUM.** The D-TRADE-020 personal-tool pivot resolves
   the commercial-use incompatibility that drove the original HIGH verdict; entitlement checks (real-time
   NBBO refused, intraday snapshot fields zeroed) corroborate a non-commercial delayed-tier account. Residual:
   Director may optionally glance at the account dashboard to confirm the exact plan name — not a blocker.
2. ✅ **CLOSED — "SEC API key" issuer CONFIRMED = SEC-API.io**, first-hand (found the calling code myself,
   did not read the key). Re-scoped LOW; redistribution is Enterprise-only on that provider too, matching
   `<1.2>`. FinOps should reprice this as a paid $49–239/mo subscription, not $0.00 EDGAR.
3. 🟡 **STILL OPEN — Supabase data-classification lines** (PHI/BAA, cardholder-data/approval) — route to
   Legal if HELM's data model will ever touch them; unaffected by the pivot.
4. 🔴 **NEW — credential exposure found during this confirmation.** A live SEC-API.io token appears in
   plaintext in `C:\Users\beale\float-study\log_pull.txt` (4 occurrences, DNS-failure exception tracebacks).
   Outside this repo, so leg K cannot see it — a personal-machine hygiene gap, not a repo violation. **I did
   not repeat the value anywhere.** Recommend: Director rotates the token + scrubs that log file. See the
   flag inline in Provider 1 above for full detail.
