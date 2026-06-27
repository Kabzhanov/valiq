# SPDX-License-Identifier: Apache-2.0
"""B2 Data & Data Moat — 150 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import DataCfg


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def score_b2(cfg: DataCfg, llm_moat_score: float = 5.0) -> BlockResult:
    # Data Volume: 0TB=0, 0.1TB=3, 1TB=6, 10TB=8, 100TB+=10
    vol = cfg.data_volume_tb
    if vol <= 0: vol_score = 0.0
    elif vol < 0.1: vol_score = _clamp(vol / 0.1 * 3)
    elif vol < 1: vol_score = _clamp(3 + (vol - 0.1) / 0.9 * 3)
    elif vol < 10: vol_score = _clamp(6 + (vol - 1) / 9 * 2)
    elif vol < 100: vol_score = _clamp(8 + (vol - 10) / 90 * 2)
    else: vol_score = 10.0

    # History Depth: <1yr=2, 1-3yr=5, 3-5yr=7, 5yr+=10
    hist = cfg.history_depth_years
    if hist < 1: hist_score = _clamp(hist * 2)
    elif hist < 3: hist_score = _clamp(2 + (hist - 1) / 2 * 3)
    elif hist < 5: hist_score = _clamp(5 + (hist - 3) / 2 * 2)
    else: hist_score = 10.0

    # Data Rights: already 0-10 from YAML
    rights_score = _clamp(cfg.data_rights)

    # Reproducibility (LLM judge or manual 0-10): already 0-10
    repro_score = _clamp(cfg.reproducibility)

    # Training datasets: binary 0 or 10
    train_score = 10.0 if cfg.training_datasets else 0.0

    # Knowledge Graph: binary 0 or 10
    kg_score = 10.0 if cfg.knowledge_graph else 0.0

    metrics = [
        MetricResult(id="B2_Data_Volume", block="B2", name="Data Volume", weight=35,
                     raw_value=vol, score=vol_score, source="manual",
                     rationale=f"Data volume={vol}TB"),
        MetricResult(id="B2_History_Depth", block="B2", name="History Depth", weight=25,
                     raw_value=hist, score=hist_score, source="manual",
                     rationale=f"History={hist} years"),
        MetricResult(id="B2_Data_Rights", block="B2", name="Data Rights", weight=30,
                     raw_value=cfg.data_rights, score=rights_score, source="manual",
                     rationale=f"Data rights score={cfg.data_rights}/10"),
        MetricResult(id="B2_Reproducibility", block="B2", name="Reproducibility", weight=25,
                     raw_value=cfg.reproducibility, score=repro_score, source="manual",
                     rationale=f"Moat/reproducibility={cfg.reproducibility}/10"),
        MetricResult(id="B2_Training_Datasets", block="B2", name="Training Datasets", weight=20,
                     raw_value=float(cfg.training_datasets), score=train_score, source="manual",
                     rationale="Has proprietary training datasets" if cfg.training_datasets else "No training datasets"),
        MetricResult(id="B2_Knowledge_Graph", block="B2", name="Knowledge Graph", weight=15,
                     raw_value=float(cfg.knowledge_graph), score=kg_score, source="manual",
                     rationale="Has knowledge graph / data moat" if cfg.knowledge_graph else "No knowledge graph"),
    ]
    block_score = sum(m.score * m.weight for m in metrics) / 10.0
    return BlockResult(code="B2", name="Data & Data Moat", weight=150,
                       metrics=metrics, block_score=block_score)
