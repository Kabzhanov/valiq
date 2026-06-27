# SPDX-License-Identifier: Apache-2.0
"""B1 Financial Value — 220 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import FinancialCfg
from valiq.blocks import rescale_block_score


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


def _m(id: str, name: str, weight: int, raw, score_fn, source: str, rationale_fn) -> MetricResult:
    """Build a MetricResult; marks absent (present=False) when raw is None."""
    if raw is None:
        return MetricResult(id=id, block="B1", name=name, weight=weight,
                            raw_value=None, score=0.0, source=source,
                            rationale="no data", present=False)
    return MetricResult(id=id, block="B1", name=name, weight=weight,
                        raw_value=float(raw), score=score_fn(raw), source=source,
                        rationale=rationale_fn(raw), present=True)


def score_b1(cfg: FinancialCfg) -> BlockResult:
    src = cfg.provider
    metrics = [
        _m("B1_MRR", "MRR", 40, cfg.mrr, score_mrr, src,
           lambda v: f"MRR=${v:,.0f}/mo"),
        _m("B1_ARR", "ARR", 35, cfg.arr, score_arr, src,
           lambda v: f"ARR=${v:,.0f}/yr"),
        _m("B1_Growth_MoM", "Growth MoM", 35, cfg.growth_mom_pct, score_growth, src,
           lambda v: f"MoM growth={v}%"),
        _m("B1_Churn", "Churn Rate", 30, cfg.churn_pct, score_churn, src,
           lambda v: f"Churn={v}%/mo"),
        _m("B1_ARPU", "ARPU", 25, cfg.arpu, score_arpu, src,
           lambda v: f"ARPU=${v:,.0f}"),
        _m("B1_Gross_Margin", "Gross Margin", 30, cfg.gross_margin_pct, score_gross_margin, src,
           lambda v: f"Gross margin={v}%"),
        _m("B1_Burn_Runway", "Burn Rate/Runway", 25, cfg.burn_runway_months, score_burn_runway, src,
           lambda v: f"Runway={v} months"),
    ]
    return BlockResult(code="B1", name="Financial Value", weight=220,
                       metrics=metrics, block_score=rescale_block_score(metrics, 220),
                       no_data=not any(m.present for m in metrics))
