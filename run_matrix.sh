#!/usr/bin/env bash
# Standard runs. LM Studio runs always; OpenAI/Claude runs only if their keys are set.
# Usage: ./run_matrix.sh [lmstudio-model-id] [extra flags for the LM Studio runs, e.g. --no-think]
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:src"
# Use uv if available, otherwise the active Python.
if command -v uv >/dev/null 2>&1; then PY=(uv run python); else PY=(command python); fi
python() { "${PY[@]}" "$@"; }

MODEL_ARGS=()
if [[ $# -ge 1 ]]; then MODEL_ARGS=(--model "$1"); shift; MODEL_ARGS+=("$@"); fi
STAMP=$(date +%Y%m%d-%H%M)
OUT="results/$STAMP"
mkdir -p "$OUT"

echo "== 1. LM Studio, v1 prompt, no enforcement"
python -m notevals run --provider lmstudio "${MODEL_ARGS[@]}" --prompt v1 --mode prompt --name lm-v1-prompt --out "$OUT"
echo "== 2. LM Studio, v1 prompt, JSON schema enforced (schema also in prompt)"
python -m notevals run --provider lmstudio "${MODEL_ARGS[@]}" --prompt v1 --mode native --name lm-v1-native --out "$OUT"
echo "== 2b. LM Studio, v1 prompt, JSON schema enforced, schema NOT in prompt"
python -m notevals run --provider lmstudio "${MODEL_ARGS[@]}" --prompt v1 --mode native-bare --name lm-v1-native-bare --out "$OUT"
echo "== 3. LM Studio, v2 prompt, JSON schema"
python -m notevals run --provider lmstudio "${MODEL_ARGS[@]}" --prompt v2 --mode native --name lm-v2-native --out "$OUT"

python -m notevals compare "$OUT/lm-v1-prompt" "$OUT/lm-v1-native" --save "$OUT/compare-enforcement.md" > /dev/null
python -m notevals compare "$OUT/lm-v1-native" "$OUT/lm-v2-native" --save "$OUT/compare-prompt.md" > /dev/null
python -m notevals compare "$OUT/lm-v1-native-bare" "$OUT/lm-v1-native" --save "$OUT/compare-schema-in-prompt.md" > /dev/null

if [[ -n "${OPENAI_API_KEY:-}" && -n "${OPENAI_MODEL:-}" ]]; then
  echo "== 4. OpenAI, v2, JSON schema"
  python -m notevals run --provider openai --prompt v2 --mode native --name openai-v2-native --out "$OUT"
  python -m notevals compare "$OUT/lm-v2-native" "$OUT/openai-v2-native" --save "$OUT/compare-lm-vs-openai.md" > /dev/null
fi
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "== 5. Claude, v2, tool call"
  python -m notevals run --provider anthropic --prompt v2 --mode native --name claude-v2-tool --out "$OUT"
  python -m notevals compare "$OUT/lm-v2-native" "$OUT/claude-v2-tool" --save "$OUT/compare-lm-vs-claude.md" > /dev/null
fi

echo
echo "Done. Reports and comparisons in $OUT"
