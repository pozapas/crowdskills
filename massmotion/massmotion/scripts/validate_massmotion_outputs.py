#!/usr/bin/env python3
"""Validate MassMotion output folders before analysis.

The validator checks run directories for mmdb result databases, text logs, query
CSVs, and optional agent position exports. It can open mmdb files through
SQLite and validate common agent-position CSV columns.

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
import sqlite3
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


AGENT_POSITION_PATTERNS = ["*agent*position*.csv", "*positions*.csv", "*trajectory*.csv"]
DEFAULT_AGENT_POSITION_COLUMNS = ["frame", "agent_id", "x", "y", "z"]


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
    lowered = re.sub(r"[^a-z0-9]+", "", value.strip().lower())
    aliases = {
        "framenumber": "frame",
        "frame": "frame",
        "agentid": "agent_id",
        "id": "agent_id",
        "xposition": "x",
        "x": "x",
        "yposition": "y",
        "y": "y",
        "zposition": "z",
        "z": "z",
        "clocktime": "clock_time",
        "speed": "speed",
        "heading": "heading",
        "movestate": "move_state",
        "floor": "floor",
    }
    return aliases.get(lowered, lowered)


def all_files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file()]


def find_matches(root: Path, patterns: Iterable[str]) -> list[Path]:
    files = all_files(root)
    matches: list[Path] = []
    for pattern in patterns:
        direct = root / pattern
        if not any(char in pattern for char in "*?[]") and direct.exists() and direct.is_file():
            matches.append(direct)
            continue
        normalized = pattern.replace("\\", "/").lower()
        for path in files:
            rel = path.relative_to(root).as_posix().lower()
            if fnmatch.fnmatch(rel, normalized) or fnmatch.fnmatch(path.name.lower(), normalized):
                matches.append(path)
    return sorted(set(matches))


def inspect_mmdb(path: Path) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []
    try:
        with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as connection:
            cursor = connection.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 20")
            tables = [row[0] for row in cursor.fetchall()]
            if not tables:
                warnings.append(f"{path.name} opened but no SQLite tables were found")
    except sqlite3.Error as exc:
        errors.append(f"{path.name} is not a readable SQLite mmdb: {exc}")
    return warnings, errors


def inspect_csv(path: Path, required_columns: list[str], min_rows: int) -> tuple[list[str], list[str]]:
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
                errors.append(f"{path.name} missing columns: {', '.join(missing)}")
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

    mmdb_matches = find_matches(path, ["*.mmdb"])
    if args.require_mmdb:
        if not mmdb_matches:
            errors.append("missing .mmdb result database")
        else:
            files_found.extend(str(match) for match in mmdb_matches)
            mmdb_warnings, mmdb_errors = inspect_mmdb(mmdb_matches[0])
            warnings.extend(mmdb_warnings)
            errors.extend(mmdb_errors)

    log_matches = find_matches(path, ["*.txt", "*.log"])
    if args.require_log:
        if not log_matches:
            errors.append("missing simulation log file")
        else:
            files_found.extend(str(match) for match in log_matches)

    query_matches = find_matches(path, split_patterns(args.require_query_csv) or ["*.csv"])
    if args.require_query_csv:
        if not query_matches:
            errors.append("missing query CSV output")
        else:
            files_found.extend(str(match) for match in query_matches)
            if args.min_csv_rows > 0:
                csv_warnings, csv_errors = inspect_csv(query_matches[0], [], args.min_csv_rows)
                warnings.extend(csv_warnings)
                errors.extend(csv_errors)

    if args.require_agent_position_csv:
        agent_matches = find_matches(path, AGENT_POSITION_PATTERNS)
        if not agent_matches:
            errors.append("missing agent position CSV")
        else:
            files_found.extend(str(match) for match in agent_matches)
            required_columns = split_patterns(args.agent_position_columns) or DEFAULT_AGENT_POSITION_COLUMNS
            csv_warnings, csv_errors = inspect_csv(agent_matches[0], required_columns, args.min_csv_rows)
            warnings.extend(csv_warnings)
            errors.extend(csv_errors)

    for pattern in split_patterns(args.require):
        matches = find_matches(path, [pattern])
        if matches:
            files_found.extend(str(match) for match in matches)
        else:
            errors.append(f"missing required output pattern: {pattern}")

    return OutputCheck(str(path), not errors, sorted(set(files_found)), warnings, errors)


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
    parser = argparse.ArgumentParser(description="Validate MassMotion output directories.")
    parser.add_argument("output_dirs", nargs="+", type=Path)
    parser.add_argument("--require", action="append", default=[], help="required file name or glob")
    parser.add_argument("--require-mmdb", action="store_true")
    parser.add_argument("--require-log", action="store_true")
    parser.add_argument(
        "--require-query-csv",
        nargs="?",
        const="*.csv",
        action="append",
        default=[],
        help="require query CSV output; optional file name or glob",
    )
    parser.add_argument("--require-agent-position-csv", action="store_true")
    parser.add_argument("--agent-position-columns", action="append", default=[])
    parser.add_argument("--min-csv-rows", type=int, default=1)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--csv", type=Path, help="write check results to CSV")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.min_csv_rows < 0:
        print("--min-csv-rows must be non-negative")
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
