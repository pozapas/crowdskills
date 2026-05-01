# Scripted Utilities

Use these scripts for deterministic checks and file preparation around PeTrack.

## `scripts/create_3dc_points.py`

Create a PeTrack `.3dc` extrinsic calibration point file from a CSV table.

Input CSV example:

```csv
label,x_cm,y_cm,z_cm
A0,0,0,0
A1,200,0,0
A2,0,200,0
P0,0,0,200
```

Command:

```powershell
python petrack/petrack/scripts/create_3dc_points.py calibration_points.csv points.3dc
```

Behavior:

- Accepts columns `x_cm,y_cm,z_cm` or `x,y,z`.
- Writes first line as point count.
- Writes one coordinate row per input row.
- Validates finite numeric coordinates.
- Does not write labels or comments into the `.3dc` file, because PeTrack
  expects coordinate rows.

## `scripts/validate_txt_export.py`

Validate a PeTrack `.txt` trajectory export.

```powershell
python petrack/petrack/scripts/validate_txt_export.py exports/run01.txt --csv validation.csv
```

Checks:

- file exists and is non-empty
- data rows have at least `id frame x y z`
- first five fields are parseable
- coordinates are finite
- duplicate `(id, frame)` pairs are absent
- frames are monotonic within each id
- optional coordinate bounds
- optional minimum number of agents and rows

Useful options:

| Option | Purpose |
| --- | --- |
| `--json` | Print machine-readable reports. |
| `--csv path` | Write one report row per input file. |
| `--min-agents N` | Fail if fewer than N unique IDs are present. |
| `--min-rows N` | Fail if fewer than N trajectory rows are present. |
| `--bounds xmin xmax ymin ymax` | Fail points outside expected world bounds. |
| `--allow-frame-gaps` | Do not warn about frame gaps within a trajectory. |

## Recommended Use

1. Use `create_3dc_points.py` before extrinsic calibration when measured
   coordinates are stored in spreadsheets or CSV.
2. Use PeTrack GUI for calibration, recognition, tracking, and correction.
3. Export `.txt` or HDF5 after correction.
4. Run `validate_txt_export.py` before downstream analysis.
5. Store validation output beside the final export and processing log.
