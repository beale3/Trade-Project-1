# Phase 1 real-data CV results (D-TRADE-042)

> **REVISED 2026-09-06 — D-TRADE-044 armed in code.** The symmetric class-balance floor (both
> `n_fired ≥ 30` AND `n_not_fired ≥ 30`, else UNMEASURED) is now enforced by
> `helm/validation/engine/bar.py`, not just documented. **The official headline is
> `0 CLEARED / 12 DROPPED / 15 UNMEASURED`** — `opening_range_breakout`@1w's clearance is removed.
> Sections below are re-authored to the corrected verdicts (LL-19: not patched alongside superseded
> text). The original 1-CLEARED reading was produced by the pre-D-TRADE-044 bar and is superseded, not
> "wrong at the time" — the floor that removed it is a rule that did not yet exist when the run executed.
> **UNMEASURED is not a negative verdict** (D-TRADE-044): those 15 tests could not be run for want of
> observations on one side; the remedy is a larger event cohort, not abandoning the components.

**Run:** `helm/validation/run_phase1_cv.py`, against `helm/storage/data/{ohlcv_daily,event_days,
intraday_sample,intraday_5m}.csv` (D-TRADE-040/041, AIQ-co-signed clean at `b0ef54e`). Zero provider-API
calls — pure local computation over CSVs already on disk (independently confirmed: no `requests`/Massive
imports anywhere in the code path, in addition to the Lead's own grep). Full machine-readable output:
`helm/storage/phase1_cv_results.json`.

**Bar:** D-TRADE-021 (CLEARED only if it beats naive OOS under BOTH LOO-CV and 5-fold CV (≥30 seeds),
≥90% seed agreement) · D-TRADE-029 (n_fired <30 → UNMEASURED) · **D-TRADE-044 (n_not_fired <30 →
UNMEASURED too — the symmetric floor, added after this run and applied retroactively)** · the ratified
4-state schema (ADR-0001 §6.1). **No tuning, re-gridding, or re-selection was performed to change any
result below** — every verdict is the mechanical bar applied once. The one bar change since the original
run (D-TRADE-044) was proposed by AIQ and ratified by the Director specifically *because* it moves
against the result, and is now armed in code with a planted negative control.

## Leg A — entry-signal validation (27 tests: 9 components × 3 horizons)

**0 CLEARED · 12 DROPPED · 15 UNMEASURED** (post-D-TRADE-044).

| Component | Fired / Not-fired | Both ≥30? | 1d | 1w | 1m |
|---|---|---|---|---|---|
| bull_flag_breakout | 40 / 108 | ✅ | DROPPED | DROPPED | DROPPED |
| flat_top_breakout | 131 / 17 | ❌ | UNMEASURED | UNMEASURED | UNMEASURED |
| abcd_pattern | 129 / 19 | ❌ | UNMEASURED | UNMEASURED | UNMEASURED |
| micro_pullback | 126 / 22 | ❌ | UNMEASURED | UNMEASURED | UNMEASURED |
| round_number_breakout | 109 / 39 | ✅ | DROPPED | DROPPED | DROPPED |
| opening_range_breakout | 137 / 11 | ❌ | UNMEASURED | UNMEASURED | UNMEASURED |
| premarket_pivot_break | 108 / 40 | ✅ | DROPPED | DROPPED | DROPPED |
| premarket_high_break | 97 / 51 | ✅ | DROPPED | DROPPED | DROPPED |
| aligned_trigger | 148 / 0 | ❌ | UNMEASURED | UNMEASURED | UNMEASURED |

n=148 usable events out of 150 sampled (2 excluded: insufficient forward daily history to compute all
three horizons — excluded, not imputed, per NN-5's principle applied to Leg A's own construction).

**The 12 DROPPED verdicts are the trustworthy ones**: 4 components (bull_flag_breakout,
round_number_breakout, premarket_pivot_break, premarket_high_break) carry ≥30 observations on both sides,
so their comparisons were real measurements that returned a negative result. `bull_flag_breakout`
(40/108) is the best-balanced test in the batch.

**The 15 UNMEASURED verdicts are not failures** — 5 components fire on so many of these pre-selected
spike days that the non-firing comparison group is too thin (or, for `aligned_trigger`, empty) to
measure against. The remedy is a larger/less-conditioned event cohort, not dropping the components.

### Why the balance floor exists — the finding that produced D-TRADE-044
`aligned_trigger` fired on **148/148 events — every single sampled event, zero variance.** Real, not a
bug: the cohort (`event_days.csv`) is pre-selected on a big single-day gain + volume spike, and a stock
having a large gap/spike day trades above its prior close and above its own pivot essentially all
session by construction. The regression's own numbers proved it degenerate rather than merely weak:
`rmse_model_loo == rmse_naive_loo` **exactly** (30.10609 = 30.10609, 0.0% improvement, 0% seed
agreement) — a constant feature's fitted line is flat and identical to the naive mean predictor, so
"beats naive" is mathematically impossible whether or not a real relationship exists. Surfaced from this
run, proposed by AIQ, ratified by the Director as D-TRADE-044, and now **armed in
`helm/validation/engine/bar.py`** — a comparison returns UNMEASURED unless both sides carry ≥30.

`opening_range_breakout`@1w, this run's only pre-D-TRADE-044 clearance (LOO RMSE 40.98 vs naive 41.17,
0.46% improvement, 93.3% seed agreement), sat second-most-imbalanced in the batch at 137/11 — 11
non-firing observations backing the comparison. Its removal is the intended, accepted consequence of a
rule that is principled, uniform, and moves against the result.

## Leg B — exit-rule validation (7 configs: primary + 5 grid sensitivity + 2 N sensitivity)

**All 7 DROPPED**, including the primary clearance-eligible cell.

**Primary (trail_pct=8%, init_stop_pct=3% vs. fixed N=5 trading days, D-TRADE-036):** n=149 paired trades ·
full-sample mean difference **−22.44 percentage points** (trailing arm underperforms the fixed-hold arm) ·
LOO: **100% of leave-one-out estimates agree** with the full-sample direction (a robust, non-outlier-driven
result — the Stage-2 audit fix's unanimity check is doing real work here) · 5-fold×30-seed: only **2.0%**
of seed-fold evaluations favor trailing. This is a decisive, robust DROPPED, not a marginal miss.

| Config | n | Verdict |
|---|---|---|
| trail=8/init=3 vs N=5 (**primary**) | 149 | DROPPED |
| trail=5/init=2 vs N=5 (sensitivity) | 149 | DROPPED |
| trail=5/init=3 vs N=5 (sensitivity) | 149 | DROPPED |
| trail=8/init=2 vs N=5 (sensitivity) | 149 | DROPPED |
| trail=12/init=2 vs N=5 (sensitivity) | 149 | DROPPED |
| trail=12/init=3 vs N=5 (sensitivity) | 149 | DROPPED |
| trail=8/init=3 vs N=1 (sensitivity) | 150 | DROPPED |
| trail=8/init=3 vs N=21 (sensitivity) | 148 | DROPPED |

Entry rule: the pivot/red-to-green alignment trigger (`aligned_trigger`), first trade only per event. 1 of
150 events excluded from the primary run (insufficient forward daily history for the N=5 baseline).

### A construction note on the −22.4pt gap, stated plainly (see `run_phase1_cv.py`'s own docstring)
`simulate_day_trades()` force-closes at end-of-day — it has no multi-day capability, and was not extended
to gain one for this run (reusing the Stage-1 build as-is, not writing new simulator code mid-dispatch).
D-TRADE-036's N=5-**trading-day** baseline is a materially longer horizon than a same-day simulator can
represent. Resolved by computing the fixed-N arm as: same intraday entry price the trailing arm used, exit
at the daily close 5 trading days later. This is the only construction consistent with reusing the existing
simulator and giving both arms the same entry price (a valid pairing) — but it means the comparison is
**same-day exposure vs. a 5-day hold**, not two arms on an identical timeframe. Part of the −22.4pt gap is
very likely this duration mismatch (a 5-day hold captures far more of a post-spike move, up or down, than
a same-day exit structurally can) rather than pure evidence that trailing-stops underperform on a like-for-
like horizon. Flagged for AIQ's independent judgment on the construction itself, same as the paired-
comparison method was flagged at build time — not something to re-run differently to get a "fairer" number
without Director/AIQ sign-off on the construction change first.

## Summary

| | CLEARED | DROPPED | VOID | UNMEASURED |
|---|---|---|---|---|
| Leg A (27 tests) | 0 | 12 | 0 | 15 |
| Leg B (8 configs) | 0 | 8 | 0 | 0 |

Tallies are computed by `run_phase1_cv.py` itself and printed as a headline, so they never need manual
recomputation downstream. No VOID anywhere — no leakage/contamination was detected in any test.

**Per the Director's explicit framing, this all-DROPPED/UNMEASURED outcome is a valid, useful result, not
a failed run.** Read precisely: of the scanner's 9 previously-untested components, 4 were genuinely
measurable on this cohort and none of them showed an edge; 5 could not be measured at all here because
the cohort's own spike-selection makes them fire nearly always. The trailing-stop exit rule was
measurable and decisively underperformed a fixed hold — with the duration-mismatch caveat above. The
most actionable finding for Phase 2 scoping is arguably not any single verdict but the cohort-design
constraint the UNMEASURED block exposes: **a cohort pre-selected on "big spike day" cannot test
components that are themselves near-synonymous with "big spike day."**

**Not yet done (this run's explicit boundary):** `reproduced_by_aiq=TRUE` — AIQ's independent re-derivation
from raw primitives, dispatched next per D-TRADE-042, required before any CLEARED verdict counts as final.
