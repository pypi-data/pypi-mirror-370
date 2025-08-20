# Material Keys?
from typing import Literal, NamedTuple

material_keys = [
    "MATERIAL",
    "MATERIAL:AIRGAP",
    # "MATERIAL:INFRAREDTRANSPARENT",
    "MATERIAL:NOMASS",
    # "MATERIAL:ROOFVEGETATION",
    # "WINDOWMATERIAL:BLIND",
    "WINDOWMATERIAL:GLAZING",
    # "WINDOWMATERIAL:GLAZING:REFRACTIONEXTINCTIONMETHOD",
    # "WINDOWMATERIAL:GAP",
    # "WINDOWMATERIAL:GAS",
    # "WINDOWMATERIAL:GASMIXTURE",
    # "WINDOWMATERIAL:GLAZINGGROUP:THERMOCHROMIC",
    # "WINDOWMATERIAL:SCREEN",
    # "WINDOWMATERIAL:SHADE",
    # "WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM",
]

MaterialKey = Literal[
    "MATERIAL",
    "MATERIAL:AIRGAP",
    # "MATERIAL:INFRAREDTRANSPARENT",
    "MATERIAL:NOMASS",
    # "MATERIAL:ROOFVEGETATION",
    # "WINDOWMATERIAL:BLIND",
    "WINDOWMATERIAL:GLAZING",
    # "WINDOWMATERIAL:GLAZING:REFRACTIONEXTINCTIONMETHOD",
    # "WINDOWMATERIAL:GAP",
    # "WINDOWMATERIAL:GAS",
    # "WINDOWMATERIAL:GASMIXTURE",
    # "WINDOWMATERIAL:GLAZINGGROUP:THERMOCHROMIC",
    # "WINDOWMATERIAL:SCREEN",
    # "WINDOWMATERIAL:SHADE",
    # "WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM",
]


class MaterialObject(NamedTuple):
    Name: str
    Roughness: str
    Thickness: str
    Conductivity: str
    Density: str
    Specific_Heat: str
    Thermal_Absorptance: str
    Solar_Absorptance: str
    Visible_Absorptance: str

    # no:mass -> no density or thickness?

    # TODO depends on the type of material.. 


class ConstructionlObject(NamedTuple):
    Name: str
    OutsideLayer: str 
    
