from dataclasses import dataclass
from eppy.bunch_subclass import EpBunch
import replan2eplus.epnames.keys as epkeys
from geomeppy import IDF as geomeppyIDF
from pathlib import Path
from eppy.modeleditor import IDDAlreadySetError

from replan2eplus.idfobjects.subsurface import SubsurfaceKey, SubsurfaceObject
from replan2eplus.idfobjects.zone import GeomeppyBlock
from replan2eplus.idfobjects.afn import (
    AFNKeys,
    AFNSimulationControl,
    AFNZone,
    AFNSurface,
    AFNSimpleOpening,
)
from replan2eplus.idfobjects.materials import MaterialKey, material_keys


@dataclass
class IDF:
    path_to_idd: Path
    path_to_idf: Path

    def __post_init__(self):
        try:
            geomeppyIDF.setiddname(self.path_to_idd)
        except IDDAlreadySetError:
            pass  # TODO log IDD already set, especially if the one they try to set is different..

        self.idf = geomeppyIDF(idfname=self.path_to_idf)

    def print_idf(self):
        self.idf.printidf()  # TOOD make sure works?

    def view_idf_3d(self):
        self.idf.view_model()

    # TODO this is a property, unless adding filters later..
    def get_zones(self) -> list[EpBunch]:
        return [
            i for i in self.idf.idfobjects[epkeys.ZONE]
        ]  # TODO could put EzBunch on top here.. => maybe if things get out of hand..

    def get_surfaces(self) -> list[EpBunch]:
        return [i for i in self.idf.idfobjects[epkeys.SURFACE]]
    
    def get_subsurfaces(self) -> list[EpBunch]:
        return self.idf.getsubsurfaces()

    def get_materials(self) -> list[EpBunch]:
        materials = []
        for key in material_keys:
            materials.extend([self.idf.idfobjects[key]])

        return materials

    def get_constructions(self) -> list[EpBunch]:
        return self.idf.idfobjects[epkeys.CONSTRUCTION]
    


    # @property
    # def subsurfaces(self):
    #     return

    def add_geomeppy_block(self, block: GeomeppyBlock):
        self.idf.add_block(
            **block
        )  # TODO: think named tuple is just as good for this? good for consistency? not sure bc its a slightly different API

    def intersect_match(self):
        self.idf.intersect_match()

    def add_subsurface(self, key: SubsurfaceKey, subsurface_object: SubsurfaceObject):
        # TODO is this check needed / should it be hapening elsewhere? just to
        surface_names = [i.Name for i in self.get_surfaces()]
        assert subsurface_object.Building_Surface_Name in surface_names
        obj0 = self.idf.newidfobject(key.upper(), **subsurface_object._asdict())

        return obj0

    def add_afn_simulation_control(self, object: AFNSimulationControl):
        obj0 = self.idf.newidfobject(AFNKeys.SIM_CONTROL, **object._asdict())
        return obj0

    def add_afn_zone(self, object: AFNZone):
        obj0 = self.idf.newidfobject(AFNKeys.ZONE, **object._asdict())
        return obj0

    def add_afn_opening(self, object: AFNSimpleOpening):
        obj0 = self.idf.newidfobject(AFNKeys.OPENING, **object._asdict())
        return obj0

    def add_afn_surface(self, object: AFNSurface):
        obj0 = self.idf.newidfobject(AFNKeys.SURFACE, **object._asdict())
        return obj0
    
    # def add_material(self, key:MaterialKey, object: MaterialObject):
    #     pass

    # def add_construction(self, object: ConstructionObject):
    #     pass

    def update_object_construction(self, name: str, key: str, construction_name: str):
        # TODO key is a literal -> surface or subsurface.. 
        pass
