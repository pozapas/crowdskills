# PedPy Skill

PedPy is a Python toolkit for pedestrian trajectory analysis. This folder packages an AI agent-ready PedPy skill that helps an agent load trajectories, define measurement geometry, validate data, compute metrics, generate plots, and export reproducible outputs without bundling the original manuals.

## What Is Included

```text
pedpy/
|-- README.md
`-- pedpy/
    |-- SKILL.md
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    |   `-- templates/
    |       `-- pedpy_analysis_template.py
    `-- references/
        |-- pedpy-api-map.md
        |-- pedpy-pitfalls.md
        `-- pedpy-workflows.md
```

## Why This Skill Exists

Pedestrian trajectory analysis is easy to get subtly wrong. Frame rates, coordinate units, measurement geometry, border windows, Voronoi clipping, and line-crossing definitions all affect the final interpretation. This skill gives AI agent a compact, tool-specific operating guide so it can write PedPy analyses that are transparent and auditable.

## Capability Map

| Analysis need | PedPy support captured in the skill |
| --- | --- |
| Load trajectory data | DataFrame, text, HDF5, Vadere, Viswalk, Pathfinder, Crowd:it, JuPedSim |
| Build geometry | `WalkableArea`, `MeasurementArea`, `AxisAlignedMeasurementArea`, `MeasurementLine` |
| Validate trajectories | Check points against walkable areas and export invalid rows |
| Density | Classic, Voronoi, passing, and line density |
| Speed | Individual, mean, Voronoi, passing, and line speed |
| Flow | N-t curves, bottleneck flow, line flow |
| Acceleration | Individual, mean, and Voronoi acceleration |
| Spatial behavior | Neighborhoods, neighbor distance, time-distance to line, pair-distribution function |
| Profiles | Density and speed profiles on grid cells with performance guidance |
| Visualization | Measurement setup, trajectories, density, speed, flow, Voronoi cells, profiles |

## Installation

### Install Into Codex

<details>
<summary>Show install commands</summary>

Codex supports personal and project skill directories.

Personal install (all projects):

```powershell
Copy-Item -Recurse ".\pedpy\pedpy" "$env:USERPROFILE\.codex\skills\pedpy"
```

Project-scoped install (current repo only):

```powershell
Copy-Item -Recurse ".\pedpy\pedpy" ".\.codex\skills\pedpy"
```

</details>

### Install Into Claude Code

<details>
<summary>Show install commands</summary>

Claude Code loads skills from personal and project directories.

Personal install (all projects):

```powershell
Copy-Item -Recurse ".\pedpy\pedpy" "$env:USERPROFILE\.claude\skills\pedpy"
```

Project-scoped install (current repo only):

```powershell
Copy-Item -Recurse ".\pedpy\pedpy" ".\.claude\skills\pedpy"
```

</details>

### Install Into Cursor

<details>
<summary>Show install commands</summary>

Cursor supports multiple skill directories.

Personal install (all projects):

```powershell
Copy-Item -Recurse ".\pedpy\pedpy" "$env:USERPROFILE\.cursor\skills\pedpy"
```

Alternative personal path (also supported):

```powershell
Copy-Item -Recurse ".\pedpy\pedpy" "$env:USERPROFILE\.agents\skills\pedpy"
```

Project-scoped install (current repo only):

```powershell
Copy-Item -Recurse ".\pedpy\pedpy" ".\.cursor\skills\pedpy"
```

</details>

## Quickstart

After installation, prompts such as these should trigger the skill:

```text
Use $pedpy to analyze this Vadere bottleneck trajectory and compute flow and density.
```

```text
Build a PedPy notebook that loads a Pathfinder CSV, validates the walkable area, and plots Voronoi density.
```

```text
I need a fundamental diagram at this measurement line from pedestrian trajectory data.
```

## Design Notes

The skill follows progressive disclosure:

- `SKILL.md` gives the high-level workflow and method selection.
- `references/pedpy-api-map.md` maps common analysis requests to PedPy classes and functions.
- `references/pedpy-workflows.md` provides reusable code recipes.
- `references/pedpy-pitfalls.md` captures the assumptions and checks that usually decide whether results are trustworthy.
- `assets/templates/pedpy_analysis_template.py` gives AI agent a starter script to adapt when the user wants a full analysis file.

This keeps the agent fast on common tasks while still giving it enough depth for pedestrian simulation analysis.
