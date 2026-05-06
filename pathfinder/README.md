# Pathfinder Skill

Pathfinder is a GUI-centered pedestrian movement and egress simulator with command-line simulation support, CSV/JSON output files, Monte Carlo workflows, and an experimental in-simulator JavaScript API. This folder provides a Codex-ready skill for helping agents plan models, run simulations, write Pathfinder scripts, and analyze outputs from the online Pathfinder 2026.1 documentation.

## Folder Layout

```text
pathfinder/
|-- README.md
`-- pathfinder/
    |-- SKILL.md
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    |   `-- templates/
    |       |-- pathfinder_batch_runner_template.py
    |       |-- pathfinder_output_analysis_template.py
    |       `-- pathfinder_script_api_template.js
    |-- references/
    |   |-- pathfinder-docs-map.md
    |   |-- pathfinder-modeling-workflows.md
    |   |-- pathfinder-output-analysis.md
    |   |-- pathfinder-pitfalls.md
    |   |-- pathfinder-scripting-api.md
    |   `-- pathfinder-simulation-batch.md
    `-- scripts/
        |-- crawl_pathfinder_docs.py
        |-- create_pathfinder_run_manifest.py
        `-- validate_pathfinder_outputs.py
```

## What The Skill Covers

| Area | Coverage |
| --- | --- |
| Online manual ingestion | crawl and index versioned Pathfinder HTML docs |
| Modeling workflow | geometry, profiles, behaviors, occupants, queues, targets, triggers |
| Simulation execution | GUI run workflow, `testsim.bat`, exported scenarios, Monte Carlo variations |
| Native scripting | Pathfinder experimental JavaScript API and simulation callbacks |
| Python workflows | docs indexing, batch orchestration, output validation, CSV/JSON analysis |
| Output analysis | summary reports, occupant history, room/door/measurement output, Monte Carlo results |
| Research quality | assumptions, validity limits, reproducibility, sensitivity, postprocessing |

## Installation

### Install Into Codex

<details>
<summary>Show install commands</summary>

Personal install:

```powershell
Copy-Item -Recurse ".\pathfinder\pathfinder" "$env:USERPROFILE\.codex\skills\pathfinder"
```

Project-scoped install:

```powershell
Copy-Item -Recurse ".\pathfinder\pathfinder" ".\.codex\skills\pathfinder"
```

</details>

### Install Into Claude Code

<details>
<summary>Show install commands</summary>

Personal install:

```powershell
Copy-Item -Recurse ".\pathfinder\pathfinder" "$env:USERPROFILE\.claude\skills\pathfinder"
```

Project-scoped install:

```powershell
Copy-Item -Recurse ".\pathfinder\pathfinder" ".\.claude\skills\pathfinder"
```

</details>

### Install Into Cursor

<details>
<summary>Show install commands</summary>

Personal install:

```powershell
Copy-Item -Recurse ".\pathfinder\pathfinder" "$env:USERPROFILE\.cursor\skills\pathfinder"
```

Alternative personal path:

```powershell
Copy-Item -Recurse ".\pathfinder\pathfinder" "$env:USERPROFILE\.agents\skills\pathfinder"
```

Project-scoped install:

```powershell
Copy-Item -Recurse ".\pathfinder\pathfinder" ".\.cursor\skills\pathfinder"
```

</details>

## Quickstart

```text
Use $pathfinder to plan a Pathfinder egress model, define output metrics, and prepare a Python analysis workflow.
```

```text
Use $pathfinder to crawl the Pathfinder 2026.1 online docs and find pages about occupant history and command-line simulation.
```

```text
Use $pathfinder to write a JavaScript custom script that closes doors based on a measurement region count.
```

```text
Use $pathfinder to create a command-line run manifest and validate Pathfinder output CSV files.
```

## Scripted Utilities

Index online Pathfinder docs:

```powershell
python .\pathfinder\pathfinder\scripts\crawl_pathfinder_docs.py --start https://www.thunderheadeng.com/docs/2026-1/pathfinder/introduction/ --out docs_index.json --max-pages 80
```

Create a run manifest:

```powershell
python .\pathfinder\pathfinder\scripts\create_pathfinder_run_manifest.py --models .\models\case1.pth,.\models\case2.pth --testsim "C:\Program Files\Pathfinder 2026\testsim.bat" --out manifests\pathfinder_runs.csv --force
```

Validate output files:

```powershell
python .\pathfinder\pathfinder\scripts\validate_pathfinder_outputs.py .\results\case1 --require occupants_detailed.csv --require-summary
```

## Design Philosophy

The skill separates three roles: Pathfinder GUI/modeling guidance, Pathfinder's native JavaScript simulation scripting, and Python automation around docs, command-line runs, and output analysis. It does not pretend that Pathfinder exposes the same Python COM interface as Vissim/Viswalk.
