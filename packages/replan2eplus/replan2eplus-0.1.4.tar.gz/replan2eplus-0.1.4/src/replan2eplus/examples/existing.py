from replan2eplus.ezcase.defaults import PATH_TO_IDD, PATH_TO_SAMPLE_IDF
from replan2eplus.ezcase.main import EZCase


def get_example_idf():
    case = EZCase(PATH_TO_IDD, PATH_TO_SAMPLE_IDF)
    return case.initialize_idf()


def get_example_case():
    case = EZCase(PATH_TO_IDD, PATH_TO_SAMPLE_IDF)
    case.initialize_idf()
    return case
