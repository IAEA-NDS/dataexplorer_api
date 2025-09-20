import os
from flask import request, jsonify

from config import DATA_DIR
from submodules.utilities.util import get_number_from_string
from submodules.utilities.mass import mass_range
from submodules.utilities.elem import elemtoz_nz


PAGEPARAM_TYPE = {
    "thermal": "TH",
    "residual": "RP",
    "xs": "XS",
    "fy": "FY",
    "angle": "DA",
}


def input_correction(elem, mass, reaction):

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



def error_response(message, required=None, missing=None, example=None, status_code=400):
    payload = {"error": message}
    if required is not None:
        payload["required"] = required
    if missing is not None:
        payload["missing"] = missing
    if example is not None:
        payload["example"] = example
    return jsonify(payload), status_code



def find_pageparam_key(obs_type: str):
    if obs_type in PAGEPARAM_TYPE:
        return obs_type
    lower = obs_type.lower()
    for k in PAGEPARAM_TYPE.keys():
        if k.lower() == lower:
            return k
    return None


def get_bool_arg(name: str, default: bool):
    """
    リクエストクエリから真偽値を穏やかに取得するヘルパー。
    '1','true','yes','on' を True とみなす。
    """
    val = request.args.get(name)
    if val is None:
        return default
    if isinstance(val, str):
        return val.lower() in ("1", "true", "yes", "on")
    return bool(val)

