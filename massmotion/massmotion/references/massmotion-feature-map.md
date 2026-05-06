# MassMotion Feature Map

Use this reference to route MassMotion requests by software capability.

## Capability Areas

| Area | Use for |
| --- | --- |
| Project authoring | opening, creating, saving, modifying, importing, exporting, and organizing projects |
| Scene construction | floors, portals, links, stairs, escalators, barriers, gates, servers, paths, areas, collections |
| Demand and behavior | profiles, journeys, events, arrivals, origins, destinations, tasks, tokens, tallies |
| Simulation execution | run names, result databases, seeds, threading, debug runs, console runs, completion checks |
| Python SDK | standalone Python scripts using versioned `massmotion_*` modules |
| Script objects | Python scripts stored inside MassMotion projects |
| MassMotionConsole | command-line runs, script execution, query exports, return codes |
| Result databases | `.mmdb` simulation outputs, `SimulationRun`, raw frame/agent data |
| Query outputs | table queries, graph queries, map queries, CSV exports |
| Visualization | views, map display, screenshots, movies, Viewer deliverables |
| Validation | output folders, `.mmdb`, logs, query CSVs, agent position exports |

## Common User Requests

| Request | Route |
| --- | --- |
| create a model from scratch | modeling workflows plus SDK template |
| modify floors, portals, profiles, or journeys | Python SDK project authoring |
| run one simulation with Python | SDK simulation template |
| run many seeds or projects | MassMotionConsole manifest and batch template |
| run a script stored in the project | script object workflow or console `--scriptobject` |
| run a standalone script before simulation | console `--scriptfile` or SDK standalone script |
| export all query CSVs | console `--queryall` |
| export selected query CSVs | console `--query` per query name |
| analyze `.mmdb` directly | SDK `Database` or `SimulationRun` analysis |
| validate batch outputs | output validator |

## Automation Boundaries

| Boundary | Best fit |
| --- | --- |
| GUI only | model setup walkthrough, object/property explanation, troubleshooting |
| internal script object | project-local reusable automation, object generation, scripts shared with `.mm` project |
| standalone SDK Python | repeatable external scripts, simulation stepping, live agent control, custom query analysis |
| MassMotionConsole | unattended runs, seeds, scripts, simulations, query CSV export |
| external Python postprocessing | CSV aggregation, SQLite checks, reports, plots |

## Version-Sensitive Checks

- SDK module names are versioned, for example `massmotion_11_0`.
- The internal Python interpreter version can differ from the standalone SDK target.
- Console return codes and command-line options should be checked against the installed MassMotion version.
- Query columns can change with query configuration and software version; inspect headers before analysis.
