#!/usr/bin/env python3
"""Validate PeTrack text trajectory exports.

The validator reads the first five columns of each non-comment data row as
`id frame x y z` and ignores additional export columns.

Exit codes:
  0: all files passed required checks
  1: at least one file failed validation
  2: command-line usage error, raised by argparse
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


FPS_PATTERN = re.compile(r"framerate:\s*([0-9]+(?:\.[0-9]+)?)\s*fps", re.I)


@dataclass
class TrajectoryReport:
    path: str
    ok: bool
    failures: list[str]
    warnings: list[str]
    comment_lines: int = 0
    data_rows: int = 0
    unique_agents: int = 0
    first_frame: int | None = None
    last_frame: int | None = None
    fps: float | None = None
    duplicate_id_frame_pairs: int = 0
    non_monotonic_agents: int = 0
    agents_with_frame_gaps: int = 0
    xmin: float | None = None
    xmax: float | None = None
    ymin: float | None = None
    ymax: float | None = None
    zmin: float | None = None
    zmax: float | None = None


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return parsed


def parse_bounds(values: list[str]) -> tuple[float, float, float, float]:
    if len(values) != 4:
        raise argparse.ArgumentTypeError("--bounds requires xmin xmax ymin ymax")
    parsed = tuple(float(value) for value in values)
    if not all(math.isfinite(value) for value in parsed):
        raise argparse.ArgumentTypeError("bounds must be finite")
    xmin, xmax, ymin, ymax = parsed
    if xmin > xmax or ymin > ymax:
        raise argparse.ArgumentTypeError("bounds minimums must not exceed maximums")
    return xmin, xmax, ymin, ymax


def parse_data_row(line: str, line_number: int) -> tuple[int, int, float, float, float]:
    parts = line.split()
    if len(parts) < 5:
        raise ValueError(f"line {line_number}: expected at least 5 columns")
    try:
        agent_id = int(parts[0])
        frame = int(parts[1])
        x = float(parts[2])
        y = float(parts[3])
        z = float(parts[4])
    except ValueError as exc:
        raise ValueError(f"line {line_number}: first five columns must be numeric") from exc
    if agent_id < 0:
        raise ValueError(f"line {line_number}: id must be non-negative")
    if frame < 0:
        raise ValueError(f"line {line_number}: frame must be non-negative")
    if not all(math.isfinite(value) for value in [x, y, z]):
        raise ValueError(f"line {line_number}: coordinates must be finite")
    return agent_id, frame, x, y, z


def update_bounds(report: TrajectoryReport, x: float, y: float, z: float) -> None:
    report.xmin = x if report.xmin is None else min(report.xmin, x)
    report.xmax = x if report.xmax is None else max(report.xmax, x)
    report.ymin = y if report.ymin is None else min(report.ymin, y)
    report.ymax = y if report.ymax is None else max(report.ymax, y)
    report.zmin = z if report.zmin is None else min(report.zmin, z)
    report.zmax = z if report.zmax is None else max(report.zmax, z)


def validate_file(
    path: Path,
    *,
    min_agents: int,
    min_rows: int,
    bounds: tuple[float, float, float, float] | None,
    allow_frame_gaps: bool,
) -> TrajectoryReport:
    report = TrajectoryReport(path=str(path), ok=False, failures=[], warnings=[])
    if not path.exists():
        report.failures.append("file does not exist")
        return report
    if path.stat().st_size == 0:
        report.failures.append("file is empty")
        return report

    frames_by_agent: dict[int, list[int]] = defaultdict(list)
    seen_pairs: set[tuple[int, int]] = set()
    out_of_bounds = 0

    try:
        with path.open(encoding="utf-8-sig") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    report.comment_lines += 1
                    match = FPS_PATTERN.search(line)
                    if match:
                        report.fps = float(match.group(1))
                    continue

                try:
                    agent_id, frame, x, y, z = parse_data_row(line, line_number)
                except ValueError as exc:
                    report.failures.append(str(exc))
                    continue

                report.data_rows += 1
                frames_by_agent[agent_id].append(frame)
                pair = (agent_id, frame)
                if pair in seen_pairs:
                    report.duplicate_id_frame_pairs += 1
                seen_pairs.add(pair)
                report.first_frame = frame if report.first_frame is None else min(report.first_frame, frame)
                report.last_frame = frame if report.last_frame is None else max(report.last_frame, frame)
                update_bounds(report, x, y, z)

                if bounds:
                    xmin, xmax, ymin, ymax = bounds
                    if x < xmin or x > xmax or y < ymin or y > ymax:
                        out_of_bounds += 1
    except OSError as exc:
        report.failures.append(str(exc))
        return report

    report.unique_agents = len(frames_by_agent)

    if report.data_rows < min_rows:
        report.failures.append(
            f"expected at least {min_rows} data rows, found {report.data_rows}"
        )
    if report.unique_agents < min_agents:
        report.failures.append(
            f"expected at least {min_agents} agents, found {report.unique_agents}"
        )
    if report.duplicate_id_frame_pairs:
        report.failures.append(
            f"found {report.duplicate_id_frame_pairs} duplicate id-frame pairs"
        )
    if out_of_bounds:
        report.failures.append(f"{out_of_bounds} points outside expected bounds")

    for agent_id, frames in frames_by_agent.items():
        if frames != sorted(frames):
            report.non_monotonic_agents += 1
            continue
        if not allow_frame_gaps and len(frames) > 1:
            gaps = [b - a for a, b in zip(frames, frames[1:])]
            if any(gap > 1 for gap in gaps):
                report.agents_with_frame_gaps += 1

    if report.non_monotonic_agents:
        report.failures.append(
            f"{report.non_monotonic_agents} agents have non-monotonic frame order"
        )
    if report.agents_with_frame_gaps:
        report.warnings.append(
            f"{report.agents_with_frame_gaps} agents have frame gaps"
        )
    if report.fps is None:
        report.warnings.append("no framerate header found")

    report.ok = not report.failures
    return report


def write_csv(path: Path, reports: list[TrajectoryReport]) -> None:
    fieldnames = list(asdict(reports[0]).keys())
    path.parent.mkdir(parents=True, exist_ok=True)
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
        description="Validate PeTrack .txt trajectory exports."
    )
    parser.add_argument("trajectory_files", nargs="+", type=Path)
    parser.add_argument("--min-agents", type=non_negative_int, default=1)
    parser.add_argument("--min-rows", type=non_negative_int, default=1)
    parser.add_argument("--bounds", nargs=4, metavar=("XMIN", "XMAX", "YMIN", "YMAX"))
    parser.add_argument("--allow-frame-gaps", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--csv", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bounds = parse_bounds(args.bounds) if args.bounds else None
    reports = [
        validate_file(
            path,
            min_agents=args.min_agents,
            min_rows=args.min_rows,
            bounds=bounds,
            allow_frame_gaps=args.allow_frame_gaps,
        )
        for path in args.trajectory_files
    ]

    if args.csv:
        write_csv(args.csv, reports)

    if args.json:
        print(json.dumps([asdict(report) for report in reports], indent=2))
    else:
        for report in reports:
            status = "OK" if report.ok else "FAIL"
            print(
                f"{status}: {report.path} | rows={report.data_rows} "
                f"agents={report.unique_agents} frames={report.first_frame}-{report.last_frame}"
            )
            for failure in report.failures:
                print(f"  failure: {failure}")
            for warning in report.warnings:
                print(f"  warning: {warning}")

    return 0 if all(report.ok for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
