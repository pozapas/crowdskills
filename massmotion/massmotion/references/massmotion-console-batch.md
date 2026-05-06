# MassMotionConsole Batch Workflows

MassMotionConsole is the command-line entry point for opening projects, running scripts, running simulations, and exporting query CSVs. It is the preferred layer for reproducible batch runs when the GUI is not needed.

## Core Command Shape

```powershell
& "C:\Program Files\Oasys\MassMotion 11.8\MassMotionConsole.exe" `
  --project "C:\models\station.mm" `
  --scriptfile "C:\scripts\prepare_model.py" `
  --simulation "C:\results\station_seed1001\station_seed1001.mmdb" `
  --seed 1001 `
  --threads 8 `
  --queryall
```

One of `--simulation`, `--scriptobject`, or `--scriptfile` must be provided. If all are used, `--scriptfile` runs first, then `--scriptobject`, then the simulation.

## Useful Arguments

| Argument | Purpose |
| --- | --- |
| `--project path` | open `.mm` or `.mmdb` project/database |
| `--simulation path` | run simulation and write result `.mmdb` |
| `--scriptfile path` | run a Python file before simulation |
| `--scriptobject name` | run a named script object inside the project |
| `--query name` | execute named query and export CSV |
| `--queryall` | export all query objects |
| `--seed integer` | override project random seed |
| `--threads integer` | choose thread count |
| `--nothreads` | disable threading |
| `--popscale number` | scale generated agent population |
| `--csvseparator char` | choose CSV separator |
| `--csvmicrosoft` | write Excel-friendly UTF-8 BOM CSVs |
| `--dump` | write diagnostic debug output |
| `--vis` | show 3D view, slower |
| `--verbosity level` | choose output verbosity |

## Return Codes

| Code | Meaning |
| ---: | --- |
| 0 | success |
| 101 | project file not found or not openable |
| 103 | nothing to do |
| 104 | simulation could not initialize or start |
| 105 | script object or script file not found/openable |
| 106 | imported script object not found |
| 107 | script executed but returned an error |
| 108 | internal scripting error |
| 109 | script reentry |

Always inspect the generated log file next to the `.mmdb` when return code is nonzero.

## Batch Rules

| Rule | Reason |
| --- | --- |
| one result folder per run | prevents overwritten logs/CSV files |
| include seed in run id | reproducibility |
| record full command | debugging and audit |
| capture return code | console failure signal |
| run scripts before simulation | console execution order |
| use `--queryall` only when query names are stable | avoids unexpected output clutter |
| avoid `--vis` in performance batches | viewer slows execution |

## Recommended Manifest Columns

| Column | Meaning |
| --- | --- |
| `run_id` | unique scenario/seed id |
| `project_path` | source `.mm` or `.mmdb` |
| `console_path` | `MassMotionConsole.exe` |
| `simulation_path` | target `.mmdb` |
| `scriptfile_path` | optional pre-run Python script |
| `scriptobject` | optional project script object |
| `seed` | random seed |
| `threads` | requested thread count |
| `popscale` | population multiplier |
| `query_names` | pipe-separated query names or `ALL` |
| `output_dir` | directory for run artifacts |
