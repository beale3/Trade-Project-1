# guardrail/catalysts/massive.py
#
# Block A -- Massive API Ingestion (Catalyst-Neutral, Final)
# Standalone ingestion utility -- structurally safe to merge; functionally
# incomplete until the Massive API endpoint (/filings, api.massive.com) is
# verified against real Massive API documentation. This module is NOT used
# by Guardrail v2.1 filters, SI-Gate, S3, or Composite scoring -- it exists
# only for optional research, metadata enrichment, and future validation.
# Guardrail v2.1 remains strictly catalyst-neutral (see spec/§7 and the
# catalyst-study finding that catalyst signals did not beat naive baselines
# under LOO + 5-fold x 30-seed testing).

import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import requests


@dataclass
class MassiveConfig:
    api_key: str
    base_url: str

    @staticmethod
    def from_env() -> "MassiveConfig":
        key = os.getenv("MASSIVE_API_KEY")
        if not key:
            raise RuntimeError("Missing MASSIVE_API_KEY environment variable")

        # NOTE: Placeholder base URL -- must be replaced with the correct endpoint
        base = os.getenv("MASSIVE_BASE_URL", "https://api.massive.com")

        return MassiveConfig(api_key=key, base_url=base)


@dataclass
class MassiveFiling:
    symbol: str
    filing_id: str
    form_type: str
    filed_at: Optional[datetime]
    raw: dict  # full JSON for research use


class MassiveClient:
    """
    Safe ingestion-only Massive API client.
    Does NOT integrate with Guardrail scoring.
    Endpoints must be verified before production use.
    """

    def __init__(self, config: MassiveConfig):
        self.config = config

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Accept": "application/json",
        }

    def get_filings(self, symbol: str, limit: int = 10) -> List[MassiveFiling]:
        """
        Fetch recent filings for research purposes only.
        Endpoint is a placeholder until verified.
        """
        url = f"{self.config.base_url}/filings"  # MUST be verified
        params = {"symbol": symbol, "limit": limit}

        resp = requests.get(url, headers=self._headers(), params=params)
        resp.raise_for_status()
        data = resp.json()

        filings = []
        for item in data:
            filed_at_raw = item.get("filed_at")
            if filed_at_raw:
                try:
                    filed_at = datetime.fromisoformat(filed_at_raw)
                except Exception:
                    filed_at = None
            else:
                filed_at = None

            filings.append(
                MassiveFiling(
                    symbol=symbol,
                    filing_id=item.get("id", ""),
                    form_type=item.get("form_type", ""),
                    filed_at=filed_at,
                    raw=item,
                )
            )
        return filings


# Important notes for implementers:
# - The /filings endpoint is placeholder only.
# - You must verify the correct Massive API endpoints before implementing.
# - This module is not part of Guardrail v2.1 scoring logic.
# - Structurally safe to merge; functionally incomplete until the Massive
#   API endpoint is verified.
