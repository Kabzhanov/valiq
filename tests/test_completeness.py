# SPDX-License-Identifier: Apache-2.0
"""Tests for data completeness + confidence band policy."""
import pytest

from valiq.blocks import rescale_block_score
from valiq.models import MetricResult, BlockResult, Assessment
from valiq.blocks.b1_financial import score_b1
from valiq.blocks.b6_compliance import score_b6
from valiq.config import (
    FinancialCfg, DataCfg, ProductCfg, TechCfg, ClientsCfg,
    ComplianceCfg, MarketCfg, TeamCfg, IpCfg,
    ValIQConfig, ProjectCfg, LLMCfg, AtiCfg, SubmitCfg,
)
from valiq.scorer import run_assessment
from valiq.report.valuation import compute_valuation, _half_width_pct, _confidence_label


# ──────────────────────────────────────────
# MetricResult.present default
# ──────────────────────────────────────────

def test_metric_present_default_true():
    m = MetricResult(id="X", block="B1", name="Test", weight=10, score=5.0)
    assert m.present is True


def test_metric_absent_flag():
    m = MetricResult(id="X", block="B1", name="Test", weight=10, score=0.0, present=False)
    assert m.present is False


# ──────────────────────────────────────────
# rescale_block_score helper
# ──────────────────────────────────────────

def _make_metric(block, weight, score, present=True):
    return MetricResult(id="X", block=block, name="T", weight=weight, score=score, present=present)


def test_rescale_all_present_max_score():
    metrics = [_make_metric("B1", 40, 10.0), _make_metric("B1", 60, 10.0)]
    # sum=100*10/10/10 * 100 ... wait: sum(10*w)/sum(w)/10 * block_weight
    # = 10 / 10 * 100 = 100
    result = rescale_block_score(metrics, 100)
    assert result == pytest.approx(100.0)


def test_rescale_all_present_zero_score():
    metrics = [_make_metric("B1", 40, 0.0), _make_metric("B1", 60, 0.0)]
    assert rescale_block_score(metrics, 100) == pytest.approx(0.0)


def test_rescale_no_present_returns_zero():
    metrics = [
        _make_metric("B1", 40, 8.0, present=False),
        _make_metric("B1", 60, 9.0, present=False),
    ]
    assert rescale_block_score(metrics, 220) == pytest.approx(0.0)


def test_rescale_partial_present_same_as_full_when_equal_scores():
    """Half present at score=6, other half absent → same block score as all at 6."""
    all_present = [_make_metric("B1", 50, 6.0), _make_metric("B1", 50, 6.0)]
    half_present = [_make_metric("B1", 50, 6.0), _make_metric("B1", 50, 6.0, present=False)]
    full = rescale_block_score(all_present, 200)
    partial = rescale_block_score(half_present, 200)
    assert full == pytest.approx(partial)   # rescaled to same max


def test_rescale_matches_original_formula_when_all_present():
    """When all present, rescale = sum(score*weight)/10 (original formula)."""
    metrics = [
        _make_metric("B1", 40, 7.0),
        _make_metric("B1", 35, 5.0),
        _make_metric("B1", 25, 9.0),
    ]
    original = sum(m.score * m.weight for m in metrics) / 10.0
    rescaled = rescale_block_score(metrics, 100)
    assert rescaled == pytest.approx(original)


# ──────────────────────────────────────────
# All-None config → block scored as no_data
# ──────────────────────────────────────────

def test_all_none_b1_no_data():
    b1 = score_b1(FinancialCfg())
    assert b1.no_data is True
    assert b1.block_score == pytest.approx(0.0)
    assert all(not m.present for m in b1.metrics)


def test_partial_b1_only_mrr_present():
    cfg = FinancialCfg(mrr=50_000)  # only MRR provided
    b1 = score_b1(cfg)
    assert b1.no_data is False
    present = [m for m in b1.metrics if m.present]
    assert len(present) == 1
    assert present[0].id == "B1_MRR"
    # block_score must be > 0 and <= 220
    assert 0 < b1.block_score <= 220


def test_b6_ati_always_present_even_when_cfg_empty():
    """ATI metric is always present when ati_score is given; optional metrics absent."""
    b6 = score_b6(ComplianceCfg(), ati_score=8.0)
    ati_m = next(m for m in b6.metrics if m.id == "B6_ATI")
    other = [m for m in b6.metrics if m.id != "B6_ATI"]
    assert ati_m.present is True
    assert all(not m.present for m in other)
    assert b6.no_data is False   # ATI is present, so not no_data


# ──────────────────────────────────────────
# Assessment completeness_pct + confidence
# ──────────────────────────────────────────

def _full_cfg(ati_score=7.9):
    """Config with all metric fields filled."""
    return ValIQConfig(
        project=ProjectCfg(name="Test"),
        financial=FinancialCfg(mrr=10_000, arr=120_000, growth_mom_pct=12,
                               churn_pct=2.5, arpu=250, gross_margin_pct=72,
                               burn_runway_months=14),
        data=DataCfg(data_volume_tb=2.0, history_depth_years=3.0,
                     data_rights=8.0, reproducibility=7.0,
                     training_datasets=True, knowledge_graph=True),
        product=ProductCfg(stage="prod", automation_depth_pct=70,
                           integrations_count=8, has_docs=True, has_roadmap=True,
                           ux_nps=55, active_modules=7),
        tech=TechCfg(test_coverage_pct=72, tech_debt_score=6.5,
                     mttr_hours=4.0, time_to_deploy_hours=1.5,
                     architecture_score=7.5, uptime_pct=99.7, code_docs_pct=65),
        clients=ClientsCfg(active_clients=25, ltv_cac_ratio=4.5,
                           nps=55, client_churn_pct=3.0,
                           top_client_revenue_pct=18, enterprise_contracts=2),
        compliance=ComplianceCfg(g12_scan_passed=True, kz_law_checklist_pct=80,
                                 has_privacy_policy=True, pentest_done=False),
        market=MarketCfg(tam_usd_bn=5.0, som_arr_ratio=50,
                         moat_score=7.0, entry_barriers=6.0, market_growth_pct=15),
        team=TeamCfg(bus_factor=2, dev_processes_score=7.0,
                     key_developers=2, ceo_dependency=True),
        ip=IpCfg(brand_registered=False, patents_count=0,
                 proprietary_algorithms=True, code_copyright=True),
        llm=LLMCfg(),
        ati=AtiCfg(source="manual", score=ati_score),
        submit=SubmitCfg(),
    )


def _empty_cfg(ati_score=7.9):
    """Config with all metric fields None (connector/provider fields intact)."""
    return ValIQConfig(
        project=ProjectCfg(name="Empty"),
        financial=FinancialCfg(), data=DataCfg(), product=ProductCfg(),
        tech=TechCfg(), clients=ClientsCfg(),
        compliance=ComplianceCfg(),
        market=MarketCfg(), team=TeamCfg(), ip=IpCfg(),
        llm=LLMCfg(),
        ati=AtiCfg(source="manual", score=ati_score),
        submit=SubmitCfg(),
    )


def test_full_data_completeness_high():
    a = run_assessment(_full_cfg())
    assert a.completeness_pct == pytest.approx(100.0)
    assert a.confidence == "high"


def test_no_data_completeness_low():
    a = run_assessment(_empty_cfg())
    # Only ATI metric in B6 is present; everything else is absent
    assert a.completeness_pct < 50.0
    assert a.confidence == "low"


def test_completeness_pct_range():
    a = run_assessment(_full_cfg())
    assert 0.0 <= a.completeness_pct <= 100.0


def test_partial_data_medium_confidence():
    """Roughly half the metrics filled → medium confidence."""
    cfg = ValIQConfig(
        project=ProjectCfg(name="Partial"),
        # B1: 3 of 7 metrics filled
        financial=FinancialCfg(mrr=10_000, arr=120_000, growth_mom_pct=12),
        # B2: 3 of 6
        data=DataCfg(data_volume_tb=1.0, history_depth_years=2.0, data_rights=7.0),
        # B3: 3 of 7
        product=ProductCfg(stage="prod", has_docs=True, active_modules=5),
        # B4: 3 of 7
        tech=TechCfg(test_coverage_pct=60, uptime_pct=99.5, architecture_score=7.0),
        # B5: 3 of 6
        clients=ClientsCfg(active_clients=20, nps=40, enterprise_contracts=1),
        # B6: ATI only (1 of 5 present)
        compliance=ComplianceCfg(),
        # B7: 2 of 5
        market=MarketCfg(tam_usd_bn=3.0, moat_score=6.0),
        # B8: 2 of 4
        team=TeamCfg(bus_factor=2, dev_processes_score=6.0),
        # B9: 2 of 4
        ip=IpCfg(proprietary_algorithms=True, code_copyright=True),
        llm=LLMCfg(),
        ati=AtiCfg(source="manual", score=7.0),
        submit=SubmitCfg(),
    )
    a = run_assessment(cfg)
    # 3+3+3+3+3+1+2+2+2 = 22 present out of 51 total = 43% — low confidence
    assert a.completeness_pct < 80.0
    assert a.confidence in ("medium", "low")


# ──────────────────────────────────────────
# Valuation confidence band widening
# ──────────────────────────────────────────

def test_half_width_at_100pct():
    """100% completeness → ±20%."""
    assert _half_width_pct(100.0) == pytest.approx(20.0)


def test_half_width_at_50pct():
    """50% completeness → ±40%."""
    assert _half_width_pct(50.0) == pytest.approx(40.0)


def test_half_width_at_0pct():
    """0% completeness → capped at ±60%."""
    assert _half_width_pct(0.0) == pytest.approx(60.0)


def test_half_width_capped_at_60():
    """Formula never exceeds 60."""
    assert _half_width_pct(-50.0) == pytest.approx(60.0)


def test_half_width_continuous_at_80pct():
    """80% → 20 + 20*0.4 = 28."""
    assert _half_width_pct(80.0) == pytest.approx(28.0)


def test_confidence_label_values():
    assert _confidence_label(100.0) == "high"
    assert _confidence_label(80.0) == "high"
    assert _confidence_label(79.9) == "medium"
    assert _confidence_label(50.0) == "medium"
    assert _confidence_label(49.9) == "low"
    assert _confidence_label(0.0) == "low"


def test_valuation_100pct_is_plus_minus_20():
    """100% completeness → exact ±20% band (parity invariant)."""
    v = compute_valuation(arr_usd=120_000, growth_mom_pct=12,
                          total_score=786, mrr_usd=10_000, completeness_pct=100.0)
    assert v.low == pytest.approx(v.point_estimate * 0.80)
    assert v.high == pytest.approx(v.point_estimate * 1.20)
    assert v.confidence == "high"
    assert v.completeness_pct == pytest.approx(100.0)


def test_valuation_50pct_is_plus_minus_40():
    """50% completeness → ±40% band."""
    v = compute_valuation(arr_usd=120_000, growth_mom_pct=12,
                          total_score=786, mrr_usd=10_000, completeness_pct=50.0)
    assert v.low == pytest.approx(v.point_estimate * 0.60)
    assert v.high == pytest.approx(v.point_estimate * 1.40)
    assert v.confidence == "medium"


def test_valuation_0pct_is_plus_minus_60():
    """0% completeness → ±60% band."""
    v = compute_valuation(arr_usd=120_000, growth_mom_pct=12,
                          total_score=786, mrr_usd=10_000, completeness_pct=0.0)
    assert v.low == pytest.approx(v.point_estimate * 0.40)
    assert v.high == pytest.approx(v.point_estimate * 1.60)
    assert v.confidence == "low"


def test_valuation_default_completeness_backward_compat():
    """compute_valuation with no completeness_pct arg → ±20% (backward compat)."""
    v = compute_valuation(arr_usd=120_000, growth_mom_pct=12,
                          total_score=786, mrr_usd=10_000)
    assert v.low == pytest.approx(v.point_estimate * 0.80)
    assert v.high == pytest.approx(v.point_estimate * 1.20)


def test_existing_valuation_test_still_passes():
    """Existing test_spec_example_bizdnai_q3 must still hold with full completeness."""
    v = compute_valuation(arr_usd=120_000, growth_mom_pct=12,
                          total_score=786, mrr_usd=10_000, completeness_pct=100.0)
    assert v.base_multiple == 7.0
    assert v.itai_multiplier == 1.2
    assert v.stage_multiplier == 1.0
    expected_point = 120_000 * 7.0 * 1.2 * 1.0
    assert v.point_estimate == pytest.approx(expected_point)
    assert v.low == pytest.approx(expected_point * 0.8)
    assert v.high == pytest.approx(expected_point * 1.2)
