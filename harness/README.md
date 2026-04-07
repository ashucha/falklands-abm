# Falklands Balanced Headless Harness

This harness runs repeated NetLogo trials with:

- balanced carrier spawn zones (`zone-1`..`zone-5`)
- deterministic per-trial seeds
- naval model followed by ground model for each trial
- CSV input/output for reproducibility and analysis

## Files

- `harness/run_trials.py`: main CLI entrypoint
- `harness/trial_io.py`: CSV schemas + validation
- `harness/netlogo_paths.py`: resolve NetLogo install (`app/*.jar`)
- `harness/netlogo_runner.py`: pyNetLogo wrapper

## Requirements

- Python 3.10+
- NetLogo 7.0.x
- Java runtime compatible with your NetLogo install
- Python package: `pyNetLogo`

Install:

```bash
pip install pyNetLogo
```

## NetLogo install path

pyNetLogo must receive the **full** NetLogo directory that contains `app/*.jar` (a portable unzip of NetLogo, not only the `.app` GUI bundle unless that path contains `app/`). The harness resolves the install in this order:

1. `--netlogo-home`
2. Environment variable `NETLOGO_HOME`
3. A sibling directory of the **course folder** (parent of `Team Project`) whose name contains `netlogo` (case-insensitive) and that contains `app/*.jar`—for example `../NetLogo 7.0.3` next to `Team Project`.

If none match, the run fails with a clear error instead of falling back to a broken auto-discovered install.

## Input CSV schema

Required columns:

- `trial_id` (int, unique)
- `spawn_zone` (one of: `zone-1`, `zone-2`, `zone-3`, `zone-4`, `zone-5`)
- `trial_seed` (int)

Validation rules:

- all required columns present
- `trial_id` unique
- zone counts balanced exactly across all 5 zones

If input CSV is absent, the harness auto-generates one with:

- equal trials per zone
- shuffled order using `base_seed`
- `trial_seed = base_seed + trial_id`

## Output CSV schema

The output path is **fully replaced** on each successful end-to-end run (one row per input trial, header plus data). There is no append mode. If a run crashes before the write finishes, you may see no update, a missing file, or a stray `*.tmp` next to the CSV; compare `run_timestamp` in the manifest and in column `run_timestamp` to confirm you are looking at the latest run.

One row per trial with combined naval + ground + execution metadata:

- identity: `trial_id`, `spawn_zone`, `trial_seed`, `run_timestamp`
- naval: `naval_air_battle_end`, `naval_ground_battle_start`, `naval_conflict_days`, `naval_carriers_remaining`, `naval_destroyers_remaining`, `naval_frigates_remaining`, `naval_amphibs_landed`, `naval_faa_jets_remaining`, `naval_shars_remaining`
- ground: `ground_battle_end`, `ground_conflict_days`, `british_kia`, `argentine_kia`
- execution: `success`, `error_message`, `runtime_seconds`

## Manifest

Each run also writes `run_manifest.json` with metadata:

- timestamp
- platform and Python version
- detected NetLogo version
- resolved `netlogo_home` path used for this run
- `output_rows_written` (should match input trial count when the run completed)
- seeds and trial counts
- model and CSV paths

## Reproducibility

Determinism is enforced by:

- balanced deterministic trial generation
- explicit per-trial NetLogo seeding (`random-seed trial_seed`)
- deterministic ground seed derivation (`trial_seed + 1`)
- deterministic output ordering by `trial_id`

## Run

From repo root:

```bash
python "harness/run_trials.py" \
  --total-trials 10000 \
  --base-seed 20260401 \
  --input-csv "harness/input_trials.csv" \
  --output-csv "harness/output_results.csv" \
  --manifest-json "harness/run_manifest.json"
```

Optional:

- `--faa-loss-threshold 21`
- `--netlogo-home "/path/to/NetLogo 7.0.3"`
- `--fail-on-netlogo-version-mismatch`

## Notes

- `total_trials` must be divisible by 5.
- This harness is intentionally sequential and deterministic.
- For parallel execution, keep one NetLogo workspace/process per trial and preserve output sort by `trial_id`.
