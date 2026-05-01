# Calibration, Sensitivity, And Uncertainty

Use this reference when JuPedSim is used for inference, model comparison, or
parameter studies.

## Calibration Posture

Treat defaults as starting points, not evidence. A calibrated JuPedSim study
links model parameters to observed quantities such as speed distributions,
bottleneck flow, route split, or evacuation time.

| Calibration level | Evidence standard | Appropriate claim |
| --- | --- | --- |
| Uncalibrated | plausible defaults and literature-style ranges | exploratory behavior under assumptions |
| Partially calibrated | one or two metrics match reference data | limited scenario-level inference |
| Calibrated and validated | separate calibration and validation cases | stronger predictive or comparative claims |

## Parameter Families

| Parameter family | Examples | Observable effect |
| --- | --- | --- |
| Kinematics | desired speed, reaction time, tau | travel time and speed recovery |
| Body/spacing | radius, distance-to-agent placement | density, bottleneck capacity, jamming |
| Interaction strength | neighbor or wall repulsion strength/range | local avoidance, wall hugging, clogging |
| Routing | stage graph, transition policy, waypoint distance | path choice and congestion location |
| Numerics/output | dt, every_nth_frame, max_iterations | stability, temporal resolution, runtime |

Only compare model families after deciding which parameters are semantically
comparable. For example, `desired_speed` is comparable; force scale and CSM
time gap are not direct equivalents.

## Calibration Workflow

1. Select target metrics before tuning.
2. Define admissible parameter ranges from domain knowledge.
3. Run a coarse sweep with repeated seeds.
4. Exclude invalid runs with documented criteria.
5. Score each run with a transparent objective function.
6. Refine near the best region if needed.
7. Validate on a separate scenario, seed set, or time interval.

Example objective:

```text
loss = w1 * abs(flow_sim - flow_obs) / flow_obs
     + w2 * abs(speed_sim - speed_obs) / speed_obs
     + w3 * stuck_agent_rate
```

Keep weights explicit. A hidden objective function is not reproducible.

## Sensitivity Analysis

Use sensitivity analysis to distinguish robust conclusions from parameter
artifacts.

| Method | Use when | Output |
| --- | --- | --- |
| One-at-a-time sweep | early exploration | response curve per factor |
| Local perturbation | calibrated baseline exists | slope around baseline |
| Factorial design | interactions are plausible | main and interaction effects |
| Seed replication | stochastic placement matters | uncertainty from random starts |
| Stress envelope | safety margin matters | failure boundary |

Report whether conclusions depend on a narrow parameter interval.

## Uncertainty Reporting

For each metric, summarize across seeds and runs:

- mean and standard deviation
- median and interquartile range when distributions are skewed
- min/max for stress testing
- failed-run count and reason
- paired differences when comparing two policies on matched seeds

Avoid reporting only the best run. It creates a false sense of precision.

## Model Comparison Discipline

When comparing CSM, CSM V2, AVM, GCFM, and SFM:

- freeze geometry and stage graph
- reuse initial positions whenever physically valid
- match desired-speed samples
- keep `dt` and writer interval constant unless the model requires a stability check
- report model-specific parameters in separate columns
- include a failure/stuck metric, not only evacuation time

If a model needs a different `dt` for stability, treat that as part of the
model configuration and report it clearly.

## Calibration Red Flags

| Red flag | Why it matters |
| --- | --- |
| Tuning by animation | qualitative fit may hide metric mismatch |
| Single seed | random placement can dominate local congestion |
| Changing geometry during calibration | geometry effects confound model parameters |
| Using final evacuation time only | local density or flow may be wrong |
| No failed-run policy | invalid runs silently bias results |
| Copying parameters across model families | names may match while mechanisms differ |

## Recommended Artifacts

Store these beside the run outputs:

- `manifest.csv`: factors, seeds, model parameters, output paths
- `validation.csv`: SQLite health and completion checks
- `metrics.csv`: one row per run with computed metrics
- `analysis.ipynb` or script: reproducible plots and tables
- `assumptions.md`: what was calibrated, assumed, or left unknown
