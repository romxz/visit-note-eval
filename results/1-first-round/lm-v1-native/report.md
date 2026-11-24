# Run lm-v1-native

Provider `lmstudio`, model `qwen/qwen3-14b`, prompt `v1`, mode `native`, temperature 0.0, 12 cases.

**Overall 0.83** · schema-valid 100% (first try 100%) · **critical errors 14** · unsupported items 4 · mean latency 15.516s

## By field

| Field | Score |
|---|---|
| chief_complaint | 1.00 |
| symptoms | 0.85 |
| symptom_status | 0.85 |
| medications | 0.96 |
| med_action | 0.91 |
| med_dose | 0.68 |
| allergy_status | 0.33 |
| allergy_items | 1.00 |
| tests_ordered | 0.92 |
| referrals | 0.92 |
| follow_up_status | 0.67 |
| follow_up_interval | 1.00 |

## By case

| Case | Overall | Critical | Valid | Attempts | Unsupported |
|---|---|---|---|---|---|
| 01-cough-viral | 0.80 | 0 | yes | 1 | 0 |
| 02-bp-dose-change | 0.83 | 3 | yes | 1 | 0 |
| 03-statin-switch | 0.92 | 1 | yes | 1 | 0 |
| 04-knee-spouse-distractor | 0.83 | 2 | yes | 1 | 1 |
| 05-chest-negations | 0.91 | 1 | yes | 1 | 0 |
| 06-asr-drug-names | 0.92 | 1 | yes | 1 | 0 |
| 07-nothing-to-record | 0.75 | 1 | yes | 1 | 1 |
| 08-migraine-prior-test | 0.90 | 0 | yes | 1 | 1 |
| 09-asthma-mixed-actions | 0.86 | 2 | yes | 1 | 0 |
| 10-uti | 0.70 | 1 | yes | 1 | 0 |
| 11-physical-ozempic-distractor | 1.00 | 0 | yes | 1 | 0 |
| 12-rash-conditional-referral | 0.55 | 2 | yes | 1 | 1 |

## Critical errors

- 02-bp-dose-change: symptom_status: headache: got present, wanted denied
- 02-bp-dose-change: symptom_status: dizziness: got present, wanted denied
- 02-bp-dose-change: allergy_status: got none_known, wanted listed
- 03-statin-switch: allergy_status: got none_known, wanted not_mentioned
- 04-knee-spouse-distractor: symptom_status: swelling: got present, wanted denied
- 04-knee-spouse-distractor: medications: added metformin (continued), not in transcript
- 05-chest-negations: allergy_status: got none_known, wanted listed
- 06-asr-drug-names: allergy_status: got none_known, wanted not_mentioned
- 07-nothing-to-record: allergy_status: got none_known, wanted not_mentioned
- 09-asthma-mixed-actions: medications: missed vitamin d (stopped)
- 09-asthma-mixed-actions: allergy_status: got none_known, wanted listed
- 10-uti: allergy_status: got none_known, wanted listed
- 12-rash-conditional-referral: med_action: hydrocortisone: got continued, wanted started
- 12-rash-conditional-referral: allergy_status: got none_known, wanted not_mentioned

## Unsupported items (in the note, not in the transcript's answer key)

- 04-knee-spouse-distractor: medication: metformin (continued)
- 07-nothing-to-record: symptom: flu (present)
- 08-migraine-prior-test: test: MRI (already performed and was normal)
- 12-rash-conditional-referral: referral: Dermatology (if no improvement in two weeks)

## Failures

**01-cough-viral**
- symptoms: missed shortness of breath (denied)
- med_dose: acetaminophen: got '500 mg every six hours as needed for fever', wanted '500 mg every 6 hours as needed'
- follow_up_status: got scheduled, wanted as_needed

**02-bp-dose-change**
- symptom_status: headache: got present, wanted denied
- symptom_status: dizziness: got present, wanted denied
- allergy_status: got none_known, wanted listed

**03-statin-switch**
- allergy_status: got none_known, wanted not_mentioned

**04-knee-spouse-distractor**
- symptom_status: swelling: got present, wanted denied
- follow_up_status: got scheduled, wanted as_needed

**05-chest-negations**
- symptoms: missed heartburn (present)
- allergy_status: got none_known, wanted listed

**06-asr-drug-names**
- allergy_status: got none_known, wanted not_mentioned

**07-nothing-to-record**
- symptoms: missed fever (denied)
- allergy_status: got none_known, wanted not_mentioned

**08-migraine-prior-test**
- symptoms: missed vision changes (denied)

**09-asthma-mixed-actions**
- medications: missed vitamin d (stopped)
- med_dose: fluticasone: got '125 micrograms, 2 puffs twice daily', wanted '250 mcg two puffs twice a day'
- allergy_status: got none_known, wanted listed

**10-uti**
- symptoms: missed fever (denied)
- symptoms: missed back pain (denied)
- med_dose: nitrofurantoin: got '100 mg', wanted '100 mg twice a day for 5 days'
- allergy_status: got none_known, wanted listed
- follow_up_status: got scheduled, wanted as_needed

**12-rash-conditional-referral**
- med_action: hydrocortisone: got continued, wanted started
- med_dose: hydrocortisone: got 'prescribed', wanted None
- allergy_status: got none_known, wanted not_mentioned
- follow_up_status: got scheduled, wanted as_needed

