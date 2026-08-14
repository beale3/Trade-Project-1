# guardrail/catalysts/edgar_mirror.py
#
# Block B -- EDGAR Mirror Wrapper (Catalyst-Neutral)
#
# *** KNOWN BUG -- DO NOT MERGE AS-IS ***
# Confirmed against the real Trade/edgar_client.py (query_filings(), lines
# 104-107): the actual filing dict has columns
#   ["accession", "cik", "company_name", "form_type", "date_filed", "filename", "source"]
# This file's get_filings() below reads "filedAt" / "formType" / "accessionNo" /
# "items" -- none of which exist in the real schema (leftover from an earlier
# sec-api.io-based draft of this module). As written, every EdgarMirrorFiling
# comes back with empty/None fields for every filing, silently, with no error.
# Fix: read "date_filed" (already typed as a Python date/datetime by DuckDB --
# do not string-parse it), "accession" (not "accession_no"), "form_type"
# (correct key already), and drop "items" (not tracked by this mirror at all).
#
# Also unverified: `from Trade.edgar_client import EdgarClient` assumes Trade
# is an importable package. The real caller (rolling_watchlist.py:43-57)
# explicitly avoids this via sys.path manipulation + `from edgar_client import
# EdgarClient` wrapped in try/except ImportError -- specifically because
# Trade is "a sibling repo, not a package." This import will likely raise
# ModuleNotFoundError as written.
#
# Also: EDGAR_MIRROR_ROOT (this file) vs EDGAR_MIRROR_PATH (established
# convention in rolling_watchlist.py) -- same concept, different env var name.
#
# Architecturally this module is correct: it wraps the existing DuckDB-backed
# EDGAR mirror already in production (Trade/edgar_client.py +
# Trade/edgar_index.duckdb) instead of building a redundant sec-api.io
# connector. Do not build a new EDGAR ingestion path -- fix this one.

import os
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from Trade.edgar_client import EdgarClient as _EdgarClient  # see import note above


@dataclass
class EdgarMirrorConfig:
    db_path: Path
    cache_dir: Path

    @staticmethod
    def from_env() -> "EdgarMirrorConfig":
        root = os.getenv("EDGAR_MIRROR_ROOT")  # see env-var-name note above
        if not root:
            raise RuntimeError("Missing EDGAR_MIRROR_ROOT environment variable")

        root_path = Path(root)
        db = root_path / "edgar_index.duckdb"
        cache = root_path / "edgar_cache"

        if not db.exists():
            raise RuntimeError(f"EDGAR mirror DB not found: {db}")

        if not cache.exists():
            raise RuntimeError(f"EDGAR mirror cache directory not found: {cache}")

        return EdgarMirrorConfig(db_path=db, cache_dir=cache)


@dataclass
class EdgarMirrorFiling:
    symbol: str
    accession_no: str
    form_type: str
    filed_at: Optional[datetime]
    items: List[str]     # NOTE: not tracked by the real mirror -- always empty
    raw: dict             # full JSON from the mirror


class EdgarMirror:
    """
    Safe wrapper around the existing DuckDB-backed EDGAR mirror.
    Catalyst-neutral. No scoring integration.
    """

    def __init__(self, config: EdgarMirrorConfig):
        self.client = _EdgarClient(
            db_path=str(config.db_path),
            cache_dir=str(config.cache_dir),
        )

    def get_filings(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[EdgarMirrorFiling]:
        """
        Fetch filings from the local EDGAR mirror.
        Uses the project's existing, validated ingestion path.

        KNOWN BUG: field names below do not match the real schema -- see
        module header. Every result currently comes back empty/None.
        """
        filings = self.client.query_filings(
            ticker=symbol,
            start_date=start_date,
            end_date=end_date,
        )

        results = []
        for f in filings:
            filed_at_raw = f.get("filedAt")  # WRONG KEY -- real key is "date_filed"
            if filed_at_raw:
                try:
                    filed_at = datetime.fromisoformat(
                        filed_at_raw.replace("Z", "+00:00")
                    )
                except Exception:
                    filed_at = None
            else:
                filed_at = None

            results.append(
                EdgarMirrorFiling(
                    symbol=symbol,
                    accession_no=f.get("accessionNo", ""),  # WRONG KEY -- real key is "accession"
                    form_type=f.get("formType", ""),        # WRONG KEY -- real key is "form_type"
                    filed_at=filed_at,
                    items=f.get("items", []),               # WRONG -- field doesn't exist in this mirror
                    raw=f,
                )
            )

        return results


def get_all_filings(
    symbol: str,
    mirror: EdgarMirror,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[EdgarMirrorFiling]:
    """Convenience helper for Guardrail v2.1. Catalyst-neutral."""
    return mirror.get_filings(symbol, start_date, end_date)


# No scoring integration: this module intentionally excludes SI-Gate
# adjustments, S3 adjustments, Composite adjustments, catalyst weights, and
# catalyst recency modifiers, because catalyst signals did not beat naive
# baselines under LOO + 5-fold x 30-seed testing (catalyst-study). EDGAR data
# may be ingested for research, dashboards, reporting, and audit trails only.
