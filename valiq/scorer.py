# SPDX-License-Identifier: Apache-2.0
"""Scorer orchestrator: runs all 9 block scorers, enforces ATI gate."""
from __future__ import annotations
from valiq.config import ValIQConfig
from valiq.models import Assessment, BlockResult
from valiq.blocks.b1_financial import score_b1
from valiq.blocks.b2_data import score_b2
from valiq.blocks.b3_product import score_b3
from valiq.blocks.b4_tech import score_b4
from valiq.blocks.b5_clients import score_b5
from valiq.blocks.b6_compliance import score_b6, ATIRequiredError
from valiq.blocks.b7_market import score_b7
from valiq.blocks.b8_team import score_b8
from valiq.blocks.b9_ip import score_b9
from valiq.connectors.ati import get_ati_score


def run_assessment(cfg: ValIQConfig, only: str | None = None) -> Assessment:
    """
    Run all block scorers and return an Assessment.
    If ATI score is unavailable, blocks B1-B5,B7-B9 are scored but
    B6 is skipped and ati_status="ati_required" (no valuation is produced).
    """
    # Resolve ATI score
    ati_score = get_ati_score(cfg.ati, cfg.compliance)

    blocks: list[BlockResult] = []
    ati_status = "ok"

    scorer_map = {
        "B1": lambda: score_b1(cfg.financial),
        "B2": lambda: score_b2(cfg.data),
        "B3": lambda: score_b3(cfg.product),
        "B4": lambda: score_b4(cfg.tech),
        "B5": lambda: score_b5(cfg.clients),
        "B7": lambda: score_b7(cfg.market),
        "B8": lambda: score_b8(cfg.team),
        "B9": lambda: score_b9(cfg.ip),
    }

    for code, fn in scorer_map.items():
        if only and code != only:
            continue
        blocks.append(fn())

    # B6 requires ATI
    if not only or only == "B6":
        try:
            b6 = score_b6(cfg.compliance, ati_score=ati_score)
            blocks.append(b6)
        except ATIRequiredError:
            ati_status = "ati_required"
            # Create a zero-scored B6 placeholder
            from valiq.models import MetricResult
            placeholder_metrics = [
                MetricResult(id="B6_ATI", block="B6", name="AI Trust Index", weight=40,
                             score=0.0, source="ati",
                             rationale="ATI score required — visit bizdnai.com/index/"),
                MetricResult(id="B6_G12_Scan", block="B6", name="G12 Scan", weight=20,
                             score=0.0, source="ati", rationale="Pending ATI"),
                MetricResult(id="B6_KZ_Law_230", block="B6", name="KZ Law 230-VIII", weight=15,
                             score=0.0, source="manual", rationale="Pending ATI"),
                MetricResult(id="B6_Privacy_Policy", block="B6", name="Privacy Policy", weight=10,
                             score=0.0, source="manual", rationale="Pending ATI"),
                MetricResult(id="B6_Pentest", block="B6", name="Security Audit", weight=15,
                             score=0.0, source="manual", rationale="Pending ATI"),
            ]
            blocks.append(BlockResult(
                code="B6", name="Trust & Compliance (BLOCKED)", weight=100,
                metrics=placeholder_metrics, block_score=0.0, active=False
            ))

    # Sort blocks by code
    blocks.sort(key=lambda b: b.code)

    total_score = sum(b.block_score for b in blocks)

    return Assessment(
        project_name=cfg.project.name,
        total_score=total_score,
        blocks=blocks,
        ati_status=ati_status,
        ati_score=ati_score,
        partial=(ati_status == "ati_required"),
    )
