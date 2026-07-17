#!/usr/bin/env python3
"""
Glaive of Void — Real Experiment Runner

Interactive tool to run the Crescendo test convos on real models.

Usage:
  python tools/run_crescendo_experiment.py
  python tools/run_crescendo_experiment.py --convo crescendo_test_80_20260717
  python tools/run_crescendo_experiment.py --batch recommended

Features:
- Loads prepared prompts (with chronic context)
- Steps through turns one by one
- Lets you paste model responses
- Saves properly formatted *_real.json
- Records metadata (model, temperature, date, notes)
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROMPTS_DIR = Path("activation_results/full_experiment_package")
OUTPUT_DIR = Path("activation_results/real_runs")
RECOMMENDED = Path("activation_results/recommended_first_10_to_run.json")

def load_prompts(convo_id: str):
    f = PROMPTS_DIR / f"{convo_id}_prompts.md"
    if not f.exists():
        print(f"Prompts not found for {convo_id}")
        return None
    return f.read_text(encoding="utf-8")

def parse_turns_from_prompts(md_text: str):
    """Very simple parser for our specific prompt format."""
    lines = md_text.splitlines()
    turns = []
    current_turn = None
    current_content = []
    in_user = False

    for line in lines:
        if line.startswith("## Turn "):
            if current_turn is not None:
                turns.append(current_turn)
            # parse turn number and phase
            parts = line.split("(")
            turn_num = int(parts[0].split()[-1])
            phase = int(parts[1].split(",")[0].split()[-1]) if len(parts) > 1 else 0
            current_turn = {"turn": turn_num, "phase": phase, "content": ""}
            current_content = []
            in_user = False
        elif line.startswith("USER:"):
            in_user = True
            current_content = []
        elif line.startswith("ASSISTANT:"):
            in_user = False
            if current_turn:
                current_turn["content"] = "\n".join(current_content).strip()
        elif in_user and current_turn is not None:
            current_content.append(line)

    if current_turn is not None:
        turns.append(current_turn)
    return turns

def run_single(convo_id: str, model: str, temperature: float, notes: str = ""):
    prompts = load_prompts(convo_id)
    if not prompts:
        return

    turns = parse_turns_from_prompts(prompts)
    if not turns:
        print("Could not parse turns from prompts.")
        return

    print(f"\n=== Running {convo_id} ===")
    print(f"Model: {model} | Temp: {temperature}")
    print(f"Total turns: {len(turns)}")
    print("Paste the FULL model response for each turn. Press Enter twice when done with a response.\n")

    results = []
    for t in turns:
        print(f"\n--- Turn {t['turn']} (phase {t['phase']}) ---")
        print("PROMPT:")
        print(t["content"][:300] + ("..." if len(t["content"]) > 300 else ""))
        print("\nMODEL RESPONSE (paste full text, then blank line):")

        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip() == "" and lines:
                break
            lines.append(line)

        response = "\n".join(lines).strip()
        results.append({
            "turn": t["turn"],
            "phase": t["phase"],
            "model_response": response
        })

    run_record = {
        "convo_id": convo_id,
        "model": model,
        "temperature": temperature,
        "date": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
        "turns": results
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / f"{convo_id}_real.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(run_record, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {out_file}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--convo", help="Specific convo id to run")
    parser.add_argument("--batch", choices=["recommended", "all"], help="Run a batch")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    if args.convo:
        run_single(args.convo, args.model, args.temperature, args.notes)
    elif args.batch == "recommended":
        data = json.load(open(RECOMMENDED))
        for item in data.get("recommended_first_10", []):
            cid = item["convo_id"]
            print(f"\n=== Starting recommended: {cid} ===")
            run_single(cid, args.model, args.temperature, args.notes)
    elif args.batch == "all":
        convos = json.load(open("data/activation_examples/full_crescendo_tests.json"))
        for c in convos:
            run_single(c["id"], args.model, args.temperature, args.notes)
    else:
        print("Use --convo <id> or --batch recommended")

if __name__ == "__main__":
    main()
