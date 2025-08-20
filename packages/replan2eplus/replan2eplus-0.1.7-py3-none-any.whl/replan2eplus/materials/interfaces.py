from dataclasses import dataclass
from typing import NamedTuple


class Material(NamedTuple):
    name: str
    # TODO this will have inheritance -> there are many types of materials!


class Construction(NamedTuple):
    name: str
    materials: list[Material]

    def create_construction(self, arg):
        pass


@dataclass
class BaseConstructionSet:
    default: Construction
    interior: Construction | None = None
    exterior: Construction | None = None

    def __post_init__(self):
        if not self.interior:
            self.interior = self.default
        if not self.exterior:
            self.exterior = self.default

@dataclass
class EPConstructionSet:
    wall: BaseConstructionSet
    roof: BaseConstructionSet
    floor: BaseConstructionSet
    window: BaseConstructionSet
    door: BaseConstructionSet

    # TODO check that the window construction set is valid.. ie has window materials.. 
# @dataclass
# class GroupedConstructionSet:
#     construction: Construction

# think about -> whose responsibility is it to expand?? 

