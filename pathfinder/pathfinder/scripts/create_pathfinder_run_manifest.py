#!/usr/bin/env python3
"""Create a deterministic Pathfinder command-line run manifest.

The manifest is designed for external Python orchestration around Pathfinder's
testsim.bat command-line simulator. It records one row per model, scenario,
variation, and seed combination without modifying any Pathfinder model files.

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
class ManifestResult:
    ok: bool
    output_file: str
    rows: int
    factors: list[str]
    message: str


def split_text_values(text: str) -> list[str]:
    values = [value.strip() for value in text.split(",") if value.strip()]
    if not values:
        raise argparse.ArgumentTypeError("at least one comma-separated value required")
    return values


def split_int_values(text: str) -> list[int]:
    values: list[int] = []
    for value in split_text_values(text):
        parsed = int(value)
        if parsed < 0:
            raise argparse.ArgumentTypeError("seed values must be non-negative")
        values.append(parsed)
    return values


def split_paths(text: str) -> list[Path]:
    return [Path(value) for value in split_text_values(text)]


def safe_part(value: object) -> str:
    return SAFE_TEXT.sub("-", str(value)).strip("-") or "value"


def build_rows(args: argparse.Namespace) -> list[dict[str, object]]:
    axes: list[tuple[str, list[object]]] = [
        ("model_path", [str(path) for path in args.models]),
        ("scenario", args.scenarios),
        ("variation", args.variations),
        ("seed", args.seeds),
    ]
    factor_names = [name for name, values in axes if len(values) > 1]
    rows: list[dict[str, object]] = []

    for index, values in enumerate(itertools.product(*[values for _name, values in axes]), 1):
        row = dict(zip([name for name, _values in axes], values))
        model_stem = Path(str(row["model_path"])).stem
        run_id = "_".join(
            [
                safe_part(args.study),
                safe_part(model_stem),
                safe_part(row["scenario"]),
                safe_part(row["variation"]),
                f"seed{safe_part(row['seed'])}",
                f"{index:04d}",
            ]
        )
        output_dir = Path(args.output_root) / run_id
        row.update(
            {
                "run_id": run_id,
                "study": args.study,
                "testsim_path": str(args.testsim),
                "output_dir": str(output_dir),
                "expected_summary": str(output_dir / "summary.txt"),
                "expected_occupant_history": str(output_dir / "occupant_history.csv"),
                "status": "planned",
                "notes": "",
            }
        )
        rows.append(row)

    if not factor_names:
        factor_names = ["model_path"]
    for row in rows:
        row["factors"] = "|".join(factor_names)
    return rows


def validate_args(args: argparse.Namespace) -> list[str]:
    failures: list[str] = []
    if not args.models:
        failures.append("--models must include at least one .pth file")
    if args.check_models:
        missing = [str(path) for path in args.models if not path.exists()]
        if missing:
            failures.append("missing model files: " + ", ".join(missing))
    if args.check_testsim and not args.testsim.exists():
        failures.append(f"testsim path does not exist: {args.testsim}")
    return failures


def write_manifest(path: Path, rows: list[dict[str, object]], force: bool) -> None:
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
    parser = argparse.ArgumentParser(description="Create a Pathfinder run manifest.")
    parser.add_argument("--study", default="pathfinder_study")
    parser.add_argument("--models", type=split_paths, required=True, help="comma-separated .pth model paths")
    parser.add_argument(
        "--testsim",
        type=Path,
        default=Path("testsim.bat"),
        help="Pathfinder command-line simulator batch file",
    )
    parser.add_argument("--scenarios", type=split_text_values, default=["base"])
    parser.add_argument("--variations", type=split_text_values, default=["nominal"])
    parser.add_argument("--seeds", type=split_int_values, default=[0])
    parser.add_argument("--output-root", type=Path, default=Path("results"))
    parser.add_argument("--out", type=Path, default=Path("pathfinder_runs.csv"))
    parser.add_argument("--check-models", action="store_true")
    parser.add_argument("--check-testsim", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = validate_args(args)
    if failures:
        result = ManifestResult(False, str(args.out), 0, [], "; ".join(failures))
        print(json.dumps(asdict(result), indent=2) if args.json else result.message)
        return 1

    rows = build_rows(args)
    try:
        write_manifest(args.out, rows, args.force)
    except OSError as exc:
        result = ManifestResult(False, str(args.out), 0, [], str(exc))
        print(json.dumps(asdict(result), indent=2) if args.json else result.message)
        return 1

    factors = sorted({factor for row in rows for factor in str(row["factors"]).split("|")})
    result = ManifestResult(
        True,
        str(args.out),
        len(rows),
        factors,
        f"Wrote {len(rows)} Pathfinder run rows to {args.out}",
    )
    print(json.dumps(asdict(result), indent=2) if args.json else result.message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
