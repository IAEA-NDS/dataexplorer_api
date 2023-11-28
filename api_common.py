import os
import json

from config import DATA_DIR, EXFOR_JSON_GIT_REPO_PATH, EXFORTABLES_PY_GIT_REPO_PATH
from submodules.utilities.util import get_number_from_string
from submodules.utilities.reaction import convert_partial_reactionstr_to_inl
from submodules.utilities.mass import mass_range
from submodules.utilities.elem import elemtoz_nz



def input_correction(elem, mass, reaction):
    print(elem, mass, reaction)

    if elem and mass:
        min = mass_range[elemtoz_nz(elem.capitalize())]["min"]
        max = mass_range[elemtoz_nz(elem.capitalize())]["max"]

        if mass == "0":
            pass

        elif not int(min) < int(get_number_from_string(mass)) < int(max):
            mass = None

    else:
        mass = None

    return elem.capitalize(), mass.lower(), reaction.lower()




def generate_link_of_files(dir, files):
    ## similar to list_link_of_files in dataexplorer/common.py
    flinks = []
    for f in sorted(files):

        linkdir = dir.replace(DATA_DIR, "")

        fullpath = os.path.join(linkdir, f)

        flinks.append(fullpath)

    return flinks


