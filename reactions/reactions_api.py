
from flask import jsonify, request, Blueprint
import pandas as pd
import numpy as np
from config import API_BASE_URL

from api_common import PAGEPARAM_TYPE, input_correction, error_response, get_bool_arg, find_pageparam_key

from submodules.common import generate_exfortables_file_path, generate_endftables_file_path, generate_link_of_files
from submodules.exfor.queries import exfor_index_query, get_entry_bib, data_query
from submodules.endflibs.queries import lib_index_query, lib_data_query
from submodules.utilities.reaction import get_mt, MT_BRANCH_LIST_FY
from submodules.utilities.util import get_number_from_string

reactions_api = Blueprint('reactions', __name__,)

page_size = 20




def generate_access_urls(reaction):
    url = f"{API_BASE_URL}data/{reaction.split(',')[0].lower()}"



@reactions_api.route('/')
def home():
    return jsonify({'message': "This is REACTIONS REST API"})


@reactions_api.route("/<string:obs_type>", methods=['GET'])
def search(obs_type):
    # pagination
    page = request.args.get('page', default=1, type=int)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    # no query args: show brief example/help
    if not request.args:
        return jsonify(
            {
                'message': "Cross section search example: ",
                "example": f"{API_BASE_URL}reactions/xs?target_elem=Al&target_mass=27&reaction=n%2Cp"
            }
        )

    # obs_type key lookup (case-insensitive)
    obs_key = find_pageparam_key(obs_type)
    if obs_key is None:
        return error_response(
            "Invalid obs_type",
            required=list(PAGEPARAM_TYPE.keys()),
            example=f"{API_BASE_URL}reactions/xs?target_elem=Al&target_mass=27&reaction=n%2Cp"
        )

    # decide required parameters depending on observation type (RP uses rp_elem/rp_mass)
    mapped_obs_type = PAGEPARAM_TYPE[obs_key]  # e.g. 'XS', 'TH', 'FY', 'RP', ...
    print(obs_key, mapped_obs_type)

    if mapped_obs_type.upper() == "RP":
        required_params = ["rp_elem", "rp_mass", "reaction"]
        example_url = f"{API_BASE_URL}reactions/residual?target_elem=Mo&target_mass=100&rp_elem=Tc&rp_mass=99m&reaction=p,x"
    elif mapped_obs_type.upper() == "FY":
        required_params = ["target_elem", "target_mass", "reaction", "fy_type"]
        example_url = f"{API_BASE_URL}reactions/fy?target_elem=U&target_mass=235&reaction=n,f&fy_type=Cumulative"
    else:
        required_params = ["target_elem", "target_mass", "reaction"]
        example_url = f"{API_BASE_URL}reactions/{obs_key}?target_elem=Al&target_mass=27&reaction=n%2Cp"


    # check for missing required params
    missing = [p for p in required_params if not request.args.get(p)]
    if missing:
        return error_response(
            "Missing required parameters",
            required=required_params,
            missing=missing,
            example=example_url
        )

    # Build a simple input_store from request args (preserve single values)
    input_store = {k: request.args.get(k) for k in request.args.keys()}
    input_store["obs_type"] = mapped_obs_type

    # normalize boolean flags
    input_store["table"] = get_bool_arg("table", False)
    input_store["eval"] = get_bool_arg("eval", False)
    input_store["excl_junk_switch"] = get_bool_arg("excl_junk_switch", True)

    # auto-complete reaction/projectile when inc_pt provided (fix typo from original)
    if input_store.get("reaction"):
        # if reaction, use reaction string
        proj = input_store["reaction"].split(",")[0].lower()
        input_store["projectile"] = proj
        input_store["inc_pt"] = proj.upper()

    elif input_store.get("inc_pt"):
        # if not reaction, use inc_pt
        proj = input_store["inc_pt"].lower()
        input_store["projectile"] = proj
        input_store["inc_pt"] = proj.upper()
        input_store["reaction"] = f"{proj.upper()},X"

    # input correction depending on RP vs others
    if input_store["obs_type"].upper() == "RP":
        rp_elem, rp_mass, reaction = input_correction(
            input_store.get("rp_elem"),
            input_store.get("rp_mass"),
            input_store.get("reaction"),
        )
        if not (rp_elem and rp_mass and reaction):
            # 必須項目は既にチェック済みだが、正規化後に無効になった場合は 400 を返す
            return error_response(
                "Input error after normalization for RP parameters",
                required=required_params,
                example=example_url
            )
        input_store["rp_elem"] = rp_elem
        input_store["rp_mass"] = rp_mass
        input_store["reaction"] = reaction

    else:
        elem, mass, reaction = input_correction(
            input_store.get("target_elem"),
            input_store.get("target_mass"),
            input_store.get("reaction"),
        )
        if not (elem and mass and reaction):
            return error_response(
                "Input error after normalization for target parameters",
                required=required_params,
                example=example_url
            )
        input_store["target_elem"] = elem
        input_store["target_mass"] = mass
        input_store["reaction"] = reaction

    # observation-specific handling
    if input_store["obs_type"] == "XS":
        input_store["mt"] = get_mt(input_store["reaction"])
        # level number detection (e.g. n,n1 -> level 1)
        second_part = input_store["reaction"].split(",")[1] if "," in input_store["reaction"] else ""
        if second_part and second_part[-1].isdigit():
            input_store["level_num"] = int(get_number_from_string(second_part))
        else:
            input_store["level_num"] = None

    elif input_store["obs_type"] == "TH":
        input_store["mt"] = get_mt(input_store["reaction"])

    elif input_store["obs_type"] == "FY":
        fy_type = input_store.get("fy_type")
        if fy_type:
            branch_info = MT_BRANCH_LIST_FY.get(fy_type)
            input_store["branch"] = branch_info["branch"] if branch_info else None
            input_store["mt"] = branch_info["mt"] if branch_info else None

    elif input_store["obs_type"] == "RP":
        # (rp_elem/rp_mass were set above)
        pass

    # --- Run queries ---
    legends = {}
    libraries = {}

    entries = exfor_index_query(input_store)
    if entries:
        # merge bibliographic info
        legends = get_entry_bib(e[:5] for e in entries.keys())
        legends = {
            t: dict(**i, **v)
            for k, i in legends.items()
            for t, v in entries.items()
            if k == t[:5]
        }

        # files for exfor tables
        ex_files = generate_exfortables_file_path(input_store)
        # if table requested, attach datatables (paginated)
        if input_store.get("table"):
            for entid in list(legends.keys())[start_index:end_index]:
                df = data_query(input_store, [entid])
                df = df.drop(columns=["entry_id"])
                df = df.astype(object).replace(np.nan, 'None')
                legends[entid].update({
                    "datatable": df.to_dict('list'),
                    "file": generate_link_of_files(ex_files)
                })

    # prepare response skeleton
    data = {
        "inputs": input_store,
        "aggregations": dict(list(legends.items())[start_index:end_index]),
        "hits": len(entries),
        "page": int(page)
    }

    # evaluated libraries
    if input_store.get("eval"):
        libs = lib_index_query(input_store)
        lib_df = pd.DataFrame()
        if libs:
            lib_files = generate_endftables_file_path(input_store)
            for l_id in libs.keys():
                lib_df = lib_data_query(input_store, [l_id])
                libraries[libs[l_id]] = {
                    "e_inc_max": max(lib_df["en_inc"].unique()),
                    "e_inc_min": min(lib_df["en_inc"].unique()),
                    "points": len(lib_df.index),
                }
                if input_store.get("table"):
                    lib_df = lib_df.drop(columns=["reaction_id", "id"])
                    libraries[libs[l_id]].update({
                        "datatable": lib_df.to_dict('list'),
                        "file": generate_link_of_files(lib_files)
                    })
        data["evaluated_libraries"] = libraries

    if not entries and not libraries:
        return jsonify({"hits": 0, "message": "no data"})

    return jsonify(data)



