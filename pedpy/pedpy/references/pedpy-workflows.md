# PedPy Workflows

Use these recipes as starting points. Adapt paths, geometry, units, frame rates, and output names to the user's project.

## Minimal DataFrame Workflow

```python
import pandas as pd
from pedpy import TrajectoryData

data = pd.DataFrame(
    [[1, 0, 0.0, 0.0], [1, 1, 0.1, 0.0]],
    columns=["id", "frame", "x", "y"],
)
traj = TrajectoryData(data=data, frame_rate=25.0)
```

Use this when the user already has clean tabular data or wants to convert from a custom source.

## Geometry Setup

```python
from pedpy import MeasurementArea, MeasurementLine, WalkableArea

walkable_area = WalkableArea(
    polygon=[(-2.0, -1.0), (2.0, -1.0), (2.0, 6.0), (-2.0, 6.0)]
)

measurement_area = MeasurementArea(
    coordinates=[(-0.8, 1.0), (0.8, 1.0), (0.8, 1.8), (-0.8, 1.8)]
)

measurement_line = MeasurementLine(coordinates=[(-0.5, 2.0), (0.5, 2.0)])
```

After defining geometry, plot it over trajectories before trusting metrics.

```python
from pedpy import plot_measurement_setup

ax = plot_measurement_setup(
    traj=traj,
    walkable_area=walkable_area,
    measurement_areas=[measurement_area],
    measurement_lines=[measurement_line],
)
ax.set_aspect("equal")
```

## Validate Trajectories

```python
from pedpy import get_invalid_trajectory, is_trajectory_valid

if not is_trajectory_valid(traj_data=traj, walkable_area=walkable_area):
    invalid = get_invalid_trajectory(traj_data=traj, walkable_area=walkable_area)
    invalid.to_csv("invalid_trajectories.csv", index=False)
    raise ValueError("Some trajectory points are outside the walkable area.")
```

Use this before Voronoi methods and before any plot that suggests geometry-data alignment.

## Classic Density

```python
from pedpy import compute_classic_density, plot_density

classic_density = compute_classic_density(
    traj_data=traj,
    measurement_area=measurement_area,
)

plot_density(density=classic_density, title="Classic density")
```

Classic density counts pedestrians in a measurement area and divides by area. It is direct and easy to interpret.

## Voronoi Density

```python
from pedpy import Cutoff, compute_individual_voronoi_polygons, compute_voronoi_density

individual_voronoi = compute_individual_voronoi_polygons(
    traj_data=traj,
    walkable_area=walkable_area,
    cut_off=Cutoff(radius=1.0, quad_segments=3),
)

voronoi_density, intersecting = compute_voronoi_density(
    individual_voronoi_data=individual_voronoi,
    measurement_area=measurement_area,
)
```

Use a cutoff when unbounded or very large cells would dominate the interpretation. Record the radius in outputs.

## Bottleneck Flow

```python
from pedpy import SpeedCalculation, compute_flow, compute_individual_speed, compute_n_t

nt, crossing_frames = compute_n_t(
    traj_data=traj,
    measurement_line=measurement_line,
)

individual_speed = compute_individual_speed(
    traj_data=traj,
    frame_step=int(traj.frame_rate),
    compute_velocity=True,
    speed_calculation=SpeedCalculation.BORDER_SINGLE_SIDED,
)

flow = compute_flow(
    nt=nt,
    crossing_frames=crossing_frames,
    individual_speed=individual_speed,
    delta_frame=100,
    frame_rate=traj.frame_rate,
)
```

For fundamental diagrams at a measurement line, pair this with line density or line speed.

## Passing Metrics

```python
from pedpy import compute_frame_range_in_area, compute_passing_density, compute_passing_speed

frames_in_area, used_area = compute_frame_range_in_area(
    traj_data=traj,
    measurement_line=measurement_line,
    width=1.0,
)

passing_density = compute_passing_density(
    density_per_frame=classic_density,
    frames=frames_in_area,
)

passing_speed = compute_passing_speed(
    frames_in_area=frames_in_area,
    frame_rate=traj.frame_rate,
    distance=1.0,
)
```

Passing metrics produce per-pedestrian values for a virtual area around a measurement line.

## Mean And Voronoi Speed

```python
from pedpy import compute_mean_speed_per_frame, compute_voronoi_speed

mean_speed = compute_mean_speed_per_frame(
    traj_data=traj,
    individual_speed=individual_speed,
    measurement_area=measurement_area,
)

voronoi_speed = compute_voronoi_speed(
    traj_data=traj,
    individual_speed=individual_speed,
    individual_voronoi_intersection=intersecting,
    measurement_area=measurement_area,
)
```

The mean speed requires speed values for pedestrians inside the measurement area. Border settings can remove rows.

## Line Density, Speed, And Flow

```python
from pedpy import (
    compute_line_density,
    compute_line_flow,
    compute_line_speed,
    compute_species,
)

species = compute_species(
    trajectory_data=traj,
    individual_voronoi_polygons=individual_voronoi,
    measurement_line=measurement_line,
    frame_step=int(traj.frame_rate),
)

line_density = compute_line_density(
    individual_voronoi_polygons=individual_voronoi,
    measurement_line=measurement_line,
    species=species,
)

line_speed = compute_line_speed(
    individual_voronoi_polygons=individual_voronoi,
    measurement_line=measurement_line,
    individual_speed=individual_speed,
    species=species,
)

line_flow = compute_line_flow(
    individual_voronoi_polygons=individual_voronoi,
    measurement_line=measurement_line,
    individual_speed=individual_speed,
    species=species,
)
```

Use this path when the analysis is explicitly line-based or when building a fundamental diagram at a measurement line.

## Profiles

```python
import pandas as pd
from pedpy import (
    FRAME_COL,
    ID_COL,
    DensityMethod,
    SpeedMethod,
    compute_grid_cell_polygon_intersection_area,
    compute_profiles,
    get_grid_cells,
)

profile_data = (
    individual_speed
    .merge(individual_voronoi, on=[ID_COL, FRAME_COL])
    .merge(traj.data, on=[ID_COL, FRAME_COL])
)

profile_data = profile_data[profile_data.frame.between(250, 400)]

grid_cells, _, _ = get_grid_cells(walkable_area=walkable_area, grid_size=0.4)
grid_area, resorted_profile_data = compute_grid_cell_polygon_intersection_area(
    data=profile_data,
    grid_cells=grid_cells,
)

density_profiles, speed_profiles = compute_profiles(
    data=resorted_profile_data,
    walkable_area=walkable_area.polygon,
    grid_size=0.4,
    speed_method=SpeedMethod.ARITHMETIC,
    density_method=DensityMethod.VORONOI,
)
```

Profiles are compute-heavy. Restrict frames and use `AxisAlignedMeasurementArea` when the user only needs a rectangular subregion.

## Export Results

```python
from pathlib import Path
import numpy as np

output_dir = Path("pedpy-results")
output_dir.mkdir(parents=True, exist_ok=True)

classic_density.reset_index().to_csv(output_dir / "classic_density.csv", index=False)
flow.to_csv(output_dir / "flow.csv", index=False)
np.savetxt(output_dir / "density_profiles.txt", density_profiles.reshape(-1))
```

For each exported file, explain the measurement geometry and method parameters that produced it.

