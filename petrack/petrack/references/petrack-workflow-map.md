# PeTrack Workflow Map

Use this reference to keep PeTrack work ordered. Most failures come from doing
steps out of sequence or trusting automatic tracking before calibration and
manual correction are finished.

## End-To-End Workflow

| Phase | Goal | Main artifacts |
| --- | --- | --- |
| Experiment planning | Record video that can be tracked | camera plan, marker plan, calibration plan |
| Intrinsic calibration | Correct lens distortion | chessboard video/images, `.pet` project |
| Extrinsic calibration | Map image to world coordinates | combined calibration image, `.3dc` point file |
| Recognition | Detect heads or markers in frames | recognition ROI, marker parameters, height/ID maps |
| Tracking | Link detections into trajectories | tracking ROI, search settings, `.trc` working file |
| Correction | Repair automatic tracking errors | corrected `.trc`, correction notes |
| Export | Produce analysis-ready data | `.txt` or HDF5 trajectory export, optional video/view export |
| Validation | Check output consistency | trajectory QA report, processing log |

## Recommended Working Order

1. Open or create a PeTrack project.
2. Load calibration material before the main experiment video when possible.
3. Perform intrinsic calibration and activate it.
4. Perform extrinsic calibration with ordered image points and `.3dc` world points.
5. Save a calibrated `.pet` project before recognition setup.
6. Load the experiment video or image sequence.
7. Set tracking ROI first; set recognition ROI inside it.
8. Configure marker recognition and verify detections visually.
9. Tune tracking settings on a representative segment.
10. Run `calculate all` after settings are stable.
11. Export `.trc` as the working trajectory file.
12. Disable active recognition/tracking before manual correction.
13. Correct trajectories person by person.
14. Export `.txt` or HDF5 for external analysis.
15. Validate exported trajectory files and archive the full processing state.

## File Roles

| File type | Role | Notes |
| --- | --- | --- |
| `.pet` | PeTrack project | Stores settings and links to project data. Save versions after major phases. |
| `.3dc` | Extrinsic calibration points | First line is point count; following rows are `x y z` in centimeters. |
| `.trc` | PeTrack working trajectory format | Best for saving correction progress and re-importing into PeTrack. |
| `.txt` | Text trajectory export | Main external analysis format; includes header comments and rows like `id frame x y z`. |
| `.h5` | HDF5 trajectory export | Useful for richer metadata and analysis workflows such as PedPy. |
| video/image sequence | Input data | Keep original raw video untouched; use clipped working copies when needed. |

## Project Versioning Pattern

Use explicit project filenames:

```text
experiment_01_calibrated.pet
experiment_01_recognition.pet
experiment_01_tracked.pet
experiment_01_corrected.pet
experiment_01_corrected.trc
experiment_01_trajectories_m.txt
```

This makes it clear which file can be used to restart each phase.

## When To Pause And Recheck

- Calibration error is high or straight lines remain curved after intrinsic calibration.
- Extrinsic points were clicked in a different order than the `.3dc` rows.
- Recognition ROI extends outside tracking ROI.
- Marker colors also appear in clothing, floor, walls, or shadows.
- Code marker IDs are missing in many frames.
- Automatic tracking creates many short tracks or duplicate tracks.
- Export units or optional fields do not match the downstream analysis.

## Answer Pattern For Users

When giving PeTrack instructions, prefer:

1. Current phase.
2. Required inputs.
3. Exact PeTrack tab/menu/action.
4. Quality check.
5. Saved artifact.
6. Next phase.

This keeps GUI instructions reproducible instead of becoming a loose checklist.
