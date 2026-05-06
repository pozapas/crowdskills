# Viswalk-COM API Map

This reference maps the COM object hierarchy and the pedestrian-specific surfaces most often needed for Python automation.

## Root Objects

| Python path | COM interface | Purpose |
| --- | --- | --- |
| `Vissim` | `IVissim` | top-level automation server |
| `Vissim.Net` | `INet` | network objects, base data, pedestrian objects, measurements |
| `Vissim.Simulation` | `ISimulation` | simulation parameters and run control |
| `Vissim.Evaluation` | evaluation object | evaluation configuration and result handling |
| `Vissim.Graphics` | graphics object | network window, zoom, GUI behavior |

`IVissim` exposes `LoadNet`, `LoadLayout`, `SaveNet`, `SaveNetAs`, `SetResultsFolder`, `SuspendUpdateGUI`, `ResumeUpdateGUI`, `New`, `Exit`, `Net`, and `Simulation`.

`ISimulation` exposes `RunContinuous`, `RunSingleStep`, `Stop`, and attributes such as `RandSeed`, `SimPeriod`, `SimBreakAt`, `SimRes`, `SimSpeed`, `UseMaxSimSpeed`, and `IsRunning`.

## Pedestrian Containers On `Vissim.Net`

| Path | Interface | Typical use |
| --- | --- | --- |
| `Vissim.Net.Areas` | `IAreaContainer` | walkable pedestrian areas |
| `Vissim.Net.Ramps` | ramp container | ramps and stairs connecting pedestrian areas or levels |
| `Vissim.Net.Obstacles` | obstacle container | non-walkable polygons inside pedestrian spaces |
| `Vissim.Net.Levels` | level container | vertical level assignment |
| `Vissim.Net.PedestrianTypes` | `IPedestrianTypeContainer` | pedestrian type base data and walking behavior reference |
| `Vissim.Net.PedestrianClasses` | `IPedestrianClassContainer` | class filters for routes, area behavior, and evaluation |
| `Vissim.Net.WalkingBehaviors` | walking behavior container | Viswalk behavior parameter sets |
| `Vissim.Net.AreaBehaviorTypes` | `IAreaBehaviorTypeContainer` | behavior by area, class, time interval, walking behavior, desired speed |
| `Vissim.Net.PedestrianCompositions` | `IPedestrianCompositionContainer` | type and desired-speed distribution mixtures for demand |
| `Vissim.Net.PedestrianInputs` | `IPedestrianInputContainer` | pedestrian demand injected on areas |
| `Vissim.Net.PedestrianRoutingDecisionsStatic` | `IPedestrianRoutingDecisionStaticContainer` | origin areas for static pedestrian routes |
| `Vissim.Net.PedestrianRoutingDecisionsPartial` | `IPedestrianRoutingDecisionPartialContainer` | route-choice decision points for partial pedestrian routes |
| `Vissim.Net.Pedestrians` | `IPedestrianContainer` | live pedestrian objects during simulation |
| `Vissim.Net.AreaMeasurements` | `IAreaMeasurementContainer` | density, speed, count, and stop metrics over sections/areas |
| `Vissim.Net.PedestrianTravelTimeMeasurements` | `IPedestrianTravelTimeMeasurementContainer` | travel times between start/end areas |

## Container And Collection Rules

Vissim COM distinguishes containers and collections:

| Surface | Meaning | Add/remove? | Random access |
| --- | --- | --- | --- |
| Container | owns actual objects of that type | yes, through `Add...` and `Remove...` methods | `ItemByKey(key)` |
| Collection | references objects owned somewhere else | usually no | often `GetAll`, iteration, filters |

Use containers for creation. Use collections for traversal, filters, relationships, and fast attribute reads.

## Attribute Access

Use the same pattern on most COM objects:

```python
name = obj.AttValue("Name")
obj.SetAttValue("Name", "new name")
```

Common collection helpers:

| Method | Use |
| --- | --- |
| `GetAll()` | returns all objects in the container or collection |
| `ItemByKey(key)` | returns one object by its `No` key where supported |
| `ItemKeyExists(key)` | checks whether a key exists |
| `GetMultiAttValues(attr)` | reads one attribute for many objects |
| `SetMultiAttValues(attr, values)` | writes one attribute for many rows |
| `GetMultipleAttributes(attrs)` | reads several attributes for many objects |
| `SetMultipleAttributes(attrs, values)` | writes several attributes for multiple rows |
| `SetAllAttValues(attr, value)` | writes the same value to all objects |

The first column returned by `GetMultiAttValues` is a consecutive row number, not necessarily the object `No`.

## Common Method Signatures

| Task | COM method |
| --- | --- |
| Add area | `Vissim.Net.Areas.AddArea(key, wkt_polygon)` |
| Add pedestrian input | `Vissim.Net.PedestrianInputs.AddPedestrianInput(key, area)` |
| Add static routing decision | `Vissim.Net.PedestrianRoutingDecisionsStatic.AddPedestrianRoutingDecisionStatic(key, area)` |
| Add static route on area | `decision.PedRoutSta.AddPedestrianRouteStaticOnArea(key, area)` |
| Add static route on ramp | `decision.PedRoutSta.AddPedestrianRouteStaticOnRamp(key, ramp)` |
| Add route location on area | `route.PedRoutLoc.AddPedestrianRouteLocationOnArea(key, area)` |
| Add route location on ramp | `route.PedRoutLoc.AddPedestrianRouteLocationOnRamp(key, ramp)` |
| Add partial routing decision | `Vissim.Net.PedestrianRoutingDecisionsPartial.AddPedestrianRoutingDecisionPartial(key, area)` |
| Add partial route on area | `decision.PedRoutPart.AddPedestrianRoutePartialOnArea(key, area)` |
| Add pedestrian on area | `Vissim.Net.Pedestrians.AddPedestrianOnArea(ped_type, area, desired_speed)` |
| Add pedestrian at relative coordinate | `Vissim.Net.Pedestrians.AddPedestrianOnAreaAtCoordinate(ped_type, area, relative_x, relative_y, orientation_x, orientation_y, desired_speed, speed)` |
| Remove live pedestrian | `Vissim.Net.Pedestrians.RemovePedestrian(pedestrian_or_no)` |
| Add travel time measurement | `Vissim.Net.PedestrianTravelTimeMeasurements.AddPedestrianTravelTimeMeasurement(key, start_area, end_area)` |

When the manual says a parameter is `Variant`, Python can often pass either an object reference or a key. Prefer object references when the method signature names an interface such as `IArea`.

## High-Value Attribute Names

| Object | Useful attributes |
| --- | --- |
| `ISimulation` | `RandSeed`, `RandSeedIncr`, `SimPeriod`, `SimBreakAt`, `SimRes`, `UseMaxSimSpeed`, `IsRunning`, `SimSec` |
| `IArea` | `No`, `Name`, `Geometry`, `GeometryType`, `AreaBehavType`, `Level`, `Dens`, `NumPedsAvg`, `ExperDens`, `IsQueue` |
| `IPedestrianInput` | `No`, `Name`, `Area`, `PedComp`, `Volume(i)`, `Cont(i)` |
| `IPedestrian` | `No`, `CoordCentX`, `CoordCentY`, `CoordCentZ`, `DesSpeed`, `Speed`, `PedType`, `CurDestNo`, `DistTravTot`, `DwellTm` |
| `IPedestrianType` | `No`, `Name`, `WalkBehav`, `HgtVar`, `LenVar`, `WidVar` |
| `IPedestrianRecord` | `FromTime`, `ToTime`, `Resolution`, `FilterType`, `WriteFile`, `WriteDatabase` |
| `IAreaMeasurement` | `DensAvg`, `SpeedAvg`, `NumPedsAvg`, `ExperDensAvg`, `NearNeighbDistAvg`, `OrigCnt`, `DestCnt` |
| `IPedestrianNetworkPerformanceMeasurement` | `PedEnt`, `PedArr`, `PedAct`, `DensAvg`, `FlowAvg`, `SpeedAvg`, `TravTmAvg`, `StopsAvg` |

Use the CHM attribute page to verify editability and subattribute dimensions before writing.
