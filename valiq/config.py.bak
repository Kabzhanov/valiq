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
    mrr: float = 0.0
    arr: float = 0.0
    growth_mom_pct: float = 0.0
    churn_pct: float = 0.0
    arpu: float = 0.0
    gross_margin_pct: float = 0.0
    burn_runway_months: float = 0.0


@dataclass
class DataCfg:
    data_volume_tb: float = 0.0
    history_depth_years: float = 0.0
    data_rights: float = 5.0       # 0-10
    reproducibility: float = 5.0   # 0-10 (10=hardest to copy)
    training_datasets: bool = False
    knowledge_graph: bool = False


@dataclass
class ProductCfg:
    stage: str = "mvp"             # idea|mvp|beta|prod|scale|enterprise
    automation_depth_pct: float = 0.0
    integrations_count: int = 0
    has_docs: bool = False
    has_roadmap: bool = False
    ux_nps: float = 0.0
    active_modules: int = 0


@dataclass
class TechCfg:
    provider: str = "manual"
    repo: str = ""
    token_env: str = ""
    test_coverage_pct: float = 0.0
    tech_debt_score: float = 5.0   # 0-10 (10=no debt)
    mttr_hours: float = 24.0
    time_to_deploy_hours: float = 4.0
    architecture_score: float = 5.0  # 0-10 (LLM judge)
    uptime_pct: float = 99.0
    code_docs_pct: float = 50.0


@dataclass
class ClientsCfg:
    provider: str = "manual"
    api_key_env: str = ""
    active_clients: int = 0
    ltv_cac_ratio: float = 0.0
    nps: float = 0.0
    client_churn_pct: float = 0.0
    top_client_revenue_pct: float = 100.0
    enterprise_contracts: int = 0


@dataclass
class ComplianceCfg:
    g12_scan_passed: bool = False
    kz_law_checklist_pct: float = 0.0  # 0-100
    has_privacy_policy: bool = False
    pentest_done: bool = False
    # ati_score is fetched dynamically via connectors/ati.py
    ati_score_manual: Optional[float] = None  # fallback if no live ATI


@dataclass
class MarketCfg:
    tam_usd_bn: float = 0.0
    som_arr_ratio: float = 0.0     # SOM/ARR
    moat_score: float = 5.0        # 0-10 (LLM judge)
    entry_barriers: float = 5.0    # 0-10
    market_growth_pct: float = 0.0


@dataclass
class TeamCfg:
    bus_factor: int = 1
    dev_processes_score: float = 5.0  # 0-10
    key_developers: int = 0
    ceo_dependency: bool = True


@dataclass
class IpCfg:
    brand_registered: bool = False
    patents_count: int = 0
    proprietary_algorithms: bool = False
    code_copyright: bool = False


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
