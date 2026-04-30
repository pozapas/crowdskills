# PedPy API Map

This map is a compact navigation layer for PedPy 1.4.0 style workflows. Use it to select functions quickly, then write code around the user's actual data, geometry, and requested metrics.

## Data Containers

| Object | Purpose | Notes |
| --- | --- | --- |
| `TrajectoryData(data, frame_rate)` | Internal trajectory container | DataFrame input should include `id`, `frame`, `x`, `y`; PedPy also works with geometry-derived `point` data. |
| `WalkableArea(polygon, obstacles=None)` | Space pedestrians can occupy | Required for validation and Voronoi boundary clipping. |
| `MeasurementArea(coordinates)` | Polygonal area for density, speed, acceleration, and profiles | Classic density examples use convex polygons. |
| `AxisAlignedMeasurementArea(x_min, y_min, x_max, y_max)` | Rectangular area aligned to axes | Useful for profile speedups and explicit grid bounds. |
| `MeasurementLine(coordinates)` | Line for crossings and entrance distance | Use for N-t curves, flow, line metrics, and time-distance analysis. |

## Loaders

| Format | Function |
| --- | --- |
| Generic trajectory file | `load_trajectory(trajectory_file=..., default_frame_rate=..., default_unit=...)` |
| Text/Juelich-style archive text | `load_trajectory_from_txt(...)` |
| Ped Data Archive HDF5 | `load_trajectory_from_ped_data_archive_hdf5(...)`; geometry via `load_walkable_area_from_ped_data_archive_hdf5(...)` |
| Vadere | `load_trajectory_from_vadere(trajectory_file=..., frame_rate=...)`; geometry via `load_walkable_area_from_vadere_scenario(...)` |
| Viswalk | `load_trajectory_from_viswalk(...)` |
| Pathfinder CSV/JSON | `load_trajectory_from_pathfinder_csv(...)`; `load_trajectory_from_pathfinder_json(...)` |
| Crowd:it | `load_trajectory_from_crowdit(...)`; geometry via `load_walkable_area_from_crowdit(...)` |
| JuPedSim SQLite | `load_trajectory_from_jupedsim_sqlite(...)`; geometry via `load_walkable_area_from_jupedsim_sqlite(...)` |

`TrajectoryUnit.METER` and `TrajectoryUnit.CENTIMETER` are available for explicit unit handling.

## Validation And Utilities

| Need | Function |
| --- | --- |
| Check whether trajectories are inside walkable area | `is_trajectory_valid(traj_data=..., walkable_area=...)` |
| Get invalid trajectory rows | `get_invalid_trajectory(traj_data=..., walkable_area=...)` |
| Crossing frames at a line | `compute_crossing_frames(traj_data=..., measurement_line=...)` |
| Frame intervals inside virtual area near line | `compute_frame_range_in_area(traj_data=..., measurement_line=..., width=...)` |
| Time and distance to line | `compute_time_distance_line(traj_data=..., measurement_line=...)` |
| Intersect Voronoi polygons with measurement area | `compute_intersecting_polygons(individual_voronoi_data=..., measurement_area=...)` |

## Density

| Metric | Function | Inputs |
| --- | --- | --- |
| Classic density | `compute_classic_density(...)` | `traj_data`, `measurement_area` |
| Individual Voronoi polygons | `compute_individual_voronoi_polygons(...)` | `traj_data`, `walkable_area`, optional `Cutoff` |
| Voronoi density | `compute_voronoi_density(...)` | individual Voronoi output, `measurement_area` |
| Passing density | `compute_passing_density(...)` | density per frame and frame intervals |
| Line density | `compute_line_density(...)` | individual Voronoi polygons, measurement line, species |

## Speed

| Metric | Function | Inputs |
| --- | --- | --- |
| Individual speed | `compute_individual_speed(...)` | `traj_data`, `frame_step`, optional movement direction, optional velocity components |
| Mean speed per frame | `compute_mean_speed_per_frame(...)` | trajectory data, individual speed, measurement area |
| Voronoi speed | `compute_voronoi_speed(...)` | trajectory data, individual speed, Voronoi intersections, measurement area |
| Passing speed | `compute_passing_speed(...)` | frame intervals, frame rate, distance |
| Species at line | `compute_species(...)` | trajectory data, Voronoi polygons, measurement line, frame step |
| Line speed | `compute_line_speed(...)` | Voronoi polygons, measurement line, individual speed, species |

`SpeedCalculation` supports `BORDER_EXCLUDE`, `BORDER_ADAPTIVE`, and `BORDER_SINGLE_SIDED`.

## Flow

| Metric | Function | Inputs |
| --- | --- | --- |
| N-t curve | `compute_n_t(...)` | trajectory data, measurement line |
| Flow over crossing intervals | `compute_flow(...)` | N-t, crossing frames, individual speed, `delta_frame`, frame rate |
| Line flow | `compute_line_flow(...)` | Voronoi polygons, measurement line, individual speed, species |

## Acceleration

| Metric | Function | Inputs |
| --- | --- | --- |
| Individual acceleration | `compute_individual_acceleration(...)` | `traj_data`, `frame_step`, optional movement direction/components |
| Mean acceleration | `compute_mean_acceleration_per_frame(...)` | trajectory data, individual acceleration, measurement area |
| Voronoi acceleration | `compute_voronoi_acceleration(...)` | trajectory data, individual acceleration, Voronoi intersections, measurement area |

`AccelerationCalculation.BORDER_EXCLUDE` is the documented border mode.

## Profiles

| Need | Function |
| --- | --- |
| Build profile grid | `get_grid_cells(walkable_area=..., axis_aligned_measurement_area=..., grid_size=...)` |
| Cache grid/polygon intersections | `compute_grid_cell_polygon_intersection_area(data=..., grid_cells=...)` |
| Speed profile | `compute_speed_profile(...)` |
| Density profile | `compute_density_profile(...)` |
| Combined density and speed profiles | `compute_profiles(...)` |

`DensityMethod` includes `CLASSIC`, `GAUSSIAN`, and `VORONOI`.
`SpeedMethod` includes `ARITHMETIC`, `GAUSSIAN`, `MEAN`, and `VORONOI`.

## Neighborhood And Spatial Analysis

| Need | Function |
| --- | --- |
| Voronoi neighbors | `compute_neighbors(individual_voronoi_data, as_list=False)` |
| Neighbor distances | `compute_neighbor_distance(traj_data=..., neighborhood=...)` |
| Pair-distribution function | `compute_pair_distribution_function(traj_data=..., radius_bin_size=..., randomisation_stacking=...)` |

## Plotting

Common plot helpers include:

- `plot_trajectories(...)`
- `plot_walkable_area(...)`
- `plot_measurement_setup(...)`
- `plot_nt(...)`
- `plot_flow(...)` and `plot_flow_at_line(...)`
- `plot_density(...)`, `plot_density_distribution(...)`, and `plot_density_at_line(...)`
- `plot_speed(...)`, `plot_speed_distribution(...)`, and `plot_speed_at_line(...)`
- `plot_acceleration(...)`
- `plot_voronoi_cells(...)`
- `plot_profiles(...)`
- `plot_neighborhood(...)`
- `plot_time_distance(...)`

## Column Identifiers

Prefer constants over string literals:

| Concept | Constant |
| --- | --- |
| Pedestrian and frame keys | `ID_COL`, `FRAME_COL` |
| Coordinates and geometry | `X_COL`, `Y_COL`, `POINT_COL`, `POLYGON_COL`, `INTERSECTION_COL` |
| Time and crossing | `TIME_COL`, `CROSSING_FRAME_COL`, `FIRST_FRAME_COL`, `LAST_FRAME_COL`, `MID_FRAME_COL` |
| Density and counts | `DENSITY_COL`, `COUNT_COL`, `DENSITY_SP1_COL`, `DENSITY_SP2_COL` |
| Speed and velocity | `SPEED_COL`, `MEAN_SPEED_COL`, `V_X_COL`, `V_Y_COL`, `SPEED_SP1_COL`, `SPEED_SP2_COL` |
| Flow | `FLOW_COL`, `CUMULATED_COL`, `FLOW_SP1_COL`, `FLOW_SP2_COL` |
| Acceleration | `ACC_COL`, `A_X_COL`, `A_Y_COL` |
| Neighborhood | `NEIGHBORS_COL`, `NEIGHBOR_ID_COL`, `DISTANCE_COL` |
| Line/species outputs | `SPECIES_COL`, `START_POSITION_COL`, `MID_POSITION_COL`, `END_POSITION_COL` |

