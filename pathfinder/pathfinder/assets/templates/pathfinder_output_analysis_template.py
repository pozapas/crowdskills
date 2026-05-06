#!/usr/bin/env python3
"""Starter analysis template for Pathfinder summary and occupant-history output.

The template uses only the Python standard library. Extend the metric extraction
once the specific Pathfinder output filenames and column headers are known.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any


def normalize_column(value: str) -> str:
    lowered = value.strip().lower()
    lowered = lowered.replace("(s)", "").replace("(m)", "").replace("(m/s)", "")
    lowered = re.sub(r"[^a-z0-9]+", "", lowered)
    aliases = {
        "t": "time",
        "timesec": "time",
        "simulationtime": "time",
        "occupantid": "id",
        "agentid": "id",
        "personid": "id",
        "xpos": "x",
        "xposition": "x",
        "ypos": "y",
        "yposition": "y",
        "v": "speed",
        "velocity": "speed",
    }
    return aliases.get(lowered, lowered)


def find_first(root: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        matches = sorted(root.rglob(pattern))
        if matches:
            return matches[0]
    return None


def parse_summary(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    metrics: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = re.sub(r"\s+", "_", key.strip().lower())
        if key:
            metrics[key] = value.strip()
    return metrics


def parse_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def analyze_occupant_history(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            return {"occupant_history_rows": 0, "occupant_history_error": "missing header"}
        column_map = {normalize_column(column): column for column in reader.fieldnames}
        time_col = column_map.get("time")
        id_col = column_map.get("id")
        speed_col = column_map.get("speed")
        active_col = column_map.get("active")

        occupant_ids: set[str] = set()
        rows = 0
        final_time = 0.0
        max_speed = 0.0
        active_at_final = 0

        for row in reader:
            rows += 1
            if id_col and row.get(id_col):
                occupant_ids.add(row[id_col])
            if time_col:
                value = parse_float(row.get(time_col, ""))
                if value is not None:
                    final_time = max(final_time, value)
            if speed_col:
                value = parse_float(row.get(speed_col, ""))
                if value is not None:
                    max_speed = max(max_speed, value)
            if active_col and row.get(active_col, "").strip().lower() in {"true", "1", "yes"}:
                active_at_final += 1

    return {
        "occupant_history_file": str(path),
        "occupant_history_rows": rows,
        "occupant_count": len(occupant_ids),
        "final_time_seconds": final_time,
        "max_speed": max_speed,
        "active_rows": active_at_final,
    }


def analyze_output_dir(root: Path) -> dict[str, Any]:
    summary_path = find_first(root, ["*summary*.txt", "*summary*.html"])
    occupant_path = find_first(root, ["*occupant*history*.csv", "*occupants*detailed*.csv", "*occupants*.csv"])
    result: dict[str, Any] = {"output_dir": str(root)}
    result["summary_file"] = str(summary_path) if summary_path else ""
    result.update({f"summary_{key}": value for key, value in parse_summary(summary_path).items()})
    result.update(analyze_occupant_history(occupant_path))
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
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
    parser = argparse.ArgumentParser(description="Analyze Pathfinder output folders.")
    parser.add_argument("output_dirs", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, default=Path("pathfinder_output_metrics.csv"))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = [analyze_output_dir(path) for path in args.output_dirs]
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        write_csv(args.out, rows)
        print(f"Wrote {len(rows)} output metric rows to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
