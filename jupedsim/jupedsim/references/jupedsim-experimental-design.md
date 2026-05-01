# Experimental Design For JuPedSim Studies

Use this reference when the user wants a research-grade simulation study, not
only a runnable script.

## Table Of Contents

- Study framing
- Scenario validity
- Experimental designs
- Randomization and replication
- Metric design
- Reporting structure
- Threats to validity

## Study Framing

Start by writing the study as a testable claim:

```text
Under [geometry], [population], [model], and [routing policy], changing
[factor] from [low] to [high] changes [metric] by [direction/amount].
```

Examples:

| Research aim | Better formulation |
| --- | --- |
| "simulate evacuation" | "Estimate how exit width affects total evacuation time and peak bottleneck density." |
| "compare models" | "Compare CSM, AVM, and SFM under identical initial positions and routing, using completion time and stuck-agent rate." |
| "test queues" | "Measure how controlled queue release affects downstream density and travel-time variance." |

Record what the simulation is allowed to answer and what it cannot answer. A
microscopic simulation can test consequences of assumptions; it does not
automatically validate those assumptions.

## Scenario Validity

Use four validity layers.

| Layer | Question | JuPedSim implication |
| --- | --- | --- |
| Face validity | Does the setup look plausible to domain experts? | Geometry, speed ranges, density, and route graph should pass visual inspection. |
| Construct validity | Does the metric represent the concept? | Use flow for capacity, density exposure for crowding, completion-time distribution for evacuation performance. |
| Internal validity | Did only the intended factor change? | Freeze seeds, initial positions, geometry, dt, output interval, and route graph across comparisons. |
| External validity | Where can results generalize? | State limits: geometry class, population type, model family, calibration status. |

## Scenario Taxonomy

Classify the scenario before coding.

| Scenario type | Primary risk | Required controls |
| --- | --- | --- |
| Evacuation | exit reachability and termination | max iteration guard, final agent count, exit-stage placement |
| Bottleneck | geometry dominates conclusions | exact width, measurement line, density region |
| Route choice | assignment policy may confound congestion | route utilization, transition policy, exit usage |
| Queue/waiting | intervention timing changes result | release log, queue count, waiting state history |
| Bidirectional flow | visual lane patterns can mislead | group IDs, mixing metric, repeated seeds |
| Direct steering | agents do not exit automatically | explicit target updates and removal policy |

## Experimental Designs

Choose the smallest design that answers the question.

| Design | Use when | Notes |
| --- | --- | --- |
| Single baseline | debugging or demonstration | Do not overclaim; report as illustrative. |
| One-factor sweep | one causal factor is central | Best first design for bottleneck width, density, speed, or radius. |
| Matched model comparison | model family is central | Use identical geometry, starts, speeds, dt, and output interval. |
| Factorial design | interactions matter | Keep levels few; repeated seeds are more valuable than too many factors. |
| Calibration loop | empirical data exists | Separate calibration data from validation data. |
| Stress test | find failure boundaries | Report as robustness, not typical behavior. |

## Randomization And Replication

Use independent seeds for stochastic placement and model-level randomness. Do not
change the seed when the factor under study changes unless the goal is a fully
randomized population sample.

Recommended practices:

- Use at least three seeds for exploratory sweeps.
- Use five or more seeds when reporting model comparison or sensitivity results.
- Store seed, placement method, geometry label, model parameters, and output path
  in a manifest.
- Compare paired runs when possible: the same initial positions under different
  model families or policies.

## Metric Design

Define metrics before running the sweep.

| Concept | Candidate metrics |
| --- | --- |
| Evacuation performance | total evacuation time, median exit time, 95th percentile exit time |
| Capacity | flow through line, N-t slope, saturation flow interval |
| Crowding | peak density, density exposure time, time above threshold |
| Comfort | speed reduction, stop-and-go frequency, acceleration proxy |
| Robustness | stuck-agent count, failed-run rate, sensitivity slope |
| Route policy | route usage share, exit imbalance, local density difference |

Avoid using animation as the only evidence. Animation is a diagnostic, not a
metric.

## Reporting Structure

A strong JuPedSim study report includes:

1. Question and hypothesis.
2. Geometry diagram or exact geometry description.
3. Model family and parameter table.
4. Population generation method, spacing, density/count, and seeds.
5. Journey/stage graph and intervention policy.
6. Run settings: dt, writer interval, max iterations, stop condition.
7. Validation checks and failed-run handling.
8. Metrics and statistical summaries.
9. Limitations and transferability.

## Threats To Validity

| Threat | Symptom | Mitigation |
| --- | --- | --- |
| Unreachable target | agents never exit | routability check, intermediate waypoint, smaller exit polygon |
| Placement bias | density varies by seed | fixed seed schedule, replicate, report initial density |
| Model unfairness | model comparison changes hidden factors | shared start positions, comparable speed/radius assumptions |
| Output aliasing | missed line crossings or density spikes | smaller `every_nth_frame`, sensitivity check |
| Overfitting | parameters tuned to one case | holdout geometry or validation scenario |
| Statistical noise | conclusion changes by seed | confidence intervals, paired comparisons |

## Minimum Advanced Level Deliverable

For thesis or paper support, produce:

- executable simulation code
- manifest CSV
- validation report for every SQLite recording
- metric table with one row per run
- plots with units and scenario labels
- short paragraph distinguishing calibrated facts from assumptions
