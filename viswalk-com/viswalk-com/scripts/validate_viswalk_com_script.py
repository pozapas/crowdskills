#!/usr/bin/env python3
"""Static checks for Python scripts that automate Viswalk/Vissim COM.

The validator catches common mistakes before a script launches Vissim. It does
not execute the target script and cannot verify that object keys exist in a
specific .inpx file.

Exit codes:
  0: all scripts passed required checks
  1: at least one script failed validation
  2: command-line usage error, raised by argparse
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


COM_IMPORT_PATTERNS = (
    "win32com.client",
    "comtypes.client",
)
VISWALK_TOKENS = (
    "Pedestrian",
    "Pedestrians",
    "PedestrianInputs",
    "PedestrianRoutingDecisions",
    "PedRout",
    "Areas",
    "AreaMeasurements",
    "PedestrianTravelTimeMeasurements",
)
SIM_RUN_TOKENS = ("RunContinuous", "RunSingleStep")


@dataclass
class ScriptReport:
    path: str
    ok: bool
    failures: list[str]
    warnings: list[str]
    has_com_import: bool = False
    has_vissim_dispatch: bool = False
    has_load_or_new: bool = False
    has_attvalue: bool = False
    has_setattvalue: bool = False
    has_simulation_run: bool = False
    has_viswalk_tokens: bool = False
    has_cleanup: bool = False


ValidationResult = ScriptReport


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    return any(token in text for token in tokens)


def find_com_import(tree: ast.AST, text: str) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in COM_IMPORT_PATTERNS:
                    return True
        if isinstance(node, ast.ImportFrom):
            if node.module in COM_IMPORT_PATTERNS:
                return True
    return contains_any(text, COM_IMPORT_PATTERNS)


def validate_file(path: Path, *, require_viswalk: bool, strict: bool) -> ScriptReport:
    report = ScriptReport(path=str(path), ok=False, failures=[], warnings=[])
    if not path.exists():
        report.failures.append("file does not exist")
        return report
    if path.suffix.lower() != ".py":
        report.warnings.append("file extension is not .py")

    try:
        text = read_text(path)
    except OSError as exc:
        report.failures.append(str(exc))
        return report

    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        report.failures.append(f"syntax error: {exc}")
        return report

    report.has_com_import = find_com_import(tree, text)
    report.has_vissim_dispatch = (
        "Vissim.Vissim" in text
        and ("EnsureDispatch(" in text or re.search(r"\bDispatch\(", text) is not None)
    )
    report.has_load_or_new = any(token in text for token in (".LoadNet(", ".LoadProject(", ".New("))
    report.has_attvalue = ".AttValue(" in text or "AttValue(" in text
    report.has_setattvalue = ".SetAttValue(" in text or "SetAttValue(" in text
    report.has_simulation_run = contains_any(text, SIM_RUN_TOKENS)
    report.has_viswalk_tokens = contains_any(text, VISWALK_TOKENS)
    report.has_cleanup = any(token in text for token in ("ResumeUpdateGUI", ".Stop(", ".Exit(", "finally:"))

    if not report.has_com_import:
        report.failures.append("missing win32com.client or comtypes.client import")
    if not report.has_vissim_dispatch:
        report.failures.append("missing Vissim COM Dispatch or EnsureDispatch call")
    if not report.has_load_or_new:
        report.warnings.append("script does not load a network, load a project, or create a new network")
    if not report.has_attvalue:
        report.warnings.append("script does not read COM attributes with AttValue")
    if not report.has_setattvalue:
        report.warnings.append("script does not write COM attributes with SetAttValue")
    if not report.has_simulation_run:
        report.warnings.append("script does not run the simulation")
    if require_viswalk and not report.has_viswalk_tokens:
        report.failures.append("missing Viswalk/pedestrian-specific COM object usage")
    if not report.has_cleanup:
        report.warnings.append("no obvious cleanup, Stop, Exit, ResumeUpdateGUI, or finally block found")

    risky_path_pattern = re.compile(r"['\"][A-Za-z]:\\(?!\\)")
    if risky_path_pattern.search(text):
        report.warnings.append("contains Windows paths that may need raw strings or escaped backslashes")
    if "GetMultiAttValues" in text and "to_list" not in text and "list(" not in text:
        report.warnings.append("uses GetMultiAttValues without an obvious COM tuple conversion")
    later_interval_volume = re.search(r"SetAttValue\(\s*['\"]Volume\(([2-9]|\d{2,})\)", text)
    if later_interval_volume and "Cont(" not in text:
        report.warnings.append("sets later interval volume without checking interval continuity")

    if strict and report.warnings:
        report.failures.extend(f"strict warning: {warning}" for warning in report.warnings)

    report.ok = not report.failures
    return report


def write_csv(path: Path, reports: list[ScriptReport]) -> None:
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
        description="Validate Python scripts that automate Viswalk/Vissim COM."
    )
    parser.add_argument("scripts", nargs="+", type=Path)
    parser.add_argument("--require-viswalk", action="store_true")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--csv", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reports = [
        validate_file(path, require_viswalk=args.require_viswalk, strict=args.strict)
        for path in args.scripts
    ]

    if args.csv and reports:
        write_csv(args.csv, reports)

    if args.json:
        print(json.dumps([asdict(report) for report in reports], indent=2))
    else:
        for report in reports:
            status = "OK" if report.ok else "FAIL"
            print(f"{status}: {report.path}")
            for failure in report.failures:
                print(f"  failure: {failure}")
            for warning in report.warnings:
                print(f"  warning: {warning}")

    return 0 if all(report.ok for report in reports) else 1


if __name__ == "__main__":
    sys.exit(main())
