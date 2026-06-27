# SPDX-License-Identifier: Apache-2.0
"""B4 Technology — 120 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import TechCfg


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def score_b4(cfg: TechCfg) -> BlockResult:
    # Test coverage %: 0=0, 40=4, 60=6, 80=8, 90%+=10
    cov = cfg.test_coverage_pct
    if cov < 40: cov_score = _clamp(cov / 40 * 4)
    elif cov < 60: cov_score = _clamp(4 + (cov - 40) / 20 * 2)
    elif cov < 80: cov_score = _clamp(6 + (cov - 60) / 20 * 2)
    elif cov < 90: cov_score = _clamp(8 + (cov - 80) / 10 * 2)
    else: cov_score = 10.0

    # Tech debt (0-10 score, 10=no debt): already normalised
    debt_score = _clamp(cfg.tech_debt_score)

    # MTTR hours (lower=better): >72h=0, 24-72h=4, 8-24h=6, 2-8h=8, <2h=10
    mttr = cfg.mttr_hours
    if mttr > 72: mttr_score = 0.0
    elif mttr > 24: mttr_score = _clamp((72 - mttr) / 48 * 4)
    elif mttr > 8: mttr_score = _clamp(4 + (24 - mttr) / 16 * 2)
    elif mttr > 2: mttr_score = _clamp(6 + (8 - mttr) / 6 * 2)
    else: mttr_score = 10.0

    # Time to deploy hours (lower=better): >24h=0, 4-24h=4, 1-4h=7, <1h=10
    ttd = cfg.time_to_deploy_hours
    if ttd > 24: ttd_score = 0.0
    elif ttd > 4: ttd_score = _clamp((24 - ttd) / 20 * 4)
    elif ttd > 1: ttd_score = _clamp(4 + (4 - ttd) / 3 * 3)
    else: ttd_score = 10.0

    # Architecture (0-10 from LLM judge or manual)
    arch_score = _clamp(cfg.architecture_score)

    # Uptime %: <95=0, 95-99=5, 99-99.5=7, 99.5-99.9=8, 99.9%+=10
    up = cfg.uptime_pct
    if up < 95: up_score = 0.0
    elif up < 99: up_score = _clamp((up - 95) / 4 * 5)
    elif up < 99.5: up_score = _clamp(5 + (up - 99) / 0.5 * 2)
    elif up < 99.9: up_score = _clamp(7 + (up - 99.5) / 0.4 * 1)
    else: up_score = 10.0

    # Code docs %: 0=0, 30=3, 60=6, 80=8, 100=10
    cdoc = cfg.code_docs_pct
    cdoc_score = _clamp(cdoc / 10.0)

    metrics = [
        MetricResult(id="B4_Test_Coverage", block="B4", name="Test Coverage", weight=20,
                     raw_value=cov, score=cov_score, source=cfg.provider,
                     rationale=f"Test coverage={cov}%"),
        MetricResult(id="B4_Tech_Debt", block="B4", name="Tech Debt", weight=20,
                     raw_value=cfg.tech_debt_score, score=debt_score, source=cfg.provider,
                     rationale=f"Tech debt score={cfg.tech_debt_score}/10 (10=none)"),
        MetricResult(id="B4_MTTR", block="B4", name="MTTR", weight=18,
                     raw_value=mttr, score=mttr_score, source=cfg.provider,
                     rationale=f"MTTR={mttr}h"),
        MetricResult(id="B4_Time_to_Deploy", block="B4", name="Time to Deploy", weight=15,
                     raw_value=ttd, score=ttd_score, source=cfg.provider,
                     rationale=f"Deploy time={ttd}h"),
        MetricResult(id="B4_Architecture", block="B4", name="Architecture", weight=20,
                     raw_value=cfg.architecture_score, score=arch_score, source="manual",
                     rationale=f"Architecture score={cfg.architecture_score}/10"),
        MetricResult(id="B4_Uptime", block="B4", name="Uptime", weight=15,
                     raw_value=up, score=up_score, source=cfg.provider,
                     rationale=f"Uptime={up}%"),
        MetricResult(id="B4_Code_Docs", block="B4", name="Code Documentation", weight=12,
                     raw_value=cdoc, score=cdoc_score, source=cfg.provider,
                     rationale=f"Code docs={cdoc}%"),
    ]
    block_score = sum(m.score * m.weight for m in metrics) / 10.0
    return BlockResult(code="B4", name="Technology", weight=120,
                       metrics=metrics, block_score=block_score)
