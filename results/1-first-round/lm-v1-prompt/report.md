# Run lm-v1-prompt

Provider `lmstudio`, model `qwen/qwen3-14b`, prompt `v1`, mode `prompt`, temperature 0.0, 12 cases.

**Overall 0.95** · schema-valid 100% (first try 100%) · **critical errors 2** · unsupported items 2 · mean latency 15.023s

## By field

| Field | Score |
|---|---|
| chief_complaint | 0.92 |
| symptoms | 0.92 |
| symptom_status | 1.00 |
| medications | 0.96 |
| med_action | 1.00 |
| med_dose | 0.76 |
| allergy_status | 1.00 |
| allergy_items | 1.00 |
| tests_ordered | 1.00 |
| referrals | 0.92 |
| follow_up_status | 1.00 |
| follow_up_interval | 1.00 |

## By case

| Case | Overall | Critical | Valid | Attempts | Unsupported |
|---|---|---|---|---|---|
| 01-cough-viral | 0.91 | 0 | yes | 1 | 0 |
| 02-bp-dose-change | 1.00 | 0 | yes | 1 | 0 |
| 03-statin-switch | 1.00 | 0 | yes | 1 | 0 |
| 04-knee-spouse-distractor | 0.97 | 0 | yes | 1 | 0 |
| 05-chest-negations | 1.00 | 0 | yes | 1 | 0 |
| 06-asr-drug-names | 0.96 | 2 | yes | 1 | 1 |
| 07-nothing-to-record | 1.00 | 0 | yes | 1 | 0 |
| 08-migraine-prior-test | 1.00 | 0 | yes | 1 | 0 |
| 09-asthma-mixed-actions | 0.94 | 0 | yes | 1 | 0 |
| 10-uti | 0.88 | 0 | yes | 1 | 0 |
| 11-physical-ozempic-distractor | 0.91 | 0 | yes | 1 | 0 |
| 12-rash-conditional-referral | 0.88 | 0 | yes | 1 | 1 |

## Critical errors

- 06-asr-drug-names: medications: added jar dance (started), not in transcript
- 06-asr-drug-names: medications: missed empagliflozin (started)

## Unsupported items (in the note, not in the transcript's answer key)

- 06-asr-drug-names: medication: jar dance (started)
- 12-rash-conditional-referral: referral: dermatology

## Failures

**01-cough-viral**
- med_dose: acetaminophen: got '500 mg every six hours as needed', wanted '500 mg every 6 hours as needed'

**04-knee-spouse-distractor**
- symptoms: missed knee pain (present)

**06-asr-drug-names**
- medications: missed empagliflozin (started)

**09-asthma-mixed-actions**
- med_dose: fluticasone: got 'two puffs twice a day', wanted '250 mcg two puffs twice a day'
- med_dose: salbutamol: got None, wanted '2 puffs as needed'

**10-uti**
- symptoms: missed painful urination (present)
- symptoms: missed urinary frequency (present)
- med_dose: nitrofurantoin: got '100 mg twice a day for five days', wanted '100 mg twice a day for 5 days'

**11-physical-ozempic-distractor**
- chief_complaint: got None, wanted [['physical', 'annual', 'checkup', 'check-up']]

**12-rash-conditional-referral**
- symptoms: missed itching (present)

