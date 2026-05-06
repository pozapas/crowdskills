#!/usr/bin/env python3
"""
summarize_evac_outputs.py - Summarize Evacuationz output folders.

Responsibilities:
- Inventory common Evacuationz log and CSV outputs.
- Extract version, total agents, stop time, warnings/errors, and CSV shape.
- Produce a compact JSON or text digest for QA and reporting.

Usage:
    python summarize_evac_outputs.py path/to/output-folder
    python summarize_evac_outputs.py path/to/output-folder --json
    python summarize_evac_outputs.py path/to/log.html --output digest.json

Exit Codes:
    0  - Success
    1  - General failure
    2  - Invalid arguments
    10 - No usable outputs found
    11 - Verification failure
"""

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Result:
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.success

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def summarize_log(path: Path) -> Dict[str, Any]:
    text = read_text(path)
    version_match = re.search(r"Evacuat\w*\s+version\s+([^<\r\n]+)", text, flags=re.IGNORECASE)
    total_match = re.search(r"Total\s+number\s+of\s+agents\s*=\s*(\d+)", text, flags=re.IGNORECASE)
    stop_match = re.search(r"stopped\s+at\s+([-+]?\d+(?:\.\d+)?)\s*s", text, flags=re.IGNORECASE)
    issue_lines = []
    for line in re.split(r"\r?\n", text):
        plain = re.sub(r"<[^>]+>", " ", line)
        if re.search(r"\b(error|warning|missing|failed)\b", plain, flags=re.IGNORECASE):
            issue_lines.append(" ".join(plain.split()))

    return {
        "path": str(path),
        "version": version_match.group(1).strip() if version_match else None,
        "total_agents": int(total_match.group(1)) if total_match else None,
        "stop_time_s": float(stop_match.group(1)) if stop_match else None,
        "issue_lines": issue_lines[:50],
        "issue_count": len(issue_lines),
    }


def summarize_csv(path: Path) -> Dict[str, Any]:
    rows = 0
    columns = 0
    header: List[str] = []
    first_data: List[str] = []
    last_data: List[str] = []
    last_time: Optional[float] = None

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row:
                continue
            if rows == 0:
                header = row
                columns = len(row)
            else:
                if not first_data:
                    first_data = row
                last_data = row
                try:
                    last_time = float(row[0])
                except (ValueError, IndexError):
                    pass
            rows += 1

    return {
        "path": str(path),
        "rows": rows,
        "columns": columns,
        "header": header,
        "first_data_row": first_data,
        "last_data_row": last_data,
        "last_time_s": last_time,
    }


def classify_output(path: Path) -> str:
    name = path.name.lower()
    if name.endswith(".html") and "log" in name:
        return "log"
    if name.endswith(".html") and "result" in name:
        return "results_html"
    if name.endswith(".csv") and "pre" in name and "evac" in name:
        return "pre_evac_csv"
    if name.endswith(".csv") and "agent" in name:
        return "agents_csv"
    if name.endswith(".csv") and "node" in name:
        return "nodes_csv"
    if name.endswith(".csv") and "evac" in name:
        return "evac_csv"
    if name.endswith(".smv"):
        return "smokeview"
    return "other"


def collect_outputs(path: Path) -> List[Path]:
    if path.is_file():
        return [path]
    patterns = ["*.html", "*.csv", "*.smv"]
    files: List[Path] = []
    for pattern in patterns:
        files.extend(path.glob(pattern))
    return sorted(files)


def process(path: Path) -> Result:
    if not path.exists():
        return Result(False, f"Path not found: {path}", errors=[f"Path not found: {path}"])

    files = collect_outputs(path)
    if not files:
        return Result(False, f"No Evacuationz output files found in {path}", errors=["No output files found"])

    logs: List[Dict[str, Any]] = []
    csvs: List[Dict[str, Any]] = []
    inventory: Dict[str, int] = {}
    warnings: List[str] = []
    errors: List[str] = []

    for file_path in files:
        role = classify_output(file_path)
        inventory[role] = inventory.get(role, 0) + 1
        try:
            if role == "log":
                logs.append(summarize_log(file_path))
            elif file_path.suffix.lower() == ".csv":
                csvs.append({**summarize_csv(file_path), "role": role})
        except Exception as exc:
            warnings.append(f"{file_path}: could not summarize: {exc}")

    if not logs:
        warnings.append("No log.html file found")
    if not csvs and inventory.get("results_html", 0) == 0:
        warnings.append("No CSV or results HTML output found")

    primary_log = logs[0] if logs else {}
    data = {
        "target": str(path),
        "files_found": len(files),
        "inventory": inventory,
        "logs": logs,
        "csvs": csvs,
        "summary": {
            "version": primary_log.get("version"),
            "total_agents": primary_log.get("total_agents"),
            "stop_time_s": primary_log.get("stop_time_s"),
            "log_issue_count": primary_log.get("issue_count", 0),
        },
    }

    recognized = sum(count for role, count in inventory.items() if role != "other")
    success = recognized > 0
    message = "Output summary complete" if success else "No recognized Evacuationz outputs found"
    if not success:
        errors.append("No recognized Evacuationz outputs found")
    return Result(success, message, data=data, errors=errors, warnings=warnings)


def verify_result(result: Result) -> Tuple[bool, str]:
    if "files_found" not in result.data:
        return False, "Missing files_found"
    if result.data["files_found"] <= 0:
        return False, "No files recorded"
    if "inventory" not in result.data:
        return False, "Missing inventory"
    return True, "Verification passed"


def print_text(result: Result) -> None:
    print(result.message)
    print(f"Files found: {result.data.get('files_found', 0)}")
    print(f"Inventory: {json.dumps(result.data.get('inventory', {}), sort_keys=True)}")
    summary = result.data.get("summary", {})
    if summary:
        print(f"Version: {summary.get('version')}")
        print(f"Total agents: {summary.get('total_agents')}")
        print(f"Stop time: {summary.get('stop_time_s')}")
        print(f"Log issues: {summary.get('log_issue_count')}")
    for warning in result.warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    for error in result.errors:
        print(f"Error: {error}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize Evacuationz output files")
    parser.add_argument("path", type=Path, help="Output directory or single output file")
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    parser.add_argument("--output", "-o", type=Path, help="Write JSON result to file")
    parser.add_argument("--no-verify", action="store_true", help="Skip result self-verification")
    args = parser.parse_args()

    result = process(args.path)
    if result.data and not args.no_verify:
        ok, message = verify_result(result)
        if not ok:
            result.success = False
            result.errors.append(f"Self-verification failed: {message}")

    payload = result.to_dict()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2))

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_text(result)

    if result.success:
        sys.exit(0)
    if any("Self-verification failed" in error for error in result.errors):
        sys.exit(11)
    sys.exit(10)


if __name__ == "__main__":
    main()

