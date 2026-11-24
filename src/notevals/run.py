"""Run an eval: every case through one provider/prompt/mode, scored and saved."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from .extract import extract
from .providers import MockProvider, make_provider
from .report import run_report
from .score import aggregate, score_note

ROOT = Path(__file__).resolve().parents[2]


def load_cases(path: Path, only: list[str] | None = None) -> list[dict]:
    cases = json.loads(path.read_text())
    if only:
        cases = [c for c in cases if any(c["id"].startswith(o) for o in only)]
    return cases


def slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9.]+", "-", s).strip("-").lower()


def run_eval(
    provider_name: str,
    model: str | None,
    prompt: str,
    mode: str,
    cases_path: Path,
    schema_path: Path,
    out_dir: Path,
    only: list[str] | None = None,
    temperature: float | None = 0.0,
    max_attempts: int = 2,
    run_name: str | None = None,
    quiet: bool = False,
    max_tokens: int = 2048,
    timeout: float = 180.0,
    no_think: bool = False,
) -> Path:
    provider = make_provider(provider_name, model, temperature,
                             max_tokens=max_tokens, timeout=timeout, no_think=no_think)
    schema = json.loads(schema_path.read_text())
    prompt_path = Path(prompt)
    if not prompt_path.exists():
        prompt_path = ROOT / "prompts" / f"{prompt}.md"
    system = prompt_path.read_text()
    cases = load_cases(cases_path, only)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = run_name or f"{stamp}-{provider.name}-{slug(provider.model)}-{prompt_path.stem}-{mode}"
    run_dir = out_dir / name
    run_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "run": name,
        "provider": provider.name,
        "model": provider.model,
        "prompt": prompt_path.stem,
        "mode": mode,
        "temperature": temperature,
        "max_attempts": max_attempts,
        "max_tokens": max_tokens,
        "no_think": no_think,
        "cases": len(cases),
        "started": stamp,
    }

    results = []
    if not quiet:
        print(f"{provider.name} / {provider.model} / prompt {prompt_path.stem} / mode {mode}"
              f"{' / no-think' if no_think else ''}")
    for case in cases:
        if not quiet:
            print(f"  {case['id']:<34} ...", end="\r", flush=True)
        if isinstance(provider, MockProvider):
            provider.case = case
        try:
            ex = extract(provider, system, case["transcript"], schema, mode, max_attempts)
        except Exception as e:  # timeout or API error: record it and keep going
            from .extract import Extraction
            if not quiet:
                print(f"\r  {case['id']:<34} error: {type(e).__name__}: {str(e)[:120]}")
            ex = Extraction(note=None, valid=False, attempts=1, errors=[f"{type(e).__name__}: {e}"])
        sc = score_note(ex.note, case["expected"], ex.valid)
        results.append(
            {
                "id": case["id"],
                "tags": case.get("tags", []),
                "valid": ex.valid,
                "attempts": ex.attempts,
                "schema_errors": ex.errors,
                "latency_s": round(ex.latency_s, 3),
                "usage": ex.usage,
                "note": ex.note,
                "raw": ex.raw,
                **sc,
            }
        )
        if not quiet:
            flag = "" if ex.valid else "  INVALID"
            retry = f"  (attempts: {ex.attempts})" if ex.attempts > 1 else ""
            crit = f"  critical: {len(sc['critical'])}" if sc["critical"] else ""
            print(f"  {case['id']:<34} {sc['overall']:.2f}{crit}{retry}{flag}")

    write_run(run_dir, meta, results, quiet)
    return run_dir


def summarize(results: list[dict]) -> dict:
    summary = aggregate(results)
    summary["schema_valid"] = sum(r["valid"] for r in results) / len(results) if results else None
    summary["first_try_valid"] = (
        sum(r["valid"] and r["attempts"] == 1 for r in results) / len(results) if results else None
    )
    summary["unsupported_items"] = sum(len(r["unsupported"]) for r in results)
    summary["mean_latency_s"] = (
        round(sum(r["latency_s"] for r in results) / len(results), 3) if results else None
    )
    summary["critical_errors"] = sum(len(r["critical"]) for r in results)
    return summary


def write_run(run_dir: Path, meta: dict, results: list[dict], quiet: bool = False) -> dict:
    summary = summarize(results)
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    with (run_dir / "cases.jsonl").open("w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    (run_dir / "report.md").write_text(run_report(meta, summary, results))

    if not quiet:
        print(f"\noverall {summary['overall']:.3f}  schema-valid {summary['schema_valid']:.0%}  "
              f"critical errors {summary['critical_errors']}  unsupported items {summary['unsupported_items']}")
        print(f"saved to {run_dir}")
    return summary


def rescore(run_dir: Path, cases_path: Path, quiet: bool = False) -> dict:
    """Re-score saved model outputs with the current scorer and answer keys (no model calls)."""
    meta = json.loads((run_dir / "meta.json").read_text())
    expected = {c["id"]: c["expected"] for c in json.loads(cases_path.read_text())}
    results = [json.loads(line) for line in (run_dir / "cases.jsonl").read_text().splitlines() if line]
    for r in results:
        r.update(score_note(r["note"], expected[r["id"]], r["valid"]))
        if not quiet:
            crit = f"  critical: {len(r['critical'])}" if r["critical"] else ""
            print(f"  {r['id']:<34} {r['overall']:.2f}{crit}")
    meta["rescored"] = datetime.now().strftime("%Y%m%d-%H%M%S")
    return write_run(run_dir, meta, results, quiet)
