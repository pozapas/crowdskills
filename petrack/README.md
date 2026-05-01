# PeTrack Skill

PeTrack extracts pedestrian trajectories from videos through calibration,
recognition, tracking, correction, and export. This folder provides an AI agent-ready skill for helping an agent guide PeTrack workflows and validate
trajectory outputs without copying the PeTrack manuals into the repository.

## Folder Layout

```text
petrack/
|-- README.md
`-- petrack/
    |-- SKILL.md
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    |   `-- templates/
    |       |-- petrack_correction_checklist_template.md
    |       `-- petrack_processing_log_template.md
    |-- references/
    |   |-- petrack-calibration.md
    |   |-- petrack-export-analysis.md
    |   |-- petrack-pitfalls.md
    |   |-- petrack-planning-quality.md
    |   |-- petrack-recognition-tracking.md
    |   |-- petrack-scripted-utilities.md
    |   `-- petrack-workflow-map.md
    `-- scripts/
        |-- create_3dc_points.py
        `-- validate_txt_export.py
```

## What The Skill Covers

| Area | Coverage |
| --- | --- |
| Experiment planning | camera placement, lighting, markers, synchronization, data preparation |
| Calibration | intrinsic calibration, extrinsic calibration, `.3dc` point files |
| Recognition | multicolor markers, code markers, machine-learning markers, ROI setup |
| Tracking | tracking ROI, search settings, Kalman/extrapolation options, batch tracking |
| Correction | person-by-person review, correction-tab tests, split/merge/delete operations |
| Export | `.trc`, `.txt`, HDF5, video/view export, marker IDs, head direction |
| Validation | trajectory export checks, point-file creation, reproducibility notes |

## Installation

### Install Into Codex

<details>
<summary>Show install commands</summary>

Codex supports personal and project skill directories.

Personal install (all projects):

```powershell
Copy-Item -Recurse ".\petrack\petrack" "$env:USERPROFILE\.codex\skills\petrack"
```

Project-scoped install (current repo only):

```powershell
Copy-Item -Recurse ".\petrack\petrack" ".\.codex\skills\petrack"
```

</details>

### Install Into Claude Code

<details>
<summary>Show install commands</summary>

Claude Code loads skills from personal and project directories.

Personal install (all projects):

```powershell
Copy-Item -Recurse ".\petrack\petrack" "$env:USERPROFILE\.claude\skills\petrack"
```

Project-scoped install (current repo only):

```powershell
Copy-Item -Recurse ".\petrack\petrack" ".\.claude\skills\petrack"
```

</details>

### Install Into Cursor

<details>
<summary>Show install commands</summary>

Cursor supports multiple skill directories.

Personal install (all projects):

```powershell
Copy-Item -Recurse ".\petrack\petrack" "$env:USERPROFILE\.cursor\skills\petrack"
```

Alternative personal path (also supported):

```powershell
Copy-Item -Recurse ".\petrack\petrack" "$env:USERPROFILE\.agents\skills\petrack"
```

Project-scoped install (current repo only):

```powershell
Copy-Item -Recurse ".\petrack\petrack" ".\.cursor\skills\petrack"
```

</details>

Example prompts:

```text
Use $petrack to plan the full workflow for extracting trajectories from an overhead camera video with multicolor hats.
```

```text
Use $petrack to prepare an extrinsic calibration .3dc file and explain how to click the points in PeTrack.
```

```text
Use $petrack to diagnose why my exported trajectories have duplicate tracks and missing IDs.
```

## Scripted Utilities

Create a `.3dc` extrinsic calibration point file:

```powershell
python .\petrack\petrack\scripts\create_3dc_points.py calibration_points.csv points.3dc
```

Validate a PeTrack `.txt` export:

```powershell
python .\petrack\petrack\scripts\validate_txt_export.py exports\run01.txt --csv validation\run01_validation.csv
```
