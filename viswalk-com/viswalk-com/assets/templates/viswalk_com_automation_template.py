#!/usr/bin/env python3
"""Single-run Viswalk/Vissim COM automation template.

Customize object keys and result attributes for the user's network before
running. This template expects pywin32 and a registered Vissim COM server.
"""

from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path
from typing import Any

import win32com.client as com


def connect_vissim(version: str | None = None) -> Any:
    prog_id = "Vissim.Vissim" if not version else f"Vissim.Vissim.{version}"
    return com.gencache.EnsureDispatch(prog_id)


def load_network(vissim: Any, network: Path, layout: Path | None) -> None:
    if not network.exists():
        raise FileNotFoundError(f"network file not found: {network}")
    vissim.LoadNet(str(network), False)
    if layout:
        if not layout.exists():
            raise FileNotFoundError(f"layout file not found: {layout}")
        vissim.LoadLayout(str(layout))


def set_simulation(vissim: Any, *, seed: int, sim_period: float, sim_resolution: float) -> None:
    sim = vissim.Simulation
    sim.SetAttValue("RandSeed", seed)
    sim.SetAttValue("SimPeriod", sim_period)
    sim.SetAttValue("SimRes", sim_resolution)
    sim.SetAttValue("UseMaxSimSpeed", True)


def configure_pedestrian_input(vissim: Any, *, input_key: int, volume: float) -> None:
    ped_input = vissim.Net.PedestrianInputs.ItemByKey(input_key)
    ped_input.SetAttValue("Volume(1)", volume)


def add_rectangle_area(vissim: Any, *, key: int, name: str, x: float, y: float, width: float, height: float) -> Any:
    polygon = (
        f"POLYGON(({x} {y}, {x + width} {y}, {x + width} {y + height}, "
        f"{x} {y + height}, {x} {y}))"
    )
    area = vissim.Net.Areas.AddArea(key, polygon)
    area.SetAttValue("Name", name)
    return area


def run_simulation(vissim: Any) -> float:
    started = time.perf_counter()
    vissim.Simulation.RunContinuous()
    return time.perf_counter() - started


def read_area_snapshot(vissim: Any, area_keys: list[int]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in area_keys:
        area = vissim.Net.Areas.ItemByKey(key)
        rows.append(
            {
                "area_no": area.AttValue("No"),
                "area_name": area.AttValue("Name"),
                "num_peds_avg": area.AttValue("NumPedsAvg"),
                "density": area.AttValue("Dens"),
                "experienced_density": area.AttValue("ExperDens"),
            }
        )
    return rows


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_int_list(text: str) -> list[int]:
    return [int(value.strip()) for value in text.split(",") if value.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one Viswalk/Vissim COM scenario.")
    parser.add_argument("--network", type=Path, required=True)
    parser.add_argument("--layout", type=Path)
    parser.add_argument("--version", help="optional Vissim COM version suffix")
    parser.add_argument("--result-dir", type=Path, default=Path("results") / "single_run")
    parser.add_argument("--seed", type=int, default=1001)
    parser.add_argument("--sim-period", type=float, default=900.0)
    parser.add_argument("--sim-resolution", type=float, default=10.0)
    parser.add_argument("--pedestrian-input-key", type=int, default=1)
    parser.add_argument("--ped-volume", type=float, default=1000.0)
    parser.add_argument("--area-keys", type=parse_int_list, default=[1])
    parser.add_argument("--out", type=Path, default=Path("results") / "single_run" / "area_snapshot.csv")
    parser.add_argument("--close", action="store_true", help="close Vissim after the run")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    vissim = connect_vissim(args.version)
    try:
        load_network(vissim, args.network, args.layout)
        args.result_dir.mkdir(parents=True, exist_ok=True)
        vissim.SetResultsFolder(str(args.result_dir))
        vissim.SuspendUpdateGUI()
        try:
            set_simulation(
                vissim,
                seed=args.seed,
                sim_period=args.sim_period,
                sim_resolution=args.sim_resolution,
            )
            configure_pedestrian_input(
                vissim,
                input_key=args.pedestrian_input_key,
                volume=args.ped_volume,
            )
        finally:
            vissim.ResumeUpdateGUI()

        elapsed = run_simulation(vissim)
        rows = read_area_snapshot(vissim, args.area_keys)
        for row in rows:
            row.update(
                {
                    "seed": args.seed,
                    "ped_volume": args.ped_volume,
                    "sim_period": args.sim_period,
                    "elapsed_wall_seconds": round(elapsed, 3),
                }
            )
        write_rows(args.out, rows)
        print(f"Wrote {len(rows)} rows to {args.out}")
        return 0
    finally:
        if args.close:
            vissim.Exit()


if __name__ == "__main__":
    raise SystemExit(main())
