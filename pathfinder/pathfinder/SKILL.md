---
name: pathfinder
description: "Pathfinder pedestrian movement and egress simulation skill for model planning, online documentation lookup, GUI workflow guidance, command-line runs with testsim.bat, scenarios, Monte Carlo variations, JavaScript simulator scripting API, output file validation, CSV/JSON postprocessing, occupant history analysis, summary reports, door and room histories, measurement regions, queues, targets, triggers, assisted evacuation, and research-grade egress study design."
license: MIT
---

# Pathfinder

Use this skill to guide Pathfinder pedestrian movement and egress simulation work. Pathfinder is primarily a GUI modeling application, with command-line simulation support, CSV/JSON outputs, Monte Carlo workflows, and an experimental JavaScript simulation scripting API. Python is most useful around Pathfinder: crawling docs, preparing batch manifests, launching command-line runs, validating outputs, and analyzing results.

## First Pass

Before giving instructions or writing code, establish:

1. Pathfinder version and documentation source, usually `https://www.thunderheadeng.com/docs/2026-1/pathfinder/`.
2. User goal: model setup, simulation run, scripting API, output analysis, Monte Carlo, troubleshooting, or research design.
3. Model status: existing `.pth`, exported simulator `.txt`, exported scenario files, or no model yet.
4. Simulation mode and assumptions: SFPE or Steering, behavior mode parameters, time limit, output frequency, and randomization posture.
5. Occupant setup: profiles, behaviors, starting rooms, movement groups, queues, targets, triggers, assisted evacuation, and tags.
6. Output contract: summary report, occupant history, room/door history, measurement regions, JSON, plots, or postprocessed tables.
7. Automation boundary: Python outside Pathfinder, JavaScript inside Pathfinder, or command-line `testsim.bat`.

If the user asks for "Python code for Pathfinder", clarify whether they need Python to run/analyze Pathfinder outputs or JavaScript code for Pathfinder's in-simulator scripting API.

## Triggers

Use this skill for requests like:

- `Use $pathfinder to build a Pathfinder egress study workflow.`
- `Create Python code to analyze Pathfinder occupant history CSV files.`
- `Write a Pathfinder custom script for door control by region count.`
- `Run Pathfinder models from the command line and validate the outputs.`

## Reference Routing

- Read `references/pathfinder-docs-map.md` for online documentation structure and source URLs.
- Read `references/pathfinder-modeling-workflows.md` for geometry, profiles, behaviors, occupants, queues, targets, and triggers.
- Read `references/pathfinder-simulation-batch.md` for GUI runs, `testsim.bat`, exported scenarios, Monte Carlo variations, and batch execution.
- Read `references/pathfinder-scripting-api.md` before writing JavaScript custom scripts.
- Read `references/pathfinder-output-analysis.md` for summary reports, occupant history, measurement outputs, and Python analysis.
- Read `references/pathfinder-pitfalls.md` when diagnosing modeling, scripting, command-line, or output problems.

## Process

### Phase 1: Ground The Workflow

Identify the model state, versioned docs, simulation mode, occupant logic, output files, and whether the requested automation belongs in Python or Pathfinder's JavaScript API.

### Phase 2: Build Or Analyze

For modeling tasks, give GUI-oriented steps and quality checks. For scripts, write JavaScript callbacks against `api.simctl.v1`, `api.geometry.v1`, `api.agents.v1`, `api.io.v1`, or `api.triggers.v1`. For Python, write docs crawlers, run manifests, batch launchers, output validators, or analysis scripts.

### Phase 3: Verify Evidence

Check that the model can run, output files exist, required columns are present, metrics match the research question, and claims are tied to Pathfinder outputs rather than only animation impressions.

## Core Workflow

1. Frame the study.
   - State the egress or movement question, population, layout scope, scenario alternatives, response metrics, and validity limits.
   - Identify whether Pathfinder is being used for design comparison, code compliance support, evacuation timing, wayfinding, queueing, or sensitivity analysis.

2. Build or audit the model.
   - Check imported geometry, rooms, doors, stairs, ramps, elevators, queues, targets, triggers, and measurement regions.
   - Verify occupant profiles, behaviors, movement groups, sources, initial positions, and tags.
   - Separate geometry alternatives into scenarios when geometry changes are being compared.

3. Configure simulation and outputs.
   - Set time limit, behavior mode, output frequency, detailed occupant data, JSON output needs, and Monte Carlo parameters.
   - Use scenarios and Monte Carlo variations deliberately; randomization seed is distinct from occupant seeds.
   - Decide whether the run is GUI-managed or command-line through `testsim.bat`.

4. Automate the right layer.
   - Use JavaScript custom scripts only for runtime simulation behavior and callbacks.
   - Use Python for batch manifests, command invocation, file discovery, validation, CSV/JSON parsing, and plots.
   - Use the docs crawler when exact online documentation pages or headings are needed.

5. Run and collect outputs.
   - For GUI runs, use Pathfinder's Run Simulation workflow.
   - For command line, call `testsim.bat "full_model_path"` or pass directories of `.pth` files.
   - For multiple scenarios or Monte Carlo variations, export scenarios and variations to separate files before command-line runs.

6. Analyze and report.
   - Parse summary reports, occupant history, door/room histories, measurement regions, and Monte Carlo result files as needed.
   - Report units, data output frequency, incomplete occupants, stuck occupants, missing files, and filters used.
   - Tie conclusions to output metrics such as completion time, distance, flow, occupancy, density, target use, trigger use, and occupant histories.

## Decision Table

| User goal | Pathfinder path |
| --- | --- |
| Learn where docs live | `crawl_pathfinder_docs.py` and `pathfinder-docs-map.md` |
| Plan a model | GUI workflow, modeling references, quality gates |
| Run one model | GUI run or `testsim.bat "model.pth"` |
| Run multiple files | manifest plus batch runner template |
| Run scenarios or Monte Carlo | export scenarios/variations, then run exported `.pth` files |
| Runtime door/trigger control | JavaScript custom script, `sim.onUpdate`, geometry/trigger APIs |
| Count agents in a region | JavaScript `agents.findAll(region).size()` or output measurement regions |
| Analyze trajectories | Python parse occupant history CSV/JSON |
| Analyze evacuation times | summary report, occupant summary/history, Monte Carlo results |
| Diagnose bad results | pitfalls reference, model audit, output validation |

## Coding Standards

- Do not write Python as if Pathfinder had a Vissim-style COM API.
- Use JavaScript for in-simulator callbacks and Python for external automation.
- When using custom scripts, declare `var sim = api.simctl.v1`, `var geom = api.geometry.v1`, `var agents = api.agents.v1`, `var io = api.io.v1`, and `var triggers = api.triggers.v1`.
- Keep custom script globals namespaced to avoid collisions across scripts.
- Close PrintStreams in `sim.onExit`.
- In Python, use `pathlib.Path`, `subprocess.run`, `csv`, `json`, and pandas only when available or explicitly allowed.
- Validate required columns before analyzing output files.
- Preserve one result directory per run, scenario, or variation.

## Templates

Adapt templates from `assets/templates/`:

- `pathfinder_batch_runner_template.py` for manifest-driven `testsim.bat` execution.
- `pathfinder_output_analysis_template.py` for summary and occupant-history analysis.
- `pathfinder_script_api_template.js` for in-simulator door/region/trigger examples.

## Scripts

- `scripts/crawl_pathfinder_docs.py` crawls versioned Pathfinder online docs and writes a compact JSON/CSV/Markdown index.
- `scripts/create_pathfinder_run_manifest.py` creates deterministic CSV manifests for command-line Pathfinder runs.
- `scripts/validate_pathfinder_outputs.py` checks output folders for required summary, occupant history, and requested files.

Exit codes:

| Code | Meaning |
| --- | --- |
| 0 | operation completed successfully |
| 1 | validation, crawl, filesystem, subprocess, or output failure |
| 2 | command-line usage error from `argparse` |

## Verification

- [ ] The docs version and source URLs are stated.
- [ ] Python-vs-JavaScript automation responsibility is explicit.
- [ ] Model assumptions, scenario factors, and simulation parameters are documented.
- [ ] Required output files and columns are checked before analysis.
- [ ] Batch runs preserve one output record per model/scenario/variation.
- [ ] Conclusions cite metrics from Pathfinder outputs, not only visual playback.

## Quality Gates

- Documentation gate: source pages are from the intended Pathfinder version.
- Modeling gate: geometry, occupant profiles, behaviors, queues, targets, triggers, and measurement regions match the study question.
- Simulation gate: behavior mode, time limit, output frequency, and Monte Carlo settings are explicit.
- Scripting gate: runtime scripts use the Pathfinder JavaScript API and avoid global name collisions.
- Batch gate: `testsim.bat` path, model paths, output directories, and exit codes are captured.
- Output gate: required files exist and required columns are present.
- Interpretation gate: incomplete or stuck occupants are identified before reporting evacuation timing.
- Reproducibility gate: model path, docs version, run manifest, randomization settings, and analysis code are retained.

## Anti-Patterns

| Avoid | Use instead |
| --- | --- |
| Claiming Pathfinder has Python COM automation like Vissim | separate Python external workflows from JavaScript custom scripts |
| Treating Monte Carlo seed as the same thing as occupant seeds | document both randomization concepts |
| Running multi-scenario models from command line without exporting variations | export scenarios and variations to separate files first |
| Drawing conclusions from 3D playback alone | parse summary, measurement, and occupant output files |
| Ignoring detailed output frequency | report time step/output interval with trajectory metrics |
| Leaving custom script streams open | close streams in `sim.onExit` |

## Extension Points

- Add deeper references for assisted evacuation, elevators, PyroSim/FDS coupling, and Results Viewer workflows.
- Add validators for room history, door history, measurement region, and Monte Carlo result schemas.
- Add optional pandas plotting utilities for flow, occupancy, completion time, and occupant trajectories.
- Add project-specific templates for station, stadium, school, hospital, and assisted evacuation studies.
