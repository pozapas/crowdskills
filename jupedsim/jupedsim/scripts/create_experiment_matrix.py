#!/usr/bin/env python3
"""Create a reproducible JuPedSim experiment matrix CSV.

The script does not run JuPedSim. It creates a deterministic manifest that a
simulation template can consume, review, or extend.

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
    values = []
    for value in split_values(text):
        parsed = int(value)
        if parsed <= 0:
            raise argparse.ArgumentTypeError("integer values must be positive")
        values.append(parsed)
    return values


def split_floats(text: str) -> list[float]:
    values = []
    for value in split_values(text):
        parsed = float(value)
        if parsed <= 0:
            raise argparse.ArgumentTypeError("numeric values must be positive")
        values.append(parsed)
    return values


def parse_extra_factor(text: str) -> tuple[str, list[str]]:
    if "=" not in text:
        raise argparse.ArgumentTypeError("extra factors must use name=value1,value2")
    name, value_text = text.split("=", 1)
    name = name.strip()
    if not name:
        raise argparse.ArgumentTypeError("factor name cannot be empty")
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise argparse.ArgumentTypeError(
            "factor names must be valid identifier-like strings"
        )
    return name, split_values(value_text)


def safe_part(value: object) -> str:
    return SAFE_TEXT.sub("-", str(value)).strip("-") or "value"


def build_rows(args: argparse.Namespace) -> list[dict[str, object]]:
    axes: list[tuple[str, list[object]]] = [
        ("model_name", args.models),
        ("seed", args.seeds),
        ("number_of_agents", args.agents),
        ("desired_speed", args.desired_speeds),
        ("radius", args.radii),
    ]
    axes.extend(args.factor or [])

    rows = []
    keys = [key for key, _values in axes]
    for index, values in enumerate(itertools.product(*[values for _key, values in axes]), 1):
        row = dict(zip(keys, values))
        row.update(
            {
                "run_id": f"{safe_part(args.scenario)}_{index:04d}",
                "scenario": args.scenario,
                "dt": args.dt,
                "every_nth_frame": args.every_nth_frame,
                "max_iterations": args.max_iterations,
            }
        )
        suffix = "_".join(
            [
                safe_part(args.scenario),
                safe_part(row["model_name"]),
                f"n{row['number_of_agents']}",
                f"v{safe_part(row['desired_speed'])}",
                f"r{safe_part(row['radius'])}",
                f"seed{row['seed']}",
                f"{index:04d}",
            ]
        )
        row["output_file"] = str(Path(args.output_dir) / f"{suffix}.sqlite")
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
        description="Create a JuPedSim experiment matrix manifest."
    )
    parser.add_argument("--scenario", default="jupedsim_scenario")
    parser.add_argument("--models", type=split_values, default=["csm", "csm_v2", "avm"])
    parser.add_argument("--seeds", type=split_ints, default=[1001, 1002, 1003])
    parser.add_argument("--agents", type=split_ints, default=[50])
    parser.add_argument("--desired-speeds", type=split_floats, default=[1.2])
    parser.add_argument("--radii", type=split_floats, default=[0.2])
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--every-nth-frame", type=int, default=5)
    parser.add_argument("--max-iterations", type=int, default=10000)
    parser.add_argument("--factor", action="append", type=parse_extra_factor)
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--out", type=Path, default=Path("manifest.csv"))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.dt <= 0:
        raise SystemExit("--dt must be positive")
    if args.every_nth_frame <= 0:
        raise SystemExit("--every-nth-frame must be positive")
    if args.max_iterations <= 0:
        raise SystemExit("--max-iterations must be positive")

    rows = build_rows(args)
    try:
        write_manifest(args.out, rows, force=args.force)
    except OSError as exc:
        result = MatrixResult(
            ok=False,
            output_file=str(args.out),
            rows=0,
            factors=[],
            message=str(exc),
        )
        print(json.dumps(asdict(result), indent=2) if args.json else result.message)
        return 1

    factor_names = [
        "model_name",
        "seed",
        "number_of_agents",
        "desired_speed",
        "radius",
    ] + [name for name, _values in (args.factor or [])]
    result = MatrixResult(
        ok=True,
        output_file=str(args.out),
        rows=len(rows),
        factors=factor_names,
        message=f"Wrote {len(rows)} rows to {args.out}",
    )
    print(json.dumps(asdict(result), indent=2) if args.json else result.message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
