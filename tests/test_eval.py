import json
from pathlib import Path

from jsonschema import Draft202012Validator

from notevals.extract import extract, parse_json
from notevals.providers import MockProvider, expected_to_note
from notevals.report import compare_report
from notevals.run import run_eval
from notevals.score import dose_ok, name_matches, score_note

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema" / "visit_note.schema.json").read_text())
CASES = json.loads((ROOT / "data" / "cases.json").read_text())
HELDOUT = json.loads((ROOT / "data" / "heldout.json").read_text())
ALL = CASES + HELDOUT


def test_answer_keys_produce_schema_valid_notes():
    v = Draft202012Validator(SCHEMA)
    for case in ALL:
        errors = list(v.iter_errors(expected_to_note(case["expected"])))
        assert not errors, (case["id"], errors)


def test_case_ids_unique():
    ids = [c["id"] for c in ALL]
    assert len(ids) == len(set(ids))


def test_perfect_note_scores_one():
    for case in ALL:
        sc = score_note(expected_to_note(case["expected"]), case["expected"])
        assert sc["overall"] == 1.0, (case["id"], sc["failures"])
        assert sc["unsupported"] == [] and sc["critical"] == []


def test_name_matching():
    assert name_matches("Tylenol", {"name": "acetaminophen", "aliases": ["tylenol"]})
    assert name_matches("right knee X-ray", {"name": "knee x-ray", "aliases": ["x-ray"]})
    assert not name_matches("fatigue", {"name": "fever"})


def test_dose_matching():
    assert dose_ok("500mg twice daily", "500 mg twice a day")
    assert not dose_ok("10 mg", "20 mg once daily")
    assert dose_ok("500 mg every six hours", "500 mg every 6 hours as needed")
    assert dose_ok(None, None)
    assert not dose_ok("1 tube", None)


def test_errors_are_caught():
    case = next(c for c in CASES if c["id"].startswith("02"))
    note = expected_to_note(case["expected"])
    note["medications"][0]["action"] = "continued"  # lisinopril was changed
    note["medications"].append({"name": "metformin", "dose": None, "action": "started"})
    note["follow_up"]["interval_days"] = 30
    sc = score_note(note, case["expected"])
    assert sc["fields"]["med_action"] == 0.5
    assert sc["fields"]["follow_up_interval"] == 0.0
    assert "medication: metformin (started)" in sc["unsupported"]
    assert sc["overall"] < 1.0
    assert len(sc["critical"]) == 2  # wrong action + added medication


def test_parse_json_handles_fences():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json('Here you go: {"a": 1} thanks') == {"a": 1}


def test_retry_recovers_from_invalid_json():
    p = MockProvider("noisy")
    case = next(c for c in CASES if c["id"].startswith("07"))
    p.case = case
    ex = extract(p, "sys", case["transcript"], SCHEMA, max_attempts=2)
    assert ex.valid and ex.attempts == 2


def test_end_to_end_mock_runs_and_compare(tmp_path):
    common = dict(
        prompt="v2", mode="native", cases_path=ROOT / "data" / "cases.json",
        schema_path=ROOT / "schema" / "visit_note.schema.json", out_dir=tmp_path, quiet=True,
    )
    a = run_eval("mock", "noisy", run_name="noisy", **common)
    b = run_eval("mock", "perfect", run_name="perfect", **common)
    sa = json.loads((a / "summary.json").read_text())
    sb = json.loads((b / "summary.json").read_text())
    assert sb["overall"] == 1.0 and sa["overall"] < 1.0
    assert sb["critical_errors"] == 0 and sa["critical_errors"] > 0
    assert "Improved cases" in compare_report(a, b)
    assert (a / "report.md").read_text().startswith("# Run noisy")


def test_misnamed_drug_is_one_critical_error():
    case = next(c for c in CASES if c["id"].startswith("06"))
    note = expected_to_note(case["expected"])
    note["medications"][1]["name"] = "jar dance"
    sc = score_note(note, case["expected"])
    assert len(sc["critical"]) == 1 and "wrong name for empagliflozin" in sc["critical"][0]


def test_rescore_matches_original(tmp_path):
    from notevals.run import rescore
    run = run_eval("mock", "noisy", prompt="v2", mode="native", cases_path=ROOT / "data" / "cases.json",
                   schema_path=ROOT / "schema" / "visit_note.schema.json", out_dir=tmp_path,
                   run_name="r", quiet=True)
    before = json.loads((run / "summary.json").read_text())
    after = rescore(run, ROOT / "data" / "cases.json", quiet=True)
    assert after["overall"] == before["overall"]


def test_heldout_examples_not_in_prompts():
    """Held-out transcripts must not leak into the prompts used for tuning."""
    prompts = " ".join(p.read_text().lower() for p in (ROOT / "prompts").glob("*.md"))
    for phrase in ["amlo dipping", "loss art an", "orthopedics", "codeine", "allopurinol", "rosuvastatin 5"]:
        assert phrase not in prompts, phrase
