# Findings

Local model `qwen/qwen3-14b` in LM Studio, reasoning off (`/no_think`), temperature 0, up to 2 attempts per case. 12 tuning cases and 4 held-out cases, all synthetic. November 2026. Everything ran locally; no hosted models were used.

## Results

| Run | Cases | Overall | Critical errors | Schema-valid |
|---|---|---|---|---|
| v1 prompt, no enforcement | 12 | 0.951 | 1 | 100% |
| v1, schema enforced, schema also in prompt | 12 | 0.951 | 1 | 100% |
| v1, schema enforced, schema **not** in prompt | 12 | 0.838 | 14 | 100% |
| v2 (rules), schema enforced | 12 | 0.964 | 2 | 100% |
| v3 (v2 with a contradiction removed) | 12 | 0.972 | 2 | 100% |
| v1 on held-out cases | 4 | 0.839 | 0 | 100% |
| v3 on held-out cases | 4 | 0.889 | 0 | 100% |

A repeat of the four tuning-set runs gave the same scores, so results are reproducible at temperature 0. About 16 seconds per case.

## What the numbers say

1. **The model has to see the schema; enforcing it is not enough.** With LM Studio's JSON-schema mode alone, the schema constrains the output but its field descriptions never reach the model. With the minimal prompt, the model then had no idea what the choices meant: it set allergies to `none_known` in all 12 cases, including ones where it listed "Penicillin" in the same field, and recorded denied symptoms as present. Putting the schema text in the prompt took allergy status from 0.33 to 1.00 and critical errors from 14 to 1. My first run had exactly this flaw, so it compared "schema visible vs not" when it was meant to compare "enforced vs not".
2. **Enforcement changed nothing for this model.** With the schema in the prompt, enforced and unenforced runs produced identical notes in 12 of 12 cases. Qwen3-14B already writes valid JSON at temperature 0, so here enforcement is insurance against malformed output, with no effect on accuracy.
3. **The prompt rules helped, and the gain held on unseen cases.** Tuning set: 0.951 (v1), 0.964 (v2), 0.972 (v3). Held-out set: 0.839 (v1) to 0.889 (v3), with no case getting worse. Most of the held-out gain came from one rule (the reason for the visit can be a non-symptom: 0.25 to 0.75 on that field). Four cases is too few to trust the size of the gain; the direction is the result.
4. **Prompt fixes trade errors, and the totals hide it.** v2 told the model both to write drug names "exactly as spoken" and to correct mishearings. It followed the first: "met forming", "jar dance" and "A one C" went into the note verbatim, where v1 had written "metformin". v3 removed the contradiction and fixed those, but in another case the model started recording a friend's Ozempic as a stopped medication. The critical-error count was 2 before and after; only the per-case comparison showed that the errors had changed.
5. **Several "model errors" were my design errors.** The note format could not say "come back if not better in a week" (a conditional instruction with a time window), so both possible answers were partly wrong. The format did not say whether the main complaint belongs in the symptom list. My scorer read "six" and "6" as different doses, and counted a misheard drug name as two errors. I fixed the format and the scorer before judging the model on those fields.
6. **What this model does not do well, even with explicit rules:** it ignores "a referral offered only if something happens has not been made" (it recorded a conditional orthopedics referral), it cannot map "jar dance" to Jardiance (it resolved "amlo dipping" and "loss art an" without trouble, so this looks like a brand-name knowledge gap), and it read "six weeks" as 180 days once.

## Changes made because of these results

- `native` mode puts the schema in the prompt; the old behaviour is kept as `native-bare` to show the effect.
- Follow-up can carry a time window on as-needed instructions; symptoms include the main complaint; both stated in the schema.
- Scorer reads number words in doses and counts a misnamed drug once. A `rescore` command applies scorer and answer-key fixes to saved outputs without calling the model again.
- Prompt v3; 4 held-out cases added before v3 was run.

## Caveats

- 16 cases, one local model, one run each. Enough to see failure patterns, not to rank models.
- The prompts were revised while looking at the 12 tuning cases, so those scores are optimistic. The held-out set is the fairer check.
- After the held-out run I loosened one answer key (H1: the model listed "kidney function" and "potassium" as two tests where the key expected one) and re-scored. That changed the held-out scores by about 0.01. In H3 I kept a judgment call: "we'll repeat the cholesterol in three months" counts as a test ordered today, which the model disagreed with.
- Matching is lexical, so a misspelling ("creatininine") counts as a miss.

## What I'd do next

- Run v3 on other models, local and hosted (the harness supports OpenAI and Claude), to separate this model's limits from the task's.
- Write more cases in the weakest areas (conditional referrals, brand-name drugs, time intervals) and a noisier speech-recognition version of each transcript.
- Repeat runs at a non-zero temperature to measure how stable each answer is.
- Add an LLM judge as a second layer on top of the exact checks, never replacing them, for two jobs: deciding whether pairs the lexical scorer could not match mean the same thing ("can't lift my arm" vs "limited range of motion"), and checking, without an answer key, whether each item in a note is supported by the transcript. The second is what production monitoring needs, since real notes have no answer key. Use a different model as the judge, and measure its agreement with the answer keys on these cases before trusting it.
- Track the scores per prompt or model change, the way a release check would.
