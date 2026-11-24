# Comparison

- **A** `lm-v1-native-bare`: lmstudio/qwen/qwen3-14b · v1 · native-bare
- **B** `lm-v1-native`: lmstudio/qwen/qwen3-14b · v1 · native

| Metric | A | B | Change |
|---|---|---|---|
| overall | 0.84 | 0.95 | +0.11 |
| chief_complaint | 1.00 | 0.83 | -0.17 |
| symptoms | 0.85 | 0.89 | +0.04 |
| symptom_status | 0.85 | 1.00 | +0.15 |
| medications | 0.96 | 0.96 | +0.00 |
| med_action | 0.91 | 1.00 | +0.09 |
| med_dose | 0.73 | 0.97 | +0.24 |
| allergy_status | 0.33 | 1.00 | +0.67 |
| allergy_items | 1.00 | 1.00 | +0.00 |
| tests_ordered | 0.92 | 1.00 | +0.08 |
| referrals | 0.92 | 0.92 | +0.00 |
| follow_up_status | 0.67 | 0.92 | +0.25 |
| follow_up_interval | 1.00 | 1.00 | +0.00 |
| schema-valid | 100% | 100% | |
| first-try valid | 100% | 100% | |
| critical errors | 14 | 1 | -13 |
| unsupported items | 4 | 5 | +1 |
| mean latency (s) | 17.045 | 16.864 | |

## Improved cases

- 12-rash-conditional-referral: +0.33
- 10-uti: +0.30
- 02-bp-dose-change: +0.21
- 04-knee-spouse-distractor: +0.17
- 09-asthma-mixed-actions: +0.11
- 01-cough-viral: +0.10
- 08-migraine-prior-test: +0.10
- 05-chest-negations: +0.09
- 06-asr-drug-names: +0.04

## Regressed cases

- 11-physical-ozempic-distractor: -0.09
  - new: got None, wanted [['physical', 'annual', 'checkup', 'check-up']]
- 07-nothing-to-record: -0.01
  - new: got None, wanted [['note', 'work']]
  - new: got scheduled, wanted not_mentioned
- 03-statin-switch: -0.01
  - new: missed muscle aches (present)
