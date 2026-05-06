# Pathfinder Pitfalls

## Automation Layer Confusion

Pathfinder custom scripts are JavaScript/Java inside the simulator. Python does not control Pathfinder's simulation internals directly. Use Python for external orchestration and analysis.

## Command-Line Runs

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Only one scenario runs | active scenario behavior from command-line run | export scenarios/variations to separate `.pth` files |
| No Monte Carlo randomization | running original multi-variation model directly | export Monte Carlo variations first |
| No management dialog | expected command-line behavior | run from GUI if pause/resume is needed |
| No 3D geometry visualization | geometry file not exported | export imported geometry file when needed |

## Output Missing

Detailed occupant history requires detailed data output on relevant profiles. JSON requires JSON output enabled. Large models can generate large files; choose output frequency deliberately.

## Scripting Issues

| Issue | Fix |
| --- | --- |
| Script editor not visible | launch with `-J-Dex_enable_scripting` |
| script variables conflict | namespace globals |
| stream locked or incomplete | close PrintStream in `sim.onExit` |
| object not found | include group prefix or verify object name |
| restart fails | scripting is not compatible with simulation restart |

## Interpretation

Do not treat completion time as meaningful for occupants who never completed relevant behavior actions. Report stuck or incomplete occupants separately.

Do not compare scenarios if output frequency, time limit, occupant population, or measurement definitions changed unintentionally.

## Monte Carlo

Monte Carlo is for randomized input effects, not geometry modification. Use scenarios for geometry alternatives.

The Monte Carlo randomization seed is distinct from occupant seeds and can generate occupant seeds when profile-property randomization is enabled.
