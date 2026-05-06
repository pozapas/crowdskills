#!/usr/bin/env python3
"""Create a deterministic MassMotionConsole run manifest.

The manifest captures one row per project, seed, thread-count, and population
scale combination. Rows include output paths and the exact console command a
batch runner can execute.

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
import shlex
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


SAFE_TEXT = re.compile(r"[^A-Za-z0-9_.-]+")


@dataclass(frozen=True)
class ConsoleManifestResult:
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


def split_paths(text: str) -> list[Path]:
    return [Path(value) for value in split_text_values(text)]


def split_int_values(text: str) -> list[int]:
    values: list[int] = []
    for value in split_text_values(text):
        parsed = int(value)
        if parsed < 0:
            raise argparse.ArgumentTypeError("integer values must be non-negative")
        values.append(parsed)
    return values


def split_positive_floats(text: str) -> list[float]:
    values: list[float] = []
    for value in split_text_values(text):
        parsed = float(value)
        if parsed <= 0:
            raise argparse.ArgumentTypeError("population scale must be positive")
        values.append(parsed)
    return values


def safe_part(value: object) -> str:
    return SAFE_TEXT.sub("-", str(value)).strip("-") or "value"


def quote_command(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def query_label(args: argparse.Namespace) -> str:
    if args.queryall:
        return "ALL"
    return "|".join(args.query)


def command_parts(row: dict[str, object], args: argparse.Namespace) -> list[str]:
    parts = [
        str(row["console_path"]),
        "--project",
        str(row["project_path"]),
    ]
    if row.get("scriptfile_path"):
        parts.extend(["--scriptfile", str(row["scriptfile_path"])])
    if row.get("scriptobject"):
        parts.extend(["--scriptobject", str(row["scriptobject"])])
    if args.run_simulation:
        parts.extend(["--simulation", str(row["simulation_path"])])
    if row.get("seed") != "":
        parts.extend(["--seed", str(row["seed"])])
    if row.get("threads") != "":
        parts.extend(["--threads", str(row["threads"])])
    if row.get("popscale") != "":
        parts.extend(["--popscale", str(row["popscale"])])
    if args.nothreads:
        parts.append("--nothreads")
    if args.dump:
        parts.append("--dump")
    if args.vis:
        parts.append("--vis")
    if args.csvmicrosoft:
        parts.append("--csvmicrosoft")
    if args.csvseparator:
        parts.extend(["--csvseparator", args.csvseparator])
    if args.verbosity:
        parts.extend(["--verbosity", args.verbosity])
    if args.queryall:
        parts.append("--queryall")
    else:
        for query in args.query:
            parts.extend(["--query", query])
    return parts


def build_rows(args: argparse.Namespace) -> list[dict[str, object]]:
    thread_values = args.threads or [""]
    popscale_values = args.popscale or [""]
    axes: list[tuple[str, list[object]]] = [
        ("project_path", [str(path) for path in args.projects]),
        ("seed", args.seeds),
        ("threads", thread_values),
        ("popscale", popscale_values),
    ]
    factors = [name for name, values in axes if len(values) > 1]
    rows: list[dict[str, object]] = []
    for index, values in enumerate(itertools.product(*[values for _name, values in axes]), 1):
        row = dict(zip([name for name, _values in axes], values))
        project_stem = Path(str(row["project_path"])).stem
        run_id = "_".join(
            [
                safe_part(args.study),
                safe_part(project_stem),
                f"seed{safe_part(row['seed'])}",
                f"thr{safe_part(row['threads'])}" if row["threads"] != "" else "thrdefault",
                f"pop{safe_part(row['popscale'])}" if row["popscale"] != "" else "popdefault",
                f"{index:04d}",
            ]
        )
        output_dir = Path(args.output_root) / run_id
        row.update(
            {
                "run_id": run_id,
                "study": args.study,
                "console_path": str(args.console),
                "scriptfile_path": str(args.scriptfile) if args.scriptfile else "",
                "scriptobject": args.scriptobject or "",
                "simulation_path": str(output_dir / f"{run_id}.mmdb"),
                "expected_log": str(output_dir / f"{run_id}.txt"),
                "output_dir": str(output_dir),
                "query_names": query_label(args),
                "status": "planned",
                "notes": "",
                "factors": "|".join(factors or ["project_path"]),
            }
        )
        row["command"] = quote_command(command_parts(row, args))
        rows.append(row)
    return rows


def validate_args(args: argparse.Namespace) -> list[str]:
    failures: list[str] = []
    if not args.projects:
        failures.append("--projects must include at least one file")
    if not args.run_simulation and not args.scriptfile and not args.scriptobject:
        failures.append("provide --run-simulation, --scriptfile, or --scriptobject")
    if args.check_projects:
        missing = [str(path) for path in args.projects if not path.exists()]
        if missing:
            failures.append("missing project files: " + ", ".join(missing))
    if args.check_console and not args.console.exists():
        failures.append(f"console path does not exist: {args.console}")
    if args.scriptfile and args.check_scripts and not args.scriptfile.exists():
        failures.append(f"scriptfile does not exist: {args.scriptfile}")
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
    parser = argparse.ArgumentParser(description="Create a MassMotionConsole manifest.")
    parser.add_argument("--study", default="massmotion_study")
    parser.add_argument("--projects", type=split_paths, required=True, help="comma-separated .mm/.mmdb files")
    parser.add_argument("--console", type=Path, default=Path("MassMotionConsole.exe"))
    parser.add_argument("--scriptfile", type=Path)
    parser.add_argument("--scriptobject")
    parser.add_argument("--run-simulation", action="store_true")
    parser.add_argument("--query", action="append", default=[])
    parser.add_argument("--queryall", action="store_true")
    parser.add_argument("--seeds", type=split_int_values, default=[0])
    parser.add_argument("--threads", type=split_int_values, default=[])
    parser.add_argument("--popscale", type=split_positive_floats, default=[])
    parser.add_argument("--nothreads", action="store_true")
    parser.add_argument("--dump", action="store_true")
    parser.add_argument("--vis", action="store_true")
    parser.add_argument("--csvmicrosoft", action="store_true")
    parser.add_argument("--csvseparator")
    parser.add_argument("--verbosity")
    parser.add_argument("--output-root", type=Path, default=Path("results"))
    parser.add_argument("--out", type=Path, default=Path("massmotion_console_runs.csv"))
    parser.add_argument("--check-projects", action="store_true")
    parser.add_argument("--check-console", action="store_true")
    parser.add_argument("--check-scripts", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = validate_args(args)
    if failures:
        result = ConsoleManifestResult(False, str(args.out), 0, [], "; ".join(failures))
        print(json.dumps(asdict(result), indent=2) if args.json else result.message)
        return 1
    rows = build_rows(args)
    try:
        write_manifest(args.out, rows, args.force)
    except OSError as exc:
        result = ConsoleManifestResult(False, str(args.out), 0, [], str(exc))
        print(json.dumps(asdict(result), indent=2) if args.json else result.message)
        return 1
    factors = sorted({factor for row in rows for factor in str(row["factors"]).split("|")})
    result = ConsoleManifestResult(
        True,
        str(args.out),
        len(rows),
        factors,
        f"Wrote {len(rows)} MassMotionConsole run rows to {args.out}",
    )
    print(json.dumps(asdict(result), indent=2) if args.json else result.message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
