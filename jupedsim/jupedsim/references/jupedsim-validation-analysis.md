# Validation And Analysis

Use this checklist before calling a JuPedSim result trustworthy.

## Before Running

- Confirm the geometry is one connected walkable area after union and holes.
- Check start positions, stages, and exit centers are inside the geometry.
- Check start positions are not too close to walls or other agents.
- Use `RoutingEngine.is_routable(...)` for start and target points in complex geometry.
- Record seeds for stochastic placement and model RNGs.
- State `dt` and trajectory writer interval.
- Use explicit `max_iterations` unless the scenario is guaranteed to empty.

## During Running

Prefer this loop shape:

```python
max_iterations = 10000
while simulation.agent_count() > 0 and simulation.iteration_count() < max_iterations:
    simulation.iterate()
```

For intervention experiments, keep policies auditable:

```python
if simulation.iteration_count() == release_iteration:
    queue.pop(5)
```

For density-triggered or location-triggered policies, save the trigger condition and threshold.

## After Running

Check:

- final `agent_count()`
- `iteration_count()` and `elapsed_time()`
- `removed_agents()` behavior if agents should exit
- SQLite file exists and has nonzero frames
- writer was closed
- no agents got stuck near wide exit centers, obstacle corners, or unreachable waypoints

## SQLite Recording Checks

```python
recording = jps.Recording("run.sqlite")
print(recording.num_frames, recording.fps, recording.bounds())
first = recording.frame(0)
last = recording.frame(recording.num_frames - 1)
```

For direct SQL checks:

```sql
SELECT count(*) FROM frame_data;
SELECT max(frame), count(DISTINCT id) FROM trajectory_data;
SELECT key, value FROM metadata;
```

## Common Failure Modes

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `add_agent` fails | Agent too close to wall/agent or invalid parameter | Increase spacing, reduce radius, move spawn area, inspect error |
| Agents never exit | Exit center unreachable or exit too wide/poorly placed | Use smaller/multiple exits, add waypoint before exit |
| Simulation never ends | Direct steering has no removal or agents stuck | Add max iterations, remove manually, inspect route |
| Placement fails | Requested density conflicts with constraints | Reduce count/density or spacing constraints |
| Strange routing around holes | Geometry triangulation/shortest path issue | Use intermediate waypoints and routability checks |
| Model comparison unfair | Different seeds, positions, dt, or output interval | Freeze scenario construction and vary only model |

## Reproducibility Manifest

For every serious run, write a manifest row containing:

- scenario name
- geometry label or WKT path
- model name
- model parameters
- agent parameter summary
- distribution method and seed
- number of agents
- `dt`
- writer interval
- max iterations
- output file
- completion status
- final agent count
- elapsed time

## Reporting Standards

A strong result section states:

- what model was used and why
- what geometry and route graph were used
- how agents were distributed
- which parameter values were default and which were changed
- what metrics were computed
- what limitations remain

Avoid phrases like "the simulation proves." Prefer "under this geometry, model, and parameterization, the simulation suggests."

