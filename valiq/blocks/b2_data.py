# SPDX-License-Identifier: Apache-2.0
"""B2 Data & Data Moat — 120 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import DataCfg
from valiq.blocks import rescale_block_score


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def _absent(id: str, name: str, weight: int) -> MetricResult:
    return MetricResult(id=id, block="B2", name=name, weight=weight,
                        raw_value=None, score=0.0, source="manual",
                        rationale="no data", present=False)


def score_b2(cfg: DataCfg) -> BlockResult:
    metrics: list[MetricResult] = []

    # Data Volume
    vol = cfg.data_volume_tb
    if vol is None:
        metrics.append(_absent("B2_Data_Volume", "Data Volume", 35))
    else:
        if vol <= 0: vol_s = 0.0
        elif vol < 0.1: vol_s = _clamp(vol / 0.1 * 3)
        elif vol < 1: vol_s = _clamp(3 + (vol - 0.1) / 0.9 * 3)
        elif vol < 10: vol_s = _clamp(6 + (vol - 1) / 9 * 2)
        elif vol < 100: vol_s = _clamp(8 + (vol - 10) / 90 * 2)
        else: vol_s = 10.0
        metrics.append(MetricResult(id="B2_Data_Volume", block="B2", name="Data Volume", weight=35,
                                    raw_value=vol, score=vol_s, source="manual",
                                    rationale=f"Data volume={vol}TB", present=True))

    # History Depth
    hist = cfg.history_depth_years
    if hist is None:
        metrics.append(_absent("B2_History_Depth", "History Depth", 25))
    else:
        if hist < 1: hist_s = _clamp(hist * 2)
        elif hist < 3: hist_s = _clamp(2 + (hist - 1) / 2 * 3)
        elif hist < 5: hist_s = _clamp(5 + (hist - 3) / 2 * 2)
        else: hist_s = 10.0
        metrics.append(MetricResult(id="B2_History_Depth", block="B2", name="History Depth", weight=25,
                                    raw_value=hist, score=hist_s, source="manual",
                                    rationale=f"History={hist} years", present=True))

    # Data Rights (0-10)
    dr = cfg.data_rights
    if dr is None:
        metrics.append(_absent("B2_Data_Rights", "Data Rights", 30))
    else:
        metrics.append(MetricResult(id="B2_Data_Rights", block="B2", name="Data Rights", weight=30,
                                    raw_value=dr, score=_clamp(dr), source="manual",
                                    rationale=f"Data rights score={dr}/10", present=True))

    # Reproducibility (0-10)
    rep = cfg.reproducibility
    if rep is None:
        metrics.append(_absent("B2_Reproducibility", "Reproducibility", 25))
    else:
        metrics.append(MetricResult(id="B2_Reproducibility", block="B2", name="Reproducibility", weight=25,
                                    raw_value=rep, score=_clamp(rep), source="manual",
                                    rationale=f"Moat/reproducibility={rep}/10", present=True))

    # Training Datasets (bool)
    td = cfg.training_datasets
    if td is None:
        metrics.append(_absent("B2_Training_Datasets", "Training Datasets", 20))
    else:
        metrics.append(MetricResult(id="B2_Training_Datasets", block="B2", name="Training Datasets", weight=20,
                                    raw_value=float(td), score=10.0 if td else 0.0, source="manual",
                                    rationale="Has proprietary training datasets" if td else "No training datasets",
                                    present=True))

    # Knowledge Graph (bool)
    kg = cfg.knowledge_graph
    if kg is None:
        metrics.append(_absent("B2_Knowledge_Graph", "Knowledge Graph", 15))
    else:
        metrics.append(MetricResult(id="B2_Knowledge_Graph", block="B2", name="Knowledge Graph", weight=15,
                                    raw_value=float(kg), score=10.0 if kg else 0.0, source="manual",
                                    rationale="Has knowledge graph / data moat" if kg else "No knowledge graph",
                                    present=True))

    return BlockResult(code="B2", name="Data & Data Moat", weight=120,
                       metrics=metrics, block_score=rescale_block_score(metrics, 120),
                       no_data=not any(m.present for m in metrics))
