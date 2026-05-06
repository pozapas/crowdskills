# MassMotion Skill

MassMotion is an Oasys pedestrian simulation platform with GUI authoring, an internal Python scripting environment, a companion standalone Python SDK, command-line execution through `MassMotionConsole.exe`, and simulation result databases in `.mmdb` format. This folder provides a Codex-ready skill for helping agents plan MassMotion models, write Python SDK scripts, run console batches, and validate/analyze outputs.

## Folder Layout

```text
massmotion/
|-- README.md
`-- massmotion/
    |-- SKILL.md
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    |   `-- templates/
    |       |-- massmotion_console_batch_template.py
    |       |-- massmotion_query_analysis_template.py
    |       |-- massmotion_script_object_template.py
    |       `-- massmotion_sdk_simulation_template.py
    |-- references/
    |   |-- massmotion-console-batch.md
    |   |-- massmotion-feature-map.md
    |   |-- massmotion-modeling-workflows.md
    |   |-- massmotion-output-analysis.md
    |   |-- massmotion-pitfalls.md
    |   `-- massmotion-python-sdk.md
    `-- scripts/
        |-- create_massmotion_console_manifest.py
        `-- validate_massmotion_outputs.py
```

## What The Skill Covers

| Area | Coverage |
| --- | --- |
| Feature routing | modeling, SDK, script-object, console, and output-analysis capability map |
| GUI modeling workflow | scene authoring, imported geometry, agents, journeys, events, simulation, analysis |
| Python SDK | `massmotion_11_0`, SDK init/fini, project authoring, simulation stepping, queries, mmdb access |
| Internal scripts | script objects, project access, script sharing, third-party module paths |
| Console automation | `MassMotionConsole.exe`, scripts, simulations, seeds, threads, queries, return codes |
| Output validation | `.mmdb` SQLite checks, logs, query CSVs, agent position exports |
| Research quality | random seed control, run manifests, query provenance, output interpretation |

## Installation

Current [OpenAI Codex Agent Skills docs](https://developers.openai.com/codex/skills) use `.agents/skills` for user and repository-scoped skills. Clone the CrowdSkill repository first and run commands from its root; relative paths such as `.\massmotion\massmotion` only work after `Set-Location crowdskills`. The installer replaces the selected destination skill folder when it already exists, which avoids nested copies and stale files.

```powershell
git clone https://github.com/pozapas/crowdskills.git
Set-Location crowdskills
.\scripts\install-crowdskill.ps1 -Skill massmotion
```

Project-scoped install into another repository:

```powershell
.\scripts\install-crowdskill.ps1 -Skill massmotion -ProjectRoot "D:\path\to\your\project"
```

Manual source path: `.\massmotion\massmotion`

Default user destination: `$HOME\.agents\skills\massmotion`

Other agents that support the Agent Skills folder format can use the same source folder: copy the directory containing `SKILL.md` to that agent's configured skills path.

If the skill does not appear in `/skills` or when typing `$massmotion`, restart Codex.

## Quickstart

```text
Use $massmotion to write a Python SDK script that opens a .mm project, runs a simulation, and evaluates agent summary metrics.
```

```text
Use $massmotion to create a MassMotionConsole batch manifest for three seeds and export all table queries.
```

```text
Use $massmotion to validate mmdb files, logs, and query CSV output from a MassMotion batch.
```

## Scripted Utilities

Create a console run manifest:

```powershell
python .\massmotion\massmotion\scripts\create_massmotion_console_manifest.py --projects .\models\station.mm --seeds 1001,1002,1003 --queryall --out manifests\massmotion_runs.csv --force
```

Validate output folders:

```powershell
python .\massmotion\massmotion\scripts\validate_massmotion_outputs.py .\results\station_seed1001 --require-mmdb --require-log --require-query-csv
```

## Design Philosophy

The skill separates MassMotion GUI modeling, internal script objects, standalone Python SDK workflows, and command-line console automation. It treats the `.mmdb` result database as the main reproducible evidence source and keeps the skill focused on software features, scripts, validation, and analysis.
