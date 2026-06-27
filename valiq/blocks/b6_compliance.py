# SPDX-License-Identifier: Apache-2.0
"""B6 Trust & Compliance — 100 points. Requires ATI score (hard gate)."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import ComplianceCfg
from valiq.blocks import rescale_block_score


class ATIRequiredError(Exception):
    """Raised when ATI score is required but not available."""
    def __init__(self):
        super().__init__(
            "ATI score is required for Block 6 (Compliance). "
            "Please obtain your AI Trust Index score at https://bizdnai.com/index/ first."
        )


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def _absent(id: str, name: str, weight: int, source: str = "manual") -> MetricResult:
    return MetricResult(id=id, block="B6", name=name, weight=weight,
                        raw_value=None, score=0.0, source=source,
                        rationale="no data", present=False)


def score_b6(cfg: ComplianceCfg, ati_score: float | None = None) -> BlockResult:
    """Score Block 6. ati_score must be 0-10. Raises ATIRequiredError if absent."""
    if ati_score is None:
        raise ATIRequiredError()

    metrics: list[MetricResult] = []

    # ATI metric — always present when score_b6 is called (gate above)
    ati_metric_score = _clamp(ati_score)
    metrics.append(MetricResult(id="B6_ATI", block="B6", name="AI Trust Index", weight=40,
                                raw_value=ati_score, score=ati_metric_score, source="ati",
                                rationale=f"ATI score={ati_score}/10 → ATI×4={ati_metric_score*4:.1f} pts",
                                present=True))

    # G12 scan (bool, optional)
    g12 = cfg.g12_scan_passed
    if g12 is None:
        metrics.append(_absent("B6_G12_Scan", "G12 Infrastructure Scan", 20, "ati"))
    else:
        metrics.append(MetricResult(id="B6_G12_Scan", block="B6", name="G12 Infrastructure Scan", weight=20,
                                    raw_value=float(g12), score=10.0 if g12 else 0.0, source="ati",
                                    rationale="G12 scan passed" if g12 else "G12 scan not passed",
                                    present=True))

    # KZ law checklist % (0-100, optional)
    kz = cfg.kz_law_checklist_pct
    if kz is None:
        metrics.append(_absent("B6_KZ_Law_230", "KZ Law 230-VIII", 15))
    else:
        metrics.append(MetricResult(id="B6_KZ_Law_230", block="B6", name="KZ Law 230-VIII", weight=15,
                                    raw_value=kz, score=_clamp(kz / 10.0), source="manual",
                                    rationale=f"KZ law checklist={kz}%", present=True))

    # Privacy policy (bool, optional)
    pp = cfg.has_privacy_policy
    if pp is None:
        metrics.append(_absent("B6_Privacy_Policy", "Privacy Policy", 10))
    else:
        metrics.append(MetricResult(id="B6_Privacy_Policy", block="B6", name="Privacy Policy", weight=10,
                                    raw_value=float(pp), score=10.0 if pp else 0.0, source="manual",
                                    rationale="Privacy Policy/DPA present" if pp else "No Privacy Policy",
                                    present=True))

    # Pentest (bool, optional)
    pt = cfg.pentest_done
    if pt is None:
        metrics.append(_absent("B6_Pentest", "Security Audit", 15))
    else:
        metrics.append(MetricResult(id="B6_Pentest", block="B6", name="Security Audit", weight=15,
                                    raw_value=float(pt), score=10.0 if pt else 0.0, source="manual",
                                    rationale="Pentest done <12mo" if pt else "No recent pentest",
                                    present=True))

    return BlockResult(code="B6", name="Trust & Compliance", weight=100,
                       metrics=metrics, block_score=rescale_block_score(metrics, 100),
                       no_data=not any(m.present for m in metrics))
