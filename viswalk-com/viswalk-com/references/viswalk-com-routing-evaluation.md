# Viswalk-COM Routing And Evaluation

This reference covers pedestrian routing decisions, routes, route locations, and measurements.

## Static Pedestrian Routes

Static routes start at a routing decision on an area:

```python
origin = vissim.Net.Areas.ItemByKey(1)
dest = vissim.Net.Areas.ItemByKey(2)

decision = vissim.Net.PedestrianRoutingDecisionsStatic.AddPedestrianRoutingDecisionStatic(0, origin)
route = decision.PedRoutSta.AddPedestrianRouteStaticOnArea(0, dest)
route.SetAttValue("RelFlow(1)", 1.0)
```

Intermediate route locations are child objects on the route:

```python
via = vissim.Net.Areas.ItemByKey(3)
route.PedRoutLoc.AddPedestrianRouteLocationOnArea(0, via)
```

Use ramp variants when routing through ramps/stairs:

```python
route_on_ramp = decision.PedRoutSta.AddPedestrianRouteStaticOnRamp(0, ramp)
route_on_ramp.PedRoutLoc.AddPedestrianRouteLocationOnArea(0, dest)
```

## Partial Pedestrian Routes

Partial routes are used when pedestrians should make downstream choices at route decision points:

```python
partial_decision = vissim.Net.PedestrianRoutingDecisionsPartial.AddPedestrianRoutingDecisionPartial(0, origin)
partial_route = partial_decision.PedRoutPart.AddPedestrianRoutePartialOnArea(0, dest)
partial_route.PedRoutLoc.AddPedestrianRouteLocationOnArea(0, via)
```

Before coding partial routing, clarify:

| Question | Why |
| --- | --- |
| What is the decision area? | route decisions are attached to areas |
| What are candidate destinations? | each route needs a destination area or ramp |
| Are choices fixed, logit, or dynamic? | attributes differ by path choice method |
| Which pedestrian classes apply? | route decisions can filter by classes |
| Which time intervals apply? | route flows can be interval-indexed |

## Area And Class Filters

Routing decisions expose `PedClasses` collections. Apply class filters only when the scenario needs different behavior by pedestrian class. Otherwise leave filters broad and document that routes apply to all relevant pedestrians.

## Travel Time Measurements

Create travel-time measurements before running:

```python
tt = vissim.Net.PedestrianTravelTimeMeasurements.AddPedestrianTravelTimeMeasurement(
    0,
    start_area,
    end_area,
)
tt.SetAttValue("Name", "concourse_to_exit")
```

The measurement attributes include start and end point/location fields, pedestrian counts, and result attributes. Many result attributes require subattribute notation for simulation run, time interval, and class. Use the COM Help attribute page or Vissim list headers to confirm the exact string.

## Area Measurements

Area measurements provide density, speed, count, stop, orientation, and nearest-neighbor metrics over configured sections/areas. Use them when the analysis asks for local crowd state rather than only travel time.

Common area measurement result attributes include:

| Attribute | Meaning |
| --- | --- |
| `DensAvg`, `DensMin`, `DensMax` | density |
| `SpeedAvg`, `SpeedMin`, `SpeedMax` | speed |
| `NumPedsAvg`, `NumPedsMin`, `NumPedsMax` | pedestrian counts |
| `ExperDensAvg` | experienced density |
| `NearNeighbDistAvg` | nearest-neighbor distance |
| `OrigCnt`, `DestCnt` | origin and destination counts |

## Pedestrian Records

`IPedestrianRecord` configures pedestrian record output. Useful attributes include `FromTime`, `ToTime`, `Resolution`, `FilterType`, `WriteFile`, and `WriteDatabase`. Configure record output before the run.

Use selected attributes when the downstream workflow needs per-pedestrian trajectories or states. If the final analysis is density/speed/flow, consider whether PedPy should consume exported trajectories after the run.

## Network Performance

Pedestrian network performance attributes include entered, arrived, active pedestrians, average density, flow, speed, travel time, stops, and stop time. These are useful for high-level scenario comparisons, but they can hide local bottlenecks. Pair them with area or travel-time measurements for interpretation.

## Result Extraction Pattern

Use a small wrapper to make subattribute assumptions visible:

```python
def read_att(obj, attr):
    try:
        return obj.AttValue(attr)
    except Exception as exc:
        raise RuntimeError(f"Could not read {attr} from {obj}") from exc

rows = []
for area in vissim.Net.Areas.GetAll():
    rows.append({
        "area_no": area.AttValue("No"),
        "area_name": area.AttValue("Name"),
        "num_peds_avg": area.AttValue("NumPedsAvg"),
        "density": area.AttValue("Dens"),
    })
```

For evaluation attributes with subattributes, do not guess. First check the Vissim list header or query the CHM attribute page.
