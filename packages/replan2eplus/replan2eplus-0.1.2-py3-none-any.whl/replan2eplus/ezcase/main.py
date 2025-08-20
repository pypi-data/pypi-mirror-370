from dataclasses import dataclass
from pathlib import Path
from replan2eplus.idfobjects.idf import IDF
from replan2eplus.subsurfaces.interfaces import SubsurfaceInputs
from replan2eplus.subsurfaces.presentation import create_subsurfaces
from replan2eplus.zones.interfaces import Room
from replan2eplus.zones.presentation import create_zones


@dataclass 
class EZCase:
    path_to_idd: Path
    path_to_initial_idf: Path

    # TODO: do these need to be initialized here?
    # path_to_weather: Path
    # path_to_analysis_period: AnalysisPeriod

    def initialize_idf(self):
        self.idf = IDF(self.path_to_idd, self.path_to_initial_idf)
        return self.idf

    def add_zones(self, rooms: list[Room]):
        # TODO - check that idf exists!
        self.zones, self.surfaces = create_zones(self.idf, rooms)
        # when do constructuins, these surfaces will be updated..

    def add_subsurfaces(self, inputs: SubsurfaceInputs):
        self.subsurfaces = create_subsurfaces(inputs, self.zones, self.idf)


if __name__ == "__main__":
    pass
