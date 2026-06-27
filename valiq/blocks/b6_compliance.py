# SPDX-License-Identifier: Apache-2.0
"""B6 Trust & Compliance — 100 points. Requires ATI score (hard gate)."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import ComplianceCfg


class ATIRequiredError(Exception):
    """Raised when ATI score is required but not available."""
    def __init__(self):
        super().__init__(
            "ATI score is required for Block 6 (Compliance). "
            "Please obtain your AI Trust Index score at https://bizdnai.com/index/ first."
        )


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def score_b6(cfg: ComplianceCfg, ati_score: float | None = None) -> BlockResult:
    """Score Block 6. ati_score must be 0-10. Raises ATIRequiredError if absent."""
    if ati_score is None:
        raise ATIRequiredError()

    ati_metric_score = _clamp(ati_score)  # 0-10; weight=40 → contributes up to 40 pts
    g12_score = 10.0 if cfg.g12_scan_passed else 0.0
    kz_score = _clamp(cfg.kz_law_checklist_pct / 10.0)  # 0-100% → 0-10
    pp_score = 10.0 if cfg.has_privacy_policy else 0.0
    pentest_score = 10.0 if cfg.pentest_done else 0.0

    metrics = [
        MetricResult(id="B6_ATI", block="B6", name="AI Trust Index", weight=40,
                     raw_value=ati_score, score=ati_metric_score, source="ati",
                     rationale=f"ATI score={ati_score}/10 → ATI×4={ati_metric_score*4:.1f} pts"),
        MetricResult(id="B6_G12_Scan", block="B6", name="G12 Infrastructure Scan", weight=20,
                     raw_value=float(cfg.g12_scan_passed), score=g12_score, source="ati",
                     rationale="G12 scan passed" if cfg.g12_scan_passed else "G12 scan not passed"),
        MetricResult(id="B6_KZ_Law_230", block="B6", name="KZ Law 230-VIII", weight=15,
                     raw_value=cfg.kz_law_checklist_pct, score=kz_score, source="manual",
                     rationale=f"KZ law checklist={cfg.kz_law_checklist_pct}%"),
        MetricResult(id="B6_Privacy_Policy", block="B6", name="Privacy Policy", weight=10,
                     raw_value=float(cfg.has_privacy_policy), score=pp_score, source="manual",
                     rationale="Privacy Policy/DPA present" if cfg.has_privacy_policy else "No Privacy Policy"),
        MetricResult(id="B6_Pentest", block="B6", name="Security Audit", weight=15,
                     raw_value=float(cfg.pentest_done), score=pentest_score, source="manual",
                     rationale="Pentest done <12mo" if cfg.pentest_done else "No recent pentest"),
    ]
    block_score = sum(m.score * m.weight for m in metrics) / 10.0
    return BlockResult(code="B6", name="Trust & Compliance", weight=100,
                       metrics=metrics, block_score=block_score)
