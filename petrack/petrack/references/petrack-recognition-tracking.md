# Recognition, Tracking, And Correction

Use this reference when configuring PeTrack detection, linking detections into
trajectories, or repairing automatic tracking results.

## Recognition Setup

Recognition detects pedestrians or markers. The recognition ROI is green and
should be inside the tracking ROI.

| Setting | Guidance |
| --- | --- |
| `active` | Enables automatic recognition. Disable it before manual correction unless deliberately retracking. |
| `step` | Recognition interval. Use `1` when accuracy matters; larger values fill gaps with tracking. |
| marker | Choose multicolor, code marker, combined marker, or machine-learning marker. |
| parameter | Opens marker-specific settings. |
| ROI | Set to the relevant image area only; avoid false-positive regions. |

## ROI Rule

The tracking ROI must be larger than the recognition ROI. Detections outside
the tracking ROI can produce one-point trajectories. A robust setup is:

1. Set or verify the blue tracking ROI.
2. Use recognition `adjust automatically` or manually set the green ROI inside it.
3. Fix ROIs once they are correct.

## Multicolor Markers

Use when colored hats or beanies are available and camera resolution may be
limited.

Recommended sequence:

1. Select multicolor marker.
2. Open marker parameters.
3. Disable open/close morphology while selecting color.
4. Enable mask with partial opacity to inspect selected pixels.
5. Select color using color range or color picker.
6. Set map height for each color class.
7. Enable morphology only after the color range is reasonable.
8. Check area and shape filters to remove non-head blobs.

Important options:

- `use code marker`: combine color detection with ArUco code detection.
- `ignore head without black dot or code marker`: reduces false positives but
  may drop valid detections when codes are not always readable.
- `auto correct perspective view`: useful, but prefer applying only at export
  when tracking quality would suffer.
- `open radius` removes small specks.
- `close radius` fills small holes.

## Code Markers

Use when individual identity, questionnaire linkage, or head direction is
needed.

Checks:

- Select the correct ArUco dictionary.
- Verify marker resolution at the actual camera distance.
- Inspect detected candidates: successful detections carry marker ID; failed
  candidates indicate unreadable codes or poor parameters.
- Tune adaptive thresholding when detections are unstable.

Code marker export can include marker ID and head direction.

## Machine-Learning Markers

Use when physical markers are unavailable or custom detection classes are
needed.

Requirements:

- ONNX model.
- Correct YOLO family selection: YOLOv5 or YOLOv8 to YOLOv11.
- Optional `.names` file for multiple classes.

Parameters:

- confidence threshold: prediction confidence required for acceptance.
- NMS threshold: overlap threshold for suppressing duplicate detections.
- score threshold: class confidence threshold, useful with multiple classes.
- image width: must match training image size.

Machine-learning recognition still needs ROI control and manual QA.

## Tracking Setup

Tracking links detections over time and fills gaps using optical flow.

| Setting | Guidance |
| --- | --- |
| `active` | Tracks while navigating the video. |
| `calculate all` | Runs complete video forward and backward after settings are stable. |
| `repeat below quality` | Avoids overwriting good existing points unless quality is poor. |
| `use kalman filter` | Usually stabilizes trajectories. |
| `extrapolation for big diff.` | Discards implausible jumps and extrapolates, but only for a short run of frames. |
| `merge` | Used for controlled manual merging. Disable after use. |
| `only selected` | Applies tracking only to selected people when show-only controls are active. |

Search region:

- Increase scale when expected motion between frames is larger.
- Adjust pyramid levels carefully.
- `max. error` controls when tracking should be rejected.
- Include textured marker regions; plain flat color can be weak for optical flow.

## Manual Correction

Before correction:

- Open the tracked project.
- Import `.trc` if the project does not load trajectories.
- Disable active recognition and tracking.
- Use show-only controls to inspect one person at a time.

Check each trajectory:

- correct start and end frames
- no duplicate trajectory for the same person
- no non-participant trajectory
- no large jumps, sharp peaks, or impossible speed
- no split tracks that should be merged
- no missing person or missing segment
- head point is sufficiently accurate

Common operations:

- create new trajectory
- retrack trajectory
- retrack with recognition
- move point
- split trajectory
- merge trajectories
- delete complete trajectory
- delete past/future segment

Save progress by exporting `.trc` regularly.

## Correction Tab Tests

| Test | Finds |
| --- | --- |
| Equality | Trajectories close to each other, often duplicates. |
| Velocity | Sudden movement changes or jumps. |
| Length | Short trajectories below a chosen frame count. |
| Inside | Trajectories starting/ending inside recognition ROI. |

Treat test output as candidates for review, not automatic proof of error.
