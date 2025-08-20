from dataclasses import dataclass
from typing import NamedTuple, Literal, TypeVar
from replan2eplus.ezobjects.subsurface import Subsurface
from replan2eplus.ezobjects.zone import Zone
from replan2eplus.geometry.contact_points import CornerEntries
from replan2eplus.geometry.directions import WallNormal, WallNormalNamesList
from replan2eplus.geometry.domain_create import Dimension
from replan2eplus.geometry.nonant import NonantEntries
from replan2eplus.idfobjects.afn import (
    AFNSimpleOpening,
    AFNSimulationControl,
    AFNSurface,
    AFNZone,
)


class Edge(NamedTuple):
    u: str
    v: str

    @property
    def is_directed_edge(self):
        return self.u in WallNormalNamesList or self.v in WallNormalNamesList

    @property
    def as_tuple(self):
        return (self.u, self.v)

    @property
    def sorted_directed_edge(self):
        if self.is_directed_edge:
            zone, drn = sorted(
                [self.u, self.v], key=lambda x: x in WallNormalNamesList
            )  # NOTE: order is (false=0, true=1)
            return (zone, WallNormal[drn])
        else:
            raise Exception("This is not a directed edge!")


class ZoneDirectionEdge(NamedTuple):
    u: str
    v: WallNormal


class ZoneEdge(NamedTuple):
    u: str
    v: str


class Location(NamedTuple):
    nonant_loc: NonantEntries
    nonant_contact_loc: CornerEntries
    subsurface_contact_loc: CornerEntries


class Details(NamedTuple):
    # edge: Edge
    dimension: Dimension
    location: Location
    type_: Literal["Door", "Window"]


T = TypeVar("T")


# TODO move to utils4plans
def flatten_dict_map(dict_map: dict[int, list[int]]) -> list[tuple[int, int]]:
    res = []
    for k, v in dict_map.items():
        res.extend([(k, input) for input in v])
    return res


class IndexPair(NamedTuple):
    detail_ix: int
    edge_ix: int


@dataclass
class SubsurfaceInputs:
    edges: dict[int, Edge]
    details: dict[int, Details]
    map_: dict[int, list[int]]

    @property
    def _index_pairs(self):
        flattened_map = flatten_dict_map(self.map_)
        return (IndexPair(*i) for i in flattened_map)

    @property
    def _zone_edges(self):
        return {
            k: ZoneEdge(*v) for k, v in self.edges.items() if not v.is_directed_edge
        }

    @property
    def _zone_drn_edges(self):
        return {
            k: ZoneDirectionEdge(*v.sorted_directed_edge)
            for k, v in self.edges.items()
            if v.is_directed_edge
        }

    def _replace_indices(self, edge_dict: dict[int, T]):
        return [
            (edge_dict[i.edge_ix], self.details[i.detail_ix])
            for i in self._index_pairs
            if i.edge_ix in edge_dict.keys()
        ]

    @property
    def zone_pairs(self):
        return self._replace_indices(self._zone_edges)

    @property
    def zone_drn_pairs(self):
        return self._replace_indices(self._zone_drn_edges)


@dataclass
class AFNInputs:
    zones_: list[Zone]
    surfaces: list[Subsurface]  # or airboundaries!

    @property
    def sim_control(self):
        return AFNSimulationControl()

    @property
    def zones(self):
        # TODO if there was a parameter map would apply here..
        return [AFNZone(i.zone_name) for i in self.zones_]

    @property
    def surfaces_and_openings(self):
        # Air boundary is allowed by venting is constant, on..
        openings: dict[str, AFNSimpleOpening] = {
            i.subsurface_name: AFNSimpleOpening(f"SimpleOpening__{i.subsurface_name}")
            for i in self.surfaces
        }
        openings_list = list(openings.values())
        surfaces = [
            AFNSurface(surface_name, opening.Name)
            for surface_name, opening in openings.items()
        ]
        return surfaces, openings_list
