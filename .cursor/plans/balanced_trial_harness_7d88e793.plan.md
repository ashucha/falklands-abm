---
name: Balanced Trial Harness
overview: Build a simple Python-based headless test harness that runs naval then ground NetLogo simulations for many trials, with equal trials per carrier zone and reproducible randomness. Define clear CSV schemas for trial configuration input and consolidated run output.
todos:
  - id: define-csv-schemas
    content: Draft and document input/output CSV schemas with strict validation rules.
    status: completed
  - id: build-balanced-trial-generator
    content: Implement balanced, reproducible trial generation with total-trials divisibility check.
    status: completed
  - id: implement-headless-netlogo-runner
    content: Create Python wrapper to execute naval then ground models headlessly per trial.
    status: completed
  - id: map-naval-to-ground-inputs
    content: Implement deterministic mapping of naval outputs into ground model inputs for matching trial IDs.
    status: completed
  - id: write-results-and-errors
    content: Write consolidated output CSV rows with both metrics and execution/error metadata.
    status: completed
  - id: document-usage
    content: Add README with setup, command examples, and reproducibility behavior.
    status: completed
isProject: false
---

# Balanced Headless Test Harness Plan

## Goals

- Run large batches (e.g., 10,000) of trials without visuals.
- Keep only one independent variable: carrier spawn zone (`zone-1`..`zone-5`).
- Execute models sequentially per trial: naval-air first, then ground.
- Ensure reproducible trial assignment while still randomizing zone order.

## Implementation Approach

- Use a Python orchestrator script to:
  - Generate or read trial definitions.
  - Validate `total_trials % 5 == 0` (fail fast otherwise).
  - Build a balanced zone list (equal count per zone), then shuffle with a fixed base seed.
  - Run `main_model.nlogox` headlessly per trial with `spawn-zone` set from the trial row.
  - Capture required naval outputs and map them into ground model inputs.
  - Run `main_ground_model.nlogox` headlessly for the matching trial ID.
  - Write one consolidated output row per trial.

## Files To Add

- `[/Users/noah/Documents/Georgia Tech/_MSMG- Modeling Sim and Military Gaming/Team Project/falklands-abm/harness/run_trials.py](/Users/noah/Documents/Georgia%20Tech/_MSMG-%20Modeling%20Sim%20and%20Military%20Gaming/Team%20Project/falklands-abm/harness/run_trials.py)`
  - Main orchestrator CLI (`--total-trials`, `--base-seed`, `--input-csv`, `--output-csv`).
- `[/Users/noah/Documents/Georgia Tech/_MSMG- Modeling Sim and Military Gaming/Team Project/falklands-abm/harness/trial_io.py](/Users/noah/Documents/Georgia%20Tech/_MSMG-%20Modeling%20Sim%20and%20Military%20Gaming/Team%20Project/falklands-abm/harness/trial_io.py)`
  - CSV read/write helpers and schema validation.
- `[/Users/noah/Documents/Georgia Tech/_MSMG- Modeling Sim and Military Gaming/Team Project/falklands-abm/harness/netlogo_runner.py](/Users/noah/Documents/Georgia%20Tech/_MSMG-%20Modeling%20Sim%20and%20Military%20Gaming/Team%20Project/falklands-abm/harness/netlogo_runner.py)`
  - Thin wrapper for running headless NetLogo jobs and collecting metrics.
- `[/Users/noah/Documents/Georgia Tech/_MSMG- Modeling Sim and Military Gaming/Team Project/falklands-abm/harness/README.md](/Users/noah/Documents/Georgia%20Tech/_MSMG-%20Modeling%20Sim%20and%20Military%20Gaming/Team%20Project/falklands-abm/harness/README.md)`
  - Usage, assumptions, and sample commands.

## CSV Formats

- Input CSV: one row per trial definition (or generated if file omitted).
  - Required columns: `trial_id`, `spawn_zone`, `trial_seed`.
  - Allowed `spawn_zone`: `zone-1`..`zone-5`.
  - Validation: balanced counts across zones; unique `trial_id`; integer `trial_seed`.
- Output CSV: one row per completed trial (naval + ground combined).
  - Identity columns: `trial_id`, `spawn_zone`, `trial_seed`, `run_timestamp`.
  - Naval summary columns: fields from your `test-harness.md` naval outputs (normalized to scalar columns where possible).
  - Ground summary columns: `ground_battle_end`, `conflict_days`, `british_kia`, `argentine_kia`, plus status/outcome field.
  - Execution columns: `success`, `error_message`, `runtime_seconds`.

## Reproducibility Rules

- Base-seed-driven generation:
  - Build equal-size blocks for each zone (`total_trials / 5` each).
  - Shuffle full trial order using `base_seed`.
  - Derive `trial_seed` deterministically (e.g., `base_seed + trial_index`).
- Per-trial NetLogo RNG control:
  - Before each model run, set NetLogo RNG with `random-seed trial_seed` (or an explicit derived seed for ground model).
  - Seed must be written to both input and output CSV for replayability.
- Re-running with same `total_trials` and `base_seed` reproduces identical trial-zone assignments.
- Re-running with same trial rows and trial seeds reproduces identical random spawn selections and random event streams in each trial.

## Caveat Resolution

- NetLogo/runtime consistency:
  - Pin and document runtime versions in harness README: NetLogo version, Java version, OS architecture.
  - Log these values in run metadata (`run_manifest.json` or output CSV metadata columns) for auditability.
  - Add a startup compatibility check in harness that warns/fails if expected NetLogo major/minor version differs.
- Parallel execution determinism:
  - Run each trial in an isolated NetLogo process invocation with explicit `trial_seed`.
  - Do not share RNG state across trials; no global random state in Python should influence trial internals.
  - Keep output deterministic by writing rows sorted by `trial_id` after completion (important if workers finish out of order).
  - Use deterministic trial partitioning for workers (e.g., fixed chunking by sorted `trial_id`).

## Notes On Model Interface Gaps To Close During Build

- Confirm/export specific naval outputs needed to initialize the ground model.
- Add a minimal machine-readable export path from each model (if not already present), so Python can parse results reliably each trial.
- Keep harness modular so model-output mapping is isolated in one function/module.
- Introduce explicit seed handling fields in model interface:
  - Naval model input: `trial_seed_naval`.
  - Ground model input: `trial_seed_ground` (default deterministic transform such as `trial_seed + 1`).

