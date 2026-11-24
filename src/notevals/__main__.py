"""Command line: python -m notevals run|compare ..."""

from __future__ import annotations

import argparse
from pathlib import Path

from .report import compare_report
from .run import ROOT, rescore, run_eval


def main(argv=None):
    p = argparse.ArgumentParser(prog="notevals", description="Structured visit-note extraction eval.")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run every case through one model and score it")
    r.add_argument("--provider", default="lmstudio", choices=["lmstudio", "openai", "anthropic", "mock"])
    r.add_argument("--model", help="model id (LM Studio: defaults to the first loaded model)")
    r.add_argument("--prompt", default="v2", help="prompt name in prompts/ or a path (default v2)")
    r.add_argument("--mode", default="native", choices=["native", "native-bare", "tool", "prompt"],
                   help="native = enforced JSON schema (LM Studio/OpenAI) or tool call (Claude), schema also "
                        "in the prompt; native-bare = enforcement only; tool = function calling; "
                        "prompt = no enforcement")
    r.add_argument("--cases", default=str(ROOT / "data" / "cases.json"))
    r.add_argument("--schema", default=str(ROOT / "schema" / "visit_note.schema.json"))
    r.add_argument("--only", help="comma-separated case id prefixes, e.g. 01,06")
    r.add_argument("--temperature", type=float, default=0.0)
    r.add_argument("--attempts", type=int, default=2, help="max attempts per case (validate + retry)")
    r.add_argument("--max-tokens", type=int, default=2048, help="output token cap per call")
    r.add_argument("--timeout", type=float, default=180.0, help="seconds per call before giving up")
    r.add_argument("--no-think", action="store_true",
                   help="append /no_think (turns off the reasoning section on Qwen3-style models)")
    r.add_argument("--name", help="run folder name (default: timestamp-provider-model-prompt-mode)")
    r.add_argument("--out", default=str(ROOT / "results"))

    rs = sub.add_parser("rescore", help="re-score saved runs with the current scorer and answer keys")
    rs.add_argument("runs", nargs="+")
    rs.add_argument("--cases", default=str(ROOT / "data" / "cases.json"))

    c = sub.add_parser("compare", help="compare two run folders")
    c.add_argument("a")
    c.add_argument("b")
    c.add_argument("--save", help="also write the comparison to this markdown file")

    args = p.parse_args(argv)
    if args.cmd == "run":
        run_eval(
            provider_name=args.provider,
            model=args.model,
            prompt=args.prompt,
            mode=args.mode,
            cases_path=Path(args.cases),
            schema_path=Path(args.schema),
            out_dir=Path(args.out),
            only=args.only.split(",") if args.only else None,
            temperature=args.temperature,
            max_attempts=args.attempts,
            run_name=args.name,
            max_tokens=args.max_tokens,
            timeout=args.timeout,
            no_think=args.no_think,
        )
    elif args.cmd == "rescore":
        for run in args.runs:
            print(run)
            rescore(Path(run), Path(args.cases))
    else:
        text = compare_report(Path(args.a), Path(args.b))
        print(text)
        if args.save:
            Path(args.save).write_text(text)


if __name__ == "__main__":
    main()
