# Pathfinder Scripting API

Pathfinder's in-simulator scripting API is JavaScript-based and experimental. It is not Python and it is not Vissim COM.

## Enable The Script Editor

The docs state that custom scripting requires a VM argument.

Batch file form:

```text
-Dex_enable_scripting
```

Shortcut or command-line wrapper form:

```text
-J-Dex_enable_scripting
```

Example:

```powershell
pathfinder.exe -J-Dex_enable_scripting
```

When enabled, use Model -> Edit Custom Scripts. Scripts are stored in the `.pth` model and run whenever that model is simulated.

## Timing And Scope

Key rules:

- Scripts run when the simulation initializes, before movement starts.
- Use callback functions for runtime behavior.
- Scripting is not compatible with simulation restart.
- All custom scripts share global scope, so namespace variables to avoid collisions.
- Search by object name may include or omit group prefixes.

## Core Modules

Use these convenience variables:

```javascript
var sim = api.simctl.v1;
var geom = api.geometry.v1;
var agents = api.agents.v1;
var io = api.io.v1;
var triggers = api.triggers.v1;
```

| Module | Purpose |
| --- | --- |
| `api.simctl.v1` | simulation callbacks and management |
| `api.geometry.v1` | doors, rooms, measurement regions, opening/closing, door direction |
| `api.agents.v1` | occupant lookup and agent collections |
| `api.io.v1` | output streams and logging |
| `api.triggers.v1` | trigger influence controls |

## Common Patterns

Register an update callback:

```javascript
sim.onUpdate(function (t) {
  // called once each simulation timestep
});
```

Register an exit callback:

```javascript
sim.onExit(function () {
  // close streams here
});
```

Find and control a door:

```javascript
var door = geom.find("Station Entrance");
geom.close(door);
geom.open(door);
geom.setDoorDir(door, "+x");
```

Count agents in a measurement region:

```javascript
var region = geom.find("Region A");
var count = agents.findAll(region).size();
```

Find tagged agents:

```javascript
var employees = agents.findAllTagged("employee");
```

Control trigger influence:

```javascript
var alarm = triggers.find("Fire alarm trigger");
triggers.setInfluenceChance(alarm, 1.0);
```

## I/O Pattern

Use `api.io.v1` for console output. Use a PrintStream for file output and close it on exit:

```javascript
var io = api.io.v1;
var out = io.openPrintStream("custom.tsv");

sim.onUpdate(function (t) {
  out.println(t + "\t" + "value");
});

sim.onExit(function () {
  out.close();
});
```

## Extended API

The docs note that the extended API can use JavaScript and Java platform classes via `Java.type()`, but detailed internal classes are beyond the core documentation. Prefer core API methods first.
