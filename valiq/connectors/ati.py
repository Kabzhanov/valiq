# SPDX-License-Identifier: Apache-2.0
"""ATI connector — reads AI Trust Index score for the ATI gate (Block 6)."""
from __future__ import annotations
from typing import Optional


class ATIConnector:
    """Fetches ATI score from bizdnai.com/index/ or ATI cabinet API."""
    def __init__(self, site_url: str = "", source: str = "manual",
                 manual_score: Optional[float] = None):
        self.site_url = site_url
        self.source = source
        self.manual_score = manual_score

    def get_ati_score(self) -> Optional[float]:
        """Return ATI score (0-10) or None if unavailable."""
        if self.manual_score is not None:
            return float(self.manual_score)
        if self.source == "cabinet" and self.site_url:
            return self._fetch_from_cabinet()
        return None

    def _fetch_from_cabinet(self) -> Optional[float]:
        """Fetch ATI score from valiq.json or ATI cabinet API."""
        try:
            import httpx
            url = self.site_url.rstrip("/") + "/valiq.json"
            resp = httpx.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                score = data.get("ati_score") or data.get("index")
                if score is not None:
                    return float(score)
            # Try ati.json
            url2 = self.site_url.rstrip("/") + "/ati.json"
            resp2 = httpx.get(url2, timeout=10)
            if resp2.status_code == 200:
                data2 = resp2.json()
                score2 = data2.get("index") or data2.get("ati_score")
                if score2 is not None:
                    return float(score2)
        except Exception:
            pass
        return None


def get_ati_score(ati_cfg, compliance_cfg=None) -> Optional[float]:
    """Convenience function: returns ATI score or None."""
    manual = getattr(ati_cfg, "score", None)
    if manual is None and compliance_cfg is not None:
        manual = getattr(compliance_cfg, "ati_score_manual", None)
    connector = ATIConnector(
        site_url=getattr(ati_cfg, "site_url", ""),
        source=getattr(ati_cfg, "source", "manual"),
        manual_score=manual,
    )
    return connector.get_ati_score()
