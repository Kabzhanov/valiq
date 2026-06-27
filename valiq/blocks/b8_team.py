# SPDX-License-Identifier: Apache-2.0
"""B8 Team — 50 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import TeamCfg
from valiq.blocks import rescale_block_score


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def _absent(id: str, name: str, weight: int) -> MetricResult:
    return MetricResult(id=id, block="B8", name=name, weight=weight,
                        raw_value=None, score=0.0, source="manual",
                        rationale="no data", present=False)


def score_b8(cfg: TeamCfg) -> BlockResult:
    metrics: list[MetricResult] = []

    # Bus factor
    bf = cfg.bus_factor
    if bf is None:
        metrics.append(_absent("B8_Bus_Factor", "Bus Factor", 15))
    else:
        if bf <= 1: bf_s = 2.0
        elif bf == 2: bf_s = 5.0
        elif bf < 5: bf_s = _clamp(5 + (bf - 2) / 3 * 5)
        else: bf_s = 10.0
        metrics.append(MetricResult(id="B8_Bus_Factor", block="B8", name="Bus Factor", weight=15,
                                    raw_value=float(bf), score=bf_s, source="manual",
                                    rationale=f"Bus factor={bf} people", present=True))

    # Dev processes score (0-10)
    proc = cfg.dev_processes_score
    if proc is None:
        metrics.append(_absent("B8_Dev_Processes", "Dev Processes", 15))
    else:
        metrics.append(MetricResult(id="B8_Dev_Processes", block="B8", name="Dev Processes", weight=15,
                                    raw_value=proc, score=_clamp(proc), source="manual",
                                    rationale=f"Dev processes maturity={proc}/10", present=True))

    # Key developers
    kd = cfg.key_developers
    if kd is None:
        metrics.append(_absent("B8_Key_Developers", "Key Developers", 10))
    else:
        if kd == 0: kd_s = 0.0
        elif kd == 1: kd_s = 4.0
        elif kd == 2: kd_s = 7.0
        else: kd_s = 10.0
        metrics.append(MetricResult(id="B8_Key_Developers", block="B8", name="Key Developers", weight=10,
                                    raw_value=float(kd), score=kd_s, source="manual",
                                    rationale=f"Tech leads + seniors={kd}", present=True))

    # CEO dependency (bool; False=good, product runs without CEO)
    ceo = cfg.ceo_dependency
    if ceo is None:
        metrics.append(_absent("B8_CEO_Dependency", "CEO Dependency", 10))
    else:
        metrics.append(MetricResult(id="B8_CEO_Dependency", block="B8", name="CEO Dependency", weight=10,
                                    raw_value=float(ceo), score=0.0 if ceo else 10.0, source="manual",
                                    rationale="Product runs without CEO" if not ceo else "High CEO dependency",
                                    present=True))

    return BlockResult(code="B8", name="Team", weight=50,
                       metrics=metrics, block_score=rescale_block_score(metrics, 50),
                       no_data=not any(m.present for m in metrics))
