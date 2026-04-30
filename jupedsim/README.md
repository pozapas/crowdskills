# JuPedSim Skill

JuPedSim is a pedestrian dynamics simulation package with a Python interface and C++ core. This folder provides a Codex-ready skill for designing, implementing, validating, and analyzing JuPedSim studies at research depth.

## Folder Layout

```text
jupedsim/
|-- README.md
`-- jupedsim/
    |-- SKILL.md
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    |   `-- templates/
    |       |-- evacuation_scenario_template.py
    |       `-- experiment_matrix_template.py
    `-- references/
        |-- jupedsim-api-map.md
        |-- jupedsim-geometry-routing.md
        |-- jupedsim-model-selection.md
        |-- jupedsim-pitfalls.md
        |-- jupedsim-research-workflows.md
        `-- jupedsim-validation-analysis.md
```

The installable skill folder is `jupedsim/jupedsim/`.

## What The Skill Covers

| Area | Coverage |
| --- | --- |
| Simulation construction | `Simulation`, `dt`, run loops, termination guards, tracing |
| Geometry | Shapely polygons, WKT, holes, obstacles, routability |
| Movement models | CSM, CSM V2, AVM, GCFM, SFM |
| Routing | stages, journeys, fixed/round-robin/least-targeted transitions |
| Crowd management | exits, queues, waiting sets, direct steering |
| Population design | density, number, percentage, ring distributions, seeds |
| Output | SQLite writer, custom writers, recording API |
| Research practice | model comparison, sensitivity analysis, calibration posture |
| Validation | geometry, placement, routing, run completion, reproducibility manifests |

## Install Into Codex

```powershell
Copy-Item -Recurse ".\jupedsim\jupedsim" "$env:USERPROFILE\.codex\skills\jupedsim"
```

Example prompts:

```text
Use $jupedsim to design a bottleneck capacity experiment with a parameter sweep over width and desired speed.
```

```text
Use $jupedsim to compare CSM, AVM, and Social Force on the same corridor evacuation geometry.
```

```text
Build a JuPedSim simulation with queues, waiting sets, and PedPy postprocessing for density and flow.
```

## Manual Policy

The JuPedSim package and documentation supplied for skill creation remain outside this GitHub-ready folder under:

```text
Manuals/JuPedSim/
```

The repo `.gitignore` excludes `Manuals/`. This folder contains distilled guidance, not copied manuals.

## Design Philosophy

The skill is intentionally research-oriented. A high-quality JuPedSim answer should not only produce executable code; it should also make the model assumptions, geometry choices, routing logic, stochastic seeds, output interval, validation checks, and postprocessing metrics visible.

