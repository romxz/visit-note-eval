"""Markdown reports for one run and for a comparison of two runs."""

from __future__ import annotations

import json
from pathlib import Path

from .score import FIELDS


def _fmt(v) -> str:
    return "n/a" if v is None else f"{v:.2f}"


def _pct(v) -> str:
    return "n/a" if v is None else f"{v:.0%}"


def run_report(meta: dict, summary: dict, results: list[dict]) -> str:
    lines = [
        f"# Run {meta['run']}",
        "",
        f"Provider `{meta['provider']}`, model `{meta['model']}`, prompt `{meta['prompt']}`, "
        f"mode `{meta['mode']}`, temperature {meta['temperature']}, {meta['cases']} cases.",
        "",
        f"**Overall {_fmt(summary['overall'])}** · schema-valid {_pct(summary['schema_valid'])} "
        f"(first try {_pct(summary['first_try_valid'])}) · **critical errors {summary['critical_errors']}** "
        f"· unsupported items {summary['unsupported_items']} "
        f"· mean latency {summary['mean_latency_s']}s",
        "",
        "## By field",
        "",
        "| Field | Score |",
        "|---|---|",
    ]
    lines += [f"| {f} | {_fmt(summary.get(f))} |" for f in FIELDS]
    lines += ["", "## By case", "", "| Case | Overall | Critical | Valid | Attempts | Unsupported |", "|---|---|---|---|---|---|"]
    for r in results:
        lines.append(
            f"| {r['id']} | {_fmt(r['overall'])} | {len(r['critical'])} | {'yes' if r['valid'] else 'no'} | {r['attempts']} "
            f"| {len(r['unsupported'])} |"
        )

    crit = [(r["id"], c) for r in results for c in r["critical"]]
    lines += ["", "## Critical errors", ""]
    lines += [f"- {cid}: {c}" for cid, c in crit] or ["None."]

    unsupported = [(r["id"], u) for r in results for u in r["unsupported"]]
    lines += ["", "## Unsupported items (in the note, not in the transcript's answer key)", ""]
    lines += [f"- {cid}: {u}" for cid, u in unsupported] or ["None."]

    lines += ["", "## Failures", ""]
    any_fail = False
    for r in results:
        if r["failures"]:
            any_fail = True
            lines.append(f"**{r['id']}**")
            lines += [f"- {f['field']}: {f['detail']}" for f in r["failures"]]
            if not r["valid"] and r["schema_errors"]:
                lines += [f"  - schema: {e}" for e in r["schema_errors"][:5]]
            lines.append("")
    if not any_fail:
        lines.append("None.")
    return "\n".join(lines) + "\n"


def load_run(run_dir: Path):
    meta = json.loads((run_dir / "meta.json").read_text())
    summary = json.loads((run_dir / "summary.json").read_text())
    results = [json.loads(line) for line in (run_dir / "cases.jsonl").read_text().splitlines() if line]
    return meta, summary, results


def compare_report(a_dir: Path, b_dir: Path) -> str:
    ma, sa, ra = load_run(a_dir)
    mb, sb, rb = load_run(b_dir)

    def label(m):
        return f"{m['provider']}/{m['model']} · {m['prompt']} · {m['mode']}"

    lines = [
        "# Comparison",
        "",
        f"- **A** `{ma['run']}`: {label(ma)}",
        f"- **B** `{mb['run']}`: {label(mb)}",
        "",
        "| Metric | A | B | Change |",
        "|---|---|---|---|",
    ]
    for f in ["overall", *FIELDS]:
        a, b = sa.get(f), sb.get(f)
        delta = "" if a is None or b is None else f"{b - a:+.2f}"
        lines.append(f"| {f} | {_fmt(a)} | {_fmt(b)} | {delta} |")
    lines.append(f"| schema-valid | {_pct(sa['schema_valid'])} | {_pct(sb['schema_valid'])} | |")
    lines.append(f"| first-try valid | {_pct(sa['first_try_valid'])} | {_pct(sb['first_try_valid'])} | |")
    lines.append(f"| critical errors | {sa['critical_errors']} | {sb['critical_errors']} | "
                 f"{sb['critical_errors'] - sa['critical_errors']:+d} |")
    lines.append(f"| unsupported items | {sa['unsupported_items']} | {sb['unsupported_items']} | "
                 f"{sb['unsupported_items'] - sa['unsupported_items']:+d} |")
    lines.append(f"| mean latency (s) | {sa['mean_latency_s']} | {sb['mean_latency_s']} | |")

    by_a = {r["id"]: r for r in ra}
    improved, regressed = [], []
    for r in rb:
        if r["id"] not in by_a:
            continue
        d = r["overall"] - by_a[r["id"]]["overall"]
        if d > 0.005:
            improved.append((r["id"], d))
        elif d < -0.005:
            regressed.append((r["id"], d))

    lines += ["", "## Improved cases", ""]
    lines += [f"- {cid}: {d:+.2f}" for cid, d in sorted(improved, key=lambda x: -x[1])] or ["None."]
    lines += ["", "## Regressed cases", ""]
    for cid, d in sorted(regressed, key=lambda x: x[1]):
        new_fail = {f["detail"] for f in next(r for r in rb if r["id"] == cid)["failures"]}
        old_fail = {f["detail"] for f in by_a[cid]["failures"]}
        lines.append(f"- {cid}: {d:+.2f}")
        lines += [f"  - new: {x}" for x in sorted(new_fail - old_fail)]
    if not regressed:
        lines.append("None.")
    return "\n".join(lines) + "\n"
