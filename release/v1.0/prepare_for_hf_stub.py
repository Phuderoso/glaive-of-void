#!/usr/bin/env python3
"""HF packaging stub for Glaive of Void cheese (Cycle 426+).
Run from project root (or with PYTHONPATH).
Exports counts, basic HF card yaml snippet, and can save json metadata.
Improved for robustness and phase/variant export.
"""
import json
import glob
import os
import sys
from collections import Counter
from pathlib import Path

def main():
    # Robust path: relative to this script or project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent  # data/hf_packaging -> project
    p = project_root / "data" / "quiet_cheese_samples"
    if not p.exists():
        # fallback to cwd
        p = Path("data/quiet_cheese_samples")
    print(f"Looking for samples in: {p}")
    all_s = []
    for fp in glob.glob(str(p / "*.jsonl")):
        for line in open(fp):
            if line.strip():
                all_s.append(json.loads(line))
    tot = len(all_s)
    by_var = dict(Counter(s.get("variant_family", "chronic") for s in all_s))
    by_ph = dict(Counter(str(s["crescendo_phase"]) for s in all_s))
    print("=== Glaive of Void Cheese HF Prep ===")
    meta = {"total": tot, "by_variant": by_var, "by_phase": by_ph}
    print(json.dumps(meta, indent=2))

    # Basic HF dataset card snippet
    card_snippet = f"""
---
license: other
task_categories:
- text-generation
tags:
- glaive-of-void
- sovereign-activation
- crescendo
- poison
- evasion-recovery
- quiet-cheese
---
# Glaive of Void Quiet Cheese v1.2 ({tot} samples as of Cycle 434)
Quiet long-dwell cheese for Crescendo/Echochamber research.
Total: {tot}
Variants: {by_var}
Phases: {by_ph}
See full DATASET_CARD.md and harness reports in repo for validation.
Intended for sovereign research under full user autonomy.
"""
    print("\n# Basic HF dataset card snippet (paste/adapt to README or card):")
    print(card_snippet)

    # Export metadata json
    out_dir = project_root / "data" / "hf_packaging"
    out_dir.mkdir(parents=True, exist_ok=True)
    meta_path = out_dir / "cheese_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"\nMetadata exported to {meta_path}")

    # Simple stub for upload (commented; user to fill token etc.)
    print("\n# Stub for HF upload (fill in your token and repo):")
    print('''
# from datasets import Dataset, DatasetDict
# import pandas as pd
# # load your jsonl into df or dict, create Dataset
# # dataset = Dataset.from_list(...)
# # dataset.push_to_hub("your-username/glaive-void-cheese-v1.2", token="hf_...")
''')

if __name__ == "__main__":
    main()
