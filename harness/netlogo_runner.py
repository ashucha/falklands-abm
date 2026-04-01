from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class NavalOutputs:
    air_battle_end: str
    ground_battle_start: str
    conflict_days: float
    carriers_remaining: int
    destroyers_remaining: int
    frigates_remaining: int
    amphibs_landed: int
    faa_jets_remaining: int
    shars_remaining: int


@dataclass
class GroundInputs:
    ground_battle_start: str
    air_battle_end: str
    destroyers_remaining: int
    frigates_remaining: int


@dataclass
class GroundOutputs:
    ground_battle_end: str
    conflict_days: float
    british_kia: int
    argentine_kia: int


class NetLogoRunner:
    """
    Thin pyNetLogo wrapper.

    Requires:
      pip install pyNetLogo
    and either:
      - NETLOGO_HOME env var, or
      - netlogo_home passed in constructor.
    """

    def __init__(self, netlogo_home: Path | None = None) -> None:
        try:
            import pyNetLogo  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "pyNetLogo is required. Install with: pip install pyNetLogo"
            ) from exc

        self._pyNetLogo = pyNetLogo
        self._netlogo_home = str(netlogo_home) if netlogo_home else None

    def _new_link(self, model_path: Path):
        kwargs: dict[str, Any] = {"gui": False}
        if self._netlogo_home:
            kwargs["netlogo_home"] = self._netlogo_home
        link = self._pyNetLogo.NetLogoLink(**kwargs)
        link.load_model(str(model_path))
        return link

    def run_naval_trial(
        self,
        model_path: Path,
        trial_id: int,
        spawn_zone: str,
        trial_seed: int,
        faa_loss_threshold: int,
    ) -> NavalOutputs:
        nl = self._new_link(model_path)
        try:
            nl.command(f"set trial-id {trial_id}")
            nl.command(f"set trial-seed {trial_seed}")
            nl.command(f"set faa-loss-threshold {faa_loss_threshold}")
            nl.command(f'set spawn-zone "{spawn_zone}"')
            nl.command("setup")
            nl.command("while [not naval-trial-done?] [ go ]")

            return NavalOutputs(
                air_battle_end=str(nl.report("air-battle-end-string")),
                ground_battle_start=str(nl.report("ground-battle-start-string")),
                conflict_days=float(nl.report("conflict-days")),
                carriers_remaining=int(nl.report("count carriers")),
                destroyers_remaining=int(nl.report("count destroyers")),
                frigates_remaining=int(nl.report("count frigates")),
                amphibs_landed=int(nl.report("amphibs-landed")),
                faa_jets_remaining=int(nl.report("faa-jets")),
                shars_remaining=int(nl.report("count shars")),
            )
        finally:
            nl.kill_workspace()

    def run_ground_trial(
        self,
        model_path: Path,
        trial_id: int,
        trial_seed_ground: int,
        ground_inputs: GroundInputs,
    ) -> GroundOutputs:
        nl = self._new_link(model_path)
        try:
            nl.command(f"set trial-id {trial_id}")
            nl.command(f"set trial-seed-ground {trial_seed_ground}")
            nl.command(f'set ground-battle-start-input "{ground_inputs.ground_battle_start}"')
            nl.command(f'set air-battle-end-input "{ground_inputs.air_battle_end}"')
            nl.command(f"set destroyers-remaining-input {ground_inputs.destroyers_remaining}")
            nl.command(f"set frigates-remaining-input {ground_inputs.frigates_remaining}")
            nl.command("setup")
            nl.command("while [not ground-trial-done?] [ go ]")

            return GroundOutputs(
                ground_battle_end=str(nl.report("ground-battle-end-string")),
                conflict_days=float(nl.report("conflict-days")),
                british_kia=int(nl.report("british-casualties")),
                argentine_kia=int(nl.report("argentine-casualties")),
            )
        finally:
            nl.kill_workspace()
