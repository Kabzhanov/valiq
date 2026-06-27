# SPDX-License-Identifier: Apache-2.0
"""GitHub connector — fetches tech metrics (coverage, cycle time). Stub: returns None if no token."""
from __future__ import annotations
import os
from typing import Optional


class GitHubConnector:
    """Fetches CI/test metrics from GitHub Actions API."""
    def __init__(self, repo: str, token_env: str = "GITHUB_TOKEN"):
        self.repo = repo
        self.token_env = token_env

    def _headers(self) -> dict:
        token = os.environ.get(self.token_env, "")
        return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"} if token else {}

    def fetch(self) -> dict:
        """Returns dict with tech metric overrides, or empty dict if unavailable."""
        token = os.environ.get(self.token_env, "")
        if not token or not self.repo:
            return {}
        try:
            import httpx
            url = f"https://api.github.com/repos/{self.repo}"
            resp = httpx.get(url, headers=self._headers(), timeout=10)
            if resp.status_code != 200:
                return {}
            data = resp.json()
            return {
                "open_issues": data.get("open_issues_count", 0),
                "size": data.get("size", 0),
            }
        except Exception:
            return {}
