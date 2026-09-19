"""The feedback loop: formalize -> (prove -> check -> critique)* -> done."""
from __future__ import annotations

import hashlib
import re
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .agents import Attempt, Critic, Formalizer, Prover
from .checker import LeanChecker, assemble
from .config import Config
from .explainer import STANDARD_AXIOMS, Explainer, ProofInspector
from .llm import make_client
from .trace import render_trace

HEADER = "import Mathlib"


@dataclass
class Problem:
    name: str
    informal: str
    formal_statement: str | None = None  # skip the formalizer if given
    constraints: str = ""                # extra instructions to the prover
    forbidden: tuple[str, ...] = ()      # substrings that fail the guard (to force the loop to work)


@dataclass
class RunResult:
    problem: str
    statement: str
    success: bool
    attempts: int
    proof: str | None
    elapsed_s: float
    log_path: str
    axioms: list[str] = field(default_factory=list)
    aux: str = ""
    explanation_path: str | None = None
    trace_path: str | None = None


class Orchestrator:
    def __init__(self, cfg: Config | None = None, verbose: bool = True, llm=None):
        self.cfg = cfg or Config()
        self.llm = llm or make_client(self.cfg)
        self.header = HEADER
        self.checker = LeanChecker(self.cfg)
        self.formalizer = Formalizer(self.llm, self.cfg.model)
        self.prover = Prover(self.llm, self.cfg.model,
                             probe=(self.checker.probe if self.cfg.probes_per_attempt > 0 else None),
                             max_probes=self.cfg.probes_per_attempt)
        self.critic = Critic(self.llm, self.cfg.critic_model)
        self.inspector = ProofInspector(self.checker)
        self.explainer = Explainer(self.llm, self.cfg.model)
        self.verbose = verbose

    def _log(self, msg: str):
        if self.verbose:
            print(msg, flush=True)

    def _event(self, fh, kind: str, **data):
        fh.write(json.dumps({"t": time.time(), "event": kind, **data}) + "\n")
        fh.flush()

    def _llm(self, fh, role: str, fn, *args, **kwargs):
        """Run an agent call and log every LLM request it made, tagged with the role."""
        n = len(self.llm.calls)
        out = fn(*args, **kwargs)
        for c in self.llm.calls[n:]:
            self._event(fh, "llm", role=role, **c)
        return out

    def _finish(self, fh, result: "RunResult") -> "RunResult":
        self._event(fh, "end", success=result.success, attempts=result.attempts, elapsed_s=result.elapsed_s)
        fh.flush()
        trace_path = Path(result.log_path).parent / "trace.md"
        trace_path.write_text(render_trace(Path(result.log_path)))
        result.trace_path = str(trace_path)
        if result.proof:
            (Path(result.log_path).parent / "proof.lean").write_text(assemble(self.header, result.statement, result.proof, result.aux))
        files = ["events.jsonl", "trace.md"] + (["proof.lean"] if result.proof else []) + (["explanation.md"] if result.explanation_path else [])
        self._log(f"\n[run folder] {Path(result.log_path).parent}\n  " + "  ".join(files))
        return result

    def formalize(self, problem: Problem, fh) -> str:
        if problem.formal_statement:
            self._event(fh, "formalize", statement=problem.formal_statement, source="given")
            return problem.formal_statement
        feedback = None
        for i in range(3):
            stmt = self._llm(fh, "formalizer", self.formalizer.run, problem.informal, feedback)
            res = self._check_statement_only(stmt)
            self._event(fh, "formalize", statement=stmt, ok=res.ok or res.errors() == [], lean=res.summary(), try_=i)
            if not res.errors() and not res.timed_out:
                self._log(f"[formalizer] {stmt}")
                return stmt
            feedback = res.summary()
            self._log(f"[formalizer] statement failed to compile, retrying:\n{feedback}")
        raise RuntimeError("formalizer could not produce a compiling statement")

    def _check_statement_only(self, stmt: str):
        # Bypass the banned-token guard for statement validation.
        banned = self.cfg.banned_tokens
        self.cfg.banned_tokens = ()
        try:
            return self.checker.check(self.header, stmt, "sorry", tag="Formalize")
        finally:
            self.cfg.banned_tokens = banned

    def explain(self, problem: Problem, statement: str, proof: str, axioms: list[str], fh, aux: str = "") -> str:
        self._log("\n[explainer] collecting goal states...")
        states = self.inspector.goal_states(self.header, statement, proof, aux)
        md = self._llm(fh, "explainer", self.explainer.run, statement, proof, states, axioms, aux)
        header = f"# {problem.name}\n\n```lean\n{assemble(self.header, statement, proof, aux).rstrip()}\n```\n\n"
        path = self.run_dir / "explanation.md"
        path.write_text(header + md + "\n")
        self._event(fh, "explanation", path=str(path), states=[s.__dict__ for s in states])
        self._log(md)
        return str(path)

    def run(self, problem: Problem, header: str | None = None) -> RunResult:
        self.header = header or HEADER
        t0 = time.time()
        run_dir = self.cfg.runs_dir / f"{problem.name}_{time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(t0))}"
        run_dir.mkdir(parents=True, exist_ok=True)
        self.run_dir = run_dir
        log_path = run_dir / "events.jsonl"
        latest = self.cfg.runs_dir / "latest"
        latest.unlink(missing_ok=True)
        latest.symlink_to(run_dir.name)
        history: list[Attempt] = []
        stall_sigs: list[str] = []
        seen: set[str] = set()
        constraints = problem.constraints
        if problem.forbidden:
            constraints += f" Do NOT use any of these: {', '.join(problem.forbidden)}."

        with open(log_path, "w") as fh:
            self._event(fh, "start", problem=asdict(problem), model=self.cfg.model, backend=self.cfg.backend,
                        max_attempts=self.cfg.max_attempts, probes_per_attempt=self.cfg.probes_per_attempt)
            statement = self.formalize(problem, fh)

            for i in range(1, self.cfg.max_attempts + 1):
                self._log(f"\n=== attempt {i}/{self.cfg.max_attempts} ===")
                aux, proof, err, probes = self._llm(fh, "prover", self.prover.run, self.header, statement, history, constraints)
                for pi, pr in enumerate(probes, 1):
                    self._log(f"[probe {pi}] {pr['code'].strip()[:200]}\n   -> {pr['output'][:300].replace(chr(10), ' | ')}")
                self._event(fh, "probes", attempt=i, probes=probes)
                self._log((aux + "\n\n" if aux else "") + proof)

                digest = hashlib.sha1(" ".join((aux + proof).split()).encode()).hexdigest()
                res = None
                if err:
                    att = Attempt(i, proof, f"GUARD: {err}", False, aux=aux, probes=probes)
                elif digest in seen:
                    att = Attempt(i, proof, "GUARD: identical to a previous failed attempt", False, aux=aux, probes=probes)
                else:
                    seen.add(digest)
                    forbidden_hit = next((f for f in problem.forbidden if f in proof or f in aux), None)
                    if forbidden_hit:
                        att = Attempt(i, proof, f"GUARD: uses forbidden lemma/tactic {forbidden_hit!r}", False, aux=aux, probes=probes)
                    else:
                        tc = time.time()
                        res = self.checker.check(self.header, statement, proof, tag=problem.name, aux=aux)
                        self._log(f"[lean {time.time()-tc:.1f}s] {res.summary()[:1500]}")
                        att = Attempt(i, proof, res.summary(), res.ok, aux=aux, probes=probes)
                        self._event(fh, "check", attempt=i, ok=res.ok, returncode=res.returncode,
                                    timed_out=res.timed_out, file=str(res.file_path), raw=res.raw_output[-4000:])

                if att.ok:
                    axioms, ax_raw = self.inspector.axioms(self.header, statement, proof, aux)
                    nonstandard = sorted(set(axioms) - STANDARD_AXIOMS)
                    self._event(fh, "axioms", attempt=i, axioms=axioms, raw=ax_raw)
                    if nonstandard:
                        att.ok = False
                        att.check_summary = f"GUARD: proof depends on non-standard axioms {nonstandard}"
                        self._log(f"[axioms] rejected: {nonstandard}")
                    else:
                        self._log(f"[axioms] {axioms}")
                        self._event(fh, "success", attempt=i, proof=proof, aux=aux)
                        self._log(f"\n*** PROVED in {i} attempt(s) ***")
                        result = RunResult(problem.name, statement, True, i, proof, time.time() - t0, str(log_path), axioms, aux=aux)
                        if self.cfg.explain:
                            result.explanation_path = self.explain(problem, statement, proof, axioms, fh, aux)
                        return self._finish(fh, result)

                att.diagnosis = self._llm(fh, "critic", self.critic.run, statement, att, history)
                # Stall detection: the same leading error N attempts in a row means the problem is upstream
                # (a definition, a statement, an instance) and more attempts are wasted money.
                sig = re.sub(r"line \d+:\d+", "", att.check_summary.splitlines()[0])[:120] if att.check_summary else ""
                stall_sigs.append(sig)
                if self.cfg.stall_after and len(stall_sigs) >= self.cfg.stall_after and len(set(stall_sigs[-self.cfg.stall_after:])) == 1 and sig:
                    self._event(fh, "attempt", **{k: v for k, v in asdict(att).items()})
                    history.append(att)
                    self._event(fh, "failure", attempts=i, stalled=True, signature=sig)
                    self._log(f"\n*** STALLED: same error {self.cfg.stall_after} attempts in a row: {sig[:100]} ***")
                    return self._finish(fh, RunResult(problem.name, statement, False, i, None, time.time() - t0, str(log_path)))
                self._log(f"[critic] {att.diagnosis.get('category')}: {att.diagnosis.get('diagnosis')}\n         -> {att.diagnosis.get('suggestion')}")
                self._event(fh, "attempt", **{k: v for k, v in asdict(att).items()})
                history.append(att)

            self._event(fh, "failure", attempts=self.cfg.max_attempts)
            self._log(f"\n*** FAILED after {self.cfg.max_attempts} attempts ***")
            return self._finish(fh, RunResult(problem.name, statement, False, self.cfg.max_attempts, None, time.time() - t0, str(log_path)))
