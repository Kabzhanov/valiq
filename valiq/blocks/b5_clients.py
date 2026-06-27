# SPDX-License-Identifier: Apache-2.0
"""B5 Client Base — 180 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import ClientsCfg
from valiq.blocks import rescale_block_score


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def _absent(id: str, name: str, weight: int, source: str = "manual") -> MetricResult:
    return MetricResult(id=id, block="B5", name=name, weight=weight,
                        raw_value=None, score=0.0, source=source,
                        rationale="no data", present=False)


def score_b5(cfg: ClientsCfg) -> BlockResult:
    src = cfg.provider
    metrics: list[MetricResult] = []

    # Active clients
    c = cfg.active_clients
    if c is None:
        metrics.append(_absent("B5_Active_Clients", "Active Clients", 25, src))
    else:
        if c == 0: c_s = 0.0
        elif c < 5: c_s = _clamp(c / 5 * 3)
        elif c < 20: c_s = _clamp(3 + (c - 5) / 15 * 2)
        elif c < 100: c_s = _clamp(5 + (c - 20) / 80 * 2)
        elif c < 500: c_s = _clamp(7 + (c - 100) / 400 * 3)
        else: c_s = 10.0
        metrics.append(MetricResult(id="B5_Active_Clients", block="B5", name="Active Clients", weight=25,
                                    raw_value=float(c), score=c_s, source=src,
                                    rationale=f"Active clients={c}", present=True))

    # LTV/CAC ratio
    ltv = cfg.ltv_cac_ratio
    if ltv is None:
        metrics.append(_absent("B5_LTV_CAC", "LTV/CAC", 25, src))
    else:
        if ltv < 1: ltv_s = _clamp(ltv * 4)
        elif ltv < 3: ltv_s = _clamp(4)
        elif ltv < 5: ltv_s = _clamp(4 + (ltv - 3) / 2 * 2)
        elif ltv < 10: ltv_s = _clamp(6 + (ltv - 5) / 5 * 2)
        else: ltv_s = 10.0
        metrics.append(MetricResult(id="B5_LTV_CAC", block="B5", name="LTV/CAC", weight=25,
                                    raw_value=ltv, score=ltv_s, source=src,
                                    rationale=f"LTV/CAC={ltv:.1f}x", present=True))

    # NPS
    nps = cfg.nps
    if nps is None:
        metrics.append(_absent("B5_NPS", "NPS", 20, src))
    else:
        if nps < 0: nps_s = 0.0
        elif nps < 30: nps_s = _clamp(nps / 30 * 3)
        elif nps < 50: nps_s = _clamp(3 + (nps - 30) / 20 * 2)
        elif nps < 70: nps_s = _clamp(5 + (nps - 50) / 20 * 2)
        else: nps_s = 10.0
        metrics.append(MetricResult(id="B5_NPS", block="B5", name="NPS", weight=20,
                                    raw_value=nps, score=nps_s, source=src,
                                    rationale=f"NPS={nps}", present=True))

    # Client churn (lower=better)
    cc = cfg.client_churn_pct
    if cc is None:
        metrics.append(_absent("B5_Churn", "Client Churn", 15, src))
    else:
        if cc >= 10: cc_s = 0.0
        elif cc >= 5: cc_s = _clamp((10 - cc) / 5 * 3)
        elif cc >= 2: cc_s = _clamp(3 + (5 - cc) / 3 * 3)
        elif cc >= 1: cc_s = _clamp(6 + (2 - cc) * 2)
        else: cc_s = 10.0
        metrics.append(MetricResult(id="B5_Churn", block="B5", name="Client Churn", weight=15,
                                    raw_value=cc, score=cc_s, source=src,
                                    rationale=f"Client churn={cc}%/mo", present=True))

    # Concentration (top-1 client %, lower=better)
    conc = cfg.top_client_revenue_pct
    if conc is None:
        metrics.append(_absent("B5_Concentration", "Client Concentration", 20, src))
    else:
        if conc > 50: conc_s = 0.0
        elif conc > 30: conc_s = _clamp((50 - conc) / 20 * 4)
        elif conc > 20: conc_s = _clamp(4 + (30 - conc) / 10 * 2)
        elif conc > 10: conc_s = _clamp(6 + (20 - conc) / 10 * 2)
        else: conc_s = 10.0
        metrics.append(MetricResult(id="B5_Concentration", block="B5", name="Client Concentration", weight=20,
                                    raw_value=conc, score=conc_s, source=src,
                                    rationale=f"Top client={conc}% of revenue", present=True))

    # Enterprise contracts
    ec = cfg.enterprise_contracts
    if ec is None:
        metrics.append(_absent("B5_Enterprise_Contracts", "Enterprise Contracts", 15, src))
    else:
        if ec == 0: ec_s = 0.0
        elif ec == 1: ec_s = 5.0
        elif ec < 3: ec_s = _clamp(5 + (ec - 1) / 2 * 2)
        elif ec < 5: ec_s = _clamp(7 + (ec - 3) / 2 * 3)
        else: ec_s = 10.0
        metrics.append(MetricResult(id="B5_Enterprise_Contracts", block="B5", name="Enterprise Contracts", weight=15,
                                    raw_value=float(ec), score=ec_s, source=src,
                                    rationale=f"Enterprise/govt contracts={ec}", present=True))

    return BlockResult(code="B5", name="Client Base", weight=180,
                       metrics=metrics, block_score=rescale_block_score(metrics, 180),
                       no_data=not any(m.present for m in metrics))
