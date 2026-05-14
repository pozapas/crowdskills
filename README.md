<p align="center">
  <img src="assets/crowdskill-hero.png" alt="CrowdSkill pedestrian simulation skills" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/release-v1.0.0-1a73e8?style=flat-square" alt="release v1.0.0">
  <img src="https://img.shields.io/badge/skills-7%20packages-2d6a4f?style=flat-square" alt="7 skill packages">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-0078d4?style=flat-square" alt="cross-platform">
  <img src="https://img.shields.io/badge/Python-%E2%89%A53.10-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python &ge;3.10">
  <img src="https://img.shields.io/badge/agents-Codex%20%7C%20Claude%20Code%20%7C%20Cursor-e06c1b?style=flat-square" alt="supported agents">
  <img src="https://img.shields.io/badge/license-MIT-22863a?style=flat-square" alt="MIT license">
</p>

# CrowdSkill

CrowdSkill is a structured library of AI-agent skills for pedestrian dynamics research and engineering. It covers the full analytical pipeline: microscopic and mesoscopic simulation, empirical trajectory extraction from video, trajectory-based flow analysis, and egress-safety modeling. Each skill encapsulates a tool's operational surface, its API topology, workflow sequencing, failure modes, output schema, and validation criteria, as agent-executable instructions rather than prose documentation.

> Simulation work is only reproducible when every decision is recoverable: which model family, which parameter set, which seed schedule, which output columns, which measurement geometry, and which benchmark the results are compared against. CrowdSkill makes those decisions explicit at every stage.

## Table of Contents

- [CrowdSkill](#crowdskill)
  - [Table of Contents](#table-of-contents)
  - [Release Notes — Version 1.0](#release-notes--version-10)
  - [Skill Inventory](#skill-inventory)
  - [Design Principles](#design-principles)
  - [Package Structure](#package-structure)
  - [Installation](#installation)
    - [npx (cross-platform)](#npx-cross-platform)
    - [Local installer (explicit path control)](#local-installer-explicit-path-control)
    - [Manual installation](#manual-installation)
  - [Representative Invocations](#representative-invocations)
  - [Workflow Coverage](#workflow-coverage)
    - [Experiment Design](#experiment-design)
    - [Automation and Batch Execution](#automation-and-batch-execution)
    - [Output Validation and Analysis](#output-validation-and-analysis)
  - [Contributing a New Skill](#contributing-a-new-skill)

---

## Release Notes — Version 1.0

_Initial public release &mdash; May 6, 2026_

<p align="center">
  <img src="assets/poster.png" alt="CrowdSkill version one at a glance" width="100%">
</p>

---

## Skill Inventory

| Skill | Tool | Computational Scope |
| --- | --- | --- |
| `jupedsim` | JuPedSim | Microscopic pedestrian simulation: collision-free speed model (CFSM), social force variants, generalized centrifugal force model (GCFM); waypoint routing; geometry and walkable-area construction; SQLite trajectory recording; parametric experiment matrices |
| `pedpy` | PedPy | Trajectory analysis: classical density (Voronoi, arithmetic mean), individual and mean speed profiles, flow through measurement lines and areas, fundamental diagram extraction, spatiotemporal binning |
| `petrack` | PeTrack | Photogrammetric trajectory extraction: stereo and monocular calibration, intrinsic/extrinsic parameter estimation, marker-based and markerless tracking, manual correction workflows, TXT and HDF5 export |
| `viswalk-com` | PTV Viswalk / Vissim | COM automation via `pywin32`: pedestrian input objects, routing decisions, area measurements, data collection, stochastic seed sweeps, COM object lifecycle and error recovery |
| `pathfinder` | Thunderhead Pathfinder | Occupant movement and egress: geometry import and zone definition, simulation profile configuration, headless console execution, JavaScript custom-event scripting, occupant history CSV analysis |
| `massmotion` | Oasys MassMotion | Agent-based crowd simulation: Python SDK scene construction, script-object programming, `MassMotionConsole` headless execution, `.mmdb` database querying, batch CSV result aggregation |
| `evacuationz` | Evacuationz | Egress network modeling: XML/GraphML project audits, scenario configuration, deterministic and stochastic run management, benchmark comparison, structured output summaries |

---

## Design Principles

**Skills encode operational knowledge, not documentation mirrors.**
Vendor manuals describe what a tool does; skills describe how to use it correctly, in sequence, at production quality. Source manuals are excluded from version control by design.

**Reproducibility is a first-class constraint.**
Every workflow that produces a result must also produce a recoverable record: software version, random seed schedule, geometry hash or source reference, parameter manifest, and the specific output columns used in any reported metric.

**Automation is justified by correctness, not convenience.**
Scripts and templates exist to make implicit assumptions explicit and to prevent the category of errors that arise from manual repetition across seeds, scenarios, or parameter sweeps. Automation that does not improve correctness is not added.

**Tool boundaries are respected and maintained.**
Each simulator has a distinct integration model: Viswalk exposes a COM server; MassMotion provides a Python SDK and a headless console binary; JuPedSim is a pure Python library; Pathfinder uses a command-line interface and an embedded JavaScript engine; PeTrack is a GUI application with file-based I/O; PedPy is a trajectory analysis library with no simulation component. Skills do not conflate these boundaries or assume cross-tool interoperability where none exists.

**Interpretation requires evidence.**
A simulation result without an attached output path, metric definition, seed list, and comparison baseline is an unsubstantiated claim. Skills enforce that distinction.

---

## Package Structure

Each skill follows a canonical layout:

```text
tool-name/
|-- README.md
`-- tool-name/
    |-- SKILL.md
    |-- agents/
    |   `-- openai.yaml
    |-- assets/
    |   `-- templates/
    |-- references/
    `-- scripts/
```

| Path | Content and Purpose |
| --- | --- |
| `SKILL.md` | Agent instruction document: workflow sequencing, decision tables, API surface notes, quality gates, failure-mode catalog, and output validation criteria |
| `references/` | Compact domain-specific reference material: modeling theory, API contracts, common pitfalls, measurement geometry definitions, and output schema annotations |
| `scripts/` | Deterministic utility scripts: manifest generators, output validators, index builders, and schema checkers, each with a single, auditable responsibility |
| `assets/templates/` | Reusable starting points: annotated analysis pipelines, batch runner configurations, scenario checklists, and seed-sweep manifests |
| `agents/openai.yaml` | Display metadata for agent UI registration |

---

## Installation

### npx (cross-platform)

Install the full library:

```bash
npx skills add pozapas/crowdskills --full-depth
```

The `--full-depth` flag is required because each skill package is nested one directory below the repository root.

Install a single skill:

```bash
npx skills add pozapas/crowdskills --full-depth --skill viswalk-com
```

Target a specific agent runtime:

```bash
npx skills add pozapas/crowdskills --full-depth -a codex
npx skills add pozapas/crowdskills --full-depth -a claude-code
npx skills add pozapas/crowdskills --full-depth -a cursor
```

### Local installer (explicit path control)

Use the PowerShell installer when the destination directory must be specified or when offline installation is required:

```powershell
git clone https://github.com/pozapas/crowdskills.git
Set-Location crowdskills
.\scripts\install-crowdskill.ps1 -All
```

Install a single skill:

```powershell
.\scripts\install-crowdskill.ps1 -Skill viswalk-com
```

Install into an external project root:

```powershell
.\scripts\install-crowdskill.ps1 -Skill viswalk-com -ProjectRoot "D:\path\to\your\project"
```

### Manual installation

Copy the directory containing `SKILL.md` into the target agent's skills directory:

| Skill | Source path (contains `SKILL.md`) |
| --- | --- |
| `jupedsim` | `.\jupedsim\jupedsim` |
| `pedpy` | `.\pedpy\pedpy` |
| `petrack` | `.\petrack\petrack` |
| `viswalk-com` | `.\viswalk-com\viswalk-com` |
| `pathfinder` | `.\pathfinder\pathfinder` |
| `massmotion` | `.\massmotion\massmotion` |
| `evacuationz` | `.\evacuationz` |

Restart the agent process after installation if the skill is not immediately discoverable.

---

## Representative Invocations

```text
Use $jupedsim to construct a bottleneck evacuation scenario using the collision-free speed model,
record trajectories to SQLite, and run a parameter sweep over door width and desired speed.
```

```text
Use $pedpy to compute Voronoi-based density, individual speed, and specific flow through a
measurement line from this HDF5 trajectory file, and produce a fundamental diagram.
```

```text
Use $viswalk-com to write a Python COM automation script that sweeps pedestrian input volume
across five seeds, exports area measurement time series, and aggregates results into a CSV manifest.
```

```text
Use $massmotion to construct a MassMotionConsole batch manifest for three random seeds,
validate the .mmdb database integrity, log file completeness, and query CSV column schema.
```

```text
Use $pathfinder to prepare a headless console run manifest, execute the simulation,
and parse occupant history and agent count CSVs into a structured result summary.
```

```text
Use $petrack to plan stereo camera calibration, configure marker recognition parameters,
apply manual trajectory corrections, and export final tracks to TXT and HDF5.
```

```text
Use $evacuationz to audit an XML project folder for schema conformance, compare output
behavior against the published benchmark, and produce a structured run summary.
```

---

## Workflow Coverage

### Experiment Design

- Walkable geometry construction and network topology definition
- Route, journey, waypoint, and event sequencing
- Population demand specification and stochastic arrival models
- Random seed schedules and scenario manifests for multi-condition studies
- Model family selection and parameter initialization rationale
- Sensitivity analysis, calibration procedures, and cross-model comparisons

### Automation and Batch Execution

- Python scripting for JuPedSim, PedPy, and the MassMotion Python SDK
- COM automation patterns for Viswalk/Vissim with proper object lifecycle management
- Headless console execution manifests for MassMotion and Pathfinder
- Script-object and JavaScript custom-event templates for simulator-embedded scripting
- Per-run result CSV aggregation with one row per seed, scenario, and parameter configuration

### Output Validation and Analysis

- SQLite trajectory schema and integrity checks
- `.mmdb` database completeness and query provenance
- Required-column validation for all CSV result exports
- Measurement geometry provenance, confirming that measurement areas match the geometry used in the simulation
- Reproducible output directory conventions with version-stamped manifests
- Result interpretation grounded in reported metrics, not qualitative animation review

---

## Contributing a New Skill

1. Create the package root at `tool-name/tool-name/SKILL.md` following the canonical layout.
2. Author `SKILL.md` with explicit workflow sequencing, API surface notes, a failure-mode catalog, and output validation criteria, not a prose summary of the manual.
3. Add `references/` entries for non-obvious modeling decisions, API contracts, and known pitfalls.
4. Add `scripts/` only when a deterministic, single-responsibility helper materially reduces error surface or makes an implicit assumption explicit.
5. Add `assets/templates/` for any task that a user will repeat across projects.
6. Exclude proprietary manuals, generated indexes, and bulk simulation outputs from all commits.

