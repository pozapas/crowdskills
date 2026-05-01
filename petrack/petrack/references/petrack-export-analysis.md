# Export, Batch Processing, And Analysis

Use this reference when preparing PeTrack outputs for downstream analysis or
processing many videos.

## Trajectory Export Formats

| Format | Use | Notes |
| --- | --- | --- |
| `.trc` | PeTrack working file | Contains full PeTrack trajectory information. Use for re-import and correction progress. |
| `.txt` | External analysis | Space-separated trajectory rows with comment header; common analysis export. |
| `.h5` | Metadata-rich analysis | Useful when downstream tools support PeTrack HDF5 data. |

`.trc` is not intended as a stable external analysis format. Export `.txt` or
HDF5 after correction is complete.

## TXT Export Shape

A typical `.txt` export starts with comment lines beginning with `#`, followed
by rows like:

```text
id frame x/m y/m z/m
1 0 13.7271 1.0280 1.58
1 1 13.7288 1.0345 1.58
```

Depending on export options, additional fields may be present. The first five
fields should still identify person ID, frame, x, y, and z.

Use `scripts/validate_txt_export.py` to check parseability, duplicate id-frame
pairs, monotonic frame order, finite coordinates, and basic metadata.

## Export Options

| Option | Use carefully because |
| --- | --- |
| insert missing frames | Detects and interpolates dropped frames, but is computationally expensive. |
| recalculate height | Relevant for stereo projects. |
| alternate height | Needed when z changes over time, e.g. stairs or stereo height data. |
| eliminate points/trajectories without height | Can discard data; keep logs. |
| smooth | Changes trajectories in place; repeated exports can smooth repeatedly. |
| add head direction | Useful with code markers when orientation is meaningful. |
| add marker ID | Links trajectories to code marker IDs and external participant metadata. |
| use meter | Recommended for most downstream analysis. |
| add comment | Exports pedestrian comments when documented during correction. |

## Video And View Export

Use view exports for documentation, presentations, and QA:

| Export | Contains overlays? |
| --- | --- |
| Export Video/Image/Sequence | No overlays; undistortion and border applied. |
| Export View Video/Image/Sequence | Includes current PeTrack visualizations. |

For publication-quality screenshots, export the view rather than taking a
screen capture.

## Batch Processing

For repeated videos with the same calibration and similar recognition/tracking
settings:

1. Build a template `.pet` project with calibration and tuned settings.
2. Open a new sequence with `File > Open Sequence`.
3. Run `calculate all`.
4. Export a video-specific `.trc`.
5. Save a video-specific `.pet`.
6. Manually review and correct each result.

CLI example pattern:

```powershell
petrack.exe -project template.pet -sequence exp4.mp4 -autoTrack exp4_trajectories -autoSave exp4.pet
```

Run `petrack -help` for the local executable's exact options.

## Downstream Analysis

Before passing exported trajectories to PedPy, statistical analysis, or custom
scripts:

- Confirm units are meters if the downstream tool expects meters.
- Confirm frame rate and frame numbering.
- Decide whether z is height or time-varying 3D position.
- Preserve marker IDs if linking questionnaire or sensor metadata.
- Remove or flag non-participant trajectories.
- Keep a correction log and export settings with the data.

## Output Folder Pattern

```text
raw/
calibration/
projects/
working_trc/
exports_txt/
exports_hdf5/
validation/
logs/
```

This separates raw evidence, PeTrack working state, and analysis-ready files.
