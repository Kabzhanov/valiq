# SPDX-License-Identifier: Apache-2.0
"""Base connector abstraction — mirrors ati-audit connectors/base.py."""
from __future__ import annotations
from typing import Protocol, Optional


class DataConnector(Protocol):
    """Protocol for external data connectors."""
    def fetch(self) -> dict: ...


class ManualConnector:
    """Fallback: returns empty dict (all metrics come from YAML)."""
    def fetch(self) -> dict:
        return {}


def make_connector(provider: str, **kwargs) -> DataConnector:
    """Factory: returns appropriate connector or ManualConnector if provider unknown."""
    if provider == "manual" or not provider:
        return ManualConnector()
    # Unknown providers degrade gracefully to manual
    return ManualConnector()
