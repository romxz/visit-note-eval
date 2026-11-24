# Comparison

- **A** `lm-v1-native`: lmstudio/qwen/qwen3-14b · v1 · native
- **B** `lm-v2-native`: lmstudio/qwen/qwen3-14b · v2 · native

| Metric | A | B | Change |
|---|---|---|---|
| overall | 0.83 | 0.93 | +0.10 |
| chief_complaint | 1.00 | 1.00 | +0.00 |
| symptoms | 0.85 | 0.85 | +0.00 |
| symptom_status | 0.85 | 1.00 | +0.15 |
| medications | 0.96 | 0.96 | +0.00 |
| med_action | 0.91 | 1.00 | +0.09 |
| med_dose | 0.68 | 0.79 | +0.11 |
| allergy_status | 0.33 | 1.00 | +0.67 |
| allergy_items | 1.00 | 1.00 | +0.00 |
| tests_ordered | 0.92 | 1.00 | +0.08 |
| referrals | 0.92 | 0.92 | +0.00 |
| follow_up_status | 0.67 | 0.75 | +0.08 |
| follow_up_interval | 1.00 | 1.00 | +0.00 |
| schema-valid | 100% | 100% | |
| first-try valid | 100% | 100% | |
| critical errors | 14 | 2 | -12 |
| unsupported items | 4 | 4 | +0 |
| mean latency (s) | 15.516 | 15.338 | |

## Improved cases

- 12-rash-conditional-referral: +0.24
- 10-uti: +0.21
- 02-bp-dose-change: +0.17
- 07-nothing-to-record: +0.14
- 04-knee-spouse-distractor: +0.14
- 09-asthma-mixed-actions: +0.11
- 08-migraine-prior-test: +0.10
- 03-statin-switch: +0.08
- 05-chest-negations: +0.08
- 06-asr-drug-names: +0.04
- 01-cough-viral: +0.02

## Regressed cases

- 11-physical-ozempic-distractor: -0.09
