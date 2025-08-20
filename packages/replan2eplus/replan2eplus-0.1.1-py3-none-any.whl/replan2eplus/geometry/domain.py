from dataclasses import dataclass
from replan2eplus.geometry.coords import Coord
from replan2eplus.geometry.nonant import Nonant
from typing import Literal, NamedTuple
from replan2eplus.geometry.domain_calcs import (
    BaseDomain,
    calculate_cardinal_points,
    calculate_corner_points,
)
from replan2eplus.geometry.range import compute_multirange, expand_range


AXIS = Literal["X", "Y", "Z"]


class Plane(NamedTuple):
    axis: AXIS
    location: float


@dataclass(frozen=True)
class Domain(BaseDomain):
    plane: Plane | None = None

    @property
    def area(self):
        return self.horz_range.size * self.vert_range.size

    @property
    def aspect_ratio(self):
        return self.horz_range.size / self.vert_range.size

    @property
    def centroid(self):
        return Coord(self.horz_range.midpoint, self.vert_range.midpoint)

    @property
    def cardinal(self):
        return calculate_cardinal_points(self)  # TODO

    @property
    def corner(self):  # TODO should these be anscestors?
        return calculate_corner_points(self)  # TODO

    # @property
    # def bounds(self):
    #     return self.corner.tuple_list

    @property
    def nonant(self):
        return Nonant(self.horz_range.trirange, self.vert_range.trirange)  # TODO


def expand_domain(domain: Domain, factor: float):
    horz_range = expand_range(domain.horz_range, factor)
    vert_range = expand_range(domain.vert_range, factor)
    return Domain(horz_range, vert_range)


def compute_multidomain(domains: list[Domain]):
    horz_range = compute_multirange([i.horz_range for i in domains])
    vert_range = compute_multirange([i.vert_range for i in domains])
    return Domain(horz_range, vert_range)


# @dataclass
# class MultiDomain:
#     domains: list[Domain]

#     @property
#     def total_domain(self):
#         min_x = min([i.horz_range.min for i in self.domains])
#         max_x = max([i.horz_range.max for i in self.domains])
#         min_y = min([i.vert_range.min for i in self.domains])
#         max_y = max([i.vert_range.max for i in self.domains])
#         return Domain(Range(min_x, max_x), Range(min_y, max_y))
