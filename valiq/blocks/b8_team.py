# SPDX-License-Identifier: Apache-2.0
"""B8 Team — 50 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import TeamCfg


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def score_b8(cfg: TeamCfg) -> BlockResult:
    # Bus factor: 1=2, 2=5, 3+=10
    bf = cfg.bus_factor
    if bf <= 1: bf_score = 2.0
    elif bf == 2: bf_score = 5.0
    elif bf < 5: bf_score = _clamp(5 + (bf - 2) / 3 * 5)
    else: bf_score = 10.0

    # Dev processes: already 0-10
    proc_score = _clamp(cfg.dev_processes_score)

    # Key developers (tech lead + seniors): 0=0, 1=4, 2=7, 3+=10
    kd = cfg.key_developers
    if kd == 0: kd_score = 0.0
    elif kd == 1: kd_score = 4.0
    elif kd == 2: kd_score = 7.0
    else: kd_score = 10.0

    # CEO dependency: can product run 30d without CEO? Yes=10, No=0
    ceo_score = 0.0 if cfg.ceo_dependency else 10.0

    metrics = [
        MetricResult(id="B8_Bus_Factor", block="B8", name="Bus Factor", weight=15,
                     raw_value=float(bf), score=bf_score, source="manual",
                     rationale=f"Bus factor={bf} people"),
        MetricResult(id="B8_Dev_Processes", block="B8", name="Dev Processes", weight=15,
                     raw_value=cfg.dev_processes_score, score=proc_score, source="manual",
                     rationale=f"Dev processes maturity={cfg.dev_processes_score}/10"),
        MetricResult(id="B8_Key_Developers", block="B8", name="Key Developers", weight=10,
                     raw_value=float(kd), score=kd_score, source="manual",
                     rationale=f"Tech leads + seniors={kd}"),
        MetricResult(id="B8_CEO_Dependency", block="B8", name="CEO Dependency", weight=10,
                     raw_value=float(cfg.ceo_dependency), score=ceo_score, source="manual",
                     rationale="Product runs without CEO" if not cfg.ceo_dependency else "High CEO dependency"),
    ]
    block_score = sum(m.score * m.weight for m in metrics) / 10.0
    return BlockResult(code="B8", name="Team", weight=50,
                       metrics=metrics, block_score=block_score)
