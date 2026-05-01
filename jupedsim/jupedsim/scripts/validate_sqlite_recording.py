#!/usr/bin/env python3
"""Validate and summarize JuPedSim SQLite trajectory recordings.

Exit codes:
  0: all recordings passed required checks
  1: at least one recording failed validation
  2: command-line usage error, raised by argparse
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = {
    "trajectory_data": {"frame", "id", "pos_x", "pos_y", "ori_x", "ori_y"},
    "metadata": {"key", "value"},
    "geometry": {"hash", "wkt"},
    "frame_data": {"frame", "geometry_hash"},
}


@dataclass
class RecordingReport:
    path: str
    ok: bool
    failures: list[str]
    warnings: list[str]
    database_version: int | None = None
    fps: float | None = None
    frame_count: int = 0
    trajectory_rows: int = 0
    distinct_agents: int = 0
    first_frame: float | None = None
    last_frame: float | None = None
    first_frame_agents: int = 0
    last_frame_agents: int = 0
    estimated_duration: float | None = None
    xmin: float | None = None
    xmax: float | None = None
    ymin: float | None = None
    ymax: float | None = None


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return parsed


def table_columns(connection: sqlite3.Connection, table: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
    return {row[1] for row in rows}


def table_count(connection: sqlite3.Connection, table: str) -> int:
    return int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def metadata_map(connection: sqlite3.Connection) -> dict[str, str]:
    return {
        str(key): str(value)
        for key, value in connection.execute("SELECT key, value FROM metadata")
    }


def first_count_for_order(
    connection: sqlite3.Connection, order: str
) -> tuple[float | None, int]:
    row = connection.execute(
        "SELECT frame, COUNT(*) AS n "
        "FROM trajectory_data "
        "GROUP BY frame "
        f"ORDER BY frame {order} "
        "LIMIT 1"
    ).fetchone()
    if row is None:
        return None, 0
    return float(row[0]), int(row[1])


def add_schema_checks(connection: sqlite3.Connection, failures: list[str]) -> None:
    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    missing_tables = sorted(set(REQUIRED_COLUMNS) - tables)
    if missing_tables:
        failures.append(f"missing required tables: {', '.join(missing_tables)}")
        return

    for table, columns in REQUIRED_COLUMNS.items():
        missing_columns = sorted(columns - table_columns(connection, table))
        if missing_columns:
            failures.append(
                f"{table} missing columns: {', '.join(missing_columns)}"
            )


def add_consistency_checks(
    connection: sqlite3.Connection,
    report: RecordingReport,
    *,
    min_frames: int,
    max_final_agents: int | None,
    allow_empty: bool,
    sample_limit: int,
) -> None:
    metadata = metadata_map(connection)

    try:
        report.database_version = int(metadata["version"])
    except KeyError:
        report.failures.append("metadata missing version")
    except ValueError:
        report.failures.append("metadata version is not an integer")

    try:
        report.fps = float(metadata["fps"])
        if report.fps <= 0:
            report.failures.append("metadata fps must be positive")
    except KeyError:
        report.failures.append("metadata missing fps")
    except ValueError:
        report.failures.append("metadata fps is not numeric")

    report.frame_count = table_count(connection, "frame_data")
    report.trajectory_rows = table_count(connection, "trajectory_data")
    report.distinct_agents = int(
        connection.execute(
            "SELECT COUNT(DISTINCT id) FROM trajectory_data"
        ).fetchone()[0]
    )

    if report.frame_count < min_frames:
        report.failures.append(
            f"expected at least {min_frames} frame_data rows, found {report.frame_count}"
        )
    if not allow_empty and report.trajectory_rows == 0:
        report.failures.append("trajectory_data is empty")

    report.first_frame, report.first_frame_agents = first_count_for_order(
        connection, "ASC"
    )
    report.last_frame, report.last_frame_agents = first_count_for_order(
        connection, "DESC"
    )

    if max_final_agents is not None and report.last_frame_agents > max_final_agents:
        report.failures.append(
            "last recorded frame has "
            f"{report.last_frame_agents} agents, above allowed {max_final_agents}"
        )

    if report.last_frame is not None and report.fps:
        report.estimated_duration = report.last_frame / report.fps

    missing_geometry_hashes = int(
        connection.execute(
            "SELECT COUNT(*) "
            "FROM frame_data "
            "LEFT JOIN geometry ON frame_data.geometry_hash = geometry.hash "
            "WHERE geometry.hash IS NULL"
        ).fetchone()[0]
    )
    if missing_geometry_hashes:
        report.failures.append(
            f"{missing_geometry_hashes} frame_data rows reference unknown geometry hashes"
        )

    trajectory_frames_not_in_frame_data = int(
        connection.execute(
            "SELECT COUNT(*) FROM ("
            "SELECT DISTINCT frame FROM trajectory_data "
            "EXCEPT "
            "SELECT DISTINCT frame FROM frame_data"
            ")"
        ).fetchone()[0]
    )
    if trajectory_frames_not_in_frame_data:
        report.failures.append(
            f"{trajectory_frames_not_in_frame_data} trajectory frames are absent from frame_data"
        )

    bounds_row = connection.execute(
        "SELECT MIN(pos_x), MAX(pos_x), MIN(pos_y), MAX(pos_y) FROM trajectory_data"
    ).fetchone()
    if bounds_row and bounds_row[0] is not None:
        report.xmin, report.xmax, report.ymin, report.ymax = map(float, bounds_row)

    for key in ["xmin", "xmax", "ymin", "ymax"]:
        if key not in metadata and report.trajectory_rows:
            report.warnings.append(f"metadata missing {key}")

    samples = connection.execute(
        "SELECT pos_x, pos_y, ori_x, ori_y FROM trajectory_data LIMIT ?",
        (sample_limit,),
    ).fetchall()
    for index, row in enumerate(samples):
        values = [float(value) for value in row]
        if not all(math.isfinite(value) for value in values):
            report.failures.append(f"non-finite trajectory value in sample row {index}")
            break

    if sample_limit < report.trajectory_rows:
        report.warnings.append(
            f"finite-value check sampled {sample_limit} of {report.trajectory_rows} rows"
        )


def validate_recording(
    path: Path,
    *,
    min_frames: int,
    max_final_agents: int | None,
    allow_empty: bool,
    sample_limit: int,
    strict: bool,
) -> RecordingReport:
    report = RecordingReport(path=str(path), ok=False, failures=[], warnings=[])
    if not path.exists():
        report.failures.append("file does not exist")
        return report
    if path.stat().st_size == 0:
        report.failures.append("file is empty")
        return report

    try:
        with sqlite3.connect(path) as connection:
            add_schema_checks(connection, report.failures)
            if not report.failures:
                add_consistency_checks(
                    connection,
                    report,
                    min_frames=min_frames,
                    max_final_agents=max_final_agents,
                    allow_empty=allow_empty,
                    sample_limit=sample_limit,
                )
    except sqlite3.Error as exc:
        report.failures.append(f"sqlite error: {exc}")

    if strict and report.warnings:
        report.failures.extend([f"strict warning: {warning}" for warning in report.warnings])

    report.ok = not report.failures
    return report


def write_csv(path: Path, reports: list[RecordingReport]) -> None:
    fieldnames = list(asdict(reports[0]).keys())
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for report in reports:
            row: dict[str, Any] = asdict(report)
            row["failures"] = " | ".join(report.failures)
            row["warnings"] = " | ".join(report.warnings)
            writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and summarize JuPedSim SQLite trajectory recordings."
    )
    parser.add_argument("recordings", nargs="+", type=Path)
    parser.add_argument("--min-frames", type=positive_int, default=1)
    parser.add_argument("--max-final-agents", type=positive_int)
    parser.add_argument("--allow-empty", action="store_true")
    parser.add_argument("--sample-limit", type=positive_int, default=100000)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true", help="print JSON report")
    parser.add_argument("--csv", type=Path, help="write CSV summary to this path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reports = [
        validate_recording(
            path,
            min_frames=args.min_frames,
            max_final_agents=args.max_final_agents,
            allow_empty=args.allow_empty,
            sample_limit=args.sample_limit,
            strict=args.strict,
        )
        for path in args.recordings
    ]

    if args.csv:
        write_csv(args.csv, reports)

    if args.json:
        print(json.dumps([asdict(report) for report in reports], indent=2))
    else:
        for report in reports:
            status = "OK" if report.ok else "FAIL"
            duration = (
                f"{report.estimated_duration:.3f}s"
                if report.estimated_duration is not None
                else "unknown duration"
            )
            print(
                f"{status}: {report.path} | frames={report.frame_count} "
                f"rows={report.trajectory_rows} agents={report.distinct_agents} "
                f"duration={duration}"
            )
            for failure in report.failures:
                print(f"  failure: {failure}")
            for warning in report.warnings:
                print(f"  warning: {warning}")

    return 0 if all(report.ok for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
