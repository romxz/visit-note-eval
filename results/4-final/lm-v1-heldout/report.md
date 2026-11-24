# Run lm-v1-heldout

Provider `lmstudio`, model `qwen/qwen3-14b`, prompt `v1`, mode `native`, temperature 0.0, 4 cases.

**Overall 0.84** · schema-valid 100% (first try 100%) · **critical errors 0** · unsupported items 3 · mean latency 15.477s

## By field

| Field | Score |
|---|---|
| chief_complaint | 0.25 |
| symptoms | 0.87 |
| symptom_status | 1.00 |
| medications | 1.00 |
| med_action | 1.00 |
| med_dose | 1.00 |
| allergy_status | 1.00 |
| allergy_items | 1.00 |
| tests_ordered | 0.50 |
| referrals | 0.75 |
| follow_up_status | 1.00 |
| follow_up_interval | 0.75 |

## By case

| Case | Overall | Critical | Valid | Attempts | Unsupported |
|---|---|---|---|---|---|
| H1-asr-bp-meds | 0.81 | 0 | yes | 1 | 1 |
| H2-shoulder-conditional | 0.90 | 0 | yes | 1 | 1 |
| H3-lab-review-distractor | 0.82 | 0 | yes | 1 | 0 |
| H4-gout-mixed | 0.83 | 0 | yes | 1 | 1 |

## Critical errors

None.

## Unsupported items (in the note, not in the transcript's answer key)

- H1-asr-bp-meds: symptom: high blood pressure (present)
- H2-shoulder-conditional: referral: orthopedics
- H4-gout-mixed: test: creatininine

## Failures

**H1-asr-bp-meds**
- chief_complaint: got None, wanted [['blood pressure', 'hypertension', 'bp']]
- follow_up_interval: got 180, wanted 42

**H2-shoulder-conditional**
- symptoms: missed limited range of motion (present)

**H3-lab-review-distractor**
- chief_complaint: got None, wanted [['blood work', 'lab', 'results', 'bloodwork', 'cholesterol']]
- tests_ordered: missed lipid panel

**H4-gout-mixed**
- chief_complaint: got None, wanted [['gout']]
- tests_ordered: missed creatinine

