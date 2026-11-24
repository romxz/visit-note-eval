#!/usr/bin/env bash
# Final round: v3 on the tuning cases, then v1 vs v3 on the held-out cases (never used for tuning),
# then the same on OpenAI and Claude if their keys are set.
# Usage: ./run_final.sh [lmstudio-model-id] [extra flags for the LM Studio runs, e.g. --no-think]
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:src"
if command -v uv >/dev/null 2>&1; then PY=(uv run python); else PY=(command python); fi
python() { "${PY[@]}" "$@"; }

LM_ARGS=()
if [[ $# -ge 1 ]]; then LM_ARGS=(--model "$1"); shift; LM_ARGS+=("$@"); fi
OUT="results/$(date +%Y%m%d-%H%M)-final"
HELD=data/heldout.json
mkdir -p "$OUT"

run() {  # run <provider> <prompt> <set: main|heldout> <name> [extra args...]
  local provider=$1 prompt=$2 set=$3 name=$4; shift 4
  local cases=(); [[ $set == heldout ]] && cases=(--cases "$HELD")
  echo "== $name"
  python -m notevals run --provider "$provider" --prompt "$prompt" --mode native "${cases[@]}" --name "$name" --out "$OUT" "$@"
}
cmp() { python -m notevals compare "$OUT/$1" "$OUT/$2" --save "$OUT/compare-$3.md" > /dev/null; }

run lmstudio v3 main    lm-v3-main      "${LM_ARGS[@]}"
run lmstudio v1 heldout lm-v1-heldout   "${LM_ARGS[@]}"
run lmstudio v3 heldout lm-v3-heldout   "${LM_ARGS[@]}"
cmp lm-v1-heldout lm-v3-heldout lm-heldout-v1-vs-v3

if [[ -n "${OPENAI_API_KEY:-}" && -n "${OPENAI_MODEL:-}" ]]; then
  run openai v3 main    openai-v3-main
  run openai v3 heldout openai-v3-heldout
  cmp lm-v3-main openai-v3-main lm-vs-openai-main
else
  echo "(skipping OpenAI: set OPENAI_API_KEY and OPENAI_MODEL)"
fi
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  run anthropic v3 main    claude-v3-main
  run anthropic v3 heldout claude-v3-heldout
  cmp lm-v3-main claude-v3-main lm-vs-claude-main
else
  echo "(skipping Claude: set ANTHROPIC_API_KEY)"
fi

echo
echo "Done. Reports and comparisons in $OUT"
