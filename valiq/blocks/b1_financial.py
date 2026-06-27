# SPDX-License-Identifier: Apache-2.0
"""B1 Financial Value — 220 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import FinancialCfg


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def score_mrr(mrr: float) -> float:
    """Score MRR: 0=0, 10k=3, 50k=6, 100k=8, 200k+=10."""
    if mrr <= 0: return 0.0
    if mrr < 10_000: return _clamp(mrr / 10_000 * 3)
    if mrr < 50_000: return _clamp(3 + (mrr - 10_000) / 40_000 * 3)
    if mrr < 100_000: return _clamp(6 + (mrr - 50_000) / 50_000 * 2)
    if mrr < 200_000: return _clamp(8 + (mrr - 100_000) / 100_000 * 2)
    return 10.0


def score_arr(arr: float) -> float:
    """Score ARR (annual): 0=0, 120k=3, 500k=6, 1M=8, 2M+=10."""
    if arr <= 0: return 0.0
    if arr < 120_000: return _clamp(arr / 120_000 * 3)
    if arr < 500_000: return _clamp(3 + (arr - 120_000) / 380_000 * 3)
    if arr < 1_000_000: return _clamp(6 + (arr - 500_000) / 500_000 * 2)
    if arr < 2_000_000: return _clamp(8 + (arr - 1_000_000) / 1_000_000 * 2)
    return 10.0


def score_growth(growth_mom_pct: float) -> float:
    """Score MoM growth: <0=0, 0-2%=2, 2-5%=4, 5-10%=6, 10-15%=8, 15%+=10."""
    g = growth_mom_pct
    if g < 0: return 0.0
    if g < 2: return _clamp(g / 2 * 2)
    if g < 5: return _clamp(2 + (g - 2) / 3 * 2)
    if g < 10: return _clamp(4 + (g - 5) / 5 * 2)
    if g < 15: return _clamp(6 + (g - 10) / 5 * 2)
    return 10.0


def score_churn(churn_pct: float) -> float:
    """Score churn (lower=better): >10%=0, 5-10%=3, 2-5%=6, 1-2%=8, <1%=10."""
    c = churn_pct
    if c >= 10: return 0.0
    if c >= 5: return _clamp((10 - c) / 5 * 3)
    if c >= 2: return _clamp(3 + (5 - c) / 3 * 3)
    if c >= 1: return _clamp(6 + (2 - c) / 1 * 2)
    return 10.0


def score_arpu(arpu: float) -> float:
    """Score ARPU: <10=1, 10-50=3, 50-200=6, 200-500=8, 500+=10."""
    if arpu <= 0: return 0.0
    if arpu < 10: return 1.0
    if arpu < 50: return _clamp(1 + (arpu - 10) / 40 * 2)
    if arpu < 200: return _clamp(3 + (arpu - 50) / 150 * 3)
    if arpu < 500: return _clamp(6 + (arpu - 200) / 300 * 2)
    return 10.0


def score_gross_margin(gm_pct: float) -> float:
    """Score gross margin: <30%=2, 30-50%=5, 50-70%=7, 70%+=10."""
    if gm_pct < 0: return 0.0
    if gm_pct < 30: return _clamp(gm_pct / 30 * 2)
    if gm_pct < 50: return _clamp(2 + (gm_pct - 30) / 20 * 3)
    if gm_pct < 70: return _clamp(5 + (gm_pct - 50) / 20 * 2)
    return 10.0


def score_burn_runway(months: float) -> float:
    """Score runway months: <3=0, 3-6=3, 6-12=6, 12-18=8, 18+=10."""
    if months <= 0: return 0.0
    if months < 3: return _clamp(months / 3 * 3)
    if months < 6: return _clamp(3 + (months - 3) / 3 * 3)
    if months < 12: return _clamp(6 + (months - 6) / 6 * 2)
    if months < 18: return _clamp(8 + (months - 12) / 6 * 2)
    return 10.0


def score_b1(cfg: FinancialCfg) -> BlockResult:
    metrics = [
        MetricResult(id="B1_MRR", block="B1", name="MRR", weight=40,
                     raw_value=cfg.mrr, score=score_mrr(cfg.mrr), source=cfg.provider,
                     rationale=f"MRR=${cfg.mrr:,.0f}/mo"),
        MetricResult(id="B1_ARR", block="B1", name="ARR", weight=35,
                     raw_value=cfg.arr, score=score_arr(cfg.arr), source=cfg.provider,
                     rationale=f"ARR=${cfg.arr:,.0f}/yr"),
        MetricResult(id="B1_Growth_MoM", block="B1", name="Growth MoM", weight=35,
                     raw_value=cfg.growth_mom_pct, score=score_growth(cfg.growth_mom_pct),
                     source=cfg.provider, rationale=f"MoM growth={cfg.growth_mom_pct}%"),
        MetricResult(id="B1_Churn", block="B1", name="Churn Rate", weight=30,
                     raw_value=cfg.churn_pct, score=score_churn(cfg.churn_pct),
                     source=cfg.provider, rationale=f"Churn={cfg.churn_pct}%/mo"),
        MetricResult(id="B1_ARPU", block="B1", name="ARPU", weight=25,
                     raw_value=cfg.arpu, score=score_arpu(cfg.arpu), source=cfg.provider,
                     rationale=f"ARPU=${cfg.arpu:,.0f}"),
        MetricResult(id="B1_Gross_Margin", block="B1", name="Gross Margin", weight=30,
                     raw_value=cfg.gross_margin_pct, score=score_gross_margin(cfg.gross_margin_pct),
                     source=cfg.provider, rationale=f"Gross margin={cfg.gross_margin_pct}%"),
        MetricResult(id="B1_Burn_Runway", block="B1", name="Burn Rate/Runway", weight=25,
                     raw_value=cfg.burn_runway_months, score=score_burn_runway(cfg.burn_runway_months),
                     source=cfg.provider, rationale=f"Runway={cfg.burn_runway_months} months"),
    ]
    block_score = sum(m.score * m.weight for m in metrics) / 10.0
    return BlockResult(code="B1", name="Financial Value", weight=220,
                       metrics=metrics, block_score=block_score)
