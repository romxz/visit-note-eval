# visit-note-eval

A small evaluation harness for one task: turning a primary-care visit transcript into a structured note (JSON), and measuring how well a model does it.

It answers questions like:

- Does forcing a JSON schema make the output more reliable than asking for JSON in the prompt?
- Did this prompt change actually help, and which cases got worse?
- Which errors would matter to a clinician (a medication added that was never discussed, "stopped" recorded as "continued"), as opposed to harmless wording differences?

**All transcripts are synthetic**, written for this project. No real patient data is used.

## What it found

Run on a local model (Qwen3-14B in LM Studio), 12 tuning cases and 4 held-out cases:

| | Overall | Critical errors |
|---|---|---|
| Schema enforced, but not shown to the model | 0.84 | 14 |
| Schema in the prompt (enforced or not: identical output) | 0.95 | 1 |
| Rules-based prompt (v3), tuning cases | 0.97 | 2 |
| Held-out cases, v1 to v3 | 0.84 to 0.89 | 0 |

- The model has to *see* the schema; enforcing it alone hides what the fields mean.
- Several apparent model errors were gaps in the note format or the scorer.
- Prompt fixes trade one error for another, and totals hide it; per-case comparison catches it.

Details, caveats and next steps: [FINDINGS.md](FINDINGS.md). Run history: [results/](results/).

## What's here

```
schema/visit_note.schema.json   the note format (strict-mode compatible JSON Schema)
data/cases.json                 12 synthetic transcripts with hand-written answer keys (used for tuning)
data/heldout.json               4 more, written after tuning started and never used for it
prompts/v1.md, v2.md, v3.md     minimal prompt; rules-based prompt; v2 with a contradiction removed
src/notevals/
  providers.py                  LM Studio (default), OpenAI, Claude, and an offline mock
  extract.py                    call the model, parse, validate against the schema, retry once with the errors
  score.py                      field-level scoring, unsupported items, critical errors
  report.py                     per-run report and A/B comparison report
tests/                          unit and end-to-end tests (offline, use the mock provider)
run_matrix.sh                   experiment runs (enforcement, schema in prompt, prompt v1 vs v2)
run_final.sh                    v3, held-out check, OpenAI/Claude cross-check
```

## The note

| Field | Notes |
|---|---|
| `chief_complaint` | short text, or null |
| `symptoms[]` | name + `present` / `denied` (explicit negatives count) |
| `medications[]` | name, dose (or null), and the clinician's decision: `started` / `continued` / `changed` / `stopped` |
| `allergies` | `listed` with items, `none_known`, or `not_mentioned` |
| `tests_ordered[]`, `referrals[]` | only those made at this visit |
| `follow_up` | `scheduled` (a visit is planned) or `as_needed` (only if something happens), each with the time the clinician gave in `interval_days`, e.g. "come back if not better in a week" = `as_needed`, 7; or `not_mentioned` |

Every field is required, and "not discussed" has an explicit value. That makes it easy to tell "the model said nothing" apart from "the model forgot", and it keeps the schema usable with strict structured-output modes.

## The cases

Each case targets something that goes wrong in practice:

| Case | What it tests |
|---|---|
| 01 cough | baseline; a denied symptom |
| 02 blood pressure | dose change vs continued medication; allergy listed; 4-week interval |
| 03 statin switch | one drug stopped, another started |
| 04 knee | spouse mentions their own medication (must not be recorded); referral |
| 05 chest burning | several denied symptoms |
| 06 diabetes | speech-recognition errors in drug names ("met forming", "jar dance") |
| 07 work note | almost nothing to record (tests over-filling) |
| 08 migraine | an MRI from last month (history, not an order) |
| 09 asthma | changed, continued and patient-stopped medications in one visit |
| 10 UTI | allergy given as a reaction ("Cipro gave me a rash") |
| 11 annual physical | patient asks about a friend's medication (must not be recorded); 1-year follow-up |
| 12 rash | a referral that is only conditional ("if it isn't better, call"); medication with no dose |

## How it's scored

Each field gets a score from 0 to 1 (or n/a when it does not apply), and a case's overall score is the mean of its fields.

- **Lists** (symptoms, medications, tests, referrals, allergy items): F1 over matched names. Matching is lowercase, punctuation-insensitive, alias-aware (the answer key lists aliases like "Tylenol" for acetaminophen) and allows whole-word containment ("right knee x-ray" matches "x-ray").
- **Within matched items:** symptom status, medication action and dose are scored separately. A dose is correct if every number in the expected dose appears in the output ("500 mg twice a day" matches "500mg BID"); a dose that wasn't spoken must stay null.
- **Unsupported items:** anything in the note that matches nothing in the answer key.
- **Critical errors** (counted separately, because averages hide them): a medication added, missed or recorded with the wrong action, a symptom flipped between present and denied, a wrong allergy status, or no valid note at all.
- **Reliability:** share of cases with a schema-valid note, and how many needed the retry.

The matching is intentionally simple and transparent rather than model-graded, so a score can always be traced back to a specific difference. The trade-off is some false misses on unusual wording; the failure list in each report shows them.

## Running it

Requires Python 3.10+. With [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv sync --extra dev
uv run pytest -q                 # offline tests
```

Commands below are written as `python -m notevals ...`; with uv, prefix them with `uv run` (or activate `.venv`).

With pip instead: `python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`.

### LM Studio (default)

1. In LM Studio, load a model and start the local server (Developer tab). Default address: `http://localhost:1234/v1`.
2. Run:

```bash
python -m notevals run                                # v2 prompt, JSON-schema mode, first loaded model
python -m notevals run --prompt v1 --mode prompt      # baseline: no schema enforcement
python -m notevals run --only 06,09                   # just some cases
```

Settings: `--model`, or the `LMSTUDIO_MODEL` / `LMSTUDIO_BASE_URL` environment variables. The base URL must include the port and `/v1` (e.g. `http://<host>:1234/v1`). From WSL2, use the Windows host's IP with "Serve on Local Network" enabled.

Pick the model explicitly: with just-in-time loading, LM Studio lists every downloaded model, and the default is simply the first one. The first call is slow while the model loads.

**Reasoning models** (Qwen3 and similar) write a long hidden reasoning section before answering. Use `--no-think` to switch it off (appends `/no_think`). Every call is also capped by `--max-tokens` (default 2048) and `--timeout` (default 180 s); a case that times out is scored as invalid and the run continues.

### OpenAI and Claude (final check)

```bash
export OPENAI_API_KEY=...  OPENAI_MODEL=<model id>
python -m notevals run --provider openai

export ANTHROPIC_API_KEY=...                           # default model claude-haiku-5-5
python -m notevals run --provider anthropic            # forced tool call (function calling)
```

### Modes

- `native`: the provider's way of enforcing structure (JSON-schema response format on LM Studio and OpenAI; a forced tool call on Claude), with the schema also pasted into the prompt.
- `native-bare`: the same enforcement, without the schema in the prompt. On LM Studio the model then appears not to see the field descriptions at all (see Findings).
- `tool`: function calling on every provider (the schema is the function's parameters), schema also in the prompt.
- `prompt`: no enforcement; the schema is pasted into the prompt.

### Results

Each run writes `results/<run>/` with `report.md` (scores, critical errors, failures), `summary.json`, `cases.jsonl` (raw outputs and per-case scores) and `meta.json`.

Re-score saved runs after changing the scorer or an answer key (no model calls):

```bash
python -m notevals rescore results/<run-a> results/<run-b>
```

Compare two runs:

```bash
python -m notevals compare results/<run-a> results/<run-b> --save results/compare-a-vs-b.md
```

`./run_matrix.sh` runs the standard set (see below) and writes the comparisons.

## Experiments

1. **Enforcement:** v1 prompt, `prompt` mode vs `native` mode. The model sees the same text in both; does constrained decoding change validity and accuracy?
1b. **Schema in the prompt:** `native-bare` vs `native`. Does the model need to *see* the schema when decoding is already constrained?
2. **Prompt:** v1 vs v2, both `native`. v2 adds rules for negatives, medication decisions, history vs orders, and other people's medications.
3. **Fix and generalize:** v3 removes a contradiction found in v2. v1 vs v3 on the held-out cases checks that the prompt changes help on transcripts they were not tuned on.
4. **Cross-check:** v3 `native` on OpenAI and Claude, to see which failures are the local model's and which are the task's (or the answer key's).

Findings go in [FINDINGS.md](FINDINGS.md).

## Limitations

- 12 tuning cases and 4 held-out cases are enough to see failure patterns, not to rank models. Differences of a few points are noise.
- The prompts were revised while looking at results on the 12 tuning cases, so scores there are optimistic. The held-out set is the fairer check.
- The answer keys are one person's reading of each transcript; a couple of cases (12 especially) are judgment calls, flagged in the case tags.
- Name matching is lexical. It will occasionally mark a reasonable synonym as a miss; check the failure list before trusting a low score.
- Transcripts are clean dialogue apart from case 06. Real speech-recognition output is messier.

## How this was built

I designed the experiments, wrote the specs, decided every change to the cases, prompts and scorer, and ran and read every result. The code was written with an AI coding agent (Claude) working from those specs, with each change reviewed by me.

## License

MIT. See [LICENSE](LICENSE).
