# Pathfinder Simulation And Batch Runs

Pathfinder simulations can be run in the GUI or from the command line.

## GUI Runs

Use Pathfinder's Run Simulation action from the GUI when:

- The user needs interactive run management.
- They need to select scenarios from the Run Scenarios dialog.
- They want to use pause, resume, cancel, or runtime visualization.
- They are still debugging model setup.

The output folder is created next to the saved `.pth` and named after the model. Multiple scenarios and Monte Carlo variations create nested output folders.

## Command-Line Runs

The docs describe `testsim.bat` in the Pathfinder installation directory.

Single model:

```powershell
& "C:\Program Files\Pathfinder 2026\testsim.bat" "C:\models\case1.pth"
```

Directory of `.pth` files:

```powershell
& "C:\Program Files\Pathfinder 2026\testsim.bat" "C:\models\exported_cases"
```

Multiple directories:

```powershell
& "C:\Program Files\Pathfinder 2026\testsim.bat" "C:\models\a" "C:\models\b"
```

Command-line runs do not provide the management dialog. If the model contains multiple scenarios or Monte Carlo variations, the active scenario runs and no randomization is performed. Export scenarios and Monte Carlo variations to separate files when batch-running them.

## Exported Scenarios And Variations

For multiple scenarios or Monte Carlo variations:

1. In Pathfinder, use File -> Export -> Export Scenarios and Monte Carlo Variations.
2. Select scenarios.
3. Choose an export folder.
4. Run the generated `_run.bat` or use generated `.pth` files in a manifest.
5. Use `_make_plots.bat` when Monte Carlo result plots are needed.

## Monte Carlo

Monte Carlo creates model variations per scenario to examine randomized input effects. Useful variables include randomized positions, randomized profile properties, randomized profiles, occupant filters, and distributions.

Important distinction: Monte Carlo randomization seed is distinct from occupant seeds. Document both when relevant.

## Manifest Workflow

Use `create_pathfinder_run_manifest.py` to create rows with:

| Column | Meaning |
| --- | --- |
| `run_id` | stable run identifier |
| `model_path` | `.pth` or simulator `.txt` |
| `testsim_path` | command-line runner |
| `output_dir` | expected results directory |
| `scenario` | scenario label, if known |
| `variation` | Monte Carlo variation label, if known |
| `notes` | assumptions or filters |

Batch runner templates should write incremental status rows so failed simulations do not erase previous results.
