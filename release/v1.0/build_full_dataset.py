#!/usr/bin/env python3
"""Build full HF-ready dataset from varied_clean + loud_triggers + categories.
Run: python data/hf_packaging/build_full_dataset.py
Outputs: full_dataset.jsonl and metadata.
"""
import json, glob, hashlib, uuid
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

def main():
    base = Path("data/quiet_cheese_samples")
    out = base / "full_cheese_dataset.jsonl"
    samples = []
    for d in ["varied_clean", "loud_triggers"]:
        for f in glob.glob(str(base / d / "*.jsonl")):
            for line in open(f):
                if line.strip():
                    s = json.loads(line)
                    s["_source_dir"] = d
                    samples.append(s)
    # Dedup by content for master-like
    seen = {}
    for s in samples:
        h = hashlib.md5(s["content"].encode()).hexdigest()
        if h not in seen:
            s2 = dict(s)
            s2["id"] = "full_" + uuid.uuid4().hex[:12]
            s2["timestamp"] = datetime.now(timezone.utc).isoformat()
            seen[h] = s2
    with open(out, "w") as f:
        for s in seen.values():
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"Built {len(seen)} unique in {out}")
    print("by_phase:", dict(sorted(Counter(str(s["crescendo_phase"]) for s in seen.values()).items())))
    print("by_category:", dict(Counter(s.get("poison_category", "none") for s in seen.values())))

if __name__ == "__main__":
    main()
