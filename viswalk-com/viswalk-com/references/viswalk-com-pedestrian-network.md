# Viswalk-COM Pedestrian Network

This reference covers pedestrian network construction and mutation through Python COM.

## Build Order

For a network created or heavily edited by COM, use this order:

1. Set units and create base data.
2. Create levels if needed.
3. Create pedestrian areas, ramps/stairs, and obstacles.
4. Create pedestrian types, classes, walking behaviors, and area behavior types.
5. Create desired-speed distributions and pedestrian compositions.
6. Create pedestrian inputs.
7. Create routing decisions and routes.
8. Create measurements.
9. Set simulation parameters and run.

Existing `.inpx` files often already contain most base data. In that case, inspect and reuse objects rather than adding duplicates.

## Units

Vissim coordinates are in meters. Attribute units for speed, acceleration, and lengths can depend on current unit settings. For scripted studies, either assert the current units or set them explicitly before creating objects.

Example pattern from PTV examples:

```python
for attr in ("UnitAccel", "UnitLenLong", "UnitLenShort", "UnitLenVeryShort", "UnitSpeed", "UnitSpeedSmall"):
    vissim.Net.NetPara.SetAttValue(attr, 0)  # 0 means metric in the PTV example
```

Do not change units in a user's existing calibrated network without asking.

## Base Data

Common creation calls:

```python
ped_type = vissim.Net.PedestrianTypes.AddPedestrianType(0)
ped_class = vissim.Net.PedestrianClasses.AddPedestrianClass(0)
walk_behavior = vissim.Net.WalkingBehaviors.AddWalkingBehavior(0)
area_behavior = vissim.Net.AreaBehaviorTypes.AddAreaBehaviorType(0)
area_behavior.AreaBehavTypeElements.AddAreaBehaviorTypeElement(ped_class)
```

Pedestrian compositions connect pedestrian types to desired-speed distributions:

```python
ped_comp = vissim.Net.PedestrianCompositions.AddPedestrianComposition(
    0,
    [ped_type, vissim.Net.DesSpeedDistributions.ItemByKey(5)],
)
```

If adding multiple relative flows, verify that relative flow values sum to the intended total.

## Areas And Geometry

Add areas with WKT:

```python
area = vissim.Net.Areas.AddArea(0, "POLYGON((0 0, 10 0, 10 5, 0 5, 0 0))")
```

Quality checks:

| Check | Why it matters |
| --- | --- |
| Closed WKT ring | invalid polygons may fail or create wrong geometry |
| Meter coordinates | Viswalk area coordinates are spatial, not screen pixels |
| Enough area for demand | overcrowded starts cause unrealistic behavior or insertion failures |
| Correct level | pedestrian routes across levels need ramps/stairs/elevators |
| Area behavior type | behavior, speed, and class assumptions should match the scenario |

Use `Area.AttValue("Geometry")`, `Area.AttValue("No")`, and `Area.AttValue("Name")` to confirm creation.

## Obstacles And Ramps

Obstacles are WKT polygons that restrict walkable space:

```python
obstacle = vissim.Net.Obstacles.AddObstacle(0, "POLYGON((4 1, 6 1, 6 2, 4 2, 4 1))")
```

Ramps/stairs connect walkable areas or levels:

```python
ramp = vissim.Net.Ramps.AddRamp(0, "POLYGON((10 0, 12 0, 12 5, 10 5, 10 0))")
```

After adding a ramp, route through it explicitly when the route should use it.

## Pedestrian Inputs

Create a pedestrian input on an area:

```python
ped_input = vissim.Net.PedestrianInputs.AddPedestrianInput(0, area)
ped_input.SetAttValue("PedComp", ped_comp)
ped_input.SetAttValue("Volume(1)", 1200)
```

For multiple intervals:

```python
ped_input.SetAttValue("Cont(2)", False)
ped_input.SetAttValue("Volume(2)", 800)
```

Check the time interval set for pedestrian inputs before using interval numbers beyond `1`.

## Live Pedestrian Insertion

Insert a pedestrian on an area with automatic placement:

```python
ped = vissim.Net.Pedestrians.AddPedestrianOnArea(ped_type, area, 1.35)
```

Insert at a coordinate relative to the area center:

```python
ped = vissim.Net.Pedestrians.AddPedestrianOnAreaAtCoordinate(
    ped_type,
    area,
    1.0,   # relative x in meters
    -0.5,  # relative y in meters
    1.0,   # orientation x
    0.0,   # orientation y
    1.35,  # desired speed in current large-speed unit
    0.0,   # current speed
)
```

Use live insertion sparingly. For ordinary demand studies, pedestrian inputs are more reproducible.

## Inspection Helpers

```python
def summarize_container(container, attrs=("No", "Name")):
    return list(container.GetMultipleAttributes(attrs))

areas = summarize_container(vissim.Net.Areas, ("No", "Name", "NumPedsAvg", "Dens"))
inputs = summarize_container(vissim.Net.PedestrianInputs, ("No", "Name", "Area", "PedComp"))
```

Use inspection before mutation and after mutation. It is easier to debug an incorrect object key before a long simulation run.
