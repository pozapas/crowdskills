#!/usr/bin/env python3
"""Validate Pathfinder output folders before analysis.

The validator checks that each run directory exists, required summary and
occupant-history files can be found, requested filename patterns are present,
and occupant-history CSV files contain usable time, occupant, and position
columns.

Exit codes:
  0: every output directory passed validation
  1: one or more output directories failed validation
  2: command-line usage error, raised by argparse
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SUMMARY_PATTERNS = ["*summary*.txt", "*summary*.html", "*summary*.json"]
OCCUPANT_HISTORY_PATTERNS = [
    "*occupant*history*.csv",
    "*occupants*history*.csv",
    "*occupants*detailed*.csv",
    "*occupant*detailed*.csv",
    "*occupants*.csv",
]
DEFAULT_OCCUPANT_COLUMNS = ["time", "id", "x", "y"]


@dataclass(frozen=True)
class OutputCheck:
    output_dir: str
    ok: bool
    files_found: list[str]
    warnings: list[str]
    errors: list[str]


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    checked_dirs: int
    passed_dirs: int
    failed_dirs: int
    message: str


def split_patterns(values: list[str]) -> list[str]:
    patterns: list[str] = []
    for value in values:
        patterns.extend(part.strip() for part in value.split(",") if part.strip())
    return patterns


def normalize_column(value: str) -> str:
    lowered = value.strip().lower()
    lowered = lowered.replace("(s)", "").replace("(m)", "").replace("(m/s)", "")
    lowered = re.sub(r"[^a-z0-9]+", "", lowered)
    if lowered in {"t", "time", "timesec", "simulationtime"}:
        return "time"
    if lowered in {"occupantid", "personid", "agentid", "pedestrianid", "id"}:
        return "id"
    if lowered in {"x", "xpos", "xposition"}:
        return "x"
    if lowered in {"y", "ypos", "yposition"}:
        return "y"
    if lowered in {"z", "zpos", "zposition"}:
        return "z"
    if lowered in {"v", "speed", "velocity"}:
        return "speed"
    return lowered


def has_wildcards(pattern: str) -> bool:
    return any(char in pattern for char in "*?[]")


def all_files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file()]


def find_matches(root: Path, patterns: Iterable[str]) -> list[Path]:
    files = all_files(root)
    matches: list[Path] = []
    for pattern in patterns:
        direct = root / pattern
        if not has_wildcards(pattern) and direct.exists() and direct.is_file():
            matches.append(direct)
            continue
        normalized_pattern = pattern.replace("\\", "/").lower()
        for path in files:
            rel = path.relative_to(root).as_posix().lower()
            name = path.name.lower()
            if fnmatch.fnmatch(rel, normalized_pattern) or fnmatch.fnmatch(name, normalized_pattern):
                matches.append(path)
    return sorted(set(matches))


def inspect_occupant_csv(path: Path, required_columns: list[str], min_rows: int) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []
    try:
        with path.open(newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames:
                return warnings, [f"{path.name} has no CSV header"]
            normalized = {normalize_column(column): column for column in reader.fieldnames}
            missing = [column for column in required_columns if normalize_column(column) not in normalized]
            if missing:
                errors.append(f"{path.name} missing occupant columns: {', '.join(missing)}")
            row_count = 0
            for row_count, _row in enumerate(reader, 1):
                if row_count >= min_rows:
                    break
            if row_count < min_rows:
                errors.append(f"{path.name} has {row_count} rows; expected at least {min_rows}")
    except UnicodeDecodeError:
        errors.append(f"{path.name} is not readable as UTF-8 CSV")
    except OSError as exc:
        errors.append(f"{path.name} could not be read: {exc}")
    return warnings, errors


def validate_dir(path: Path, args: argparse.Namespace) -> OutputCheck:
    warnings: list[str] = []
    errors: list[str] = []
    files_found: list[str] = []

    if not path.exists():
        return OutputCheck(str(path), False, [], [], [f"output directory does not exist: {path}"])
    if not path.is_dir():
        return OutputCheck(str(path), False, [], [], [f"not a directory: {path}"])

    required_patterns = split_patterns(args.require)
    if args.require_summary:
        summary_matches = find_matches(path, SUMMARY_PATTERNS)
        if summary_matches:
            files_found.extend(str(match) for match in summary_matches)
        else:
            errors.append("missing summary output file")

    occupant_matches: list[Path] = []
    if args.require_occupant_history:
        occupant_matches = find_matches(path, OCCUPANT_HISTORY_PATTERNS)
        if occupant_matches:
            files_found.extend(str(match) for match in occupant_matches)
        else:
            errors.append("missing occupant history CSV output file")

    for pattern in required_patterns:
        matches = find_matches(path, [pattern])
        if matches:
            files_found.extend(str(match) for match in matches)
        else:
            errors.append(f"missing required output pattern: {pattern}")

    if args.require_occupant_history and occupant_matches:
        required_columns = split_patterns(args.occupant_columns) or DEFAULT_OCCUPANT_COLUMNS
        csv_warnings, csv_errors = inspect_occupant_csv(
            occupant_matches[0],
            required_columns,
            args.min_rows,
        )
        warnings.extend(csv_warnings)
        errors.extend(csv_errors)

    files_found = sorted(set(files_found))
    return OutputCheck(str(path), not errors, files_found, warnings, errors)


def write_checks_csv(path: Path, checks: list[OutputCheck]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["output_dir", "ok", "files_found", "warnings", "errors"],
        )
        writer.writeheader()
        for check in checks:
            writer.writerow(
                {
                    "output_dir": check.output_dir,
                    "ok": check.ok,
                    "files_found": " | ".join(check.files_found),
                    "warnings": " | ".join(check.warnings),
                    "errors": " | ".join(check.errors),
                }
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Pathfinder output directories.")
    parser.add_argument("output_dirs", nargs="+", type=Path)
    parser.add_argument("--require", action="append", default=[], help="required file name or glob")
    parser.add_argument("--require-summary", action="store_true")
    parser.add_argument("--require-occupant-history", action="store_true")
    parser.add_argument("--occupant-columns", action="append", default=[])
    parser.add_argument("--min-rows", type=int, default=1)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--csv", type=Path, help="write check results to CSV")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.min_rows < 0:
        print("--min-rows must be non-negative")
        return 1
    try:
        checks = [validate_dir(path, args) for path in args.output_dirs]
        passed = sum(1 for check in checks if check.ok)
        failed = len(checks) - passed
        result = ValidationResult(
            ok=failed == 0,
            checked_dirs=len(checks),
            passed_dirs=passed,
            failed_dirs=failed,
            message=f"Validated {len(checks)} output dirs: {passed} passed, {failed} failed",
        )
        if args.csv:
            write_checks_csv(args.csv, checks)
        if args.json:
            print(json.dumps({"result": asdict(result), "checks": [asdict(check) for check in checks]}, indent=2))
        else:
            print(result.message)
            for check in checks:
                status = "PASS" if check.ok else "FAIL"
                print(f"{status}: {check.output_dir}")
                for warning in check.warnings:
                    print(f"  warning: {warning}")
                for error in check.errors:
                    print(f"  error: {error}")
        return 0 if result.ok else 1
    except Exception as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
