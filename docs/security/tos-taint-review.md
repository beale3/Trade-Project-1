# Provider ToS-as-taint review — HELM (`trade`)

**Author:** SecOps (SecurityOps Lead) · **Date read/authored:** 2026-08-01 · **Task:** first pre-build
ToS-taint review under D-TRADE-010 (allowed foundation work — no code build).
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

## Provider 1 · SEC EDGAR — taint: **LOW (data)** / operational-compliance HARD

**Sources (read 2026-08-01):**
- SEC.gov — "Accessing EDGAR Data" (fair-access section):
  `https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data` · **page Last-Modified:
  Fri, 31 Jul 2026 21:31:25 GMT** (HTTP header, captured at read).
- SEC.gov Webmaster FAQ / Internet Security Policy (cross-referenced from the page above).
- **Live confirmation of the policy:** an undeclared automated fetch of these SEC pages returned **HTTP 403**;
  the same request with a **declared User-Agent** (`ShupeCapital HELM SecOps … bealearthur@gmail.com`)
  returned **200**. The fair-access gate is real and enforced at the edge — this is not a paper policy.

**What EDGAR VOLUNTEERS (verbatim):**
- *"Anyone can access and download this information for free"* → EDGAR filings are **public-domain U.S.
  government works**. **No IP / redistribution / display / derivative-works restriction on the data itself.**
  (This is the crucial contrast with Polygon below.)
- *"Current max request rate: 10 requests/second."*
- *"The SEC does not allow botnets or automated tools to crawl the site. Any request that has been identified
  as part of a botnet or an automated tool outside of the acceptable policy will be managed to ensure fair
  access for all users."*
- *"Please declare your user agent in request headers:  Sample … User-Agent: Sample Company Name
  AdminContact@<sample company domain>.com"*
- *"SEC reserves the right to limit request rates to preserve fair access for all users."*
- Enforcement (SEC published behaviour): exceeding the rate or using an undeclared tool → the originating
  IP(s) are throttled/blocked; access resumes after the rate stays under threshold (~10 min).

**Taint verdict — LOW data-taint, HARD operational constraint.** Filings are freely redistributable, so
EDGAR *reduces* product risk versus market-data vendors. But three volunteered constraints are HARD and
must bind the ingestion design **before** anything is built on the in-hand key (`<2.1>`):
1. every EDGAR request carries a **declared User-Agent** identifying ShupeCapital + an admin email;
2. **global rate ≤ 10 req/s** (regardless of machine count — a fleet does not multiply the budget);
3. all EDGAR/`sec.gov` egress lives in **one sanctioned Data-Eng ingestion module** (so the UA + rate
   discipline is single-sourced, not re-implemented per caller).
Token/credential failure must be **loud + fail-closed** — an EDGAR job that is rate-blocked stops and says
so, never silently under-ingests.

> **Note on "SEC API key":** the Director holds a key in `..\Trade\sec_api_key.txt` (77 bytes, gitignored,
> never committed — good hygiene). EDGAR's own fair-access endpoint is **UA-based, not key-based**, so a
> 77-byte key most likely belongs to a **third-party EDGAR API** (e.g. an `sec-api.io`-class reseller). If
> so, **that reseller's ToS governs the data** and must be reviewed before build (a reseller commonly adds
> redistribution/query-cap terms that public EDGAR does not). **BLOCKER-CANDIDATE for the Director/Data-Eng:
> confirm which service the key authenticates** — I did not read the key (B5) and cannot infer its issuer
> from the byte count. Verdict above assumes direct public EDGAR; a reseller re-opens the taint question.

**Leg T rule (SEC/EDGAR):** all calls to `*.sec.gov` / the EDGAR host (and any third-party EDGAR reseller
host, once identified) are permitted **only** from the sanctioned Data-Eng ingestion module; a declared
User-Agent is mandatory; an EDGAR host call from any other module, or with a missing/undeclared UA, **FAILS**.

---

## Provider 2 · Polygon.io / Massive — taint: **HIGH** 🟠 (headline finding — Director + Legal decision required)

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

**Recommendation to the Director (react, don't obey):** before Polygon/Massive is confirmed in `<2.1>`,
resolve, in this order — (a) **tier:** only the **Business** tier can support a commercial SaaS; the
individual key in hand (if any) is disqualifying for build; (b) **derivative-works/advice question** →
route "are HELM's signals a licensable investment strategy?" to **Legal → Director** (`<4.3>`); (c)
**real-time vs delayed:** real-time equities/options drag in OPRA/UTP/NYSE agreements + **professional-tier
fees** → price to **FinOps** (D-TRADE-004, real dollars); delayed/EOD or reference data materially shrinks
the SRO surface; (d) **fallback:** if the near-term need is *filings/fundamentals*, **public EDGAR (LOW
taint, Provider 1) covers it with none of these constraints** — consider deferring market-data licensing
until a feature actually needs quotes.

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

## Cross-provider summary (for the Lead's consolidation)

| Provider | Entity/host state | Volunteered constraint that dominates | Taint | Decision owner |
|---|---|---|---|---|
| SEC EDGAR | stable; UA-based, no key for public EDGAR | 10 req/s cap · declared UA · no undeclared bots · **data is public-domain (redistributable)** | **LOW** (data) / HARD (ops) | Data-Eng design; **confirm the "SEC key" issuer** → Director |
| Polygon / Massive | **rebrand in transit** (polygon.io→massive; both API hosts live) | individual license = **non-commercial, Non-Professional, display-only, no redistribution, no "investment strategy" derivative works**; Business tier still bars derivative works unlicensed; real-time drags in OPRA/UTP/NYSE | **HIGH** 🟠 | **Director** (provider/tier) + **Legal** (`<4.3>` derivative/advice) |
| Supabase | stable; already adopted | **customer bears all credential-security risk**; PHI/cardholder-data lines; no uptime warranty | **MEDIUM** | mechanical (leg K/T + B5); PHI/card line → **Legal** |

**Bright-line propagation (D-TRADE-006):** this review authors the **leg T sanctioned-module rules** and
feeds the **leg K key patterns** (see `key-denylist.md`). Legs arm at their build wave (leg K/T static at
**W0**, egress at **W1**) — SKIP-visible until then (gate-spec). **DevOps wires; GA audits coverage; QA
re-runs the planted negative controls** (builder ≠ judge).

**Escalations flagged to the Lead (protocol 15 — the Lead consolidates & escalates SEV to Director; I do not
go around the Lead):**
1. 🟠 **Polygon/Massive HIGH taint** — the strawman `<1.1>` is incompatible with the individual license and
   needs a Director provider/tier decision + a Legal `<4.3>` derivative-works/advice ruling **before** `<2.1>`
   or any build. (SEV2-candidate; GA/Lead set final severity.)
2. 🟡 **"SEC API key" issuer unconfirmed** — 77-byte key ≠ public EDGAR's UA model; likely a third-party
   reseller whose ToS would re-open the EDGAR taint. Director/Data-Eng to confirm; I did not read the key (B5).
3. 🟡 **Supabase data-classification lines** (PHI/BAA, cardholder-data/approval) — route to Legal if HELM's
   data model will ever touch them (billing may).
