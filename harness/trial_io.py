from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


ALLOWED_ZONES = ("zone-1", "zone-2", "zone-3", "zone-4", "zone-5")


@dataclass(frozen=True)
class TrialSpec:
    trial_id: int
    spawn_zone: str
    trial_seed: int


@dataclass
class TrialResult:
    trial_id: int
    spawn_zone: str
    trial_seed: int
    run_timestamp: str
    naval_air_battle_end: str
    naval_ground_battle_start: str
    naval_conflict_days: float
    naval_carriers_remaining: int
    naval_destroyers_remaining: int
    naval_frigates_remaining: int
    naval_amphibs_landed: int
    naval_faa_jets_remaining: int
    naval_shars_remaining: int
    ground_battle_end: str
    ground_conflict_days: float
    british_kia: int
    argentine_kia: int
    success: bool
    error_message: str
    runtime_seconds: float


INPUT_COLUMNS = ("trial_id", "spawn_zone", "trial_seed")

OUTPUT_COLUMNS = (
    "trial_id",
    "spawn_zone",
    "trial_seed",
    "run_timestamp",
    "naval_air_battle_end",
    "naval_ground_battle_start",
    "naval_conflict_days",
    "naval_carriers_remaining",
    "naval_destroyers_remaining",
    "naval_frigates_remaining",
    "naval_amphibs_landed",
    "naval_faa_jets_remaining",
    "naval_shars_remaining",
    "ground_battle_end",
    "ground_conflict_days",
    "british_kia",
    "argentine_kia",
    "success",
    "error_message",
    "runtime_seconds",
)


def validate_trial_specs(trials: list[TrialSpec]) -> None:
    if not trials:
        raise ValueError("Input CSV has no trial rows.")

    ids = set()
    zone_counts = {z: 0 for z in ALLOWED_ZONES}
    for t in trials:
        if t.trial_id in ids:
            raise ValueError(f"Duplicate trial_id found: {t.trial_id}")
        ids.add(t.trial_id)

        if t.spawn_zone not in ALLOWED_ZONES:
            raise ValueError(
                f"Invalid spawn_zone '{t.spawn_zone}' for trial_id={t.trial_id}. "
                f"Allowed: {', '.join(ALLOWED_ZONES)}"
            )
        zone_counts[t.spawn_zone] += 1

    counts = set(zone_counts.values())
    if len(counts) != 1:
        raise ValueError(
            "Input CSV is not balanced across zones. "
            f"Observed counts: {zone_counts}"
        )


def read_input_csv(path: Path) -> list[TrialSpec]:
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in INPUT_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Input CSV missing required columns: {missing}")

        trials: list[TrialSpec] = []
        for row in reader:
            trials.append(
                TrialSpec(
                    trial_id=int(row["trial_id"]),
                    spawn_zone=row["spawn_zone"].strip(),
                    trial_seed=int(row["trial_seed"]),
                )
            )

    validate_trial_specs(trials)
    return trials


def write_input_csv(path: Path, trials: Iterable[TrialSpec]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(INPUT_COLUMNS))
        writer.writeheader()
        for t in trials:
            writer.writerow(
                {"trial_id": t.trial_id, "spawn_zone": t.spawn_zone, "trial_seed": t.trial_seed}
            )


def write_output_csv(path: Path, results: Iterable[TrialResult]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(OUTPUT_COLUMNS))
        writer.writeheader()
        for r in results:
            row = asdict(r)
            row["success"] = "1" if r.success else "0"
            writer.writerow(row)
