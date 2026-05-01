# Scripted Utilities

Use these scripts when the task benefits from deterministic validation or
repeatable experiment bookkeeping.

## `scripts/create_experiment_matrix.py`

Create a manifest CSV for parameter sweeps and model comparisons.

```powershell
python jupedsim/jupedsim/scripts/create_experiment_matrix.py `
  --scenario bottleneck `
  --models csm,csm_v2,avm `
  --seeds 1001,1002,1003,1004,1005 `
  --agents 80,120 `
  --desired-speeds 1.1,1.3 `
  --factor width=0.8,1.0,1.2 `
  --out manifests/bottleneck.csv `
  --force
```

Important behavior:

- Does not run JuPedSim.
- Produces one row per Cartesian-product combination.
- Adds deterministic `run_id` and `output_file` fields.
- Supports extra factors with `--factor name=value1,value2`.
- Use `--json` when another tool needs a machine-readable result.

Use this before writing a sweep script so the run plan is visible and reviewable.

## `scripts/validate_sqlite_recording.py`

Validate one or more JuPedSim SQLite recordings and summarize their contents.

```powershell
python jupedsim/jupedsim/scripts/validate_sqlite_recording.py outputs/*.sqlite `
  --min-frames 2 `
  --csv validation.csv
```

Useful options:

| Option | Purpose |
| --- | --- |
| `--json` | Print full machine-readable reports. |
| `--csv path` | Write one summary row per recording. |
| `--min-frames N` | Fail recordings with fewer than N `frame_data` rows. |
| `--max-final-agents N` | Fail if the last recorded frame has more than N agents. |
| `--allow-empty` | Permit recordings with no trajectory rows. |
| `--strict` | Convert warnings into failures. |

The validator checks:

- required tables and columns
- metadata version and fps
- frame count and trajectory row count
- geometry hash references
- trajectory frames present in `frame_data`
- finite sampled position/orientation values
- first and last recorded agent counts

## Recommended Agent Workflow

1. Generate or inspect a manifest with `create_experiment_matrix.py`.
2. Run the JuPedSim scripts that produce SQLite files.
3. Validate all recordings with `validate_sqlite_recording.py`.
4. Use failed rows to debug geometry, routing, termination, or writer closure.
5. Compute metrics only after validation passes.

## Exit Codes

| Script | Code | Meaning |
| --- | --- | --- |
| both | `0` | Success. |
| both | `1` | Validation, filesystem, or run-plan failure. |
| both | `2` | Command-line usage error from `argparse`. |
