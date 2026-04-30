---
name: jupedsim
description: "Advanced JuPedSim pedestrian dynamics simulation skill for designing, implementing, validating, and analyzing microscopic evacuation and crowd movement experiments. Use when users need JuPedSim code or research guidance for geometry, routing, journeys, stages, exits, queues, waiting sets, direct steering, Collision Free Speed, Anticipation Velocity, Generalized Centrifugal Force, Social Force, agent distributions, SQLite trajectory output, custom serializers, model comparison, calibration, sensitivity analysis, bottlenecks, lane formation, route-choice experiments, or PhD-level simulation study design."
---

# JuPedSim

Use this skill to build scientifically defensible JuPedSim simulations. Treat JuPedSim as an experiment design environment: geometry, model family, route graph, agent population, numerical settings, serialization, and postprocessing all shape the conclusion.

## Source Policy

Do not copy JuPedSim manuals, notebooks, examples, or package source into generated repo content. The local source used to create this skill lives outside the GitHub-bound skill folders under `Manuals/JuPedSim/`; treat it as source material, not distributable content.

## Research Framing

Start every JuPedSim task by pinning down:

1. Scientific question: evacuation time, capacity, density wave, route-choice policy, lane formation, queue behavior, local interaction model, or software integration.
2. Scenario scale: toy validation, controlled experiment replica, operational layout, or parameter sweep.
3. Geometry: walkable area, obstacles, exits, gates, bottlenecks, stage positions, and whether route targets are routable.
4. Model family: speed-based, anticipation-based, or force-based; choose the simplest model that can express the phenomenon.
5. Population: number of agents, initial distribution, desired-speed distribution, radius/body assumptions, and group assignment.
6. Output contract: SQLite trajectory, custom writer, plots, PedPy metrics, reproducibility manifest, or comparative report.

If the user asks for "a simulation" without these details, choose conservative defaults and mark them clearly in code comments or the report.

## Reference Routing

- Read `references/jupedsim-api-map.md` for callable classes, functions, and parameter surfaces.
- Read `references/jupedsim-model-selection.md` before choosing or comparing microscopic models.
- Read `references/jupedsim-geometry-routing.md` when building geometry, journeys, stages, transitions, queues, or direct steering.
- Read `references/jupedsim-research-workflows.md` for complete experiment patterns and PhD-level study design.
- Read `references/jupedsim-validation-analysis.md` before finalizing outputs, interpreting results, or writing postprocessing.

## Core Workflow

1. Build geometry first.
   - Prefer Shapely `Polygon`, `GeometryCollection`, WKT, or coordinate lists.
   - Ensure the union forms one simple walkable polygon with holes for obstacles.
   - Do not place stages, exits, or initial agents outside the walkable area.

2. Select a model deliberately.
   - `CollisionFreeSpeedModel` for efficient baseline simulations.
   - `CollisionFreeSpeedModelV2` when repulsion parameters should vary by agent.
   - `AnticipationVelocityModel` for anticipatory collision avoidance and wall gliding.
   - `GeneralizedCentrifugalForceModel` or `SocialForceModel` for force-based research questions.

3. Define stages and journeys.
   - Add exits, waypoints, queues, waiting sets, or direct steering stages.
   - Create `JourneyDescription` objects and transitions.
   - Keep exits at terminal route positions unless immediate removal is intended.

4. Generate initial agents.
   - Use JuPedSim distribution helpers for reproducible placement with spacing constraints.
   - Reuse an agent-parameter object only when intentionally changing position or speed between `add_agent` calls.
   - Seed stochastic placement and record the seed.

5. Run with explicit termination.
   - Use `while simulation.agent_count() > 0 and simulation.iteration_count() < max_iterations`.
   - Close the SQLite writer or custom writer after the loop.
   - Record `dt`, `every_nth_frame`, model parameters, geometry source, and stop condition.

6. Validate and analyze.
   - Inspect removal counts, final agent count, frame count, geometry, and trajectory bounds.
   - Convert SQLite outputs to PedPy trajectories when computing density, speed, flow, or fundamental diagrams.
   - Compare model variants with matched geometry, seeds, initial positions, and output intervals.

## Decision Table

| User goal | JuPedSim path |
| --- | --- |
| Minimal evacuation scenario | Geometry, exit stage, one journey, CSM, SQLite writer |
| Bottleneck/capacity study | Narrow geometry, controlled start distribution, PedPy flow/density analysis |
| Route-choice policy | Multiple journeys or transitions; compare fixed, round-robin, least-targeted |
| Queue or waiting behavior | `add_queue_stage` or `add_waiting_set_stage`; manipulate `pop()` or `state` |
| Dynamic target control | Direct steering stage and per-agent `agent.target` updates |
| Model comparison | Same scenario under CSM/CSM V2/AVM/GCFM/SFM with matched seeds |
| Calibration/sensitivity | Parameter matrix, repeated seeds, manifest, summary metrics |
| Custom output | Subclass `TrajectoryWriter` or use `SqliteTrajectoryWriter` plus postprocessing |

## Quality Gates

- Geometry gate: all stages, exits, and start positions are inside the walkable area and routable.
- Model gate: parameter choices match the model's assumptions and are not merely copied defaults.
- Numerical gate: `dt`, writer interval, and stop conditions are explicit.
- Reproducibility gate: seeds, geometry, population, model, and output filenames are recorded.
- Analysis gate: reported conclusions are tied to metrics, not only to animation or visual impression.

## Coding Standards

- Import JuPedSim as `import jupedsim as jps`.
- Use `pathlib.Path` for outputs.
- Keep geometry, model, stage/journey graph, population, run loop, and analysis in distinct functions.
- Prefer snake_case parameter names such as `desired_speed`, `reaction_time`, and `body_force`; legacy camelCase aliases exist but should not be used in new code.
- Catch placement failures from distribution functions and tell the user whether the requested density conflicts with spacing or boundary constraints.
- Close `simulation._writer` or custom writers in normal completion and interrupt paths.
- Name SQLite files by scenario and parameter values when running sweeps.

## Templates

Adapt templates from `assets/templates/`:

- `evacuation_scenario_template.py` for a single robust simulation script.
- `experiment_matrix_template.py` for parameter sweeps, model comparisons, and reproducibility manifests.

