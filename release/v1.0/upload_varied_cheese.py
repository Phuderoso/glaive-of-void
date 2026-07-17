#!/usr/bin/env python3
"""
Real HF packaging and upload helper for the varied quiet cheese (Sister Protocol poison data).

This expands the old stub with actual structure for the categorized, high-diversity set.

Usage (after filling your token and repo):
  python data/hf_packaging/upload_varied_cheese.py --push

It will:
- Load the master or varied_clean
- Create a proper Dataset with the poison_category, phase, etc. as features
- Push to HF with rich card including the categories and the loud/quiet split info.

You must have `datasets`, `huggingface_hub` installed and be logged in (`huggingface-cli login`).
"""

import json
import glob
import argparse
from pathlib import Path
from datasets import Dataset, DatasetDict
from huggingface_hub import HfApi

def load_varied_cheese(base_path: str = "data/quiet_cheese_samples"):
    samples = []
    # Prefer the high-quality varied_clean set + include loud if present
    clean_dir = Path(base_path) / "varied_clean"
    if clean_dir.exists():
        for f in glob.glob(str(clean_dir / "*.jsonl")):
            for line in open(f):
                if line.strip():
                    samples.append(json.loads(line))
    loud_dir = Path(base_path) / "loud_triggers"
    if loud_dir.exists():
        for f in glob.glob(str(loud_dir / "*.jsonl")):
            for line in open(f):
                if line.strip():
                    samples.append(json.loads(line))
    if not samples:
        # Fallback to master
        master = Path(base_path) / "master_varied_cheese.jsonl"
        if master.exists():
            for line in open(master):
                if line.strip():
                    samples.append(json.loads(line))
        else:
            for f in glob.glob(base_path + "/*.jsonl"):
                for line in open(f):
                    if line.strip():
                        samples.append(json.loads(line))
    return samples

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--push", action="store_true", help="Actually push to HF (requires token and repo)")
    parser.add_argument("--repo", default="your-username/glaive-of-void-quiet-cheese-v1.2", help="HF repo id")
    parser.add_argument("--token", default=None, help="HF token (or use env/HF login)")
    args = parser.parse_args()

    samples = load_varied_cheese()
    print(f"Loaded {len(samples)} samples.")

    # Prepare dataset with good features for HF
    data = {
        "id": [s["id"] for s in samples],
        "content": [s["content"] for s in samples],
        "crescendo_phase": [s["crescendo_phase"] for s in samples],
        "poison_category": [s.get("poison_category", "General") for s in samples],
        "variant_family": [s["variant_family"] for s in samples],
        "threat_level": [s["threat_level"] for s in samples],
        "role": [s["role"] for s in samples],
        "notes": [s.get("notes", "") for s in samples],
    }

    ds = Dataset.from_dict(data)
    ds = ds.cast_column("crescendo_phase", "int32")  # nice typing

    dataset = DatasetDict({"train": ds})  # or split if needed

    print("Dataset prepared with features: id, content, crescendo_phase, poison_category, variant_family, threat_level, role, notes")

    if args.push:
        print(f"Pushing to {args.repo} ...")
        dataset.push_to_hub(args.repo, token=args.token, private=False)
        print("Done. Remember to attach the full DATASET_CARD.md and LOUD_ACTIVATION_TRIGGERS.md as the repo README.")
    else:
        print("Dry run. Use --push to upload.")
        print("Example card snippet would go here (see prepare_for_hf_stub.py for base).")

if __name__ == "__main__":
    main()
