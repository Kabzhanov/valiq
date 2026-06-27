# SPDX-License-Identifier: Apache-2.0
"""Valuation formula: Valuation = ARR × Base_Multiple × ITAI_Multiplier × Stage_Multiplier."""
from __future__ import annotations
from valiq.models import Valuation


def _fmt_usd(v: float) -> str:
    """Format USD value: $1.2M, $450K, $95K."""
    if v >= 1_000_000:
        return f"${v / 1_000_000:.2f}M"
    if v >= 1_000:
        return f"${v / 1_000:.0f}K"
    return f"${v:.0f}"


def base_multiple(growth_mom_pct: float) -> tuple[float, float, float]:
    """Returns (point_multiple, low, high) based on MoM growth."""
    if growth_mom_pct < 5:
        return 4.0, 3.0, 5.0
    if growth_mom_pct <= 15:
        return 7.0, 5.0, 10.0
    return 15.0, 10.0, 20.0


def itai_multiplier(total_score: float) -> float:
    """Returns ITAI multiplier based on total ITAI Score (0-1000)."""
    if total_score < 400:
        return 0.5
    if total_score < 600:
        return 0.8
    if total_score < 750:
        return 1.0
    if total_score < 850:
        return 1.2
    if total_score < 950:
        return 1.5
    return 2.0


def stage_multiplier(mrr_usd: float) -> tuple[float, str]:
    """Returns (multiplier, stage_label) based on MRR."""
    if mrr_usd <= 0:
        return 0.2, "pre_revenue"
    if mrr_usd < 10_000:
        return 0.5, "early"
    if mrr_usd < 50_000:
        return 1.0, "growth"
    if mrr_usd < 200_000:
        return 1.5, "scale"
    return 2.0, "mature"


def _band_factors(completeness_pct: float) -> tuple[float, float]:
    """Return (low_factor, high_factor) based on data completeness.

    high (>=80%): ±20%   → 0.80 / 1.20
    medium (>=50%): ±35% → 0.65 / 1.35
    low (<50%): ±50%     → 0.50 / 1.50
    """
    if completeness_pct >= 80:
        return 0.80, 1.20
    if completeness_pct >= 50:
        return 0.65, 1.35
    return 0.50, 1.50


def _confidence_label(completeness_pct: float) -> str:
    if completeness_pct >= 80:
        return "high"
    if completeness_pct >= 50:
        return "medium"
    return "low"


def compute_valuation(
    arr_usd: float,
    growth_mom_pct: float,
    total_score: float,
    mrr_usd: float,
    completeness_pct: float = 100.0,
) -> Valuation:
    """Compute USD valuation range from financials and ITAI Score.

    The confidence band widens when completeness_pct is low:
    - >=80% completeness → ±20% (high confidence)
    - 50-80% → ±35% (medium confidence)
    - <50% → ±50% (low confidence)
    """
    bm_point, bm_low, bm_high = base_multiple(growth_mom_pct)
    im = itai_multiplier(total_score)
    sm, stage = stage_multiplier(mrr_usd)

    point = arr_usd * bm_point * im * sm
    low_factor, high_factor = _band_factors(completeness_pct)
    low = point * low_factor
    high = point * high_factor
    confidence = _confidence_label(completeness_pct)

    return Valuation(
        arr_usd=arr_usd,
        growth_mom_pct=growth_mom_pct,
        base_multiple=bm_point,
        itai_multiplier=im,
        stage_multiplier=sm,
        point_estimate=point,
        low=low,
        high=high,
        display=f"{_fmt_usd(low)} – {_fmt_usd(high)}",
        stage=stage,
        completeness_pct=completeness_pct,
        confidence=confidence,
    )
