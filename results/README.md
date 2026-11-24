# Results

All runs: `qwen/qwen3-14b` in LM Studio, `--no-think`, temperature 0. Each run folder has `report.md` (start here), `summary.json`, `cases.jsonl` (raw model output, parsed note and scores per case) and `meta.json` (settings). `compare-*.md` files compare two runs. See [FINDINGS.md](../FINDINGS.md) for what they mean.

| Folder | What it is |
|---|---|
| `1-first-round/` | The first matrix. Kept as found, because it contains the design flaw behind finding 1: in this version, `native` mode did **not** put the schema in the prompt, so `lm-v1-native` here is what later became `native-bare`. Scored with the first version of the scorer and answer keys. |
| `2-after-fixes/` | The same matrix after fixing the setup (schema in the prompt for `native`, `native-bare` added as a variant), the scorer (number words, misnamed drugs) and the note format (main complaint in symptoms, follow-up windows). |
| `3-repeat/` | `2-after-fixes` run again unchanged. Same scores: results are reproducible at temperature 0. |
| `4-final/` | Prompt v3 on the tuning cases, and v1 vs v3 on the held-out cases. The held-out runs were re-scored after one answer-key fix (H1), disclosed in FINDINGS. |
