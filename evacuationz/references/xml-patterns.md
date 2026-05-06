# XML Patterns

Source basis: XML examples and mechanisms in `Evacuationz_Exercise Guide.pdf` and `Evacuationz_Verification.pdf`.

These are compact authoring patterns. Adapt names, refs, paths, units, and values to the project. Prefer explicit units for reviewable models even where Evacuationz has defaults.

## Scenario With Output Contract

```xml
<ENZ_Scenario>
  <Files>
    <Map>map.xml</Map>
    <Populate>populate.xml</Populate>
    <AgentType>agent_type.xml</AgentType>
    <ExitBehaviour>exit_behaviour.xml</ExitBehaviour>
    <Simulation>simulation.xml</Simulation>
    <Results />
    <Evacuation />
    <Nodes />
    <Agents />
    <PreEvacuation />
    <Log />
  </Files>
</ENZ_Scenario>
```

Review points:

- Use relative paths when the batch file or run command is in the project folder.
- Request only outputs needed for the analysis, but always include the log during QA.
- Preserve the scenario file with run outputs.

## Minimal Map

```xml
<ENZ_Map>
  <Node>
    <Name>Room</Name>
    <Ref>1</Ref>
    <Length units="m">10</Length>
    <Width units="m">10</Width>
  </Node>
  <Node type="enz_safe">
    <Name>Exit</Name>
    <Ref>99</Ref>
  </Node>
  <Connection>
    <Name>Route</Name>
    <NodeRef>1</NodeRef>
    <NodeRef>99</NodeRef>
    <Length units="m">20</Length>
  </Connection>
</ENZ_Map>
```

Review points:

- Safe nodes normally do not need dimensions.
- A zero path length can trigger default distance logic based on connected node dimensions.
- Give connections stable names for output review.

## Door And Stair Connections

```xml
<Connection>
  <Name>Final Door</Name>
  <NodeRef>1</NodeRef>
  <NodeRef>99</NodeRef>
  <Length units="m">0.1</Length>
  <ConnectionType type="enz_door">
    <Width units="m">1.0</Width>
  </ConnectionType>
</Connection>

<Connection>
  <Name>Stair Flight</Name>
  <NodeRef>2</NodeRef>
  <NodeRef>3</NodeRef>
  <Length units="m">10.0</Length>
  <ConnectionType type="enz_stairs">
    <Width units="m">1.2</Width>
    <Tread units="mm">280</Tread>
    <Riser units="mm">180</Riser>
  </ConnectionType>
</Connection>
```

Review points:

- Door flow depends on effective width, not only physical width.
- Door closer and leaf settings can materially alter flow.
- Stair tread/riser dimensions affect movement speed.

## Agent Type With Explicit Movement And Delay

```xml
<ENZ_AgentType>
  <AgentTypeDefinition>
    <Name>adult</Name>
    <Speed units="m/s">1.2</Speed>
    <PreEvacuation units="s">30</PreEvacuation>
    <StartDistance type="enz_minimum" />
    <ExitBehaviour>nearest-exit</ExitBehaviour>
  </AgentTypeDefinition>
</ENZ_AgentType>
```

Review points:

- If EDM should determine decision time, set pre-evacuation to zero.
- Document whether start distance represents travel to a door, travel across a node, or a modelling convenience.
- Use stable agent type names and match them exactly in population definitions.

## Pre-Evacuation Distribution Pattern

```xml
<PreEvacuation type="enz_distribution">
  <Distribution type="enz_triangular">
    <Min units="s">0</Min>
    <MostLikely units="s">30</MostLikely>
    <Max units="s">120</Max>
  </Distribution>
</PreEvacuation>
```

Review points:

- Confirm spelling expected by the installed version. Some historical examples contain typographic inconsistencies.
- Distribution parameters need an evidence basis or sensitivity rationale.
- Record seeds and sampling method.

## Population Definition

```xml
<ENZ_Populate>
  <PopulationDefinition>
    <Agents>100</Agents>
    <NodeRef type="enz_single" refstyle="enz_ref">1</NodeRef>
    <AgentType>
      <Name>adult</Name>
    </AgentType>
  </PopulationDefinition>
</ENZ_Populate>
```

Useful variations:

- `type="enz_spread"` to distribute a population across nodes.
- `type="enz_group"` on `PopulationDefinition` for grouped occupants.
- density-based population where area is known and defensible.

## Exit Behaviour Patterns

```xml
<ENZ_ExitBehaviour>
  <ExitBehaviourDefinition>
    <Name>nearest-exit</Name>
    <ExitBehaviourType type="enz_min_distance_to_safe_node" />
  </ExitBehaviourDefinition>
  <ExitBehaviourDefinition>
    <Name>least-populated</Name>
    <ExitBehaviourType type="enz_least_populated_connection" />
  </ExitBehaviourDefinition>
</ENZ_ExitBehaviour>
```

Review points:

- Route behaviour should be selected to represent a hypothesis, not to tune the final time.
- For leader/follower behaviours, include an alternative behaviour if no leader is available.
- Required connections need map-level designation and matching behaviour.

## Simulation Controls

```xml
<ENZ_Simulation sampling="enz_monte_carlo" agent_process="enz_random">
  <MaximumTime units="s">3600</MaximumTime>
  <TimeStep units="s">0.5</TimeStep>
  <OutputFrequency units="s">10</OutputFrequency>
  <Counterflow active="enz_false" />
</ENZ_Simulation>
```

Review points:

- Time step should be fine enough for the benchmark or output resolution being claimed.
- Output frequency controls what can be inferred from nodes and agent logs.
- Random processing and Monte Carlo sampling require a seed plan.

## Smokeview Output

```xml
<ENZ_Scenario>
  <Files>
    <Map>map.xml</Map>
    <Populate>populate.xml</Populate>
    <AgentType>agent_type.xml</AgentType>
    <Log />
  </Files>
  <Smokeview>
    <ResultFile />
  </Smokeview>
</ENZ_Scenario>
```

Review points:

- Confirm yEd node dimensions and Smokeview geometry scaling.
- Agent body colour and height can be set in agent type definitions.
- Smoke layer display depends on smoke definition and layer height.

## External Configuration URL Pattern

```xml
<UrlDefinition>
  <Name>building-config</Name>
  <Path>config/building-config.xml</Path>
</UrlDefinition>
```

Use `config://building-config` in node or connection URL fields when the same configuration path is reused.

Review points:

- Prefer relative paths for reproducibility.
- Check that all referenced config files are included in the project package.

