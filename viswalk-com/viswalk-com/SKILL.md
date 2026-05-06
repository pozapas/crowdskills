---
name: viswalk-com
description: "PTV Viswalk/Vissim COM automation skill for Python. Use when users need code or guidance for pywin32 control of Vissim/Viswalk, CHM COM help extraction, COM object hierarchy, AttValue/SetAttValue patterns, pedestrian areas, ramps, obstacles, pedestrian inputs, pedestrian types/classes/compositions, static or partial pedestrian routes, manual pedestrian insertion, area/travel-time/network-performance measurements, batch simulation runs, seed sweeps, result extraction, and debugging COM automation scripts."
license: MIT
---

# Viswalk-COM

Use this skill to write reliable Python automation for PTV Viswalk pedestrian simulation through the PTV Vissim COM interface. Treat COM scripts as controlled experiments: network state, units, random seeds, input volumes, routing, simulation period, output folders, and evaluation attributes must be explicit before results are trusted.

## First Pass

Before writing code, establish these facts:

1. Vissim/Viswalk version and whether the COM server is registered on the current Windows machine.
2. Automation target: load an existing `.inpx`, create network objects, alter demand/routing, run simulations, export results, or inspect the COM manual.
3. Python environment: `pywin32` availability, intended interpreter, and whether the user wants `EnsureDispatch` or plain `Dispatch`.
4. Network context: pedestrian areas, ramps/stairs, obstacles, levels, pedestrian classes/types/compositions, inputs, routes, and measurements already present.
5. Experimental contract: seeds, simulation period, warm-up, input time intervals, result folder, output files, and metrics.
6. Safety boundary: whether the script may save the network, overwrite results, close Vissim, or create new network objects.

If the user asks for code without a network file, provide a template with clearly marked object keys and assumptions rather than pretending the keys are known.

## Triggers

Use this skill for requests like:

- `Use $viswalk-com to write Python COM code for Viswalk pedestrian inputs and routes.`
- `Index the Vissim COM CHM and find pedestrian area methods.`
- `Automate a Viswalk seed sweep with pywin32 and export measurements.`
- `Debug my Vissim COM Python script for pedestrian routes.`

## Reference Routing

- Read `references/viswalk-com-chm-workflow.md` when the user mentions `Vissim 2025 - COM.chm`, missing COM docs, or API discovery.
- Read `references/viswalk-com-api-map.md` for the COM hierarchy, core objects, method names, and container/collection rules.
- Read `references/viswalk-com-python-patterns.md` before writing Python COM code.
- Read `references/viswalk-com-pedestrian-network.md` when creating or editing pedestrian areas, inputs, compositions, or live pedestrians.
- Read `references/viswalk-com-routing-evaluation.md` when creating pedestrian routes, route decisions, area measurements, travel time measurements, records, or result extraction.
- Read `references/viswalk-com-experiment-workflows.md` for seed sweeps, batch runs, paired comparisons, and reproducibility.
- Read `references/viswalk-com-pitfalls.md` when debugging COM failures, missing attributes, read-only attributes, wrong keys, bad WKT, units, or simulation-time edit errors.
- Read `references/viswalk-com-scripted-utilities.md` before using bundled scripts.

## Process

### Phase 1: Ground The API

Identify the Vissim version, Python environment, network file, object keys, and the exact COM object/method/attribute names. When the API is uncertain, extract or query the CHM before writing code.

### Phase 2: Build The Automation

Write Python in small functions for connection, network loading, object inspection, mutation, simulation, extraction, and cleanup. Keep assumptions visible in constants, arguments, manifests, or output metadata.

### Phase 3: Verify And Report

Run static validation where possible, check generated manifests or CHM indexes, explain object keys and attributes used, and describe any steps that require a local Vissim license/runtime.

## Core Workflow

1. Connect and load safely.
   - Use `win32com.client.gencache.EnsureDispatch("Vissim.Vissim")` for generated wrappers when available.
   - Load the `.inpx` and optional `.layx` with explicit paths.
   - Set result folders before running; never overwrite outputs silently.
   - Suspend GUI updates for large edits and resume them in `finally`.

2. Inspect the network before mutating it.
   - Use `ItemByKey`, `GetAll`, `GetMultiAttValues`, and `AttValue` to verify areas, inputs, classes, routes, and measurements.
   - Distinguish containers from collections. Add/remove through containers; collections often contain only references.
   - Confirm units and coordinate assumptions. Vissim coordinates are in meters, while speed attributes follow the current speed unit.

3. Build or alter pedestrian objects deliberately.
   - For new walkable zones, use WKT polygons through `Vissim.Net.Areas.AddArea(key, wkt_polygon)`.
   - Define or reuse pedestrian types, classes, walking behaviors, area behavior types, and pedestrian compositions before configuring inputs.
   - Use `PedestrianInputs.AddPedestrianInput(key, area)` for demand and `SetAttValue("Volume(i)", value)` for interval volume.
   - For live insertion, use `Pedestrians.AddPedestrianOnArea(...)` or `AddPedestrianOnAreaAtCoordinate(...)` only when the simulation state and area capacity make sense.

4. Configure routing and evaluation.
   - Static routing starts with `PedestrianRoutingDecisionsStatic.AddPedestrianRoutingDecisionStatic(key, area)`.
   - Add static route destinations with `decision.PedRoutSta.AddPedestrianRouteStaticOnArea(...)` or the ramp variant.
   - Add intermediate route locations through `route.PedRoutLoc.AddPedestrianRouteLocationOnArea(...)`.
   - Use partial routes for route-choice or path-choice studies where downstream choices matter.
   - Create travel-time and area measurements before the run, then read result attributes after each run.

5. Run with reproducibility controls.
   - Set `RandSeed`, `SimPeriod`, `SimBreakAt`, `SimRes`, `UseMaxSimSpeed`, and result folder explicitly.
   - Prefer paired comparisons: same network, same seeds, same run length, same measurement definitions.
   - Use `RunSingleStep` for controlled interventions and `RunContinuous` for ordinary batch runs.
   - Stop or close Vissim only if the user allowed it.

6. Validate and explain.
   - Run `scripts/validate_viswalk_com_script.py` for static checks before executing Vissim automation.
   - Explain which COM attributes are assumed from the local network and which came from the manual.
   - Report units, subattribute dimensions, time intervals, seeds, and output paths.

## Decision Table

| User goal | Viswalk-COM path |
| --- | --- |
| Query the CHM manual | Use `scripts/index_com_chm.py`, then inspect matching HTML topics |
| Load and run an existing network | Use the automation template, set seed/period/results, run, read metrics |
| Change pedestrian demand | Locate `PedestrianInputs`, set `Volume(i)` and `Cont(i)` where needed |
| Create areas or obstacles | Use WKT `POLYGON((...))`, verify closed rings and level assumptions |
| Create static routes | Add routing decision on an origin area, add route destinations and route locations |
| Create partial route choices | Add partial routing decision, candidate partial routes, and choice-area logic |
| Insert pedestrians during a run | Use `Pedestrians.AddPedestrianOnAreaAtCoordinate` with explicit relative coordinates and speed |
| Batch experiments | Generate a manifest, loop rows, reload network for each run, export one row per seed/factor |
| Extract measurements | Use area/travel-time/network-performance attributes after the run; document subattribute syntax |
| Debug COM errors | Check ProgID registration, object keys, editability, simulation state, unit system, and CHM topic |

## Coding Standards

- Use `pathlib.Path` for user-controlled paths, but pass strings to COM calls.
- Keep connection, loading, network edits, simulation run, result extraction, and cleanup in separate functions.
- Use `AttValue("Attr")` to read and `SetAttValue("Attr", value)` to write.
- Use English short names from Vissim list headers or COM Help attribute tables.
- Never assume `GetMultiAttValues` first-column values are object IDs; they are consecutive row numbers.
- Prefer object references for add methods when the manual expects an interface such as `IArea`.
- Use key `0` only when auto-numbering is acceptable and store the returned object immediately.
- Mark attributes that are read-only during simulation and set them before `RunContinuous`.
- Convert COM tuples to Python lists before mutation.
- Catch `pywintypes.com_error` and include the object path, attribute, and attempted value in the message.

## Templates

Adapt templates from `assets/templates/`:

- `viswalk_com_automation_template.py` for one network, one run or a small controlled edit.
- `viswalk_com_batch_template.py` for manifest-driven seed and demand sweeps.

## Scripts

- `scripts/index_com_chm.py` decompiles a `.chm` with Windows `hh.exe` and creates a searchable topic index.
- `scripts/create_viswalk_run_matrix.py` creates deterministic CSV manifests for seed, demand, speed-factor, and route-factor sweeps.
- `scripts/validate_viswalk_com_script.py` performs static checks on Python COM scripts before they are run against Vissim.

Exit codes:

| Code | Meaning |
| --- | --- |
| 0 | operation completed successfully |
| 1 | validation, extraction, indexing, filesystem, or script-quality failure |
| 2 | command-line usage error from `argparse` |

Use scripts as consistency aids. They cannot prove that a local `.inpx` has the expected objects or that Vissim's license allows every COM operation.

## Verification

- [ ] The COM object, method, or attribute names come from the CHM, Vissim list headers, installed examples, or this skill's references.
- [ ] Python scripts separate load, mutate, run, extract, and cleanup steps.
- [ ] Object keys, seeds, simulation period, result folder, and output files are explicit.
- [ ] Geometry and routing assumptions are documented before the run.
- [ ] `scripts/validate_viswalk_com_script.py` has been run for generated Python automation when files are available.
- [ ] CHM indexing has been tested when the user asks for manual-derived API discovery.

## Quality Gates

- Environment gate: Windows, Vissim/Viswalk installed, COM server registered, and `pywin32` available.
- Manual gate: when exact method names are uncertain, the CHM has been extracted or indexed rather than guessed.
- Network gate: all object keys referenced in code are listed or discovered before mutation.
- Geometry gate: WKT polygons are closed, valid, in meters, and assigned to the intended level.
- Demand gate: pedestrian compositions, desired-speed distributions, input volumes, and interval continuity are explicit.
- Routing gate: route decisions, destinations, intermediate route locations, and route class filters match the scenario.
- Runtime gate: seed, simulation period, resolution, breakpoints, and result folder are explicit.
- Evaluation gate: measurement definitions exist before the run and result attributes are read with the correct subattributes.
- Reproducibility gate: manifest, network path, script version, Vissim version, seeds, factors, and outputs are recorded.

## Anti-Patterns

| Avoid | Use instead |
| --- | --- |
| Guessing attribute names from prose labels | query CHM attributes or Vissim list short names |
| Mutating a network before inspecting object keys | read `No`, `Name`, and related objects first |
| Saving over the user's `.inpx` during automation | write derived files or ask before saving |
| Reusing one mutated network across a parameter sweep | reload the base network per run unless reset is proven |
| Treating animation as validation | read measurement attributes, records, or exported trajectories |
| Copying the full decompiled CHM into the skill | keep compact references and use `index_com_chm.py` locally |

## Extension Points

- Add references for elevators, stairs, public transport waiting areas, and evacuation-specific workflows as those use cases appear.
- Extend `create_viswalk_run_matrix.py` with project-specific factors such as route split, obstacle layout, area behavior type, and walking behavior.
- Add runtime validators that inspect a live `.inpx` for required object keys when Vissim is available.
- Add postprocessing bridges to PedPy for exported pedestrian records and trajectory files.
