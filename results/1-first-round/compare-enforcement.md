# Comparison

- **A** `lm-v1-prompt`: lmstudio/qwen/qwen3-14b · v1 · prompt
- **B** `lm-v1-native`: lmstudio/qwen/qwen3-14b · v1 · native

| Metric | A | B | Change |
|---|---|---|---|
| overall | 0.95 | 0.83 | -0.12 |
| chief_complaint | 0.92 | 1.00 | +0.08 |
| symptoms | 0.92 | 0.85 | -0.07 |
| symptom_status | 1.00 | 0.85 | -0.15 |
| medications | 0.96 | 0.96 | -0.00 |
| med_action | 1.00 | 0.91 | -0.09 |
| med_dose | 0.76 | 0.68 | -0.08 |
| allergy_status | 1.00 | 0.33 | -0.67 |
| allergy_items | 1.00 | 1.00 | +0.00 |
| tests_ordered | 1.00 | 0.92 | -0.08 |
| referrals | 0.92 | 0.92 | +0.00 |
| follow_up_status | 1.00 | 0.67 | -0.33 |
| follow_up_interval | 1.00 | 1.00 | +0.00 |
| schema-valid | 100% | 100% | |
| first-try valid | 100% | 100% | |
| critical errors | 2 | 14 | +12 |
| unsupported items | 2 | 4 | +2 |
| mean latency (s) | 15.023 | 15.516 | |

## Improved cases

- 11-physical-ozempic-distractor: +0.09

## Regressed cases

- 12-rash-conditional-referral: -0.33
  - new: got none_known, wanted not_mentioned
  - new: got scheduled, wanted as_needed
  - new: hydrocortisone: got 'prescribed', wanted None
  - new: hydrocortisone: got continued, wanted started
- 07-nothing-to-record: -0.25
  - new: got none_known, wanted not_mentioned
  - new: missed fever (denied)
- 10-uti: -0.18
  - new: got none_known, wanted listed
  - new: got scheduled, wanted as_needed
  - new: missed back pain (denied)
  - new: missed fever (denied)
  - new: nitrofurantoin: got '100 mg', wanted '100 mg twice a day for 5 days'
- 02-bp-dose-change: -0.17
  - new: dizziness: got present, wanted denied
  - new: got none_known, wanted listed
  - new: headache: got present, wanted denied
- 04-knee-spouse-distractor: -0.14
  - new: got scheduled, wanted as_needed
  - new: swelling: got present, wanted denied
- 01-cough-viral: -0.11
  - new: acetaminophen: got '500 mg every six hours as needed for fever', wanted '500 mg every 6 hours as needed'
  - new: got scheduled, wanted as_needed
  - new: missed shortness of breath (denied)
- 08-migraine-prior-test: -0.10
  - new: missed vision changes (denied)
- 05-chest-negations: -0.09
  - new: got none_known, wanted listed
  - new: missed heartburn (present)
- 09-asthma-mixed-actions: -0.09
  - new: fluticasone: got '125 micrograms, 2 puffs twice daily', wanted '250 mcg two puffs twice a day'
  - new: got none_known, wanted listed
  - new: missed vitamin d (stopped)
- 03-statin-switch: -0.08
  - new: got none_known, wanted not_mentioned
- 06-asr-drug-names: -0.04
  - new: got none_known, wanted not_mentioned
