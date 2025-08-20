# EPBunch helpers -> not worth it to have a class..
from eppy.bunch_subclass import EpBunch


def get_epbunch_key(epbunch: EpBunch):
    return epbunch.key
