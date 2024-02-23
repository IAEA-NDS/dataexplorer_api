import os
import json
from flask import request

from config import DATA_DIR, EXFOR_JSON_GIT_REPO_PATH, EXFORTABLES_PY_GIT_REPO_PATH
from submodules.utilities.util import get_number_from_string
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



def get_url_root():
    # path             /foo/page.html
    # full_path        /foo/page.html?x=y
    # script_root      /myapplication
    # base_url         http://www.example.com/myapplication/foo/page.html
    # url              http://www.example.com/myapplication/foo/page.html?x=y
    # url_root         http://www.example.com/myapplication/
    return request.url_root



def generate_link_of_file(dir, files, entid):
    ## should be like https://nds.iaea.org/dataexplorer/exfortables_py/n/Fe-56/n-inl-L1/xs/Fe-56_n-inl-L1_Fe56_Almen-Ramstrom-20788-008-0-1975.txt
    f = next(x for x in files if entid in x)

    if f:
        return os.path.join(get_url_root().replace("api/", ""), dir.replace(DATA_DIR, ""), f)
    
    else:
        return None


