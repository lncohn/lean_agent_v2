"""The LLM roles. Each is a thin, prompt-focused wrapper over LLMClient."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from .llm import LLMClient

LEAN_CONTEXT = """You are working in Lean 4 with Mathlib (Lean v4.35, current Mathlib master).
Key syntax reminders:
- Big operators: `∑ i ∈ Finset.range n, f i` (note `∈`, not `in`).
- Tactics: induction ... with | zero => ... | succ k ih => ..., simp, simp only [...], rw [...], ring, omega,
  nlinarith, norm_num, decide, exact?, apply?, refine ⟨_, _⟩, obtain ⟨x, hx⟩ := ..., constructor, ext, funext.
- `exact?` and `apply?` search Mathlib for a closing lemma; `#check @name` shows a lemma's full type;
  `#synth Cls X` checks whether a type-class instance exists.
- Never use sorry, admit, axiom, or native_decide in a submitted proof.
"""

PROBE_TOOL = {
    "name": "lean_probe",
    "description": (
        "Run a Lean 4 snippet (with `import Mathlib` already at the top) and return Lean's output. "
        "Use it to check lemma names and types (`#check @Foo.bar`), find instances (`#synth SimplyConnectedSpace ℝ`), "
        "search for lemmas (`example : <goal> := by exact?`), or test a partial proof with `sorry` placeholders "
        "to see the remaining goals. For CONCRETE ARITHMETIC (matrix entries, images of vectors, checking a candidate "
        "preimage) use `#eval`, e.g. `#eval (d1mat.mulVec ![1,0,0,...] : Fin 10 → ℤ)` or `#eval List.ofFn fun j => ...` -- never guess "
        "numbers by hand. `#eval` is for pure values only: IO, run_cmd and metaprogramming are rejected. "
        "Each probe costs ~10s of Lean time, so batch several commands in one call."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"code": {"type": "string", "description": "Lean 4 code to run after `import Mathlib`."}},
        "required": ["code"],
    },
}


def _extract_code(text: str) -> str:
    m = re.findall(r"```(?:lean4?|lean)?\s*\n(.*?)```", text, re.S)
    return (m[-1] if m else text).strip()


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {"category": "unknown", "diagnosis": text.strip(), "suggestion": ""}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"category": "unknown", "diagnosis": text.strip(), "suggestion": ""}


def _norm(s: str) -> str:
    return " ".join(s.split())


def theorem_name(statement: str) -> str:
    m = re.match(r"\s*(?:theorem|lemma)\s+(\S+)", statement)
    return m.group(1) if m else ""


def split_submission(code: str, statement: str) -> tuple[str, str, str | None]:
    """Split prover output into (aux, proof_body, error).

    Accepts either a bare tactic block, or helper declarations followed by the full theorem
    (statement copied verbatim, then `:= by`, then tactics). The statement must match ours."""
    name = theorem_name(statement)
    pat = re.compile(rf"^(theorem|lemma)\s+{re.escape(name)}\b", re.M) if name else None
    m = pat.search(code) if pat else None
    if not m:
        if re.search(r"^(theorem|lemma)\s", code, re.M):
            return "", "", f"submission declares a theorem but not one named `{name}`"
        return "", code.strip(), None  # bare tactic block
    aux = code[: m.start()].strip("\n")
    rest = code[m.start():]
    sm = re.match(r"(.*?)\s*:=\s*by\b[ \t]*\n?(.*)\Z", rest, re.S)
    if sm:
        stmt_text, body = sm.group(1), sm.group(2)
    else:
        # term-mode proof `:= <term>`: wrap it as `exact <term>` so the checker's tactic-block model still applies
        tm = re.match(r"(.*?)\s*:=\s*(\S.*)\Z", rest, re.S)
        if not tm:
            return aux, "", "could not find `:=` after the theorem statement"
        stmt_text, term = tm.group(1), tm.group(2).strip()
        body = "exact " + ("\n  ".join(term.splitlines()) if "\n" in term else term)
    if _norm(stmt_text) != _norm(statement):
        return aux, "", (f"theorem statement was altered. Expected exactly:\n{statement}\nGot:\n{stmt_text.strip()}")
    # dedent body
    lines = body.rstrip("\n").splitlines()
    indent = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
    body = "\n".join(l[indent:] if len(l) >= indent else l for l in lines)
    return aux, body, None


@dataclass
class Attempt:
    index: int
    proof: str
    check_summary: str
    ok: bool
    aux: str = ""
    diagnosis: dict | None = None
    probes: list[dict] = field(default_factory=list)

    def render_code(self) -> str:
        return (self.aux + "\n\n" if self.aux else "") + self.proof


class Formalizer:
    SYSTEM = LEAN_CONTEXT + """
Your job: translate an informal mathematical statement into a single Lean 4 theorem *statement*.
Output ONLY a lean code block containing exactly one declaration of the form:
theorem <name> <binders> : <proposition>
Do NOT include `:= by` or any proof. Use ℕ for natural numbers unless told otherwise.
Choose the most faithful, idiomatic Mathlib phrasing."""

    def __init__(self, llm: LLMClient, model: str | None = None):
        self.llm, self.model = llm, model

    def run(self, informal: str, feedback: str | None = None) -> str:
        user = f"Informal statement:\n{informal}"
        if feedback:
            user += f"\n\nYour previous statement failed to compile:\n{feedback}\nFix it."
        text = self.llm.complete(self.SYSTEM, user, model=self.model).text
        stmt = _extract_code(text).strip()
        return re.sub(r"\s*:=\s*by.*$", "", stmt, flags=re.S).strip()


class Prover:
    SYSTEM = LEAN_CONTEXT + """
Your job: prove a given Lean 4 theorem.

You may first call the `lean_probe` tool to check lemma names, types, instances, or to test a partial
proof with `sorry` placeholders and read the remaining goals. Probe before guessing at Mathlib names.
You have a limited number of probes; the number remaining is stated in each request.

When ready, output your FINAL submission as ONE lean code block (no other code blocks after it) with:
  1. optional helper lemmas/defs (each fully proved, no sorry), then
  2. the main theorem with its statement copied EXACTLY as given, then `:= by`, then the tactic proof.
The file already begins with `import Mathlib`; do not repeat imports. You may include `open ...` lines
in the helper block. Do not change the theorem statement in any way.
If given previous failed attempts and a critic's diagnosis, change strategy accordingly; do not resubmit
a trivial variation of something that already failed.
If Lean reports a (deterministic) timeout / maximum heartbeats, put `set_option maxHeartbeats 1000000` on its own line
at the top of the helper block, and split heavy finite computations (matrix entries, `decide`, big `simp`) into
several small helper lemmas rather than one big tactic call."""

    def __init__(self, llm: LLMClient, model: str | None = None, probe=None, max_probes: int = 6):
        self.llm, self.model, self.probe, self.max_probes = llm, model, probe, max_probes

    def run(self, header: str, statement: str, history: list[Attempt], constraints: str = "") -> tuple[str, str, str | None, list[dict]]:
        parts = [f"File header (already present):\n```lean\n{header}\n```",
                 f"Theorem to prove (copy the statement verbatim in your submission):\n```lean\n{statement} := by\n  -- your tactics here\n```"]
        if constraints:
            parts.append(f"Constraints: {constraints}")
        if history:
            hist = []
            for a in history:
                block = f"--- Attempt {a.index} ---\n```lean\n{a.render_code()}\n```\nLean output:\n{a.check_summary}"
                if a.diagnosis:
                    block += f"\nCritic: [{a.diagnosis.get('category')}] {a.diagnosis.get('diagnosis')}\nSuggestion: {a.diagnosis.get('suggestion')}"
                hist.append(block)
            parts.append("Previous failed attempts (most recent last):\n" + "\n\n".join(hist))
            parts.append("Write a NEW submission that addresses the critic's most recent suggestion.")
        if self.probe:
            parts.append(f"You have {self.max_probes} lean_probe calls available for this attempt.")
        user = "\n\n".join(parts)

        probes: list[dict] = []
        if self.probe and self.llm.supports_tools:
            def handler(name: str, inp: dict) -> str:
                out = self.probe(inp.get("code", ""))
                probes.append({"code": inp.get("code", ""), "output": out})
                return out
            resp = self.llm.complete_with_tools(self.SYSTEM, user, [PROBE_TOOL], handler, model=self.model,
                                                max_tokens=16000, max_rounds=self.max_probes)
        else:
            resp = self.llm.complete(self.SYSTEM, user, model=self.model, max_tokens=16000)
        aux, body, err = split_submission(_extract_code(resp.text), statement)
        return aux, body, err, probes


class Critic:
    SYSTEM = LEAN_CONTEXT + """
Your job: read a failed Lean 4 proof attempt and its compiler output, then diagnose WHY it failed
and what to change. Each error comes with `↳ source:` quoting the exact offending line and its line number within
the submission; anchor your diagnosis on that quoted line (e.g. for a parse error, count its parentheses), and if the
same error recurred in earlier attempts say so explicitly and insist the prover rewrite that line from scratch.
Be concrete and short. Classify the failure as one of:
  unknown_identifier | type_mismatch | unsolved_goals | wrong_lemma_form | syntax | tactic_failed | timeout | guard | statement_altered | other
Respond with ONLY a JSON object:
{"category": "...", "diagnosis": "one or two sentences on the root cause",
 "suggestion": "a specific, different tactic strategy or lemma to try next; if a name was unknown, suggest probing with #check / exact?"}
If the same kind of error has recurred across attempts, say so and recommend a materially different approach."""

    def __init__(self, llm: LLMClient, model: str | None = None):
        self.llm, self.model = llm, model

    def run(self, statement: str, attempt: Attempt, history: list[Attempt]) -> dict:
        prior = "\n".join(f"Attempt {a.index}: [{(a.diagnosis or {}).get('category', '?')}] {a.check_summary.splitlines()[0] if a.check_summary else ''}" for a in history)
        probes = ""
        if attempt.probes:
            probes = "\n\nProbes the prover ran before submitting:\n" + "\n".join(
                f"```lean\n{p['code'].strip()}\n```\n→ {p['output'][:800]}" for p in attempt.probes)
        user = (
            f"Theorem:\n```lean\n{statement}\n```\n\nFailed submission (attempt {attempt.index}):\n```lean\n{attempt.render_code()}\n```\n\n"
            f"Lean output:\n{attempt.check_summary}{probes}\n\nEarlier attempts summary:\n{prior or '(none)'}"
        )
        return _extract_json(self.llm.complete(self.SYSTEM, user, model=self.model, max_tokens=1024).text)
