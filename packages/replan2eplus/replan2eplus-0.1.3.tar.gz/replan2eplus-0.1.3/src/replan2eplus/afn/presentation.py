from replan2eplus.afn.interfaces import AFNInputs
from replan2eplus.ezobjects.subsurface import Subsurface
from replan2eplus.ezobjects.zone import Zone
from replan2eplus.idfobjects.afn import (
    AFNKeys,
)
from replan2eplus.idfobjects.idf import IDF
from replan2eplus.subsurfaces.presentation import chain_flatten
from replan2eplus.subsurfaces.utils import filter_subsurfaces


def select_afn_objects(zones: list[Zone], subsurfaces: list[Subsurface]):
    afn_zones = [i for i in zones if len(i.subsurface_names) >= 2]
    potential_subsurface_names: list[str] = chain_flatten(
        [i.subsurface_names for i in afn_zones]
    )
    potential_subsurfaces = [
        i for i in subsurfaces if i.subsurface_name in potential_subsurface_names
    ]

    # TODO get airboundaries! -> need to do materials first!
    afn_subsurfaces = filter_subsurfaces(potential_subsurfaces)

    return afn_zones, afn_subsurfaces


def create_afn_objects(inputs: AFNInputs, idf: IDF):
    idf.add_afn_simulation_control(inputs.sim_control)

    for zone in inputs.zones:
        idf.add_afn_zone(zone)

    for pair in zip(*inputs.surfaces_and_openings):
        afn_surface, afn_opening = pair
        idf.add_afn_surface(afn_surface)
        idf.add_afn_opening(afn_opening)

    return idf
