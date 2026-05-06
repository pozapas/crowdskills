#!/usr/bin/env python3
"""Manifest-driven Pathfinder command-line batch runner template.

This template executes one Pathfinder model per manifest row by calling
testsim.bat. Customize output-folder handling to match the model's configured
output location before using it for production studies.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def write_results(path: Path, rows: list[dict[str, Any]]) -> None:
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


def build_command(row: dict[str, str], fallback_testsim: Path | None) -> list[str]:
    testsim = Path(row.get("testsim_path") or str(fallback_testsim or "testsim.bat"))
    model = Path(row["model_path"])
    return [str(testsim), str(model)]


def run_row(row: dict[str, str], args: argparse.Namespace) -> dict[str, Any]:
    result_row: dict[str, Any] = dict(row)
    output_dir = Path(row.get("output_dir") or Path(args.output_root) / row.get("run_id", "run"))
    output_dir.mkdir(parents=True, exist_ok=True)
    command = build_command(row, args.testsim)
    started = time.perf_counter()

    if args.dry_run:
        result_row.update(
            {
                "completed": True,
                "returncode": 0,
                "elapsed_wall_seconds": 0,
                "command": " ".join(command),
                "stdout_tail": "",
                "stderr_tail": "",
                "error": "",
            }
        )
        return result_row

    try:
        completed = subprocess.run(
            command,
            cwd=args.cwd,
            text=True,
            capture_output=True,
            timeout=args.timeout,
            check=False,
        )
        elapsed = time.perf_counter() - started
        result_row.update(
            {
                "completed": completed.returncode == 0,
                "returncode": completed.returncode,
                "elapsed_wall_seconds": round(elapsed, 3),
                "command": " ".join(command),
                "stdout_tail": completed.stdout[-2000:],
                "stderr_tail": completed.stderr[-2000:],
                "error": "",
            }
        )
    except Exception as exc:
        elapsed = time.perf_counter() - started
        result_row.update(
            {
                "completed": False,
                "returncode": "",
                "elapsed_wall_seconds": round(elapsed, 3),
                "command": " ".join(command),
                "stdout_tail": "",
                "stderr_tail": "",
                "error": str(exc),
            }
        )
    return result_row


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Pathfinder testsim.bat from a manifest.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("results") / "pathfinder_batch_results.csv")
    parser.add_argument("--testsim", type=Path, help="fallback testsim.bat path when row is blank")
    parser.add_argument("--output-root", type=Path, default=Path("results"))
    parser.add_argument("--cwd", type=Path, help="working directory for testsim.bat")
    parser.add_argument("--timeout", type=float, default=None, help="seconds per run")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stop-on-error", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_manifest(args.manifest)
    results: list[dict[str, Any]] = []
    for row in rows:
        result = run_row(row, args)
        results.append(result)
        write_results(args.out, results)
        if args.stop_on_error and not result.get("completed"):
            break
    print(f"Wrote {len(results)} batch result rows to {args.out}")
    return 0 if all(row.get("completed") for row in results) else 1


if __name__ == "__main__":
    sys.exit(main())
