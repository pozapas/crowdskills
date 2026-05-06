# Pathfinder Modeling Workflows

Pathfinder modeling is usually GUI-centered. Give operational steps and validation checks rather than only code.

## Study Framing

Clarify:

| Item | Examples |
| --- | --- |
| Scenario | building evacuation, station circulation, queueing area, assisted evacuation |
| Population | occupant count, profiles, groups, starting rooms, mobility assumptions |
| Movement logic | SFPE, Steering, behaviors, queues, triggers, targets |
| Alternatives | geometry, exits, signage, door state, staffing, queue layout |
| Metrics | completion time, first in/out, flow, occupancy, density, distance, stuck occupants |
| Output | summary report, occupant history, door/room history, measurement regions |

## Model Audit Order

1. Geometry and navigation mesh.
2. Rooms, doors, stairs, ramps, elevators, and refuge areas.
3. Profiles and speed assumptions.
4. Behaviors and movement groups.
5. Occupants, sources, tags, and initial conditions.
6. Queues, targets, and triggers.
7. Measurement regions and output settings.
8. Scenarios, Monte Carlo, and run parameters.

## Geometry And Connectivity

Check that:

- Imported geometry is scaled correctly.
- Rooms and doors are recognized as navigable.
- Stairs, ramps, and elevators connect intended floors.
- Door widths and stair geometry match the study question.
- Obstacles do not create unintended bottlenecks.
- Scenario alternatives preserve all non-tested factors.

For geometry comparison, use scenarios rather than Monte Carlo. The docs state Monte Carlo variations cannot modify geometry or geometry-related parameters such as stair width, rise/run, or door width.

## Profiles And Behaviors

Profiles encode movement characteristics. Behaviors encode what occupants do. Keep them separate in explanations:

| Concept | Use |
| --- | --- |
| Profile | speed, size, movement capabilities, profile-level properties |
| Behavior | sequence of actions and goals |
| Movement group | coordinated occupant movement |
| Queue | waiting/service behavior |
| Target | reservation or waiting location |
| Trigger | dynamic influence on occupant actions |

## Output-First Modeling

Create measurement regions before running when local metrics are needed. Enable detailed occupant data when trajectory-level analysis is needed. Avoid adding detailed output by default to huge models without warning about file size.

## Validity Notes

Pathfinder is intended to supplement expert judgment. Do not present model output as a guaranteed prediction. State assumptions, calibration posture, sensitivity limits, and whether results were validated against observations or standards.
