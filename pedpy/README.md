# PedPy Skill

PedPy is a Python toolkit for pedestrian trajectory analysis. This folder packages a Codex-ready PedPy skill that helps an agent load trajectories, define measurement geometry, validate data, compute metrics, generate plots, and export reproducible outputs without bundling the original manuals.

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

The installable skill folder is `pedpy/pedpy/`. The README you are reading is repo-facing documentation for humans browsing GitHub.

## Why This Skill Exists

Pedestrian trajectory analysis is easy to get subtly wrong. Frame rates, coordinate units, measurement geometry, border windows, Voronoi clipping, and line-crossing definitions all affect the final interpretation. This skill gives Codex a compact, tool-specific operating guide so it can write PedPy analyses that are transparent and auditable.

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

## Install Into Codex

Copy or symlink the installable folder:

```powershell
Copy-Item -Recurse ".\pedpy\pedpy" "$env:USERPROFILE\.codex\skills\pedpy"
```

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

## Manual Policy

The source manuals are intentionally not part of this GitHub-ready folder. In this workspace they live under:

```text
Manuals/pedpy/
```

The repo `.gitignore` excludes `Manuals/` so PDFs, generated HTML documentation, notebooks, and sample data stay outside version control. The skill contains only distilled workflow guidance, API navigation, pitfalls, and a generic template.

## Design Notes

The skill follows progressive disclosure:

- `SKILL.md` gives the high-level workflow and method selection.
- `references/pedpy-api-map.md` maps common analysis requests to PedPy classes and functions.
- `references/pedpy-workflows.md` provides reusable code recipes.
- `references/pedpy-pitfalls.md` captures the assumptions and checks that usually decide whether results are trustworthy.
- `assets/templates/pedpy_analysis_template.py` gives Codex a starter script to adapt when the user wants a full analysis file.

This keeps the agent fast on common tasks while still giving it enough depth for advanced pedestrian simulation analysis.
