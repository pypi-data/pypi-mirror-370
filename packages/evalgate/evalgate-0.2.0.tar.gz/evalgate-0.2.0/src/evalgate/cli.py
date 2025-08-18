
from __future__ import annotations
import os, json, pathlib, sys, yaml
import typer
from pydantic import ValidationError
from rich import print as rprint
from .config import Config
from .util import list_paths, read_json, write_json
from .evaluators import json_schema as ev_schema
from .evaluators import category_match as ev_cat
from .evaluators import latency_cost as ev_budget
from .evaluators import llm_judge as ev_llm
from .store import load_baseline
from .report import render_markdown
from .templates import (
    load_default_config,
    load_schema_example, 
    load_fixture_example,
    load_quality_judge_prompt,
    load_sentiment_judge_prompt
)

app = typer.Typer(no_args_is_help=True)

@app.command()
def init(path: str = "."):
    """Drop example config/fixtures/schemas."""
    root = pathlib.Path(path)
    (root / ".github").mkdir(parents=True, exist_ok=True)
    (root / "eval" / "fixtures").mkdir(parents=True, exist_ok=True)
    (root / "eval" / "schemas").mkdir(parents=True, exist_ok=True)
    (root / "eval" / "prompts").mkdir(parents=True, exist_ok=True)
    (root / ".evalgate" / "outputs").mkdir(parents=True, exist_ok=True)
    (root / ".github" / "evalgate.yml").write_text(load_default_config(), encoding="utf-8")
    (root / "eval" / "schemas" / "queue_item.json").write_text(
        json.dumps(load_schema_example(), indent=2), encoding="utf-8")
    (root / "eval" / "fixtures" / "cx_001.json").write_text(
        json.dumps(load_fixture_example(), indent=2), encoding="utf-8")
    
    # Create example LLM prompt templates
    (root / "eval" / "prompts" / "quality_judge.txt").write_text(
        load_quality_judge_prompt(), encoding="utf-8")
    
    (root / "eval" / "prompts" / "sentiment_judge.txt").write_text(
        load_sentiment_judge_prompt(), encoding="utf-8")
    rprint("[green]Initialized example EvalGate files.[/green]")

@app.command()
def run(config: str = typer.Option(..., help="Path to evalgate YAML"),
        output: str = typer.Option(".evalgate/results.json", help="Where to write results JSON")):
    """Run evals and write a results artifact."""
    try:
        cfg = Config.model_validate(yaml.safe_load(pathlib.Path(config).read_text(encoding="utf-8")))
    except ValidationError as e:
        rprint("[red]Invalid config:[/red]", e)
        raise typer.Exit(2)

    fixture_paths = list_paths(cfg.fixtures.path)
    output_paths = list_paths(cfg.outputs.path)
    fixtures = {pathlib.Path(p).stem: read_json(p) for p in fixture_paths}
    outputs  = {pathlib.Path(p).stem: read_json(p) for p in output_paths}

    names = sorted(set(fixtures.keys()) & set(outputs.keys()))
    f_map = {n: fixtures[n] for n in names}
    o_map = {n: outputs[n] for n in names}

    scores = []
    failures = []
    evaluator_errors = []  # Track configuration/runtime errors separately
    latency = cost = None

    for ev in cfg.evaluators:
        if not ev.enabled: continue
        
        # Check for missing required fields upfront
        if ev.type == "llm":
            if not ev.prompt_path:
                evaluator_errors.append(f"Evaluator '{ev.name}' missing required field: prompt_path")
                continue
            if not ev.provider:
                evaluator_errors.append(f"Evaluator '{ev.name}' missing required field: provider")
                continue
            if not ev.model:
                evaluator_errors.append(f"Evaluator '{ev.name}' missing required field: model")
                continue
        
        if ev.type == "schema":
            schema = read_json(ev.schema_path) if ev.schema_path else {}
            s, v = ev_schema.evaluate(o_map, schema)
        elif ev.type == "category":
            s, v = ev_cat.evaluate(o_map, f_map, ev.expected_field or "")
        elif ev.type == "budgets":
            s, v, latency, cost = ev_budget.evaluate(f_map, {
                "p95_latency_ms": cfg.budgets.p95_latency_ms,
                "max_cost_usd_per_item": cfg.budgets.max_cost_usd_per_item
            })
        elif ev.type == "llm":
            # Required field validation already done above
            try:
                s, v = ev_llm.evaluate(
                    outputs=o_map,
                    fixtures=f_map,
                    provider=ev.provider,
                    model=ev.model,
                    prompt_path=ev.prompt_path,
                    api_key_env_var=ev.api_key_env_var,
                    base_url=ev.base_url,
                    temperature=ev.temperature or 0.1,
                    max_tokens=ev.max_tokens or 1000
                )
            except Exception as e:
                rprint(f"[red]LLM evaluator {ev.name} failed: {e}[/red]")
                # Track this as an evaluator error, not just a low score
                evaluator_errors.append(f"Evaluator '{ev.name}' failed to run: {str(e)}")
                # Don't add to scores - failed evaluators shouldn't contribute to scoring
                continue
        else:
            rprint(f"[yellow]Unknown evaluator type: {ev.type}[/yellow]")
            continue
        scores.append({"name": ev.name, "score": float(s), "weight": ev.weight})
        failures.extend(v)

    total_w = sum(x["weight"] for x in scores) or 1.0
    overall = sum(x["score"] * x["weight"] for x in scores) / total_w

    baseline = load_baseline(cfg.baseline.ref, cfg.report.artifact_path) or {}
    deltas = {}
    if baseline.get("scores"):
        for x in scores:
            prev = next((s["score"] for s in baseline["scores"] if s["name"] == x["name"]), None)
            if prev is not None:
                deltas[x["name"]] = x["score"] - prev

    regression_ok = True
    if deltas and not cfg.gate.allow_regression:
        regression_ok = all((d >= -1e-6) for d in deltas.values())

    # Fail the gate if any evaluators failed to run
    evaluators_ok = len(evaluator_errors) == 0
    if not evaluators_ok:
        rprint(f"[red]Gate failed: {len(evaluator_errors)} evaluator(s) failed to run[/red]")
    
    passed = overall >= cfg.gate.min_overall_score and regression_ok and evaluators_ok
    result = {
        "overall": overall,
        "scores": [{"name": x["name"], "score": x["score"], "delta": deltas.get(x["name"])} for x in scores],
        "failures": failures,
        "evaluator_errors": evaluator_errors,  # Separate from test failures
        "latency": latency,
        "cost": cost,
        "gate": {"min_overall_score": cfg.gate.min_overall_score, "allow_regression": cfg.gate.allow_regression, "passed": passed},
        "regression_ok": regression_ok,
        "evaluators_ok": evaluators_ok,
        "artifact_path": cfg.report.artifact_path,
    }

    write_json(output, result)
    if not passed:
        rprint("[red]EvalGate FAILED[/red]")
        raise typer.Exit(1)
    else:
        rprint("[green]EvalGate PASSED[/green]")

@app.command()
def report(pr: bool = typer.Option(False, "--pr", help="(future) post PR comment via API"),
           summary: bool = typer.Option(False, "--summary", help="Write to $GITHUB_STEP_SUMMARY"),
           artifact: str = typer.Option(".evalgate/results.json", help="Path to results JSON")):
    """Render a markdown summary from results."""
    data = read_json(artifact)
    md = render_markdown(data)
    if summary and "GITHUB_STEP_SUMMARY" in os.environ:
        pathlib.Path(os.environ["GITHUB_STEP_SUMMARY"]).write_text(md, encoding="utf-8")
    else:
        print(md)

def main():
    app()

if __name__ == "__main__":
    main()

