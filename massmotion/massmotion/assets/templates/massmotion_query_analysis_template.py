#!/usr/bin/env python3
"""Analyze a MassMotion mmdb file through the Python SDK.

This template connects an existing mmdb to a SimulationRun object and evaluates
an AgentSummaryTableQuery. Adjust column indexes for the configured SDK/query
version before using the metrics in a report.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any


def load_sdk(module_name: str):
    return importlib.import_module(module_name)


def analyze_agent_summary(mm, project_path: Path, mmdb_path: Path, run_name: str) -> dict[str, Any]:
    project = mm.Project.open(str(project_path))
    sim_run_name = project.find_next_unique_name(run_name)
    sim_run = project.create_simulation_run(sim_run_name)
    sim_run.connect(str(mmdb_path))
    query_name = project.find_next_unique_name("agent_summary_table_query")
    query = project.create_agent_summary_table_query(query_name, sim_run.get_id())
    table = query.evaluate()

    durations: list[float] = []
    duration_column_index = 7
    if table.is_valid():
        for row_index in range(table.get_row_count()):
            durations.append(table.get_double_value(row_index, duration_column_index))

    project.remove_and_delete_object(query.get_id())
    return {
        "project": str(project_path),
        "mmdb": str(mmdb_path),
        "run_name": sim_run_name,
        "agent_count": len(durations),
        "min_duration": min(durations) if durations else None,
        "max_duration": max(durations) if durations else None,
        "avg_duration": sum(durations) / len(durations) if durations else None,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze MassMotion agent summary metrics.")
    parser.add_argument("--module", default="massmotion_11_0")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--mmdb", type=Path, required=True)
    parser.add_argument("--run-name", default="ScriptedAnalysisRun")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mm = load_sdk(args.module)
    mm.Sdk.init()
    try:
        result = analyze_agent_summary(mm, args.project, args.mmdb, args.run_name)
        print(json.dumps(result, indent=2))
        return 0
    finally:
        mm.Sdk.fini()


if __name__ == "__main__":
    sys.exit(main())
