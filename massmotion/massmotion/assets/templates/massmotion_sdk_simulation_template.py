#!/usr/bin/env python3
"""Standalone MassMotion SDK simulation template.

Run this with a Python environment that can import the installed MassMotion SDK
module, usually a versioned module such as massmotion_11_0.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path


def load_sdk(module_name: str):
    return importlib.import_module(module_name)


def run_simulation(mm, project_path: Path, run_name: str, mmdb_path: Path, speed_factor: float) -> int:
    project = mm.Project.open(str(project_path))
    simulation = mm.Simulation.create(project, run_name, str(mmdb_path))
    seen_agents: set[int] = set()

    while not simulation.is_done():
        for agent in simulation.get_all_agents():
            agent_id = agent.get_id()
            if agent_id in seen_agents:
                continue
            seen_agents.add(agent_id)
            if speed_factor != 1.0:
                desired = agent.get_speed() * speed_factor
                if agent.get_desired_unconstrained_speed() < desired:
                    agent.set_desired_unconstrained_speed(desired)
        simulation.step()
    return len(seen_agents)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a MassMotion SDK simulation.")
    parser.add_argument("--module", default="massmotion_11_0")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--run-name", default="DefaultRun")
    parser.add_argument("--mmdb", type=Path, default=Path("DefaultRun.mmdb"))
    parser.add_argument("--speed-factor", type=float, default=1.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mm = load_sdk(args.module)
    args.mmdb.parent.mkdir(parents=True, exist_ok=True)
    mm.Sdk.init()
    try:
        agent_count = run_simulation(mm, args.project, args.run_name, args.mmdb, args.speed_factor)
        print(f"Run {args.run_name} completed with {agent_count} observed agents")
        return 0
    finally:
        mm.Sdk.fini()


if __name__ == "__main__":
    sys.exit(main())
