---
name: petrack
description: "PeTrack pedestrian trajectory extraction skill for planning camera-based experiments, preparing calibration data, configuring intrinsic and extrinsic calibration, selecting recognition markers, setting recognition and tracking regions of interest, tuning marker/tracking parameters, correcting trajectories, exporting TRC/TXT/HDF5 outputs, validating trajectory files, preparing 3DC calibration point files, batch processing videos, and connecting PeTrack outputs to pedestrian dynamics analysis tools."
---

# PeTrack

Use this skill to guide high-quality PeTrack work from experiment planning through trajectory export. PeTrack is a GUI-centered tool, so answers should be operational: tell the user what to prepare, what to click or configure, what files to keep, and what checks to run before trusting exported trajectories.

## Source Policy

Do not copy PeTrack manuals, screenshots, videos, or documentation assets into generated repo content. The local docs used to create this skill live outside the GitHub-bound skill folder under `Manuals/PeTrack/`; treat them as source material, not distributable content.

## Reference Routing

- Read `references/petrack-workflow-map.md` for the end-to-end PeTrack workflow.
- Read `references/petrack-planning-quality.md` before advising on experiment setup, cameras, markers, lighting, synchronization, or data preparation.
- Read `references/petrack-calibration.md` for intrinsic calibration, extrinsic calibration, and `.3dc` point-file guidance.
- Read `references/petrack-recognition-tracking.md` for marker selection, recognition setup, ROI rules, tracking, and correction.
- Read `references/petrack-export-analysis.md` for `.trc`, `.txt`, HDF5, video export, CLI/batch processing, and downstream analysis.
- Read `references/petrack-pitfalls.md` when diagnosing poor tracks, calibration errors, false detections, ID switches, or export issues.

## Core Workflow

1. Clarify the data context.
   - Ask for camera count, camera position, video duration, frame rate, marker type, calibration material, and intended trajectory output.
   - If the video was already recorded, identify what cannot be repaired in software: motion blur, missing calibration footage, poor marker visibility, frame drops, or severe occlusion.

2. Plan or audit the experiment setup.
   - Prefer overhead or high-mounted cameras with small angle of view when possible.
   - Keep camera settings manual and fixed before intrinsic calibration.
   - Use stable lighting, avoid marker colors in clothing or floor surfaces, and keep non-participants out of the camera view.
   - For multi-camera or sensor fusion, require temporal synchronization and a common spatial reference.

3. Calibrate before recognition.
   - Intrinsic calibration corrects lens distortion and must match the final camera settings.
   - Extrinsic calibration maps image pixels to world coordinates and must match the final camera position and orientation.
   - Prepare `.3dc` point files in centimeters with one `x y z` coordinate row per point.
   - Keep a project file after calibration so later recognition/tracking settings can be reset without redoing calibration.

4. Configure recognition.
   - Choose marker logic based on data: multicolor marker, code marker, combined multicolor+code marker, or machine-learning marker.
   - Recognition ROI is green and should be inside the tracking ROI.
   - For multicolor markers, select color ranges with the mask visible; tune open/close morphology after color selection.
   - For code markers, select the correct ArUco dictionary and verify marker resolution before relying on marker IDs.
   - Record height assumptions and marker-to-height or marker-to-participant mappings.

5. Configure tracking.
   - Tracking ROI is blue and must be larger than the recognition ROI.
   - Tune search region scale, pyramid levels, maximum error, Kalman filter, and extrapolation using a short representative segment first.
   - Use `calculate all` only after recognition, ROI, and tracking settings are stable.
   - Export `.trc` as the working trajectory file after automatic tracking.

6. Correct manually.
   - Disable active recognition and tracking before manual correction to avoid overwriting corrected trajectories.
   - Inspect trajectories one person at a time with show-only controls.
   - Use correction tests for duplicate tracks, velocity jumps, short trajectories, and tracks starting or ending inside the recognition ROI.
   - Save correction progress as `.trc`; export analysis formats only after correction is complete.

7. Export and validate.
   - Use `.trc` for PeTrack re-import and project continuity.
   - Use `.txt` or HDF5 for analysis.
   - Prefer meter output for downstream tools.
   - Use `scripts/validate_txt_export.py` on exported `.txt` trajectories when files are available.
   - Keep project `.pet`, raw video, calibration files, `.trc`, final export, and processing notes together.

## Decision Table

| User goal | PeTrack path |
| --- | --- |
| New experiment planning | Read planning reference, camera/lighting/marker checklist, calibration plan |
| Existing video processing | Calibration audit, recognition setup, tracking setup, correction plan |
| Prepare `.3dc` file | Use `scripts/create_3dc_points.py` or the calibration reference |
| Multicolor marker setup | Color map, height map, mask, morphology, ROI and false-positive checks |
| Code marker setup | ArUco dictionary, resolution check, marker ID export, height mapping |
| ML marker setup | ONNX model, YOLO family, confidence/NMS/score thresholds |
| Batch process videos | Template `.pet`, CLI command, per-video correction and validation |
| Export for analysis | `.txt` or HDF5, meter units, marker IDs/head direction when needed |
| Diagnose bad tracks | Pitfalls reference, correction tests, ROI and calibration review |

## Scripted Utilities

- `scripts/create_3dc_points.py` creates and validates PeTrack extrinsic calibration point files from CSV coordinate tables.
- `scripts/validate_txt_export.py` checks PeTrack `.txt` trajectory exports for parseability, duplicate id-frame pairs, monotonic frames, finite coordinates, and basic metadata.

Use scripts as consistency aids; they do not replace visual inspection or manual correction.

## Quality Gates

- Planning gate: camera settings, marker choice, lighting, and participant clothing are compatible with recognition.
- Calibration gate: intrinsic calibration covers the whole area of interest; extrinsic points are ordered correctly and span the tracked area.
- Recognition gate: marker detections are inside the intended ROI, false positives are controlled, and height/ID mappings are documented.
- Tracking gate: tracking ROI encloses recognition ROI, search settings are tested on representative frames, and automatic tracking is saved as `.trc`.
- Correction gate: manual review covers start/end points, split tracks, duplicate tracks, missing people, and non-participants.
- Export gate: exported trajectory format, units, frame rate, marker IDs, head direction, and comments match the downstream analysis need.
- Reproducibility gate: keep raw video, `.pet`, calibration files, `.trc`, final export, and processing log.

## Templates

Adapt templates from `assets/templates/`:

- `petrack_processing_log_template.md` for documenting project settings, calibration, recognition, tracking, correction, and export choices.
- `petrack_correction_checklist_template.md` for person-by-person correction review.
