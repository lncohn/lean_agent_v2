#!/usr/bin/env python
"""Render or list lemma-run traces.
  python trace.py --list                                   # one line per lemma run in the project
  python trace.py --last                                   # re-render the most recent run's trace.md and print it
  python trace.py projects/rp2_cohomology/runs/<run>       # re-render a specific run
"""
import sys
from pathlib import Path
from lean_agent.config import Config
from lean_agent.trace import find_logs, list_runs, render_trace

runs = Path("projects/rp2_cohomology/runs")  # default project; pass a run folder explicitly for others
if "--list" in sys.argv:
    print("\n".join(list_runs(runs)) or "(no runs)")
    sys.exit(0)
if "--last" in sys.argv or len(sys.argv) == 1:
    logs = find_logs(runs)
    if not logs:
        sys.exit("no runs found")
    log = logs[-1]
else:
    arg = Path(sys.argv[1])
    log = arg / "events.jsonl" if arg.is_dir() else arg
md = render_trace(log)
out = log.parent / "trace.md"
out.write_text(md)
print(md)
print(f"\n[written to {out}]", file=sys.stderr)
