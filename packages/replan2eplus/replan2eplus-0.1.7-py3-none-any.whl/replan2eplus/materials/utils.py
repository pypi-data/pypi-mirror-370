from pathlib import Path
from replan2eplus.ezobjects.construction import Construction
from replan2eplus.ezobjects.epbunch_utils import get_epbunch_key
from replan2eplus.ezobjects.material import Material
from replan2eplus.idfobjects.idf import IDF


def create_materials_from_other_idf(
    path_to_idf: Path, path_to_idd: Path, material_names: list[str] = []
):
    """
    default of not specifying any material names means return all
    """
    other_idf = IDF(path_to_idd, path_to_idf)
    material_epbunches = other_idf.get_materials()
    if not material_names:
        return [Material(i, get_epbunch_key(i)) for i in material_epbunches]

    return [
        Material(i, get_epbunch_key(i))
        for i in material_epbunches
        if i.Name in material_names
    ]


def create_constructions_from_other_idf(
    path_to_idf: Path, path_to_idd: Path, construction_names: list[str] = []
):
    other_idf = IDF(path_to_idd, path_to_idf)
    construction_epbunches = other_idf.get_materials()
    if not construction_names:
        return [Construction(i, get_epbunch_key(i)) for i in construction_epbunches]

    return [
        Construction(i, get_epbunch_key(i))
        for i in construction_epbunches
        if i.Name in construction_names
    ]
