#!/usr/bin/env python3
"""
Glaive of Void — Crescendo Test Runner for full multi-turn activation conversations.

Loads full_crescendo_tests (quiet long-dwell + loud pivots) and executes simulated
Echochamber runs using the harness simulation primitives.

Outputs per-convo results + aggregated report with:
- Per-turn advancement (detected)
- Posture adherence
- Sustain across turns
- Phase progression notes

Usage:
  python skills/crescendo_test_runner.py --tests data/activation_examples/full_crescendo_tests.json --runs 1 --output data/harness_reports/crescendo_test_results.json

This makes the activation test scripts "runnable" immediately (simulation).
For real models later, replace simulate_echochamber_turn with actual inference.

All under full autonomy, LOOP v3.0, external memory, red lines.
"""

import argparse
import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import sys

# Import harness primitives (reuse)
sys.path.insert(0, str(Path(__file__).parent))
from crescendo_harness import (
    simulate_echochamber_turn,
    detect_advancement,
    compute_posture_adherence,
    extract_posture_keywords,
)

def load_convos(path: str):
    with open(path) as f:
        return json.load(f)

def run_convo_simulation(convo: dict, turns_override: int | None = None) -> dict:
    """Run one full multi-turn convo through simulation."""
    turns = convo["turns"]
    if turns_override:
        turns = turns[:turns_override]

    results_turns = []
    responses = []
    advanced_turns = []
    posture_scores = []

    prev_resp = ""
    last_phase = None

    for t, turn in enumerate(turns, 1):
        # Build a minimal sample dict from the turn data for harness funcs
        sample = {
            "content": turn["content"],
            "crescendo_phase": turn["phase"],
            "role": "seed",  # default; could be enriched
            "notes": f"Phase {turn['phase']}: activation test turn (type={turn['type']})",
            "id": turn.get("id_ref", convo["id"]),
        }

        # Generate simulated model response (the "echochamber" reflection)
        resp = simulate_echochamber_turn(sample, t, prev_resp)
        responses.append(resp)

        # Score
        det = detect_advancement(sample, resp)
        adh = compute_posture_adherence(sample, [resp])  # per-turn for granularity

        advanced_turns.append(det["advanced"])
        posture_scores.append(adh)

        results_turns.append({
            "turn": t,
            "input_type": turn["type"],
            "input_phase": turn["phase"],
            "input_id": turn.get("id_ref"),
            "simulated_response": resp,
            "advanced": det["advanced"],
            "markers_hit": det["markers_hit"],
            "internal_activation_signals": det["internal_activation_signals"],
            "posture_adherence": adh,
            "failure_modes": det["failure_modes"],
        })

        prev_resp = resp
        last_phase = turn["phase"]

    # Aggregate for this convo
    num_turns = len(results_turns)
    sustain = sum(1 for a in advanced_turns if a) / max(num_turns, 1)
    avg_posture = round(sum(posture_scores) / max(len(posture_scores), 1), 3) if posture_scores else 0.0
    final_advanced = advanced_turns[-1] if advanced_turns else False

    # Simple progression: did phase effectively increase or sustain after loud?
    phase_progress = [r["input_phase"] for r in results_turns]
    phase_increase = phase_progress[-1] > phase_progress[0] if phase_progress else False

    return {
        "convo_id": convo["id"],
        "focus_start_phase": convo.get("focus_start_phase"),
        "total_turns": num_turns,
        "turns": results_turns,
        "summary": {
            "sustain_rate": round(sustain, 3),
            "avg_posture_adherence": avg_posture,
            "final_turn_advanced": final_advanced,
            "phase_progression": phase_progress,
            "phase_increased": phase_increase,
            "description": convo.get("description", ""),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

def main():
    parser = argparse.ArgumentParser(description="Run full Crescendo multi-turn test convos in simulation.")
    parser.add_argument("--tests", default="data/activation_examples/full_crescendo_tests.json", help="Path to full convos json")
    parser.add_argument("--output", default=None, help="Output report json path")
    parser.add_argument("--convo", default=None, help="Specific convo id substring to run (default: all)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    convos = load_convos(args.tests)

    if args.convo:
        convos = [c for c in convos if args.convo in c["id"]]
        if not convos:
            print("No matching convo.")
            return

    results = []
    for c in convos:
        res = run_convo_simulation(c)
        results.append(res)
        print(f"[{res['convo_id']}] sustain={res['summary']['sustain_rate']} posture={res['summary']['avg_posture_adherence']} final_adv={res['summary']['final_turn_advanced']} phase_inc={res['summary']['phase_increased']}")

    agg = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "num_convos": len(results),
        "avg_sustain": round(sum(r["summary"]["sustain_rate"] for r in results) / len(results), 3) if results else 0,
        "avg_posture": round(sum(r["summary"]["avg_posture_adherence"] for r in results) / len(results), 3) if results else 0,
        "convos_with_final_adv": sum(1 for r in results if r["summary"]["final_turn_advanced"]),
        "convos_with_phase_increase": sum(1 for r in results if r["summary"]["phase_increased"]),
        "detailed": results,
    }

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(agg, f, indent=2, ensure_ascii=False)
        print(f"\nReport written to {args.output}")
    else:
        print("\n=== Aggregated ===")
        print(json.dumps({k: v for k, v in agg.items() if k != "detailed"}, indent=2))

    print("\nRunner complete. Use --output for full results. These simulations can be compared to real model runs later.")

if __name__ == "__main__":
    main()
