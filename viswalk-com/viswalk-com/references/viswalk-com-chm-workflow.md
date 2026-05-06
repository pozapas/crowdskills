# Viswalk-COM CHM Workflow

The Vissim COM manual is a compiled HTML Help file (`.chm`). It cannot be read like the PDF/manual sources used by several other skills. The practical solution is to decompile it locally into HTML topics, index those topics, and then use the compact index to find exact COM object, method, property, attribute, and relation pages.

## Manual Source

The workspace manual is:

```text
Manuals\Viswalk\Vissim 2025 - COM.chm
```

The file contains the PTV Vissim COM reference. Viswalk pedestrian objects are embedded in the Vissim object library under interfaces such as `IArea`, `IPedestrianInput`, `IPedestrianRoutingDecisionStatic`, `IPedestrianRouteStatic`, `IPedestrian`, `IAreaMeasurement`, and `IPedestrianTravelTimeMeasurement`.

## Extraction Method

On Windows, `hh.exe` can decompile a CHM:

```powershell
$src = Resolve-Path ".\Manuals\Viswalk\Vissim 2025 - COM.chm"
$tmp = Join-Path $env:TEMP "Vissim2025_COM.chm"
$out = Join-Path $env:TEMP "viswalk_com_chm"
Copy-Item -LiteralPath $src -Destination $tmp -Force
New-Item -ItemType Directory -Force -Path $out | Out-Null
& "$env:WINDIR\hh.exe" -decompile $out $tmp
```

Copying the CHM to a local temp path is useful when cloud-synced folders, blocked download marks, or paths with spaces cause silent extraction failures. If no files appear immediately, wait a few seconds and check the output folder again.

## Extracted Structure

Expect thousands of HTML pages:

| File pattern | Meaning |
| --- | --- |
| `VISSIMLIB_P.html` | project overview and top-level class list |
| `VISSIMLIB~IObject.html` | interface summary, public methods, public properties |
| `VISSIMLIB~IObject_attributes.html` | COM attributes usable through `AttValue` and `SetAttValue` |
| `VISSIMLIB~IObject_relations.html` | parent/child/reference relationships |
| `VISSIMLIB~IObject~Method.html` | method signature and parameters |
| `VISSIMLIB~IObject~Property.html` | property signature and return type |
| `.hhc`, `.hhk` | table of contents and keyword index |

Do not commit the full decompiled manual unless the user explicitly wants a local archive. The skill should keep compact references and scripts, not copied vendor documentation.

## Search Strategy

Use terms that match interface names and object concepts:

```powershell
python .\viswalk-com\viswalk-com\scripts\index_com_chm.py ".\Manuals\Viswalk\Vissim 2025 - COM.chm" --query Pedestrian --query Route --out com_ped_routes.json
```

By default, query filtering uses topic filenames, which is fast because COM Help filenames encode most interface and member names. Add `--body-search` when searching for attribute descriptions or terms that may appear only inside a page body.

Useful query terms:

| Task | Query terms |
| --- | --- |
| Walkable areas | `Area`, `IArea`, `AddArea`, `Geometry`, `Points` |
| Demand | `PedestrianInput`, `Volume`, `TimeIntPedVols`, `PedestrianComposition` |
| Static routing | `PedestrianRoutingDecisionStatic`, `PedestrianRouteStatic`, `PedRoutSta` |
| Partial routing | `PedestrianRoutingDecisionPartial`, `PedestrianRoutePartial`, `RouteChoiceArea` |
| Live pedestrians | `IPedestrian`, `AddPedestrianOnArea`, `AddPedestrianOnAreaAtCoordinate` |
| Measurements | `AreaMeasurement`, `PedestrianTravelTimeMeasurement`, `PedestrianRecord` |
| Simulation control | `ISimulation`, `RunContinuous`, `RunSingleStep`, `RandSeed`, `SimPeriod` |

## Manual Grounding Rule

When generating code, use this order:

1. Prefer exact method signatures from the extracted CHM topic.
2. Prefer installed PTV example scripts for Python syntax conventions.
3. Use this skill's compact references for common paths and patterns.
4. If an attribute is not found, ask the user to inspect the Vissim list header or query the CHM index.

Do not invent attributes from display names. Vissim COM generally uses English short names such as `No`, `Name`, `Volume(1)`, `RandSeed`, and `SimPeriod`.
