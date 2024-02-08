
from flask import jsonify, request, Blueprint
import pandas as pd
import numpy as np
from config import API_BASE_URL

from api_common import input_correction, generate_link_of_file

from submodules.common import generate_exfortables_file_path, generate_endftables_file_path
from submodules.exfor.queries import index_query, get_entry_bib, data_query
from submodules.reactions.queries import lib_query, lib_data_query
from submodules.utilities.reaction import get_mt, MT_BRANCH_LIST_FY
from submodules.utilities.util import get_number_from_string

reactions_api = Blueprint('reactions', __name__,)

page_size = 20




def generate_access_urls(reaction):
    url = f"{API_BASE_URL}data/{reaction.split(',')[0].lower()}"



@reactions_api.route('/')
def home():
    return jsonify({'message': "This is REACTIONS REST API"})



@reactions_api.route("/<string:type>", methods=['GET'])
def search(type):
    ## For the pagenation
    page = request.args.get('page', default=1, type=int)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size

    if not request.args:
        return jsonify(
            {
                'message': "Cross section search example: ", 
                "example": f"{API_BASE_URL}reactions/xs?target_elem=Al&target_mass=27&reaction=n%2Cp&page=1"
            }
        )

    """
    Save args into input_store
    """
    input_store = dict(request.args)
    input_store["type"] = type.upper()

    ## to make sure that the values are stored as boolean
    input_store["table"] = request.args.get("table", type=bool) if request.args.get("table") else False
    input_store["eval"] = request.args.get("eval", type=bool) if request.args.get("eval") else False
    input_store["excl_junk_switch"] = request.args.get("excl_junk_switch", type=bool) if request.args.get("excl_junk_switch") else True
    
    if input_store.get("inc_pt") and not input_store.get("rection") :
        input_store["reaction"] = f"{input_store['inc_pt'].upper()},X"

    """
    input check and return in correct format
    """
    elem, mass, reaction = input_correction(input_store.get("target_elem"), input_store.get("target_mass"), input_store.get("reaction"))

    if elem and mass and reaction:
        input_store["target_elem"] = elem
        input_store["target_mass"] = mass
        input_store["reaction"] = reaction

    else:
        return jsonify({'message': f"Input error for {elem}, {mass}, {reaction}"})

    
    if input_store["type"] == "XS":
        input_store["mt"] = get_mt(reaction)
        if reaction.split(",")[1][-1].isdigit():
            ## such as n,n1, n,n2 but not n,2n
            input_store["level_num"] = int(get_number_from_string(reaction.split(",")[1]))
        else:
            input_store["level_num"] = None


    elif input_store["type"] == "TH":
        input_store["mt"] = get_mt(reaction)


    elif input_store["type"] == "FY":
        if input_store.get("fy_type"):
            fy_type  = input_store.get("fy_type")
            input_store["branch"] = MT_BRANCH_LIST_FY[fy_type]["branch"] if MT_BRANCH_LIST_FY.get(fy_type) else None
            input_store["mt"] = MT_BRANCH_LIST_FY[fy_type]["mt"] if MT_BRANCH_LIST_FY.get(fy_type) else None


    elif input_store["type"] == "RP":
        rp_elem, rp_mass, reaction = input_correction( input_store.get("rp_elem"), input_store.get("rp_mass"), input_store.get("reaction") )
        input_store["rp_elem"] = rp_elem
        input_store["rp_mass"] = rp_mass
    


    """
    Run query for exfortables
    """
    legends = {}
    libraries = {}

    entries = index_query(input_store)
    if entries:
        """
        return format of legend looks as follows: 
        {'13947-006-0': {'author': 'S.Raman', 'year': 2004, 'level_num': None, 'e_inc_min': 2.5299999999999998e-08, 'e_inc_max': 2.5299999999999998e-08, 'points': 1, 'x4_code': '(28-NI-59(N,G)28-NI-60,,SIG,,MXW)', 'sf4': '28-NI-60', 'sf5': None, 'sf6': 'SIG', 'sf7': None, 'sf8': 'MXW', 'mt': 102, 'mf': 3},
        """
        legends =  get_entry_bib(e[:5] for e in entries.keys())
        legends = {
            t: dict(**i, **v)
            for k, i in legends.items()
            for t, v in entries.items()
            if k == t[:5]
        }

        """
        glob all exfortables formatted files
        """
        ex_dir, ex_files = generate_exfortables_file_path(input_store)

        if input_store.get("table"):
            for entid in list(legends.keys())[start_index:end_index]:
                df = data_query(input_store, [ entid ] )
                df = df.drop(columns=["entry_id"])
                df = df.astype(object).replace(np.nan, 'None')
                legends[entid].update({
                    "datatable": df.to_dict('list'), 
                    "file": generate_link_of_file(ex_dir, ex_files, entid)
                    })


    data = {"inputs": input_store ,#{key: input_store[key] for key in input_store.keys() & {"type", "target_elem", "target_mass", "mt", "mf"}},
            "aggregations": dict(list(legends.items())[start_index:end_index]), 
            "hits": len(entries), 
            "page": int(page)
            }
        

    """
    Libraries query
    Return format of libs looks as follows:
    {679555: 'tendl.2021', 680066: 'endfb8.0', 680182: 'eaf.2010', 680309: 'jeff3.3', 680977: 'jendl5.0'}
    """
    if input_store.get("eval"):
        libs = lib_query(input_store)

        lib_df = pd.DataFrame()
        if libs:
            lib_dir, lib_files = generate_endftables_file_path(input_store)

            for l_id in libs.keys():
                lib_df = lib_data_query( input_store, [ l_id ] )
                libraries[ libs[l_id] ] = {
                    "e_inc_max": max(lib_df["en_inc"].unique()),
                    "e_inc_min": min(lib_df["en_inc"].unique()),
                    "points": len(lib_df.index),
                }
                if input_store.get("table"):
                    lib_df = lib_df.drop(columns=["reaction_id", "id"])
                    libraries[ libs[l_id] ].update({
                        "datatable": lib_df.to_dict('list'),
                        "file": generate_link_of_file(lib_dir, lib_files, libs[l_id])
                        })

        data["evaluated_libraries"] = libraries
        


    if not entries and not libs:
        return jsonify({"hits": 0, 'message': "no data"})



    return jsonify(data)



