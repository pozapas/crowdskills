# Viswalk-COM Skill

Viswalk-COM helps agents write Python automation for PTV Vissim/Viswalk pedestrian simulation through the COM interface. This folder provides a Codex-ready skill with compact API routing, Python patterns, CHM extraction support, templates, and validation utilities.

## Folder Layout

```text
viswalk-com/
|-- README.md
`-- viswalk-com/
    |-- SKILL.md
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    |   `-- templates/
    |       |-- viswalk_com_automation_template.py
    |       `-- viswalk_com_batch_template.py
    |-- references/
    |   |-- viswalk-com-api-map.md
    |   |-- viswalk-com-chm-workflow.md
    |   |-- viswalk-com-experiment-workflows.md
    |   |-- viswalk-com-pedestrian-network.md
    |   |-- viswalk-com-pitfalls.md
    |   |-- viswalk-com-python-patterns.md
    |   |-- viswalk-com-routing-evaluation.md
    |   `-- viswalk-com-scripted-utilities.md
    `-- scripts/
        |-- create_viswalk_run_matrix.py
        |-- index_com_chm.py
        `-- validate_viswalk_com_script.py
```

## What The Skill Covers

| Area | Coverage |
| --- | --- |
| COM access | `win32com.client`, Vissim ProgID selection, loading `.inpx/.layx`, GUI control |
| CHM manual format | `hh.exe -decompile`, extracted HTML topic indexing, queryable COM topic inventories |
| Pedestrian network objects | areas, ramps/stairs, obstacles, levels, pedestrian types/classes/compositions |
| Demand | pedestrian inputs, time-interval volumes, desired speed distributions, compositions |
| Routing | static routes, partial routes, route locations, route choice areas, destinations |
| Runtime control | seeds, simulation period, breakpoints, single-step and continuous runs |
| Evaluation | area measurements, travel time measurements, pedestrian records, network performance |
| Automation quality | batch run manifests, static script checks, reproducibility and failure handling |

## Installation

### Install Into Codex

<details>
<summary>Show install commands</summary>

Personal install:

```powershell
Copy-Item -Recurse ".\viswalk-com\viswalk-com" "$env:USERPROFILE\.codex\skills\viswalk-com"
```

Project-scoped install:

```powershell
Copy-Item -Recurse ".\viswalk-com\viswalk-com" ".\.codex\skills\viswalk-com"
```

</details>

### Install Into Claude Code

<details>
<summary>Show install commands</summary>

Personal install:

```powershell
Copy-Item -Recurse ".\viswalk-com\viswalk-com" "$env:USERPROFILE\.claude\skills\viswalk-com"
```

Project-scoped install:

```powershell
Copy-Item -Recurse ".\viswalk-com\viswalk-com" ".\.claude\skills\viswalk-com"
```

</details>

### Install Into Cursor

<details>
<summary>Show install commands</summary>

Personal install:

```powershell
Copy-Item -Recurse ".\viswalk-com\viswalk-com" "$env:USERPROFILE\.cursor\skills\viswalk-com"
```

Alternative personal path:

```powershell
Copy-Item -Recurse ".\viswalk-com\viswalk-com" "$env:USERPROFILE\.agents\skills\viswalk-com"
```

Project-scoped install:

```powershell
Copy-Item -Recurse ".\viswalk-com\viswalk-com" ".\.cursor\skills\viswalk-com"
```

</details>

## Quickstart

```text
Use $viswalk-com to write a Python script that loads a Viswalk network, changes pedestrian input volumes, runs paired seeds, and exports travel time metrics.
```

```text
Use $viswalk-com to create a small pedestrian network with areas, an obstacle, static pedestrian routes, and area measurements through Vissim COM.
```

```text
Use $viswalk-com to index "Manuals\Viswalk\Vissim 2025 - COM.chm" and find the COM methods for pedestrian routes and areas.
```

## Scripted Utilities

Index the compiled COM help:

```powershell
python .\viswalk-com\viswalk-com\scripts\index_com_chm.py ".\Manuals\Viswalk\Vissim 2025 - COM.chm" --query Pedestrian --query Area --out com_index.json
```

Create a batch-run manifest:

```powershell
python .\viswalk-com\viswalk-com\scripts\create_viswalk_run_matrix.py --scenario station_test --network model.inpx --seeds 1001,1002,1003 --ped-volumes 800,1000,1200 --out manifests\station_test.csv --force
```

Validate a Python COM script before running Vissim:

```powershell
python .\viswalk-com\viswalk-com\scripts\validate_viswalk_com_script.py scripts\run_viswalk.py --require-viswalk
```

## Design Philosophy

The skill is Python-first and manual-grounded. It does not copy the full CHM contents into the repository. Instead, it teaches agents how to extract and index the compiled help locally, then routes common Viswalk coding tasks through compact references and reusable Python automation patterns.
