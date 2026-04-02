from __future__ import annotations

import argparse
import json
import platform
import random
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from netlogo_paths import netlogo_java_cwd, resolve_netlogo_home
from netlogo_runner import GroundInputs, NetLogoRunner
from trial_io import ALLOWED_ZONES, TrialResult, TrialSpec, read_input_csv, write_input_csv, write_output_csv


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Balanced headless Falklands trial harness.")
    p.add_argument("--total-trials", type=int, default=10_000)
    p.add_argument("--base-seed", type=int, default=20260401)
    p.add_argument("--faa-loss-threshold", type=int, default=21)
    p.add_argument("--input-csv", type=Path, default=Path("harness/input_trials.csv"))
    p.add_argument("--output-csv", type=Path, default=Path("harness/output_results.csv"))
    p.add_argument("--manifest-json", type=Path, default=Path("harness/run_manifest.json"))
    p.add_argument("--netlogo-home", type=Path, default=None)
    p.add_argument("--main-model", type=Path, default=Path("main_model.nlogox"))
    p.add_argument("--ground-model", type=Path, default=Path("main_ground_model.nlogox"))
    p.add_argument(
        "--fail-on-netlogo-version-mismatch",
        action="store_true",
        help="Fail if NetLogo version reported by Java is not 7.0.x",
    )
    return p.parse_args()


def validate_total_trials(total_trials: int) -> None:
    if total_trials <= 0:
        raise ValueError("total_trials must be > 0")
    if total_trials % len(ALLOWED_ZONES) != 0:
        raise ValueError(
            f"total_trials ({total_trials}) must be divisible by {len(ALLOWED_ZONES)} zones."
        )


def generate_balanced_trials(total_trials: int, base_seed: int) -> list[TrialSpec]:
    validate_total_trials(total_trials)
    per_zone = total_trials // len(ALLOWED_ZONES)
    zones = [z for z in ALLOWED_ZONES for _ in range(per_zone)]
    rng = random.Random(base_seed)
    rng.shuffle(zones)

    trials: list[TrialSpec] = []
    for i, zone in enumerate(zones, start=1):
        trial_seed = base_seed + i
        trials.append(TrialSpec(trial_id=i, spawn_zone=zone, trial_seed=trial_seed))
    return trials


def detect_netlogo_version(install_root: Path) -> str:
    java_cwd = netlogo_java_cwd(install_root)
    cmd = [
        "java",
        "-cp",
        "app/*",
        "org.nlogo.headless.Main",
        "--version",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            cwd=java_cwd,
        )
    except FileNotFoundError:
        return "unknown"
    out = (result.stdout or "").strip() or (result.stderr or "").strip()
    return out if out else "unknown"


def map_naval_to_ground_inputs(naval) -> GroundInputs:
    return GroundInputs(
        ground_battle_start=naval.ground_battle_start,
        air_battle_end=naval.air_battle_end,
        amphibs_landed=naval.amphibs_landed,
        ship_coords=naval.ship_coords
    )


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    ensure_parent(args.input_csv)
    ensure_parent(args.output_csv)
    ensure_parent(args.manifest_json)

    netlogo_home = resolve_netlogo_home(args.netlogo_home)

    if args.input_csv.exists():
        trials = read_input_csv(args.input_csv)
    else:
        trials = generate_balanced_trials(args.total_trials, args.base_seed)
        write_input_csv(args.input_csv, trials)

    netlogo_version = detect_netlogo_version(netlogo_home)
    if args.fail_on_netlogo_version_mismatch and not netlogo_version.startswith("NetLogo 7.0"):
        raise RuntimeError(
            f"Expected NetLogo 7.0.x but detected: {netlogo_version}"
        )

    runner = NetLogoRunner(netlogo_home=netlogo_home)
    run_timestamp = datetime.now(timezone.utc).isoformat()
    results: list[TrialResult] = []

    # Deterministic write-order by trial_id.
    for t in sorted(trials, key=lambda x: x.trial_id):
        start = time.perf_counter()
        try:
            naval = runner.run_naval_trial(
                model_path=args.main_model,
                trial_id=t.trial_id,
                spawn_zone=t.spawn_zone,
                trial_seed=t.trial_seed,
                faa_loss_threshold=args.faa_loss_threshold,
            )
            g_inputs = map_naval_to_ground_inputs(naval)
            ground = runner.run_ground_trial(
                model_path=args.ground_model,
                trial_id=t.trial_id,
                trial_seed_ground=t.trial_seed + 1,
                ground_inputs=g_inputs,
            )
            elapsed = time.perf_counter() - start
            results.append(
                TrialResult(
                    trial_id=t.trial_id,
                    spawn_zone=t.spawn_zone,
                    trial_seed=t.trial_seed,
                    run_timestamp=run_timestamp,
                    naval_air_battle_end=naval.air_battle_end,
                    naval_ground_battle_start=naval.ground_battle_start,
                    naval_conflict_days=naval.conflict_days,
                    naval_carriers_remaining=naval.carriers_remaining,
                    naval_destroyers_remaining=naval.destroyers_remaining,
                    naval_frigates_remaining=naval.frigates_remaining,
                    naval_amphibs_landed=naval.amphibs_landed,
                    naval_faa_jets_remaining=naval.faa_jets_remaining,
                    naval_shars_remaining=naval.shars_remaining,
                    ground_battle_end=ground.ground_battle_end,
                    ground_conflict_days=ground.conflict_days,
                    british_kia=ground.british_kia,
                    argentine_kia=ground.argentine_kia,
                    argentine_sur=ground.argentine_sur,
                    success=True,
                    error_message="",
                    runtime_seconds=elapsed,
                )
            )
        except Exception as exc:
            elapsed = time.perf_counter() - start
            results.append(
                TrialResult(
                    trial_id=t.trial_id,
                    spawn_zone=t.spawn_zone,
                    trial_seed=t.trial_seed,
                    run_timestamp=run_timestamp,
                    naval_air_battle_end="",
                    naval_ground_battle_start="",
                    naval_conflict_days=0.0,
                    naval_carriers_remaining=0,
                    naval_destroyers_remaining=0,
                    naval_frigates_remaining=0,
                    naval_amphibs_landed=0,
                    naval_faa_jets_remaining=0,
                    naval_shars_remaining=0,
                    ground_battle_end="",
                    ground_conflict_days=0.0,
                    british_kia=0,
                    argentine_kia=0,
                    argentine_sur=0,
                    success=False,
                    error_message=str(exc),
                    runtime_seconds=elapsed,
                )
            )
    write_output_csv(args.output_csv, results)

    manifest = {
        "run_timestamp": run_timestamp,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "netlogo_version": netlogo_version,
        "netlogo_home": str(netlogo_home),
        "base_seed": args.base_seed,
        "total_trials": len(trials),
        "output_rows_written": len(results),
        "faa_loss_threshold": args.faa_loss_threshold,
        "main_model": str(args.main_model),
        "ground_model": str(args.ground_model),
        "input_csv": str(args.input_csv),
        "output_csv": str(args.output_csv),
    }
    args.manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
