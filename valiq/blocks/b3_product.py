# SPDX-License-Identifier: Apache-2.0
"""B3 Product & Maturity — 130 points."""
from __future__ import annotations
from valiq.models import MetricResult, BlockResult
from valiq.config import ProductCfg
from valiq.blocks import rescale_block_score

_STAGE_SCORES = {
    "idea": 1.0, "mvp": 3.0, "beta": 5.0,
    "prod": 7.0, "scale": 9.0, "enterprise": 10.0,
}


def _clamp(v: float) -> float:
    return max(0.0, min(10.0, v))


def _absent(id: str, name: str, weight: int) -> MetricResult:
    return MetricResult(id=id, block="B3", name=name, weight=weight,
                        raw_value=None, score=0.0, source="manual",
                        rationale="no data", present=False)


def score_b3(cfg: ProductCfg) -> BlockResult:
    metrics: list[MetricResult] = []

    # Product Stage (str)
    if cfg.stage is None:
        metrics.append(_absent("B3_Product_Stage", "Product Stage", 30))
    else:
        stage_score = _STAGE_SCORES.get(cfg.stage.lower(), 5.0)
        metrics.append(MetricResult(id="B3_Product_Stage", block="B3", name="Product Stage", weight=30,
                                    score=stage_score, source="manual",
                                    rationale=f"Stage={cfg.stage}", present=True))

    # Automation depth %
    auto = cfg.automation_depth_pct
    if auto is None:
        metrics.append(_absent("B3_Automation_Depth", "Automation Depth", 25))
    else:
        metrics.append(MetricResult(id="B3_Automation_Depth", block="B3", name="Automation Depth", weight=25,
                                    raw_value=auto, score=_clamp(auto / 10.0), source="manual",
                                    rationale=f"Automation={auto}% of client processes", present=True))

    # Integrations count
    n_int = cfg.integrations_count
    if n_int is None:
        metrics.append(_absent("B3_Integrations", "Integrations", 20))
    else:
        if n_int == 0: int_s = 0.0
        elif n_int < 3: int_s = _clamp(n_int / 3 * 4)
        elif n_int < 5: int_s = _clamp(4 + (n_int - 3) / 2 * 2)
        elif n_int < 10: int_s = _clamp(6 + (n_int - 5) / 5 * 3)
        else: int_s = 10.0
        metrics.append(MetricResult(id="B3_Integrations", block="B3", name="Integrations", weight=20,
                                    raw_value=float(n_int), score=int_s, source="manual",
                                    rationale=f"Native integrations={n_int}", present=True))

    # Has docs (bool)
    if cfg.has_docs is None:
        metrics.append(_absent("B3_Documentation", "Documentation", 15))
    else:
        metrics.append(MetricResult(id="B3_Documentation", block="B3", name="Documentation", weight=15,
                                    raw_value=float(cfg.has_docs), score=10.0 if cfg.has_docs else 0.0,
                                    source="manual",
                                    rationale="Has docs/changelog/API ref" if cfg.has_docs else "No documentation",
                                    present=True))

    # Has roadmap (bool)
    if cfg.has_roadmap is None:
        metrics.append(_absent("B3_Roadmap", "Roadmap", 15))
    else:
        metrics.append(MetricResult(id="B3_Roadmap", block="B3", name="Roadmap", weight=15,
                                    raw_value=float(cfg.has_roadmap), score=10.0 if cfg.has_roadmap else 0.0,
                                    source="manual",
                                    rationale="Public roadmap present" if cfg.has_roadmap else "No public roadmap",
                                    present=True))

    # UX NPS
    nps = cfg.ux_nps
    if nps is None:
        metrics.append(_absent("B3_UX_Maturity", "UX Maturity", 10))
    else:
        if nps < 0: ux_s = 0.0
        elif nps < 50: ux_s = _clamp(nps / 50 * 5)
        elif nps < 70: ux_s = _clamp(5 + (nps - 50) / 20 * 2)
        else: ux_s = 10.0
        metrics.append(MetricResult(id="B3_UX_Maturity", block="B3", name="UX Maturity", weight=10,
                                    raw_value=nps, score=ux_s, source="manual",
                                    rationale=f"UX/NPS={nps}", present=True))

    # Active modules
    mods = cfg.active_modules
    if mods is None:
        metrics.append(_absent("B3_Active_Modules", "Active Modules", 15))
    else:
        if mods == 0: mod_s = 0.0
        elif mods < 3: mod_s = _clamp(mods / 3 * 4)
        elif mods < 7: mod_s = _clamp(4 + (mods - 3) / 4 * 3)
        elif mods < 10: mod_s = _clamp(7 + (mods - 7) / 3 * 2)
        else: mod_s = 10.0
        metrics.append(MetricResult(id="B3_Active_Modules", block="B3", name="Active Modules", weight=15,
                                    raw_value=float(mods), score=mod_s, source="manual",
                                    rationale=f"Active modules in prod={mods}", present=True))

    return BlockResult(code="B3", name="Product & Maturity", weight=130,
                       metrics=metrics, block_score=rescale_block_score(metrics, 130),
                       no_data=not any(m.present for m in metrics))
