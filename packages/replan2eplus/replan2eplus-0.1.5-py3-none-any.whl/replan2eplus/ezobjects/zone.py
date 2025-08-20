from eppy.bunch_subclass import EpBunch
from dataclasses import dataclass, field
from replan2eplus.errors import BadlyFormatedIDFError
from replan2eplus.ezobjects.base import EZObject

import replan2eplus.epnames.keys as epkeys
from replan2eplus.ezobjects.surface import Surface
from typing import Callable, Iterable, TypeVar, Any
from itertools import groupby

from replan2eplus.geometry.directions import WallNormal
from utils4plans.lists import chain_flatten

T = TypeVar("T")


# TODO move to utils4plans..
def sort_and_group_objects_dict(
    lst: Iterable[T], fx: Callable[[T], Any]
) -> dict[Any, list[T]]:
    sorted_objs = sorted(lst, key=fx)
    d = {}
    for k, g in groupby(sorted_objs, fx):
        d[k] = [i for i in list(g)]
    return d


@dataclass
class DirectedSurfaces:
    NORTH: list[Surface]
    EAST: list[Surface]
    SOUTH: list[Surface]
    WEST: list[Surface]
    UP: list[Surface]
    DOWN: list[Surface]


@dataclass
class Zone(EZObject):
    _epbunch: EpBunch
    expected_key: str = epkeys.ZONE
    surfaces: list[Surface] = field(default_factory=list)

    @property
    def room_name(self):
        return self._dname.plan_name

    @property
    def zone_name(self):  # idf name?
        return self._idf_name

    @property
    def surface_names(self):
        return [i.surface_name for i in self.surfaces]

    @property
    def subsurface_names(self) -> list[str]:
        return chain_flatten(
            [i.subsurface_names for i in self.surfaces if i.subsurface_names]
        )

    @property
    def directed_surfaces(self):
        d: dict[WallNormal, list[Surface]] = sort_and_group_objects_dict(
            self.surfaces, lambda x: x.direction
        )
        d_names = {k.name: v for k, v in d.items()}
        return d_names  # DirectedSurfaces(**d_names)

    @property
    def domain(self):
        floors = self.directed_surfaces[WallNormal.DOWN.name]
        assert len(floors) == 1, BadlyFormatedIDFError(
            f"Zone {self.zone_name} has 0 or more than 2 floors!: {floors}"
        )
        return floors[0].domain  # TODO check the plane..
