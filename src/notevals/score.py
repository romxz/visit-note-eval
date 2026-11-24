"""Field-level scoring of an extracted note against an answer key.

Every field gets a score from 0 to 1, or None when it does not apply to the
case (for example dose accuracy when no medication was matched). A case's
overall score is the mean of its applicable fields. Items the model returned
that match nothing in the answer key are listed as "unsupported".

Averages hide how bad a mistake is, so errors a clinician would most care
about are also counted separately as "critical": a medication added, missed
or given the wrong action, a symptom flipped between present and denied, and
a wrong allergy status.

Matching is deliberately simple and transparent:
- names: lowercase, punctuation stripped; a match if the output equals an
  expected name or alias, or one contains the other as whole words;
- doses: every number in the expected dose must appear in the output dose
  (so "500 mg twice a day" matches "500mg BID"); a null dose must stay null.
"""

from __future__ import annotations

import re
from statistics import mean

FIELDS = [
    "chief_complaint",
    "symptoms",
    "symptom_status",
    "medications",
    "med_action",
    "med_dose",
    "allergy_status",
    "allergy_items",
    "tests_ordered",
    "referrals",
    "follow_up_status",
    "follow_up_interval",
]


CRITICAL_FIELDS = {"medications", "med_action", "symptom_status", "allergy_status"}


def norm(s) -> str:
    s = str(s or "").lower().replace("-", " ")
    s = re.sub(r"[^a-z0-9. ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _contains_words(haystack: str, needle: str) -> bool:
    return bool(needle) and re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", haystack) is not None


def name_matches(out_name: str, exp: dict) -> bool:
    out = norm(out_name)
    if not out:
        return False
    for cand in [exp["name"], *exp.get("aliases", [])]:
        c = norm(cand)
        if out == c or _contains_words(out, c) or _contains_words(c, out):
            return True
    return False


def pair(outputs: list, expected: list, get_name=lambda x: x):
    """Greedy one-to-one matching. Returns (pairs, unmatched_outputs, missed_expected)."""
    used = set()
    pairs, missed = [], []
    for exp in expected:
        hit = next(
            (i for i, o in enumerate(outputs) if i not in used and name_matches(get_name(o), exp)),
            None,
        )
        if hit is None:
            if not exp.get("optional"):
                missed.append(exp)
        else:
            used.add(hit)
            pairs.append((outputs[hit], exp))
    extra = [o for i, o in enumerate(outputs) if i not in used]
    return pairs, extra, missed


def f1(n_pairs: int, n_extra: int, n_missed: int) -> float:
    if n_pairs == 0 and n_extra == 0 and n_missed == 0:
        return 1.0
    precision = n_pairs / (n_pairs + n_extra) if n_pairs + n_extra else 1.0
    recall = n_pairs / (n_pairs + n_missed) if n_pairs + n_missed else 1.0
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


NUMBER_WORDS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
    "seven": "7", "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12",
}


def numbers(s) -> set[str]:
    text = str(s or "").lower()
    text = re.sub(r"\b(" + "|".join(NUMBER_WORDS) + r")\b", lambda m: NUMBER_WORDS[m.group(1)], text)
    return set(re.findall(r"\d+(?:\.\d+)?", text))


def dose_ok(out_dose, exp_dose) -> bool:
    if exp_dose is None:
        return out_dose in (None, "")
    if not out_dose:
        return False
    return numbers(exp_dose) <= numbers(out_dose)


def _ratio(flags: list[bool]):
    return None if not flags else sum(flags) / len(flags)


def score_note(note: dict | None, expected: dict, valid: bool = True) -> dict:
    """Return {"fields": {...}, "overall": float, "unsupported": [...], "failures": [...]}."""
    if not valid or note is None:
        return {
            "fields": {f: 0.0 for f in FIELDS},
            "overall": 0.0,
            "unsupported": [],
            "critical": ["no valid note after retries"],
            "failures": [{"field": "schema", "detail": "no valid note after retries"}],
        }

    fields: dict = {}
    failures: list[dict] = []
    unsupported: list[str] = []
    critical: list[str] = []

    def fail(field, detail):
        failures.append({"field": field, "detail": detail})
        if field in CRITICAL_FIELDS:
            critical.append(f"{field}: {detail}")

    # Chief complaint: every keyword group needs one hit.
    groups = expected["chief_complaint"]["keywords"]
    cc = norm(note.get("chief_complaint"))
    if groups:
        ok = all(any(norm(k) in cc for k in g) for g in groups)
    else:
        ok = not cc
    fields["chief_complaint"] = float(ok)
    if not ok:
        fail("chief_complaint", f"got {note.get('chief_complaint')!r}, wanted {groups}")

    # Symptoms
    pairs, extra, missed = pair(note.get("symptoms", []), expected["symptoms"], lambda o: o["name"])
    fields["symptoms"] = f1(len(pairs), len(extra), len(missed))
    status = [o["status"] == e["status"] for o, e in pairs]
    fields["symptom_status"] = _ratio(status)
    for o in extra:
        unsupported.append(f"symptom: {o['name']} ({o['status']})")
    for e in missed:
        fail("symptoms", f"missed {e['name']} ({e['status']})")
    for o, e in pairs:
        if o["status"] != e["status"]:
            fail("symptom_status", f"{e['name']}: got {o['status']}, wanted {e['status']}")

    # Medications
    pairs, extra, missed = pair(note.get("medications", []), expected["medications"], lambda o: o["name"])
    fields["medications"] = f1(len(pairs), len(extra), len(missed))
    fields["med_action"] = _ratio([o["action"] == e["action"] for o, e in pairs])
    fields["med_dose"] = _ratio([dose_ok(o.get("dose"), e["dose"]) for o, e in pairs])
    # A missed drug and an added drug with the same action and dose are one
    # misnamed drug (e.g. "jar dance" for Jardiance): one critical error, not two.
    misnamed = []
    for e in list(missed):
        o = next((o for o in extra if o["action"] == e["action"] and o not in [m[0] for m in misnamed]
                  and numbers(e["dose"]) == numbers(o.get("dose"))), None)
        if o is not None:
            misnamed.append((o, e))
            missed.remove(e)
    for o, e in misnamed:
        unsupported.append(f"medication: {o['name']} ({o['action']})")
        failures.append({"field": "medications", "detail": f"wrong name for {e['name']}: got {o['name']!r}"})
        critical.append(f"medications: wrong name for {e['name']} (got {o['name']!r})")
    for o in extra:
        if o in [m[0] for m in misnamed]:
            continue
        unsupported.append(f"medication: {o['name']} ({o['action']})")
        critical.append(f"medications: added {o['name']} ({o['action']}), not in transcript")
    for e in missed:
        fail("medications", f"missed {e['name']} ({e['action']})")
    for o, e in pairs:
        if o["action"] != e["action"]:
            fail("med_action", f"{e['name']}: got {o['action']}, wanted {e['action']}")
        if not dose_ok(o.get("dose"), e["dose"]):
            fail("med_dose", f"{e['name']}: got {o.get('dose')!r}, wanted {e['dose']!r}")

    # Allergies
    out_all = note.get("allergies", {}) or {}
    exp_all = expected["allergies"]
    fields["allergy_status"] = float(out_all.get("status") == exp_all["status"])
    if out_all.get("status") != exp_all["status"]:
        fail("allergy_status", f"got {out_all.get('status')}, wanted {exp_all['status']}")
    pairs, extra, missed = pair(out_all.get("items", []), exp_all["items"])
    fields["allergy_items"] = f1(len(pairs), len(extra), len(missed))
    unsupported += [f"allergy: {o}" for o in extra]
    for e in missed:
        fail("allergy_items", f"missed {e['name']}")

    # Tests and referrals
    for key in ("tests_ordered", "referrals"):
        pairs, extra, missed = pair(note.get(key, []), expected[key])
        fields[key] = f1(len(pairs), len(extra), len(missed))
        label = "test" if key == "tests_ordered" else "referral"
        unsupported += [f"{label}: {o}" for o in extra]
        for e in missed:
            fail(key, f"missed {e['name']}")

    # Follow-up
    out_fu = note.get("follow_up", {}) or {}
    exp_fu = expected["follow_up"]
    fields["follow_up_status"] = float(out_fu.get("status") == exp_fu["status"])
    if out_fu.get("status") != exp_fu["status"]:
        fail("follow_up_status", f"got {out_fu.get('status')}, wanted {exp_fu['status']}")
    if exp_fu["interval_days"] is not None:
        ok = out_fu.get("interval_days") == exp_fu["interval_days"]
        fields["follow_up_interval"] = float(ok)
        if not ok:
            fail("follow_up_interval", f"got {out_fu.get('interval_days')}, wanted {exp_fu['interval_days']}")
    else:
        fields["follow_up_interval"] = None

    applicable = [v for v in fields.values() if v is not None]
    return {
        "fields": fields,
        "overall": mean(applicable),
        "unsupported": unsupported,
        "critical": critical,
        "failures": failures,
    }


def aggregate(case_scores: list[dict]) -> dict:
    """Mean per field across cases (ignoring None) and overall mean."""
    out = {}
    for f in FIELDS:
        vals = [c["fields"][f] for c in case_scores if c["fields"].get(f) is not None]
        out[f] = mean(vals) if vals else None
    out["overall"] = mean(c["overall"] for c in case_scores) if case_scores else None
    return out
