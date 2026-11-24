"""Call a provider, parse the JSON, validate it against the schema, retry once."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from jsonschema import Draft202012Validator

from .providers import Provider

FENCE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL)


@dataclass
class Extraction:
    note: dict | None
    valid: bool
    attempts: int
    errors: list[str] = field(default_factory=list)
    raw: list[str] = field(default_factory=list)
    latency_s: float = 0.0
    usage: dict = field(default_factory=dict)


def parse_json(text: str) -> dict:
    text = text.strip()
    m = FENCE.match(text)
    if m:
        text = m.group(1)
    if not text.startswith("{"):
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            text = text[start : end + 1]
    return json.loads(text)


def validation_errors(note, validator: Draft202012Validator) -> list[str]:
    return [
        f"{'/'.join(str(p) for p in e.absolute_path) or '(root)'}: {e.message}"
        for e in sorted(validator.iter_errors(note), key=lambda e: list(e.absolute_path))
    ]


def extract(
    provider: Provider,
    system: str,
    transcript: str,
    schema: dict,
    mode: str = "native",
    max_attempts: int = 2,
) -> Extraction:
    validator = Draft202012Validator(schema)
    user = f"Visit transcript:\n\n{transcript}"
    result = Extraction(note=None, valid=False, attempts=0)

    for attempt in range(1, max_attempts + 1):
        result.attempts = attempt
        comp = provider.complete(system, user, schema, mode)
        result.raw.append(comp.text)
        result.latency_s += comp.latency_s
        for k, v in comp.usage.items():
            result.usage[k] = result.usage.get(k, 0) + (v or 0)

        try:
            note = parse_json(comp.text)
            errors = validation_errors(note, validator)
        except (json.JSONDecodeError, ValueError) as e:
            note, errors = None, [f"not valid JSON: {e}"]

        result.errors = errors
        if not errors:
            result.note, result.valid = note, True
            return result
        result.note = note if isinstance(note, dict) else None

        # Retry with the validation errors appended to the request.
        user = (
            f"Visit transcript:\n\n{transcript}\n\n"
            "Your previous answer did not match the schema:\n- "
            + "\n- ".join(errors[:10])
            + "\nReturn a corrected note."
        )
    return result
