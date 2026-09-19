"""Post-success step: explain a compiled proof, grounded in Lean's own goal states.

1. Instrument the proof: insert `trace_state` before every tactic so Lean reports the
   goal at each step (as `info` diagnostics).
2. Run `#print axioms` to show what the proof ultimately rests on.
3. Hand statement + proof + goal states + axioms to an LLM to write the walkthrough.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .agents import LEAN_CONTEXT
from .checker import LeanChecker, assemble, parse_diagnostics
from .llm import LLMClient

STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
_CASE_RE = re.compile(r"^(\s*\|[^=]*=>)\s*(\S.*)$")   # `| succ k ih => tactic`
_THEOREM_NAME_RE = re.compile(r"^\s*(?:theorem|lemma)\s+(\S+)")


@dataclass
class StepState:
    line: str
    goal: str | None


def instrument(proof_body: str) -> tuple[str, list[str]]:
    """Return (instrumented body, original tactic lines in order of trace_state insertion)."""
    out: list[str] = []
    tactics: list[str] = []
    for raw in proof_body.strip("\n").splitlines():
        stripped = raw.strip()
        indent = raw[: len(raw) - len(raw.lstrip())]
        if not stripped or stripped.startswith("--"):
            out.append(raw)
            continue
        m = _CASE_RE.match(raw)
        if m:
            head, tactic = m.group(1), m.group(2)
            out.append(head)
            out.append(indent + "  trace_state")
            out.append(indent + "  " + tactic)
            tactics.append(tactic)
            continue
        if stripped.startswith("|") or stripped.endswith("with") or stripped.startswith(("·", ".")) and len(stripped) == 1:
            out.append(raw)          # structural line, not a tactic on its own
            continue
        if stripped.endswith("with"):
            out.append(raw)
            continue
        out.append(indent + "trace_state")
        out.append(raw)
        tactics.append(stripped)
    return "\n".join(out), tactics


def theorem_name(statement: str) -> str | None:
    m = _THEOREM_NAME_RE.match(statement)
    return m.group(1) if m else None


class ProofInspector:
    """Runs Lean to collect goal states and axioms for a finished proof."""

    def __init__(self, checker: LeanChecker):
        self.checker = checker

    def goal_states(self, header: str, statement: str, proof_body: str, aux: str = "") -> list[StepState]:
        """Compile an instrumented copy with `lean --json` so info messages carry positions."""
        import json, subprocess
        body, tactics = instrument(proof_body)
        src = assemble(header, statement, body, aux)
        path = self.checker.cfg.lean_src_dir / "Explain_trace.lean"
        path.write_text(src)
        try:
            proc = subprocess.run(["lake", "env", "lean", "--json", str(path)], cwd=self.checker.cfg.lean_project,
                                  env=self.checker.env, capture_output=True, text=True,
                                  timeout=self.checker.cfg.lean_timeout_s)
        finally:
            path.unlink(missing_ok=True)
        msgs = []
        for line in (proc.stdout + proc.stderr).splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                msgs.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        if any(m.get("severity") == "error" for m in msgs):
            return [StepState(t, None) for t in tactics]
        infos = sorted((m for m in msgs if m.get("severity") == "information"),
                       key=lambda m: (m["pos"]["line"], m["pos"]["column"]))
        if len(infos) != len(tactics):
            return [StepState(t, None) for t in tactics]
        return [StepState(t, m["data"].strip()) for t, m in zip(tactics, infos)]

    def axioms(self, header: str, statement: str, proof_body: str, aux: str = "") -> tuple[list[str], str]:
        name = theorem_name(statement)
        if not name:
            return [], "could not determine theorem name"
        src = assemble(header, statement, proof_body, aux) + f"\n#print axioms {name}\n"
        path = self.checker.cfg.lean_src_dir / "Axioms_check.lean"
        path.write_text(src)
        import subprocess
        proc = subprocess.run(["lake", "env", "lean", str(path)], cwd=self.checker.cfg.lean_project,
                              env=self.checker.env, capture_output=True, text=True, timeout=self.checker.cfg.lean_timeout_s)
        path.unlink(missing_ok=True)
        out = proc.stdout + proc.stderr
        m = re.search(r"depends on axioms: \[(.*?)\]", out, re.S)
        if m:
            return [a.strip() for a in m.group(1).split(",") if a.strip()], out.strip()
        if "does not depend on any axioms" in out:
            return [], out.strip()
        return [], out.strip()


class Explainer:
    SYSTEM = LEAN_CONTEXT + """
Your job: explain a *verified* Lean 4 proof to someone who knows the mathematics but is new to Lean.
You will be given the theorem, the proof, the exact goal state Lean reported before each tactic,
and the axioms the proof depends on. Ground every claim in that data; do not speculate about what
a tactic did if the goal states show otherwise.

Write Markdown with these sections:
1. **Statement in plain language** — restate the theorem informally; call out indexing conventions
   (e.g. `Finset.range n` is {0,...,n-1}) and anything a reader should double-check against their intent.
2. **Proof strategy** — one or two sentences.
3. **Line by line** — if there are helper lemmas, first one short paragraph per helper saying what it states and why it is needed. Then a bullet per tactic line of the main proof. For each: what the goal was (paraphrase the Lean goal
   in math notation), what the tactic does in general, and what it did here. Quote the tactic in backticks.
4. **Why you can trust this** — that Lean compiled it with no errors and no `sorry`, and what the
   listed axioms are (propext, Classical.choice, Quot.sound are Mathlib's standard three).
Be concrete and concise. No filler."""

    def __init__(self, llm: LLMClient, model: str | None = None):
        self.llm, self.model = llm, model

    def run(self, statement: str, proof_body: str, states: list[StepState], axioms: list[str], aux: str = "") -> str:
        trace = []
        for i, s in enumerate(states, 1):
            goal = s.goal if s.goal is not None else "(goal state unavailable)"
            trace.append(f"Step {i}: tactic `{s.line}`\nGoal before this tactic:\n{goal}")
        aux_part = f"Helper declarations proved first:\n```lean\n{aux}\n```\n\n" if aux.strip() else ""
        user = (
            aux_part + f"Theorem:\n```lean\n{statement} := by\n{proof_body}\n```\n\n"
            f"Goal states reported by Lean:\n\n" + "\n\n".join(trace) +
            f"\n\nAxioms the theorem depends on: {axioms or ['(none)']}"
        )
        return self.llm.complete(self.SYSTEM, user, model=self.model, max_tokens=3000).text.strip()
