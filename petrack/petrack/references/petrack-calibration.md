# Calibration

Use this reference for PeTrack intrinsic/extrinsic calibration and `.3dc` point
file preparation.

## Calibration Types

| Calibration | Purpose | Must be done after |
| --- | --- | --- |
| Intrinsic | Correct lens distortion | final camera settings, focus, resolution, lens, recording format |
| Extrinsic | Map image coordinates to world coordinates | final camera mounting, position, orientation, and intrinsic calibration |

Intrinsic calibration must be active before extrinsic calibration.

## Intrinsic Calibration

Inputs:

- chessboard or equivalent calibration pattern
- images extracted from video, or a calibration video that PeTrack can sample
- same camera settings as the experiment video

Workflow:

1. Open the Calibration tab.
2. Use `calib from images` or `calib from video`.
3. Select images that cover the full area of interest, including borders.
4. Click `calc`.
5. Enable `active`.
6. Check straight lines and border regions visually.
7. Save a project file after successful intrinsic calibration.

Quality checks:

- Area of interest is covered by calibration samples.
- Calibration images are not concentrated only in the center or one side.
- Straight structures look straight after correction.
- Border cropping is acceptable; if not, consider border handling carefully.

## Extrinsic Calibration

Inputs:

- a combined image where all measured calibration points are visible
- a `.3dc` file listing the real-world coordinates in centimeters
- an active intrinsic calibration

Workflow:

1. Open the combined calibration image in PeTrack.
2. Fix the coordinate system/alignment grid if mouse dragging risks moving it.
3. Click image points in the same order as the `.3dc` coordinate rows.
4. Load the `.3dc` file in the extrinsic parameters section.
5. Use `fetch` to associate selected pixel points with world points.
6. Use `calc` to calculate extrinsic parameters.
7. Inspect `show`, `error`, coordinate system, and calibration points.
8. Exclude or re-click badly aligned points if needed.
9. Save the project and save updated point coordinates if appropriate.

## `.3dc` Point File

Initial `.3dc` format:

```text
4
0 0 0
200 0 0
0 200 0
0 0 200
```

Rules:

- First line is the number of points.
- Each following row is `x y z` in centimeters.
- Row order must match the order in which image points are clicked.
- Use a coordinate origin that is convenient; relative positions must be correct.
- Point placement accuracy matters because small measured errors can create
  large spatial errors across the experiment area.

Use `scripts/create_3dc_points.py` to create a `.3dc` file from a CSV table.

## Point Selection Tips

- Zoom in before clicking points.
- Use the same point order as the `.3dc` file.
- If a click moves a nearby point instead of adding one, place the new point
  nearby and move it into position.
- Remove incorrect points and reselect them rather than trying to compensate
  later.
- Use calibration-point visualization to identify outliers.

## Common Calibration Failures

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Extrinsic calibration unavailable | Intrinsic calibration not active | Finish and activate intrinsic calibration first. |
| Straight lines remain curved | Poor intrinsic coverage or wrong camera settings | Recalibrate with better distributed images. |
| World coordinates look shifted/rotated | Point click order does not match `.3dc` order | Re-click points in file order. |
| High extrinsic error | inaccurate measured points, poor clicking, or outlier points | Check point file, zoom/re-click, remove bad outliers. |
| Exported positions wrong near borders | perspective/height assumptions or calibration coverage | Review height maps, calibration span, camera angle. |

## Saved Artifacts

Keep:

- intrinsic calibration images or video
- combined extrinsic calibration image
- original `.3dc` coordinate file
- updated `.3dc` file after PeTrack saves pixel coordinates
- calibrated `.pet` project
- notes on coordinate origin and units
