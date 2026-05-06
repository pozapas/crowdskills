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
    |-- scripts/
    |   |-- create_experiment_matrix.py
    |   `-- validate_sqlite_recording.py
    `-- references/
        |-- jupedsim-api-map.md
        |-- jupedsim-calibration-uncertainty.md
        |-- jupedsim-experimental-design.md
        |-- jupedsim-geometry-routing.md
        |-- jupedsim-model-selection.md
        |-- jupedsim-pitfalls.md
        |-- jupedsim-research-workflows.md
        |-- jupedsim-scripted-utilities.md
        `-- jupedsim-validation-analysis.md
```

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
| Experiment design | hypotheses, validity threats, DOE, replication, uncertainty |
| Validation | geometry, placement, routing, run completion, SQLite recording audits |
| Automation | manifest creation and recording validation scripts |

## Installation

Current [OpenAI Codex Agent Skills docs](https://developers.openai.com/codex/skills) use `.agents/skills` for user and repository-scoped skills. Clone the CrowdSkill repository first and run commands from its root; relative paths such as `.\jupedsim\jupedsim` only work after `Set-Location crowdskills`. The installer replaces the selected destination skill folder when it already exists, which avoids nested copies and stale files.

```powershell
git clone https://github.com/pozapas/crowdskills.git
Set-Location crowdskills
.\scripts\install-crowdskill.ps1 -Skill jupedsim
```

Project-scoped install into another repository:

```powershell
.\scripts\install-crowdskill.ps1 -Skill jupedsim -ProjectRoot "D:\path\to\your\project"
```

Manual source path: `.\jupedsim\jupedsim`

Default user destination: `$HOME\.agents\skills\jupedsim`

Other agents that support the Agent Skills folder format can use the same source folder: copy the directory containing `SKILL.md` to that agent's configured skills path.

If the skill does not appear in `/skills` or when typing `$jupedsim`, restart Codex.

## Quickstart

```text
Use $jupedsim to design a bottleneck capacity experiment with a parameter sweep over width and desired speed.
```

```text
Use $jupedsim to compare CSM, AVM, and Social Force on the same corridor evacuation geometry.
```

```text
Build a JuPedSim simulation with queues, waiting sets, and PedPy postprocessing for density and flow.
```

```text
Use $jupedsim to create an experiment plan for bottleneck capacity with uncertainty analysis and a manifest.
```

## Scripted Utilities

Create a run manifest:

```powershell
python .\jupedsim\jupedsim\scripts\create_experiment_matrix.py --scenario bottleneck --models csm,csm_v2,avm --seeds 1001,1002,1003 --factor width=0.8,1.0,1.2 --out manifests\bottleneck.csv --force
```

Validate JuPedSim SQLite outputs:

```powershell
python .\jupedsim\jupedsim\scripts\validate_sqlite_recording.py outputs\*.sqlite --csv validation.csv
```

## Design Philosophy

The skill is intentionally research-oriented. A high-quality JuPedSim answer should not only produce executable code; it should also make the hypothesis, model assumptions, geometry choices, routing logic, stochastic seeds, output interval, validation checks, uncertainty, and postprocessing metrics visible.
