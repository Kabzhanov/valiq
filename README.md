<p align="center">
  <h1 align="center">ValIQ — IT/AI Product Valuation Engine</h1>
  <p align="center">
    Open-source CLI that scores the <strong>market value &amp; maturity</strong> of an IT/AI product<br>
    on a <strong>0–1000</strong> scale across <strong>9 blocks / 51 metrics</strong>, then converts the score into a<br>
    <strong>USD valuation range</strong>.
  </p>
  <p align="center">
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache-2.0"></a>
    <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white" alt="Python 3.11+">
    <a href="https://github.com/Kabzhanov/valiq/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
    <a href="https://bizdnai.com/valiq/"><img src="https://img.shields.io/badge/Standard-ValIQ_Open_Standard-blueviolet" alt="ValIQ Open Standard"></a>
    <img src="https://img.shields.io/badge/Tests-passing-brightgreen" alt="Tests: passing">
  </p>
</p>

---

ValIQ answers **"how much is this product worth, and why?"** — the valuation companion to the
[AI Trust Index (ATI)](https://github.com/Kabzhanov/ati-audit), which answers *"can it be trusted?"*.
The two indexes form a matched pair: **trustworthy AND valuable** is the strongest position for
raising investment and winning enterprise clients.

| | ATI (`ati-audit`) | **ValIQ (`valiq`)** |
|---|---|---|
| Question | "Can I trust this product?" | "How much is it worth?" |
| Scale | 0–10 | 0–1000 → **USD range** |
| Units | 12 directions (G1–G12) | 9 blocks × 51 metrics |
| Result | trust score + green shield | ITAI score + **valuation range** |
| Badge | `bizdnai.com/index/` | `bizdnai.com/valiq/` |

**ValIQ consumes ATI.** Block 6 (Compliance, 100 pts) takes 40 points directly from your ATI
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

Requires **Python 3.11+**.

---

## Quickstart

```bash
# 1. Generate a starter config
valiq init                       # writes valiq.yaml

# 2. Edit valiq.yaml with your numbers (or use the bundled example)

# 3. Score your product (local-only, all metrics from YAML)
valiq run --self -c examples/valiq.yaml --out report.html

# 4. Print the USD valuation range
valiq estimate -c examples/valiq.yaml
```

**Example output** (ITAI score 696 / 1000):

```
ITAI Score : 696 / 1000
Stage       : Series-A candidate
Valuation   : $672K – $1.01M  (±20% range)
ATI status  : verified (score 7.4)
```

Score a single block:

```bash
valiq run --only B1 -c examples/valiq.yaml      # Financial block only
```

Compare two assessments:

```bash
valiq compare a.json b.json
```

Submit scores only (no raw data) to the public registry:

```bash
valiq submit -c examples/valiq.yaml --registry https://bizdnai.com/api/valiq/submit
```

---

## The 9 Blocks (1000 points)

| # | Block | Weight | Primary sources |
|---|-------|-------:|-----------------|
| B1 | Financial Value | 220 | payment APIs, P&L, bank statements |
| B2 | Data & Data Moat | 150 | DB schema, data volume, rights, LLM |
| B3 | Product & Maturity | 130 | YAML, GitHub Projects, docs, NPS |
| B4 | Technology | 120 | GitHub/GitLab CI, SonarQube, Prometheus |
| B5 | Client Base | 120 | CRM (amoCRM / Bitrix24), surveys |
| B6 | **Trust & Compliance** | 100 | **ATI API, G12 scan, KZ checklist** |
| B7 | Market & Competition | 80 | YAML, TAM/SAM/SOM, LLM |
| B8 | Team | 50 | LinkedIn, GitHub, YAML |
| B9 | Intellectual Property | 30 | patents, brand, registries |
| | **Total** | **1000** | |

Each metric is normalised to 0–10, multiplied by its weight, and summed; the block total is
`Σ(score × weight) / 10`. The full 51-metric breakdown lives in `valiq/blocks/`.

---

## The ATI Gate (hard invariant)

Block 6 **requires** an ATI score. If none is available (no `ati.score` in YAML and no live ATI
cabinet connection), ValIQ:

1. still computes blocks B1–B5 and B7–B9,
2. marks the assessment `ati_status: "ati_required"`,
3. **refuses to produce a USD valuation**, and
4. points you to <https://bizdnai.com/index/> to obtain your ATI score first.

ValIQ is **step 2** — get trustworthy (ATI), then get valued (ValIQ).

---

## Valuation Formula

```
Valuation = ARR × Base_Multiple × ITAI_Multiplier × Stage_Multiplier
```

| Factor | Driver | Example values |
|--------|--------|----------------|
| `Base_Multiple` | MoM growth | <5% → 4× · 5–15% → 7× · >15% → 15× |
| `ITAI_Multiplier` | total ITAI score | 0–400 → 0.5× · 400–650 → 0.8–1.2× · 950+ → 2.0× |
| `Stage_Multiplier` | monthly MRR | pre-revenue → 0.2× · $10K–$50K → 1.0× · >$200K → 2.0× |

The output is a **±20% range**, e.g. `$672K – $1.01M`.

---

## Project Layout

```
valiq/
├── valiq/
│   ├── blocks/          # B1–B9 metric definitions (51 metrics total)
│   ├── connectors/      # Optional data connectors: Stripe, GitHub, amoCRM, ATI
│   ├── llm/             # BYOK LLM judge for subjective metrics
│   ├── report/          # HTML report renderer
│   ├── cli.py           # CLI entry-point (valiq init / run / estimate / compare / submit)
│   ├── scorer.py        # Core scoring engine
│   ├── models.py        # Pydantic assessment models
│   └── pii.py           # PII redaction for submitted payloads
├── tests/               # pytest suite (ati_gate, scorer, valuation)
├── examples/
│   └── valiq.yaml       # Annotated starter config
└── pyproject.toml
```

---

## Contributing

PRs are welcome, especially for:

- **New connectors** — add a connector in `valiq/connectors/` (follow `base.py`)
- **Metric improvements** — edit a block in `valiq/blocks/` and update the weight table
- **New jurisdictions** — extend the B6 checklist for your country's AI/data-protection law

Before submitting, run:

```bash
pytest -q
ruff check valiq
```

---

## License & Author

Licensed under the **Apache-2.0** License — see [`LICENSE`](LICENSE).

ITAI / ValIQ standard by **Rashid Kabzhanov** — [bizdnai.com/valiq/](https://bizdnai.com/valiq/)

Sibling project: [ati-audit](https://github.com/Kabzhanov/ati-audit) — the governance & trust companion.
