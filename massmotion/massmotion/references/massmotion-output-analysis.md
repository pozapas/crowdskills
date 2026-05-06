# MassMotion Output Analysis

MassMotion outputs are centered on `.mmdb` result databases, logs, query outputs, maps, images, and optional agent position exports.

## Generated Simulation Files

| Output | Meaning |
| --- | --- |
| `.mmdb` | SQLite database containing data required for playback and analysis of one simulation run |
| `.txt` log | diagnostic information from project initialization and execution |
| debug folder | optional obstacle maps, approach maps, route-cost CSVs, and diagnostic artifacts |
| query CSV | exported table-query results from console or GUI |
| agent position CSV | frame, agent id, position, and optional clock time, speed, heading, move state, animation time, floor |

## Agent Position Export

MassMotion agent position exports commonly use this core column order:

```text
Frame Number, Agent ID, X Position, Y Position, Z Position
```

Optional columns can include clock time, speed, heading, move state, animation time, and floor. If a project origin is set, exported positions use world coordinates instead of project coordinates.

## SDK Analysis Paths

| Need | Path |
| --- | --- |
| run-derived project object | `SimulationRun` |
| existing database | `SimulationRun.connect(mmdb_path)` |
| raw frame data | `Database.open(mmdb_path)` |
| per-agent table | `AgentSummaryTableQuery` |
| trip timing | `AgentTripTimeTableQuery` |
| transition use | `AgentTransitionTableQuery` |
| server metrics | `ServerSummaryTableQuery` |
| density/path maps | map query plus `View.show_map()` |

## Validation Before Analysis

- `.mmdb` exists and opens through SQLite or SDK.
- Log exists and does not contain obvious fatal errors.
- Query CSVs have headers and at least one data row.
- Agent position CSV contains frame, agent id, and XYZ position columns.
- Seed, MassMotion version, run name, and query names are known.
- Time range and sampling period are documented.

## Reporting Rules

| Report item | Include |
| --- | --- |
| run provenance | project file, MassMotion version, seed, script, command |
| output provenance | `.mmdb`, log, query object, CSV path |
| metrics | units, filters, time ranges, sampling |
| incomplete runs | console return code, stopped simulation status, log finding |
| spatial outputs | map type, display objects, resolution, legend/LOS standard |
| raw trajectories | coordinate system, sampling period, speed caveat |

## Common Metrics

- total agents generated
- agents completed or still active
- min/max/average time in simulation
- trip time by journey, transition, or OD pair
- server wait/service measures
- flow counts through transitions
- average/max density by area or map
- LOS exposure or time above density
- path usage and accessibility changes
