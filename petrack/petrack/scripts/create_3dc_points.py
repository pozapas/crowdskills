#!/usr/bin/env python3
"""Create a PeTrack .3dc extrinsic calibration point file from CSV.

Exit codes:
  0: .3dc file written
  1: validation or filesystem error
  2: command-line usage error, raised by argparse
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Point3D:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Result:
    ok: bool
    input_file: str
    output_file: str
    points: int
    message: str


def parse_float(value: str, *, row_number: int, column: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(
            f"row {row_number}: column {column} is not numeric: {value!r}"
        ) from exc
    if not math.isfinite(parsed):
        raise ValueError(f"row {row_number}: column {column} is not finite")
    return parsed


def coordinate_columns(fieldnames: list[str] | None) -> tuple[str, str, str]:
    if not fieldnames:
        raise ValueError("CSV file has no header")
    lowered = {field.lower(): field for field in fieldnames}
    for candidate in [("x_cm", "y_cm", "z_cm"), ("x", "y", "z")]:
        if all(name in lowered for name in candidate):
            return tuple(lowered[name] for name in candidate)  # type: ignore[return-value]
    raise ValueError("CSV must contain x_cm,y_cm,z_cm or x,y,z columns")


def read_points(path: Path) -> list[Point3D]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        x_col, y_col, z_col = coordinate_columns(reader.fieldnames)
        points = []
        for row_number, row in enumerate(reader, start=2):
            if not any((value or "").strip() for value in row.values()):
                continue
            points.append(
                Point3D(
                    parse_float(row[x_col], row_number=row_number, column=x_col),
                    parse_float(row[y_col], row_number=row_number, column=y_col),
                    parse_float(row[z_col], row_number=row_number, column=z_col),
                )
            )
    if len(points) < 4:
        raise ValueError(
            "at least four points are recommended for extrinsic calibration"
        )
    return points


def format_number(value: float) -> str:
    text = f"{value:.10g}"
    return "0" if text == "-0" else text


def write_3dc(path: Path, points: list[Point3D], *, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists; pass --force to overwrite")
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [str(len(points))]
    lines.extend(
        f"{format_number(point.x)} {format_number(point.y)} {format_number(point.z)}"
        for point in points
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a PeTrack .3dc point file from a CSV coordinate table."
    )
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("output_file", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        points = read_points(args.csv_file)
        write_3dc(args.output_file, points, force=args.force)
        result = Result(
            ok=True,
            input_file=str(args.csv_file),
            output_file=str(args.output_file),
            points=len(points),
            message=f"Wrote {len(points)} points to {args.output_file}",
        )
    except (OSError, ValueError) as exc:
        result = Result(
            ok=False,
            input_file=str(args.csv_file),
            output_file=str(args.output_file),
            points=0,
            message=str(exc),
        )

    print(json.dumps(asdict(result), indent=2) if args.json else result.message)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
