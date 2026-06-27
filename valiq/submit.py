# SPDX-License-Identifier: Apache-2.0
"""Submit ValIQ scores to a registry endpoint (scores only, no raw data)."""
import json
import hashlib
from valiq.pii import redact

try:
    import httpx as _httpx
    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False


def build_payload(assessment: dict) -> dict:
    """Build submit payload: scores + redacted rationale only."""
    blocks = [
        {
            "code": b["code"],
            "block_score": b["block_score"],
            "weight": b["weight"],
            "metrics": [
                {
                    "id": m["id"],
                    "score": m["score"],
                    "weight": m["weight"],
                    "rationale_redacted": redact(m.get("rationale", "")),
                }
                for m in b.get("metrics", [])
            ],
        }
        for b in assessment.get("blocks", [])
    ]
    payload = {
        "total_score": assessment.get("total_score"),
        "ati_status": assessment.get("ati_status"),
        "ati_score": assessment.get("ati_score"),
        "blocks": blocks,
        "project_meta": {
            "name": assessment.get("project_name", ""),
        },
        "signature": None,
    }
    return payload


def sign_sha256(payload: dict) -> str:
    """SHA-256 fingerprint of the payload (sorted keys, no signature field)."""
    signing_input = {k: v for k, v in payload.items() if k != "signature"}
    return hashlib.sha256(
        json.dumps(signing_input, sort_keys=True).encode()
    ).hexdigest()


def _default_post(url: str, json_data: dict) -> dict:
    if not _HAS_HTTPX:
        raise RuntimeError("httpx not installed; run: pip install httpx")
    try:
        return _httpx.post(url, json=json_data, timeout=60).json()
    except Exception as e:
        return {"error": str(e)}


def submit(payload: dict, registry_url: str, _post=_default_post) -> dict:
    return _post(registry_url, payload)
