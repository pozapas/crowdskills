# MassMotion Pitfalls

## SDK And Python

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: massmotion_11_0` | SDK not installed or PATH/PYTHONPATH wrong | verify installed module and SDK directory |
| DLL load failure | wrong Python bitness or SDK path missing | use 64-bit Python and include SDK DLL folder |
| works in MassMotion but fails standalone | internal interpreter paths differ from environment | configure environment PATH/PYTHONPATH for standalone SDK |
| works standalone but fails in script object | MassMotion ignores environment `PYTHONPATH` | add paths in application preferences |
| SDK state errors in batch | cleanup omitted | wrap `Sdk.init()`/`Sdk.fini()` in `try/finally` |

## Simulation

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| project edits do not affect active run | simulation copied project at `Simulation.create()` | edit before create or use `Simulation` control methods |
| different results with same seed | project or MassMotion version changed | record version, project hash, seed, and settings |
| slow batch runs | debug view or too many threads | use console simulation, avoid `--vis`, tune `--threads` |
| stopped run still has outputs | MassMotion writes partial database | treat as partial and inspect log/run details |

## Console

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| return code 103 | no action specified | provide `--simulation`, `--scriptobject`, or `--scriptfile` |
| return code 104 | simulation failed to start | inspect log and project issues |
| return code 105 | script file/object missing | verify path or script object name |
| return code 107 | script returned error | inspect script output/log |
| query CSV missing | query name not found or no simulation | confirm query object and use `--simulation` with `--query` |

## Analysis

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| agent position coordinates look shifted | project origin applied on export | document world coordinates or disable origin for project coordinates |
| speed differs from frame displacement | exported speed is pre-overlap-adjustment | do not recompute claims without noting caveat |
| query tables have unexpected columns | query configuration or MassMotion version changed | inspect headers before analysis |
| map export missing | map queries require view/display workflow | use SDK `View.show_map()` or GUI export |
