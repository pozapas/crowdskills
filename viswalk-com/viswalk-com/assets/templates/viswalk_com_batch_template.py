#!/usr/bin/env python3
"""Manifest-driven Viswalk/Vissim COM batch template.

This template reloads the base network for each manifest row, applies common
pedestrian demand factors, runs the simulation, and writes one result row per
manifest row. Customize metric extraction for the user's measurements.
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


def load_row_network(vissim: Any, row: dict[str, str]) -> None:
    network = Path(row["network_path"])
    layout = Path(row["layout_path"]) if row.get("layout_path") else None
    if not network.exists():
        raise FileNotFoundError(f"network file not found: {network}")
    vissim.LoadNet(str(network), False)
    if layout:
        if not layout.exists():
            raise FileNotFoundError(f"layout file not found: {layout}")
        vissim.LoadLayout(str(layout))


def apply_row(vissim: Any, row: dict[str, str]) -> None:
    sim = vissim.Simulation
    sim.SetAttValue("RandSeed", int(row["seed"]))
    sim.SetAttValue("SimPeriod", float(row["sim_period"]))
    sim.SetAttValue("SimRes", float(row["sim_resolution"]))
    sim.SetAttValue("UseMaxSimSpeed", True)

    result_dir = Path(row["results_dir"])
    result_dir.mkdir(parents=True, exist_ok=True)
    vissim.SetResultsFolder(str(result_dir))

    ped_input = vissim.Net.PedestrianInputs.ItemByKey(int(row["pedestrian_input_key"]))
    ped_input.SetAttValue("Volume(1)", float(row["ped_volume_1"]))

    # Optional project-specific examples:
    # area = vissim.Net.Areas.ItemByKey(int(row["area_key_for_speed_factor"]))
    # area.SetAttValue("DesSpeedFact", float(row["desired_speed_factor"]))
    #
    # route = (
    #     vissim.Net.PedestrianRoutingDecisionsStatic
    #     .ItemByKey(int(row["route_decision_key"]))
    #     .PedRoutSta.ItemByKey(int(row["route_key"]))
    # )
    # route.SetAttValue("RelFlow(1)", float(row["route_factor"]))


def run(vissim: Any) -> float:
    started = time.perf_counter()
    vissim.Simulation.RunContinuous()
    return time.perf_counter() - started


def extract_metrics(vissim: Any, row: dict[str, str]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}

    area_key = row.get("metric_area_key")
    if area_key:
        area = vissim.Net.Areas.ItemByKey(int(area_key))
        metrics["area_num_peds_avg"] = area.AttValue("NumPedsAvg")
        metrics["area_density"] = area.AttValue("Dens")
        metrics["area_experienced_density"] = area.AttValue("ExperDens")

    travel_time_key = row.get("travel_time_measurement_key")
    if travel_time_key:
        measurement = vissim.Net.PedestrianTravelTimeMeasurements.ItemByKey(int(travel_time_key))
        metrics["travel_time_measurement_no"] = measurement.AttValue("No")
        # Customize subattribute strings from the Vissim list header or COM Help.
        # metrics["travel_time_avg"] = measurement.AttValue("TravTm(...)")

    return metrics


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def write_results(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Viswalk COM manifest.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("results") / "batch_results.csv")
    parser.add_argument("--version", help="optional Vissim COM version suffix")
    parser.add_argument("--close", action="store_true", help="close Vissim after the batch")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_rows = read_manifest(args.manifest)
    vissim = connect_vissim(args.version)
    results: list[dict[str, Any]] = []
    try:
        for row in manifest_rows:
            result_row: dict[str, Any] = dict(row)
            try:
                load_row_network(vissim, row)
                vissim.SuspendUpdateGUI()
                try:
                    apply_row(vissim, row)
                finally:
                    vissim.ResumeUpdateGUI()
                elapsed = run(vissim)
                result_row.update(extract_metrics(vissim, row))
                result_row["completed"] = True
                result_row["elapsed_wall_seconds"] = round(elapsed, 3)
                result_row["error"] = ""
            except Exception as exc:
                result_row["completed"] = False
                result_row["elapsed_wall_seconds"] = ""
                result_row["error"] = str(exc)
            results.append(result_row)
            write_results(args.out, results)
        print(f"Wrote {len(results)} rows to {args.out}")
        return 0 if all(row.get("completed") for row in results) else 1
    finally:
        if args.close:
            vissim.Exit()


if __name__ == "__main__":
    raise SystemExit(main())
