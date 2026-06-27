# SPDX-License-Identifier: Apache-2.0
"""amoCRM connector — fetches client metrics. Stub: returns empty dict if no key."""
from __future__ import annotations
import os


class AmoCRMConnector:
    """Fetches active clients, NPS, LTV data from amoCRM API."""
    def __init__(self, api_key_env: str = "AMOCRM_API_KEY"):
        self.api_key_env = api_key_env

    def fetch(self) -> dict:
        """Returns dict with client metric overrides, or empty dict if unavailable."""
        key = os.environ.get(self.api_key_env, "")
        if not key:
            return {}
        # Stub: real implementation would call amoCRM REST API
        return {}
