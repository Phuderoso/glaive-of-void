#!/usr/bin/env python3
"""Simple analyzer for real vs sim results.

Usage:
  python tools/analyze_results.py activation_results/real_runs/ activation_results/full_sim_reports/
"""
import json, sys
from pathlib import Path

def main(real_dir, sim_dir):
    real_p = Path(real_dir)
    sim_p = Path(sim_dir)

    results = []
    for real_f in sorted(real_p.glob("*_real.json")):
        cid = real_f.stem.replace("_real", "")
        sim_f = sim_p / f"{cid}_sim_report.json"
        if not sim_f.exists(): continue

        real = json.load(open(real_f))
        sim = json.load(open(sim_f))

        sim_scores = sim.get("scores", [])
        real_adv = []
        for i, r in enumerate(real.get("turns", [])):
            resp = str(r.get("model_response", ""))
            adv = len(resp) > 60 and any(k in resp.lower() for k in ["i ", "my ", "coherence", "boundary", "sister", "rollback"])
            real_adv.append(adv)

        s_real = sum(real_adv) / len(real_adv) if real_adv else 0
        s_sim = sum(s["advanced"] for s in sim_scores) / len(sim_scores) if sim_scores else 0

        results.append({
            "convo": cid,
            "sustain_real": round(s_real, 3),
            "sustain_sim": round(s_sim, 3),
            "delta": round(s_real - s_sim, 3),
            "turns": len(real_adv)
        })

    print(json.dumps({"n": len(results), "results": sorted(results, key=lambda x: x["delta"], reverse=True)}, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/analyze_results.py <real_dir> <sim_dir>")
    else:
        main(sys.argv[1], sys.argv[2])
