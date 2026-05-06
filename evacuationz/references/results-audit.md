# Results Audit Guide

Use this guide after a run completes or when reviewing someone else's Evacuationz output folder.

## Output File Roles

| Output | What it tells you | Audit questions |
|--------|-------------------|-----------------|
| `log.html` | Software version, files opened, defaults, warnings/errors, total agents, stop time | Did all expected files open? Were defaults used intentionally? Did total agents match the population plan? |
| `results.html` | Summary result view | Does the headline time match the log and evacuation output? |
| `evac.csv` or `~evac.csv` | Evacuation progression over time | When did the last agent reach safety? Is the curve plausible? |
| `nodes.csv` or `~nodes.csv` | Node occupancy over time | Where and when did congestion occur? Are safe nodes accumulating as expected? |
| `agents_*.csv` or `~agents_*.csv` | Agent tracks and optional attributes | Are route choices, EDM states, and delays behaving as intended? |
| `pre-evac.csv` | Assigned pre-evacuation times | Do samples match the declared distribution and units? |
| `smokeview.smv` and particle files | Visualization | Does geometry and movement visualization match the intended model? |
| Base file | Consolidated protected input | Is it preserved unmodified, or did hash checks fail? |

## First-Pass Acceptance Criteria

- The log reports the expected Evacuationz version or the version is documented.
- Every intended input file is opened.
- Total number of agents equals the population plan.
- Simulation stopped because evacuation completed or a planned maximum time was reached.
- No error or warning is ignored without explanation.
- Requested output files exist and are non-empty.
- Headline result is traceable to a specific output file and row/value.

## Log Review Pattern

Search for these terms:

| Term | Meaning |
|------|---------|
| `Opened` | Confirms which project, scenario, map, population, agent type, simulation, system, and output files were used |
| `default` | Identifies implicit assumptions that may need reporting |
| `Total number of agents` | Population consistency check |
| `stopped at` | Main completion or maximum-time indicator |
| `error`, `warning`, `missing`, `failed` | Potential acceptance blocker |

## CSV Review Pattern

For each CSV:

1. Confirm row count and header shape.
2. Confirm the time column is monotonic if present.
3. Confirm the last time is consistent with the log.
4. Confirm total evacuated agents equals expected population.
5. Inspect early rows for unintended pre-movement or immediate evacuation.
6. Inspect final rows for stranded agents or unresolved occupancy.

## Diagnostic Questions

| Symptom | Likely causes |
|---------|---------------|
| Final time is much longer than hand calculation | Start distance included, pre-evacuation not zero, door/stair effective width smaller, route choice different, congestion, output timestep |
| Final time is much shorter than expected | Start distance set to minimum, path length zero/default, pre-evacuation omitted, opening used instead of door, population missing |
| Agents choose unexpected exits | Behaviour type mismatch, specified safe node name mismatch, required route not marked, reassessment active |
| Door flow too high | Opening used instead of door, effective width not controlled, closer/leaves not set, specific flow changed |
| Stair movement unexpected | Tread/riser/width units wrong, stairs encoded as path/node incorrectly, handrail/floor height assumptions differ |
| EDM timing unexpected | Pre-evacuation also defined, attributes missing, alarm or smoke timing different, VM2 flag unsupported for chosen mode |
| Smokeview geometry wrong | yEd scaling mismatch, node dimensions in yEd override data fields, connections attached at unexpected positions |

## Evidence Labels

Use these labels in reports:

| Label | Meaning |
|-------|---------|
| `checked` | Verified directly against file output or script summary |
| `benchmark-pass` | Compared against a benchmark within tolerance |
| `sensitivity-supported` | Supported by a factor/seed sensitivity study |
| `assumed` | Input selected from project judgement, code guide, or literature but not independently verified here |
| `exploratory` | Used to examine possible behaviour, not as a calibrated prediction |
| `waived` | Check was intentionally skipped with a documented reason |

## Minimum Output Digest

Include this digest in every reproducible package:

| Field | Value |
|-------|-------|
| Project name |  |
| Evacuationz version |  |
| Scenario file |  |
| Run command or Runz/batch file |  |
| Random seed(s) |  |
| Total agents |  |
| Final evacuation/stop time |  |
| Output files generated |  |
| Benchmark checks |  |
| Warnings/errors |  |
| Reviewer notes |  |

