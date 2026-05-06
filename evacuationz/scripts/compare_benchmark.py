#!/usr/bin/env python3
"""
compare_benchmark.py - Compare an observed Evacuationz result with a benchmark.

Responsibilities:
- List built-in Evacuationz benchmark cases.
- Extract observed stop time from a number, log file, or CSV file.
- Compare observed and expected values with explicit tolerances.

Usage:
    python compare_benchmark.py --list
    python compare_benchmark.py --case door_flow_100_agents_1m --observed 108
    python compare_benchmark.py --case movement_corridor_path --observed-file log.html --json

Exit Codes:
    0  - Benchmark passed or list printed
    1  - General failure
    2  - Invalid arguments
    10 - Benchmark mismatch
    11 - Verification failure
"""

import argparse
import csv
import json
import math
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "movement_corridor_path": {
        "expected": 40.5,
        "tolerance": 1.0,
        "source": "Evacuationz_Verification.pdf section 2.1.1",
        "mechanism": "single-agent corridor path travel",
    },
    "movement_corridor_node": {
        "expected": 40.5,
        "tolerance": 1.0,
        "source": "Evacuationz_Verification.pdf section 2.1.2",
        "mechanism": "single-agent corridor node travel",
    },
    "stair_speed_imo": {
        "expected": 12.0,
        "tolerance": 1.0,
        "source": "Evacuationz_Verification.pdf section 2.1.3",
        "mechanism": "single-agent stair movement",
    },
    "door_flow_100_agents_1m": {
        "expected": 108.0,
        "tolerance": 2.16,
        "source": "Evacuationz_Verification.pdf section 2.2",
        "mechanism": "100 agents through 1.0 m door",
    },
    "sfpe_handbook_9_storey": {
        "expected": 1871.0,
        "tolerance": 93.55,
        "source": "Evacuationz_Verification.pdf section 2.5",
        "mechanism": "SFPE Handbook 9-storey building example",
    },
    "sfpe_guide_300_zero_start": {
        "expected": 221.5,
        "tolerance": 11.08,
        "source": "Evacuationz_Verification.pdf section 2.6",
        "mechanism": "SFPE Guide example with zero start distance",
    },
    "sfpe_guide_300_fixed_start": {
        "expected": 283.0,
        "tolerance": 14.15,
        "source": "Evacuationz_Verification.pdf section 2.6",
        "mechanism": "SFPE Guide example with 200 ft start distance",
    },
    "exercise2_default_single_agent": {
        "expected": 1890.0,
        "tolerance": 2.0,
        "source": "Evacuationz_Exercise Guide.pdf exercise 2",
        "mechanism": "default single-agent pre-evacuation and travel",
    },
    "exercise3_custom_agent": {
        "expected": 36.5,
        "tolerance": 1.0,
        "source": "Evacuationz_Exercise Guide.pdf exercise 3",
        "mechanism": "custom speed, pre-evacuation, start distance",
    },
    "edm_awake_familiar_remote": {
        "expected": 61.0,
        "tolerance": 2.0,
        "source": "Evacuationz_Exercise Guide.pdf exercise 24",
        "mechanism": "EDM awake/familiar remote alarm case",
    },
    "edm_asleep_unfamiliar_remote": {
        "expected": 600.0,
        "tolerance": 5.0,
        "source": "Evacuationz_Exercise Guide.pdf exercise 24",
        "mechanism": "EDM asleep/unfamiliar remote alarm case",
    },
}


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


def extract_from_log(text: str) -> Optional[float]:
    patterns = [
        r"Simulation\s*#?\d*\s*stopped\s+at\s+([-+]?\d+(?:\.\d+)?)\s*s",
        r"stopped\s+at\s+([-+]?\d+(?:\.\d+)?)\s*s",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def extract_from_csv(path: Path) -> Optional[float]:
    last_time: Optional[float] = None
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row:
                continue
            try:
                value = float(row[0])
            except ValueError:
                continue
            last_time = value
    return last_time


def extract_observed(path: Path) -> Optional[float]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    from_log = extract_from_log(text)
    if from_log is not None:
        return from_log
    if path.suffix.lower() == ".csv":
        return extract_from_csv(path)
    numbers = [float(match.group(0)) for match in re.finditer(r"[-+]?\d+(?:\.\d+)?", text)]
    return numbers[-1] if numbers else None


def compare(case_id: str, observed: float, tolerance: Optional[float]) -> Result:
    if case_id not in BENCHMARKS:
        return Result(False, f"Unknown benchmark case: {case_id}", errors=[f"Unknown case: {case_id}"])
    if not math.isfinite(observed):
        return Result(False, "Observed value is not finite", errors=["Observed value must be finite"])

    case = BENCHMARKS[case_id]
    expected = float(case["expected"])
    tol = float(tolerance if tolerance is not None else case["tolerance"])
    diff = observed - expected
    abs_diff = abs(diff)
    relative = abs_diff / expected if expected else 0.0
    passed = abs_diff <= tol

    data = {
        "case_id": case_id,
        "mechanism": case["mechanism"],
        "source": case["source"],
        "expected": expected,
        "observed": observed,
        "difference": diff,
        "absolute_difference": abs_diff,
        "relative_difference": relative,
        "tolerance": tol,
        "status": "pass" if passed else "fail",
    }
    if passed:
        return Result(True, f"{case_id} passed", data=data)
    return Result(False, f"{case_id} failed", data=data, errors=[f"Difference {abs_diff:g} exceeds tolerance {tol:g}"])


def verify_result(result: Result) -> Tuple[bool, str]:
    if "case_id" not in result.data:
        return False, "Missing case_id"
    for key in ("expected", "observed", "absolute_difference", "tolerance", "status"):
        if key not in result.data:
            return False, f"Missing comparison field: {key}"
    if result.data["status"] not in {"pass", "fail"}:
        return False, "Invalid status"
    return True, "Verification passed"


def list_cases(json_output: bool) -> None:
    payload = {
        case_id: {
            "expected": case["expected"],
            "tolerance": case["tolerance"],
            "mechanism": case["mechanism"],
            "source": case["source"],
        }
        for case_id, case in sorted(BENCHMARKS.items())
    }
    if json_output:
        print(json.dumps(payload, indent=2))
        return
    for case_id, case in payload.items():
        print(f"{case_id}: expected={case['expected']} tolerance={case['tolerance']} ({case['mechanism']})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Evacuationz output with a built-in benchmark")
    parser.add_argument("--list", action="store_true", help="List benchmark cases")
    parser.add_argument("--case", help="Benchmark case id")
    parser.add_argument("--observed", type=float, help="Observed value in seconds")
    parser.add_argument("--observed-file", type=Path, help="Log, text, or CSV file from which to extract observed time")
    parser.add_argument("--tolerance", type=float, help="Override absolute tolerance in seconds")
    parser.add_argument("--json", action="store_true", help="Print JSON result")
    parser.add_argument("--output", "-o", type=Path, help="Write JSON result to file")
    parser.add_argument("--no-verify", action="store_true", help="Skip result self-verification")
    args = parser.parse_args()

    if args.list:
        list_cases(args.json)
        sys.exit(0)

    if not args.case:
        parser.error("--case is required unless --list is used")
    if args.observed is None and args.observed_file is None:
        parser.error("provide --observed or --observed-file")
    if args.observed is not None and args.observed_file is not None:
        parser.error("use only one of --observed or --observed-file")

    observed = args.observed
    if args.observed_file is not None:
        if not args.observed_file.exists():
            result = Result(False, f"Observed file not found: {args.observed_file}", errors=["Observed file not found"])
        else:
            extracted = extract_observed(args.observed_file)
            if extracted is None:
                result = Result(False, f"Could not extract observed time from {args.observed_file}", errors=["No observed time found"])
            else:
                result = compare(args.case, extracted, args.tolerance)
                result.data["observed_file"] = str(args.observed_file)
    else:
        result = compare(args.case, float(observed), args.tolerance)

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
        print(result.message)
        if result.data:
            print(f"Expected: {result.data['expected']} s")
            print(f"Observed: {result.data['observed']} s")
            print(f"Tolerance: {result.data['tolerance']} s")
            print(f"Difference: {result.data['difference']} s")
        for error in result.errors:
            print(f"Error: {error}", file=sys.stderr)

    if result.success:
        sys.exit(0)
    if any("Self-verification failed" in error for error in result.errors):
        sys.exit(11)
    sys.exit(10)


if __name__ == "__main__":
    main()

