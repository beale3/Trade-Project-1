# Guardrail v2.1 — Session Work Product

Committed from a Claude Code session that reviewed and empirically re-validated the Guardrail
scan spec (originally v2.0) against `scan_log.csv`, a FINRA short-interest dataset
(`short-interest-study/raw_short_interest_all.csv`), and a historical price backfill pulled via
the market-data MCP API. Every numeric claim in `spec/` was checked against one of the artifacts
in `analysis/` or `data/` before being accepted.

## Status

- **§3 (SI-Gate), §4 (Rel-Vol Tail), §5 (Tradability Floor), §6 (Composite Scoring),
  §7 (S3 Durability Score), §8 (Composite Backtest Summary), §9 (v2.0→v2.1 Diff Report)**:
  each individually reviewed and confirmed accurate against the underlying data. Compiled into
  `spec/guardrail-v2.1-spec.md`.
- **§0-§2, §10-§11**: carried forward from the original v2.0 document. §1's SI-match universe-
  exclusion rule was identified as a genuine bug and is corrected in §3 (tri-state SI-gate,
  UNKNOWN never excludes a ticker) — the original v2.0 text of §1 should not be used as-is.
  §2's "Gain% (Open→High)" definition was flagged as inconsistent with what was actually tested
  (`gain_pct` = close vs. prior close, confirmed against `scan_log.csv`) and has not yet been
  corrected in the source document — **do not implement §2 literally without fixing this**.
- **Full v2.1 document assembly**: not completed. What exists is the individually-confirmed
  §3-§9 plus these implementation notes — no single canonical file merges this with the
  unmodified v2.0 sections.

## Known open items

1. **Population-purity reconciliation** (flagged in §3.3/§8.2): the n=241 historical-backfill
   sub-$2 dataset shows materially higher baseline round-trip rates (53.5%) than the scan_log-
   derived population (14-30%), not yet reconciled. Treat the SI-gate microcap null result as
   corroborating evidence, not a fully independent replication, until this is understood.
2. **Block A (Massive API ingestion)**: finalized, catalyst-neutral, environment-variable
   configured, fails loudly on missing key. The `/filings` endpoint path itself is still an
   unverified placeholder — confirm against real Massive API docs before use.
3. **Block B (EDGAR mirror wrapper)**: architecturally correct (wraps the existing
   `Trade/edgar_client.py` DuckDB-backed mirror rather than building a redundant sec-api.io
   connector) but **has a confirmed field-mapping bug**, not yet fixed as of this commit — see
   `code/edgar_mirror.py`'s header comment for the exact correction needed. As pasted, every
   `EdgarMirrorFiling` will come back with empty/None fields because it reads `filedAt`/
   `formType`/`accessionNo` (leftover from an earlier sec-api.io-based draft) instead of the
   real mirror's actual columns: `date_filed`, `form_type`, `accession` (confirmed directly
   against `Trade/edgar_client.py:104-107`). Also uses `from Trade.edgar_client import ...`,
   which will likely raise `ModuleNotFoundError` since `Trade` is a sibling repo added to
   `sys.path`, not an importable package (see `rolling_watchlist.py:43-57` for the established
   pattern). Do not merge Block B until these are fixed.
4. **S3 corrected formula** (§7.3): proposed but not independently re-validated through the
   LOO+5-fold×30-seed harness as its own standalone score — only its constituent parts
   (raw `days_to_cover`) were validated directly.

## Contents

- `spec/guardrail-v2.1-spec.md` — §3-§9, confirmed final text.
- `analysis/` — the three Python scripts used to produce every number cited in the spec.
- `data/guardrail_conditioned_sub2.csv` — the n=241 Guardrail-conditioned sub-$2 historical
  observation table (real data, pulled via market-data API + FINRA short-interest join).
- `code/` — Block A (Massive ingestion, final) and Block B (EDGAR mirror wrapper, has a known
  bug — see above and the file's own header comment).
