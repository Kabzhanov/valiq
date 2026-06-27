# SPDX-License-Identifier: Apache-2.0
"""ValIQ CLI: init | run | estimate | compare | submit."""
from __future__ import annotations
import json
import os
import shutil
import sys

import click

from valiq import __version__
from valiq.config import load_config
from valiq.scorer import run_assessment
from valiq.report.valuation import compute_valuation
from valiq.report.html import to_html
from valiq.submit import build_payload, sign_sha256, submit as submit_payload

_EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")
_EXAMPLE_CONFIG = os.path.join(_EXAMPLES_DIR, "valiq.yaml")


def _assessment_to_dict(assessment) -> dict:
    return assessment.model_dump()


def _maybe_valuation(cfg, assessment):
    """Return a Valuation or None. None when ATI gate is open."""
    if assessment.ati_status == "ati_required":
        return None
    return compute_valuation(
        arr_usd=cfg.financial.arr or 0.0,
        growth_mom_pct=cfg.financial.growth_mom_pct or 0.0,
        total_score=assessment.total_score,
        mrr_usd=cfg.financial.mrr or 0.0,
        completeness_pct=assessment.completeness_pct,
    )


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="valiq")
@click.pass_context
def cli(ctx):
    """ValIQ — IT/AI Product Index (ITAI Score). Score a product 0-1000 and estimate its value."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option("-o", "--output", default="valiq.yaml", help="Destination config path.")
def init(output):
    """Generate an example valiq.yaml to edit."""
    src = os.path.abspath(_EXAMPLE_CONFIG)
    if not os.path.exists(src):
        raise click.ClickException(f"Example config not found at {src}")
    shutil.copy(src, output)
    click.echo(f"Created {output} — edit it then run: valiq run --self -c {output}")


@cli.command()
@click.option("-c", "--config", "config_path", default="valiq.yaml", help="Path to valiq.yaml.")
@click.option("--self", "self_mode", is_flag=True, help="Local-only mode (default; no live connectors).")
@click.option("--only", help="Score only this block code (e.g. B1).")
@click.option("--out", help="Write report to this file (.html or .json).")
def run(config_path, self_mode, only, out):
    """Run the full assessment (or a single block) and produce a report."""
    cfg = load_config(config_path)
    assessment = run_assessment(cfg, only=only)
    valuation = _maybe_valuation(cfg, assessment) if not only else None

    rep = _assessment_to_dict(assessment)
    if valuation is not None:
        rep["valuation"] = valuation.model_dump()

    if assessment.ati_status == "ati_required":
        click.echo(
            "Warning: ATI score required — Block 6 blocked, no valuation produced. "
            "Obtain your ATI score at https://bizdnai.com/index/ first.",
            err=True,
        )

    if out and out.endswith(".html"):
        with open(out, "w", encoding="utf-8") as f:
            f.write(to_html(assessment, valuation))
        click.echo(f"HTML report written to {out}")
    elif out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(json.dumps(rep, indent=2))
        click.echo(f"JSON report written to {out}")

    click.echo(f"ITAI Score: {assessment.total_score:.0f} / 1000  (status: {assessment.ati_status})")
    for b in assessment.blocks:
        click.echo(f"  {b.code}: {b.name:<32} {b.block_score:6.1f} / {b.weight}")
    if valuation is not None:
        click.echo(f"Estimated value: {valuation.display}")


@cli.command()
@click.option("-c", "--config", "config_path", default="valiq.yaml", help="Path to valiq.yaml.")
def estimate(config_path):
    """Print the USD valuation range (requires ATI score)."""
    cfg = load_config(config_path)
    assessment = run_assessment(cfg)
    valuation = _maybe_valuation(cfg, assessment)
    if valuation is None:
        raise click.ClickException(
            "ATI score required — cannot estimate value. "
            "Obtain your ATI score at https://bizdnai.com/index/ first."
        )
    click.echo(f"ITAI Score:   {assessment.total_score:.0f} / 1000")
    click.echo(f"ARR:          ${valuation.arr_usd:,.0f}")
    click.echo(f"Base x:       {valuation.base_multiple}x  (MoM {valuation.growth_mom_pct}%)")
    click.echo(f"ITAI x:       {valuation.itai_multiplier}x")
    click.echo(f"Stage x:      {valuation.stage_multiplier}x  ({valuation.stage})")
    click.echo(f"Point:        ${valuation.point_estimate:,.0f}")
    click.echo(f"Valuation:    {valuation.display}")


@cli.command()
@click.argument("file_a", type=click.Path(exists=True))
@click.argument("file_b", type=click.Path(exists=True))
def compare(file_a, file_b):
    """Compare two JSON assessment reports block-by-block."""
    with open(file_a, encoding="utf-8") as f:
        a = json.load(f)
    with open(file_b, encoding="utf-8") as f:
        b = json.load(f)
    click.echo(f"{'Block':<8}{'A':>10}{'B':>10}{'Delta':>10}")
    blocks_a = {x["code"]: x for x in a.get("blocks", [])}
    blocks_b = {x["code"]: x for x in b.get("blocks", [])}
    for code in sorted(set(blocks_a) | set(blocks_b)):
        sa = blocks_a.get(code, {}).get("block_score", 0.0)
        sb = blocks_b.get(code, {}).get("block_score", 0.0)
        click.echo(f"{code:<8}{sa:>10.1f}{sb:>10.1f}{sb - sa:>+10.1f}")
    ta = a.get("total_score", 0.0)
    tb = b.get("total_score", 0.0)
    click.echo(f"{'TOTAL':<8}{ta:>10.1f}{tb:>10.1f}{tb - ta:>+10.1f}")


@cli.command()
@click.option("-c", "--config", "config_path", default="valiq.yaml", help="Path to valiq.yaml.")
@click.option("--registry", required=True, help="Registry URL to POST scores to.")
def submit(config_path, registry):
    """Submit scores only (SHA-256 signed, PII-redacted) to a registry."""
    cfg = load_config(config_path)
    assessment = run_assessment(cfg)
    payload = build_payload(_assessment_to_dict(assessment))
    payload["signature"] = sign_sha256(payload)
    result = submit_payload(payload, registry)
    click.echo(f"Submit result: {result}")


def main(argv=None) -> int:
    try:
        cli.main(args=argv, prog_name="valiq", standalone_mode=False)
    except click.ClickException as exc:
        click.echo(f"valiq: error: {exc.format_message()}", err=True)
        return 1
    except Exception as exc:  # clean message instead of stack trace
        click.echo(f"valiq: error: {exc}", err=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
