"""JuPedSim evacuation scenario template.

Customize geometry, model, population, and postprocessing for a single
reproducible simulation.
"""

from __future__ import annotations

import pathlib
import sys
from dataclasses import asdict, dataclass

import jupedsim as jps
from shapely import Polygon


@dataclass(frozen=True)
class ScenarioConfig:
    name: str = "baseline"
    output_file: pathlib.Path = pathlib.Path("baseline.sqlite")
    dt: float = 0.01
    every_nth_frame: int = 5
    max_iterations: int = 10000
    number_of_agents: int = 50
    seed: int = 12345
    desired_speed: float = 1.2
    radius: float = 0.2


def build_geometry() -> tuple[Polygon, Polygon, Polygon]:
    """Return walkable area, spawn area, and exit polygon."""
    walkable_area = Polygon([(0, 0), (20, 0), (20, 8), (0, 8)])
    spawn_area = Polygon([(1, 1), (5, 1), (5, 7), (1, 7)])
    exit_polygon = Polygon([(19, 3), (20, 3), (20, 5), (19, 5)])
    return walkable_area, spawn_area, exit_polygon


def build_simulation(config: ScenarioConfig, walkable_area: Polygon) -> jps.Simulation:
    return jps.Simulation(
        model=jps.CollisionFreeSpeedModel(),
        geometry=walkable_area,
        dt=config.dt,
        trajectory_writer=jps.SqliteTrajectoryWriter(
            output_file=config.output_file,
            every_nth_frame=config.every_nth_frame,
        ),
    )


def add_route(simulation: jps.Simulation, exit_polygon: Polygon) -> tuple[int, int]:
    exit_id = simulation.add_exit_stage(exit_polygon)
    journey = jps.JourneyDescription([exit_id])
    journey_id = simulation.add_journey(journey)
    return journey_id, exit_id


def add_population(
    simulation: jps.Simulation,
    config: ScenarioConfig,
    spawn_area: Polygon,
    journey_id: int,
    exit_id: int,
) -> list[int]:
    positions = jps.distribute_by_number(
        polygon=spawn_area,
        number_of_agents=config.number_of_agents,
        distance_to_agents=2 * config.radius + 0.05,
        distance_to_polygon=config.radius + 0.05,
        seed=config.seed,
    )

    agent_ids = []
    params = jps.CollisionFreeSpeedModelAgentParameters(
        journey_id=journey_id,
        stage_id=exit_id,
        desired_speed=config.desired_speed,
        radius=config.radius,
    )
    for position in positions:
        params.position = position
        agent_ids.append(simulation.add_agent(params))
    return agent_ids


def run(simulation: jps.Simulation, config: ScenarioConfig) -> dict[str, object]:
    try:
        while (
            simulation.agent_count() > 0
            and simulation.iteration_count() < config.max_iterations
        ):
            simulation.iterate()
    except KeyboardInterrupt:
        if simulation._writer:
            simulation._writer.close()
        sys.exit(1)
    finally:
        if simulation._writer:
            simulation._writer.close()

    return {
        **asdict(config),
        "iterations": simulation.iteration_count(),
        "elapsed_time": simulation.elapsed_time(),
        "final_agent_count": simulation.agent_count(),
        "completed": simulation.agent_count() == 0,
    }


def main() -> None:
    config = ScenarioConfig()
    walkable_area, spawn_area, exit_polygon = build_geometry()
    simulation = build_simulation(config, walkable_area)
    journey_id, exit_id = add_route(simulation, exit_polygon)
    add_population(simulation, config, spawn_area, journey_id, exit_id)
    summary = run(simulation, config)
    print(summary)


if __name__ == "__main__":
    main()

