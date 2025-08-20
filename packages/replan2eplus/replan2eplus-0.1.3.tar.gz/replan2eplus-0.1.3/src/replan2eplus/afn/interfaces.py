from replan2eplus.ezobjects.subsurface import Subsurface
from replan2eplus.ezobjects.zone import Zone
from replan2eplus.idfobjects.afn import (
    AFNSimpleOpening,
    AFNSimulationControl,
    AFNSurface,
    AFNZone,
)


from dataclasses import dataclass


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
