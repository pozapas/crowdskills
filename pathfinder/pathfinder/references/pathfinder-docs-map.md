# Pathfinder Docs Map

Primary source:

```text
https://www.thunderheadeng.com/docs/2026-1/pathfinder/introduction/
```

The 2026.1 manual is versioned, crawlable HTML. Use the online docs as the source of truth and keep only compact references in this skill.

## Top-Level Sections

| Section | URL | Use |
| --- | --- | --- |
| Introduction | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/introduction/` | scope, assumptions, output overview |
| Examples | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/examples/` | tutorial workflows |
| Geometry | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/geometry/` | imported geometry, rooms, doors, stairs, ramps |
| Profiles | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/profiles/` | occupant profile properties |
| Behaviors | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/behaviors/` | behavior actions and goals |
| Occupants | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/occupants/` | occupant creation and initial conditions |
| Movement Groups | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/groups/` | groups and organized movement |
| Queues | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/queues/` | queueing and service points |
| Targets | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/targets/` | occupant target workflows |
| Triggers | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/triggers/` | dynamic behavior triggers |
| Simulation | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/simulation/` | parameters, starting, stopping, command-line runs |
| Output | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/output/` | summary, histories, measurements, JSON/CSV |
| Advanced | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/advanced/` | scripting API, Monte Carlo, assisted evacuation |
| Troubleshooting | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/troubleshooting/` | common problems |
| Results Viewer | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/results/` | visualization |
| Appendices | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/appendices/` | technical details and references |

## High-Value Pages

| Topic | URL |
| --- | --- |
| Simulation command line | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/simulation/starting/` |
| Simulation parameters | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/simulation/parameters/` |
| Output overview | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/output/` |
| Summary report | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/output/summary/` |
| Occupant history | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/output/occupant-history/` |
| Monte Carlo | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/advanced/monte-carlo/` |
| Scripting API | `https://www.thunderheadeng.com/docs/2026-1/pathfinder/advanced/scripting/` |

## Ingestion Strategy

Use `scripts/crawl_pathfinder_docs.py` to create a compact local index:

```powershell
python .\pathfinder\pathfinder\scripts\crawl_pathfinder_docs.py --start https://www.thunderheadeng.com/docs/2026-1/pathfinder/introduction/ --max-pages 80 --out pathfinder_docs.json --markdown pathfinder_docs.md
```

Crawler rules:

| Rule | Reason |
| --- | --- |
| Stay under `/docs/2026-1/pathfinder/` | avoid crawling unrelated products |
| Store source URL and title | preserve attribution and version |
| Extract headings and code blocks | enough for routing without copying the manual |
| Keep summaries short | avoid vendor-doc duplication |
| Re-crawl when the docs version changes | versioned docs can change between releases |

When answering exact manual questions, cite the online page URL and quote minimally.
