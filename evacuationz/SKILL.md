---
name: evacuationz
description: Evacuationz skill for fire engineering and evacuation research. Use it to create, audit, verify, compare, and report network egress models using XML, yEd/GraphML, scenario files, stochastic inputs, smoke or lighting effects, route choice, and benchmark evidence.
license: MIT
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
metadata:
  version: 1.0.0
  domains:
    - fire-engineering
    - evacuation
    - egress-modeling
    - verification-validation
    - research
  source_documents:
    - Evacuationz_Exercise Guide.pdf
    - Evacuationz_Verification.pdf
---

# Evacuationz

Use this skill when working with Evacuationz network egress models where the output needs to withstand engineering review, research replication, sensitivity analysis, or benchmark comparison. It turns the exercise guide and verification guide into a repeatable workflow for building scenarios, checking assumptions, running comparisons, and preparing defensible technical outputs.

This skill supports engineering judgement. It does not certify code compliance, approve a design, or replace review by the authority having jurisdiction.

## Triggers

- `build an Evacuationz scenario` - Create or restructure model inputs from a building, study, or hypothesis.
- `audit this Evacuationz project` - Inspect XML, yEd/GraphML, logs, outputs, and assumptions for technical weaknesses.
- `verify Evacuationz results` - Compare a case against known movement, door, stair, route choice, or pre-evacuation benchmarks.
- `design an Evacuationz research study` - Plan experimental factors, seeds, distributions, uncertainty analysis, and reporting.
- `explain this Evacuationz output` - Interpret log, evacuation, node, agent, pre-evacuation, or Smokeview outputs.

## Quick Reference

| Task | Primary output | Use these references |
|------|----------------|----------------------|
| Convert building or trial data to a model | Scenario plan plus XML/yEd authoring checklist | Modeling Protocol, XML Patterns |
| Check model credibility | Audit findings and verification matrix | Results Audit Guide, Verification Benchmark Atlas |
| Run research experiments | Scenario matrix, seed plan, factor definitions, reporting structure | Research Design guide, Study Plan template |
| Compare to a benchmark | Pass/fail comparison with tolerance rationale | `scripts/compare_benchmark.py`, Verification Benchmark Atlas |
| Summarize completed runs | Output inventory and result digest | `scripts/summarize_evac_outputs.py`, Results Audit Guide |

## Operating Principles

1. Separate modelling intent from software mechanics. First state the fire engineering or research question, then map it to nodes, connections, populations, delays, distributions, route choices, smoke or lighting effects, and outputs.
2. Keep every modelling assumption traceable. Geometry simplifications, start distances, pre-evacuation inputs, door effective widths, stair parameters, merge rates, reassessment rules, and stochastic sampling all need an explicit basis.
3. Use verification cases as calibration anchors, not decoration. Simple travel, door flow, stair flow, route choice, pre-evacuation, and yEd geometry checks should be run before trusting a complex building case.
4. Treat stochastic outputs as distributions. Avoid single-run conclusions unless the scenario is deterministic or the purpose is only a smoke test.
5. Report model limits as part of the result. Evacuationz can represent many behaviours, but some guide capabilities are rudimentary or evolving, especially group and leader interaction, complex EDM cases, and future map-list features.

## Process

### Phase 1: Frame The Model

Define the decision context before creating or editing files.

1. **Question and endpoint** - Identify whether the purpose is design comparison, evacuation time estimation, evacuation research, training, sensitivity study, or software verification.
2. **Scenario envelope** - Record building type, occupied areas, safe nodes, relevant fire effects, alarm/notification assumptions, and whether pre-evacuation is direct input or produced through EDM.
3. **Evidence basis** - Link each core assumption to one of: project data, field/trial data, code/design guide requirement, literature, calibration target, or explicit exploratory hypothesis.
4. **Credibility tier** - Choose the minimum required evidence:
   - Tier 1: did the model run and produce expected files?
   - Tier 2: did components match benchmark cases?
   - Tier 3: did stochastic behaviour converge across seeds and distributions?
   - Tier 4: did results compare reasonably to independent data or trials?

**Verification:** The scenario can be summarized in one paragraph, and every high-impact assumption has a source or stated uncertainty.

### Phase 2: Construct Or Audit Inputs

Build or inspect the Evacuationz model as a network.

1. **Geometry and topology** - Check node dimensions, safe nodes, connection lengths, door/opening/stair types, yEd scaling, URL configuration, and required routes.
2. **Population and agents** - Define population counts, density rules, spread/range node refs, multiple agent types, speed distributions, pre-evacuation distributions, start distances, attributes, individual logs, and body dimensions where relevant.
3. **Systems and environmental effects** - Add alarm systems, node delays, smoke movement reduction, lighting reduction, EDM activation, smoke layer height, or Smokeview output only where they answer the scenario question.
4. **Simulation controls** - Set maximum time, time step, output frequency, sampling method, random seed strategy, agent processing mode, counterflow, and reassessment behaviour.
5. **Output contract** - Request the files needed for the analysis: log, results, evacuation, nodes, pre-evacuation, agents, yEd output, Smokeview, or base files.

**Verification:** `scripts/validate_enz_project.py` reports no structural errors, and warnings are either fixed or recorded as intentional modelling decisions.

### Phase 3: Verify, Interpret, And Report

Use simple tests and output audits before drawing conclusions from complex scenarios.

1. **Benchmark check** - Compare the relevant component behaviour against the verification atlas, including tolerances for time step, transition time, stochastic sampling, or documented model mismatch.
2. **Output audit** - Inspect log status, total agents, simulation stop time, output files, last evacuation state, node occupancy, agent tracks, pre-evacuation samples, and any warnings or errors.
3. **Uncertainty treatment** - For non-deterministic cases, report number of runs, seeds, distribution parameters, central tendency, spread, convergence checks, and factor effects.
4. **Engineering interpretation** - Separate simulated clearance time from design decision logic. State whether the result is a direct estimate, comparative result, model diagnostic, or sensitivity response.
5. **Reproducibility package** - Preserve input files, run scripts, software version, seed plan, output digest, benchmark matrix, and report assumptions.

**Verification:** A reviewer can rerun the scenario, reproduce the headline metric, identify the scenario basis, and see which benchmark checks support the model.

## Commands

Run these from the skill package directory or pass absolute paths.

```bash
python scripts/validate_enz_project.py path/to/project --json
python scripts/summarize_evac_outputs.py path/to/output-folder --json
python scripts/compare_benchmark.py --list
python scripts/compare_benchmark.py --case door_flow_100_agents_1m --observed 108
```

## Scripts

| Script | Purpose | Exit codes |
|--------|---------|------------|
| `scripts/validate_enz_project.py` | Parse XML/GraphML project inputs, classify Evacuationz file roles, check references, and flag modelling risks. | `0` success, `1` failure, `10` validation failure, `11` verification failure |
| `scripts/summarize_evac_outputs.py` | Inventory logs and CSV outputs, extract run status, agent totals, stop times, and table dimensions. | `0` success, `1` failure, `10` missing usable outputs, `11` verification failure |
| `scripts/compare_benchmark.py` | Compare an observed time to built-in benchmark expectations from the verification and exercise guides. | `0` pass, `1` failure, `10` benchmark mismatch, `11` verification failure |

## Anti-Patterns

| Avoid | Why it fails | Instead |
|-------|--------------|---------|
| Using a single complex building model as the first test | Input mistakes can masquerade as behavioural findings | Start with a minimal benchmark and then add complexity in traceable increments |
| Treating yEd visual size as equivalent to modelled dimensions without checking scaling | Smokeview and network geometry can diverge from intended physical dimensions | Verify node and path dimensions explicitly and inspect generated yEd/Smokeview output |
| Mixing pre-evacuation and EDM without stating intent | EDM does not replace pre-evacuation when both are defined; values can combine | Set pre-evacuation to zero when EDM should be the only decision-time mechanism |
| Reporting one stochastic run as a stable result | Random sampling, route choice, and distributions can move the result materially | Run a seed plan and report variation |
| Comparing to hand calculations without accounting for model transition/time-step effects | Evacuationz may include node-path transfer and time-step rounding effects | Use benchmark tolerances and explain expected offsets |
| Ignoring warnings because outputs were produced | Log warnings can identify missing specifications, default assumptions, or file reference errors | Make the log part of the acceptance criteria |

## Verification Checklist

- [ ] Scope, scenario endpoint, and credibility tier are recorded.
- [ ] XML/GraphML inputs parse or documented exceptions are understood.
- [ ] Node, path, door, stair, and safe-node assumptions are checked.
- [ ] Population, agent types, start distance, pre-evacuation, and route choice are traceable.
- [ ] Simulation controls and seed strategy are recorded.
- [ ] Benchmark comparisons are selected for the mechanisms actually used.
- [ ] Logs and output files are summarized and preserved.
- [ ] Claims are worded to match the evidence tier and uncertainty treatment.

## Extension Points

1. **Project-specific benchmark sets:** Add JSON benchmark files for a lab, course, jurisdiction, or paper and compare them with `compare_benchmark.py`.
2. **Automated run orchestration:** Extend the scripts to call local Evacuationz or batch files when the executable path is known.
3. **Statistical post-processing:** Add bootstrap intervals, convergence plots, or scenario-factor regression after output formats are standardized.
4. **Code or design guide overlays:** Add jurisdiction-specific checks without hardcoding them into the core skill.
5. **GraphML extraction:** Add deeper yEd data extraction for embedded Evacuationz fields if the project uses `.graphml` as the primary source.

## References

- Capability Map - Condensed map of Evacuationz concepts from the exercise guide.
- Modeling Protocol - End-to-end modelling protocol for engineering and research use.
- Verification Benchmark Atlas - Benchmark catalogue distilled from the verification guide.
- XML Patterns - XML authoring patterns and common modelling fragments.
- Results Audit Guide - Log, CSV, and output interpretation checklist.
- Research Design - Experimental design, uncertainty, sensitivity, and reporting guidance.
- Study Plan template - Reusable study plan template.
- `assets/templates/verification-matrix.csv` - Starter verification matrix.
- Report Outline template - Fire engineering/research report structure.
- `assets/templates/scenario-manifest.yaml` - Scenario metadata manifest for reproducible studies.


