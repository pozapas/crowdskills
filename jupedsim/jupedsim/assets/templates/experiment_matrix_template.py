"""JuPedSim experiment matrix template.

Use this as a starting point for model comparisons, sensitivity analysis, and
reproducibility manifests.
"""

from __future__ import annotations

import csv
import pathlib
from dataclasses import asdict, dataclass, replace

import jupedsim as jps
from shapely import Polygon


@dataclass(frozen=True)
class RunConfig:
    scenario: str
    model_name: str
    seed: int
    number_of_agents: int
    desired_speed: float
    radius: float
    dt: float = 0.01
    every_nth_frame: int = 5
    max_iterations: int = 10000

    @property
    def output_file(self) -> pathlib.Path:
        return pathlib.Path(
            f"{self.scenario}_{self.model_name}_n{self.number_of_agents}_"
            f"v{self.desired_speed:.2f}_seed{self.seed}.sqlite"
        )


def build_geometry() -> tuple[Polygon, Polygon, Polygon]:
    walkable_area = Polygon([(0, 0), (30, 0), (30, 10), (0, 10)])
    spawn_area = Polygon([(1, 1), (6, 1), (6, 9), (1, 9)])
    exit_polygon = Polygon([(29, 4), (30, 4), (30, 6), (29, 6)])
    return walkable_area, spawn_area, exit_polygon


def model_and_params(config: RunConfig):
    if config.model_name == "csm":
        return (
            jps.CollisionFreeSpeedModel(),
            jps.CollisionFreeSpeedModelAgentParameters,
        )
    if config.model_name == "csm_v2":
        return (
            jps.CollisionFreeSpeedModelV2(),
            jps.CollisionFreeSpeedModelV2AgentParameters,
        )
    if config.model_name == "avm":
        return (
            jps.AnticipationVelocityModel(rng_seed=config.seed),
            jps.AnticipationVelocityModelAgentParameters,
        )
    raise ValueError(f"Unsupported model_name: {config.model_name}")


def run_one(config: RunConfig) -> dict[str, object]:
    walkable_area, spawn_area, exit_polygon = build_geometry()
    model, parameter_class = model_and_params(config)
    simulation = jps.Simulation(
        model=model,
        geometry=walkable_area,
        dt=config.dt,
        trajectory_writer=jps.SqliteTrajectoryWriter(
            output_file=config.output_file,
            every_nth_frame=config.every_nth_frame,
        ),
    )

    exit_id = simulation.add_exit_stage(exit_polygon)
    journey_id = simulation.add_journey(jps.JourneyDescription([exit_id]))
    positions = jps.distribute_by_number(
        polygon=spawn_area,
        number_of_agents=config.number_of_agents,
        distance_to_agents=2 * config.radius + 0.05,
        distance_to_polygon=config.radius + 0.05,
        seed=config.seed,
    )

    for position in positions:
        simulation.add_agent(
            parameter_class(
                position=position,
                journey_id=journey_id,
                stage_id=exit_id,
                desired_speed=config.desired_speed,
                radius=config.radius,
            )
        )

    while (
        simulation.agent_count() > 0
        and simulation.iteration_count() < config.max_iterations
    ):
        simulation.iterate()
    simulation._writer.close()

    return {
        **asdict(config),
        "output_file": str(config.output_file),
        "iterations": simulation.iteration_count(),
        "elapsed_time": simulation.elapsed_time(),
        "final_agent_count": simulation.agent_count(),
        "completed": simulation.agent_count() == 0,
    }


def main() -> None:
    base = RunConfig(
        scenario="corridor",
        model_name="csm",
        seed=1001,
        number_of_agents=50,
        desired_speed=1.2,
        radius=0.2,
    )
    configs = [
        replace(base, model_name=model_name, seed=seed)
        for model_name in ["csm", "csm_v2", "avm"]
        for seed in [1001, 1002, 1003]
    ]

    rows = [run_one(config) for config in configs]
    with open("manifest.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()

