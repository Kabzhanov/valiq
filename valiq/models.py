# SPDX-License-Identifier: Apache-2.0
"""Domain models for ValIQ assessment."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class MetricResult(BaseModel):
    id: str            # e.g. "B1_MRR"
    block: str         # "B1"
    name: str          # "MRR"
    weight: int        # 40
    raw_value: Optional[float] = None
    score: float = 0.0  # 0.0-10.0 normalised
    source: str = "manual"   # "manual"|"stripe"|"github"|"amocrm"|"ati"|"llm"
    rationale: str = ""
    present: bool = True     # False means "no data" — excluded from scoring


class BlockResult(BaseModel):
    code: str          # "B1"
    name: str          # "Financial Value"
    weight: int        # 220
    metrics: list[MetricResult]
    block_score: float   # 0.0-weight (contribution to 1000)
    active: bool = True
    no_data: bool = False  # True when ALL metrics absent


class Assessment(BaseModel):
    project_name: str
    version: str = "1.0"
    total_score: float            # 0-1000
    blocks: list[BlockResult]
    ati_status: str = "ok"        # "ok" | "ati_required"
    ati_score: Optional[float] = None  # 0-10
    partial: bool = False          # True when ATI gate blocked
    completeness_pct: float = 100.0   # % of metrics with data
    confidence: str = "high"          # "high"|"medium"|"low"


class Valuation(BaseModel):
    arr_usd: float
    growth_mom_pct: float
    base_multiple: float
    itai_multiplier: float
    stage_multiplier: float
    point_estimate: float
    low: float
    high: float
    display: str                   # "$0.92M – $1.38M"
    stage: str
    completeness_pct: float = 100.0
    confidence: str = "high"
