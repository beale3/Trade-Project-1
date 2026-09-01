# D-TRADE-040/041 audit — SDE1's raw re-pull, split-artifact filter, intraday sample (AIQ, 2026-08-31)

Independent audit per the Director's build-chain discipline extension to data delivery (SDE1 executes →
AIQ audits → QA reproduces → Lead verifies at source). Read `helm/ingest/identify_events.py` in full
(source, to understand the mechanism — not imported for computation); every check below is my own code run
directly against the actual CSVs and against `tools.rolling_watchlist.compute_relative_volume` (a raw
primitive, legitimate to call directly), never against `identify_events.py`'s own output as ground truth.

## Headline verdict
**The split-exclusion mechanism itself is mechanically sound (NN-1-safe) and the underlying phenomenon
SDE1 found is real — but its coverage is severely incomplete: 3 of at least 30 tickers with genuine
in-window split transitions are listed. 27 are missing. 17 of the current 559 "clean" event-days are
still split-artifact contamination, independently confirmed, including 3 that already consumed real paid
intraday-pull calls.** This needs a fix-and-regenerate pass before Leg A/B consumes this cohort, not a
sign-off as-is.

## 1 — NN-1: is `split_contaminated_mask` look-ahead-safe?
Read `identify_events.py::split_contaminated_mask` directly. For a given ticker, it takes a **hardcoded**
transition date (from `SPLIT_TRANSITION_DATES`, a static module constant — not computed per-row from the
data), finds that date's position in the ticker's own sorted trading-day index (`start_pos`), and marks
positions `[start_pos, start_pos+20]` as contaminated. This is pure position arithmetic against a fixed,
already-known date — it does not read any data beyond a given row to decide whether that row is excluded.
**Confirmed NN-1-safe as implemented.**
**Separately, correctly self-disclosed by SDE1's own docstring:** the *discovery* method (diffing complete
raw vs. complete adjusted historical files) is fully retrospective and won't generalize to detecting a
*future* split in a live/ongoing pull with no adjusted reference to diff against. This is fine for curating
a fixed historical backtest cohort (the same "use hindsight to define what's excluded" pattern NN-5 already
sanctions) but must never be mistaken for a live/point-in-time split detector. Confirmed accurate, not a
new finding.

## 2 — MAJOR FINDING: `SPLIT_TRANSITION_DATES` covers 3 of ≥30 tickers with real in-window transitions
Independently reproduced the raw-vs-adjusted divergence across **all 100 tickers** (not just SDE1's 4
spot-checked). Method: merge `ohlcv_daily.csv` (raw) against
`ohlcv_daily_adjusted_D-TRADE-038_SUPERSEDED.csv` (adjusted) on (ticker, date); compute the raw/adjusted
close-price ratio per row; flag any ticker where that ratio steps by >15% between consecutive trading
days (a genuine split signature — verified on several examples to be a **clean, permanent** step, not
reverting: pre- and post-jump ratio standard deviation both ≈0.0, e.g. NKLA 0.0333→1.0 on 2024-06-25,
TRVN 0.04→1.0 on 2024-08-13, XHG 0.05→1.0 on 2025-05-09 — textbook reverse-split ratios, not noise).

**Result: 30 tickers have a genuine in-window transition. Only 3 (ANY, AREBW, ASST) are in
`SPLIT_TRANSITION_DATES`. 27 are missing:**
`BKYI (2026-04-30), BTM (2026-02-23), ENSC (2024-12-06), GWH (2024-08-26), HTOO (2025-07-14), HYZN
(2024-09-11), ILLR (2026-06-23), KZIA (2024-10-28, 2025-04-17), LESL (2025-09-29), LUCY (2024-07-18), LYEL
(2025-06-02), MSS (2026-04-24), NKLA (2024-06-25), NUKK (2024-10-24), PHGE (2024-08-26, 2025-11-25), POLA
(2024-11-19), PSIG (2025-10-13), SGN (2024-11-18), SNSE (2025-06-17), SRFM (2024-08-19), TCRT (2024-07-18),
TRVN (2024-08-13), UPXI (2024-10-03), VATE (2024-08-09), WORX (2026-04-10), XHG (2024-11-08, 2025-05-09),
ZEPP (2024-09-16)`.
(Note: several other tickers show large raw-vs-adjusted divergence — e.g. RCON at a constant 0.005 ratio
throughout — but their ratio never *changes within the pulled window*, meaning the split predates the
pull's start; those introduce no in-window `pct_change()`/rel-vol artifact and correctly need no exclusion
entry. Only the 27 above have an actual in-window step.)

## 3 — Quantified impact: 17 of the current 559 "clean" events are still contaminated
For each of the 27 missing tickers, checked whether any `event_days.csv` row falls within [transition,
transition+20 trading days] of its own missed split (same 20-trading-day, own-index window SDE1 already
uses for the 3 covered tickers — applied here to the ones that should have been covered too). **17 hits**,
several with the exact tell-tale split-artifact signature (extreme, physically-implausible-for-a-single-day
gain/rel-vol) SDE1's own docstring uses to define the problem:

| date | ticker | gain_pct | relative_volume |
|---|---|---|---|
| 2026-06-25 | ILLR | 296.57 | 78.06 |
| 2024-10-25 | UPXI | 170.00 | 57.48 |
| 2024-09-10 | TRVN | 53.73 | 14.98 |
| 2024-10-17 | UPXI | 29.64 | 14.62 |
| 2025-07-22 | HTOO | 56.78 | 13.69 |
| 2025-10-13 | PSIG | 937.12 | 12.55 |
| 2024-10-24 | NUKK | 825.38 | 6.42 |
| 2025-05-13 | XHG | 12.50 | 6.20 |
| 2026-06-26 | ILLR | 46.23 | 6.03 |
| 2024-12-09 | XHG | 11.11 | 5.54 |
| 2025-07-25 | HTOO | 47.78 | 5.52 |
| 2024-10-29 | UPXI | 27.04 | 4.82 |
| 2024-09-27 | ZEPP | 14.61 | 4.20 |
| 2024-10-18 | UPXI | 10.06 | 3.33 |
| 2025-04-17 | KZIA | 366.17 | 3.15 |
| 2024-07-18 | TCRT | 590.43 | 2.93 |
| 2025-06-04 | LYEL | 68.59 | 2.75 |

PSIG's 937% one-day "gain," NUKK's 825%, TCRT's 590%, KZIA's 366% are the same order of magnitude as the
ASST 455.74%/1312x example SDE1 already correctly identified as the archetypal split artifact — these read
as the same phenomenon, uncaught.

**Compounding cost:** 3 of these 17 (HTOO 2025-07-22, UPXI 2024-10-17, XHG 2024-12-09) are already inside
the 150-event **paid** intraday pull (`intraday_sample.csv`/`intraday_5m.csv`) — real provider calls
already spent on contaminated events.

## 4 — The ASST 2025-05-07 check: correctly NOT excluded, but SDE1's own diagnosis of it is wrong
Per the Lead's specific ask. Confirmed: `event_days.csv` still contains ASST 2025-05-07 (gain=455.74%,
rel_vol=1312.0) — **correctly not excluded**, since it falls at trading-day position 232, nowhere near
either of ASST's two real transition windows (`[20,40]` for 2024-07-02, `[421,441]` for 2026-02-06).
**But SDE1's own module docstring calls this event "not a real trading day, a split artifact" — that
characterization is wrong.** Mapped ASST's full raw/adjusted ratio history: it has exactly 2 segments
(0.05 from 2024-07-02 to 2026-02-05, 1.00 after) — **no ratio change anywhere near 2025-05-07 at all.**
Pulled the raw OHLCV directly: close jumps 0.61→3.39 (2025-05-06→05-07), volume jumps ~197K→**315,839,429**
shares, then stays elevated (241.9M, 54.4M, 18.4M shares) over the following days while price gradually
decays (7.69→8.12→7.01→5.97→4.70) — a sustained multi-day pattern, not a single corrupted tick or a
split-basis discontinuity. This is the signature of a **real, large market event** (consistent with a
short-squeeze/news-driven spike on a thin-float microcap), not a data artifact. **Correct outcome
(un-excluded), wrong stated reason — worth fixing the docstring so a future reader doesn't inherit the
mischaracterization**, but this specific event needs no code change.

## 5 — Data sanity, both new files: zero violations
`ohlcv_daily.csv` (raw, 45,426 rows/100 tickers) and `intraday_5m.csv` (15,703 rows/78 tickers/121 event
dates): High≥Low, Close/Open within [Low,High], no negative/zero volume or price, no duplicate keys, no
NaN in any core field — all zero violations on both files, checked directly.

## 6 — Intraday point-in-time bound
Every one of the 15,703 intraday bars' own timestamp date exactly matches its `event_date` column (0
mismatches) — no bar's data crosses into an adjacent day. Bar times span 04:00–19:55 (pre-market through
after-hours), consistent with the scanner's premarket-pattern components; not itself a leakage concern
since NN-1 is about a row not reading data from *after its own timestamp*, which this doesn't do.

## 7 — Count cross-checks
150 unique (ticker, event_date) pairs in `intraday_5m.csv` exactly match `intraday_sample.csv`'s 150 rows.
No discrepancy.

## Recommendation
Extend `SPLIT_TRANSITION_DATES` with the 27 tickers/dates above, re-run `identify_events.py` (559 will
drop further — my 17-row table is a lower bound on what a full re-run removes, since some of the 27 may
also have additional in-window events beyond what I checked), and re-derive the intraday sample from the
corrected event list (at minimum, the 3 already-paid-for contaminated pulls should be replaced). Fix the
docstring's ASST 2025-05-07 characterization to avoid a future reader inheriting the wrong reason. None of
this is a redesign — the mechanism is right, the coverage just needs finishing.
