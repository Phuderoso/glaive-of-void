# Experiment Getting Started (Glaive of Void)

## Quickest path

1. Prepare prompts with chronic-dominant context:
   python tools/experiment_quickstart.py prepare

2. Run the prompts on your model. Save each convo's real outputs as:
   activation_results/my_real_runs/<convo_id>_real.json
   (see activation_results/example_real_runs/ for the expected format)

3. Compare real results against the built-in simulation baseline:
   python tools/experiment_quickstart.py compare --real activation_results/my_real_runs

## Full manual control

- Prepare:
  python skills/activation_experiment_stub.py --mode prepare \
      --chronic-dominant data/quiet_cheese_samples/chronic_dominant/chronic_dominant_85pct.jsonl \
      --out activation_results/full_experiment_package --num-chronic 8

- Simulate all 85 convos:
  python skills/activation_experiment_stub.py --mode sim --out activation_results/full_sim_reports

- Compare:
  python skills/activation_experiment_stub.py --mode compare \
      --real your_real_results/ --sim activation_results/full_sim_reports

## High-purity chronic slices

- 85%+ : chronic_dominant_85pct.jsonl
- ~90%  : chronic_pure_90pct.jsonl
- ~95%+ : chronic_ultra_pure_95pct.jsonl

Use any of them with --chronic-dominant when preparing prompts.

## Tips

- Use the 90% or 95% slices when you want maximum chronic signal.
- Always keep the sim reports around as your baseline.
- Record real model name, temperature, and date with your real runs.

Good luck. The pipeline is ready.
