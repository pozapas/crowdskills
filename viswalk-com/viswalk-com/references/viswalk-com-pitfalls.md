# Viswalk-COM Pitfalls

## Environment

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Invalid class string` | Vissim COM server not registered or wrong ProgID | start Vissim once, repair installation, use registered ProgID |
| `No module named win32com` | `pywin32` missing in the active interpreter | `python -m pip install pywin32` |
| `EnsureDispatch` wrapper errors | stale generated COM cache | clear pywin32 gen cache or use `Dispatch` temporarily |
| Vissim opens but script hangs | modal dialog, license prompt, file warning | run once manually and resolve dialogs |

## Object Keys

`ItemByKey(1)` uses the object's `No` key, not its position in a list. `GetAll()[0]` returns the first object in COM enumeration, which might not have key `1`.

When creating objects with key `0`, Vissim auto-assigns a number. Store the returned object:

```python
area = vissim.Net.Areas.AddArea(0, polygon)
area_no = area.AttValue("No")
```

## Attribute Names

Do not use long display names such as `"Number of pedestrians (average)"` in COM calls. Use short English attribute names such as `NumPedsAvg`.

Time-interval attributes use indexed notation such as `Volume(1)` and `RelFlow(1)`.

## Editability

The CHM attribute pages include editability and simulation behavior. Some attributes are read-only or read-only during simulation. If `SetAttValue` fails during a run, check whether the attribute must be set before `RunContinuous`.

## Units

Coordinates are in meters, but speed attributes are in the current unit for large speeds. Document the current unit system when setting desired speeds or reading speeds.

## WKT Geometry

Common geometry failures:

- polygon ring not closed
- comma/space formatting wrong
- self-intersection
- coordinates assigned to the wrong level
- obstacles larger than or outside the area
- route destination area not reachable

Use simple rectangles first, then add complexity.

## Collections Versus Containers

Creation methods are on containers. Relationship properties often return collections. If a property name appears on an object but no `Add...` method exists, inspect whether the child object is owned by a different container.

## Batch Runs

Reload the base network for each run when factors mutate network state. Resetting attributes manually is fragile when routes, random seeds, or results are involved.

## CHM Extraction

If `hh.exe -decompile` produces an empty folder:

1. Copy the CHM to a local temp path.
2. Remove Windows file-blocking marks if present.
3. Use a fresh output directory.
4. Wait a few seconds after `hh.exe` returns.
5. Verify that files like `VISSIMLIB_P.html` and `.hhc/.hhk` exist.

## Measurement Interpretation

Area-level average density and network-level performance can hide local congestion. For pedestrian studies, pair global metrics with local area measurements, travel-time measurements, or exported trajectories.
