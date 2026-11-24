# Comparison

- **A** `lm-v1-native`: lmstudio/qwen/qwen3-14b · v1 · native
- **B** `lm-v2-native`: lmstudio/qwen/qwen3-14b · v2 · native

| Metric | A | B | Change |
|---|---|---|---|
| overall | 0.95 | 0.96 | +0.01 |
| chief_complaint | 0.83 | 0.92 | +0.08 |
| symptoms | 0.89 | 0.97 | +0.08 |
| symptom_status | 1.00 | 1.00 | +0.00 |
| medications | 0.96 | 0.92 | -0.04 |
| med_action | 1.00 | 1.00 | +0.00 |
| med_dose | 0.97 | 0.97 | -0.00 |
| allergy_status | 1.00 | 1.00 | +0.00 |
| allergy_items | 1.00 | 1.00 | +0.00 |
| tests_ordered | 1.00 | 0.92 | -0.08 |
| referrals | 0.92 | 0.92 | +0.00 |
| follow_up_status | 0.92 | 1.00 | +0.08 |
| follow_up_interval | 1.00 | 1.00 | +0.00 |
| schema-valid | 100% | 100% | |
| first-try valid | 100% | 100% | |
| critical errors | 1 | 2 | +1 |
| unsupported items | 5 | 5 | +0 |
| mean latency (s) | 17.191 | 17.831 | |

## Improved cases

- 07-nothing-to-record: +0.26
- 03-statin-switch: +0.06

## Regressed cases

- 06-asr-drug-names: -0.16
  - new: missed hba1c
  - new: wrong name for metformin: got 'met forming'
