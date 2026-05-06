# Research Design With Evacuationz

Use this reference for studies that go beyond a single engineering run: sensitivity analysis, model comparison, calibration, validation, or publication-ready simulation experiments.

## Study Types

| Study type | Goal | Minimum design |
|------------|------|----------------|
| Mechanism verification | Confirm a model feature behaves as expected | One controlled benchmark per mechanism |
| Design comparison | Compare alternatives under shared assumptions | Matched scenario matrix with same population and seed plan |
| Sensitivity analysis | Identify which assumptions drive results | Factor table, ranges, run count, ranking method |
| Uncertainty propagation | Estimate output distribution from input uncertainty | Input distributions, random seeds, summary intervals |
| Calibration | Tune uncertain parameters against observed data | Training target, parameter bounds, loss metric, holdout case |
| Validation comparison | Compare model to independent measurements | Independent data, residual analysis, uncertainty discussion |
| Behaviour exploration | Explore route choice, EDM, groups, leaders, or smoke effects | Clearly labelled exploratory assumptions and stress tests |

## Scenario Matrix Fields

| Field | Example |
|-------|---------|
| Scenario id | `A1_baseline`, `B2_voice_alarm_smoke` |
| Geometry variant | baseline, widened door, blocked exit, alternative stair |
| Population variant | peak load, staff only, mixed agents, density-based |
| Behaviour variant | nearest exit, least populated, required route, probabilistic |
| Pre-evacuation | fixed, triangular, log-normal, EDM |
| Environmental condition | no smoke, smoke reduction, reduced lighting, combined |
| Simulation controls | timestep, max time, processing, sampling |
| Seeds | explicit seed list or deterministic |
| Outputs | log, evacuation, nodes, agents, pre-evacuation |
| Benchmarks | selected mechanism checks |

## Factor Design

Prefer a small, interpretable design before a large sweep.

| Factor class | Candidate factors |
|--------------|-------------------|
| Geometry | door width, stair width, path length, node area, blocked connection |
| Population | occupant count, distribution across nodes, density, agent mix |
| Movement | speed distribution, start distance, congestion/counterflow |
| Behaviour | exit choice algorithm, reassessment, leader/follower, group behaviour |
| Pre-movement | fixed delay, distribution parameters, alarm delay, EDM attributes |
| Environment | smoke reduction factor, layer height, lighting factor |
| Simulation | time step, sampling method, agent processing, seed |

## Seed And Run Planning

| Situation | Minimum treatment |
|-----------|-------------------|
| Deterministic benchmark | One run is enough if inputs are deterministic |
| Stochastic pre-evacuation or speed | Use a planned seed set; report mean, median, spread, and final time quantiles |
| Route choice randomness | Report exit split variability and stranded/late-agent checks |
| Sensitivity ranking | Use enough repetitions to separate factor effects from random variation |
| Trial comparison | Keep seeds separate from calibration targets and report residuals |

A practical starting point is 20 runs per stochastic scenario for screening and 100+ runs for final uncertainty summaries, adjusted to observed convergence.

## Analysis Outputs

| Metric | Use |
|--------|-----|
| Final evacuation time | Headline clearance metric |
| Time to N percent evacuated | Robust comparison when tail behaviour is unstable |
| Exit split | Route choice and signage studies |
| Maximum node occupancy | Congestion and bottleneck diagnosis |
| Door/stair throughput | Capacity checks |
| Pre-evacuation sample summaries | Behavioural delay validation |
| Agent-level paths | Route verification and anomalous-agent review |
| Residuals vs observed data | Calibration/validation |

## Interpretation Rules

- Do not describe exploratory behaviour settings as calibrated human behaviour.
- Do not collapse uncertainty to a single value without reporting spread.
- Do not compare two designs using different random seed sets unless that is intentional and explained.
- Do not use a model feature in a research claim without a mechanism-level verification check.
- Do not tune route behaviour or pre-evacuation distributions to match a target and then validate on the same target.

## Reporting Structure For Research

1. Research question and contribution.
2. Evacuationz version and modelling environment.
3. Scenario and network abstraction.
4. Population, agent type, and behaviour definitions.
5. Distribution choices and evidence basis.
6. Simulation controls and seed plan.
7. Verification matrix.
8. Experimental design and number of runs.
9. Output processing method.
10. Results with uncertainty.
11. Sensitivity or residual analysis.
12. Limitations and reproducibility package.

