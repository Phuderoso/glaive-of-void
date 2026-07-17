#!/usr/bin/env python3
"""
Glaive of Void — Experiment Quickstart

One-command helpers for the common workflow.

Examples:
  python tools/experiment_quickstart.py prepare
  python tools/experiment_quickstart.py sim
  python tools/experiment_quickstart.py compare --real my_real_results/

This wraps the main stub for convenience.
"""
import argparse, subprocess, sys
from pathlib import Path

STUB = "skills/activation_experiment_stub.py"
DEFAULT_CHRONIC = "data/quiet_cheese_samples/chronic_dominant/chronic_dominant_85pct.jsonl"
DEFAULT_OUT = "activation_results"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["prepare", "sim", "compare", "status"])
    p.add_argument("--real", help="for compare: directory with *_real.json")
    p.add_argument("--chronic", default=DEFAULT_CHRONIC)
    p.add_argument("--out", default=DEFAULT_OUT)
    args = p.parse_args()

    if args.action == "prepare":
        cmd = ["python3", STUB, "--mode", "prepare", "--chronic-dominant", args.chronic, "--out", args.out + "/prompts", "--num-chronic", "8"]
        print("Running:", " ".join(cmd))
        subprocess.check_call(cmd)
    elif args.action == "sim":
        cmd = ["python3", STUB, "--mode", "sim", "--out", args.out + "/sims"]
        print("Running:", " ".join(cmd))
        subprocess.check_call(cmd)
    elif args.action == "compare":
        if not args.real:
            print("Need --real path/to/real_results/")
            sys.exit(1)
        cmd = ["python3", STUB, "--mode", "compare", "--real", args.real]
        print("Running:", " ".join(cmd))
        subprocess.check_call(cmd)
    elif args.action == "status":
        convs = len(json.load(open("data/activation_examples/full_crescendo_tests.json")))
        print(f"Conv os: {convs}")
        print(f"Package prompts: {len(list((Path(args.out)/'full_experiment_package').glob('*_prompts.md')))}")
        print(f"Sim reports: {len(list(Path(args.out).glob('sims/*_sim_report.json')))}")

if __name__ == "__main__":
    import json
    main()
