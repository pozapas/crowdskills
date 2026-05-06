# Viswalk-COM Scripted Utilities

The skill includes small Python utilities. They are deterministic aids for agents and users, not replacements for reviewing the network in Vissim.

## `index_com_chm.py`

Purpose: decompile and index the compiled Vissim COM manual.

Usage:

```powershell
python .\viswalk-com\viswalk-com\scripts\index_com_chm.py ".\Manuals\Viswalk\Vissim 2025 - COM.chm" --query Pedestrian --query Route --out com_routes.json
```

Outputs:

| Output | Meaning |
| --- | --- |
| console table | matching topic names and summaries |
| `--out file.json` | full topic records in JSON |
| `--csv file.csv` | compact topic records in CSV |

Use `--extract-dir` to control where the HTML topics are written. If the input is already an extracted folder, the script indexes it directly.
Use `--body-search` for slower full-page searches when filename matching is not enough.

## `create_viswalk_run_matrix.py`

Purpose: create a reproducible manifest for seed and factor sweeps.

Usage:

```powershell
python .\viswalk-com\viswalk-com\scripts\create_viswalk_run_matrix.py --scenario station --network model.inpx --layout model.layx --seeds 1001,1002 --ped-volumes 800,1000 --speed-factors 0.9,1.0 --out manifests\station.csv --force
```

The script does not run Vissim. It creates a CSV that the batch template can consume.

## `validate_viswalk_com_script.py`

Purpose: catch common static mistakes before launching Vissim.

Usage:

```powershell
python .\viswalk-com\viswalk-com\scripts\validate_viswalk_com_script.py run_viswalk.py --require-viswalk --json
```

Checks include syntax, COM import, Vissim dispatch, `AttValue`/`SetAttValue` use, simulation run methods, Viswalk-specific object paths, hard-coded risky paths, and missing cleanup patterns.

Static validation cannot know whether object keys exist in a user's `.inpx`. Always combine it with runtime inspection.
