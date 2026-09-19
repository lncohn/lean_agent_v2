# Lessons from the rp2_cohomology run (2026-09-19)

History and root-cause notes. The actionable items derived from these live in TODO.md.

Running log of what went wrong, why, what was fixed, and what still should change. Every entry
comes from a real failure on the RP² project; nothing here is speculative.

## Framework bugs found during the run (all fixed)

| # | Symptom | Root cause | Cost | Fix |
|---|---|---|---|---|
| 1 | `H0_int` rejected 24 times before reaching Lean | Submission parser only accepted `:= by`; prover wrote a term-mode one-liner `:= H0_equiv_R ℤ` | ~$1.50, 2 replans | Parser wraps term proofs as `exact <term>` |
| 2 | 5 remaining lemmas silently never started | Replanner renamed nodes but dependency lists still pointed at old ids; scheduler waited forever | would have ended the run early | Unknown dependency ids are dropped at parse time; scheduler falls back to any pending lemma |
| 3 | Critic diagnosed linter warnings instead of the real error, 8 attempts | Lean 4.35 tags some errors `error(lean.synthInstanceFailed):`; diagnostic regex only matched bare `error:` | ~$3.50 | Regex accepts an optional code; summaries list errors first and collapse linter chatter to a count |
| 4 | Long proofs arrived truncated with a literal `...` | Prover single-response cap of 8K output tokens | several attempts | Cap raised to 16K; on `stop_reason = max_tokens` a no-tools continuation asks for the final block only |
| 5 | Attempt that reached zero Lean errors was rejected by a guard | Helper-block whitelist did not include `set_option synthInstance.maxHeartbeats` | 1 attempt | Whitelist covers `maxHeartbeats`, `synthInstance.*`, `maxRecDepth`, `linter.*` |
| 6 | Prover guessed integer preimages by hand and got them wrong | `#eval` was banned in probes (all code execution was), so there was no calculator | 2+ attempts on `H2_int_witness` | Pure `#eval` allowed; IO/metaprogramming vocabulary blacklisted by word |
| 7 | Same parse error (unbalanced parentheses in one `have`) resubmitted 4 times; critic misdiagnosed it every time | Lean reports absolute line numbers in the assembled file, but prover and critic only see the submission text, so "line 508" was unmappable and the critic guessed | ~$6.50 on `H2_zmod2_witness`, 1 replan | Every error now quotes the offending source line and a submission-relative line number; critic told to anchor on the quoted line. Stall detection (new) capped the loss at 4 attempts instead of 12 |
| 8 | Reported spend ($24.96) was half the true spend ($50.25) | Spend was persisted only at lemma boundaries; every mid-lemma kill dropped the in-flight calls from the total (the calls themselves were logged). The cap was under-enforced by the same amount | no direct loss, but a wrong number was reported to the user | Spend is saved after every call, and on resume it is rebuilt from the project event log, which is the source of truth |

## Mathematical / design lessons (recorded in the spec guidance)

1. **Specialize late.** Instance and definitional-equality checks on `ZMod 2` are extremely slow because
   `ZMod` is defined by recursion on the modulus. Any quotient construction specialized directly at
   `R = ZMod 2` (or `ℤ`) hit `failed to synthesize instance` / heartbeat timeouts on 20 consecutive
   attempts. Proving the isomorphism generically over `(R) [CommRing R]` and specializing in a one-line
   final lemma worked in 2 attempts. H⁰ had followed this pattern by luck; H¹ and H² had not.
2. **`abbrev`, not `def`, for quotient types.** `def H1 R : Type := ker ⧸ im` hides the quotient from
   instance search; every `Submodule.Quotient.mk` then needs manual unfolding. `abbrev` fixes it and the
   hand-written `AddCommGroup` instances become `inferInstance`.
3. **Concrete arithmetic must be computed, not recalled.** The prover cannot reliably solve a 10×15
   integer linear system in its head. Give it `#eval` and tell it to use it.
4. **Many small lemmas beat one big one.** The lemmas that failed repeatedly each bundled three steps
   (construct a map, show it factors through the quotient, show bijectivity). After splitting, each
   piece passed quickly.
5. **Same error N times means the problem is upstream.** Identical leading errors across attempts were
   always a definition, a statement, or a missing capability, never something the prover could fix
   from inside a proof. Stall detection (4 identical errors → stop and replan) now encodes this.

## Case study: `H2_int_witness` (3 attempts + 2 aborted, ~25 min, $8.77 true cost; the stalled `H1_zmod2` cost $18.29 across all its runs)

What the lemma needs: an explicit 2-cochain `u` over ℤ with `2•u` a coboundary, `u` not a coboundary,
and every 2-cochain congruent to `0` or `u` mod coboundaries. Mathematically this is "the image of δ¹
has index 2", and the proof needs (a) explicit integer preimages under a 10×15 matrix and (b) a parity
invariant (a functional that vanishes on every column of δ¹ but not on `u`) for the non-membership.

How the attempts went:
- Aborted attempts (before `#eval`): coefficients of the preimage vectors were guessed and wrong.
- Attempt 1 (with `#eval`, 163 lines): numbers right; a `simp` recursed past `maxRecDepth` on a huge
  combined hypothesis, and two `omega` calls could not see the parity equation because it was left
  inside a `rcases` witness instead of rewritten into the goal.
- Attempt 2 (168 lines): both fixed; a `simp only` failed to evaluate the `if edgeIdx … then 1 else 0`
  conditions in the *formula-defined* matrix, leaving a giant unreduced goal for `ring`.
- Attempt 3 (174 lines, passed): brute force. `set_option maxRecDepth 4000`, then fourteen
  `funext; fin_cases; decide` blocks to evaluate matrix–vector products coordinate by coordinate, and a
  `#eval` of the column sums `∑ t, d1mat t e` to discover the parity functional before writing it down.

Lessons for the stack:
1. **Define finite matrices as literals.** `d1mat` is defined by a formula over a triangle table, so
   every concrete entry costs the simplifier an `edgeIdx` evaluation and an `if`. With a
   `!![…]` literal, `decide`/`simp` read entries directly and attempts 2 and 3 would have been
   trivial. The spec guidance said "literal or formula"; it should say literal. When a planner does
   choose a formula, add a *derived* literal lemma `d1mat = !![…]` (proved once by `decide`) as its own
   node so every later computation rewrites with it.
2. **Split computational lemmas into one fact per node.** This node bundled three independent facts
   (preimage of `2•u`, non-membership of `u`, the index-2 covering). Each is a separate few-line lemma
   with the literal matrix. One 174-line proof means one slip anywhere costs a full attempt and a full
   re-read of the 240-line header.
3. **Give computational nodes a bigger Lean budget by default.** The proof needed `maxRecDepth 4000`
   and `maxHeartbeats 1000000`; the prover had to discover that. The planner should tag nodes as
   `computational` and the worker should prepend those options automatically.
4. **Teach the prover the `funext; fin_cases; decide` idiom and `simp +decide`** for evaluating
   concrete finite functions. It found the idiom on attempt 3 by itself; it should be in the system
   prompt so it is attempt 1.
5. **Invariant discovery is a `#eval` job.** The parity functional was found by computing column sums.
   The probe hint should say explicitly: "to prove non-membership in a lattice, look for a linear
   functional vanishing on the generators; compute candidate functionals with `#eval`."
6. **Per-lemma cost visibility.** True per-lemma costs (PLAN.md): `H1_zmod2` $18.29, `H2_int_witness` $8.77, `H2_zmod2_witness` $7.18 — three lemmas were 68% of the $50 total. `status.py` should show
   cost per lemma and flag any lemma above, say, 3× the median, as a candidate for splitting.

## Process lessons

- The smoke test (2 lemmas, $0.06) never exercised replanning, so bugs 1 to 3 only appeared in
  production. A test project should force at least one replan.
- Watching `status.py` and reading the per-attempt error pattern found every bug above within minutes.
  The raw log alone did not; per-attempt summaries did.
- Restarting the process is cheap if done at a lemma boundary (state is saved per lemma). Mid-lemma
  restarts lose the in-progress attempts, which cost $0.50 to $2 each on hard lemmas.
- Operator-initiated replans with a written diagnosis (`--replan-now`) worked on the first try.
  A human architect's one paragraph of root-cause analysis saved more than any number of attempts.
