# SPDX-License-Identifier: Apache-2.0
"""B9 Intellectual Property — 30 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import IpCfg
from valiq.blocks import rescale_block_score


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def _absent(id: str, name: str, weight: int) -> MetricResult:
    return MetricResult(id=id, block="B9", name=name, weight=weight,
                        raw_value=None, score=0.0, source="manual",
                        rationale="no data", present=False)


def score_b9(cfg: IpCfg) -> BlockResult:
    metrics: list[MetricResult] = []

    # Brand / TM (bool)
    br = cfg.brand_registered
    if br is None:
        metrics.append(_absent("B9_Brand_TM", "Brand / TM", 8))
    else:
        metrics.append(MetricResult(id="B9_Brand_TM", block="B9", name="Brand / TM", weight=8,
                                    raw_value=float(br), score=10.0 if br else 0.0, source="manual",
                                    rationale="Brand/TM registered" if br else "No registered brand",
                                    present=True))

    # Patents count
    pc = cfg.patents_count
    if pc is None:
        metrics.append(_absent("B9_Patents", "Patents", 8))
    else:
        metrics.append(MetricResult(id="B9_Patents", block="B9", name="Patents", weight=8,
                                    raw_value=float(pc), score=min(10.0, pc * 4.0), source="manual",
                                    rationale=f"Patents={pc} (each +4 pts, max 10)",
                                    present=True))

    # Proprietary algorithms (bool)
    algo = cfg.proprietary_algorithms
    if algo is None:
        metrics.append(_absent("B9_Algorithms", "Proprietary Algorithms", 8))
    else:
        metrics.append(MetricResult(id="B9_Algorithms", block="B9", name="Proprietary Algorithms", weight=8,
                                    raw_value=float(algo), score=10.0 if algo else 0.0, source="manual",
                                    rationale="Proprietary algorithms/models in prod" if algo else "No proprietary algorithms",
                                    present=True))

    # Code copyright (bool)
    copy = cfg.code_copyright
    if copy is None:
        metrics.append(_absent("B9_Code_Copyright", "Code Copyright", 6))
    else:
        metrics.append(MetricResult(id="B9_Code_Copyright", block="B9", name="Code Copyright", weight=6,
                                    raw_value=float(copy), score=10.0 if copy else 0.0, source="manual",
                                    rationale="Code owned by legal entity" if copy else "No formal code copyright",
                                    present=True))

    return BlockResult(code="B9", name="Intellectual Property", weight=30,
                       metrics=metrics, block_score=rescale_block_score(metrics, 30),
                       no_data=not any(m.present for m in metrics))
