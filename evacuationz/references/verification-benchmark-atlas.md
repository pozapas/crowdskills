# Verification Benchmark Atlas

Source basis: `Evacuationz_Verification.pdf` and selected exercise-guide worked examples. Values below are intended as practical anchors for model QA. They are not a substitute for rerunning the full verification exercises with the installed software version.

## Tolerance Rules

| Case type | Default tolerance | Rationale |
|-----------|-------------------|-----------|
| Single-agent deterministic movement | 1 s | Time-step rounding and node/path transfer effects can add small offsets |
| Door/stair flow benchmark | 2 percent or 2 s, whichever is larger | Flow is usually stable but integer agents and transfer effects matter |
| Large multi-storey scenario | 5 percent unless a source-specific tolerance is justified | Geometry and modelling assumptions create larger spread |
| Stochastic distribution check | Compare distribution shape and summary statistics, not only final time | Seed and sampling method affect individual draws |
| Trial comparison | Report residuals and uncertainty, not pass/fail only | Human evacuation trials include measurement and scenario uncertainty |

## Built-In Benchmark Cases

These names match `scripts/compare_benchmark.py`.

| Case id | Mechanism | Expected value | Source section | Notes |
|---------|-----------|----------------|----------------|-------|
| `movement_corridor_path` | 40 m corridor represented as path | 40.5 s | Verification 2.1.1 | IMO movement speed case, includes transition/time-step effect |
| `movement_corridor_node` | 40 m corridor represented as node | 40.5 s | Verification 2.1.2 | Start distance fixed at 40 m |
| `stair_speed_imo` | Single agent down 10 m stair | 12.0 s | Verification 2.1.3 | Hand calculation about 10.9 s; model includes transitions |
| `door_flow_100_agents_1m` | 100 agents through 1.0 m door | 108.0 s | Verification 2.2 | Effective width uses 0.15 m boundary layer each side |
| `sfpe_handbook_9_storey` | SFPE Handbook 9-storey example | 1871.0 s | Verification 2.5 | Hand calculation cited as 1524 s; model assumptions differ |
| `sfpe_guide_300_zero_start` | SFPE Guide example excluding travel to door | 221.5 s | Verification 2.6 | 300 agents, two stairs, zero start distance |
| `sfpe_guide_300_fixed_start` | SFPE Guide example including 200 ft start distance | 283.0 s | Verification 2.6 | Guide value cited as 300 s including travel |
| `exercise2_default_single_agent` | Default pre-evacuation plus travel | 1890.0 s | Exercise Guide 2 | 1800 s pre-evacuation plus about 90 s travel |
| `exercise3_custom_agent` | Custom speed/pre-evac/start distance | 36.5 s | Exercise Guide 3 | 30 s pre-evacuation plus travel and simulation completion offset |
| `edm_awake_familiar_remote` | EDM awake/familiar remote alarm case | 61.0 s | Exercise Guide 24 | Comparable to C/VM2 60 s case |
| `edm_asleep_unfamiliar_remote` | EDM asleep/unfamiliar remote alarm case | 600.0 s | Exercise Guide 24 | Comparable to C/VM2 600 s case |

## Mechanism Coverage

| Verification area | What it checks | Use it before trusting |
|-------------------|----------------|------------------------|
| Travel speed | Agent movement along paths and through node travel distance | Any model where uncongested movement contributes materially |
| Door flow | Specific flow, effective width, door/opening distinctions, closer effects | Door-limited clearance or room exit flow |
| Stair flow | Stair speed and specific flow | Multi-storey evacuation or stair bottlenecks |
| FEDG and SFPE examples | Comparisons to established hand calculations | Engineering design comparisons |
| Pre-evacuation distributions | Fixed, uniform, normal, log-normal and room clearance effects | Behavioural delay studies |
| yEd geometry | Graphical input geometry and stair flow replication | Models authored primarily in yEd |
| Route choice | Minimum/maximum distance, minimum nodes, random, specified exit, required connection | Studies involving route selection or exit split |
| NIST stair trials | Multi-building stair evacuation comparisons | External validation claims |
| Lecture rooms | Lecture-type room clearance comparisons | Assembly/lecture room modelling |

## Benchmark Selection Workflow

1. List mechanisms used in the model.
2. Select the smallest benchmark that exercises each high-impact mechanism.
3. Run or compare the benchmark with documented software version and time step.
4. If a benchmark fails, fix the component before interpreting the complex scenario.
5. If a benchmark is intentionally waived, state why the mechanism is not material to the claim.

## Reporting Benchmark Results

Use a table with these fields:

| Field | Description |
|-------|-------------|
| Benchmark id | Name or section reference |
| Mechanism | Door, stair, route, pre-evacuation, yEd, etc. |
| Expected | Target value or distribution property |
| Observed | Model result |
| Tolerance | Numeric or qualitative criterion |
| Status | Pass, fail, waived, or not applicable |
| Explanation | Time-step offset, transition effect, version difference, or correction made |

