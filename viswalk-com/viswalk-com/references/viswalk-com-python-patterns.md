# Viswalk-COM Python Patterns

Use these patterns when writing Python automation for Vissim/Viswalk COM.

## Environment

Install and verify `pywin32` in the Python interpreter that will run the automation:

```powershell
python -m pip install pywin32
python -c "import win32com.client; print('pywin32 ok')"
```

COM automation is Windows-only and requires a registered Vissim installation. If multiple Vissim versions are installed, start with the unversioned ProgID and use a version-specific ProgID only after verifying it is registered locally.

## Connect

```python
import win32com.client as com

vissim = com.gencache.EnsureDispatch("Vissim.Vissim")
# Use com.Dispatch("Vissim.Vissim") after wrappers are generated if startup speed matters.
```

For advanced scripts, constants can be accessed from the generated wrapper module, but most Viswalk automation is clearer with documented string attributes.

## Load Network And Layout

```python
from pathlib import Path

network_path = Path(r"C:\models\station.inpx")
layout_path = Path(r"C:\models\station.layx")

vissim.LoadNet(str(network_path), False)
if layout_path.exists():
    vissim.LoadLayout(str(layout_path))
```

The second `LoadNet` argument controls whether objects are read additionally. Use `False` unless the user explicitly wants to merge network elements.

## Read And Write Attributes

```python
area = vissim.Net.Areas.ItemByKey(1)
print(area.AttValue("Name"))
area.SetAttValue("Name", "Main concourse")
```

Attributes with time intervals use subscript notation:

```python
ped_input = vissim.Net.PedestrianInputs.ItemByKey(1)
ped_input.SetAttValue("Volume(1)", 1200)
ped_input.SetAttValue("Cont(2)", False)
ped_input.SetAttValue("Volume(2)", 900)
```

The exact attribute and subattribute syntax comes from the COM Help or from English Vissim list headers.

## Convert COM Tuples

Many pywin32 calls return tuples. Convert before editing:

```python
def to_list(value):
    if isinstance(value, (tuple, list)):
        return [to_list(item) for item in value]
    return value

rows = to_list(vissim.Net.Areas.GetMultiAttValues("Name"))
rows[0][1] = "Renamed area"
vissim.Net.Areas.SetMultiAttValues("Name", rows)
```

Remember that row `0` in Python is not necessarily object key `1`.

## Batch Read Attributes

Use batch reads for many objects:

```python
attrs = ("No", "Name", "NumPedsAvg", "Dens")
area_rows = vissim.Net.Areas.GetMultipleAttributes(attrs)
```

For live pedestrians during a run:

```python
ped_attrs = ("No", "CoordCentX", "CoordCentY", "Speed", "DesSpeed")
ped_rows = vissim.Net.Pedestrians.GetMultipleAttributes(ped_attrs)
```

## Run Simulation

```python
sim = vissim.Simulation
sim.SetAttValue("RandSeed", 1001)
sim.SetAttValue("SimPeriod", 900)
sim.SetAttValue("UseMaxSimSpeed", True)
sim.RunContinuous()
```

For interventions:

```python
sim.SetAttValue("SimBreakAt", 120)
sim.RunContinuous()
# mutate editable attributes here
sim.SetAttValue("SimBreakAt", 240)
sim.RunContinuous()
```

Use `RunSingleStep()` when the script needs step-level control.

## Safe GUI And Cleanup Pattern

```python
try:
    vissim.SuspendUpdateGUI()
    # network edits
finally:
    vissim.ResumeUpdateGUI()
```

Only call `vissim.Exit()` when the user has approved closing the Vissim instance.

## COM Error Handling

```python
try:
    ped_input.SetAttValue("Volume(1)", 1200)
except Exception as exc:
    raise RuntimeError(
        "Failed to set PedestrianInput 1 Volume(1). "
        "Check editability, time interval, and simulation state."
    ) from exc
```

Good error messages include:

| Context | Include |
| --- | --- |
| object lookup | container path and key |
| attribute write | object path, attribute name, value, simulation state |
| method call | method name and parameter objects |
| file load | absolute path and `LoadNet` additional flag |

## Result Folder Pattern

```python
results_dir = Path("results") / "run_1001"
results_dir.mkdir(parents=True, exist_ok=True)
vissim.SetResultsFolder(str(results_dir))
```

Set result folders before running. For batch experiments, use one folder per run or a database naming scheme that cannot collide.
