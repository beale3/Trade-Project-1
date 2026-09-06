# Phase 1 real-data CV results (D-TRADE-042)

**Run:** `helm/validation/run_phase1_cv.py`, against `helm/storage/data/{ohlcv_daily,event_days,
intraday_sample,intraday_5m}.csv` (D-TRADE-040/041, AIQ-co-signed clean at `b0ef54e`). Zero provider-API
calls — pure local computation over CSVs already on disk (independently confirmed: no `requests`/Massive
imports anywhere in the code path, in addition to the Lead's own grep). Full machine-readable output:
`helm/storage/phase1_cv_results.json`.

**Bar, unchanged:** D-TRADE-021 (CLEARED only if it beats naive OOS under BOTH LOO-CV and 5-fold CV
(≥30 seeds), ≥90% seed agreement) · D-TRADE-029 (n<30 → UNMEASURED) · the ratified 4-state schema
(ADR-0001 §6.1). **No tuning, re-gridding, or re-selection was performed to change any result below** —
every verdict is the mechanical bar applied once, as built and Stage-2-audited.

## Leg A — entry-signal validation (27 tests: 9 components × 3 horizons)

**26 of 27 DROPPED. 1 of 27 CLEARED** (`opening_range_breakout` @ 1w).

| Component | Fired / Total | 1d | 1w | 1m |
|---|---|---|---|---|
| bull_flag_breakout | 40/148 | DROPPED | DROPPED | DROPPED |
| flat_top_breakout | 131/148 | DROPPED | DROPPED | DROPPED |
| abcd_pattern | 129/148 | DROPPED | DROPPED | DROPPED |
| micro_pullback | 126/148 | DROPPED | DROPPED | DROPPED |
| round_number_breakout | 109/148 | DROPPED | DROPPED | DROPPED |
| opening_range_breakout | 137/148 | DROPPED | **CLEARED** | DROPPED |
| premarket_pivot_break | 108/148 | DROPPED | DROPPED | DROPPED |
| premarket_high_break | 97/148 | DROPPED | DROPPED | DROPPED |
| aligned_trigger | 148/148 | DROPPED | DROPPED | DROPPED |

n=148 usable events out of 150 sampled (2 excluded: insufficient forward daily history to compute all
three horizons — excluded, not imputed, per NN-5's principle applied to Leg A's own construction).

### The one CLEARED result, in full
`opening_range_breakout @ 1w`: LOO RMSE 40.98 vs. naive 41.17 (0.46% improvement, beats naive) · 5-fold
seed agreement 93.3% (≥90% required) · n_support=137/148. **Mechanically CLEARED under the bar as built.**
Two honest caveats, not a retraction: (1) the effect size is small — 0.46% RMSE improvement is the same
order of magnitude as the short-interest study's own "modest tilt, not a strong signal" result, and should
be read the same way. (2) only 11 of 148 events did NOT fire this component — the comparison group backing
the "not fired" side of the regression is thin, even though n_support clears the 30-event floor by a wide
margin (the floor counts firings, not balance — see the methodology gap below).

### 🔴 A finding about the BAR, not the data — flagging for AIQ/Architect, not self-fixed
`aligned_trigger` fired on **148/148 events — literally every single sampled event, zero variance.**
Confirmed this is real, not a bug: the cohort (`event_days.csv`) is pre-selected on a big single-day
gain + volume spike (`gain_pct`/`relative_volume` columns) — a stock having a large gap/spike day trades
above its prior close and above its own pivot for essentially the whole session almost by construction.
The regression's own numbers prove it's degenerate, not merely weak: `rmse_model_loo == rmse_naive_loo`
**exactly** (30.10609 = 30.10609, 0.0% improvement, 0% seed agreement) — a constant feature has a flat
fitted line identical to the naive mean predictor, so "beats naive" is mathematically impossible regardless
of any real relationship. **This DROPPED verdict is not a meaningful head-to-head test result — it's an
untestable case the D-TRADE-021 bar's current design doesn't detect, because the 30-event floor (D-TRADE-
029) counts firing events, not comparison-group balance.** Several other components share a milder version
of this (flat_top_breakout 131/17, abcd_pattern 129/19, micro_pullback 126/22, opening_range_breakout
137/11) — `bull_flag_breakout` (40/108) is the best-balanced test among the 9 and its DROPPED verdict is
the most statistically trustworthy of the batch. **Recommend a future bar revision add a minimum-balance
check (e.g., both classes ≥30, not just the fired class) — flagging the gap, not patching around it myself
mid-run** (the Director's own instruction: report the failure/limitation, don't tune past it).

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
| Leg A (27 tests) | 1 | 26 | 0 | 0 |
| Leg B (7 configs) | 0 | 7 | 0 | 0 |

No VOID (no leakage/contamination detected) and no UNMEASURED (n=148-150 across the board comfortably
clears D-TRADE-029's 30-event floor for every test — the floor was not the binding constraint here; the
newly-surfaced balance gap above is a different, unaddressed constraint). **Per the Director's explicit
framing, this near-total-DROPPED outcome is treated as a valid, useful result, not a failed run** — it says
the existing scanner's untested components and the new trailing-stop rule mostly do not show a real edge in
this 148-150-event sample, with one modest, honestly-caveated exception and one methodology gap (the
balance check) surfaced for the bar's own future improvement.

**Not yet done (this run's explicit boundary):** `reproduced_by_aiq=TRUE` — AIQ's independent re-derivation
from raw primitives, dispatched next per D-TRADE-042, required before any CLEARED verdict counts as final.
