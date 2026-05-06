# MassMotion Python SDK

MassMotion provides a Python SDK for project authoring, simulation control, analysis, database access, and visualization. Common examples use `massmotion_11_0 as mm`; the actual module name depends on the installed SDK version.

## Environment Checklist

| Requirement | Check |
| --- | --- |
| 64-bit Python | required for SDK DLL loading |
| SDK install path | usually under `C:/Program Files/Oasys/MassMotion SDK .../` |
| SDK environment variable | older SDK installations may expose `MASSMOTION_SDK_DIR_11_0` |
| PATH/DLL discovery | SDK folder must be discoverable by Python |
| module name | often `massmotion_11_0`; verify installed package |
| internal interpreter | MassMotion 11.8 script objects commonly use Python 3.12 |

## Standalone SDK Lifecycle

Use this pattern for external scripts:

```python
import massmotion_11_0 as mm

mm.Sdk.init()
try:
    project = mm.Project.open("c:/temp/my_project.mm")
    # SDK work here
finally:
    mm.Sdk.fini()
```

Do not omit cleanup. It keeps repeated batch runs from leaking SDK state.

## Project Authoring

Core classes and methods:

| Task | SDK path |
| --- | --- |
| create a new project | `mm.Project.create()` |
| open an existing project or database | `mm.Project.open(path)` |
| save a project | `project.save(path)` |
| list objects | `project.get_objects()` |
| get floors/portals/profiles | `project.get_floors()`, `get_portals()`, `get_profile(name)` |
| create floor | `project.create_floor(name, MeshGeometry)` |
| create portal | `project.create_portal(name, MeshGeometry)` |
| create profile | `project.create_profile(name)` |
| create journey | `project.create_journey(name)` |
| check object exists | `project.has_object(name)` |
| unique names | `project.find_next_unique_name(prefix)` |

Geometry examples use `MeshGeometry.create_flat_polygon()` with `Vec2d` points and object methods such as `get_geometry()` and `set_geometry()`.

## Simulation

Create and step a simulation:

```python
project = mm.Project.open("c:/temp/my_project.mm")
simulation = mm.Simulation.create(project, "DefaultRun", "DefaultRun.mmdb")

while not simulation.is_done():
    frame_summary = simulation.step()
```

Important rule: `Simulation.create()` makes a copy of the project for the simulation. Edits to the original project after simulation creation do not affect the active simulation. Use `Simulation` methods for runtime control.

Runtime control examples:

| Task | SDK path |
| --- | --- |
| inspect created agents | `frame_summary.get_created_agents()` |
| list active agents | `simulation.get_all_agents()` |
| request new agent | `simulation.request_new_agent(mm.AgentRequest(portal_id))` |
| assign tasks | `agent.add_task_as_active(task)` |
| direct agent movement | `agent.assume_control()`, `agent.move_to()`, `agent.release_control()` |
| open/close gates | `simulation.close_gate(gate_id)`, `simulation.is_gate_open_to_all(gate_id)` |

## Analysis

Simulation data are stored in `.mmdb` files. Access patterns:

| Need | SDK path |
| --- | --- |
| connect existing result database | `project.create_simulation_run(name)` then `run.connect(mmdb_path)` |
| evaluate table query | create query, configure it, call `query.evaluate()` |
| evaluate graph query | create graph query, configure it, call `query.evaluate()` |
| evaluate map query | create map query, display it through `View.show_map()` |
| read raw frame/agent data | `mm.Database.open(mmdb_path)` |

Common table and map query families:

| Query family | Use |
| --- | --- |
| `AgentSummaryTableQuery` | per-agent summary metrics |
| `AgentTripTimeTableQuery` | trip completion timing |
| `AgentTransitionTableQuery` | transition usage |
| `AgentTokenTimeTableQuery` | time holding tokens |
| `ServerSummaryTableQuery` | server wait/service summaries |
| `OriginDestinationMatrixTableQuery` | OD matrix summaries |
| `AverageDensityMapQuery` | average spatial density |
| `MaxDensityMapQuery` | maximum density |
| `AgentPathMapQuery` | path usage |
| `AgentTimeToExitMapQuery` | spatial time-to-exit |

## Visualization

Use `View` to display simulations, playback existing runs, show maps, capture images, and generate movies. A map query is evaluated by showing it in a view.

## Internal Script Objects

Inside MassMotion script objects:

- The application provides an internal Python interpreter.
- Use `from massmotion_11_0 import *` or the installed module conventions used by the script templates.
- Access the current project with `Project.get_current_project()`.
- Script-object changes are immediate and usually participate in undo/rollback; running a simulation is not fully undoable because the database file persists.
- Scripts can import functions from other script objects by object name.
- Third-party modules are found through MassMotion application preferences `PYTHONPATH`; MassMotionConsole uses the environment `PYTHONPATH`.

## Good SDK Habits

- Validate every object name before using it.
- Keep project mutation before `Simulation.create()` unless using runtime simulation APIs.
- Record run name and `.mmdb` path.
- Use explicit seeds in console workflows or project settings.
- Remove temporary query objects if a script creates them only for analysis.
- Save project files only when the script intentionally modifies the project.
