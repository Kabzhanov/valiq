# SPDX-License-Identifier: Apache-2.0
"""Parse valiq.yaml configuration."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import yaml


@dataclass
class ProjectCfg:
    name: str = ""
    type: str = "saas"
    has_ai: bool = False
    country: str = ""
    site_url: str = ""


@dataclass
class FinancialCfg:
    provider: str = "manual"
    api_key_env: str = ""
    mrr: Optional[float] = None
    arr: Optional[float] = None
    growth_mom_pct: Optional[float] = None
    churn_pct: Optional[float] = None
    arpu: Optional[float] = None
    gross_margin_pct: Optional[float] = None
    burn_runway_months: Optional[float] = None


@dataclass
class DataCfg:
    data_volume_tb: Optional[float] = None
    history_depth_years: Optional[float] = None
    data_rights: Optional[float] = None       # 0-10
    reproducibility: Optional[float] = None   # 0-10 (10=hardest to copy)
    training_datasets: Optional[bool] = None
    knowledge_graph: Optional[bool] = None


@dataclass
class ProductCfg:
    stage: Optional[str] = None               # idea|mvp|beta|prod|scale|enterprise
    automation_depth_pct: Optional[float] = None
    integrations_count: Optional[int] = None
    has_docs: Optional[bool] = None
    has_roadmap: Optional[bool] = None
    ux_nps: Optional[float] = None
    active_modules: Optional[int] = None


@dataclass
class TechCfg:
    provider: str = "manual"
    repo: str = ""
    token_env: str = ""
    test_coverage_pct: Optional[float] = None
    tech_debt_score: Optional[float] = None   # 0-10 (10=no debt)
    mttr_hours: Optional[float] = None
    time_to_deploy_hours: Optional[float] = None
    architecture_score: Optional[float] = None  # 0-10 (LLM judge)
    uptime_pct: Optional[float] = None
    code_docs_pct: Optional[float] = None


@dataclass
class ClientsCfg:
    provider: str = "manual"
    api_key_env: str = ""
    active_clients: Optional[int] = None
    ltv_cac_ratio: Optional[float] = None
    nps: Optional[float] = None
    client_churn_pct: Optional[float] = None
    top_client_revenue_pct: Optional[float] = None
    enterprise_contracts: Optional[int] = None


@dataclass
class ComplianceCfg:
    g12_scan_passed: Optional[bool] = None
    kz_law_checklist_pct: Optional[float] = None  # 0-100
    has_privacy_policy: Optional[bool] = None
    pentest_done: Optional[bool] = None
    # ati_score is fetched dynamically via connectors/ati.py
    ati_score_manual: Optional[float] = None  # fallback if no live ATI


@dataclass
class MarketCfg:
    tam_usd_bn: Optional[float] = None
    som_arr_ratio: Optional[float] = None     # SOM/ARR
    moat_score: Optional[float] = None        # 0-10 (LLM judge)
    entry_barriers: Optional[float] = None    # 0-10
    market_growth_pct: Optional[float] = None


@dataclass
class TeamCfg:
    bus_factor: Optional[int] = None
    dev_processes_score: Optional[float] = None  # 0-10
    key_developers: Optional[int] = None
    ceo_dependency: Optional[bool] = None


@dataclass
class IpCfg:
    brand_registered: Optional[bool] = None
    patents_count: Optional[int] = None
    proprietary_algorithms: Optional[bool] = None
    code_copyright: Optional[bool] = None


@dataclass
class LLMCfg:
    provider: str = ""
    model: str = ""
    api_key_env: str = ""


@dataclass
class AtiCfg:
    site_url: str = ""
    source: str = "manual"   # "cabinet" | "manual"
    score: Optional[float] = None


@dataclass
class SubmitCfg:
    registry_url: str = ""


@dataclass
class ValIQConfig:
    project: ProjectCfg
    financial: FinancialCfg
    data: DataCfg
    product: ProductCfg
    tech: TechCfg
    clients: ClientsCfg
    compliance: ComplianceCfg
    market: MarketCfg
    team: TeamCfg
    ip: IpCfg
    llm: LLMCfg
    ati: AtiCfg
    submit: SubmitCfg


def _dc(cls, raw: dict):
    """Construct a dataclass from raw dict, ignoring unknown keys."""
    import dataclasses
    known = {f.name for f in dataclasses.fields(cls)}
    return cls(**{k: v for k, v in raw.items() if k in known})


def load_config(path: str) -> ValIQConfig:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return ValIQConfig(
        project=_dc(ProjectCfg, raw.get("project", {})),
        financial=_dc(FinancialCfg, raw.get("financial", {})),
        data=_dc(DataCfg, raw.get("data", {})),
        product=_dc(ProductCfg, raw.get("product", {})),
        tech=_dc(TechCfg, raw.get("tech", {})),
        clients=_dc(ClientsCfg, raw.get("clients", {})),
        compliance=_dc(ComplianceCfg, raw.get("compliance", {})),
        market=_dc(MarketCfg, raw.get("market", {})),
        team=_dc(TeamCfg, raw.get("team", {})),
        ip=_dc(IpCfg, raw.get("ip", {})),
        llm=_dc(LLMCfg, raw.get("llm", {})),
        ati=_dc(AtiCfg, raw.get("ati", {})),
        submit=_dc(SubmitCfg, raw.get("submit", {})),
    )
