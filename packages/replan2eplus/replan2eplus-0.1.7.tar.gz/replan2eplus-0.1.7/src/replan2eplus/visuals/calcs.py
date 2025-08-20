from typing import Literal, NamedTuple
from replan2eplus.errors import IDFMisunderstandingError
from replan2eplus.ezobjects.subsurface import Subsurface
from replan2eplus.ezobjects.zone import Zone
from replan2eplus.geometry.contact_points import CardinalPoints
from replan2eplus.geometry.coords import Coord
from replan2eplus.geometry.directions import WallNormal, WallNormalNamesList
from replan2eplus.geometry.domain import Domain, Plane
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from dataclasses import dataclass

from replan2eplus.geometry.range import Range


def domain_to_mpl_patch(domain: Domain):
    return Rectangle(
        (domain.horz_range.min, domain.vert_range.min),
        domain.horz_range.size,
        domain.vert_range.size,
        fill=False,
    )


class MPlData(NamedTuple):
    xdata: list[float]
    ydata: list[float]


def split_coords(coords: list[Coord]):
    return MPlData([i.x for i in coords], [i.y for i in coords])


class Alignment(NamedTuple):
    horizontalalignment: Literal["left", "center", "right"]
    verticalalignment: Literal["top", "center", "baseline", "bottom"]
    rotation: Literal["vertical"] | None = None


@dataclass
class Line:
    start: Coord
    end: Coord
    plane: Plane

    @property
    def alignment(self):
        # also depends on if exterior or interiro -> i exterior, always want outside.. but do we even really want labels or just legend? just for testing?
        if self.plane.axis == "X":
            return Alignment("right", "center", "vertical")._asdict()
        else:
            return Alignment("center", "top")._asdict()

    @property
    def to_line2D(self):
        return Line2D(
            *split_coords([self.start, self.end])
        )  # TODO think about cleaning this up..

    @property
    def centroid(self):
        return (
            Range(self.start.x, self.end.x).midpoint,
            Range(self.start.y, self.end.y).midpoint,
        )


# TODO write tests for this!
def domain_to_line(domain: Domain):
    assert domain.plane
    plane = domain.plane
    if plane.axis == "Z":
        raise IDFMisunderstandingError("Can't flatten a domain in the Z Plane!")
    else:
        min_ = domain.horz_range.min
        max_ = domain.horz_range.max
    if plane.axis == "X":
        start = Coord(plane.location, min_)
        end = Coord(plane.location, max_)
    else:
        assert plane.axis == "Y"
        start = Coord(min_, plane.location)
        end = Coord(max_, plane.location)
    return Line(start, end, plane)


# this is a pretty generic fx -> utils4plans -> filter, get1 throw error
def get_zones(name, zones: list[Zone]):
    # NOTE: changing this for studies! 
    possible_zones = [i for i in zones if i.zone_name == name]
    assert len(possible_zones) == 1, f"Name: {name}, poss_zones: {possible_zones}"
    return possible_zones[0]


def subsurface_connection(
    subsurface: Subsurface, zones: list[Zone], cardinal_coords: CardinalPoints
):
    space_a, space_b = subsurface.edge
    middle_coord = Coord(*domain_to_line(subsurface.domain).centroid)
    zone_a = get_zones(space_a, zones)
    coord_a = zone_a.domain.centroid
    if space_b in WallNormal:
        assert isinstance(space_b, WallNormal)
        coord_b = cardinal_coords.dict_[space_b.name]
    else:
        zone_b = get_zones(space_b, zones)
        coord_b = zone_b.domain.centroid

    points = [coord_a, middle_coord, coord_b]
    return Line2D(*split_coords(points))
