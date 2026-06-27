# SPDX-License-Identifier: Apache-2.0
"""BYOK LLM judge for subjective metrics (architecture, moat, automation depth).
API key from env ONLY — never written to disk or included in payloads."""
from __future__ import annotations
import os
from typing import Optional


class LLMJudge:
    """LLM judge for subjective metric scoring. BYOK — key from env."""
    def __init__(self, provider: str = "", model: str = "", api_key_env: str = ""):
        self.provider = provider
        self.model = model
        self.api_key_env = api_key_env

    def _key(self) -> str:
        return os.environ.get(self.api_key_env, "") if self.api_key_env else ""

    def _available(self) -> bool:
        return bool(self.provider and self.model and self._key())

    def score_metric(self, metric_name: str, description: str,
                     context: dict | None = None) -> Optional[float]:
        """Ask LLM to score a subjective metric 0-10. Returns None if unavailable."""
        if not self._available():
            return None
        prompt = (
            f"You are an expert IT/AI product evaluator. Score the following metric from 0 to 10.\n"
            f"Metric: {metric_name}\n"
            f"Description: {description}\n"
            f"Context: {context or {}}\n\n"
            f"Respond with ONLY a single number between 0 and 10 (can be decimal)."
        )
        try:
            return self._call(prompt)
        except Exception:
            return None

    def _call(self, prompt: str) -> Optional[float]:
        key = self._key()
        if self.provider == "openai":
            import httpx
            resp = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json={"model": self.model, "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 10},
                timeout=30,
            )
            text = resp.json()["choices"][0]["message"]["content"].strip()
        elif self.provider == "anthropic":
            import httpx
            resp = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
                json={"model": self.model, "max_tokens": 10,
                      "messages": [{"role": "user", "content": prompt}]},
                timeout=30,
            )
            text = resp.json()["content"][0]["text"].strip()
        elif self.provider == "http":
            import httpx
            resp = httpx.post(
                self.model,  # model field holds URL for http provider
                json={"prompt": prompt, "max_tokens": 10},
                timeout=30,
            )
            text = str(resp.json().get("text", "")).strip()
        else:
            return None
        # Parse float from response
        import re
        m = re.search(r"\d+(?:\.\d+)?", text)
        if m:
            return max(0.0, min(10.0, float(m.group())))
        return None


def make_judge(llm_cfg) -> LLMJudge:
    return LLMJudge(
        provider=getattr(llm_cfg, "provider", ""),
        model=getattr(llm_cfg, "model", ""),
        api_key_env=getattr(llm_cfg, "api_key_env", ""),
    )
