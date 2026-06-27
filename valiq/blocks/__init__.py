# SPDX-License-Identifier: Apache-2.0
"""Shared helpers for block scorers."""
from __future__ import annotations
from valiq.models import MetricResult


def rescale_block_score(metrics: list[MetricResult], block_weight: int) -> float:
    """Compute block score rescaled over present metrics only.

    Formula: Σ(score×weight, present) / Σ(weight, present) / 10 × block_weight

    When all metrics present: identical to sum(m.score*m.weight for m in metrics)/10.
    When zero present: returns 0.0.
    """
    present = [m for m in metrics if m.present]
    if not present:
        return 0.0
    w_sum = sum(m.weight for m in present)
    return sum(m.score * m.weight for m in present) / w_sum / 10.0 * block_weight
