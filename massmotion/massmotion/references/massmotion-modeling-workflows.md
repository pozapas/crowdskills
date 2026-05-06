# MassMotion Modeling Workflows

MassMotion projects usually iterate through authoring, simulation, and analysis. Use this reference for GUI/model planning questions and to decide what should be scripted.

## Authoring

Authoring creates the simulation scene and the events that generate or control agents.

| Topic | Checks |
| --- | --- |
| imported geometry | reference geometry is not directly simulated |
| MassMotion objects | floors, barriers, links, stairs, escalators, portals, gates, servers, paths |
| generated objects | converted from IFC, generic geometry, drawing lines, or drawing regions |
| component editing | object mode versus component mode is clear |
| project origin | affects exported world coordinates |
| profiles | agent physical and behavioral properties |
| journeys/events | population count, arrivals, origins, destinations, start times |
| collections | grouping, visibility, filters, query targeting |
| tallies/tokens | operational state and scripted control |

## Scene Construction

Imported IFC, 3D geometry, 2D drawings, and images are sources for generating MassMotion objects. The model should not rely on imported reference geometry alone for simulation; generate the appropriate MassMotion object types and audit connectivity.

## Simulation Setup

| Setting | Why it matters |
| --- | --- |
| simulation type | console is fastest, debug viewer is for inspection |
| run name | links project object to result database |
| `.mmdb` path | saved result evidence |
| random seed | same seed and unchanged project should reproduce results |
| threads | performance and repeatability context |
| multiple runs | sensitivity to random variation |
| population scaling | scenario factor and audit field |
| dump/debug options | obstacle maps, approach maps, route-cost CSVs |

## Analysis Setup

Plan analysis before running:

- table queries for agent, server, transition, token, trip, and OD metrics
- graph queries for time-series outputs
- map queries for density, path, proximity, time, and accessibility outputs
- agent position table export when raw trajectories are needed outside SDK
- bookmarks/views for consistent images or viewer deliverables

## Modeling Quality Checklist

- [ ] Imported geometry has been converted to MassMotion objects where needed.
- [ ] Floors, links, stairs, escalators, gates, and portals connect as intended.
- [ ] Journeys have profiles, origins, destinations, arrival timing, and population counts.
- [ ] Servers, tallies, tokens, and events are initialized before the run.
- [ ] Random seed, thread count, run name, and output database are recorded.
- [ ] Query objects exist before console `--query` or `--queryall` export.
- [ ] Output paths are unique for each scenario and seed.
