# SPDX-License-Identifier: Apache-2.0
"""B7 Market & Competition — 80 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import MarketCfg


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def score_b7(cfg: MarketCfg) -> BlockResult:
    # TAM USD billions: <1B=5, 1-10B=15, >10B=20 → normalise to 0-10
    tam = cfg.tam_usd_bn
    if tam <= 0: tam_score = 0.0
    elif tam < 1: tam_score = _clamp(tam * 5)
    elif tam < 10: tam_score = _clamp(5 + (tam - 1) / 9 * 5)
    else: tam_score = 10.0

    # SOM/ARR ratio: <5=2, 5-50=5, 50-500=8, 500+=10
    som = cfg.som_arr_ratio
    if som <= 0: som_score = 0.0
    elif som < 5: som_score = _clamp(som / 5 * 2)
    elif som < 50: som_score = _clamp(2 + (som - 5) / 45 * 3)
    elif som < 500: som_score = _clamp(5 + (som - 50) / 450 * 3)
    else: som_score = 10.0

    # Moat score: already 0-10 (LLM judge or manual)
    moat_score = _clamp(cfg.moat_score)

    # Entry barriers: already 0-10
    barrier_score = _clamp(cfg.entry_barriers)

    # Market growth %/yr: <5=2, 5-10=5, 10-20=7, 20%+=10
    mg = cfg.market_growth_pct
    if mg < 5: mg_score = _clamp(mg / 5 * 2)
    elif mg < 10: mg_score = _clamp(2 + (mg - 5) / 5 * 3)
    elif mg < 20: mg_score = _clamp(5 + (mg - 10) / 10 * 2)
    else: mg_score = 10.0

    metrics = [
        MetricResult(id="B7_TAM", block="B7", name="TAM", weight=20,
                     raw_value=tam, score=tam_score, source="manual",
                     rationale=f"TAM=${tam}B"),
        MetricResult(id="B7_SOM_ARR", block="B7", name="SOM/ARR", weight=20,
                     raw_value=som, score=som_score, source="manual",
                     rationale=f"SOM/ARR ratio={som:.1f}x"),
        MetricResult(id="B7_Moat", block="B7", name="Competitive Moat", weight=20,
                     raw_value=cfg.moat_score, score=moat_score, source="manual",
                     rationale=f"Moat score={cfg.moat_score}/10"),
        MetricResult(id="B7_Entry_Barriers", block="B7", name="Entry Barriers", weight=10,
                     raw_value=cfg.entry_barriers, score=barrier_score, source="manual",
                     rationale=f"Entry barriers={cfg.entry_barriers}/10"),
        MetricResult(id="B7_Market_Growth", block="B7", name="Market Growth", weight=10,
                     raw_value=mg, score=mg_score, source="manual",
                     rationale=f"Market growth={mg}%/yr"),
    ]
    block_score = sum(m.score * m.weight for m in metrics) / 10.0
    return BlockResult(code="B7", name="Market & Competition", weight=80,
                       metrics=metrics, block_score=block_score)
