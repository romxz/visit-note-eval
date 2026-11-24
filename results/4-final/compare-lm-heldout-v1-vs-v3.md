# Comparison

- **A** `lm-v1-heldout`: lmstudio/qwen/qwen3-14b · v1 · native
- **B** `lm-v3-heldout`: lmstudio/qwen/qwen3-14b · v3 · native

| Metric | A | B | Change |
|---|---|---|---|
| overall | 0.84 | 0.89 | +0.05 |
| chief_complaint | 0.25 | 0.75 | +0.50 |
| symptoms | 0.87 | 0.96 | +0.10 |
| symptom_status | 1.00 | 1.00 | +0.00 |
| medications | 1.00 | 1.00 | +0.00 |
| med_action | 1.00 | 1.00 | +0.00 |
| med_dose | 1.00 | 1.00 | +0.00 |
| allergy_status | 1.00 | 1.00 | +0.00 |
| allergy_items | 1.00 | 1.00 | +0.00 |
| tests_ordered | 0.50 | 0.50 | +0.00 |
| referrals | 0.75 | 0.75 | +0.00 |
| follow_up_status | 1.00 | 1.00 | +0.00 |
| follow_up_interval | 0.75 | 0.75 | +0.00 |
| schema-valid | 100% | 100% | |
| first-try valid | 100% | 100% | |
| critical errors | 0 | 0 | +0 |
| unsupported items | 3 | 2 | -1 |
| mean latency (s) | 15.477 | 16.054 | |

## Improved cases

- H1-asr-bp-meds: +0.11
- H4-gout-mixed: +0.08

## Regressed cases

None.
