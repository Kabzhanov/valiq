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


def compute_valuation(
    arr_usd: float,
    growth_mom_pct: float,
    total_score: float,
    mrr_usd: float,
) -> Valuation:
    """Compute USD valuation range from financials and ITAI Score."""
    bm_point, bm_low, bm_high = base_multiple(growth_mom_pct)
    im = itai_multiplier(total_score)
    sm, stage = stage_multiplier(mrr_usd)

    point = arr_usd * bm_point * im * sm
    low = point * 0.8
    high = point * 1.2

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
    )
