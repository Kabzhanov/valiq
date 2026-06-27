# SPDX-License-Identifier: Apache-2.0
"""Tests for the scorer: weights, determinism, block sums."""
import os

import pytest

from valiq.config import load_config
from valiq.scorer import run_assessment
from valiq.blocks.b1_financial import score_b1
from valiq.blocks.b2_data import score_b2
from valiq.blocks.b3_product import score_b3
from valiq.blocks.b4_tech import score_b4
from valiq.blocks.b5_clients import score_b5
from valiq.blocks.b6_compliance import score_b6
from valiq.blocks.b7_market import score_b7
from valiq.blocks.b8_team import score_b8
from valiq.blocks.b9_ip import score_b9
from valiq.config import (
    FinancialCfg, DataCfg, ProductCfg, TechCfg, ClientsCfg,
    ComplianceCfg, MarketCfg, TeamCfg, IpCfg,
)

_EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "examples", "valiq.yaml")

# Expected block weights per the spec (sum = 1000).
_EXPECTED_BLOCK_WEIGHTS = {
    "B1": 220, "B2": 150, "B3": 130, "B4": 120, "B5": 120,
    "B6": 100, "B7": 80, "B8": 50, "B9": 30,
}

# Expected per-metric weights per block (must sum to the block weight).
_EXPECTED_METRIC_WEIGHTS = {
    "B1": [40, 35, 35, 30, 25, 30, 25],
    "B2": [35, 25, 30, 25, 20, 15],
    "B3": [30, 25, 20, 15, 15, 10, 15],
    "B4": [20, 20, 18, 15, 20, 15, 12],
    "B5": [25, 25, 20, 15, 20, 15],
    "B6": [40, 20, 15, 10, 15],
    "B7": [20, 20, 20, 10, 10],
    "B8": [15, 15, 10, 10],
    "B9": [8, 8, 8, 6],
}


def _all_blocks():
    return [
        score_b1(FinancialCfg()),
        score_b2(DataCfg()),
        score_b3(ProductCfg()),
        score_b4(TechCfg()),
        score_b5(ClientsCfg()),
        score_b6(ComplianceCfg(), ati_score=5.0),
        score_b7(MarketCfg()),
        score_b8(TeamCfg()),
        score_b9(IpCfg()),
    ]


def test_block_weights_sum_to_1000():
    total = sum(b.weight for b in _all_blocks())
    assert total == 1000


def test_each_block_weight_matches_spec():
    for b in _all_blocks():
        assert b.weight == _EXPECTED_BLOCK_WEIGHTS[b.code], b.code


def test_metric_weights_sum_to_block_weight():
    for b in _all_blocks():
        metric_sum = sum(m.weight for m in b.metrics)
        assert metric_sum == b.weight, f"{b.code}: metrics sum {metric_sum} != {b.weight}"


def test_metric_weights_match_appendix_a():
    for b in _all_blocks():
        weights = [m.weight for m in b.metrics]
        assert weights == _EXPECTED_METRIC_WEIGHTS[b.code], b.code


def test_total_metric_count():
    # The enumerated weight model (Appendix A) defines 51 weighted metrics
    # summing to 1000 points across 9 blocks. ("54" is the spec's headline figure;
    # the authoritative weight table lists 51.)
    count = sum(len(b.metrics) for b in _all_blocks())
    assert count == 51


def test_block_score_never_exceeds_weight():
    # Perfect 10/10 metrics → block_score == weight
    for b in _all_blocks():
        assert 0.0 <= b.block_score <= b.weight + 1e-9, b.code


def test_example_scores_deterministically():
    cfg = load_config(os.path.abspath(_EXAMPLE))
    a1 = run_assessment(cfg)
    a2 = run_assessment(cfg)
    assert a1.total_score == a2.total_score
    assert a1.ati_status == "ok"
    # Example has ATI=7.9, healthy financials → mid-high score, within range.
    assert 0 < a1.total_score <= 1000
    assert a1.total_score == pytest.approx(a2.total_score)


def test_example_total_equals_sum_of_blocks():
    cfg = load_config(os.path.abspath(_EXAMPLE))
    a = run_assessment(cfg)
    block_sum = sum(b.block_score for b in a.blocks)
    assert a.total_score == pytest.approx(block_sum)


def test_only_single_block():
    cfg = load_config(os.path.abspath(_EXAMPLE))
    a = run_assessment(cfg, only="B1")
    assert len(a.blocks) == 1
    assert a.blocks[0].code == "B1"
