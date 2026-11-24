"""Model providers.

Each provider turns (system prompt, user message, schema, mode) into a raw JSON
string. Modes:

- "native": the provider's own way of forcing structure (JSON-schema response
  format for LM Studio and OpenAI; a forced tool call for Claude), with the
  schema also pasted into the prompt so the model sees the field descriptions.
- "native-bare": the same enforcement without the schema in the prompt. Some
  servers (LM Studio, it appears) only use the schema to constrain decoding, so
  the model never sees what the fields and choices mean. Kept as a variant
  because that difference turned out to matter (see FINDINGS.md).
- "tool": a forced function/tool call on every provider, schema also in the
  prompt. (LM Studio support depends on the loaded model.)
- "prompt": no enforcement. The schema is pasted into the prompt and the model
  is asked to answer with JSON. The baseline.
"""

from __future__ import annotations

import copy
import json
import os
import time
from dataclasses import dataclass, field

TOOL_NAME = "record_visit_note"
TOOL_DESCRIPTION = "Record the structured note for this visit."


@dataclass
class Completion:
    text: str
    latency_s: float
    usage: dict = field(default_factory=dict)


def api_schema(schema: dict) -> dict:
    """Schema copy without keys some APIs reject at the top level."""
    s = copy.deepcopy(schema)
    for key in ("$schema", "title"):
        s.pop(key, None)
    return s


def prompt_with_schema(system: str, schema: dict) -> str:
    return (
        f"{system}\n\nThe JSON must match this JSON Schema exactly:\n"
        f"```json\n{json.dumps(api_schema(schema), indent=2)}\n```"
    )


class Provider:
    name = "base"

    def __init__(self, model: str | None = None, temperature: float | None = 0.0,
                 max_tokens: int = 2048, timeout: float = 180.0, no_think: bool = False):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.no_think = no_think

    def user_text(self, user: str) -> str:
        # Qwen3-style soft switch that turns off the long hidden reasoning section.
        return f"{user}\n\n/no_think" if self.no_think else user

    def complete(self, system: str, user: str, schema: dict, mode: str) -> Completion:
        raise NotImplementedError


# --------------------------------------------------------------------------- #
# OpenAI-compatible (OpenAI and LM Studio)
# --------------------------------------------------------------------------- #


class OpenAICompatible(Provider):
    name = "openai"

    def __init__(self, model=None, temperature=0.0, base_url=None, api_key=None, **kw):
        super().__init__(model, temperature, **kw)
        try:
            from openai import OpenAI
        except ImportError as e:  # pragma: no cover
            raise SystemExit("Install the openai package: pip install openai") from e
        self.client = OpenAI(base_url=base_url, api_key=api_key, timeout=self.timeout, max_retries=0)

    def _create(self, **kwargs):
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        try:
            return self.client.chat.completions.create(**kwargs)
        except Exception as e:  # some models reject a custom temperature
            if "temperature" in str(e).lower() and "temperature" in kwargs:
                kwargs.pop("temperature")
                return self.client.chat.completions.create(**kwargs)
            raise

    def complete(self, system, user, schema, mode):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": self.user_text(user)},
        ]
        kwargs: dict = {"model": self.model, "messages": messages, "max_tokens": self.max_tokens}
        if mode in ("native", "tool", "prompt"):
            messages[0]["content"] = prompt_with_schema(system, schema)
        if mode in ("native", "native-bare"):
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "visit_note", "strict": True, "schema": api_schema(schema)},
            }
        elif mode == "tool":
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": TOOL_NAME,
                        "description": TOOL_DESCRIPTION,
                        "parameters": api_schema(schema),
                        "strict": True,
                    },
                }
            ]
            kwargs["tool_choice"] = {"type": "function", "function": {"name": TOOL_NAME}}
        elif mode == "prompt":
            pass
        else:
            raise ValueError(f"unknown mode {mode!r}")

        t0 = time.perf_counter()
        resp = self._create(**kwargs)
        latency = time.perf_counter() - t0
        msg = resp.choices[0].message
        if resp.choices[0].finish_reason == "length":
            print(f"    warning: hit the {self.max_tokens}-token output cap (raise --max-tokens, or try --no-think)")
        if mode == "tool" and msg.tool_calls:
            text = msg.tool_calls[0].function.arguments
        else:
            text = msg.content or ""
        usage = {}
        if resp.usage:
            usage = {"input_tokens": resp.usage.prompt_tokens, "output_tokens": resp.usage.completion_tokens}
        return Completion(text=text, latency_s=latency, usage=usage)


class OpenAIProvider(OpenAICompatible):
    name = "openai"

    def __init__(self, model=None, temperature=0.0, **kw):
        model = model or os.environ.get("OPENAI_MODEL")
        if not model:
            raise SystemExit("Set --model or OPENAI_MODEL for the openai provider.")
        super().__init__(model, temperature, **kw)


class LMStudioProvider(OpenAICompatible):
    name = "lmstudio"

    def __init__(self, model=None, temperature=0.0, **kw):
        base_url = os.environ.get("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
        super().__init__(model, temperature, base_url=base_url, api_key="lm-studio", **kw)
        self.model = model or os.environ.get("LMSTUDIO_MODEL") or self._first_loaded_model(base_url)

    def _first_loaded_model(self, base_url: str) -> str:
        try:
            models = self.client.models.list().data
        except Exception as e:
            cause = e.__cause__ or e
            raise SystemExit(
                f"Could not reach LM Studio at {base_url} ({type(cause).__name__}: {cause}).\n"
                "Check that its local server is running (Developer tab), that the URL includes "
                "the port (usually :1234) and ends in /v1, and, from WSL2, that you use the "
                "Windows host's IP with 'Serve on Local Network' enabled."
            ) from e
        if not models:
            raise SystemExit("LM Studio has no model loaded. Load one, or pass --model.")
        return models[0].id


# --------------------------------------------------------------------------- #
# Anthropic (Claude)
# --------------------------------------------------------------------------- #


class AnthropicProvider(Provider):
    name = "anthropic"
    default_model = "claude-haiku-5-5"

    def __init__(self, model=None, temperature=0.0, **kw):
        kw["no_think"] = False  # not applicable
        super().__init__(model or os.environ.get("ANTHROPIC_MODEL") or self.default_model, temperature, **kw)
        try:
            import anthropic
        except ImportError as e:  # pragma: no cover
            raise SystemExit("Install the anthropic package: pip install anthropic") from e
        self.client = anthropic.Anthropic(timeout=self.timeout)

    def complete(self, system, user, schema, mode):
        kwargs: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        if mode in ("native", "tool", "prompt"):
            kwargs["system"] = prompt_with_schema(system, schema)
        if mode in ("native", "native-bare", "tool"):
            kwargs["tools"] = [
                {"name": TOOL_NAME, "description": TOOL_DESCRIPTION, "input_schema": api_schema(schema)}
            ]
            kwargs["tool_choice"] = {"type": "tool", "name": TOOL_NAME}
        elif mode == "prompt":
            pass
        else:
            raise ValueError(f"unknown mode {mode!r}")

        t0 = time.perf_counter()
        resp = self.client.messages.create(**kwargs)
        latency = time.perf_counter() - t0
        text = ""
        for block in resp.content:
            if block.type == "tool_use":
                text = json.dumps(block.input)
                break
            if block.type == "text":
                text += block.text
        usage = {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}
        return Completion(text=text, latency_s=latency, usage=usage)


# --------------------------------------------------------------------------- #
# Mock (offline, for tests and dry runs)
# --------------------------------------------------------------------------- #


def expected_to_note(expected: dict) -> dict:
    """Turn an answer key into the note a perfect model would return."""
    def names(items):
        return [i["name"] for i in items if not i.get("optional")]

    groups = expected["chief_complaint"]["keywords"]
    return {
        "chief_complaint": " ".join(g[0] for g in groups) if groups else None,
        "symptoms": [
            {"name": s["name"], "status": s["status"]} for s in expected["symptoms"] if not s.get("optional")
        ],
        "medications": [
            {"name": m["name"], "dose": m["dose"], "action": m["action"]} for m in expected["medications"]
        ],
        "allergies": {"status": expected["allergies"]["status"], "items": names(expected["allergies"]["items"])},
        "tests_ordered": names(expected["tests_ordered"]),
        "referrals": names(expected["referrals"]),
        "follow_up": dict(expected["follow_up"]),
    }


class MockProvider(Provider):
    """Offline provider.

    model="perfect": returns the answer key.
    model="noisy": returns the answer key with deterministic mistakes, so the
    scoring and report code can be exercised without a real model.
    The mock reads the answer key from `self.case`, set by the runner.
    """

    name = "mock"

    def __init__(self, model=None, temperature=0.0, **kw):
        super().__init__(model or "perfect", temperature, **kw)
        self.case: dict | None = None
        self.calls = 0

    def complete(self, system, user, schema, mode):
        assert self.case is not None, "runner must set MockProvider.case"
        self.calls += 1
        note = expected_to_note(self.case["expected"])
        if self.model == "noisy":
            n = int(self.case["id"][:2])
            if n % 3 == 0 and note["medications"]:
                note["medications"][0]["action"] = "continued"
            if n % 4 == 0:
                note["symptoms"].append({"name": "fatigue", "status": "present"})
            if n % 5 == 0:
                note["follow_up"] = {"status": "not_mentioned", "interval_days": None}
            if n == 7 and self.calls % 2 == 1:
                return Completion(text='{"chief_complaint": "work note"', latency_s=0.0)
        return Completion(text=json.dumps(note), latency_s=0.0)


PROVIDERS = {
    "lmstudio": LMStudioProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "mock": MockProvider,
}


def make_provider(name: str, model: str | None = None, temperature: float | None = 0.0, **kw) -> Provider:
    try:
        cls = PROVIDERS[name]
    except KeyError:
        raise SystemExit(f"Unknown provider {name!r}. Choose from: {', '.join(PROVIDERS)}")
    return cls(model=model, temperature=temperature, **kw)
