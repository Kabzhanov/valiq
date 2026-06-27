# SPDX-License-Identifier: Apache-2.0
"""Tests for the ATI gate (hard invariant, SPEC 1.1)."""
import pytest

from valiq.config import (
    ValIQConfig, ProjectCfg, FinancialCfg, DataCfg, ProductCfg, TechCfg,
    ClientsCfg, ComplianceCfg, MarketCfg, TeamCfg, IpCfg, LLMCfg, AtiCfg, SubmitCfg,
)
from valiq.scorer import run_assessment
from valiq.blocks.b6_compliance import score_b6, ATIRequiredError


def _cfg(ati_score=None):
    return ValIQConfig(
        project=ProjectCfg(name="Test"),
        financial=FinancialCfg(arr=120_000, mrr=10_000, growth_mom_pct=12),
        data=DataCfg(),
        product=ProductCfg(),
        tech=TechCfg(),
        clients=ClientsCfg(),
        compliance=ComplianceCfg(),
        market=MarketCfg(),
        team=TeamCfg(),
        ip=IpCfg(),
        llm=LLMCfg(),
        ati=AtiCfg(source="manual", score=ati_score),
        submit=SubmitCfg(),
    )


def test_b6_raises_without_ati():
    with pytest.raises(ATIRequiredError):
        score_b6(ComplianceCfg(), ati_score=None)


def test_b6_scores_with_ati():
    b6 = score_b6(ComplianceCfg(), ati_score=7.9)
    assert b6.code == "B6"
    # ATI metric score should equal the ATI value (0-10).
    ati_metric = next(m for m in b6.metrics if m.id == "B6_ATI")
    assert ati_metric.score == pytest.approx(7.9)


def test_gate_blocks_valuation_when_no_ati():
    a = run_assessment(_cfg(ati_score=None))
    assert a.ati_status == "ati_required"
    assert a.partial is True
    # B1-B5, B7-B9 still computed (8 real blocks + 1 placeholder B6 = 9)
    assert len(a.blocks) == 9
    # B6 is inactive / zero-scored
    b6 = next(b for b in a.blocks if b.code == "B6")
    assert b6.active is False
    assert b6.block_score == 0.0


def test_gate_open_when_ati_present():
    a = run_assessment(_cfg(ati_score=7.9))
    assert a.ati_status == "ok"
    assert a.partial is False
    assert a.ati_score == pytest.approx(7.9)
    b6 = next(b for b in a.blocks if b.code == "B6")
    assert b6.active is True
    assert b6.block_score > 0.0


def test_other_blocks_score_even_without_ati():
    a = run_assessment(_cfg(ati_score=None))
    b1 = next(b for b in a.blocks if b.code == "B1")
    assert b1.block_score > 0.0   # financials still scored
