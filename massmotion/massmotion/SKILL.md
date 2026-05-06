---
name: massmotion
description: "Oasys MassMotion pedestrian simulation skill for GUI model planning, Python SDK scripts, internal script objects, MassMotionConsole command-line runs, random seed batches, mmdb result databases, table and map queries, agent position CSV exports, generated simulation logs, output validation, and research-grade pedestrian movement analysis."
license: MIT
---

# MassMotion

Use this skill for Oasys MassMotion pedestrian movement simulation work. MassMotion supports GUI authoring and analysis, Python script objects inside MassMotion, a standalone Python SDK module such as `massmotion_11_0`, command-line automation through `MassMotionConsole.exe`, and simulation result databases stored as `.mmdb` SQLite files.

## First Pass

Before giving instructions or writing code, establish:

1. MassMotion version, installed paths, and whether the target is MassMotion 11.x, the SDK, or MassMotionConsole.
2. Software capability area: GUI modeling, SDK Python, internal script object, console automation, result analysis, or troubleshooting.
3. User goal: model setup, Python SDK authoring, internal script object, console batch, simulation control, query/export, mmdb analysis, or troubleshooting.
4. Automation boundary: GUI workflow, internal Python script object, standalone SDK Python script, or `MassMotionConsole.exe`.
5. Model state: `.mm` project, `.mmdb` result database, script object, exported `mmxml`, agent position CSV, query CSV, or no model yet.
6. Scenario inputs: projects, events/journeys, profiles, seeds, population scaling, threads, scripts, query names, and output folders.
7. Output contract: `.mmdb`, `.txt` log, table query CSVs, agent position CSV, maps, images, movies, or summary metrics.

If the user asks for "Python for MassMotion", clarify whether the script runs inside MassMotion, through the standalone SDK, or through MassMotionConsole's `--scriptfile`.

## Triggers

Use this skill for requests like:

- `Use $massmotion to automate a MassMotion simulation with Python.`
- `Write a MassMotion SDK script that opens a .mm project and runs DefaultRun.mmdb.`
- `Create a MassMotionConsole batch for multiple random seeds and query CSV exports.`
- `Validate MassMotion mmdb, log, and query CSV outputs for a batch study.`

## Reference Routing

- Read `references/massmotion-feature-map.md` for feature routing and automation boundaries.
- Read `references/massmotion-python-sdk.md` before writing standalone SDK scripts or internal script-object code.
- Read `references/massmotion-console-batch.md` before using `MassMotionConsole.exe`.
- Read `references/massmotion-modeling-workflows.md` for authoring, scene objects, journeys, events, and simulation setup.
- Read `references/massmotion-output-analysis.md` for `.mmdb`, logs, query CSVs, agent position exports, and maps.
- Read `references/massmotion-pitfalls.md` when diagnosing SDK imports, script execution, console runs, or results.

## Process

### Phase 1: Ground The Run Context

Identify the installed version, SDK module name, model files, result files, console path, script location, and whether the request belongs to GUI guidance, MassMotion script objects, standalone SDK Python, or console automation.

### Phase 2: Build Or Analyze

For GUI tasks, give workflow steps tied to scene authoring, simulation, and analysis. For Python tasks, use the SDK patterns: `Sdk.init()`, `Project.open()` or `Project.create()`, object access by name/id/type, `Simulation.create()`, `simulation.step()`, `SimulationRun.connect()`, table/graph/map queries, `Database.open()`, and `View` image capture. For console tasks, generate a manifest and command list with seeds, threads, scripts, simulations, and query exports.

### Phase 3: Verify Evidence

Check that scripts call `Sdk.fini()`, projects and SDK DLLs are discoverable, console return codes are captured, `.mmdb` files open as SQLite databases, logs exist, query CSVs have rows, random seeds are recorded, and output metrics are based on saved results rather than visual playback alone.

## Core Workflow

1. Frame the study.
   - State the pedestrian movement question, facility scope, population, operating scenario, output metrics, and limits.
   - Decide whether the workflow is exploratory GUI modeling, reproducible batch execution, live simulation control, or post-run analysis.

2. Prepare the model.
   - Check scene geometry, floors, portals, links, stairs, escalators, barriers, gates, servers, tallies, areas, profiles, journeys, events, and collections.
   - Keep imported reference geometry separate from MassMotion objects used in simulation.
   - Record project settings that affect randomness, threading, working path, and output generation.

3. Choose the automation layer.
   - Use internal script objects for project-local automation that benefits from MassMotion's undo/rollback behavior.
   - Use standalone SDK Python for repeatable external scripts, direct simulation stepping, query execution, database reads, and image capture.
   - Use MassMotionConsole for command-line batches, pre-simulation scripts, simulations, query CSV exports, seeds, population scaling, threads, and logs.

4. Run and collect evidence.
   - Preserve one output folder per project/scenario/seed.
   - Capture console command, return code, seed, `.mmdb`, log, query CSVs, and agent position exports.
   - Use `.mmdb` plus `SimulationRun`, `Database`, table queries, graph queries, or map queries for analysis.

5. Analyze and report.
   - Validate files before reading them.
   - Report the query names, filters, time range, sampling period, units, random seed, MassMotion version, and whether the run completed.
   - Treat stopped or failed simulations as incomplete unless the analysis intentionally covers partial results.

## Decision Table

| User goal | MassMotion path |
| --- | --- |
| Route a feature request | `massmotion-feature-map.md` |
| Create or modify project objects | SDK `Project`, `SimObject`, geometry, profiles, journeys |
| Run a simulation in Python | `Simulation.create(project, run_name, mmdb_path)` plus `step()` loop |
| Control agents during simulation | `AgentRequest`, agent tasks, `assume_control()`, `move_to()`, gate/server/tally methods |
| Run batches from command line | `MassMotionConsole.exe` manifest and batch runner |
| Export table query CSVs | console `--query`/`--queryall` or SDK `TableQuery.evaluate()` |
| Analyze raw trajectories | agent position CSV export or SDK `Database.open(mmdb)` frame data |
| Create maps/images | SDK `MapQuery`, `View.show_map()`, `View.capture_image()` |
| Diagnose run failures | console return codes, logs, issue output, SDK import/path checks |

## Coding Standards

- Do not write MassMotion code as if it were Vissim COM or Pathfinder JavaScript.
- For standalone SDK scripts, import the installed module such as `massmotion_11_0` and call `mm.Sdk.init()` before SDK operations and `mm.Sdk.fini()` in a `finally` block.
- Verify 64-bit Python and SDK DLL discovery before blaming user code.
- For MassMotion 11.8 and later, remember the internal interpreter is Python 3.12; standalone SDK expectations may differ. Check the installed module/version.
- Use project object names only after confirming `project.has_object(name)` or handling missing names.
- Do not mutate the original project after `Simulation.create()` and expect the already-created simulation copy to change.
- Use `Path` and absolute paths for `.mm`, `.mmdb`, scripts, and CSV outputs.
- Capture MassMotionConsole return codes and log paths in every batch result.
- Validate `.mmdb` as SQLite before running analysis queries.
- Keep one result row per project, seed, script, and query combination.

## Templates

Adapt templates from `assets/templates/`:

- `massmotion_sdk_simulation_template.py` for standalone SDK scripts that open projects, run simulations, and optionally adjust agents.
- `massmotion_script_object_template.py` for internal script-object patterns using `Project.get_current_project()`.
- `massmotion_console_batch_template.py` for manifest-driven `MassMotionConsole.exe` batches.
- `massmotion_query_analysis_template.py` for connecting `.mmdb` files and evaluating table-query metrics.

## Scripts

- `scripts/create_massmotion_console_manifest.py` writes deterministic command-line run manifests.
- `scripts/validate_massmotion_outputs.py` checks `.mmdb`, logs, CSV exports, and agent position columns.

Exit codes:

| Code | Meaning |
| --- | --- |
| 0 | operation completed successfully |
| 1 | validation, filesystem, subprocess, SDK, or output failure |
| 2 | command-line usage error from `argparse` |

## Verification

- [ ] The MassMotion version and installed capability path are identified.
- [ ] The automation layer is explicit: GUI, script object, standalone SDK, or console.
- [ ] SDK scripts call `Sdk.init()` and `Sdk.fini()` and use the correct module name.
- [ ] Console commands include `--project`, one of `--simulation`/`--scriptobject`/`--scriptfile`, seed/thread options when used, and query exports when required.
- [ ] `.mmdb`, log, and CSV outputs are validated before analysis.
- [ ] Random seeds, population scaling, threads, and query names are retained with results.
- [ ] Conclusions cite saved outputs and query metrics, not only visual playback.

## Quality Gates

- Version gate: identify MassMotion version, SDK module name, console path, and interpreter context.
- Model gate: scene objects, imported reference geometry, portals, profiles, journeys, events, gates, servers, areas, and tallies match the study question.
- SDK gate: 64-bit Python, SDK DLL path, module name, project path, and cleanup are handled.
- Simulation gate: seed, run name, output `.mmdb`, completion state, and log are captured.
- Console gate: return codes are interpreted and nonzero codes are investigated with the log.
- Analysis gate: query source run, filters, time range, sampling period, units, and CSV schema are documented.
- Reproducibility gate: project path, version, scripts, manifest, seeds, console command, and outputs are retained.

## Anti-Patterns

| Avoid | Use instead |
| --- | --- |
| Assuming MassMotion exposes COM automation | use MassMotion Python SDK or MassMotionConsole |
| Writing SDK code without `Sdk.init()`/`Sdk.fini()` | wrap SDK lifecycle in `try/finally` |
| Expecting project edits after `Simulation.create()` to affect the active simulation | mutate before create or use `Simulation` control methods |
| Ignoring 64-bit Python and DLL/PATH requirements | verify module import and SDK install path first |
| Running many seeds into one output folder | one output directory and result row per run |
| Treating a stopped simulation as complete | inspect logs, return code, and run details |
| Analyzing CSVs without checking headers | validate required columns and row counts |

## Extension Points

- Add validators for known MassMotion table-query CSV schemas.
- Add project-specific SDK templates for stations, stadiums, airports, schools, and evacuation studies.
- Add mmdb schema discovery utilities once representative databases are available.
- Add optional pandas plotting utilities for density, flow, LOS, trip time, and agent paths.
- Add project-specific examples from approved reusable project templates.
