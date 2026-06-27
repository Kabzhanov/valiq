# SPDX-License-Identifier: Apache-2.0
"""Stripe connector — fetches financial metrics (MRR, churn, ARPU). Stub: returns empty dict if no key."""
from __future__ import annotations
import os


class StripeConnector:
    """Fetches MRR/ARR/Churn from Stripe API."""
    def __init__(self, api_key_env: str = "STRIPE_SECRET_KEY"):
        self.api_key_env = api_key_env

    def fetch(self) -> dict:
        """Returns dict with financial metric overrides, or empty dict if unavailable."""
        key = os.environ.get(self.api_key_env, "")
        if not key:
            return {}
        try:
            import httpx
            headers = {"Authorization": f"Bearer {key}"}
            resp = httpx.get(
                "https://api.stripe.com/v1/balance",
                headers=headers, timeout=10
            )
            if resp.status_code != 200:
                return {}
            # Real implementation would calculate MRR from subscriptions
            return {}
        except Exception:
            return {}
