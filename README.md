# ValIQ — IT/AI Product Index (ITAI Score)

> Open-source, client-side CLI that scores the **market value & maturity** of an IT/AI product
> on a **0–1000** scale across **9 blocks / 51 metrics**, then converts the score into a
> **USD valuation range**.

ValIQ answers **"how much is this product worth, and why?"** — the valuation companion to the
[AI Trust Index (ATI)](https://github.com/Kabzhanov/ati-audit), which answers *"can it be trusted?"*.
The two indexes are a matched pair: **trustworthy AND valuable** is the strongest position for
raising investment and winning enterprise clients.

| | ATI (`ati-audit`) | **ValIQ (`valiq`)** |
|---|---|---|
| Question | "Can I trust this product?" | "How much is it worth?" |
| Scale | 0–10 | 0–1000 → **USD range** |
| Units | 12 directions (G1–G12) | 9 blocks × 51 metrics |
| Result | trust score + green shield | maturity score + **valuation range** |
| Badge | `bizdnai.com/index/` | `bizdnai.com/valiq/` |

**ValIQ consumes ATI** — Block 6 (Compliance, 100 pts) takes 40 points directly from your ATI
score (`ATI × 4`). No ATI score → ValIQ refuses to produce a final valuation and directs you to
run ATI first (the **ATI gate**, see below).

---

## Principles

- **Privacy-first / client-side.** Your raw financials, source code, and customer PII never leave
  your machine. Only computed scores (optionally) go to a registry.
- **Manual-input-first.** Every metric can be supplied via `valiq.yaml`. Connectors
  (Stripe / GitHub / amoCRM / ATI) are optional and degrade gracefully — no token, no problem.
- **BYOK LLM judge.** Subjective metrics (architecture, moat, automation depth) can be scored by
  your own LLM. The API key is read from an environment variable only — never written to disk,
  never included in any payload.
- **Append-only & signed.** Each run is a fresh assessment; submitted payloads carry a SHA-256
  fingerprint for tamper-evidence.

---

## Install

```bash
git clone https://github.com/Kabzhanov/valiq.git
cd valiq
pip install -e .
```

Requires Python 3.11+.

## Quickstart

```bash
# 1. Generate a starter config
valiq init                       # writes valiq.yaml

# 2. Edit valiq.yaml with your numbers (or use the bundled example)

# 3. Score it (local-only, all metrics from YAML)
valiq run --self -c examples/valiq.yaml --out report.html

# 4. Print the USD valuation range
valiq estimate -c examples/valiq.yaml
```

Score just one block:

```bash
valiq run --only B1 -c examples/valiq.yaml      # Financial block only
```

Compare two assessments:

```bash
valiq compare a.json b.json
```

Submit scores only (no raw data) to a registry:

```bash
valiq submit -c examples/valiq.yaml --registry https://bizdnai.com/api/valiq/submit
```

---

## The 9 blocks (1000 points)

| # | Block | Weight | Source |
|---|-------|-------:|--------|
| B1 | Financial Value | 220 | payment APIs, P&L, bank |
| B2 | Data & Data Moat | 150 | DB schema, volume, rights, LLM |
| B3 | Product & Maturity | 130 | YAML, GitHub Projects, docs, NPS |
| B4 | Technology | 120 | GitHub/GitLab CI, SonarQube, Prometheus |
| B5 | Client Base | 120 | CRM (amoCRM/Bitrix24), surveys |
| B6 | **Trust & Compliance** | 100 | **ATI API, G12 scan, KZ checklist** |
| B7 | Market & Competition | 80 | YAML, TAM/SAM/SOM, LLM |
| B8 | Team | 50 | LinkedIn, GitHub, YAML |
| B9 | Intellectual Property | 30 | patents, brand, registries |

Each metric is normalised to 0–10, multiplied by its weight, and summed; the block total is
`Σ(score × weight) / 10`. The 51-metric breakdown lives in `valiq/blocks/`.

## The ATI gate (hard invariant)

Block 6 **requires** an ATI score. If none is available (no `ati.score` in YAML and no live ATI
cabinet), ValIQ:

1. still computes blocks B1–B5 and B7–B9,
2. marks the assessment `ati_status: "ati_required"`,
3. **refuses to produce a USD valuation**, and
4. points you to <https://bizdnai.com/index/> to obtain your ATI score first.

ValIQ is **step 2** — get trustworthy (ATI), then get valued (ValIQ).

## Valuation formula

```
Valuation = ARR × Base_Multiple × ITAI_Multiplier × Stage_Multiplier
```

| Factor | Driver | Values |
|--------|--------|--------|
| Base_Multiple | MoM growth | <5% → 4× · 5–15% → 7× · >15% → 15× |
| ITAI_Multiplier | total score | 0–400 → 0.5× … 950+ → 2.0× |
| Stage_Multiplier | MRR | pre-revenue → 0.2× … >$200K → 2.0× |

The output is a **±20% range**, e.g. `$0.92M – $1.38M`.

---

## License

Apache-2.0 — see [LICENSE](LICENSE).

Standard author: Rashid Kabzhanov, CEO & Co-Founder, BizDNAi.com.
Public registry: <https://bizdnai.com/valiq/> · Repo: `Kabzhanov/valiq`.
