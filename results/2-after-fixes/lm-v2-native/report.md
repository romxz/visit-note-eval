# Run lm-v2-native

Provider `lmstudio`, model `qwen/qwen3-14b`, prompt `v2`, mode `native`, temperature 0.0, 12 cases.

**Overall 0.96** · schema-valid 100% (first try 100%) · **critical errors 2** · unsupported items 5 · mean latency 17.831s

## By field

| Field | Score |
|---|---|
| chief_complaint | 0.92 |
| symptoms | 0.97 |
| symptom_status | 1.00 |
| medications | 0.92 |
| med_action | 1.00 |
| med_dose | 0.97 |
| allergy_status | 1.00 |
| allergy_items | 1.00 |
| tests_ordered | 0.92 |
| referrals | 0.92 |
| follow_up_status | 1.00 |
| follow_up_interval | 1.00 |

## By case

| Case | Overall | Critical | Valid | Attempts | Unsupported |
|---|---|---|---|---|---|
| 01-cough-viral | 1.00 | 0 | yes | 1 | 0 |
| 02-bp-dose-change | 1.00 | 0 | yes | 1 | 0 |
| 03-statin-switch | 0.97 | 0 | yes | 1 | 1 |
| 04-knee-spouse-distractor | 1.00 | 0 | yes | 1 | 0 |
| 05-chest-negations | 1.00 | 0 | yes | 1 | 0 |
| 06-asr-drug-names | 0.80 | 2 | yes | 1 | 3 |
| 07-nothing-to-record | 1.00 | 0 | yes | 1 | 0 |
| 08-migraine-prior-test | 1.00 | 0 | yes | 1 | 0 |
| 09-asthma-mixed-actions | 0.97 | 0 | yes | 1 | 0 |
| 10-uti | 1.00 | 0 | yes | 1 | 0 |
| 11-physical-ozempic-distractor | 0.91 | 0 | yes | 1 | 0 |
| 12-rash-conditional-referral | 0.92 | 0 | yes | 1 | 1 |

## Critical errors

- 06-asr-drug-names: medications: wrong name for metformin (got 'met forming')
- 06-asr-drug-names: medications: wrong name for empagliflozin (got 'jar dance')

## Unsupported items (in the note, not in the transcript's answer key)

- 03-statin-switch: symptom: thigh pain (present)
- 06-asr-drug-names: medication: met forming (continued)
- 06-asr-drug-names: medication: jar dance (started)
- 06-asr-drug-names: test: A one C
- 12-rash-conditional-referral: referral: dermatology

## Failures

**06-asr-drug-names**
- medications: wrong name for metformin: got 'met forming'
- medications: wrong name for empagliflozin: got 'jar dance'
- tests_ordered: missed hba1c

**09-asthma-mixed-actions**
- med_dose: salbutamol: got None, wanted '2 puffs as needed'

**11-physical-ozempic-distractor**
- chief_complaint: got None, wanted [['physical', 'annual', 'checkup', 'check-up']]

