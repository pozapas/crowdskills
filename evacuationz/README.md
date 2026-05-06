<div align="center">

# Evacuationz

**A structured AI skill for authoring, auditing, benchmarking, and reporting Evacuationz network egress models.**

![Domain](https://img.shields.io/badge/domain-fire%20egress%20modelling-b22222?style=flat-square)
![Type](https://img.shields.io/badge/type-AI%20skill-4a90d9?style=flat-square)
![Scripts](https://img.shields.io/badge/scripts-Python%203-3572A5?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-research%20use-lightgrey?style=flat-square)

*Describe your building, occupants, and study goal in plain language - the skill converts that into structured workflows, XML drafts, validation checklists, benchmark comparisons, and report outlines.*

</div>

---

## Table of Contents

- [Overview](#overview)
- [Capabilities at a Glance](#capabilities-at-a-glance)
- [Package Structure](#package-structure)
- [Quick Start](#quick-start)
- [Command-Line Smoke Tests](#command-line-smoke-tests)
- [Examples](#examples)
  - [1 - Project Folder Audit](#1--project-folder-audit)
  - [2 - Populate from Occupant Counts](#2--populate-from-occupant-counts)
  - [3 - Populate with Numeric Node References](#3--populate-with-numeric-node-references)
  - [4 - Multiple Agent Types](#4--multiple-agent-types)
  - [5 - Density-Based Population](#5--density-based-population)
  - [6 - Scenario Output Contract](#6--scenario-output-contract)
  - [7 - Benchmark Comparison](#7--benchmark-comparison)
  - [8 - Completed Run Review](#8--completed-run-review)
  - [9 - Design Comparison Study Plan](#9--design-comparison-study-plan)
  - [10 - Research Workflow with Uncertainty](#10--research-workflow-with-uncertainty)
- [Input Reference](#input-reference)
- [Common Modelling Mistakes](#common-modelling-mistakes)
- [Recommended Workflow](#recommended-workflow)
- [Source Basis](#source-basis)

---

## Overview

Evacuationz is an AI skill package for working with Evacuationz network egress simulations. It covers the full modelling lifecycle: project validation, XML authoring, scenario review, benchmark verification, run summarisation, study design, and report preparation.

The skill is accessible to new and experienced users alike. You can provide raw building descriptions, occupant data, or completed output folders, and the skill will respond with structured, actionable outputs.

> **Scope note.** The included scripts inspect existing files and outputs. They do not execute Evacuationz itself.

---

## Capabilities at a Glance

| Task | What you provide | What the skill produces |
|------|-----------------|------------------------|
| Audit a project folder | Folder with XML or GraphML files | File inventory, role classification, missing references, QA warnings |
| Author a population file | Occupant counts, node names or refs, agent types | Draft `populate.xml` with validation notes |
| Review a scenario file | `scenario.xml` and linked files | Input gap checks, output contract review, reproducibility notes |
| Inspect geometry | Nodes, safe nodes, doors, stairs, connections | Topology summary and modelling risk flags |
| Run a benchmark check | Observed result time and mechanism name | Pass/fail result with tolerance and source basis |
| Summarise completed runs | Output folder with logs and CSV files | Run digest: version, agents, stop time, outputs, warnings |
| Design a study | Research or engineering question | Scenario matrix, seed plan, factors, outputs, verification matrix |
| Prepare a report | Inputs, outputs, assumptions, results | Structured outline with evidence labels and limitations |

---

## Package Structure

```
evacuationz/
|-- SKILL.md                        # Routing, workflow rules, use constraints
|-- references/
|   |-- capability-map.md           # Full capability index
|   |-- modeling-protocol.md        # Modelling conventions and best practices
|   |-- xml-patterns.md             # Annotated XML patterns for all file roles
|   |-- verification-benchmark-atlas.md  # Benchmark cases with tolerances
|   |-- results-audit.md            # Output review guide
|   `-- research-design.md          # Study design and uncertainty guidance
|-- templates/
|   |-- study-plan.md               # Study planning template
|   |-- report-outline.md           # Report structure template
|   |-- scenario-manifest.yaml      # Scenario manifest template
|   `-- verification-matrix.csv     # Verification matrix template
`-- scripts/
    |-- validate_enz_project.py     # Project folder auditor
    |-- summarize_evac_outputs.py   # Run output summariser
    `-- compare_benchmark.py        # Benchmark comparator
```

---

## Quick Start

Invoke the skill using any of these prompt patterns inside Codex or Claude:

```text
Use evacuationz to audit this Evacuationz project folder:
D:\path\to\project
```

```text
Use evacuationz to create populate.xml from this population plan:
[paste node names, occupant counts, and agent types]
```

```text
Use evacuationz to design a verification matrix for a model
with doors, stairs, pre-evacuation distributions, and route choice.
```

```text
Use evacuationz to interpret these Evacuationz outputs:
D:\path\to\output-folder
```

---

## Command-Line Smoke Tests

Run these from the package root to verify the scripts are working correctly.

```powershell
cd "D:\OneDrive - Texas State University\AIT\Papers\RAG paper\Skill\evacuationz"

python .\scripts\validate_enz_project.py .\test --json
python .\scripts\compare_benchmark.py --list
python .\scripts\compare_benchmark.py --case door_flow_100_agents_1m --observed 108
python .\scripts\summarize_evac_outputs.py .\test --json
```

| Script | Expected behaviour |
|--------|--------------------|
| `validate_enz_project.py` | Scans XML/GraphML inputs; reports file roles, counts, missing references, warnings |
| `compare_benchmark.py --list` | Prints all available benchmark case names |
| `compare_benchmark.py --case ... --observed ...` | Returns pass/fail against tolerance |
| `summarize_evac_outputs.py` | Requires output files (logs, CSVs); exits cleanly on input-only folders |

---

## Examples

### 1 - Project Folder Audit

<details>
<summary>Show prompt and expected output</summary>

**Prompt**

```text
Use evacuationz to audit this project folder:
D:\OneDrive - Texas State University\AIT\Papers\RAG paper\Skill\evacuationz\test

Tell me:
- which files were recognised
- whether scenario references are missing
- whether the model has safe nodes, doors, stairs, and populations
- what I should fix before running Evacuationz
```

**Typical output**

```
Files scanned: 5
Roles found: map, populate, scenario, simulation, system
Map: 107 nodes, 3 safe nodes, 108 connections, 101 doors, 7 stairs
Population: 51 population definitions, 239 total agents
Warnings:
  - Length values are missing explicit units in the map.
  - Scenario references agent-type.xml and exit-behaviour.xml, but they are not present.
  - Scenario does not request Log output.
  - Simulation does not explicitly set MaximumTime or OutputFrequency.
```

**Why this matters**

| Warning | Risk |
|---------|------|
| Missing `agent-type.xml` | Occupants may use silent defaults or the model may not run as intended |
| Missing `exit-behaviour.xml` | Route choice assumptions become undocumented |
| No `Log` output requested | QA is weakened; logs capture opened files, defaults, total agents, and stop time |

</details>

---

### 2 - Populate from Occupant Counts

<details>
<summary>Show prompt and expected XML</summary>

**Prompt**

```text
Use evacuationz to create populate.xml.

Population:
- 120 office occupants spread across Office 1, Office 2, and Office 3
- 20 visitors in Lobby
- 8 staff in Control Room
- Agent type: adult for all
- Use node names, not numeric refs
```

**Expected XML**

```xml
<ENZ_Populate>
  <PopulationDefinition>
    <Agents>120</Agents>
    <NodeRef type="enz_spread">Office 1, Office 2, Office 3</NodeRef>
    <AgentType>
      <Name>adult</Name>
    </AgentType>
  </PopulationDefinition>

  <PopulationDefinition>
    <Agents>20</Agents>
    <NodeRef type="enz_single">Lobby</NodeRef>
    <AgentType>
      <Name>adult</Name>
    </AgentType>
  </PopulationDefinition>

  <PopulationDefinition>
    <Agents>8</Agents>
    <NodeRef type="enz_single">Control Room</NodeRef>
    <AgentType>
      <Name>adult</Name>
    </AgentType>
  </PopulationDefinition>
</ENZ_Populate>
```

**Suggested follow-up**

```text
Now validate the generated populate.xml and confirm it matches my population plan.
```

</details>

---

### 3 - Populate with Numeric Node References

<details>
<summary>Show prompt and expected XML</summary>

**Prompt**

```text
Use evacuationz to create populate.xml using numeric node references.

Node references:
  Lobby = 1 | Office 1 = 101 | Office 2 = 102 | Office 3 = 103 | Control Room = 7

Population:
- 120 office occupants spread across Office 1, Office 2, and Office 3
- 20 visitors in Lobby
- 8 staff in Control Room
- Agent type: adult
```

**Expected XML**

```xml
<ENZ_Populate>
  <PopulationDefinition>
    <Agents>120</Agents>
    <NodeRef type="enz_spread" refstyle="enz_ref">101, 102, 103</NodeRef>
    <AgentType>
      <Name>adult</Name>
    </AgentType>
  </PopulationDefinition>

  <PopulationDefinition>
    <Agents>20</Agents>
    <NodeRef type="enz_single" refstyle="enz_ref">1</NodeRef>
    <AgentType>
      <Name>adult</Name>
    </AgentType>
  </PopulationDefinition>

  <PopulationDefinition>
    <Agents>8</Agents>
    <NodeRef type="enz_single" refstyle="enz_ref">7</NodeRef>
    <AgentType>
      <Name>adult</Name>
    </AgentType>
  </PopulationDefinition>
</ENZ_Populate>
```

> Use numeric refs when your map uses stable `<Ref>` values and you need to avoid name-spelling mismatches.

</details>

---

### 4 - Multiple Agent Types

<details>
<summary>Show prompt and expected XML</summary>

**Prompt**

```text
Use evacuationz to create populate.xml.

Occupants:
- 90 adults in Main Office              -> agent type: adult
- 12 mobility-impaired in Main Office   -> agent type: mobility_impaired
- 6 staff in Reception                  -> agent type: staff
- 15 visitors in Lobby                  -> agent type: visitor
Use node names.
```

**Expected XML**

```xml
<ENZ_Populate>
  <PopulationDefinition>
    <Agents>90</Agents>
    <NodeRef type="enz_single">Main Office</NodeRef>
    <AgentType><Name>adult</Name></AgentType>
  </PopulationDefinition>

  <PopulationDefinition>
    <Agents>12</Agents>
    <NodeRef type="enz_single">Main Office</NodeRef>
    <AgentType><Name>mobility_impaired</Name></AgentType>
  </PopulationDefinition>

  <PopulationDefinition>
    <Agents>6</Agents>
    <NodeRef type="enz_single">Reception</NodeRef>
    <AgentType><Name>staff</Name></AgentType>
  </PopulationDefinition>

  <PopulationDefinition>
    <Agents>15</Agents>
    <NodeRef type="enz_single">Lobby</NodeRef>
    <AgentType><Name>visitor</Name></AgentType>
  </PopulationDefinition>
</ENZ_Populate>
```

> **Critical check:** Confirm all agent type names exist in your `agent-type.xml` before running.

</details>

---

### 5 - Density-Based Population

<details>
<summary>Show prompt and workflow</summary>

**Prompt**

```text
Use evacuationz to draft a population file using occupant density.

Spaces:
- Open Office:    0.10 agents/m^2
- Training Room:  0.50 agents/m^2
- Lobby:          0.20 agents/m^2

Agent type: adult. Use node names.
```

**Density-based authoring workflow**

```
1. Validate map  ->  confirm node length and width values
2. Compute area  ->  resolve any missing dimensions
3. Apply density ->  calculate expected agent counts per node
4. Draft XML     ->  write PopulationDefinition blocks
5. Validate      ->  confirm total agents match plan
```

The skill will prompt for missing area data if node dimensions are not defined in the map.

</details>

---

### 6 - Scenario Output Contract

<details>
<summary>Show prompt and expected XML</summary>

**Prompt**

```text
Use evacuationz to review my scenario.xml.

Required outputs:
- final evacuation time
- node congestion history
- agent route histories
- pre-evacuation delay samples
- log file for QA
```

**Expected `<Files>` block**

```xml
<ENZ_Scenario>
  <Files>
    <Map>map.xml</Map>
    <Populate>populate.xml</Populate>
    <AgentType>agent-type.xml</AgentType>
    <ExitBehaviour>exit-behaviour.xml</ExitBehaviour>
    <Simulation>simulation.xml</Simulation>
    <System>system.xml</System>
    <Evacuation />
    <Nodes />
    <Agents />
    <PreEvacuation />
    <Results />
    <Log />
  </Files>
</ENZ_Scenario>
```

**Output tag purposes**

| Tag | Supports |
|-----|----------|
| `<Evacuation />` | Final-time and evacuation-curve checks |
| `<Nodes />` | Congestion diagnosis |
| `<Agents />` | Route and state review |
| `<PreEvacuation />` | Delay distribution checks |
| `<Log />` | QA, reproducibility, and warning capture |

</details>

---

### 7 - Benchmark Comparison

<details>
<summary>Show prompt, command, and expected result</summary>

**Prompt**

```text
Use evacuationz to compare my observed door-flow result.

Case: 100 agents through a 1.0 m door
Observed final evacuation time: 109 s
```

**Command-line equivalent**

```powershell
python .\scripts\compare_benchmark.py --case door_flow_100_agents_1m --observed 109
```

**Expected output**

```
Expected:   108.0 s
Observed:   109.0 s
Tolerance:    2.16 s
Status:     PASS
```

> Always benchmark individual mechanisms (doors, stairs) before interpreting results from a full model.

</details>

---

### 8 - Completed Run Review

<details>
<summary>Show prompt and command</summary>

**Prompt**

```text
Use evacuationz to summarise this completed run folder:
D:\path\to\run-output

Report: software version, total agents, stop time, output files found,
log warnings and errors, and whether the output set supports my conclusions.
```

**Command-line equivalent**

```powershell
python .\scripts\summarize_evac_outputs.py "D:\path\to\run-output" --json
```

> Requires Evacuationz output files - `log.html`, `results.html`, `evac.csv`, `nodes.csv`, `agents.csv`, or equivalent. The script exits cleanly on input-only folders.

</details>

---

### 9 - Design Comparison Study Plan

<details>
<summary>Show prompt and expected deliverables</summary>

**Prompt**

```text
Use evacuationz to design a study plan.

Goal: Compare evacuation performance across two final-exit alternatives.

Alternatives:
- Base:     existing 1.0 m exit door
- Option A: widen final exit to 1.5 m
- Option B: add a second final exit

Population: 240 office occupants
Pre-evacuation: triangular distribution - min 30 s, mode 90 s, max 240 s

Required outputs: final evacuation time, T90, node congestion, exit split
```

**Expected skill deliverables**

- Scenario matrix (Base / Option A / Option B)
- Shared population and pre-evacuation assumptions
- Seed plan for stochastic repetitions
- Output contract with required tags
- Door-flow benchmark requirement
- Sensitivity notes for pre-evacuation assumptions
- Report table structure

</details>

---

### 10 - Research Workflow with Uncertainty

<details>
<summary>Show prompt and expected deliverables</summary>

**Prompt**

```text
Use evacuationz to plan a research workflow.

Question: How sensitive is total evacuation time to pre-evacuation
distribution and route choice?

Factors:
- Pre-evacuation: fixed, triangular, log-normal
- Route choice: nearest exit, least populated connection, weighted routes
- Population: 100, 200, 300 agents

Need: scenario matrix, run counts, seed plan, verification checks,
reporting structure
```

**Expected skill deliverables**

- Full factor table with levels
- Total scenario count
- Recommended run repetitions per cell
- Seed strategy
- Benchmarks for movement, door/stair flow, route choice, and pre-evacuation
- Output metrics: final time, T90, exit split, max node occupancy
- Warning against single-run inference from stochastic inputs

</details>

---

## Input Reference

| Task | Minimum inputs required |
|------|------------------------|
| `populate.xml` authoring | Node names or refs, occupant counts, agent type names, placement strategy (`enz_spread` / `enz_single` / range) |
| Agent type file | Walking speeds, pre-evacuation values or distributions, start-distance rules, route behaviour name |
| Scenario review | Scenario file, linked file names, intended output list |
| Map audit | Map file, expected exit count, known doors/stairs, geometry assumptions |
| Benchmark check | Mechanism name and observed output time |
| Run summary | Folder containing log and output CSV/HTML files |
| Study plan | Goal, alternatives, factors, population assumptions, outputs, uncertainty requirements |

---

## Common Modelling Mistakes

The skill actively checks for all of the following:

- [ ] Scenario references files that are absent from the project folder
- [ ] Population definitions missing an explicit agent type
- [ ] Map node dimensions without stated units
- [ ] Scenario configured without a `<Log />` output request
- [ ] Simulation omitting `MaximumTime` or `OutputFrequency`
- [ ] Stochastic conclusions drawn from a single run
- [ ] Route choice assumptions left undocumented
- [ ] Door or stair bottlenecks not benchmarked before full-model runs

---

## Recommended Workflow

```
Goal definition
     |
     v
Project folder audit  -->  Fix missing references and structural issues
     |
     v
Confirm all file roles
(map - populate - agent-type - scenario - simulation - system)
     |
     v
Run Evacuationz
     |
     v
Summarise outputs  -->  Check log for warnings and stop reason
     |
     v
Benchmark comparisons  -->  Validate mechanism-level behaviour
     |
     v
Report or study matrix
```

---

## Source Basis

This package was derived from:

| Document | Role |
|----------|------|
| `Evacuationz_Exercise Guide.pdf` | Modelling conventions, XML patterns, worked examples |
| `Evacuationz_Verification.pdf` | Benchmark cases, tolerance criteria, verification methodology |
