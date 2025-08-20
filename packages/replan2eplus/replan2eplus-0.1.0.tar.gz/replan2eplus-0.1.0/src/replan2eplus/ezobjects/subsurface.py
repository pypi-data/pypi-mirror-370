from typing import NamedTuple
from replan2eplus.ezobjects.base import EZObject
from dataclasses import dataclass
import replan2eplus.epnames.keys as epkeys
from replan2eplus.geometry.directions import WallNormal
from replan2eplus.geometry.domain import Domain, Literal
from eppy.bunch_subclass import EpBunch

from replan2eplus.geometry.range import Range
from replan2eplus.ezobjects.surface import Surface

subsurface_options = ["DOOR", "WINDOW", "DOOR:INTERZONE"]

display_map = {"DOOR": "Door", "WINDOW": "Window", "DOOR:INTERZONE": "Door"}


class GenericEdge(NamedTuple):
    space_a: str
    space_b: str | WallNormal


@dataclass
class Subsurface(EZObject):
    _epbunch: EpBunch
    expected_key: str
    surface: Surface
    edge: GenericEdge

    def __post_init__(self):
        assert self.expected_key in subsurface_options

    # def set_edge(self, edge: tuple[str, str]):
    #     self.edge = edge

    def __eq__(self, other):
        if isinstance(other, Subsurface):
            if other.edge == self.edge:
                return True
            # later could include domain.. if have two subsurfaces on one location.. 
        return False

    @property
    def subsurface_name(self):
        return self._epbunch.Name

    @property
    def display_name(self):
        type_ = display_map[self.expected_key]
        return f"{type_}_{self.surface.display_name}"

    @property
    def domain(self):
        surf_domain = self.surface.domain
        surface_min_horz = surf_domain.horz_range.min
        surface_min_vert = surf_domain.vert_range.min

        horz_min = surface_min_horz + float(self._epbunch.Starting_X_Coordinate)
        width = float(self._epbunch.Length)

        vert_min = surface_min_vert + float(self._epbunch.Starting_Z_Coordinate)
        height = float(self._epbunch.Height)

        horz_range = Range(horz_min, horz_min + width)
        vert_range = Range(vert_min, vert_min + height)

        return Domain(horz_range, vert_range, surf_domain.plane)
        # need the surface its on..

    # TODO properties to add: surface, partner obj, connecting zones, "driving zones" (for the purpose of the AFN )
