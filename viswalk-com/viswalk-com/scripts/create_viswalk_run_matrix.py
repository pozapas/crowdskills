#!/usr/bin/env python3
"""Create a reproducible Viswalk COM batch-run manifest.

The script does not run Vissim. It writes a CSV manifest that a COM automation
template can consume for paired seed, demand, speed, and route-factor sweeps.

Exit codes:
  0: manifest written
  1: validation or filesystem error
  2: command-line usage error, raised by argparse
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


SAFE_TEXT = re.compile(r"[^A-Za-z0-9_.-]+")


@dataclass(frozen=True)
class MatrixResult:
    ok: bool
    output_file: str
    rows: int
    factors: list[str]
    message: str


def split_values(text: str) -> list[str]:
    values = [value.strip() for value in text.split(",") if value.strip()]
    if not values:
        raise argparse.ArgumentTypeError("at least one comma-separated value required")
    return values


def split_ints(text: str) -> list[int]:
    values: list[int] = []
    for value in split_values(text):
        parsed = int(value)
        if parsed <= 0:
            raise argparse.ArgumentTypeError("integer values must be positive")
        values.append(parsed)
    return values


def split_floats(text: str) -> list[float]:
    values: list[float] = []
    for value in split_values(text):
        parsed = float(value)
        if parsed <= 0:
            raise argparse.ArgumentTypeError("numeric values must be positive")
        values.append(parsed)
    return values


def safe_part(value: object) -> str:
    return SAFE_TEXT.sub("-", str(value)).strip("-") or "value"


def build_rows(args: argparse.Namespace) -> list[dict[str, object]]:
    axes: list[tuple[str, list[object]]] = [
        ("seed", args.seeds),
        ("pedestrian_input_key", args.pedestrian_input_keys),
        ("ped_volume_1", args.ped_volumes),
        ("desired_speed_factor", args.speed_factors),
        ("route_factor", args.route_factors),
    ]
    keys = [key for key, _values in axes]

    rows: list[dict[str, object]] = []
    for index, values in enumerate(itertools.product(*[values for _key, values in axes]), 1):
        row = dict(zip(keys, values))
        run_id = "_".join(
            [
                safe_part(args.scenario),
                f"seed{row['seed']}",
                f"in{row['pedestrian_input_key']}",
                f"vol{safe_part(row['ped_volume_1'])}",
                f"spd{safe_part(row['desired_speed_factor'])}",
                f"rte{safe_part(row['route_factor'])}",
                f"{index:04d}",
            ]
        )
        row.update(
            {
                "run_id": run_id,
                "scenario": args.scenario,
                "network_path": str(args.network),
                "layout_path": str(args.layout) if args.layout else "",
                "sim_period": args.sim_period,
                "sim_resolution": args.sim_resolution,
                "warmup_seconds": args.warmup_seconds,
                "results_dir": str(Path(args.output_root) / run_id),
                "notes": "",
            }
        )
        rows.append(row)
    return rows


def write_manifest(path: Path, rows: list[dict[str, object]], *, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists; pass --force to overwrite")
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
    parser = argparse.ArgumentParser(
        description="Create a Viswalk COM experiment manifest."
    )
    parser.add_argument("--scenario", default="viswalk_scenario")
    parser.add_argument("--network", type=Path, required=True, help="base .inpx file")
    parser.add_argument("--layout", type=Path, help="optional .layx file")
    parser.add_argument("--seeds", type=split_ints, default=[1001, 1002, 1003])
    parser.add_argument("--pedestrian-input-keys", type=split_ints, default=[1])
    parser.add_argument("--ped-volumes", type=split_floats, default=[1000.0])
    parser.add_argument("--speed-factors", type=split_floats, default=[1.0])
    parser.add_argument("--route-factors", type=split_floats, default=[1.0])
    parser.add_argument("--sim-period", type=float, default=900.0)
    parser.add_argument("--sim-resolution", type=float, default=10.0)
    parser.add_argument("--warmup-seconds", type=float, default=0.0)
    parser.add_argument("--output-root", default="results")
    parser.add_argument("--out", type=Path, default=Path("viswalk_manifest.csv"))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures: list[str] = []
    if args.sim_period <= 0:
        failures.append("--sim-period must be positive")
    if args.sim_resolution <= 0:
        failures.append("--sim-resolution must be positive")
    if args.warmup_seconds < 0:
        failures.append("--warmup-seconds must be non-negative")
    if args.warmup_seconds >= args.sim_period:
        failures.append("--warmup-seconds must be less than --sim-period")
    if failures:
        result = MatrixResult(False, str(args.out), 0, [], "; ".join(failures))
        print(json.dumps(asdict(result), indent=2) if args.json else result.message)
        return 1

    rows = build_rows(args)
    try:
        write_manifest(args.out, rows, force=args.force)
    except OSError as exc:
        result = MatrixResult(False, str(args.out), 0, [], str(exc))
        print(json.dumps(asdict(result), indent=2) if args.json else result.message)
        return 1

    factors = [
        "seed",
        "pedestrian_input_key",
        "ped_volume_1",
        "desired_speed_factor",
        "route_factor",
    ]
    result = MatrixResult(
        True,
        str(args.out),
        len(rows),
        factors,
        f"Wrote {len(rows)} rows to {args.out}",
    )
    print(json.dumps(asdict(result), indent=2) if args.json else result.message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
