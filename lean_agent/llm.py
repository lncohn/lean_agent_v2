"""LLM client abstraction. Two backends behind one `complete()` call.

- AnthropicClient: the Anthropic Python SDK, authenticated with ANTHROPIC_API_KEY
  (or ANTHROPIC_AUTH_TOKEN for a proxy that takes a bearer token). Supports the probe tool loop.
- ClaudeCLIClient: shells out to `claude -p`. No credentials needed; slower per call.
"""
from __future__ import annotations

import os
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    tool_calls: list = None  # [{"name", "input", "output"}] for tool-using completions


class LLMClient(ABC):
    """Subclasses implement `_complete`; `complete` wraps it and records usage in `self.calls`."""

    supports_tools = False

    def __init__(self):
        self.calls: list[dict] = []
        self.on_call = None  # optional callback(call_dict), e.g. a BudgetTracker

    def _record(self, system, user, resp: LLMResponse, t0: float):
        self.calls.append({
            "model": resp.model, "input_tokens": resp.input_tokens, "output_tokens": resp.output_tokens,
            "latency_s": round(time.time() - t0, 2), "prompt_chars": len(system) + len(user),
            "system": system, "user": user, "response": resp.text, "tool_calls": resp.tool_calls or [],
        })
        if self.on_call:
            self.on_call(self.calls[-1])

    def complete_with_tools(self, system, user, tools, handler, *, model=None, max_tokens=4096, max_rounds=6) -> LLMResponse:
        raise NotImplementedError("this backend does not support tools")

    @abstractmethod
    def _complete(self, system: str, user: str, *, model: str | None, max_tokens: int) -> LLMResponse:
        ...

    def complete(self, system: str, user: str, *, model: str | None = None, max_tokens: int = 4096) -> LLMResponse:
        t0 = time.time()
        resp = self._complete(system, user, model=model, max_tokens=max_tokens)
        self._record(system, user, resp, t0)
        return resp


class AnthropicClient(LLMClient):
    supports_tools = True

    def __init__(self, default_model: str, base_url: str | None = None):
        super().__init__()
        import anthropic  # local import so the CLI backend works without the SDK

        self._anthropic = anthropic
        self.default_model = default_model
        kwargs = {"max_retries": 3}
        if base_url:
            kwargs["base_url"] = base_url
        if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("ANTHROPIC_AUTH_TOKEN"):
            raise RuntimeError("Set ANTHROPIC_API_KEY (or ANTHROPIC_AUTH_TOKEN) to use the anthropic backend, "
                               "or set LEAN_AGENT_BACKEND=claude_cli to go through `claude -p`.")
        self._client = anthropic.Anthropic(**kwargs)

    def _complete(self, system, user, *, model=None, max_tokens=4096) -> LLMResponse:
        model = model or self.default_model
        resp = self._client.messages.create(
            model=model, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        return LLMResponse(text, model, resp.usage.input_tokens, resp.usage.output_tokens)


    def complete_with_tools(self, system, user, tools, handler, *, model=None, max_tokens=4096, max_rounds=6) -> LLMResponse:
        """Agentic loop: let the model call tools up to `max_rounds` times, then force a final answer."""
        model = model or self.default_model
        t0 = time.time()
        messages = [{"role": "user", "content": user}]
        tool_log: list[dict] = []
        in_tok = out_tok = 0
        final_text = ""
        for round_ in range(max_rounds + 1):
            use_tools = round_ < max_rounds and len(tool_log) < max_rounds
            kwargs = dict(model=model, max_tokens=max_tokens, system=system, messages=messages)
            if use_tools:
                kwargs["tools"] = tools
            resp = self._create(**kwargs)
            in_tok += resp.usage.input_tokens; out_tok += resp.usage.output_tokens
            if resp.stop_reason == "max_tokens":
                # Cut off mid-answer. Ask for just the final code block, with no tools, and stop.
                messages.append({"role": "assistant", "content": [b.model_dump() for b in resp.content if b.type == "text"] or [{"type": "text", "text": "..."}]})
                messages.append({"role": "user", "content": "Your previous message was cut off by the length limit. Reply with ONLY the complete final lean code block (helper lemmas + theorem + proof), nothing else. If the proof is too long, shorten it by moving pieces into helper lemmas."})
                resp = self._create(model=model, max_tokens=max_tokens, system=system, messages=messages)
                in_tok += resp.usage.input_tokens; out_tok += resp.usage.output_tokens
                final_text = "".join(b.text for b in resp.content if b.type == "text")
                break
            text = "".join(b.text for b in resp.content if b.type == "text")
            tool_uses = [b for b in resp.content if b.type == "tool_use"]
            if text:
                final_text = text
            if not tool_uses or not use_tools:
                break
            messages.append({"role": "assistant", "content": [b.model_dump() for b in resp.content]})
            results = []
            for tu in tool_uses:
                out = handler(tu.name, tu.input)
                tool_log.append({"name": tu.name, "input": tu.input, "output": out})
                results.append({"type": "tool_result", "tool_use_id": tu.id, "content": out})
            if round_ == max_rounds - 1 or len(tool_log) >= max_rounds:
                results.append({"type": "text", "text": "You have no probes left. Submit your final answer now as a single lean code block."})
            else:
                results.append({"type": "text", "text": f"{max_rounds - len(tool_log)} probe(s) left."})
            messages.append({"role": "user", "content": results})
        r = LLMResponse(final_text, model, in_tok, out_tok, tool_log)
        self._record(system, user, r, t0)
        return r

    def _create(self, **kwargs):
        return self._client.messages.create(**kwargs)


class ClaudeCLIClient(LLMClient):
    def __init__(self, default_model: str | None = None, binary: str = "claude"):
        super().__init__()
        self.default_model = default_model
        self.binary = binary

    def _complete(self, system, user, *, model=None, max_tokens=4096) -> LLMResponse:
        cmd = [self.binary, "-p", "--output-format", "text"]
        if system:
            cmd += ["--append-system-prompt", system]
        if model or self.default_model:
            cmd += ["--model", model or self.default_model]
        out = subprocess.run(cmd, input=user, capture_output=True, text=True, timeout=600)
        if out.returncode != 0:
            raise RuntimeError(f"claude -p failed ({out.returncode}): {out.stderr[-2000:]}")
        return LLMResponse(out.stdout.strip(), model or self.default_model or "claude-cli")


def make_client(cfg) -> LLMClient:
    if cfg.backend == "anthropic":
        return AnthropicClient(cfg.model, cfg.base_url)
    if cfg.backend == "claude_cli":
        return ClaudeCLIClient(None)
    raise ValueError(f"unknown backend {cfg.backend!r}")
