"""Render a run's JSONL event log as a human-readable Markdown trace."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def load(path: Path) -> list[dict]:
    events = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return events


def _code(text: str, lang: str = "lean") -> str:
    return f"```{lang}\n{text.rstrip()}\n```"


def _details(summary: str, body: str) -> str:
    return f"<details><summary>{summary}</summary>\n\n{body}\n\n</details>"


def _fmt_t(t: float, t0: float) -> str:
    return f"+{t - t0:6.1f}s"


def render_trace(path: Path) -> str:
    ev = load(path)
    if not ev:
        return f"# (empty log: {path.name})\n"
    t0 = ev[0]["t"]
    start = next((e for e in ev if e["event"] == "start"), {})
    end = next((e for e in ev if e["event"] == "end"), None)
    problem = start.get("problem", {})
    out: list[str] = []

    # ---- header -------------------------------------------------------------
    out.append(f"# Trace: {problem.get('name', path.stem)}")
    out.append(f"*{datetime.fromtimestamp(t0):%Y-%m-%d %H:%M:%S}*  ·  model `{start.get('model')}`  ·  backend `{start.get('backend')}`"
               + (f"  ·  budget {start['max_attempts']} attempts × {start.get('probes_per_attempt', 0)} probes" if 'max_attempts' in start else "") + "\n")
    if end:
        verdict = "PROVED" if end["success"] else "FAILED"
        out.append(f"**Outcome: {verdict}** in {end['attempts']} attempt(s), {end['elapsed_s']:.1f}s wall clock.\n")
    out.append("**Informal statement**\n\n> " + problem.get("informal", "").replace("\n", "\n> "))
    if problem.get("constraints"):
        out.append(f"\n**Constraints:** {problem['constraints']}")
    if problem.get("forbidden"):
        out.append(f"\n**Forbidden:** `{'`, `'.join(problem['forbidden'])}`")

    # ---- LLM usage summary --------------------------------------------------
    llm = [e for e in ev if e["event"] == "llm"]
    if llm:
        by_role: dict[str, dict] = {}
        for e in llm:
            r = by_role.setdefault(e["role"], {"calls": 0, "in": 0, "out": 0, "lat": 0.0})
            r["calls"] += 1; r["in"] += e.get("input_tokens", 0); r["out"] += e.get("output_tokens", 0); r["lat"] += e.get("latency_s", 0)
        rows = ["| role | calls | input tokens | output tokens | LLM time |", "|---|---:|---:|---:|---:|"]
        for role, r in by_role.items():
            rows.append(f"| {role} | {r['calls']} | {r['in']:,} | {r['out']:,} | {r['lat']:.1f}s |")
        tot = {k: sum(r[k] for r in by_role.values()) for k in ("calls", "in", "out", "lat")}
        rows.append(f"| **total** | {tot['calls']} | {tot['in']:,} | {tot['out']:,} | {tot['lat']:.1f}s |")
        out.append("## LLM usage\n\n" + "\n".join(rows))
    checks = [e for e in ev if e["event"] == "check"]
    if checks:
        out.append(f"\nLean checks: {len(checks)}")

    # ---- timeline -----------------------------------------------------------
    out.append("\n## Timeline\n")
    llm_iter = iter(llm)
    pending_llm: list[dict] = []

    def take_llm(role: str) -> dict | None:
        # llm events are logged right after the agent call, so the next one with this role is ours
        for i, e in enumerate(pending_llm):
            if e["role"] == role:
                return pending_llm.pop(i)
        for e in llm_iter:
            if e["role"] == role:
                return e
            pending_llm.append(e)
        return None

    def llm_block(e: dict | None, title: str) -> str:
        if not e:
            return ""
        meta = f"`{e.get('model')}` · {e.get('input_tokens', 0):,} in / {e.get('output_tokens', 0):,} out · {e.get('latency_s', 0)}s"
        tcs = e.get("tool_calls") or []
        if tcs:
            meta += f" · {len(tcs)} probe(s)"
        body = f"**System prompt**\n\n{_code(e.get('system', ''), 'text')}\n\n**User prompt**\n\n{_code(e.get('user', ''), 'text')}\n\n**Raw response**\n\n{_code(e.get('response', ''), 'text')}"
        blocks = [meta]
        if tcs:
            probes_md = "\n\n".join(
                f"**Probe {k}**\n\n{_code(tc['input'].get('code', ''), 'lean')}\n\nLean said:\n\n{_code(tc['output'], 'text')}"
                for k, tc in enumerate(tcs, 1))
            blocks.append(_details(f"{len(tcs)} Lean probe(s) the prover ran before submitting", probes_md))
        blocks.append(_details(f"{title}: full prompt and response", body))
        return "\n\n".join(blocks)

    attempt_checks = {e["attempt"]: e for e in checks}
    attempt_axioms = {e["attempt"]: e for e in ev if e["event"] == "axioms"}

    for e in ev:
        k = e["event"]
        ts = _fmt_t(e["t"], t0)
        if k == "formalize":
            src = e.get("source")
            out.append(f"### {ts}  Formalizer" + (" (statement supplied by problem file, LLM skipped)" if src == "given" else f" try {e.get('try_', 0) + 1}"))
            out.append(_code(e["statement"]))
            if src != "given":
                out.append(f"Lean on the `sorry`-stubbed statement: `{e.get('lean', '').splitlines()[0] if e.get('lean') else 'OK'}`")
                out.append(llm_block(take_llm("formalizer"), "formalizer"))
        elif k == "attempt" or k == "success":
            i = e["attempt"] if k == "success" else e["index"]
            proof = e["proof"]
            status = "✅ PASSED" if k == "success" else "❌ failed"
            out.append(f"### {ts}  Attempt {i}: {status}")
            out.append(llm_block(take_llm("prover"), "prover"))
            aux = e.get("aux", "")
            if aux:
                out.append("**Helper declarations submitted**\n\n" + _code(aux))
            out.append("**Main proof submitted**\n\n" + _code(proof))
            chk = attempt_checks.get(i)
            if k == "success":
                out.append("**Lean:** compiled with no errors and no `sorry`.")
                ax = attempt_axioms.get(i)
                if ax:
                    out.append(f"**Axioms:** `{'`, `'.join(ax['axioms'])}`")
            else:
                out.append("**Lean output**\n\n" + _code(e["check_summary"], "text"))
                if chk and chk.get("raw"):
                    out.append(_details("raw Lean stdout/stderr", _code(chk["raw"], "text")))
                d = e.get("diagnosis") or {}
                out.append(f"**Critic:** `{d.get('category')}`\n\n{d.get('diagnosis', '')}\n\n**Suggestion:** {d.get('suggestion', '')}")
                out.append(llm_block(take_llm("critic"), "critic"))
        elif k == "axioms" and e["attempt"] not in {x.get("attempt") for x in ev if x["event"] == "success"}:
            out.append(f"### {ts}  Axiom check rejected attempt {e['attempt']}\n\n" + _code(e.get("raw", ""), "text"))
        elif k == "explanation":
            out.append(f"### {ts}  Explainer")
            states = e.get("states", [])
            got = sum(1 for s in states if s.get("goal"))
            out.append(f"Goal states captured for {got}/{len(states)} tactic lines. Explanation written to `{Path(e['path']).name}`.")
            if states:
                body = "\n\n".join(f"**`{s['line']}`**\n\n{_code(s['goal'] or '(unavailable)', 'text')}" for s in states)
                out.append(_details("goal state before each tactic (from Lean)", body))
            out.append(llm_block(take_llm("explainer"), "explainer"))
        elif k == "failure":
            out.append(f"### {ts}  Gave up after {e['attempts']} attempts")
    return "\n\n".join(x for x in out if x) + "\n"


def find_logs(runs_dir: Path) -> list[Path]:
    return sorted((p for p in runs_dir.glob("*/events.jsonl") if not p.parent.is_symlink()), key=lambda p: p.stat().st_mtime)


def list_runs(runs_dir: Path) -> list[str]:
    rows = []
    for p in find_logs(runs_dir):
        ev = load(p)
        start = next((e for e in ev if e["event"] == "start"), {})
        end = next((e for e in ev if e["event"] == "end"), None)
        succ = next((e for e in ev if e["event"] == "success"), None)
        status = ("PROVED" if succ else "FAILED") if (end or succ or any(e["event"] == "failure" for e in ev)) else "incomplete"
        n = max([e.get("index", 0) for e in ev if e["event"] == "attempt"] + [succ["attempt"] if succ else 0])
        rows.append(f"{datetime.fromtimestamp(ev[0]['t']):%m-%d %H:%M}  {status:10s} {n:2d} att  {p.parent.name}")
    return rows
