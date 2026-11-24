# Run lm-v3-main

Provider `lmstudio`, model `qwen/qwen3-14b`, prompt `v3`, mode `native`, temperature 0.0, 12 cases.

**Overall 0.97** · schema-valid 100% (first try 100%) · **critical errors 2** · unsupported items 5 · mean latency 17.008s

## By field

| Field | Score |
|---|---|
| chief_complaint | 1.00 |
| symptoms | 0.86 |
| symptom_status | 1.00 |
| medications | 0.93 |
| med_action | 1.00 |
| med_dose | 0.97 |
| allergy_status | 1.00 |
| allergy_items | 1.00 |
| tests_ordered | 1.00 |
| referrals | 0.92 |
| follow_up_status | 1.00 |
| follow_up_interval | 1.00 |

## By case

| Case | Overall | Critical | Valid | Attempts | Unsupported |
|---|---|---|---|---|---|
| 01-cough-viral | 1.00 | 0 | yes | 1 | 0 |
| 02-bp-dose-change | 1.00 | 0 | yes | 1 | 0 |
| 03-statin-switch | 1.00 | 0 | yes | 1 | 0 |
| 04-knee-spouse-distractor | 1.00 | 0 | yes | 1 | 0 |
| 05-chest-negations | 1.00 | 0 | yes | 1 | 0 |
| 06-asr-drug-names | 0.96 | 1 | yes | 1 | 1 |
| 07-nothing-to-record | 0.96 | 0 | yes | 1 | 1 |
| 08-migraine-prior-test | 1.00 | 0 | yes | 1 | 0 |
| 09-asthma-mixed-actions | 0.97 | 0 | yes | 1 | 0 |
| 10-uti | 1.00 | 0 | yes | 1 | 0 |
| 11-physical-ozempic-distractor | 0.88 | 1 | yes | 1 | 2 |
| 12-rash-conditional-referral | 0.89 | 0 | yes | 1 | 1 |

## Critical errors

- 06-asr-drug-names: medications: wrong name for empagliflozin (got 'jar dance')
- 11-physical-ozempic-distractor: medications: added Ozempic (stopped), not in transcript

## Unsupported items (in the note, not in the transcript's answer key)

- 06-asr-drug-names: medication: jar dance (started)
- 07-nothing-to-record: symptom: flu (present)
- 11-physical-ozempic-distractor: symptom: weight loss (denied)
- 11-physical-ozempic-distractor: medication: Ozempic (stopped)
- 12-rash-conditional-referral: referral: dermatology

## Failures

**06-asr-drug-names**
- medications: wrong name for empagliflozin: got 'jar dance'

**09-asthma-mixed-actions**
- med_dose: salbutamol: got None, wanted '2 puffs as needed'

**12-rash-conditional-referral**
- symptoms: missed itching (present)

