"""Project mode: build a multi-lemma Lean development under a dollar budget.

  plan (LLM) -> skeleton compiles? -> for each lemma in dependency order:
      worker = the single-theorem prove loop, with the growing library as header
  lemma exhausts its budget -> replan (LLM) the remaining nodes -> continue
  budget cap reached at any point -> save state, write report, stop (resumable).
"""
from __future__ import annotations

import json
import re
import shutil
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .agents import LEAN_CONTEXT, _extract_json
from .budget import BudgetExceeded, BudgetTracker, call_cost
from .checker import LeanChecker
from .config import Config
from .explainer import STANDARD_AXIOMS
from .llm import make_client
from .orchestrator import Orchestrator, Problem

HEADER = "import Mathlib"


@dataclass
class Node:
    id: str
    kind: str                      # "def" (any fully-given code block) | "lemma" (statement only, to be proved)
    informal: str
    code: str                      # def: full code. lemma: statement without `:= by`
    depends_on: list[str] = field(default_factory=list)
    status: str = "pending"        # pending | proved | failed | blocked
    proof: str | None = None       # lemma tactic body once proved
    aux: str = ""                  # helper declarations the worker added
    attempts: int = 0
    run_dir: str | None = None
    failure_summary: str = ""

    def library_code(self) -> str:
        if self.kind == "def":
            return self.code.strip("\n")
        assert self.proof is not None
        body = "\n".join("  " + l if l.strip() else l for l in self.proof.strip("\n").splitlines())
        return (self.aux.strip("\n") + "\n\n" if self.aux.strip() else "") + f"{self.code.rstrip()} := by\n{body}"


@dataclass
class ProjectSpec:
    name: str
    goal: str                      # what the final theorems must say (informal + any required Lean shapes)
    guidance: str = ""             # design hints for the planner
    max_nodes: int = 30
    attempts_per_lemma: int = 12
    max_replans: int = 3


class Planner:
    SYSTEM = LEAN_CONTEXT + """
You are the architect of a Lean 4 + Mathlib development. You will be given a goal and design guidance.
Produce a dependency-ordered plan as JSON:

{"nodes": [
  {"id": "snake_case_id", "kind": "def", "informal": "...", "code": "<complete Lean code: def/abbrev/notation/open/instance, fully given, NO sorry>", "depends_on": []},
  {"id": "...", "kind": "lemma", "informal": "...", "code": "theorem name (binders) : statement   -- NO `:= by`, NO proof", "depends_on": ["id1", ...]}
]}

Rules:
- Definitions are design decisions: give them completely and concretely. Prefer computable, finite, decidable
  representations (Fin n, explicit Matrix/vectors, ZMod) so that lemmas can be closed by decide/simp/omega/norm_num.
- Lemmas contain ONLY the statement line(s). Each will be proved separately by a prover that sees all earlier nodes.
- Keep each lemma small and independently provable (a few lines of tactics each). Many small lemmas beat one big one.
- Order nodes so every node only references earlier nodes. `depends_on` lists the ids it uses.
- The final node(s) must be exactly the target theorem(s) described in the goal.
- The file starts with `import Mathlib`; do not include imports. You may add `open ...` as a def node.
- Total nodes: at most the stated maximum. Respond with ONLY the JSON object."""

    REPLAN_SUFFIX = """

You are REVISING an existing plan because a lemma could not be proved within its budget. You will see the current
plan, which nodes are already PROVED (keep their id and code byte-identical so the proofs stay valid, unless you must
change a definition they depend on -- then their proofs are discarded and they will be re-proved), the failed lemma,
and a summary of what went wrong. Return the complete revised plan (all nodes) in the same JSON format. Typical
fixes: split the lemma into smaller steps, restate it in a more computable form, add a missing helper lemma, or
change a definition to a representation that is easier to reason about."""

    def __init__(self, llm, model):
        self.llm, self.model = llm, model

    def plan(self, spec: ProjectSpec, feedback: str | None = None) -> list[Node]:
        user = f"GOAL:\n{spec.goal}\n\nDESIGN GUIDANCE:\n{spec.guidance}\n\nMaximum nodes: {spec.max_nodes}."
        if feedback:
            user += f"\n\nYour previous plan's skeleton failed to compile. Fix these errors:\n{feedback}"
        return self._parse(self.llm.complete(self.SYSTEM, user, model=self.model, max_tokens=16000).text)

    def replan(self, spec: ProjectSpec, nodes: list[Node], failed: Node, feedback: str | None = None) -> list[Node]:
        plan_json = json.dumps([{"id": n.id, "kind": n.kind, "informal": n.informal, "code": n.code,
                                 "depends_on": n.depends_on, "status": n.status} for n in nodes], indent=1, ensure_ascii=False)
        user = (f"GOAL:\n{spec.goal}\n\nDESIGN GUIDANCE:\n{spec.guidance}\n\nMaximum nodes: {spec.max_nodes}.\n\n"
                f"CURRENT PLAN (with status):\n{plan_json}\n\nFAILED LEMMA: {failed.id}\n{failed.failure_summary}")
        if feedback:
            user += f"\n\nYour previous revised plan's skeleton failed to compile. Fix these errors:\n{feedback}"
        return self._parse(self.llm.complete(self.SYSTEM + self.REPLAN_SUFFIX, user, model=self.model, max_tokens=16000).text)

    @staticmethod
    def _parse(text: str) -> list[Node]:
        data = _extract_json(text)
        nodes = []
        for n in data.get("nodes", []):
            code = n["code"].strip()
            if n["kind"] == "lemma":
                code = re.sub(r"\s*:=\s*by.*$", "", code, flags=re.S).strip()
            nodes.append(Node(n["id"], n["kind"], n.get("informal", ""), code, list(n.get("depends_on", []))))
        ids = {n.id for n in nodes}
        for n in nodes:
            n.depends_on = [d for d in n.depends_on if d in ids]
        if not nodes:
            raise ValueError("planner returned no nodes:\n" + text[:1000])
        return nodes


class ProjectOrchestrator:
    def __init__(self, spec: ProjectSpec, cfg: Config, budget_usd: float, project_dir: Path, verbose: bool = True):
        self.spec, self.cfg, self.verbose = spec, cfg, verbose
        self.dir = project_dir
        self.dir.mkdir(parents=True, exist_ok=True)
        self.cfg.runs_dir = self.dir / "runs"
        self.cfg.explain = False
        self.cfg.max_attempts = spec.attempts_per_lemma
        self.llm = make_client(cfg)
        self.state_path = self.dir / "state.json"
        self.nodes: list[Node] = []
        self.replans = 0
        spent = self._load_state()
        self.budget = BudgetTracker(budget_usd, spent)
        self.llm.on_call = self._on_call
        self.checker = LeanChecker(cfg)
        self.planner = Planner(self.llm, cfg.model)
        self.events = open(self.dir / "events.jsonl", "a")

    # ---------- bookkeeping ----------
    def _log(self, msg):
        if self.verbose:
            print(msg, flush=True)

    def _event(self, kind, **data):
        self.events.write(json.dumps({"t": time.time(), "event": kind, **data}, ensure_ascii=False) + "\n"); self.events.flush()

    def _on_call(self, call):
        self._event("llm", role="project", model=call["model"], input_tokens=call["input_tokens"],
                    output_tokens=call["output_tokens"], cost_usd=round(call_cost(call), 4))
        try:
            self.budget.on_call(call)
        finally:
            self._save_state()  # persist spend after EVERY call so a killed process never loses money from the total

    def _save_state(self):
        self.state_path.write_text(json.dumps({
            "spec": asdict(self.spec), "spent_usd": self.budget.spent if hasattr(self, "budget") else 0.0,
            "replans": self.replans, "nodes": [asdict(n) for n in self.nodes]}, indent=1, ensure_ascii=False))
        (self.dir / "library.lean").write_text(self.library_text())

    def _load_state(self) -> float:
        if not self.state_path.exists():
            return 0.0
        st = json.loads(self.state_path.read_text())
        self.nodes = [Node(**n) for n in st["nodes"]]
        self.replans = st.get("replans", 0)
        return max(st.get("spent_usd", 0.0), self._spend_from_log())

    def _spend_from_log(self) -> float:
        """Sum of every LLM call ever logged for this project; robust to processes killed mid-lemma."""
        path = self.dir / "events.jsonl"
        if not path.exists():
            return 0.0
        total = 0.0
        for l in path.read_text().splitlines():
            try:
                e = json.loads(l)
            except json.JSONDecodeError:
                continue
            if e.get("event") == "llm":
                total += e.get("cost_usd") if e.get("cost_usd") is not None else call_cost(e)
        return total

    # ---------- library assembly ----------
    def library_text(self, upto: str | None = None, include_pending_as_sorry: bool = False) -> str:
        parts = [HEADER, ""]
        for n in self.nodes:
            if n.id == upto:
                break
            if n.kind == "def" or n.status == "proved":
                parts += [n.library_code(), ""]
            elif include_pending_as_sorry and n.kind == "lemma":
                parts += [f"{n.code} := by\n  sorry", ""]
        return "\n".join(parts)

    def header_for(self, node: Node) -> str:
        return self.library_text(upto=node.id).rstrip()

    def compile_skeleton(self) -> str | None:
        """Every def concrete, every lemma stubbed with sorry. Returns error text or None."""
        src = self.library_text(include_pending_as_sorry=True)
        path = self.cfg.lean_src_dir / "Project_skeleton.lean"
        path.write_text(src)
        out, rc, timed_out = self.checker._run(path, self.cfg.lean_timeout_s)
        errs = [l for l in out.splitlines() if ": error:" in l]
        if timed_out:
            return "skeleton compile timed out"
        if rc != 0 or errs:
            # attach a few lines of context after each error
            return "\n".join(out.splitlines()[:80])
        return None

    # ---------- planning ----------
    def make_plan(self):
        feedback = None
        for i in range(4):
            self._log(f"[planner] drafting plan (try {i + 1})...")
            self.nodes = self.planner.plan(self.spec, feedback)
            self._event("plan", try_=i, nodes=[asdict(n) for n in self.nodes])
            self._save_state()
            feedback = self.compile_skeleton()
            if feedback is None:
                self._log(f"[planner] skeleton compiles: {len(self.nodes)} nodes, {sum(n.kind == 'lemma' for n in self.nodes)} lemmas to prove")
                for n in self.nodes:
                    if n.kind == "def":
                        n.status = "proved"
                self._save_state()
                return
            self._log(f"[planner] skeleton failed:\n{feedback[:1500]}")
        raise RuntimeError("planner could not produce a compiling skeleton")

    def do_replan(self, failed: Node) -> bool:
        if self.replans >= self.spec.max_replans:
            return False
        self.replans += 1
        old = {n.id: n for n in self.nodes}
        feedback = None
        for i in range(3):
            self._log(f"[replanner] revising plan after {failed.id} failed (replan {self.replans}, try {i + 1})...")
            new_nodes = self.planner.replan(self.spec, self.nodes, failed, feedback)
            # carry over proofs for nodes whose code is unchanged and whose deps are all unchanged
            changed = set()
            for n in new_nodes:
                o = old.get(n.id)
                if o is None or o.code.strip() != n.code.strip() or o.kind != n.kind:
                    changed.add(n.id)
            for n in new_nodes:
                o = old.get(n.id)
                deps_changed = any(d in changed for d in n.depends_on)
                if n.kind == "def":
                    n.status = "proved"
                elif o and o.status == "proved" and n.id not in changed and not deps_changed:
                    n.status, n.proof, n.aux, n.attempts, n.run_dir = "proved", o.proof, o.aux, o.attempts, o.run_dir
            saved = self.nodes
            self.nodes = new_nodes
            self._event("replan", n=self.replans, try_=i, failed=failed.id, nodes=[asdict(n) for n in self.nodes])
            feedback = self.compile_skeleton()
            if feedback is None:
                # invalidated proofs must still compile in context; verify the full library with sorries once more
                self._save_state()
                self._log(f"[replanner] new skeleton compiles: {len(self.nodes)} nodes")
                return True
            self._log(f"[replanner] skeleton failed:\n{feedback[:1200]}")
            self.nodes = saved
        return False

    # ---------- proving ----------
    def next_node(self) -> Node | None:
        status = {n.id: n.status for n in self.nodes}
        pending = [n for n in self.nodes if n.kind == "lemma" and n.status == "pending"]
        for n in pending:
            # dependency ids that do not name any node (planner typos / renames) are ignored
            if all(status.get(d, "proved") == "proved" for d in n.depends_on if d in status):
                return n
        # Nothing eligible but work remains (e.g. a dependency is blocked). The header already contains
        # every proved node, so fall back to the first pending lemma whose listed deps are not failed.
        for n in pending:
            if not any(status.get(d) in ("failed", "blocked") for d in n.depends_on):
                return n
        return None

    def prove_node(self, node: Node) -> bool:
        self._log(f"\n#### node {node.id}: {node.informal}\n{node.code}")
        worker = Orchestrator(self.cfg, verbose=self.verbose, llm=self.llm)
        problem = Problem(name=node.id, informal=node.informal, formal_statement=node.code)
        result = worker.run(problem, header=self.header_for(node))
        node.attempts += result.attempts
        node.run_dir = str(Path(result.log_path).parent)
        if result.success:
            node.status, node.proof, node.aux = "proved", result.proof, result.aux
            self._log(f"[project] {node.id} PROVED  (spent ${self.budget.spent:.2f} of ${self.budget.cap:.2f})")
        else:
            node.status = "failed"
            node.failure_summary = self._failure_summary(Path(result.log_path))
            self._log(f"[project] {node.id} FAILED after {result.attempts} attempts  (spent ${self.budget.spent:.2f})")
        self._event("node", id=node.id, status=node.status, attempts=result.attempts, spent_usd=round(self.budget.spent, 2))
        self._save_state()
        return result.success

    @staticmethod
    def _failure_summary(log_path: Path) -> str:
        lines = []
        for l in log_path.read_text().splitlines():
            e = json.loads(l)
            if e["event"] == "failure" and e.get("stalled"):
                lines.append(f"STALLED: identical error on {e['attempts']} consecutive attempts: {e.get('signature', '')}")
            if e["event"] == "attempt":
                d = e.get("diagnosis") or {}
                lines.append(f"attempt {e['index']}: {e['check_summary'].splitlines()[0][:200]} | critic[{d.get('category')}]: {d.get('diagnosis', '')[:300]}")
        return "\n".join(lines[-6:])

    def force_replan(self, node_id: str, note: str) -> bool:
        """Operator-initiated replan: mark a node failed with a diagnosis and revise the plan around it."""
        node = next(n for n in self.nodes if n.id == node_id)
        node.status = "failed"
        node.failure_summary = (node.failure_summary + "\n\nOPERATOR DIAGNOSIS:\n" + note).strip()
        self._event("operator_replan", id=node_id, note=note)
        ok = self.do_replan(node)
        if not ok:
            node.status = "pending"
        self._save_state()
        return ok

    def run(self):
        t0 = time.time()
        try:
            if not self.nodes:
                self.make_plan()
            while True:
                node = self.next_node()
                if node is None:
                    break
                ok = self.prove_node(node)
                if not ok:
                    if not self.do_replan(node):
                        # mark dependents blocked and continue with whatever is still provable
                        self._mark_blocked(node)
        except BudgetExceeded as e:
            self._log(f"\n[project] STOPPED: {e}")
            self._event("budget_stop", spent_usd=self.budget.spent)
        finally:
            self._save_state()
            self.write_report(time.time() - t0)

    def _mark_blocked(self, failed: Node):
        failed_ids = {failed.id}
        changed = True
        while changed:
            changed = False
            for n in self.nodes:
                if n.status == "pending" and any(d in failed_ids for d in n.depends_on):
                    n.status = "blocked"; failed_ids.add(n.id); changed = True

    # ---------- final verification & report ----------
    def verify_final(self) -> tuple[bool, str]:
        lemmas = [n for n in self.nodes if n.kind == "lemma"]
        if any(n.status != "proved" for n in lemmas):
            return False, "not all lemmas proved"
        src = self.library_text()
        names = [m.group(1) for n in lemmas for m in [re.match(r"\s*(?:theorem|lemma)\s+(\S+)", n.code)] if m]
        src += "\n" + "\n".join(f"#print axioms {nm}" for nm in names) + "\n"
        path = self.cfg.lean_src_dir / "Project_final.lean"
        path.write_text(src)
        out, rc, _ = self.checker._run(path, self.cfg.lean_timeout_s)
        axioms = set(a.strip() for m in re.finditer(r"depends on axioms: \[(.*?)\]", out, re.S) for a in m.group(1).split(","))
        bad = axioms - STANDARD_AXIOMS
        ok = rc == 0 and ": error:" not in out and "sorry" not in out and not bad
        return ok, out[-3000:]

    def node_costs(self) -> dict[str, float]:
        """Dollar cost per lemma, summed over every run folder for that lemma (including aborted ones)."""
        costs: dict[str, float] = {}
        for ej in (self.dir / "runs").glob("*/events.jsonl"):
            if ej.parent.is_symlink():
                continue
            name = None; c = 0.0
            for l in ej.read_text().splitlines():
                try:
                    e = json.loads(l)
                except json.JSONDecodeError:
                    continue
                if e["event"] == "start":
                    name = e["problem"]["name"]
                elif e["event"] == "llm":
                    c += call_cost(e)
            if name:
                costs[name] = costs.get(name, 0.0) + c
        return costs

    def write_plan_md(self) -> Path:
        costs = self.node_costs()
        lemmas = [n for n in self.nodes if n.kind == "lemma"]
        mark = {"proved": "✅", "pending": "⬜", "failed": "❌", "blocked": "⛔"}
        md = [f"# Plan: {self.spec.name}", "",
              f"{sum(n.status == 'proved' for n in lemmas)}/{len(lemmas)} lemmas proved · "
              f"{sum(n.kind == 'def' for n in self.nodes)} definitions · spent ${self.budget.spent:.2f} of ${self.budget.cap:.2f} · replans {self.replans}", "",
              "## Goal", "", self.spec.goal, "", "## Design guidance given to the planner", "", self.spec.guidance, "",
              "## Nodes in dependency order", "",
              "| # | | id | kind | what it says | depends on | attempts | cost |", "|---:|---|---|---|---|---|---:|---:|"]
        for i, n in enumerate(self.nodes, 1):
            cost = f"${costs[n.id]:.2f}" if n.id in costs else ""
            deps = ", ".join(f"`{d}`" for d in n.depends_on) or ""
            md.append(f"| {i} | {mark[n.status]} | `{n.id}` | {n.kind} | {n.informal.replace('|', '\\|')} | {deps} | {n.attempts or ''} | {cost} |")
        md += ["", "## Statements", ""]
        for n in self.nodes:
            md += [f"### `{n.id}` ({n.kind}, {n.status})", "", n.informal, "", "```lean", n.code, "```", ""]
        if costs:
            top = sorted(costs.items(), key=lambda kv: -kv[1])[:5]
            md += ["## Most expensive lemmas", "", "| lemma | cost |", "|---|---:|"] + [f"| `{k}` | ${v:.2f} |" for k, v in top] + [""]
        path = self.dir / "PLAN.md"
        path.write_text("\n".join(md))
        return path

    # ---- EXPLANATION.md: plain-language walkthrough of the finished development ----
    EXPLAIN_SYSTEM = LEAN_CONTEXT + """
Your job: explain a *complete, machine-verified* Lean 4 + Mathlib development to a mathematically literate reader who is
new to Lean. You are given the goal, the full library (definitions and proved theorems in dependency order), and each
node's informal description and attempt count. Every proof compiled and depends only on the standard axioms; do not
speculate beyond what the code shows.

Write Markdown with these sections:
1. **What was proved** — the final theorems in plain language, as a small table (H^k over each ring), and what the
   objects are (which triangulation, how cochains and coboundaries are represented, how H^k is defined).
2. **How the development is organised** — the definitions first (what each one is, in one or two sentences each),
   then the arc of the argument: H^0, H^1, H^2, and the generic-then-specialise pattern.
3. **Walkthrough of each theorem** — in library order. For each: the statement in words, the key idea of the proof,
   and the main Lean tactics/lemmas it relies on (quote identifiers in backticks). Two to six sentences each; more for
   the substantive ones (the witness computations, the generic isomorphisms), one for the one-line specialisations.
4. **Reading the Lean** — a short glossary of the notation that appears (`Fin n → R`, `LinearMap.ker/range`, `⧸`,
   `≃+`, `Nonempty`, `ZMod 2`, `Matrix.mulVec`, `decide`, `fin_cases`, `Submodule.liftQ`, etc.), each in one line.
5. **Why you can trust this** — compiled with no errors and no sorry, `#print axioms` on every theorem lists only
   `propext`, `Classical.choice`, `Quot.sound`; explain what those are in one line each.
Be concrete and concise. No filler."""

    def write_explanation(self) -> Path | None:
        lemmas = [n for n in self.nodes if n.kind == "lemma"]
        if any(n.status != "proved" for n in lemmas):
            return None
        plan = "\n".join(f"- `{n.id}` ({n.kind}, {n.attempts} attempt(s)): {n.informal}" for n in self.nodes)
        user = (f"GOAL:\n{self.spec.goal}\n\nNODES (dependency order):\n{plan}\n\n"
                f"FULL LIBRARY (compiles, verified):\n```lean\n{self.library_text().strip()}\n```")
        path = self.dir / "EXPLANATION.md"
        if path.exists():
            self._log("[explainer] EXPLANATION.md exists (hand-edited); not regenerating. Delete it to regenerate.")
            return path
        self._log("[explainer] writing EXPLANATION.md ...")
        md = self.llm.complete(self.EXPLAIN_SYSTEM, user, model=self.cfg.model, max_tokens=16000).text.strip()
        path = self.dir / "EXPLANATION.md"
        path.write_text(f"# {self.spec.name}: explanation of the verified development\n\n{md}\n")
        self._save_state()
        return path

    def write_report(self, elapsed: float):
        lemmas = [n for n in self.nodes if n.kind == "lemma"]
        proved = [n for n in lemmas if n.status == "proved"]
        complete = len(proved) == len(lemmas) and lemmas
        final_ok, final_out = self.verify_final() if complete else (False, "")
        rows = ["| node | kind | status | attempts | run |", "|---|---|---|---:|---|"]
        for n in self.nodes:
            run = f"[{Path(n.run_dir).name}]({Path(n.run_dir).name}/trace.md)" if n.run_dir else ""
            rows.append(f"| `{n.id}` | {n.kind} | {n.status} | {n.attempts} | {run} |")
        md = [f"# Project: {self.spec.name}", "",
              f"**Status:** {'COMPLETE and verified' if final_ok else ('all lemmas proved but final verification FAILED' if complete else 'incomplete')}  ·  "
              f"lemmas proved {len(proved)}/{len(lemmas)}  ·  spent ${self.budget.spent:.2f} of ${self.budget.cap:.2f}  ·  "
              f"replans {self.replans}  ·  {elapsed / 60:.1f} min this session", "",
              "## Goal", "", self.spec.goal, "", "## Plan and outcome", "", *rows, ""]
        if complete:
            md += ["## Final verification (`#print axioms` on every lemma)", "", "```text", final_out.strip(), "```", ""]
        failed = [n for n in self.nodes if n.status in ("failed", "blocked")]
        if failed:
            md += ["## Failures", ""]
            for n in failed:
                md += [f"### `{n.id}` ({n.status})", "", "```lean", n.code, "```", "", n.failure_summary or "(blocked by a failed dependency)", ""]
        md += ["## Library (`library.lean`)", "", "```lean", self.library_text().strip(), "```", ""]
        (self.dir / "report.md").write_text("\n".join(md))
        plan_path = self.write_plan_md()
        expl = None
        if final_ok and self.cfg.explain_project:
            try:
                expl = self.write_explanation()
            except BudgetExceeded as e:
                self._log(f"[explainer] skipped: {e}")
        self._log(f"\n[project] report: {self.dir / 'report.md'}   plan: {plan_path}   library: {self.dir / 'library.lean'}"
                  + (f"   explanation: {expl}" if expl else ""))
