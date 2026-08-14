# Guardrail v2.1 Specification — §3-§9

Each section below is the confirmed-final text from the review session. §0-§2 and §10-§11 carry
forward from the original v2.0 document with two known exceptions, both noted in `README.md`:
§1's SI-match exclusion rule (superseded by §3's tri-state gate) and §2's "Gain% (Open→High)"
definition (inconsistent with what was actually tested; not yet corrected in source).

---

## 3. SI-Gate (Guardrail v2.1 — Corrected and Split by Price Band)

### 3.1 Definition (unchanged mechanically)

SI-gate condition:
- Days-to-Cover ≥ 3.0
- Evaluated on the nearest prior SI settlement date
- SI-gate state is tri-state:
  - PASS: days-to-cover ≥ 3.0
  - FAIL: days-to-cover < 3.0
  - UNKNOWN: no usable SI record within the lookback window

**Important:** UNKNOWN must not exclude a ticker from the Guardrail universe. It is a third
state, not an implicit FAIL.

### 3.2 Validated universe: $2–$20 (core band)

For $2–$20 names, SI-gate remains a validated structural quality signal.

Using `scan_log.csv` × SI-join (core band, n=805) and the LOO + 5-fold × 30-seed harness:
- Slope (days-to-cover → fwd 1M returns): positive, p<0.05 (slope=0.02034, p=0.0015)
- Spearman ρ: ≈0.25 (Pearson r=0.111 in the first check; Spearman ρ=0.249 in the composite
  backtest re-run — both significant, different metrics)
- LOO vs naive: SI-gate model beats naive baseline (RMSE 0.622 vs 0.625)
- Seed agreement: 30/30 seeds beat naive (100%)
- AUC (binary pass/fail): 0.556 (>0.55)

**Interpretation:**
- SI-gate is retained as a core structural gate for $2–$20.
- FULL PASS in this band (core + SI-gate + tail exclusion + tradability) shows better forward 1M
  behavior than naive and than SI-FAIL/EXTREME_TAIL categories.
- SI-gate is the primary predictive component of the composite in the core band — core-pass
  alone (AUC 0.511) and core+tail without SI (AUC 0.506) are both near coin-flip.

### 3.3 Microcaps: $0.50–$2.00 (tested, not validated)

For $0.50–$2.00 names, SI-gate has now been tested at adequate power and does not validate.

Using the historical backfill (2024–2026, 754 tickers):
- Total SI-matched sub-$2 observations: 8,384 (recount; original estimate 8,386)
- Guardrail-conditioned (gain ≥10%, rel-vol ≥2): 241
- SI-gate pass: 34, SI-gate fail: 207, unknown: 0 (by construction — seeded from the SI file)

Running the same LOO + 5-fold × 30-seed harness on this n=241 conditioned sample (fwd_1m_ret):
- Slope (days-to-cover → fwd 1M returns): -0.638, p=0.785 (not significant)
- Spearman ρ: 0.075, p=0.26 (not significant)
- Seed agreement: 0/30 seeds beat naive (0%)
- LOO vs naive: SI-gate model does not beat naive baseline
- AUC (binary pass/fail): 0.524 (below 0.55 threshold)

**Interpretation:**
- SI-gate for sub-$2 is no longer "provisional pending n ≥ 150" — it has been tested at n=241
  and failed every acceptance criterion.
- There is no demonstrated predictive validity for days-to-cover in the microcap
  Guardrail-conditioned universe.

**Guardrail v2.1 rule change:**
- Do not use SI-gate as a quality gate for sub-$2 names.
- For $0.50–$2.00, SI-gate is informational only: SI-gate state may be displayed, but must not
  be used to suppress, promote, or classify microcaps as FULL PASS vs FAIL.
- Microcap risk control should rely on rel-vol tail classification (>50×) and tradability, not
  SI-gate.

**Population-purity caveat (unreconciled):** the n=241 backfill population shows materially
higher baseline round-trip rates (53.5%) than the scan_log-derived population (14–30%). This
discrepancy has not yet been reconciled. The SI-gate null result should therefore be treated as
corroborating evidence rather than an independently clean replication until this gap is
understood.

### 3.4 Tri-state behavior and implementation

Across all price bands:
- UNKNOWN never auto-drops a ticker from the Guardrail universe. Treated as "no SI
  information," not "fails SI-gate."
- $2–$20: FULL PASS requires SI-gate PASS. SI-FAIL and SI-UNKNOWN are distinct, structurally
  different categories (see §8.5 — they do not behave alike).
- $0.50–$2.00: SI-gate state is logged and displayed, but not used in the composite decision.
  Microcap classification relies on core criteria (price, gain, rel-vol), rel-vol tail (>50×),
  and tradability floor.

### 3.5 Spec language (summary)

SI-gate (days-to-cover ≥ 3.0) remains a validated structural quality gate for the $2–$20
universe and is required for FULL PASS in that band. For $0.50–$2.00 microcaps, SI-gate has
been tested at adequate power (n=241) and does not demonstrate predictive validity; it must not
be used as a gating criterion for microcaps in Guardrail v2.1. SI-gate for sub-$2 is
informational only, while rel-vol tail classification (>50×) and tradability serve as the
primary microcap risk controls. SI-gate supports three states (pass/fail/unknown); UNKNOWN
never excludes a ticker from the universe.

---

## 4. Rel-Vol Tail (Guardrail v2.1 — Validated Risk-Control Component)

### 4.1 Definition

A ticker is classified as EXTREME TAIL if:
- rel_vol > 50×,
- evaluated only among candidates that already clear core criteria:
  - price ∈ [$0.50, $20]
  - gain_pct ≥ 10%
  - rel_vol ≥ 2×
  - baseline_dollar_vol ≥ $250k

This matches the implementation used in all empirical tests. It is **not** evaluated
independently of gain_pct or price band.

Classification is binary: TAIL (rel_vol > 50×) / NON-TAIL (rel_vol ≤ 50×). Rel-vol tail is a
risk-control lever, not a return-lift signal.

### 4.2 Empirical validation (core band and microcaps)

**Core Band ($2–$20)**, from `scan_log.csv` × SI-join (n=4,223):
- Round-trip rate (fwd 1W < -20%): EXTREME TAIL 40.4% vs baseline 14–15%
- 1M median return: EXTREME TAIL -32.2% vs baseline -9.6%

Extreme tail events are structurally dangerous — ~3× higher round-trip rates and much deeper
median drawdowns. Validated risk-control filter for the core band.

**Microcaps ($0.50–$2.00)**, from the historical backfill (n=241 Guardrail-conditioned):
- Round-trip rate: EXTREME TAIL 71.0% vs NON-TAIL 53.5%

Microcaps run hotter overall — both tail and non-tail round-trip rates are elevated relative to
the core band. **The effect size of tail exclusion (difference between tail and non-tail) is
smaller than in the core band**: core-band gap is ~25.9pp / 2.79× ratio; microcap gap is ~17.5pp
/ 1.33× ratio. Tail exclusion remains the strongest validated microcap risk-control lever, even
though SI-gate does not validate for microcaps.

**Cross-reference caveat:** these elevated microcap round-trip rates reflect the same
population-purity discrepancy documented in §3.3; treat the microcap tail results as
corroborating evidence rather than a clean independent replication until that gap is
reconciled.

### 4.3 Role in the composite Guardrail

Rel-vol tail exclusion is a risk filter, not a predictive signal: "avoid catastrophic left-tail
outcomes," not "predict positive forward returns."

Composite behavior:
- FULL PASS requires `rel_vol_tail == False`
- CORE_SI_FAIL and EXTREME_TAIL categories show structurally worse forward returns
- EXTREME TAIL is the worst category in central-tendency and downside metrics — **but has the
  highest outsized-runner rate of any category** (runner≥50%: 8.4% vs next-closest 3.8%;
  runner≥100%: 5.1% vs next-closest 1.6%). This bimodality matches the "Bimodal Momentum" risk
  class described in the original v2.0 document. Tail exclusion is justified because downside
  risk dominates in real trading, not because tail names never produce winners — they produce
  more of them, along with more catastrophic losses.

### 4.4 Implementation rules

- EXTREME TAIL always overrides SI-gate and core-pass classification (even SI-gate PASS cannot
  produce FULL PASS if rel_vol > 50×) — but only among tickers that already cleared core
  criteria; tail is never evaluated independently of them.
- EXTREME TAIL is always FAIL regardless of SI-gate, tradability, or price band.
- Microcaps: tail exclusion is the primary validated risk-control for $0.50–$2.00, replacing
  SI-gate as the structural safety filter.

### 4.5 Spec language (summary)

Rel-vol tail classification (rel_vol > 50×), evaluated only among candidates that already clear
core criteria, is a validated risk-control component across both the $2–$20 and $0.50–$2.00
universes. Extreme tail events exhibit structurally elevated round-trip rates and worse
forward-return central tendency in all datasets tested, but also the highest outsized-runner
rate of any category — a genuinely bimodal risk profile, not simply "worse." Tail exclusion is
mandatory for FULL PASS and serves as the primary microcap risk-control lever. SI-gate cannot
override tail classification.

---

## 5. Tradability Floor (Guardrail v2.1 — Structural Liquidity Requirement)

### 5.1 Definition

A ticker satisfies the Tradability Floor if `baseline_dollar_vol ≥ $250,000`, where
`baseline_dollar_vol = avg_vol_20d × scan_open` (matches the definition used in all empirical
tests — note: *not* prior_close). The Tradability Floor is a structural requirement, not a
predictive signal. It is evaluated before SI-gate and before rel-vol tail classification.

### 5.2 Rationale (structural, not empirical)

The floor exists because Guardrail must avoid recommending tickers that cannot be traded safely,
and execution feasibility is a practical requirement independent of backtest results.

**Important:** the Tradability Floor is *not* justified by historical forward-return behavior.
Testing showed no positive relationship between baseline liquidity and forward returns, and in
some cases the relationship ran the opposite direction. The floor is retained only as a
structural safeguard for real trading, not as a quality filter.

### 5.3 Empirical behavior (clarified)

Empirical testing showed:
- No evidence that higher baseline liquidity reduces round-trip rates (at the exact $250k
  threshold: excluded group round-trip 22.2% vs retained group 22.4% — a wash)
- No evidence that higher baseline liquidity improves forward returns
- No evidence that liquidity strengthens SI-gate or rel-vol predictive behavior (this specific
  interaction was never tested — absence of evidence, not evidence of a tested-and-failed
  relationship)
- In some splits, thin-liquidity names performed *better* than high-liquidity names (sub-$2
  candidates with baseline-$-vol <$50k: 7.7% round-trip vs ≥$50k group's 24.8%; logistic
  regression coefficient on log(baseline_dollar_vol) was +0.57 — positive, i.e. wrong-signed
  relative to a "liquidity protects" hypothesis)

Because of this: the Tradability Floor is not a predictive component, not a return-quality
filter, not a risk-control signal. It is purely structural.

### 5.4 Role in the composite Guardrail

Hard requirement for FULL PASS, CORE PASS, and any ticker considered "tradable."

- Evaluated before SI-gate; a ticker below the floor cannot be FULL PASS even if SI-gate PASS.
- Does not override EXTREME TAIL — tail remains FAIL regardless of liquidity.
- Microcaps: mandatory; SI-gate is informational only; tail exclusion + tradability floor form
  the microcap safety core.

### 5.5 Spec language (summary)

The Tradability Floor (`baseline_dollar_vol ≥ $250k`, using `avg_vol_20d × scan_open`) is a
structural liquidity requirement in Guardrail v2.1. It is not a predictive signal and is not
justified by historical forward-return behavior — testing found no positive relationship, and
in some splits the opposite. It exists purely to ensure execution feasibility. A ticker must
meet the floor to qualify as FULL PASS or CORE PASS. In the microcap universe, where SI-gate
does not validate, the Tradability Floor — combined with rel-vol tail exclusion — forms the
primary structural safety filter.

---

## 6. Composite Scoring (Guardrail v2.1 — Corrected Structural Logic)

### 6.1 Overview

Determines classification as FULL PASS / CORE PASS — SI-FAIL / CORE PASS — SI-UNKNOWN /
EXTREME TAIL / FAIL (core band), or MICROCAP PASS / EXTREME TAIL / FAIL (microcaps).

### 6.2 Required inputs

price, gain_pct, rel_vol, baseline_dollar_vol, rel_vol_tail flag, si_gate_state
(pass/fail/unknown), price_bucket (sub2/core/above20).

### 6.3 Core criteria (entry filter)

A ticker must satisfy all of the following to be eligible for any PASS classification:
1. price ∈ [$0.50, $20]
2. gain_pct ≥ 10%
3. rel_vol ≥ 2×
4. baseline_dollar_vol ≥ $250k (Tradability Floor)

If any core criterion fails → FAIL. SI-gate and tail logic are not evaluated until core
criteria pass.

### 6.4 Rel-vol tail override (risk filter)

A ticker is classified as EXTREME TAIL only if `rel_vol > 50×` **and core criteria have already
passed**. EXTREME TAIL is always FAIL, regardless of SI-gate state, tradability, or price band
(tradability is, by this point, already guaranteed true, since it's part of core criteria).
EXTREME TAIL is not evaluated for tickers that fail core criteria — those are already FAIL.

### 6.5 SI-gate logic (quality filter)

**Core band ($2–$20):** SI-PASS → FULL PASS. SI-FAIL → CORE PASS — SI-FAIL. SI-UNKNOWN → CORE
PASS — SI-UNKNOWN. SI-UNKNOWN is not treated as FAIL.

**Microcaps ($0.50–$2.00):** SI-gate is informational only; does not affect classification.
Microcap classification depends only on core criteria, tradability, and rel-vol tail exclusion.

### 6.6 Composite categories (final classification)

**FULL PASS (core band only):** price ∈ [$2,$20], core criteria pass, tradability passes,
rel_vol_tail == False, si_gate_state == PASS.

**CORE PASS — SI-FAIL (core band only):** same as above but si_gate_state == FAIL.
Structurally worse than FULL PASS.

**CORE PASS — SI-UNKNOWN (core band only):** same as above but si_gate_state == UNKNOWN.
Empirically, SI-UNKNOWN behaves similar to FAIL/baseline, not like SI-FAIL (see §8.5) — must
remain a distinct category.

**EXTREME TAIL (all price bands):** rel_vol > 50× and core criteria pass. Always FAIL.

**FAIL (all price bands):** core criteria fail, OR (after core criteria pass) rel_vol_tail ==
True. SI-gate is not evaluated when core criteria fail.

### 6.7 Microcap composite logic

A microcap is MICROCAP PASS if core criteria pass, tradability floor passes, and
rel_vol_tail == False. SI-gate does not affect microcap classification. Categories:
MICROCAP PASS / EXTREME TAIL (rel_vol > 50× after core criteria) / FAIL (anything else).

### 6.8 Spec language (summary)

The Guardrail v2.1 Composite Score integrates core criteria, rel-vol tail exclusion, and the
Tradability Floor. SI-gate remains a validated quality signal for the $2–$20 universe but is
informational only for microcaps. EXTREME TAIL is evaluated only after core criteria pass and
is always FAIL. FULL PASS requires core criteria, tradability, non-tail status, and SI-gate
PASS. CORE PASS is split into SI-FAIL and SI-UNKNOWN, which behave differently and must remain
distinct. Microcaps rely solely on core criteria, tradability, and tail exclusion.

---

## 7. S3 Durability Score (Guardrail v2.1 — Corrected Weighting)

*Rewritten per composite backtest findings; not carried forward from v2.0. Proposed correction —
see §7.3 caveat.*

### 7.1 Why this section cannot carry forward

The v2.0 `_score_ease_of_entry` formula (`rolling_watchlist.py:539-556`):
```
volume_score = clip(rel_vol / 5.0, 0, 1) × 10        # saturates at 5x
squeeze_score = clip(log1p(dtc) / log1p(10), 0, 1) × 10   # saturates at dtc=10
ease_of_entry = clip(0.7 × volume_score + 0.3 × squeeze_score, 0, 10)
```
Tested as a continuous predictor of fwd_1m_ret (core band, n=3,449): **slope = -0.0118,
p=0.012** — negative and statistically significant. The dominant 70%-weighted term is actively
anti-correlated with the outcome.

### 7.2 Root cause

| component | weight | tested alone | result |
|---|---|---|---|
| `volume_score` (rel-vol, capped 5×) | 70% | not tested in isolation | the blend it dominates shows negative slope |
| `squeeze_score` (days-to-cover) | 30% | tested directly as raw `days_to_cover` | slope=+0.0203, p=0.002, Spearman=0.249, 30/30 seeds beat naive |

Rel-vol's validated empirical role (§4) is as a threshold risk flag (>50× = bad), not a
magnitude that should be continuously rewarded as it rises toward 5×.

### 7.3 Corrected formula — core band ($2–$20)

Drop the rel-vol-magnitude reward term (already handled by the core-criteria gate and tail
exclusion elsewhere in the composite — scoring it again double-counts a signal with no
standalone validated support):
```
ease_of_entry_v2.1 = squeeze_score = clip(log1p(days_to_cover) / log1p(10), 0, 1) × 10
```
i.e. weight moves from 0.7/0.3 (volume/SI) to 0/1.0.

**Caveat:** this is a *proposed* fix, not itself independently re-validated. The raw
`days_to_cover` continuous test passed the full harness; this exact rescaled formula has not
been separately re-run through LOO+5-fold×30-seed as a standalone score. A validation pass on
the literal revised formula is recommended before treating it as more than "directionally
correct and code-ready to test."

### 7.4 Corrected behavior — microcaps

Neither component has validated standing for sub-$2 (SI/days-to-cover fails at n=241; rel-vol-
as-magnitude was never independently supported even in the core band). S3 should not output a
synthesized durability score for microcaps — display raw inputs (rel-vol, gain%, days-to-cover
if available) without collapsing them into a number implying unearned confidence.

### 7.5 Implementation rules

- Core band: `ease_of_entry` = SI-only formula above.
- Microcaps: `ease_of_entry` returns `None`/not-computed, not a numeric value.
- Rel-vol continues to gate entry and trigger tail exclusion elsewhere in the composite — only
  its double-counted role inside S3 is removed.

### 7.6 Spec language (summary)

The v2.0 S3 ease-of-entry formula (70% rel-vol magnitude, 30% SI squeeze bonus) showed a
negative, statistically significant slope against forward returns (core band, n=3,449,
p=0.012). Guardrail v2.1 removes the rel-vol-magnitude reward term entirely and weights
ease-of-entry solely on the SI/days-to-cover component, which independently passed the full
harness. For microcaps, where neither component is validated, S3 does not output a synthesized
score. This revised formula is a proposal grounded in tested constituent parts and should
itself be re-validated as a standalone score before final deployment.

---

## 8. Composite Backtest Summary (Guardrail v2.1 — Empirical Findings)

### 8.1 Overview

All results come from `scan_log.csv` × SI-join (core band, n=4,223), the historical backfill
dataset (microcaps, n=241 Guardrail-conditioned), the LOO + 5-fold × 30-seed harness, and
category-level forward-return analysis.

### 8.2 SI-gate results

**Core band:** validated. slope positive p<0.05; Spearman ρ≈0.25, significant; AUC>0.55; 30/30
seeds beat naive. SI-gate is a structural quality signal, required for FULL PASS.

**Microcaps:** not validated. slope negative p=0.785; Spearman ρ=0.075, p=0.26; AUC=0.524; 0/30
seeds beat naive. SI-gate must be informational only for microcaps.

**Population-purity caveat:** the microcap backfill population has higher baseline round-trip
rates (53.5%) than scan_log (14–30%). Not yet reconciled. The microcap SI-gate null result is
corroborating, not an independent replication.

### 8.3 Rel-vol tail results

Validated across both datasets. Core band: round-trip 40.4% (tail) vs 14–15% (baseline); 1M
median -32.2% (tail) vs -9.6% (baseline). Microcaps: round-trip 71.0% (tail) vs 53.5%
(non-tail). Tail events are structurally dangerous; microcaps run hotter overall but tail
effect-size is smaller than in core band; EXTREME TAIL is bimodal (worst downside, highest
runner rate); downside risk dominates → tail exclusion is mandatory.

### 8.4 Tradability floor results

No positive relationship between baseline liquidity and forward returns; in some splits,
thin-liquidity names performed better; retained only as a practical execution safeguard, not a
predictive filter.

### 8.5 Composite category behavior — core band (n=4,223, verified)

| Category | n | 1M Median | Round-Trip% | Positive-Rate% |
|---|---|---|---|---|
| FULL PASS | 192 | -7.5% | 7.3% | 41.1% |
| CORE PASS — SI-UNKNOWN | 2,385 | -7.4% | 15.1% | 38.1% |
| CORE PASS — SI-FAIL | 320 | -22.1% | 30.9% | 26.6% |
| EXTREME TAIL | 188 | -32.2% | 40.4% | 20.5% |
| FAIL | 1,138 | -9.8% | 14.2% | 33.3% |
| Naive baseline | — | -9.6% | ~14–15% | 35.2% |

Sum check: 192+2,385+320+188+1,138 = 4,223. ✓

**Interpretation:** FULL PASS is the best-performing category on every relative dimension —
lowest round-trip rate, highest positive-rate, least-negative median, only category with a
positive *mean* (right-skewed distribution). **FULL PASS does not have a positive median
return** — do not overstate this. SI-UNKNOWN behaves like FAIL/baseline, not like SI-FAIL,
which is why it must remain a distinct category. EXTREME TAIL is the worst downside category
but has the highest runner rate, confirming its bimodal risk profile.

### 8.6 S3 durability score results

v2.0 formula: slope=-0.0118, p=0.012, directionally wrong, dominated by rel-vol magnitude
(70%); SI component (30%) is the only validated part. v2.1 correction: rel-vol magnitude reward
removed; S3 becomes SI-only (days-to-cover rescaled); microcap S3 disabled.

### 8.7 Acceptance criteria summary

| Component | Validated? | Notes |
|---|---|---|
| SI-gate (core) | ✔ | Positive slope, significant ρ, 30/30 seeds |
| SI-gate (microcaps) | ✘ | Null result, negative slope |
| Rel-vol tail | ✔ | Validated risk-control across datasets |
| Tradability floor | Structural | Not predictive |
| Composite categories | ✔ | FULL PASS best-performing tier (not literally positive-median); SI-UNKNOWN must remain distinct |
| S3 durability score | ✘ (v2.0) → proposed ✔ (v2.1, unvalidated as a standalone formula) | Negative slope diagnosed and addressed |

### 8.8 Spec language (summary)

The Guardrail v2.1 composite is supported by empirical testing across both the scan_log and
historical backfill datasets. SI-gate validates for the $2–$20 universe but fails for
microcaps. Rel-vol tail exclusion is a robust risk-control lever across all price bands. The
Tradability Floor is retained as a structural safeguard rather than a predictive filter.
Composite category behavior confirms FULL PASS as the best-performing tier (not literally
positive-median), with SI-UNKNOWN behaving like baseline and SI-FAIL materially worse. The v2.0
S3 durability score exhibited a negative slope and is replaced in v2.1 with a proposed
SI-only formulation, itself pending standalone validation.

---

## 9. v2.0 → v2.1 Diff Report

### 9.1 Overview

Three types of change: **(A)** genuine belief/behavior changes driven by new empirical testing
after v2.0 was written; **(B)** actual bugs or contradictions present in the original v2.0
text; **(C)** drafting corrections made during the v2.1 rewrite process (not v2.0 behavior, not
true version diffs). Only (A) and (B) represent real v2.0 → v2.1 specification changes.

### 9.2 SI-gate — (A): open question resolved

v2.0 (verbatim): *"SI-gate is validated for the $2–$20 universe. SI-gate is not yet validated
for the $0.50–$2 universe… SI-gate is still used for sub-$2 names. But its predictive validity
is not yet confirmed."* v2.0 was already uncertain, not confident — the microcap question was
explicitly left open. v2.1 resolves it (negatively) at n=241 with the full harness.

### 9.3 SI-gate universe eligibility — (B): genuine v2.0 bug

v2.0 (verbatim, §1): *"Exclude tickers with no SI settlement record within 45 days."* ~80% of
core-band candidates have no matchable SI record — this rule would have silently removed most
of the universe for a data-coverage reason, contradicting v2.0's own category taxonomy. v2.1
correction: tri-state SI-gate; UNKNOWN never excludes a ticker.

### 9.4 Composite categories — SI-UNKNOWN — (A): new category added

v2.0 had exactly four categories (FULL PASS, CORE PASS/SI-FAIL, EXTREME TAIL, FAIL) with no
SI-UNKNOWN state at all. v2.1 adds CORE PASS — SI-UNKNOWN as a fifth, empirically distinct
category (behaves like baseline/FAIL, not like SI-FAIL).

### 9.5 Rel-vol tail bimodality — (A): quantified, not newly discovered

v2.0 (verbatim, §4): *"This tail contains both: the worst fades, the largest winners"* — named
"Bimodal Momentum." Concept already present in v2.0; v2.1 adds quantification (round-trip
40.4% vs 14-15%; runner-rate 8.4% vs 3.8%) and corrects v2.0's factually wrong example tickers
(PLAG, QMCO, AIXI don't clear 50× anywhere in scan_log; replaced with ZYBT, YMAT, PCLA).

### 9.6 Rel-vol tail ordering — (C): drafting correction, not a v2.0 diff

v2.0's §2 bullet list was ambiguous on sequencing, but v2.0's own §5 category definitions
already required core-pass before EXTREME_REL_VOL_TAIL. The explicit "independent of
gain_pct/price band" error was introduced in an early v2.1-drafting-session-only draft of §4.1
and fixed within the same review cycle — not a v2.0 position.

### 9.7 Tradability floor — (A): empirical confirmation + internal consistency fix

v2.0 (verbatim, §9): *"Tradability Floor (Execution Only)… Do not use dollar-volume as a
quality filter."* v2.0 already held this position, untested, while simultaneously baking it
into §2's hard binary gate — an unreconciled internal tension. v2.1 empirically confirms "not
predictive" (and finds it sometimes runs the opposite direction) and resolves the tension
explicitly: floor stays as a hard gate, justified on execution-feasibility grounds only.

### 9.8 S3 durability score — (A): genuinely new finding

v2.0 already documented the 5× saturation mechanic and said dollar-volume shouldn't be added to
scoring. The negative-slope finding (-0.0118, p=0.012) was not discoverable until the composite
backtest ran, well after v2.0 was written.

### 9.9 Numerical corrections — (C): drafting log, not a v2.0 diff

The §8.5 table errors (FULL PASS median sign error, EXTREME TAIL positive-rate drift,
category-sum mismatch) occurred and were caught entirely within this session's drafting of
v2.1's own §8. v2.0 never had a composite backtest section — there is no "v2.0 behavior" to
diff against here.

### 9.10 Summary

**True v2.0 → v2.1 changes (A):** SI-gate microcap question resolved (negative); SI-UNKNOWN
added as a distinct category; tail risk quantified, example tickers corrected; tradability
floor empirically confirmed as non-predictive; S3 wrong-signed weighting discovered and
corrected (proposed).

**Actual v2.0 bug fixed (B):** SI-gate universe-exclusion rule corrected.

**Drafting corrections (C):** tail ordering clarified; numerical corrections in §8 fixed.
