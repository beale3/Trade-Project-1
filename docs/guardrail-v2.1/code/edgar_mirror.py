# guardrail/catalysts/edgar_mirror.py
#
# Block B -- EDGAR Mirror Wrapper (Catalyst-Neutral)
#
# Fixed 2026-08-14 per Director instruction, against the real
# Trade/edgar_client.py schema (query_filings(), lines 104-107; re-verified
# directly, not just from the prior draft's citation):
#   ["accession", "cik", "company_name", "form_type", "date_filed", "filename", "source"]
# date_filed comes back as a native Python date/datetime (DuckDB DATE column
# via the Python driver) -- it is type-checked, not string-parsed. "items"
# (8-K item codes) isn't tracked by this mirror at all and is always [].
#
# Import mirrors the established sibling-repo pattern (rolling_watchlist.py:
# 43-57): Trade is "a sibling repo, not a package," so it's added to
# sys.path at runtime rather than imported as `Trade.edgar_client`, with a
# try/except ImportError degrading to None the same way. Note this file sits
# one directory deeper than rolling_watchlist.py (docs/guardrail-v2.1/code/
# vs tools/), so the default sibling-repo lookup uses parents[5], not [3].
#
# Env var: EDGAR_MIRROR_PATH (matches rolling_watchlist.py's established
# convention -- EDGAR_MIRROR_ROOT was a naming mismatch in the prior draft).
#
# Verified 2026-08-14 (Lead): ran get_filings("AAPL") against the real
# Trade/edgar_index.duckdb mirror -- 100 real filings returned, accession_no/
# form_type populated (not empty), filed_at a real datetime.date, items == [].
#
# Architecturally this module wraps the existing DuckDB-backed EDGAR mirror
# already in production (Trade/edgar_client.py + Trade/edgar_index.duckdb)
# instead of building a redundant sec-api.io connector -- do not build a new
# EDGAR ingestion path.

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from datetime import date, datetime
from typing import Optional, List

_EDGAR_MIRROR_ROOT = Path(os.environ["EDGAR_MIRROR_PATH"]) if os.environ.get("EDGAR_MIRROR_PATH") \
    else Path(__file__).resolve().parents[5] / "Trade"
if str(_EDGAR_MIRROR_ROOT) not in sys.path:
    sys.path.insert(0, str(_EDGAR_MIRROR_ROOT))
try:
    from edgar_client import EdgarClient as _EdgarClient
except ImportError:
    _EdgarClient = None


@dataclass
class EdgarMirrorConfig:
    db_path: Path
    cache_dir: Path

    @staticmethod
    def from_env() -> "EdgarMirrorConfig":
        root = os.getenv("EDGAR_MIRROR_PATH")
        if not root:
            raise RuntimeError("Missing EDGAR_MIRROR_PATH environment variable")

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
    items: List[str]     # not tracked by the real mirror -- always empty
    raw: dict             # full record from the mirror


class EdgarMirror:
    """
    Safe wrapper around the existing DuckDB-backed EDGAR mirror.
    Catalyst-neutral. No scoring integration.
    """

    def __init__(self, config: EdgarMirrorConfig):
        if _EdgarClient is None:
            raise RuntimeError("edgar_client is not importable -- check EDGAR_MIRROR_PATH")
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
        """
        filings = self.client.query_filings(
            ticker=symbol,
            start_date=start_date,
            end_date=end_date,
        )

        results = []
        for f in filings:
            date_filed_raw = f.get("date_filed")
            if isinstance(date_filed_raw, (date, datetime)):
                filed_at = date_filed_raw
            else:
                filed_at = None  # unexpected type from the mirror -- don't guess-parse it

            results.append(
                EdgarMirrorFiling(
                    symbol=symbol,
                    accession_no=f.get("accession", ""),
                    form_type=f.get("form_type", ""),
                    filed_at=filed_at,
                    items=[],  # not tracked by this mirror
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
