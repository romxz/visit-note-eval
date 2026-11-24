# Run lm-v2-native

Provider `lmstudio`, model `qwen/qwen3-14b`, prompt `v2`, mode `native`, temperature 0.0, 12 cases.

**Overall 0.93** · schema-valid 100% (first try 100%) · **critical errors 2** · unsupported items 4 · mean latency 15.338s

## By field

| Field | Score |
|---|---|
| chief_complaint | 1.00 |
| symptoms | 0.85 |
| symptom_status | 1.00 |
| medications | 0.96 |
| med_action | 1.00 |
| med_dose | 0.79 |
| allergy_status | 1.00 |
| allergy_items | 1.00 |
| tests_ordered | 1.00 |
| referrals | 0.92 |
| follow_up_status | 0.75 |
| follow_up_interval | 1.00 |

## By case

| Case | Overall | Critical | Valid | Attempts | Unsupported |
|---|---|---|---|---|---|
| 01-cough-viral | 0.82 | 0 | yes | 1 | 0 |
| 02-bp-dose-change | 1.00 | 0 | yes | 1 | 0 |
| 03-statin-switch | 1.00 | 0 | yes | 1 | 0 |
| 04-knee-spouse-distractor | 0.97 | 0 | yes | 1 | 0 |
| 05-chest-negations | 0.99 | 0 | yes | 1 | 0 |
| 06-asr-drug-names | 0.96 | 2 | yes | 1 | 1 |
| 07-nothing-to-record | 0.89 | 0 | yes | 1 | 0 |
| 08-migraine-prior-test | 1.00 | 0 | yes | 1 | 0 |
| 09-asthma-mixed-actions | 0.97 | 0 | yes | 1 | 0 |
| 10-uti | 0.91 | 0 | yes | 1 | 0 |
| 11-physical-ozempic-distractor | 0.91 | 0 | yes | 1 | 2 |
| 12-rash-conditional-referral | 0.79 | 0 | yes | 1 | 1 |

## Critical errors

- 06-asr-drug-names: medications: added jar dance (started), not in transcript
- 06-asr-drug-names: medications: missed empagliflozin (started)

## Unsupported items (in the note, not in the transcript's answer key)

- 06-asr-drug-names: medication: jar dance (started)
- 11-physical-ozempic-distractor: symptom: weight_loss (denied)
- 11-physical-ozempic-distractor: symptom: fever (denied)
- 12-rash-conditional-referral: referral: dermatology

## Failures

**01-cough-viral**
- med_dose: acetaminophen: got '500 mg', wanted '500 mg every 6 hours as needed'
- follow_up_status: got scheduled, wanted as_needed

**04-knee-spouse-distractor**
- symptoms: missed knee pain (present)

**05-chest-negations**
- symptoms: missed heartburn (present)

**06-asr-drug-names**
- medications: missed empagliflozin (started)

**07-nothing-to-record**
- follow_up_status: got scheduled, wanted not_mentioned

**09-asthma-mixed-actions**
- med_dose: salbutamol: got None, wanted '2 puffs as needed'

**10-uti**
- med_dose: nitrofurantoin: got '100 mg twice a day for five days', wanted '100 mg twice a day for 5 days'

**12-rash-conditional-referral**
- symptoms: missed itching (present)
- follow_up_status: got scheduled, wanted as_needed

