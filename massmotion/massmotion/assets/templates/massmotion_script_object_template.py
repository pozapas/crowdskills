"""MassMotion internal script-object template.

Paste this into a MassMotion script object. It expects to run inside MassMotion
or MassMotionConsole with access to the current project.
"""

from massmotion_11_0 import *


def ensure_rect_floor(project, name, corners):
    if project.has_object(name):
        print("{} already exists".format(name))
        return project.get_floor(name)
    geometry = MeshGeometry.create_flat_polygon(0.0, [Vec2d(x, y) for x, y in corners])
    floor = project.create_floor(name, geometry)
    print("Created " + name)
    return floor


def ensure_portal(project, name, corners):
    if project.has_object(name):
        print("{} already exists".format(name))
        return project.get_portal(name)
    geometry = MeshGeometry.create_flat_polygon(0.02, [Vec2d(x, y) for x, y in corners])
    portal = project.create_portal(name, geometry)
    print("Created " + name)
    return portal


def ensure_journey(project, name, origin_portal, destination_portal, profile_name="DefaultProfile"):
    if project.has_object(name):
        print("{} already exists".format(name))
        return project.get_journey(name)
    journey = project.create_journey(name)
    journey.set_profile(project.get_profile(profile_name).get_id())
    journey.set_population_count(100)
    journey.set_arrive_evenly_spaced(120)
    journey.set_absolute_start_time(60)
    journey.set_origins([origin_portal.get_id()])
    journey.set_lowest_cost_destinations([destination_portal.get_id()])
    print("Created " + name)
    return journey


def main():
    project = Project.get_current_project()
    floor = ensure_rect_floor(
        project,
        "ScriptedFloor",
        [(0, 0), (10, 0), (10, 30), (0, 30)],
    )
    origin = ensure_portal(project, "ScriptedPortalA", [(2, 28), (8, 28), (8, 29), (2, 29)])
    destination = ensure_portal(project, "ScriptedPortalB", [(2, 1), (8, 1), (8, 2), (2, 2)])
    ensure_journey(project, "ScriptedJourney", origin, destination)
    print("Script finished for " + floor.get_name())


main()
