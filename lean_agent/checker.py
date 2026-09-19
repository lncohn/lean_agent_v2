"""Lean checker: the ground-truth verifier in the loop.

The orchestrator owns the theorem statement. The prover supplies (optionally) a block of
helper declarations and the tactic block for the main theorem. This module assembles the
file, compiles it with `lake env lean`, and parses the output into structured diagnostics.
It also offers `probe()` so the prover can run `#check` / `exact?` style queries.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

# Lean 4.3x may tag messages with a code: `...:12:3: error(lean.synthInstanceFailed): msg`
_DIAG_RE = re.compile(r"^(?P<file>[^:\n]+):(?P<line>\d+):(?P<col>\d+): (?P<sev>error|warning|info)(?:\([^)]*\))?: (?P<msg>.*)$")
_LINTER_NOTE = "This linter can be disabled with"

# Never acceptable anywhere in a submission. `#print axioms` is the final backstop, but
# rejecting these up front gives the critic a clear signal.
BANNED_ANYWHERE = ("sorry", "admit", "native_decide", "axiom ", "opaque ", "unsafe ", "implemented_by", "extern ", "partial def")
# Allowed at top level in the helper block.
AUX_DECL_RE = re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(theorem|lemma|def|abbrev|instance|open|namespace|end|section|variable|local\s+notation|set_option\s+(?:maxHeartbeats|synthInstance\.maxHeartbeats|synthInstance\.maxSize|maxRecDepth|linter\.\S+)|attribute)\b")
# Things that can run arbitrary code at elaboration time; never allowed in probes.
# Words that reach IO or Lean's metaprogramming layer. `#eval` itself is allowed for pure computation.
PROBE_BANNED_WORDS = ("run_cmd", "run_tac", "IO", "System", "Lean", "Elab", "Meta", "Term", "Tactic", "initialize", "unsafe",
                      "implemented_by", "extern", "axiom", "macro_rules", "macro", "elab", "syntax", "declare_syntax_cat",
                      "import", "Process", "FilePath", "getEnv", "ptrAddr", "opaque")
_PROBE_BANNED_RE = re.compile(r"(?<![\w.'])(" + "|".join(re.escape(w) for w in PROBE_BANNED_WORDS) + r")(?![\w'])")
# Never allowed in the main tactic block.
DECL_IN_BODY_RE = re.compile(r"^\s*(theorem|lemma|axiom|def|instance|abbrev)\b", re.M)


@dataclass
class Diagnostic:
    severity: str
    line: int
    col: int
    message: str

    def render(self) -> str:
        return f"[{self.severity}] line {self.line}:{self.col}: {self.message}"


@dataclass
class CheckResult:
    ok: bool
    diagnostics: list[Diagnostic]
    raw_output: str
    returncode: int
    timed_out: bool
    source: str
    file_path: Path | None = None
    guard_failure: str | None = None
    submission_start: int | None = None  # 1-based line in `source` where the prover's text (aux or theorem) begins

    def errors(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.severity == "error"]

    def _locate(self, d: Diagnostic) -> str:
        """Render an error with the offending source line and its position relative to the submission,
        so the prover/critic can find it in the text they actually wrote."""
        lines = self.source.splitlines()
        if not (1 <= d.line <= len(lines)):
            return d.render()
        src_line = lines[d.line - 1]
        where = ""
        if self.submission_start is not None:
            if d.line >= self.submission_start:
                where = f" (submission line {d.line - self.submission_start + 1})"
            else:
                where = " (in the library header: NOT your code; the statement or a dependency)"
        return f"[error] line {d.line}:{d.col}{where}: {d.message}\n  ↳ source: {src_line.strip()[:200]}"

    def summary(self) -> str:
        if self.guard_failure:
            return f"GUARD: {self.guard_failure}"
        if self.timed_out:
            return "TIMEOUT: Lean did not finish within the time limit"
        if self.ok:
            return "OK"
        # Errors first; then warnings, minus pure linter chatter (unused simp args, unreachable tactics)
        errs = [self._locate(d) for d in self.diagnostics if d.severity == "error"]
        warns = [d.render() for d in self.diagnostics if d.severity == "warning" and _LINTER_NOTE not in d.message]
        n_lint = sum(1 for d in self.diagnostics if d.severity == "warning" and _LINTER_NOTE in d.message)
        parts = errs + warns
        if n_lint:
            parts.append(f"({n_lint} linter warning(s) about unused simp arguments / unreachable tactics omitted)")
        return "\n".join(parts) or self.raw_output[-2000:]


def parse_diagnostics(output: str) -> list[Diagnostic]:
    diags: list[Diagnostic] = []
    for line in output.splitlines():
        m = _DIAG_RE.match(line)
        if m:
            diags.append(Diagnostic(m["sev"], int(m["line"]), int(m["col"]), m["msg"]))
        elif diags:
            diags[-1].message += "\n" + line
    return diags


def assemble(header: str, statement: str, proof_body: str, aux: str = "") -> str:
    """Build the full Lean file. `statement` ends right before `:= by`."""
    body = proof_body.strip("\n")
    body_lines = [("  " + l if l.strip() else l) for l in body.splitlines()]
    parts = [header.rstrip(), ""]
    if aux.strip():
        parts += [aux.strip("\n"), ""]
    parts.append(f"{statement.rstrip()} := by\n" + "\n".join(body_lines) + "\n")
    return "\n".join(parts)


def guard(proof_body: str, aux: str = "", banned: tuple[str, ...] = BANNED_ANYWHERE) -> str | None:
    for text, where in ((proof_body, "proof"), (aux, "helper block")):
        low = text.lower()
        for tok in banned:
            if tok in low:
                return f"{where} contains banned token {tok.strip()!r}"
    if DECL_IN_BODY_RE.search(proof_body):
        return "main proof contains a top-level declaration; helpers belong in the block before the theorem"
    # Every top-level (column 0) line of the helper block must start an allowed declaration.
    for line in aux.splitlines():
        if line and not line[0].isspace() and not line.startswith("--") and not line.startswith("/-") and not line.startswith("-/"):
            if not AUX_DECL_RE.match(line):
                return f"helper block has a disallowed top-level line: {line[:80]!r}"
    return None


class LeanChecker:
    def __init__(self, cfg):
        self.cfg = cfg
        self.env = dict(os.environ)
        self.env["PATH"] = f"{cfg.elan_bin}:{self.env.get('PATH', '')}"
        self.cfg.lean_src_dir.mkdir(parents=True, exist_ok=True)

    def _run(self, path: Path, timeout: int, extra: list[str] = ()) -> tuple[str, int, bool]:
        try:
            proc = subprocess.run(["lake", "env", "lean", *extra, str(path)], cwd=self.cfg.lean_project, env=self.env,
                                  capture_output=True, text=True, timeout=timeout)
            return proc.stdout + proc.stderr, proc.returncode, False
        except subprocess.TimeoutExpired as e:
            return (e.stdout or "") + (e.stderr or ""), -1, True

    def check(self, header: str, statement: str, proof_body: str, tag: str = "Attempt", aux: str = "") -> CheckResult:
        source = assemble(header, statement, proof_body, aux)
        submission_start = len(header.rstrip().splitlines()) + 2  # header, blank line, then aux/statement
        g = guard(proof_body, aux, self.cfg.banned_tokens)
        if g:
            return CheckResult(False, [], "", -1, False, source, None, g)
        digest = hashlib.sha1(source.encode()).hexdigest()[:10]
        path = self.cfg.lean_src_dir / f"{tag}_{digest}.lean"
        path.write_text(source)
        out, rc, timed_out = self._run(path, self.cfg.lean_timeout_s)
        diags = parse_diagnostics(out)
        if timed_out:
            return CheckResult(False, diags, out, rc, True, source, path, submission_start=submission_start)
        uses_sorry = any("sorry" in d.message for d in diags)
        ok = rc == 0 and not any(d.severity == "error" for d in diags) and not uses_sorry
        return CheckResult(ok, diags, out, rc, False, source, path, submission_start=submission_start)

    def probe(self, code: str, header: str = "import Mathlib") -> str:
        """Run an arbitrary snippet (e.g. `#check foo`, `example : ... := by exact?`) and return Lean's output."""
        # Probes may use sorry and declarations freely, but must not be able to execute code on this machine.
        m = _PROBE_BANNED_RE.search(code)
        if m:
            return (f"probe rejected: `{m.group(1)}` is not allowed in probes. Allowed: #check, #synth, #print, exact?, apply?, "
                    f"examples with sorry, and #eval of pure computations (no IO, no metaprogramming).")
        src = f"{header}\n\n{code.strip()}\n"
        path = self.cfg.lean_src_dir / f"Probe_{hashlib.sha1(src.encode()).hexdigest()[:10]}.lean"
        path.write_text(src)
        try:
            out, rc, timed_out = self._run(path, min(self.cfg.lean_timeout_s, 120))
        finally:
            path.unlink(missing_ok=True)
        out = out.replace(str(path), "probe.lean").strip()
        if timed_out:
            out += "\n[probe timed out]"
        if not out:
            out = "(no output: the snippet compiled without messages)"
        return out[:6000]
