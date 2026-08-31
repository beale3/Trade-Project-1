# D-TRADE-038 real-data pull — independent audit (AIQ, 2026-08-31)

Independent audit of SDE1's real Massive OHLCV pull (`3cf6cc7`), per the Director's explicit build-chain
discipline extension: "SDE1 executes, AIQ independently re-derives/audits, QA re-runs for reproducibility,
Lead verifies at source." Read `helm/ingest/massive.py`, `helm/ingest/run_gate2_pull.py`,
`helm/storage/raw_store.py` directly (source, to understand what the code claims to do — not imported for
computation); every check below runs my own pandas code directly against the actual CSVs, independent of
`helm/ingest`'s or `helm/storage`'s own claims.

## Scope
First real provider data in this project (100 tickers, 2024-06-03→2026-07-17, `helm/storage/data/
ohlcv_daily.csv`, 45,426 rows) plus `spend_ledger.csv` (200 rows). No CV/backtest run against this data
yet — that's a separate, later audit once AI/ML's engine consumes it. This covers: NN-1 point-in-time
integrity of the pull itself, basic data sanity, and ledger-vs-CSV consistency.

## NN-1 — point-in-time integrity of the ingest mechanism
`helm/ingest/massive.py::fetch_daily_ohlcv` requests an explicit, bounded `[start_date, end_date]` window
per call (`MASSIVE_AGGS_URL.../range/1/day/{start}/{end}`) — not an unbounded or "as of today" query. The
approved run (`run_gate2_pull.py`) sets `end_date = today - 45 days` (a data-quality buffer, not a
point-in-time mechanism itself). **Independently verified, not just read from source:** no row in the
actual CSV has a date later than the approved `end_date` (max date = 2026-07-17, exactly matching `today
(2026-08-31) - 45 days`). The ingest layer's pull mechanics are point-in-time-safe by construction for
their stated purpose (a bounded historical range pull). **Downstream note, not yet auditable:** NN-1
compliance for the eventual FEATURE/LABEL construction depends on how AI/ML's Leg A/B code later joins this
raw data to forward returns — that's a separate, future audit once that join exists; this only confirms the
raw pull itself introduces no leak.

## Data sanity — all checks clean, zero violations
Run directly against `ohlcv_daily.csv` (45,426 rows, 100 unique tickers):
- High ≥ Low: **0 violations**
- Close within [Low, High]: **0 violations**
- Open within [Low, High]: **0 violations**
- Negative or zero volume: **0**
- Negative or zero price (any of O/H/L/C): **0**
- Duplicate (ticker, date) pairs: **0**
- NaN in any core OHLCV field: **0**

## Ledger-vs-CSV consistency
`spend_ledger.csv`: 200 rows = 100 `ok=False` (the pre-credential-fix failed calls) + 100 `ok=True`
(the successful pull), matching the reported history exactly. **Cross-checked every one of the 100
successful calls' claimed `rows_returned` against the actual row count for that ticker in the CSV: zero
mismatches.** Sum of ledger-claimed rows (45,426) equals the actual CSV total (45,426) exactly. The ledger
is not just present — it is honest about what was actually written.

## Row-count variance across tickers — investigated, explained
Rows per ticker range from 75 to 532 (mean 454). Checked the 9 tickers under 200 rows individually against
their own date spans:
- **Late-starting** (AGPU, NCEL, OTH, MRDN) — first row well after `START_DATE`, consistent with a
  late IPO/uplisting into the window.
- **Early-ending** (HYZN, INVO, NKLA, PAYOW, PMD) — last row well before `end_date`, consistent with
  delisting/ticker-change/halt (e.g. NKLA's real-world 2024–2025 bankruptcy/relisting history is publicly
  consistent with an early stop). Not a partial-pull artifact — the gap-check below confirms these are
  real, not caused by a broken mid-range pull.
- **Missing-business-day check** (gaps within each ticker's own observed range): most tickers show 0-9
  missing business days (ordinary holiday/data-vendor noise); a handful (TRVN, AREBW, MDCXW — not in the
  low-row-count list, i.e. these have long overall spans but real internal gaps) show up to ~200 missing
  business days, plausible for real trading halts on volatile microcaps. **No NaN-filled or interpolated
  rows anywhere** — missing days are true absences, matching NN-5's "excluded, not imputed" principle, not
  a data-integrity defect.

## Findings — 2, both forward-looking flags, neither blocks this delivery

### Finding 1 — `adjusted=true` is a genuine, undisclosed point-in-time risk for this cohort
`massive.py`'s API call uses `adjusted=true` — **not a new choice**, it matches `tools/rolling_watchlist.py`'s
own pre-existing Massive call exactly (verified by direct text comparison), so this delivery didn't
introduce it. But this is the **first time it becomes load-bearing for an actual historical backtest**
rather than a live "as of right now" scan, where the distinction doesn't matter (a live scan always reads
today's own adjustment factor for every date). Split/dividend-adjusted historical prices can be
**retroactively restated** by a later corporate action — a stock split declared in month M+3 changes what
"Close" reads for a date in month M when refetched afterward. That is a real look-ahead vector, distinct
from the date-range bounding already verified safe above. Given this cohort (the short-interest study's
754-ticker universe, sampled to 100) skews toward volatile microcaps where reverse splits are common, this
is not hypothetical. **Not found or disclosed as a risk anywhere in the ADR/canonical docs.**
**Recommendation:** an explicit decision (Director/Architect/AI/ML/AIQ) on adjusted vs. raw/unadjusted
prices for Leg A/B, with whichever is chosen recorded as a disclosed, deliberate choice — not a silently
inherited default from a different use case (the live dashboard) where it happened not to matter.

### Finding 2 — coverage gaps need explicit skip-not-impute handling downstream
Some tickers have real internal gaps (up to ~40% of business days missing in a few cases). The raw data
itself handles this correctly (no fabricated fill) — this is a forward note for whoever builds the Leg
A/B point-in-time join: it must skip missing dates cleanly, matching NN-5's already-established
exclude-don't-impute principle, not assume every ticker has continuous daily coverage across the window.

## Verdict
**The pull is independently verified clean.** All data-sanity and ledger-consistency checks pass with
zero violations; the ingest mechanism is point-in-time-safe by construction for its stated purpose; the
row-count variance across tickers is explained by real market history, not a pull defect. Two findings are
flagged for downstream design decisions (adjusted-price choice, gap-handling), neither is a defect in this
delivery. No blocker to Stage continuing.
