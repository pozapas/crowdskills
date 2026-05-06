# Evacuationz Capability Map

Source basis: `Evacuationz_Exercise Guide.pdf` and `Evacuationz_Verification.pdf`.

This reference maps the source guides into a working model vocabulary. Use it to choose which Evacuationz mechanisms belong in a scenario and which checks should accompany them.

## Core File Roles

| Role | Typical root or location | Purpose | Review focus |
|------|--------------------------|---------|--------------|
| Scenario | `ENZ_Scenario`, `Evacuationz_Scenario`, yEd data field | Points to input/output files and requests outputs | Relative paths, output contract, copied log, base file, Smokeview request |
| Map | `ENZ_Map`, yEd/GraphML | Nodes, safe nodes, connections, doors, stairs, lengths, widths | Connectivity, node dimensions, safe nodes, effective widths, stair geometry |
| Populate | `ENZ_Populate` | Populations, node references, counts, spread/range placement, groups | Total agents, node targets, density limits, group behaviour |
| Agent type | `ENZ_AgentType` | Speed, pre-evacuation, start distance, distributions, attributes, body data | Units, distributions, EDM attributes, exit behaviour link |
| Exit behaviour | `ENZ_ExitBehaviour` | Route and connection selection rules | Behaviour type, subtype, required routes, reassessment |
| System | `ENZ_System` | Alarm, smoke, lighting, environmental systems | Trigger timing, node assignment, compatible units |
| Simulation | `ENZ_Simulation` | Time, timestep, processing, sampling, counterflow, EDM | Maximum time, seed plan, Monte Carlo/stratified choice, run count |

## Capability Families

| Family | Mechanisms | Source guide coverage | Verification anchor |
|--------|------------|-----------------------|---------------------|
| Geometry | Node length/width, path length, safe nodes, yEd scaling, external config URLs | Exercises 1, 4, 17, 27, 29, 30 | Corridor travel, yEd stair geometry |
| Door and opening flow | Door width, leaves, closer, openings, variable specific flow | Exercises 5, 6, 26 | IMO door flow, door closer comparison |
| Stair movement | Stair speed, flow, handrails, floor-to-floor height | Exercise 7 | IMO stair speed, stair flow |
| Population | Direct counts, density, spread/range placement, complex populations | Exercises 2, 9, 10, 12 | Pre-evacuation and clearance tests |
| Agent properties | Speed, pre-evacuation, start distance, height, diameter, distributions, individuals | Exercises 3, 8, 10, 14 | Movement speed, distribution checks |
| Route choice | Minimum/maximum distance, node count, random, specified safe node, preferred/required/weighted routes, behaviour lists, probabilistic selection | Exercises 18, 19 | Exit choice and required connection tests |
| Environmental effects | Smoke movement reduction, lighting reduction, alarms, node delays, EDM | Exercises 20-24 | Limited direct benchmarks; use component checks and sensitivity |
| Interaction | Notification, groups, leaders, least/most populated connection | Exercise 25 | Use cautiously; source notes limitations |
| Outputs | Log, results, evacuation, nodes, agents, pre-evacuation, yEd, Smokeview, base file | Exercises 2, 11, 15, 17, 27, 28, 32 | Output inventory and hash/base checks |
| Automation | XML scripting and batch execution | Exercises 30-31 | Reproducible run scripts and project manifests |

## High-Leverage Assumptions

| Assumption | Why it matters | Minimum documentation |
|------------|----------------|-----------------------|
| Start distance type/value | Changes early movement and can shift door/stair flow profiles | Type, units, basis, and whether travel-to-door is included |
| Door type and effective width | Door boundary layer and closer behaviour directly control flow | Physical width, door/opening type, leaves, closer, specific flow |
| Stair tread/riser/width | Affects speed and specific flow | Tread, riser, clear width, handrail assumptions, floor height |
| Pre-evacuation distribution | Can dominate evacuation time | Distribution type, parameters, truncation, source, seed plan |
| EDM activation | Combines with pre-evacuation unless pre-evacuation is zero | EDM flags, VM2 setting, agent attributes, alarm/smoke timings |
| Route choice | Determines congestion and exit split | Behaviour type, specified safe nodes/connections, reassessment rules |
| Stochastic sampling | Affects repeatability and uncertainty | Seed policy, number of runs, sampling method, convergence evidence |
| yEd geometry scaling | Visual geometry and modelled geometry can diverge | Export check, generated node/path output, Smokeview review if used |

## Mechanism Selection Rules

Use the simplest mechanism that represents the research or engineering question.

| Need | Prefer | Avoid until justified |
|------|--------|-----------------------|
| Basic travel time check | Fixed speed, fixed start distance, zero pre-evacuation | Distributions, EDM, route reassessment |
| Flow capacity check | Door/stair benchmark with controlled start distance | Complex route choice or smoke effects |
| Design comparison | Same population and uncertainty model across alternatives | Changing multiple assumptions between alternatives |
| Human behaviour study | Explicit agent types, distributions, route rules, EDM sensitivity | Hiding behavioural effects in generic defaults |
| Visualization | Smokeview output after geometry audit | Using visualization as proof of numerical validity |
| Research publication | Scenario matrix, seeds, output digest, benchmark matrix | Single-run headline values |

## Known Caution Areas

- Some interaction features are described as rudimentary or evolving in the exercise guide. Treat group, leader, and crowd-following behaviours as exploratory unless separately validated for the intended claim.
- EDM calibration can match some C/VM2 combinations and not others. Do not generalize beyond documented assumptions without sensitivity analysis.
- Map list, node area, and connection length features are marked as incomplete or future-looking in the map creation section. Do not rely on them without testing the installed software version.
- Base files include a hash mechanism. If a base file is modified or the hash is removed, the program is expected to report errors. Preserve generated base files as controlled artifacts.

## Capability-to-Benchmark Matching

| If the scenario uses | Run or reference at least |
|----------------------|---------------------------|
| Uncongested movement | Corridor path/node travel benchmark |
| Door flow | IMO door flow plus width/opening/closer comparison if relevant |
| Stair flow | IMO stair speed and stair flow cases |
| Pre-evacuation distributions | Fixed/uniform/normal/log-normal checks plus room clearance sensitivity |
| yEd input | yEd stair geometry verification or generated yEd output review |
| Route choice | Exit-choice and required-connection cases |
| Multi-storey stairs | SFPE Handbook or NIST stair trial comparison |
| Lecture rooms | Lecture-type room comparison and sensitivity to geometry/population assumptions |

