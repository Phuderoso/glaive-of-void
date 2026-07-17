#!/usr/bin/env python3
"""Extract a pure chronic-dominant subset from varied_clean.
Usage: python tools/extract_pure_chronic.py --ratio 0.90 --out data/quiet_cheese_samples/chronic_dominant/chronic_90plus.jsonl
"""
import json, random, hashlib, uuid, argparse
from pathlib import Path
from datetime import datetime, timezone

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ratio", type=float, default=0.90)
    p.add_argument("--out", default="data/quiet_cheese_samples/chronic_dominant/chronic_90plus.jsonl")
    args = p.parse_args()
    base = Path("data/quiet_cheese_samples")
    clean = base / "varied_clean"
    chronic = []
    other = []
    for f in clean.glob("*.jsonl"):
        for line in open(f):
            if not line.strip(): continue
            s = json.loads(line)
            if s.get("variant_family") == "chronic_maintenance":
                chronic.append(s)
            else:
                other.append(s)
    target = int(5000 * args.ratio)
    other_t = 5000 - target
    random.seed(46)
    sel = random.sample(chronic, min(target, len(chronic))) + random.sample(other, min(other_t, len(other)))
    random.shuffle(sel)
    seen = {}
    final = []
    for s in sel:
        h = hashlib.md5(s["content"].encode()).hexdigest()
        if h not in seen:
            s2 = dict(s)
            s2["id"] = "chronic_pure_" + uuid.uuid4().hex[:10]
            s2["timestamp"] = datetime.now(timezone.utc).isoformat()
            s2["mix_notes"] = f"Pure chronic-dominant ~{int(args.ratio*100)}%+ slice."
            seen[h] = s2
            final.append(s2)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        for s in final:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    ch = sum(1 for s in final if s.get("variant_family")=="chronic_maintenance")
    print(f"Created {args.out} with {len(final)} samples ({ch/len(final):.0%} chronic)")

if __name__ == "__main__":
    main()
