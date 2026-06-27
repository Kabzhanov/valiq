# SPDX-License-Identifier: Apache-2.0
"""B7 Market & Competition — 70 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import MarketCfg
from valiq.blocks import rescale_block_score


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def _absent(id: str, name: str, weight: int) -> MetricResult:
    return MetricResult(id=id, block="B7", name=name, weight=weight,
                        raw_value=None, score=0.0, source="manual",
                        rationale="no data", present=False)


def score_b7(cfg: MarketCfg) -> BlockResult:
    metrics: list[MetricResult] = []

    # TAM USD billions
    tam = cfg.tam_usd_bn
    if tam is None:
        metrics.append(_absent("B7_TAM", "TAM", 20))
    else:
        if tam <= 0: tam_s = 0.0
        elif tam < 1: tam_s = _clamp(tam * 5)
        elif tam < 10: tam_s = _clamp(5 + (tam - 1) / 9 * 5)
        else: tam_s = 10.0
        metrics.append(MetricResult(id="B7_TAM", block="B7", name="TAM", weight=20,
                                    raw_value=tam, score=tam_s, source="manual",
                                    rationale=f"TAM=${tam}B", present=True))

    # SOM/ARR ratio
    som = cfg.som_arr_ratio
    if som is None:
        metrics.append(_absent("B7_SOM_ARR", "SOM/ARR", 20))
    else:
        if som <= 0: som_s = 0.0
        elif som < 5: som_s = _clamp(som / 5 * 2)
        elif som < 50: som_s = _clamp(2 + (som - 5) / 45 * 3)
        elif som < 500: som_s = _clamp(5 + (som - 50) / 450 * 3)
        else: som_s = 10.0
        metrics.append(MetricResult(id="B7_SOM_ARR", block="B7", name="SOM/ARR", weight=20,
                                    raw_value=som, score=som_s, source="manual",
                                    rationale=f"SOM/ARR ratio={som:.1f}x", present=True))

    # Moat score (0-10)
    moat = cfg.moat_score
    if moat is None:
        metrics.append(_absent("B7_Moat", "Competitive Moat", 20))
    else:
        metrics.append(MetricResult(id="B7_Moat", block="B7", name="Competitive Moat", weight=20,
                                    raw_value=moat, score=_clamp(moat), source="manual",
                                    rationale=f"Moat score={moat}/10", present=True))

    # Entry barriers (0-10)
    barriers = cfg.entry_barriers
    if barriers is None:
        metrics.append(_absent("B7_Entry_Barriers", "Entry Barriers", 10))
    else:
        metrics.append(MetricResult(id="B7_Entry_Barriers", block="B7", name="Entry Barriers", weight=10,
                                    raw_value=barriers, score=_clamp(barriers), source="manual",
                                    rationale=f"Entry barriers={barriers}/10", present=True))

    # Market growth %/yr
    mg = cfg.market_growth_pct
    if mg is None:
        metrics.append(_absent("B7_Market_Growth", "Market Growth", 10))
    else:
        if mg < 5: mg_s = _clamp(mg / 5 * 2)
        elif mg < 10: mg_s = _clamp(2 + (mg - 5) / 5 * 3)
        elif mg < 20: mg_s = _clamp(5 + (mg - 10) / 10 * 2)
        else: mg_s = 10.0
        metrics.append(MetricResult(id="B7_Market_Growth", block="B7", name="Market Growth", weight=10,
                                    raw_value=mg, score=mg_s, source="manual",
                                    rationale=f"Market growth={mg}%/yr", present=True))

    return BlockResult(code="B7", name="Market & Competition", weight=70,
                       metrics=metrics, block_score=rescale_block_score(metrics, 70),
                       no_data=not any(m.present for m in metrics))
