# Evacuationz Modeling Protocol

Use this protocol for new models, model audits, or research study setup. It is intentionally software-specific but keeps engineering interpretation separate from file mechanics.

## 1. Define The Decision Context

Record these before opening yEd or writing XML:

| Field | Question |
|-------|----------|
| Purpose | Is this a verification test, design comparison, evacuation time estimate, behavioural study, or teaching case? |
| Endpoint | What metric will be interpreted: final evacuation time, flow rate, exit split, node occupancy, pre-evacuation distribution, route sequence, or visualization? |
| Scenario set | Is there one deterministic scenario or a matrix of alternatives? |
| Evidence tier | Does the result need a run smoke test, component verification, uncertainty analysis, or external validation comparison? |
| Review audience | Internal modeller, fire engineer, peer reviewer, regulator, or paper reader? |

## 2. Build The Network Conceptually

Start with a network sketch independent of file format.

| Element | Required decision | Common failure |
|---------|-------------------|----------------|
| Nodes | What physical spaces, stairs, and safe areas are represented? | Using visual blocks without checking length/width |
| Safe nodes | Which terminal nodes count as outside or safe? | Accidentally giving safe nodes unnecessary geometry |
| Connections | What path, door, opening, or stair links spaces? | Path length left at default when explicit travel distance was intended |
| Doors/openings | Which width, leaves, closer state, or specific flow applies? | Forgetting boundary layer differences between door and opening |
| Stairs | Which tread, riser, width, handrail, and floor height apply? | Mixing stair node geometry and connection type assumptions |
| External configs | Which definitions come from separate XML files? | Absolute paths that break reproducibility |

## 3. Define Occupants And Behaviour

Use agent types and population definitions as the behavioural contract.

| Layer | Model choices |
|-------|---------------|
| Population placement | Fixed node, density-based, spread across nodes, range population, grouped population |
| Agent types | Speed, pre-evacuation, start distance, height/body diameter, attributes, colour for Smokeview |
| Distributions | Fixed, uniform, normal, log-normal, triangular, Weibull, discrete, truncated variants |
| Exit behaviour | Minimum distance, minimum nodes, specified safe node, required route, weighted/probabilistic route, random choice |
| Reassessment | On entering a node, at a defined time, both, and whether reset applies |
| Interaction | Notification, groups, leaders, least/most populated connection |

Review principle: define the behavioural mechanism in plain language first, then encode it.

## 4. Add Systems And Conditions Only When Needed

| Mechanism | Use when | Key checks |
|-----------|----------|------------|
| Alarm systems | Notification timing changes pre-movement or EDM state | Node/system assignment, timing, compatibility with EDM assumptions |
| Smoke movement | Visibility/smoke layer modifies walking speed | Model selected, reduction factor, layer height, affected nodes |
| Reduced lighting | Light level modifies walking speed | Proulx/reduction factor choice and combination with smoke |
| Node delay | Dwell time or local delay is part of the scenario | Fixed vs agent-type delay, node location, interaction with route choice |
| EDM | Evacuation decision process is central to the study | EDM active flag, VM2 flag, agent attributes, pre-evacuation set to zero if EDM should dominate |
| Smokeview | Visualization helps QA or communication | Generated geometry, door positions, agent body settings, smoke layer display |

## 5. Set Simulation Controls

| Control | Engineering implication |
|---------|-------------------------|
| Maximum time | Must exceed expected final evacuation time with margin |
| Time step | Affects rounding and apparent agreement with simple benchmarks |
| Output frequency | Controls temporal resolution of node/agent/evacuation outputs |
| Agent processing | Sequential/random processing can affect congested or interaction cases |
| Sampling method | Monte Carlo vs stratified sampling affects stochastic coverage |
| Counterflow | Use only if counterflow is part of the scenario basis |
| Random seed | Required for repeatability; use a planned seed set for uncertainty |

## 6. Specify Output Contract

Request outputs that match the claim.

| Claim type | Minimum outputs |
|------------|-----------------|
| Final clearance time | Log plus evacuation/results output |
| Pre-evacuation distribution | Pre-evacuation output plus agent type definition |
| Node congestion | Node output and output frequency justification |
| Agent route sequence | Agent tracking output |
| Route choice behaviour | Agent and node outputs plus behaviour definitions |
| Visualization | Smokeview files plus a geometry QA note |
| Reproducibility | Log, base/input files, project manifest, seed list |

## 7. Verify In Layers

1. **Parse layer:** XML files parse, referenced files exist, expected outputs are requested.
2. **Network layer:** node/connection counts, safe nodes, dimensions, paths, doors, and stairs match the conceptual model.
3. **Mechanism layer:** relevant benchmark cases pass within tolerance.
4. **Scenario layer:** outputs match expected population totals and final state.
5. **Study layer:** repeated runs or alternatives follow the manifest and seed plan.
6. **Interpretation layer:** claims match the evidence tier.

## 8. Engineering Report Minimums

Every formal model note should include:

- Software/version and run environment.
- Input file inventory and run command or batch file.
- Scenario objective and evidence tier.
- Geometry/network assumptions.
- Population and behaviour assumptions.
- Simulation controls and random seed plan.
- Output files and headline metrics.
- Verification matrix and any failed or waived checks.
- Sensitivity/uncertainty results if stochastic mechanisms are used.
- Limitations and scope of interpretation.

