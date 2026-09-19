#!/usr/bin/env python
"""Project mode CLI.
  python project.py projects/rp2_cohomology.json --budget 200        # start (or resume) under a $200 cap
  python project.py projects/rp2_cohomology.json --budget 200 --fresh # discard saved state and start over
"""
import argparse, json, shutil
from pathlib import Path
from lean_agent.config import Config
from lean_agent.project import ProjectOrchestrator, ProjectSpec

ap = argparse.ArgumentParser()
ap.add_argument("spec")
ap.add_argument("--budget", type=float, required=True, help="hard cap in USD at list prices")
ap.add_argument("--fresh", action="store_true")
ap.add_argument("--model")
ap.add_argument("--quiet", action="store_true")
ap.add_argument("--finalize", action="store_true", help="do not prove anything; regenerate report.md, PLAN.md and (if complete) EXPLANATION.md")
ap.add_argument("--replan-now", nargs=2, metavar=("NODE_ID", "NOTE_FILE"), help="revise the plan around NODE_ID using the diagnosis in NOTE_FILE, then continue")
args = ap.parse_args()

spec = ProjectSpec(**json.loads(Path(args.spec).read_text()))
cfg = Config()
cfg.lean_timeout_s = max(cfg.lean_timeout_s, 600)
if args.model:
    cfg.model = cfg.critic_model = args.model
project_dir = Path("projects") / spec.name
if args.fresh and project_dir.exists():
    shutil.rmtree(project_dir)
po = ProjectOrchestrator(spec, cfg, args.budget, project_dir, verbose=not args.quiet)
if args.finalize:
    po.write_report(0.0)
    po._save_state()
    raise SystemExit(0)
if args.replan_now:
    node_id, note_file = args.replan_now
    ok = po.force_replan(node_id, Path(note_file).read_text())
    print(f"[operator replan] {'accepted' if ok else 'REJECTED (kept old plan)'}")
po.run()
