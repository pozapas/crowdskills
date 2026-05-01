# Research Workflows

Use these patterns to construct PhD-level simulation studies rather than one-off scripts.

## Single Scenario Pattern

1. Define question and metric.
2. Define geometry and named regions.
3. Add stages and route graph.
4. Generate initial positions with seeds.
5. Add agents with explicit model parameters.
6. Run with max-iteration guard.
7. Close writer.
8. Validate trajectory output, preferably with `scripts/validate_sqlite_recording.py`.
9. Analyze with JuPedSim `Recording`, PedPy, or custom metrics.
10. Save a small manifest of assumptions.

## Bottleneck Capacity Study

Use when the user asks for flow, capacity, density, clogging, or evacuation through a constriction.

Key design points:

- Geometry should isolate the bottleneck width and approach region.
- Spawn area should be upstream and away from the bottleneck.
- Desired-speed distribution should be specified, not silently uniform.
- Postprocess with PedPy: N-t curve, flow, classic/Voronoi density, speed near the bottleneck.
- Compare multiple widths or crowd sizes with matched seeds.

## Route-Choice Study

Use when the question is about signage, route assignment, detours, exit choice, or crowd-management policies.

Core approach:

- Create candidate routes as journeys.
- Use fixed transitions for baseline routes.
- Use round-robin for controlled splitting.
- Use least-targeted for adaptive load balancing.
- Compare evacuation time, local density, congestion duration, and route utilization.

Record for each run:

- number assigned to each route
- transition policy
- exit usage
- completion time distribution

## Queue And Waiting Study

Use queues when order matters and release is controlled with `pop(count)`.
Use waiting sets when agents should occupy waiting positions until a stage is activated or deactivated.

Typical interventions:

- release every N seconds
- release when downstream density falls below threshold
- deactivate waiting set after an external event
- switch some agents to alternate journeys

## Lane Formation Study

For bidirectional flow:

- Use opposite exits and two agent groups.
- Keep initial group placement symmetric when possible.
- Track each group by saved agent IDs.
- Run multiple ratios and seeds.
- Postprocess speed and density by group and location.

Avoid judging lane formation only from animation. Compute lane order, lateral occupancy, group mixing, or trajectory crossings where possible.

## Model Comparison Study

Use identical scenario construction across model families:

```python
models = {
    "csm": (jps.CollisionFreeSpeedModel(), jps.CollisionFreeSpeedModelAgentParameters),
    "csm_v2": (jps.CollisionFreeSpeedModelV2(), jps.CollisionFreeSpeedModelV2AgentParameters),
    "avm": (jps.AnticipationVelocityModel(rng_seed=123), jps.AnticipationVelocityModelAgentParameters),
    "gcfm": (jps.GeneralizedCentrifugalForceModel(), jps.GeneralizedCentrifugalForceModelAgentParameters),
    "sfm": (jps.SocialForceModel(), jps.SocialForceModelAgentParameters),
}
```

For each model, match:

- geometry
- initial positions
- desired speeds where semantically comparable
- exits and journeys
- `dt`
- output interval
- maximum iterations

Then compare completion time, failed/stuck agents, trajectories, local density, and model-specific artifacts.

## Sensitivity And Calibration

For parameter sweeps:

- Sweep one conceptual factor at a time when possible.
- Use factorial designs only when interactions are central to the question.
- Repeat seeds for stochastic placement.
- Store one row per run in a manifest with parameters and output paths. Use `scripts/create_experiment_matrix.py` when a Cartesian-product run plan is appropriate.
- Separate simulation generation from metric calculation so failed runs can be diagnosed.

Useful sweep axes:

- bottleneck width
- desired-speed mean and variance
- agent radius
- density or number of agents
- model family
- CSM repulsion strength/range
- AVM anticipation and reaction time
- queue release policy

## Postprocessing Bridge To PedPy

JuPedSim SQLite trajectories can be inspected with `jps.Recording`. For pedestrian dynamics metrics, convert/read into PedPy-style trajectory data when available in the user's environment.

Common metrics:

- evacuation time: last non-empty frame or `simulation.elapsed_time()`
- N-t curve at a measurement line
- flow through bottleneck
- density near bottleneck
- mean speed and speed distribution
- time spent in queue/waiting set
- route usage by journey/group
