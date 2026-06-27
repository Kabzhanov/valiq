# SPDX-License-Identifier: Apache-2.0
"""B3 Product & Maturity — 130 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import ProductCfg

_STAGE_SCORES = {
    "idea": 1.0, "mvp": 3.0, "beta": 5.0,
    "prod": 7.0, "scale": 9.0, "enterprise": 10.0,
}


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def score_b3(cfg: ProductCfg) -> BlockResult:
    stage_score = _STAGE_SCORES.get(cfg.stage.lower(), 5.0)

    # Automation depth %: 0=0, 25=3, 50=5, 75=7, 100=10
    auto = cfg.automation_depth_pct
    auto_score = _clamp(auto / 10.0)

    # Integrations: 0=0, 1=2, 3=5, 5=7, 10+=10
    n_int = cfg.integrations_count
    if n_int == 0: int_score = 0.0
    elif n_int < 3: int_score = _clamp(n_int / 3 * 4)
    elif n_int < 5: int_score = _clamp(4 + (n_int - 3) / 2 * 2)
    elif n_int < 10: int_score = _clamp(6 + (n_int - 5) / 5 * 3)
    else: int_score = 10.0

    doc_score = 10.0 if cfg.has_docs else 0.0
    roadmap_score = 10.0 if cfg.has_roadmap else 0.0

    # UX NPS: <0=0, 0-50=5, 50-70=7, 70+=10
    nps = cfg.ux_nps
    if nps < 0: ux_score = 0.0
    elif nps < 50: ux_score = _clamp(nps / 50 * 5)
    elif nps < 70: ux_score = _clamp(5 + (nps - 50) / 20 * 2)
    else: ux_score = 10.0

    # Active modules: 0=0, 1=2, 3=5, 7=7, 10+=10
    mods = cfg.active_modules
    if mods == 0: mod_score = 0.0
    elif mods < 3: mod_score = _clamp(mods / 3 * 4)
    elif mods < 7: mod_score = _clamp(4 + (mods - 3) / 4 * 3)
    elif mods < 10: mod_score = _clamp(7 + (mods - 7) / 3 * 2)
    else: mod_score = 10.0

    metrics = [
        MetricResult(id="B3_Product_Stage", block="B3", name="Product Stage", weight=30,
                     score=stage_score, source="manual", rationale=f"Stage={cfg.stage}"),
        MetricResult(id="B3_Automation_Depth", block="B3", name="Automation Depth", weight=25,
                     raw_value=auto, score=auto_score, source="manual",
                     rationale=f"Automation={auto}% of client processes"),
        MetricResult(id="B3_Integrations", block="B3", name="Integrations", weight=20,
                     raw_value=float(n_int), score=int_score, source="manual",
                     rationale=f"Native integrations={n_int}"),
        MetricResult(id="B3_Documentation", block="B3", name="Documentation", weight=15,
                     raw_value=float(cfg.has_docs), score=doc_score, source="manual",
                     rationale="Has docs/changelog/API ref" if cfg.has_docs else "No documentation"),
        MetricResult(id="B3_Roadmap", block="B3", name="Roadmap", weight=15,
                     raw_value=float(cfg.has_roadmap), score=roadmap_score, source="manual",
                     rationale="Public roadmap present" if cfg.has_roadmap else "No public roadmap"),
        MetricResult(id="B3_UX_Maturity", block="B3", name="UX Maturity", weight=10,
                     raw_value=nps, score=ux_score, source="manual",
                     rationale=f"UX/NPS={nps}"),
        MetricResult(id="B3_Active_Modules", block="B3", name="Active Modules", weight=15,
                     raw_value=float(mods), score=mod_score, source="manual",
                     rationale=f"Active modules in prod={mods}"),
    ]
    block_score = sum(m.score * m.weight for m in metrics) / 10.0
    return BlockResult(code="B3", name="Product & Maturity", weight=130,
                       metrics=metrics, block_score=block_score)
