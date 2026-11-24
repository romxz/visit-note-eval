# Run lm-v1-prompt

Provider `lmstudio`, model `qwen/qwen3-14b`, prompt `v1`, mode `prompt`, temperature 0.0, 12 cases.

**Overall 0.95** · schema-valid 100% (first try 100%) · **critical errors 1** · unsupported items 5 · mean latency 16.63s

## By field

| Field | Score |
|---|---|
| chief_complaint | 0.83 |
| symptoms | 0.89 |
| symptom_status | 1.00 |
| medications | 0.96 |
| med_action | 1.00 |
| med_dose | 0.97 |
| allergy_status | 1.00 |
| allergy_items | 1.00 |
| tests_ordered | 1.00 |
| referrals | 0.92 |
| follow_up_status | 0.92 |
| follow_up_interval | 1.00 |

## By case

| Case | Overall | Critical | Valid | Attempts | Unsupported |
|---|---|---|---|---|---|
| 01-cough-viral | 1.00 | 0 | yes | 1 | 0 |
| 02-bp-dose-change | 1.00 | 0 | yes | 1 | 0 |
| 03-statin-switch | 0.91 | 0 | yes | 1 | 2 |
| 04-knee-spouse-distractor | 1.00 | 0 | yes | 1 | 0 |
| 05-chest-negations | 1.00 | 0 | yes | 1 | 0 |
| 06-asr-drug-names | 0.96 | 1 | yes | 1 | 1 |
| 07-nothing-to-record | 0.74 | 0 | yes | 1 | 1 |
| 08-migraine-prior-test | 1.00 | 0 | yes | 1 | 0 |
| 09-asthma-mixed-actions | 0.97 | 0 | yes | 1 | 0 |
| 10-uti | 1.00 | 0 | yes | 1 | 0 |
| 11-physical-ozempic-distractor | 0.91 | 0 | yes | 1 | 0 |
| 12-rash-conditional-referral | 0.92 | 0 | yes | 1 | 1 |

## Critical errors

- 06-asr-drug-names: medications: wrong name for empagliflozin (got 'jar dance')

## Unsupported items (in the note, not in the transcript's answer key)

- 03-statin-switch: symptom: leg ache (present)
- 03-statin-switch: symptom: thigh ache (present)
- 06-asr-drug-names: medication: jar dance (started)
- 07-nothing-to-record: symptom: flu (denied)
- 12-rash-conditional-referral: referral: dermatology

## Failures

**03-statin-switch**
- symptoms: missed muscle aches (present)

**06-asr-drug-names**
- medications: wrong name for empagliflozin: got 'jar dance'

**07-nothing-to-record**
- chief_complaint: got None, wanted [['note', 'work']]
- follow_up_status: got scheduled, wanted not_mentioned

**09-asthma-mixed-actions**
- med_dose: salbutamol: got None, wanted '2 puffs as needed'

**11-physical-ozempic-distractor**
- chief_complaint: got None, wanted [['physical', 'annual', 'checkup', 'check-up']]

