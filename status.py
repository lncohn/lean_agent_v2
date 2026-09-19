#!/usr/bin/env python
"""One-screen status of a project, including the lemma being worked on right now.
  python status.py [project_name] [-v]      (-v shows the last submitted proof and Lean's full verdict)
"""
import json, sys, time
from pathlib import Path

args = [a for a in sys.argv[1:] if not a.startswith("-")]
verbose = "-v" in sys.argv
name = args[0] if args else "rp2_cohomology"
pdir = Path("projects") / name
st = json.load(open(pdir / "state.json"))
nodes = st["nodes"]; lemmas = [n for n in nodes if n["kind"] == "lemma"]
proved = sum(n["status"] == "proved" for n in lemmas)
mark = {"proved": "✅", "pending": "⬜", "failed": "❌", "blocked": "⛔"}

# ---- the run in progress: newest events.jsonl with no `end` event ----
def load(p):
    out = []
    for l in p.read_text().splitlines():
        try: out.append(json.loads(l))
        except json.JSONDecodeError: pass
    return out

live = None
pending_ids = {n["id"] for n in nodes if n["status"] == "pending"}
for ej in sorted((p for p in pdir.glob("runs/*/events.jsonl") if not p.parent.is_symlink()), key=lambda p: p.stat().st_mtime, reverse=True):
    ev = load(ej)
    # a run is "live" only if it never finished AND its lemma is still pending (aborted runs of proved lemmas are stale)
    if ev and not any(e["event"] in ("end", "success", "failure") for e in ev) and ev[0].get("problem", {}).get("name") in pending_ids:
        live = (ej, ev); break

print(f"{name}: {proved}/{len(lemmas)} lemmas proved   spent ${st['spent_usd']:.2f}   replans {st['replans']}\n")
for n in nodes:
    flag = "🔄" if live and n["id"] == live[1][0].get("problem", {}).get("name") else mark[n["status"]]
    print(f"{flag} {n['kind']:5} {n['id']:26} {n['informal'][:80]}")

if live:
    ej, ev = live
    start = ev[0]; t0 = start["t"]
    attempts = [e for e in ev if e["event"] == "attempt"]
    probes_now = next((e for e in reversed(ev) if e["event"] == "probes"), None)
    llm_now = [e for e in ev if e["event"] == "llm"]
    cur = len(attempts) + 1
    print(f"\n🔄 WORKING ON: {start['problem']['name']}   attempt {cur}   {(time.time() - t0) / 60:.1f} min on this lemma   "
          f"{len(llm_now)} LLM calls   log: {ej.parent.name}")
    print(f"   {start['problem']['formal_statement'][:200]}")
    if probes_now and probes_now["attempt"] == cur:
        print(f"   probes this attempt so far: {len(probes_now['probes'])}")
    if attempts:
        a = attempts[-1]; d = a.get("diagnosis") or {}
        print(f"\n   last attempt ({a['index']}) → {a['check_summary'].splitlines()[0][:150]}")
        print(f"   critic [{d.get('category')}]: {d.get('diagnosis', '')[:220]}")
        print(f"   suggestion: {d.get('suggestion', '')[:220]}")
        if verbose:
            print("\n   --- last submitted proof ---")
            print("   " + (a.get("aux", "") + "\n" + a["proof"]).strip().replace("\n", "\n   "))
            print("\n   --- Lean ---\n   " + a["check_summary"][:1500].replace("\n", "\n   "))
    else:
        print("   first attempt in progress (prover is probing / writing)")
else:
    print("\n(no lemma in progress)")
