# lean_agent

An agent system that builds Lean 4 + Mathlib developments under a dollar budget, with Lean as the
ground truth. Current project: the simplicial cohomology of RP² (`projects/rp2_cohomology.json`).

```
plan (LLM) ──► skeleton: every def concrete, every lemma `sorry` ──► must compile
   │
   ▼  for each lemma whose dependencies are proved
 worker: ┌─► prover (LLM; may probe Lean first) ──► helper lemmas + tactic proof
         │      checker: `lake env lean`  ──► OK ──► `#print axioms` must be standard ──► lemma proved
         │      critic (LLM): {category, diagnosis, suggestion}
         └──── full history fed back; stops after N attempts or when the same error repeats
   │ lemma exhausts its budget (or operator supplies a diagnosis)
 replan (LLM): split / restate / change a definition; proofs of unchanged nodes are kept
   │
 final: whole library compiled, `#print axioms` on every lemma
```

Every LLM call is priced at list price (`lean_agent/budget.py`); the run stops cleanly at the cap and
is resumable from `projects/<name>/state.json`.

## Layout

```
project.py           CLI: python project.py projects/rp2_cohomology.json --budget 200 [--fresh] [--replan-now NODE NOTE_FILE]
status.py            one-screen status incl. the lemma in progress: python status.py [-v]
trace.py             re-render a lemma's run folder into trace.md: python trace.py projects/rp2_cohomology/runs/<run>
TODO.md              checklist of specific improvements; LESSONS.md has the history behind them
figures.py           draw the RP² triangulation and tabulate d0mat/d1mat straight from Lean (#eval), splice into EXPLANATION.md
lean_agent/
  project.py         Planner, ProjectOrchestrator (skeleton compile, scheduling, replanning, report)
  orchestrator.py    single-lemma loop: prove → check → critique, stall detection, per-run trace
  agents.py          Prover (tool-using), Critic, Formalizer prompts; submission parsing
  checker.py         assembles the .lean file, runs Lean, parses diagnostics, guards, `probe()`
  explainer.py       ProofInspector (axioms, goal states) and Explainer prompt
  llm.py             LLMClient: AnthropicClient (Anthropic SDK, tool loop) / ClaudeCLIClient (`claude -p`)
  budget.py          price table, BudgetTracker
  trace.py           renders a run's events.jsonl as Markdown
  config.py          env-var-driven settings
lean_env/            Lake project depending on Mathlib (scratch .lean files land in LeanEnv/)
projects/
  rp2_cohomology.json      the spec: goal, design guidance, budgets
  rp2_cohomology/
    state.json             plan + status + spend (resume point)
    library.lean           everything proved so far, standalone
    report.md              written at the end of every session
    PLAN.md, EXPLANATION.md  plan with per-lemma cost; plain-language explanation (hand-edited; not regenerated while it exists)
    figures/               triangulation.png and objects.md, produced by figures.py
    runs/<lemma>_<ts>/     trace.md, events.jsonl, proof.lean for each lemma attempt series
```

## Guards

The planner owns definitions and lemma statements; the prover may add helper lemmas but its copy of the
statement must match exactly. Rejected outright: `sorry`, `admit`, `axiom`, `native_decide`, `opaque`,
`unsafe`, duplicate submissions, non-declaration lines in the helper block. After Lean accepts a proof,
`#print axioms` must report only `propext`, `Classical.choice`, `Quot.sound`. Probes may use `#check`,
`#synth`, `exact?`, examples with `sorry`, and `#eval` of pure values; IO and metaprogramming words are
rejected.

## Setup

```
python -m venv .venv && .venv/bin/pip install anthropic matplotlib
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh   # Lean toolchain manager
cd lean_env && lake exe cache get && lake build && cd ..                                  # Mathlib (cached .olean files, a few minutes)
export ANTHROPIC_API_KEY=sk-ant-...
.venv/bin/python project.py projects/rp2_cohomology.json --budget 200
```

## Auth and models

Backend `anthropic` (default) uses the Anthropic Python SDK with `ANTHROPIC_API_KEY`; set
`LEAN_AGENT_BASE_URL` to point it at an Anthropic-compatible proxy. Backend `claude_cli`
(`LEAN_AGENT_BACKEND=claude_cli`) shells out to `claude -p` and needs no key, but has no probe tool.
Default model `claude-opus-4-8`; override with `LEAN_AGENT_MODEL` / `LEAN_AGENT_CRITIC_MODEL`
(prices for budgeting are in `lean_agent/budget.py`).
Other knobs: `LEAN_AGENT_MAX_ATTEMPTS`, `LEAN_AGENT_LEAN_TIMEOUT`, `LEAN_AGENT_PROBES`, `LEAN_AGENT_STALL_AFTER`.

## Lessons recorded in the spec guidance

- Prove structural lemmas generically over `(R) [CommRing R]` and specialize to ℤ / `ZMod 2` in one-line
  final lemmas; instance checking on `ZMod 2` times out otherwise.
- Use `abbrev` (not `def`) for types that are quotients so instances are found automatically.
- Concrete arithmetic (matrix images, preimages) must be computed with `#eval` in a probe, not guessed.
