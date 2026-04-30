---
name: pedpy
description: "PedPy pedestrian trajectory analysis workflows for loading, validating, preprocessing, analyzing, visualizing, and exporting crowd movement data. Use this skill when users need PedPy code or guidance for density, speed, flow, acceleration, Voronoi cells, N-t curves, passing metrics, profiles, measurement areas or lines, fundamental diagrams, neighborhood analysis, pair-distribution functions, or trajectory formats from Vadere, Viswalk, Pathfinder, Crowd:it, JuPedSim, text files, HDF5, or the Juelich data archive."
---

# PedPy

Use this skill to build reliable pedestrian trajectory analysis workflows with PedPy. The goal is to help Codex turn raw trajectory files and geometry into reproducible metrics, plots, and exported data without re-reading the full manual.

## Source Policy

Do not copy manuals into generated projects or this skill. The local manual used to create this skill lives outside the repo under `Manuals/pedpy/`; treat it as source material, not distributable skill content.

## First Pass

Before writing analysis code, establish these facts:

1. Input format: pandas DataFrame, text trajectory file, Ped Data Archive HDF5, Vadere, Viswalk, Pathfinder, Crowd:it, or JuPedSim.
2. Frame rate and coordinate unit. Make both explicit; many PedPy functions depend on frame rate.
3. Walkable geometry, measurement areas, and measurement lines. If geometry is missing, ask for coordinates or infer only when the data context makes that defensible.
4. Desired metrics: density, speed, flow, acceleration, profiles, neighborhood, time-distance, or spatial statistics.
5. Output form: script, notebook, plots, CSV files, or a short result interpretation.

Use `references/pedpy-api-map.md` when you need exact function names, arguments, column identifiers, or loader choices.
Use `references/pedpy-workflows.md` when composing a complete analysis pipeline.
Use `references/pedpy-pitfalls.md` when results look wrong, geometry is complicated, or a metric depends on border, Voronoi, or profile assumptions.

## Core Workflow

1. Load or construct `TrajectoryData`.
   - For a DataFrame, require at least `id`, `frame`, `x`, and `y`, then pass `frame_rate`.
   - For known simulator or archive formats, choose the matching loader rather than hand-parsing.

2. Define analysis geometry.
   - Use `WalkableArea` for the space pedestrians can occupy.
   - Use `MeasurementArea` for polygonal regions; keep classic measurement areas convex.
   - Use `MeasurementLine` for crossings, N-t curves, line flow, and entrance distance.

3. Validate before analyzing.
   - Run `is_trajectory_valid(...)` or `get_invalid_trajectory(...)` when a `WalkableArea` is available.
   - Plot the setup with `plot_measurement_setup(...)` for sanity checks.

4. Select the method that matches the research question.
   - Count-based density: `compute_classic_density(...)`.
   - Voronoi density or speed: compute individual Voronoi polygons first, then aggregate.
   - Flow through a bottleneck: compute N-t/crossing frames, compute individual speed, then compute flow.
   - Passing metrics: compute frame ranges in a virtual area, then passing density or speed.
   - Profiles: merge trajectory, speed, and Voronoi outputs; restrict frames and/or use an axis-aligned measurement area for performance.

5. Export and explain.
   - Use PedPy column identifier constants such as `ID_COL`, `FRAME_COL`, `DENSITY_COL`, and `SPEED_COL`.
   - Export tabular results with pandas and profile arrays with NumPy when appropriate.
   - Explain units, frame windows, measurement geometry, and any rows excluded by border handling.

## Method Selection

| User wants | Preferred PedPy path |
| --- | --- |
| Count density in a region over time | `compute_classic_density(traj_data, measurement_area)` |
| Voronoi density in a region | `compute_individual_voronoi_polygons(...)` then `compute_voronoi_density(...)` |
| Bottleneck crossing counts | `compute_n_t(traj_data, measurement_line)` |
| Flow over crossing intervals | `compute_n_t(...)`, `compute_individual_speed(...)`, then `compute_flow(...)` |
| Individual or mean speed | `compute_individual_speed(...)`, then `compute_mean_speed_per_frame(...)` |
| Voronoi speed | individual speed plus Voronoi intersections, then `compute_voronoi_speed(...)` |
| Acceleration | `compute_individual_acceleration(...)`, then mean or Voronoi acceleration |
| Line density, speed, or flow | Voronoi polygons plus `compute_species(...)`, then line metric functions |
| Neighborhoods | Voronoi polygons, then `compute_neighbors(..., as_list=False)` and `compute_neighbor_distance(...)` |
| Time or distance to a crossing | `compute_time_distance_line(...)` |
| Spatial profiles | `get_grid_cells(...)`, optional precomputed intersections, then profile functions |
| Pair-distribution function | `compute_pair_distribution_function(...)` |

## Coding Standards

- Prefer named imports from `pedpy` for the functions used in the workflow.
- Use `pathlib.Path` for files and create output folders explicitly.
- Keep measurement geometry near the top of the script so users can review coordinates.
- Use PedPy column constants instead of string literals where they exist.
- Merge DataFrames on `ID_COL` and `FRAME_COL`; verify that merged row counts make sense.
- For speed and acceleration, document `frame_step`, border handling, and movement direction if provided.
- For Voronoi methods, document whether a `Cutoff` was used and why.
- For profiles, limit frame ranges early and cache grid intersection areas when making multiple profile calls.

## Template

When creating a new analysis script, adapt `assets/templates/pedpy_analysis_template.py`. It is intentionally generic and should be customized with the user's loader, geometry, metrics, and outputs.

