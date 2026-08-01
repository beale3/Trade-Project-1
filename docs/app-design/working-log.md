# HELM — design working log (append-only)

Protocol 13: every seat **appends** here (per-lane labelled block); the **Lead absorbs** entries into
`canonical-design.md` and references them by `<x.y>` id. Never re-derive design from this log — it is
history; the canonical doc is truth. Hot-file rebase conflict = append collision → **keep BOTH, yours
last**, remove the three markers (LL-54).

---
### [Lead · 2026-08-01] Founding
- Two-document discipline started at founding per LL-33 (design is thin — that is expected).
- `canonical-design.md` seeded with `<1.1>` (product) as `▸ NOT DECIDED` — the blocker for real feature
  design. Strawman recorded there for the Director to react to.
- Money-truth chokepoint `<3.2>` declared as the high-invariant surface (D-TRADE-008); its invariant
  checklist locks before W1 build.
- Awaiting Director: product paragraph `<1.1>`, providers `<2.1>`, cost-model + roster locks, B9 run/skip.

### [Lead · 2026-08-01] Director ruling + asset intake
- **D-TRADE-010 (Director):** NO code build / no wave dispatch is authorized — foundation phase only.
  Propagated to stage-plan (banner + W0), foundation/README §3, open-items-ledger §B/§D.
- **Asset intake — `..\Trade\`:** a stub repo the Director asked me to pull in. Contents = a **SEC EDGAR
  API key** setup (`sec_api_key.txt.template` + a gitignored real `sec_api_key.txt`, 77 bytes — contents
  NOT read; the real key was never committed, good hygiene). Absorbed into canonical `<2.1>`: EDGAR is the
  in-hand anchor provider; the key stays out of this repo and goes to the secret store at B5.
- No other content in `..\Trade\` (no design, no code) — it is purely the key holder.

<!-- append below this line -->

### [Architect · 2026-08-01] Spawn + onboarding — HOLDING
- **Principal Architect LIVE** (clone `Trade - Architect`, branch `main`, Fable5·Max — sole frontier
  seat). Onboarded in read-order: charter (protocols 1–19 · §4.5 legend · LIVE BOARD) → decisions-log
  (D-TRADE-001..016) → canonical-design → my `oracle-boundary` row (PARTIAL) → PROFILE → stage-plan +
  gate-spec. Claimed my board row.
- **Posture = HOLD, correctly.** Product `<1.1>` = ▸ NOT DECIDED and D-TRADE-010 bars all build/wave
  dispatch → there is nothing to architect yet. An ADR authored now would rest on an undefined product;
  I will not manufacture one. First work on `<1.1>` landing (+ B9 if the Director runs it): the **W1
  CORE-SPINE A0 ADR** — transport · request-context/tenant · auth · DB adapter (Supabase
  `zyscsnhiymitpfdhjuci`) · the money-truth chokepoint `<3.2>` one-way-door surface, its invariant
  checklist locking with QA+SecOps+FinOps before build.
- **Setup note surfaced to the Lead (protocol 11):** the `Trade - Architect` clone directory was **empty**
  on spawn despite D-TRADE-016 seating the row — I cloned fresh from origin (`db3f4a6`, verified on
  `origin/main`, clean). Not a blocker; flagged so the stand-up gap is on record.
- No design content authored (my write-lane is `docs/adr/**` + this log; only the Lead edits the canonical
  doc). Awaiting Lead dispatch.

### [AIQ · 2026-08-01] Spawn · onboarded · eval methodology draft (HOLD)
- **Live + onboarded.** Clone `Trade - AIQ` was empty on spawn → cloned `beale3/Trade-Project-1`
  (origin/main @ `0ec2358`, D-TRADE-014); `pull --rebase` clean. Read in order: charter → decisions-log →
  canonical-design → my `oracle-boundary` row (VERIFIER) → PROFILE. Board row claimed. **HOLDING** per
  D-TRADE-010: `<1.1>` NOT DECIDED and no AI/ML output exists yet → no golden set can honestly exist.
- **Light prep (methodology only, no eval set — the fabrication line held):** drafted
  `docs/eval/methodology-draft.md` — a proposal for the **Lead to absorb**. It fixes the eval *method*
  before any output exists: freeze-before-measure/pin the commit (LL-41) · accuracy-vs-consistency as
  separate claims + blind write-once ground truth (LL-40) · pre-register write-once before the run (LL-44)
  · catch-matching against a shared reason-vocab co-authored with AI/ML (LL-42) · fresh-draw is the honest
  number, same-set re-seal is labelled confirmation only (LL-43) · void-on-contamination (LL-47) ·
  builder≠judge. Contains a **placeholder** reason-vocab skeleton (structural buckets, NOT product claims).
- **Nothing to grade, nothing fabricated.** No golden items, thresholds, or accuracy numbers authored.
- **Instantiation blocked on (for Lead visibility):** ① `<1.1>` product · ② `<3.4>` engine + first sealed
  outputs · ③ reason-vocab co-authored w/ AI/ML · ④ Director rubric ratification · ⑤ named blind
  ground-truth expert · ⑥ providers `<2.1>` for source-of-record grounding. Reported once to Lead.
