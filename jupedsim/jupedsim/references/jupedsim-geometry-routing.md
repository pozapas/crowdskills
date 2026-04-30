# Geometry And Routing

Geometry and routing failures are the fastest way to invalidate a JuPedSim study. Build them as first-class experimental objects.

## Walkable Area

JuPedSim works on a continuous walkable area. Agents can move inside it and cannot cross its boundaries.

Accepted inputs include:

- Shapely `Polygon`
- Shapely `GeometryCollection` containing polygons
- Shapely `MultiPolygon` that unions to a single walkable polygon
- WKT strings
- coordinate lists with optional `excluded_areas`

Example:

```python
from shapely import Polygon

walkable_area = Polygon([(0, 0), (20, 0), (20, 10), (0, 10)])
```

Use holes for internal obstacles:

```python
walkable_area = Polygon(
    [(0, 0), (20, 0), (20, 20), (0, 20)],
    holes=[
        [(4, 4), (6, 4), (6, 6), (4, 6)],
    ],
)
```

Or subtract obstacles:

```python
walkable_area = room.difference(obstacle)
```

Do not create obstacles that split the walkable area unless the goal is to demonstrate disconnected routing.

## Routability Checks

Use `RoutingEngine` before large runs:

```python
engine = jps.RoutingEngine(walkable_area)
assert engine.is_routable(start_position)
assert engine.is_routable(exit_polygon.centroid.coords[0])
path = engine.compute_waypoints(start_position, exit_polygon.centroid.coords[0])
```

This is especially useful for narrow passages, holes, imported WKT/DXF-derived geometry, and exits placed near boundaries.

## Stage Types

### Waypoint

Represents an intermediate target reached within a distance threshold.

```python
waypoint_id = simulation.add_waypoint_stage((5.0, 5.0), 0.75)
```

### Exit

Represents a polygonal area that removes agents at the next iteration after arrival.

```python
exit_id = simulation.add_exit_stage([(19, 4), (20, 4), (20, 6), (19, 6)])
```

Avoid very wide exits when the center target could create unnatural behavior. Use multiple exits when the layout warrants it.

### Queue

Agents wait in ordered positions and leave when notified.

```python
queue_id = simulation.add_queue_stage([(0, 0), (0, 1), (0, 2)])
queue = simulation.get_stage(queue_id)
queue.pop(1)
```

If more agents target a queue than positions exist, additional agents wait at the last position.

### Waiting Set

Agents fill waiting positions in order. The stage can be active or inactive.

```python
waiting_id = simulation.add_waiting_set_stage([(10, 2), (10, 3), (10, 4)])
waiting = simulation.get_stage(waiting_id)
waiting.state = jps.WaitingSetState.INACTIVE
```

If inactive, the first waiting position acts like a waypoint.

### Direct Steering

Use when the tactical route graph should be bypassed and targets are controlled at runtime.

```python
direct_stage = simulation.add_direct_steering_stage()
journey = jps.JourneyDescription([direct_stage])
journey_id = simulation.add_journey(journey)
agent = simulation.agent(agent_id)
agent.target = (12.0, 8.0)
```

A direct steering stage must be the only stage in its journey. Direct steering does not remove agents automatically.

## Journey Graphs

Journeys are directed graphs from stage to stage.

```python
journey = jps.JourneyDescription([entry_wp, queue_id, exit_id])
journey.set_transition_for_stage(
    entry_wp,
    jps.Transition.create_fixed_transition(queue_id),
)
journey.set_transition_for_stage(
    queue_id,
    jps.Transition.create_fixed_transition(exit_id),
)
journey_id = simulation.add_journey(journey)
```

Use:

- fixed transitions for deterministic routes
- round-robin transitions for controlled route splitting
- least-targeted transitions for adaptive load balancing

## Routing Design Checks

- Stages must be inside the walkable area.
- Exit stages should usually be terminal.
- Each non-terminal stage needs a transition.
- Direct steering journey should contain only the direct steering stage.
- Queue and waiting-set activation logic should be tied to iteration count, local agent count, or external policy.
- For experiments, store the route graph in a comment, manifest, or table.

