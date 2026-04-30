# JuPedSim API Map

This reference maps common simulation needs to JuPedSim objects. It is based on the local JuPedSim source package and is intended as a compact navigation layer, not a replacement for the full docs.

## Package Pattern

```python
import pathlib
import jupedsim as jps
from shapely import GeometryCollection, Polygon
```

Use `jps` consistently. JuPedSim combines Python workflow code with a C++ simulation core.

## Simulation

```python
simulation = jps.Simulation(
    model=jps.CollisionFreeSpeedModel(),
    geometry=geometry,
    dt=0.01,
    trajectory_writer=jps.SqliteTrajectoryWriter(
        output_file=pathlib.Path("trajectory.sqlite"),
        every_nth_frame=4,
    ),
)
```

Key methods:

| Method | Purpose |
| --- | --- |
| `add_waypoint_stage(position, distance)` | Add target reached within a radius |
| `add_exit_stage(polygon)` | Add removal region; agents target its center |
| `add_queue_stage(positions)` | Add ordered queue with `pop(count)` release |
| `add_waiting_set_stage(positions)` | Add waiting positions with active/inactive state |
| `add_direct_steering_stage()` | Add special stage for direct target control |
| `add_journey(journey)` | Register a journey graph |
| `add_agent(parameters)` | Add an agent with model-specific parameters |
| `iterate(count=1)` | Advance the simulation |
| `agent_count()` | Current number of agents |
| `iteration_count()` | Number of iterations performed |
| `elapsed_time()` | Simulated seconds |
| `delta_time()` | Time step length |
| `agents()` and `agent(agent_id)` | Inspect active agents |
| `agents_in_range(pos, distance)` | IDs within a search radius |
| `agents_in_polygon(poly)` | Agents inside a polygon |
| `switch_agent_journey(agent_id, journey_id, stage_id)` | Change tactical route |
| `mark_agent_for_removal(agent_id)` | Remove at start of next iteration |
| `removed_agents()` | IDs removed in last iteration |
| `get_stage(stage_id)` | Retrieve stage proxy |
| `get_geometry()` | Access current geometry |
| `switch_geometry(geometry)` | Replace geometry if agents and stages remain valid |
| `set_tracing(True)` / `get_last_trace()` | Debug operational decisions |

## Geometry

`Simulation(..., geometry=...)` accepts:

- list of `(x, y)` tuples, with optional `excluded_areas` for holes
- Shapely `Polygon`, `MultiPolygon`, `GeometryCollection`, or `MultiPoint`
- WKT strings for supported polygonal geometry

The geometry must form one simple walkable polygon after union. Use holes or `difference(...)` for obstacles. Avoid obstacles that split the walkable area into disconnected regions unless you are intentionally creating a non-routable situation for validation.

## Models And Parameters

| Model | Agent parameter class | Best for |
| --- | --- | --- |
| `CollisionFreeSpeedModel` | `CollisionFreeSpeedModelAgentParameters` | Efficient baseline, bottlenecks, evacuation examples |
| `CollisionFreeSpeedModelV2` | `CollisionFreeSpeedModelV2AgentParameters` | Per-agent neighbor and geometry repulsion |
| `AnticipationVelocityModel` | `AnticipationVelocityModelAgentParameters` | Anticipatory motion, sharp turns, wall gliding |
| `GeneralizedCentrifugalForceModel` | `GeneralizedCentrifugalForceModelAgentParameters` | Force-based research and direct steering examples |
| `SocialForceModel` | `SocialForceModelAgentParameters` | Classical social-force style experiments |

Common CSM agent parameters:

```python
jps.CollisionFreeSpeedModelAgentParameters(
    position=(1.0, 2.0),
    journey_id=journey_id,
    stage_id=exit_id,
    time_gap=1.0,
    desired_speed=1.2,
    radius=0.2,
)
```

Common CSM V2 additions:

```python
strength_neighbor_repulsion=8.0
range_neighbor_repulsion=0.1
strength_geometry_repulsion=5.0
range_geometry_repulsion=0.02
```

Common AVM additions:

```python
time_gap=1.06
wall_buffer_distance=0.1
anticipation_time=1.0
reaction_time=0.3
strength_neighbor_repulsion=8.0
range_neighbor_repulsion=0.1
```

Common GCFM parameters:

```python
mass=1
tau=0.5
desired_speed=1.2
a_v=1
a_min=0.2
b_min=0.2
b_max=0.4
```

Common SFM parameters:

```python
velocity=(0.0, 0.0)
mass=80.0
desired_speed=0.8
reaction_time=0.5
agent_scale=2000
obstacle_scale=2000
force_distance=0.08
radius=0.3
```

## Distribution Helpers

All distribution helpers require a Shapely polygon and spacing constraints.

| Function | Use |
| --- | --- |
| `distribute_by_number(...)` | Place an exact number of agents |
| `distribute_by_density(...)` | Place `round(area * density)` agents |
| `distribute_until_filled(...)` | Fill an area under spacing constraints |
| `distribute_by_percentage(...)` | Fill a percentage of the possible placement set |
| `distribute_in_circles_by_number(...)` | Ring-based placement with counts |
| `distribute_in_circles_by_density(...)` | Ring-based placement with densities |

Typical call:

```python
positions = jps.distribute_by_number(
    polygon=spawning_area,
    number_of_agents=100,
    distance_to_agents=0.4,
    distance_to_polygon=0.2,
    seed=12345,
)
```

Common placement failures indicate that the requested population, density, or spacing is incompatible with the polygon.

## Stages

| Stage | Add method | Runtime controls |
| --- | --- | --- |
| Waypoint | `add_waypoint_stage(position, distance)` | `count_targeting()` |
| Exit | `add_exit_stage(polygon)` | `count_targeting()` |
| Queue | `add_queue_stage(positions)` | `pop(count)`, `count_enqueued()`, `enqueued()` |
| Waiting set | `add_waiting_set_stage(positions)` | `state`, `count_waiting()`, `waiting()` |
| Direct steering | `add_direct_steering_stage()` | set `simulation.agent(id).target` |

Waiting set state values:

```python
jps.WaitingSetState.ACTIVE
jps.WaitingSetState.INACTIVE
```

## Journeys And Transitions

```python
journey = jps.JourneyDescription([stage_a, stage_b, exit_id])
journey.set_transition_for_stage(
    stage_a,
    jps.Transition.create_fixed_transition(stage_b),
)
journey_id = simulation.add_journey(journey)
```

Transitions:

| Transition | Use |
| --- | --- |
| `create_fixed_transition(stage_id)` | Deterministic next stage |
| `create_round_robin_transition([(stage_id, weight), ...])` | Weighted cyclic assignment |
| `create_least_targeted_transition([stage_id, ...])` | Select least-targeted candidate |
| `create_none_transition()` | No next target |

## Routing Engine

Use `jps.RoutingEngine(geometry)` to test wayfinding and diagnose routing:

```python
engine = jps.RoutingEngine(geometry)
engine.is_routable((1.0, 1.0))
waypoints = engine.compute_waypoints((1.0, 1.0), (10.0, 1.0))
```

## Serialization And Recording

SQLite writer:

```python
writer = jps.SqliteTrajectoryWriter(
    output_file=pathlib.Path("run.sqlite"),
    every_nth_frame=5,
    commit_every_nth_write=100,
)
```

The SQLite schema stores:

- `trajectory_data(frame, id, pos_x, pos_y, ori_x, ori_y)`
- `metadata(version, fps, bounds...)`
- `geometry(hash, wkt)`
- `frame_data(frame, geometry_hash)`

Read recordings:

```python
recording = jps.Recording("run.sqlite")
frame = recording.frame(0)
geometry = recording.geometry()
fps = recording.fps
num_frames = recording.num_frames
```

For non-SQLite outputs, subclass `jps.TrajectoryWriter` and implement `begin_writing`, `write_iteration_state`, and `every_nth_frame`.

