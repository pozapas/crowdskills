# Model Selection

Pick a JuPedSim model according to the phenomenon and the evidence needed. A good simulation report should justify why the model is expressive enough and where it is weak.

## Model Families

| Model | Type | Use when | Be careful with |
| --- | --- | --- | --- |
| Collision Free Speed Model | speed-based | Fast baselines, evacuation throughput, bottleneck studies, routing studies | It is simplified; global repulsion parameters apply to all agents |
| Collision Free Speed Model V2 | speed-based | Heterogeneous repulsion sensitivity or per-agent parameter sweeps | More parameters increase calibration burden |
| Anticipation Velocity Model | anticipation-based | Sharp corners, anticipatory avoidance, wall gliding, situations where future prediction matters | Reaction and anticipation parameters can dominate behavior |
| Generalized Centrifugal Force Model | force-based | Studies of force-like interaction, body asymmetry, direct steering examples | Requires more careful parameter interpretation |
| Social Force Model | force-based | Classical social-force comparisons and legacy benchmarks | Can look plausible while being poorly calibrated |

## Baseline Recommendation

For most new scenarios, start with `CollisionFreeSpeedModel` or `CollisionFreeSpeedModelV2`. Establish geometry, routing, outputs, and analysis first. Only move to AVM, GCFM, or SFM when the research question requires the additional model structure.

## Parameter Defaults From Source

| Parameter group | Important defaults |
| --- | --- |
| CSM agent | `time_gap=1.0`, `desired_speed=1.2`, `radius=0.2` |
| CSM model | `strength_neighbor_repulsion=8.0`, `range_neighbor_repulsion=0.1`, `strength_geometry_repulsion=5.0`, `range_geometry_repulsion=0.02` |
| CSM V2 agent | CSM agent defaults plus per-agent repulsion parameters |
| AVM model | `pushout_strength=0.3`, random `rng_seed` unless specified |
| AVM agent | `time_gap=1.06`, `desired_speed=1.2`, `radius=0.2`, `wall_buffer_distance=0.1`, `anticipation_time=1.0`, `reaction_time=0.3` |
| GCFM model | neighbor/geometry repulsion strengths and max interaction/interpolation distances |
| GCFM agent | `mass=1`, `tau=0.5`, `desired_speed=1.2`, `a_v=1`, `a_min=0.2`, `b_min=0.2`, `b_max=0.4` |
| SFM model | `body_force=120000`, `friction=240000` |
| SFM agent | `mass=80.0`, `desired_speed=0.8`, `reaction_time=0.5`, `agent_scale=2000`, `obstacle_scale=2000`, `force_distance=0.08`, `radius=0.3` |

Specify non-default values in the script and in the result summary. Avoid relying on hidden defaults for published experiments.

## Calibration Posture

Use this sequence for PhD-level work:

1. Define observable targets before tuning: evacuation time, flow at a bottleneck, density profile, speed distribution, lane order parameter, queue dwell time, or trajectory similarity.
2. Lock geometry and initial conditions.
3. Run a baseline with documented defaults.
4. Tune only parameters with a mechanistic reason to affect the target.
5. Use sensitivity analysis around fitted values.
6. Report non-identifiability: many parameter combinations can produce similar aggregate metrics.

## Model Comparison Rules

When comparing models:

- Use identical geometry, exit polygons, stages, start positions, seeds, `dt`, writer interval, and stop conditions.
- Keep desired-speed distributions matched unless the model requires different interpretation.
- Compare more than visual animation: use evacuation time, final count, flow, speed, density, trajectory conflicts, or route choice outcomes.
- State whether differences arise from operational movement, tactical routing, or parameterization.

## Runtime State Changes

Agent state can be inspected and some parameters can be changed during simulation through `simulation.agent(agent_id).model`. Use runtime changes intentionally:

- Good: intervention policies, adaptive speed experiments, sensitivity to waiting set activation.
- Risky: changing parameters without recording when and why.

## Deprecated Names

Use modern snake_case names. The package contains legacy aliases such as `v0`, `desiredSpeed`, `reactionTime`, `agentScale`, `obstacleScale`, `forceDistance`, and `bodyForce`; avoid them in new code.

