# PedPy Pitfalls And Checks

Use this checklist when a PedPy analysis is fragile, slow, or surprising.

## Geometry

- Plot trajectories, walkable area, measurement areas, and measurement lines before computing final metrics.
- Keep measurement area coordinates in the same coordinate system and unit as the trajectory data.
- Classic measurement areas should be convex in the documented workflow.
- Voronoi polygons are clipped by `WalkableArea`; invalid or too-tight walkable geometry can create misleading cells.
- Non-convex walkable areas can create unexpected Voronoi artifacts because the method is based on Euclidean distance.
- For profile computations, arbitrary polygons become awkward because the grid is axis-aligned; use `AxisAlignedMeasurementArea` for explicit rectangular bounds.

## Frame Rate And Windows

- `TrajectoryData.frame_rate` is not cosmetic. Flow, speed, acceleration, and passing metrics depend on it.
- Document `frame_step` in real time, for example `frame_step=int(traj.frame_rate)` for roughly one second at 25 fps.
- Border handling changes row availability:
  - `SpeedCalculation.BORDER_EXCLUDE` omits frames without a full window.
  - `SpeedCalculation.BORDER_ADAPTIVE` shrinks windows near boundaries.
  - `SpeedCalculation.BORDER_SINGLE_SIDED` can preserve border rows by looking one way.
- Mean and Voronoi speed or acceleration may fail or lose rows if the per-pedestrian metric is missing for pedestrians inside the area.

## Voronoi Choices

- Consider `Cutoff(radius=..., quad_segments=...)` when the walkable area is large or pedestrians are sparse.
- Record the cutoff radius in every report because it changes density and line metrics.
- Use cut and uncut comparison plots when method choice might affect conclusions.
- Use `compute_neighbors(..., as_list=False)` for neighborhood workflows; the legacy default list behavior is harder to use downstream.

## Line-Based Metrics

- The orientation and placement of `MeasurementLine` matter. Visualize it and verify the crossing direction.
- For line density, line speed, and line flow, compute `species` first and validate it when bidirectional movement is possible.
- Passing metrics use a virtual measurement area defined by a line and a width. Explain the width as a physical distance.

## Performance

- Profile calculations can be expensive. Restrict to relevant frames and regions before computing grids.
- Cache `compute_grid_cell_polygon_intersection_area(...)` if computing multiple profile variants on the same sorted data.
- Avoid recomputing individual Voronoi polygons for every metric; compute once and reuse.
- Export intermediate DataFrames when the analysis is long enough to need auditability.

## Result Hygiene

- Use PedPy column constants in merges and downstream plots to avoid breakage when names change.
- Check row counts after merges on `ID_COL` and `FRAME_COL`.
- Keep raw trajectory data, filtered data, and computed metrics as separate variables.
- When filtering with pandas or Shapely, rebuild `TrajectoryData(filtered_df, frame_rate=traj.frame_rate)` before reusing PedPy functions.
- In reports, always state the coordinate unit, frame rate, measurement geometry, method family, and excluded-frame policy.

