# Pathfinder Output Analysis

Pathfinder writes output files after simulation runs. Analyze files, not only visualization.

## Output Folder

After running a simulation, Pathfinder creates an output folder named after the saved `.pth` file. Multiple scenarios create separate scenario folders. Monte Carlo variations create variation folders inside scenario folders.

## Summary Report

The summary report is named like:

```text
filename_summary.txt
```

It contains simulation geometry, performance, statistics, and usage information for each room, stairway, and door. Useful quantities include completion time, travel/movement distance, trigger usage time, occupant target active usage time, and component usage.

The component table includes fields such as first in, last out, total use, and average flow for doors that served more than one occupant.

## Occupant History

Detailed occupant history is written only for occupants whose profile has detailed data output enabled. It can be written cumulatively or one file per occupant.

CSV columns documented by the online manual include:

| Column | Meaning |
| --- | --- |
| `t(s)` | output time |
| `id` | simulator-assigned occupant id |
| `name` | occupant name |
| `active` | seeking exit flag |
| `x(m)`, `y(m)`, `z(m)` | 3D position |
| `v(m/s)` | speed magnitude |
| `distance(m)` | total distance traveled |
| `location` | current room |
| `terrain type` | current terrain |
| `safe` | refuge room flag |
| `trigger` | trigger in use |
| `occupant_target` | target use |
| `last_goal_started` | last behavior action started flag |

JSON occupant history contains the same data nested by occupant ID and time step.

## Analysis Workflow

1. Locate output folder and identify scenarios/variations.
2. Validate required files exist.
3. Validate required CSV columns.
4. Compute metrics: completion time, active count, flow, distance, speed, room occupancy, region occupancy, target/trigger use.
5. Exclude or flag occupants who did not complete relevant actions.
6. Report output frequency and missing-data assumptions.

## Python Notes

Use the standard `csv` and `json` modules for portable scripts. Use pandas when available for larger analyses:

```python
import pandas as pd
hist = pd.read_csv("model occupants_detailed.csv")
```

Always handle column names with spaces and units exactly as written, such as `x(m)` and `v(m/s)`.
