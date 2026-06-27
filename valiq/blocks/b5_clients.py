# SPDX-License-Identifier: Apache-2.0
"""B5 Client Base — 120 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import ClientsCfg


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def score_b5(cfg: ClientsCfg) -> BlockResult:
    # Active clients: 0=0, 5=3, 20=5, 100=7, 500+=10
    c = cfg.active_clients
    if c == 0: c_score = 0.0
    elif c < 5: c_score = _clamp(c / 5 * 3)
    elif c < 20: c_score = _clamp(3 + (c - 5) / 15 * 2)
    elif c < 100: c_score = _clamp(5 + (c - 20) / 80 * 2)
    elif c < 500: c_score = _clamp(7 + (c - 100) / 400 * 3)
    else: c_score = 10.0

    # LTV/CAC: <1=0, 1-3=4, 3-5=6, 5-10=8, 10+=10
    ltv = cfg.ltv_cac_ratio
    if ltv < 1: ltv_score = _clamp(ltv * 4)
    elif ltv < 3: ltv_score = _clamp(4)
    elif ltv < 5: ltv_score = _clamp(4 + (ltv - 3) / 2 * 2)
    elif ltv < 10: ltv_score = _clamp(6 + (ltv - 5) / 5 * 2)
    else: ltv_score = 10.0

    # NPS: <0=0, 0-30=3, 30-50=5, 50-70=7, 70+=10
    nps = cfg.nps
    if nps < 0: nps_score = 0.0
    elif nps < 30: nps_score = _clamp(nps / 30 * 3)
    elif nps < 50: nps_score = _clamp(3 + (nps - 30) / 20 * 2)
    elif nps < 70: nps_score = _clamp(5 + (nps - 50) / 20 * 2)
    else: nps_score = 10.0

    # Client churn (lower=better): >10=0, 5-10=3, 2-5=6, 1-2=8, <1=10
    cc = cfg.client_churn_pct
    if cc >= 10: cc_score = 0.0
    elif cc >= 5: cc_score = _clamp((10 - cc) / 5 * 3)
    elif cc >= 2: cc_score = _clamp(3 + (5 - cc) / 3 * 3)
    elif cc >= 1: cc_score = _clamp(6 + (2 - cc) * 2)
    else: cc_score = 10.0

    # Concentration (top-1 client % revenue, lower=better):
    # >50%=0, 30-50%=4, 20-30%=6, 10-20%=8, <10%=10
    conc = cfg.top_client_revenue_pct
    if conc > 50: conc_score = 0.0
    elif conc > 30: conc_score = _clamp((50 - conc) / 20 * 4)
    elif conc > 20: conc_score = _clamp(4 + (30 - conc) / 10 * 2)
    elif conc > 10: conc_score = _clamp(6 + (20 - conc) / 10 * 2)
    else: conc_score = 10.0

    # Enterprise contracts: 0=0, 1=5, 3=7, 5+=10
    ec = cfg.enterprise_contracts
    if ec == 0: ec_score = 0.0
    elif ec == 1: ec_score = 5.0
    elif ec < 3: ec_score = _clamp(5 + (ec - 1) / 2 * 2)
    elif ec < 5: ec_score = _clamp(7 + (ec - 3) / 2 * 3)
    else: ec_score = 10.0

    metrics = [
        MetricResult(id="B5_Active_Clients", block="B5", name="Active Clients", weight=25,
                     raw_value=float(c), score=c_score, source=cfg.provider,
                     rationale=f"Active clients={c}"),
        MetricResult(id="B5_LTV_CAC", block="B5", name="LTV/CAC", weight=25,
                     raw_value=ltv, score=ltv_score, source=cfg.provider,
                     rationale=f"LTV/CAC={ltv:.1f}x"),
        MetricResult(id="B5_NPS", block="B5", name="NPS", weight=20,
                     raw_value=nps, score=nps_score, source=cfg.provider,
                     rationale=f"NPS={nps}"),
        MetricResult(id="B5_Churn", block="B5", name="Client Churn", weight=15,
                     raw_value=cc, score=cc_score, source=cfg.provider,
                     rationale=f"Client churn={cc}%/mo"),
        MetricResult(id="B5_Concentration", block="B5", name="Client Concentration", weight=20,
                     raw_value=conc, score=conc_score, source=cfg.provider,
                     rationale=f"Top client={conc}% of revenue"),
        MetricResult(id="B5_Enterprise_Contracts", block="B5", name="Enterprise Contracts", weight=15,
                     raw_value=float(ec), score=ec_score, source=cfg.provider,
                     rationale=f"Enterprise/govt contracts={ec}"),
    ]
    block_score = sum(m.score * m.weight for m in metrics) / 10.0
    return BlockResult(code="B5", name="Client Base", weight=120,
                       metrics=metrics, block_score=block_score)
