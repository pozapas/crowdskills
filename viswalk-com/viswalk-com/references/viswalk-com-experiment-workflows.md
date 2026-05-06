# Viswalk-COM Experiment Workflows

Use these workflows for reproducible Viswalk automation.

## Existing Network, Demand Sweep

1. Load a fixed `.inpx` and optional `.layx`.
2. Set a unique result folder for the run.
3. Set `RandSeed` and `SimPeriod`.
4. Set pedestrian input volumes such as `Volume(1)`.
5. Run the simulation.
6. Read travel time, area, and network performance metrics.
7. Write one result row per seed and factor combination.

Keep one network reload per run unless the script can prove all state is reset correctly.

## Paired Comparison

When comparing designs, preserve:

| Controlled item | Reason |
| --- | --- |
| network geometry | isolates the changed factor |
| pedestrian input definitions | avoids demand confounding |
| random seeds | enables paired differences |
| simulation period and resolution | keeps metrics comparable |
| measurement definitions | avoids changing the response variable |
| result extraction code | avoids analysis drift |

Change only the intended factor, such as input volume, route split, area behavior type, walking behavior, obstacle placement, or layout alternative.

## Batch Manifest

Use `scripts/create_viswalk_run_matrix.py` to create a manifest with:

| Column | Meaning |
| --- | --- |
| `run_id` | stable run identifier |
| `network_path` | `.inpx` path to load |
| `layout_path` | optional `.layx` path |
| `seed` | `RandSeed` |
| `sim_period` | `SimPeriod` |
| `pedestrian_input_key` | input object to modify |
| `ped_volume_1` | first interval demand |
| `desired_speed_factor` | optional area/type speed factor applied by template |
| `route_factor` | optional route relative-flow factor |
| `results_dir` | per-run output directory |

The manifest should be committed with the analysis code when possible.

## Runtime Intervention

Use breakpoints when changing values during simulation:

```python
sim.SetAttValue("SimBreakAt", 300)
sim.RunContinuous()
ped_input.SetAttValue("Volume(1)", 600)
sim.SetAttValue("SimBreakAt", 600)
sim.RunContinuous()
```

Only edit attributes that the CHM marks editable during simulation. Otherwise, reset, edit before running, and rerun.

## Result Table

A useful batch result row usually includes:

| Field | Example |
| --- | --- |
| run metadata | `run_id`, `scenario`, `network_path`, `vissim_version` |
| factors | seed, input volume, route split, speed factor |
| runtime state | sim period, result folder, script name |
| demand metrics | `PedEnt`, `PedArr`, `PedAct` |
| performance metrics | travel time, speed, density, flow, stops |
| validation fields | completed flag, error message, elapsed wall time |

Do not report only animation observations as results. Use COM evaluation attributes, exported records, or downstream trajectory analysis.

## Failure Recovery

For long batches:

- Write results incrementally after each run.
- Catch COM errors per run and continue only if state can be reset by reloading the network.
- Avoid saving the source `.inpx` unless the run intentionally creates a new network file.
- Use a fresh result folder for each run to avoid mixing database files.
- Log every object key and attribute changed.
