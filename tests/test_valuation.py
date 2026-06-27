# SPDX-License-Identifier: Apache-2.0
"""Tests for the valuation formula."""
import pytest

from valiq.report.valuation import (
    base_multiple, itai_multiplier, stage_multiplier, compute_valuation,
)


def test_base_multiple_by_growth():
    assert base_multiple(3)[0] == 4.0     # <5%
    assert base_multiple(10)[0] == 7.0    # 5-15%
    assert base_multiple(25)[0] == 15.0   # >15%


def test_itai_multiplier_thresholds():
    assert itai_multiplier(300) == 0.5
    assert itai_multiplier(500) == 0.8
    assert itai_multiplier(700) == 1.0
    assert itai_multiplier(800) == 1.2
    assert itai_multiplier(900) == 1.5
    assert itai_multiplier(980) == 2.0


def test_stage_multiplier_by_mrr():
    assert stage_multiplier(0) == (0.2, "pre_revenue")
    assert stage_multiplier(5_000)[0] == 0.5
    assert stage_multiplier(30_000)[0] == 1.0
    assert stage_multiplier(100_000)[0] == 1.5
    assert stage_multiplier(300_000)[0] == 2.0


def test_spec_example_bizdnai_q3():
    """Spec example: ARR $120k x 8x x 1.2 (Score 786) x 1.0 = $1.15M.
    Our base multiple for 12% MoM is 7x (mid of 5-10 range), stage 1.0 at $10k MRR.
    Verify the formula wiring and the ±20% range rather than the exact 8x."""
    v = compute_valuation(arr_usd=120_000, growth_mom_pct=12,
                          total_score=786, mrr_usd=10_000)
    assert v.base_multiple == 7.0
    assert v.itai_multiplier == 1.2     # 786 is in 750-850
    assert v.stage_multiplier == 1.0    # $10k MRR
    expected_point = 120_000 * 7.0 * 1.2 * 1.0
    assert v.point_estimate == pytest.approx(expected_point)
    assert v.low == pytest.approx(expected_point * 0.8)
    assert v.high == pytest.approx(expected_point * 1.2)


def test_range_is_plus_minus_20pct():
    v = compute_valuation(arr_usd=1_000_000, growth_mom_pct=20,
                          total_score=900, mrr_usd=300_000)
    assert v.low == pytest.approx(v.point_estimate * 0.8)
    assert v.high == pytest.approx(v.point_estimate * 1.2)


def test_display_string_format():
    v = compute_valuation(arr_usd=120_000, growth_mom_pct=12,
                          total_score=786, mrr_usd=10_000)
    # point = 1,008,000 → low 806,400 → "$0.81M", high 1,209,600 → "$1.21M"
    assert " – " in v.display
    assert v.display.startswith("$")


def test_pre_revenue_low_valuation():
    v = compute_valuation(arr_usd=0, growth_mom_pct=2,
                          total_score=300, mrr_usd=0)
    assert v.stage == "pre_revenue"
    assert v.point_estimate == 0.0
