"""Starter PedPy analysis script.

Adapt loader, geometry, metrics, and outputs for the user's trajectory data.
"""

from pathlib import Path

import pandas as pd
from pedpy import (
    FRAME_COL,
    ID_COL,
    Cutoff,
    MeasurementArea,
    MeasurementLine,
    SpeedCalculation,
    WalkableArea,
    compute_classic_density,
    compute_flow,
    compute_individual_speed,
    compute_individual_voronoi_polygons,
    compute_n_t,
    compute_voronoi_density,
    get_invalid_trajectory,
    is_trajectory_valid,
    plot_density,
    plot_measurement_setup,
    plot_nt,
)


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "pedpy-results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_trajectory() -> "TrajectoryData":
    """Replace this with the loader that matches the user's data source."""
    from pedpy import TrajectoryData

    data = pd.read_csv(PROJECT_ROOT / "trajectory.csv")
    return TrajectoryData(data=data, frame_rate=25.0)


def build_geometry():
    """Replace coordinates with the user's facility, experiment, or simulation geometry."""
    walkable_area = WalkableArea(
        polygon=[(-2.0, -1.0), (2.0, -1.0), (2.0, 6.0), (-2.0, 6.0)]
    )
    measurement_area = MeasurementArea(
        coordinates=[(-0.8, 1.0), (0.8, 1.0), (0.8, 1.8), (-0.8, 1.8)]
    )
    measurement_line = MeasurementLine(coordinates=[(-0.5, 2.0), (0.5, 2.0)])
    return walkable_area, measurement_area, measurement_line


def main() -> None:
    traj = load_trajectory()
    walkable_area, measurement_area, measurement_line = build_geometry()

    if not is_trajectory_valid(traj_data=traj, walkable_area=walkable_area):
        invalid = get_invalid_trajectory(traj_data=traj, walkable_area=walkable_area)
        invalid.to_csv(OUTPUT_DIR / "invalid_trajectories.csv", index=False)
        raise ValueError("Trajectory contains points outside the walkable area.")

    setup_ax = plot_measurement_setup(
        traj=traj,
        walkable_area=walkable_area,
        measurement_areas=[measurement_area],
        measurement_lines=[measurement_line],
    )
    setup_ax.set_aspect("equal")
    setup_ax.figure.savefig(OUTPUT_DIR / "measurement_setup.png", dpi=180)

    classic_density = compute_classic_density(
        traj_data=traj,
        measurement_area=measurement_area,
    )
    classic_density.reset_index().to_csv(
        OUTPUT_DIR / "classic_density.csv", index=False
    )

    individual_voronoi = compute_individual_voronoi_polygons(
        traj_data=traj,
        walkable_area=walkable_area,
        cut_off=Cutoff(radius=1.0, quad_segments=3),
    )
    voronoi_density, intersecting = compute_voronoi_density(
        individual_voronoi_data=individual_voronoi,
        measurement_area=measurement_area,
    )
    voronoi_density.reset_index().to_csv(
        OUTPUT_DIR / "voronoi_density.csv", index=False
    )

    individual_speed = compute_individual_speed(
        traj_data=traj,
        frame_step=int(traj.frame_rate),
        compute_velocity=True,
        speed_calculation=SpeedCalculation.BORDER_SINGLE_SIDED,
    )
    individual_speed.to_csv(OUTPUT_DIR / "individual_speed.csv", index=False)

    nt, crossing_frames = compute_n_t(
        traj_data=traj,
        measurement_line=measurement_line,
    )
    flow = compute_flow(
        nt=nt,
        crossing_frames=crossing_frames,
        individual_speed=individual_speed,
        delta_frame=100,
        frame_rate=traj.frame_rate,
    )
    flow.to_csv(OUTPUT_DIR / "flow.csv", index=False)

    plot_density(density=classic_density, title="Classic density").figure.savefig(
        OUTPUT_DIR / "classic_density.png", dpi=180
    )
    plot_density(density=voronoi_density, title="Voronoi density").figure.savefig(
        OUTPUT_DIR / "voronoi_density.png", dpi=180
    )
    plot_nt(nt=nt).figure.savefig(OUTPUT_DIR / "nt.png", dpi=180)

    merged = traj.data.merge(individual_speed, on=[ID_COL, FRAME_COL], how="left")
    merged.to_csv(OUTPUT_DIR / "trajectory_with_speed.csv", index=False)


if __name__ == "__main__":
    main()

