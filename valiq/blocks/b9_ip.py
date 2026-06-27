# SPDX-License-Identifier: Apache-2.0
"""B9 Intellectual Property — 30 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import IpCfg


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def score_b9(cfg: IpCfg) -> BlockResult:
    brand_score = 10.0 if cfg.brand_registered else 0.0

    # Patents: each patent + 4 pts (max 2 patents=10)
    # Weight is 8, score 0-10
    patents_raw_score = min(10.0, cfg.patents_count * 4.0)

    algo_score = 10.0 if cfg.proprietary_algorithms else 0.0
    copy_score = 10.0 if cfg.code_copyright else 0.0

    metrics = [
        MetricResult(id="B9_Brand_TM", block="B9", name="Brand / TM", weight=8,
                     raw_value=float(cfg.brand_registered), score=brand_score, source="manual",
                     rationale="Brand/TM registered" if cfg.brand_registered else "No registered brand"),
        MetricResult(id="B9_Patents", block="B9", name="Patents", weight=8,
                     raw_value=float(cfg.patents_count), score=patents_raw_score, source="manual",
                     rationale=f"Patents={cfg.patents_count} (each +4 pts, max 10)"),
        MetricResult(id="B9_Algorithms", block="B9", name="Proprietary Algorithms", weight=8,
                     raw_value=float(cfg.proprietary_algorithms), score=algo_score, source="manual",
                     rationale="Proprietary algorithms/models in prod" if cfg.proprietary_algorithms else "No proprietary algorithms"),
        MetricResult(id="B9_Code_Copyright", block="B9", name="Code Copyright", weight=6,
                     raw_value=float(cfg.code_copyright), score=copy_score, source="manual",
                     rationale="Code owned by legal entity" if cfg.code_copyright else "No formal code copyright"),
    ]
    block_score = sum(m.score * m.weight for m in metrics) / 10.0
    return BlockResult(code="B9", name="Intellectual Property", weight=30,
                       metrics=metrics, block_score=block_score)
