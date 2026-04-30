# JuPedSim Pitfalls

## Conceptual Pitfalls

- Do not treat a visually plausible animation as validation.
- Do not compare models after changing geometry, initial positions, or stop conditions.
- Do not tune parameters until the route graph and output metrics are stable.
- Do not interpret a model parameter as a physical quantity without checking the model definition.

## Geometry Pitfalls

- Obstacles may accidentally split the walkable area.
- Exit polygons close to boundaries need enough space for agents to enter.
- Wide exits can produce center-target artifacts.
- WKT/DXF-derived geometry can contain tiny artifacts; simplify or validate before simulation.
- Stages added before a geometry switch must remain valid after the switch.

## Agent Placement Pitfalls

- `distance_to_agents` is center-to-center spacing; choose it in relation to agent radius.
- `distance_to_polygon` must leave enough clearance from walls and holes.
- High density plus large radius can make placement impossible.
- Reusing one parameter object is fine because JuPedSim copies parameters on `add_agent`, but mutate it deliberately and readably.

## Run Loop Pitfalls

- Always include a maximum iteration guard in exploratory scripts.
- Call writer `close()` at the end.
- Handle `KeyboardInterrupt` by closing the writer before exit.
- Direct steering does not remove agents automatically.
- `SqliteTrajectoryWriter` only writes on simulation iteration; an output path alone does not create a complete file.

## Analysis Pitfalls

- SQLite `fps` depends on `dt` and `every_nth_frame`.
- If writer interval is too sparse, speed/flow estimates can suffer.
- A lower evacuation time can be caused by unrealistic collisions or route artifacts.
- Compare distributions, not only means, when route choice or queues are involved.
- Store failed runs too; they often reveal invalid parameter regions.

