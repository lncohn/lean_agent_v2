# TODO

Specific improvements to the stack, derived from the rp2_cohomology run. Root causes and history are in
LESSONS.md. Each item names the file to change.

## Planner (`lean_agent/project.py`, `Planner.SYSTEM`)

- [ ] Require finite linear maps to be defined as literal matrices `!![…]`, never by a formula over a lookup table.
- [ ] If a formula-defined matrix is unavoidable, emit a separate node `M = !![…]` proved by `decide`, and tell provers to rewrite with it.
- [ ] Reject plan nodes whose statement is a conjunction of independent concrete facts; one computational fact per node.
- [ ] Tag every node `computational` or `structural` in the plan JSON.
- [ ] Prove structural lemmas over `(R) [CommRing R]` and specialize to `ℤ` / `ZMod 2` in one-line final nodes. Move this from the RP² spec guidance into the default system prompt.
- [ ] Use `abbrev` for quotient types. Also move into the default system prompt.
- [ ] Replanner must output a `renamed: {old_id: new_id}` map and the parser must rewrite `depends_on` with it, instead of dropping dangling ids.

## Prover (`lean_agent/agents.py`, `Prover` system prompt and `PROBE_TOOL`)

- [ ] Add the `funext; fin_cases i <;> decide` and `simp +decide` idioms for evaluating concrete finite functions.
- [ ] Add: "to prove non-membership in the image of a matrix, find a linear functional vanishing on its columns; compute candidates (column sums, etc.) with `#eval`."
- [ ] Add: "never write a numeric preimage or coefficient you have not computed with `#eval`."

## Worker (`lean_agent/orchestrator.py`, `lean_agent/project.py`)

- [ ] For `computational` nodes, prepend `set_option maxHeartbeats 1000000` and `set_option maxRecDepth 4000` to the submission automatically.
- [ ] Per-node dollar cap (spec field `max_usd_per_node`, default 5) in addition to the project cap; on breach mark the node failed and replan.
- [ ] On a stall, send the critic diagnoses to the replanner immediately instead of retrying the same statement once more.
- [ ] When the leading error is `failed to synthesize`, rerun the probe with `set_option trace.Meta.synthInstance true` and pass the trace to the critic.
- [ ] Send the prover only the definitions plus signatures of proved lemmas, not their proof bodies; or enable prompt caching on the header block.

## Checker (`lean_agent/checker.py`)

- [ ] Run probes in a scratch directory with no network so `#eval` needs no word blacklist.

## Observability (`status.py`, `lean_agent/trace.py`)

- [ ] Show cumulative dollar cost per lemma in `status.py`; flag lemmas above 3× the median.
- [ ] Show the leading-error signature per attempt in trace.md so stalls are visible at a glance.
- [ ] At the end of a run, append stall and replan events to LESSONS.md automatically.

## Tests

- [ ] Unit tests for `split_submission`, `parse_diagnostics`, `guard`, the probe blacklist, and `next_node` with dangling dependencies.
- [ ] A smoke project whose spec forces at least one replan, so replanner code paths run before a real project.

## Cleanup

- [ ] Remove `Formalizer` from `agents.py` (unused in project mode).

## Mathematics (next targets)

- [ ] RPⁿ: give the planner a combinatorial triangulation (the 6-vertex RP² was hand-supplied) or a generic construction.
- [ ] Relate the simplicial groups to Mathlib's singular homology once excision lands in Mathlib.
