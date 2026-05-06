# Evacuationz Technical Report Outline

## 1. Executive Summary

- Purpose of the model.
- Headline result or comparison.
- Evidence tier and key limitations.

## 2. Scope And Decision Context

- Engineering decision or research question.
- Building or scenario scope.
- Included and excluded mechanisms.

## 3. Software And Files

| Item | Value |
|------|-------|
| Evacuationz version |  |
| Run method | Runz / command line / batch |
| Scenario file |  |
| Map file |  |
| Population file |  |
| Agent type file |  |
| Exit behaviour file |  |
| Simulation file |  |
| System file |  |

## 4. Network Abstraction

- Node list and physical interpretation.
- Connection list and physical interpretation.
- Safe nodes.
- Geometry simplifications.
- yEd/GraphML or XML authoring method.

## 5. Occupants And Behaviour

- Population sources and counts.
- Agent type definitions.
- Movement speed assumptions.
- Pre-evacuation or EDM assumptions.
- Start distances.
- Exit choice and reassessment.
- Interaction mechanisms, if any.

## 6. Simulation Controls

- Maximum time.
- Time step.
- Output frequency.
- Agent processing mode.
- Sampling method.
- Random seed plan.
- Number of runs.

## 7. Verification And QA

| Check | Result | Evidence |
|-------|--------|----------|
| Input parse/reference check |  |  |
| Total agent check |  |  |
| Movement benchmark |  |  |
| Door benchmark |  |  |
| Stair benchmark |  |  |
| Route behaviour benchmark |  |  |
| Output inventory |  |  |

## 8. Results

- Final evacuation/clearance times.
- Time-to-percent-evacuated metrics.
- Bottlenecks and node occupancy.
- Exit split and route patterns.
- Distribution summaries.
- Visual outputs, if used.

## 9. Sensitivity And Uncertainty

- Factor ranges.
- Number of runs.
- Seed plan.
- Summary intervals.
- Dominant factors.

## 10. Interpretation

- What the model supports.
- What the model does not support.
- Engineering or research implications.

## 11. Limitations

- Software/version limits.
- Input uncertainty.
- Behaviour model limits.
- Validation limits.

## 12. Reproducibility Package

- Input files.
- Batch/run scripts.
- Output digest.
- Verification matrix.
- Scenario manifest.
- Report data tables.

