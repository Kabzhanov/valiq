# SPDX-License-Identifier: Apache-2.0
"""B4 Technology — 160 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import TechCfg
from valiq.blocks import rescale_block_score


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def _absent(id: str, name: str, weight: int, source: str = "manual") -> MetricResult:
    return MetricResult(id=id, block="B4", name=name, weight=weight,
                        raw_value=None, score=0.0, source=source,
                        rationale="no data", present=False)


def score_b4(cfg: TechCfg) -> BlockResult:
    src = cfg.provider
    metrics: list[MetricResult] = []

    # Test coverage %
    cov = cfg.test_coverage_pct
    if cov is None:
        metrics.append(_absent("B4_Test_Coverage", "Test Coverage", 20, src))
    else:
        if cov < 40: cov_s = _clamp(cov / 40 * 4)
        elif cov < 60: cov_s = _clamp(4 + (cov - 40) / 20 * 2)
        elif cov < 80: cov_s = _clamp(6 + (cov - 60) / 20 * 2)
        elif cov < 90: cov_s = _clamp(8 + (cov - 80) / 10 * 2)
        else: cov_s = 10.0
        metrics.append(MetricResult(id="B4_Test_Coverage", block="B4", name="Test Coverage", weight=20,
                                    raw_value=cov, score=cov_s, source=src,
                                    rationale=f"Test coverage={cov}%", present=True))

    # Tech debt score (0-10, 10=no debt)
    debt = cfg.tech_debt_score
    if debt is None:
        metrics.append(_absent("B4_Tech_Debt", "Tech Debt", 20, src))
    else:
        metrics.append(MetricResult(id="B4_Tech_Debt", block="B4", name="Tech Debt", weight=20,
                                    raw_value=debt, score=_clamp(debt), source=src,
                                    rationale=f"Tech debt score={debt}/10 (10=none)", present=True))

    # MTTR hours (lower=better)
    mttr = cfg.mttr_hours
    if mttr is None:
        metrics.append(_absent("B4_MTTR", "MTTR", 18, src))
    else:
        if mttr > 72: mttr_s = 0.0
        elif mttr > 24: mttr_s = _clamp((72 - mttr) / 48 * 4)
        elif mttr > 8: mttr_s = _clamp(4 + (24 - mttr) / 16 * 2)
        elif mttr > 2: mttr_s = _clamp(6 + (8 - mttr) / 6 * 2)
        else: mttr_s = 10.0
        metrics.append(MetricResult(id="B4_MTTR", block="B4", name="MTTR", weight=18,
                                    raw_value=mttr, score=mttr_s, source=src,
                                    rationale=f"MTTR={mttr}h", present=True))

    # Time to deploy hours (lower=better)
    ttd = cfg.time_to_deploy_hours
    if ttd is None:
        metrics.append(_absent("B4_Time_to_Deploy", "Time to Deploy", 15, src))
    else:
        if ttd > 24: ttd_s = 0.0
        elif ttd > 4: ttd_s = _clamp((24 - ttd) / 20 * 4)
        elif ttd > 1: ttd_s = _clamp(4 + (4 - ttd) / 3 * 3)
        else: ttd_s = 10.0
        metrics.append(MetricResult(id="B4_Time_to_Deploy", block="B4", name="Time to Deploy", weight=15,
                                    raw_value=ttd, score=ttd_s, source=src,
                                    rationale=f"Deploy time={ttd}h", present=True))

    # Architecture score (0-10)
    arch = cfg.architecture_score
    if arch is None:
        metrics.append(_absent("B4_Architecture", "Architecture", 20, "manual"))
    else:
        metrics.append(MetricResult(id="B4_Architecture", block="B4", name="Architecture", weight=20,
                                    raw_value=arch, score=_clamp(arch), source="manual",
                                    rationale=f"Architecture score={arch}/10", present=True))

    # Uptime %
    up = cfg.uptime_pct
    if up is None:
        metrics.append(_absent("B4_Uptime", "Uptime", 15, src))
    else:
        if up < 95: up_s = 0.0
        elif up < 99: up_s = _clamp((up - 95) / 4 * 5)
        elif up < 99.5: up_s = _clamp(5 + (up - 99) / 0.5 * 2)
        elif up < 99.9: up_s = _clamp(7 + (up - 99.5) / 0.4 * 1)
        else: up_s = 10.0
        metrics.append(MetricResult(id="B4_Uptime", block="B4", name="Uptime", weight=15,
                                    raw_value=up, score=up_s, source=src,
                                    rationale=f"Uptime={up}%", present=True))

    # Code docs %
    cdoc = cfg.code_docs_pct
    if cdoc is None:
        metrics.append(_absent("B4_Code_Docs", "Code Documentation", 12, src))
    else:
        metrics.append(MetricResult(id="B4_Code_Docs", block="B4", name="Code Documentation", weight=12,
                                    raw_value=cdoc, score=_clamp(cdoc / 10.0), source=src,
                                    rationale=f"Code docs={cdoc}%", present=True))

    return BlockResult(code="B4", name="Technology", weight=160,
                       metrics=metrics, block_score=rescale_block_score(metrics, 160),
                       no_data=not any(m.present for m in metrics))
