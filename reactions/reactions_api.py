
from flask import jsonify, request, Blueprint
import pandas as pd
import numpy as np
from config import API_BASE_URL

from api_common import input_correction, generate_link_of_files

from submodules.common import generate_exfortables_file_path
from submodules.exfor.queries import index_query, get_entry_bib, data_query
from submodules.reactions.queries import lib_query, lib_data_query
from submodules.utilities.reaction import get_mt, MT_BRANCH_LIST_FY

reactions_api = Blueprint('reactions', __name__,)

page_size = 100

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

    ## put args into input_store
    input_store = dict(request.args)
    input_store["type"] = type.upper()

    if input_store.get("inc_pt") and not input_store.get("rection") :
        input_store["reaction"] = f"{input_store['inc_pt'].upper()},X"

    ## input check and return in correct format
    elem, mass, reaction = input_correction(input_store.get("target_elem"), input_store.get("target_mass"), input_store.get("reaction"))

    if elem and mass and reaction:
        input_store["target_elem"] = elem
        input_store["target_mass"] = mass
        input_store["reaction"] = reaction

    else:
        return jsonify({'message': f"Input error for {elem}, {mass}, {reaction}"})

    
    ## input correction for query
    if input_store["type"] == "XS":
        print("here")
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

    print(input_store)
    ## run query
    legends = {}
    libraries = {}

    entries = index_query(input_store)
    if entries:
        legends =  get_entry_bib(e[:5] for e in entries.keys())
        legends = {
            t: dict(**i, **v)
            for k, i in legends.items()
            for t, v in entries.items()
            if k == t[:5]
        }
    # print(legends)
    libs = lib_query(input_store)
    lib_df = pd.DataFrame()
    if libs:
        lib_df = lib_data_query( input_store, libs.keys()  )
        for l in libs.values():
            # print(lib_df[lib_df["reaction_id"] == int(l)])

            libraries[ l["lib_name"] ] = {
                "e_inc_max": max(lib_df["en_inc"].unique()),
                "e_inc_min": min(lib_df["en_inc"].unique()),
                "mf": l["mf"],
                "mt": l["mt"],
                "points": len(lib_df.index),
            }
    if not entries and not libs:
        return jsonify({"hits": 0, 'message': "no data"})


    ## generate returning data
    data = {"hits": len(entries), 
            "aggregations": dict(list(legends.items())[start_index:end_index]), 
            "libraries": libraries
            }
        
    if input_store.get("table"):
        df = data_query(input_store, dict(list(legends.items())[start_index:end_index]).keys())
        df = df.astype(object).replace(np.nan, 'None')
        table = df.to_dict('records')
        data["datatables"] = table

    else:
        ex_dir, ex_files = generate_exfortables_file_path(input_store)
        lib_dir, lib_files = generate_exfortables_file_path(input_store)
        data["files"] = generate_link_of_files( ex_dir, ex_files ) + generate_link_of_files( lib_dir, lib_files )


    return jsonify(data)






# @reactions_api.route("/xs", methods=['GET']) #, methods = ['GET'])
# def search_xs():

#     page = request.args.get('page', default=1, type=int)
#     start_index = (page - 1) * page_size
#     end_index = start_index + page_size

#     target_elem = request.args.get("target_elem")
#     target_mass = request.args.get("target_mass")
#     target = elemtoz_nz(target_elem) + "-" + target_elem.upper() + "-" + target_mass
#     reaction = request.args.get("reaction")
#     branch = request.args.get("branch")

#     if target_elem and target_mass and reaction:
#         entids = index_query("SIG", target_elem, target_mass, reaction, branch,None, None )
    
#         data = {"hits": len(entids), "aggregations": [entids][start_index:end_index] }
#         return jsonify(data)

#     else:
#         return jsonify({"hits": 0, 'message': "no data"})


# @reactions_api.route("/residual", methods=['GET']) #, methods = ['GET'])
# def search_rp():

#     target_elem = request.args.get("target_elem")
#     target_mass = request.args.get("target_mass")
#     reaction = request.args.get("reaction")
#     rp_elem = request.args.get("rp_elem")
#     rp_mass = request.args.get("rp_mass")

#     if target_elem and target_mass and reaction:
#         entids = index_query("Residual", target_elem, target_mass, reaction, None, rp_elem, rp_mass)
#         data = {"hits": len(entids), "aggregations": entids}
#         return jsonify(data)

#     else:
#         return jsonify({"hits": 0, 'message': "no data"})


# @reactions_api.route("/da", methods=['GET']) #, methods = ['GET'])
# def search_da():

#     target_elem = request.args.get("target_elem")
#     target_mass = request.args.get("target_mass")
#     reaction = request.args.get("reaction")
#     branch = request.args.get("branch")
    
#     if target_elem and target_mass and reaction:
#         entids = index_query("DA", target_elem, target_mass, reaction, branch, rp_elem=None, rp_mass=None)
#         data = {"hits": len(entids), "aggregations": entids}
#         return jsonify(data)

#     else:
#         return jsonify({"hits": 0, 'message': "no data"})




# @reactions_api.route("/de", methods=['GET']) #, methods = ['GET'])
# def search_de():

#     target_elem = request.args.get("target_elem")
#     target_mass = request.args.get("target_mass")
#     reaction = request.args.get("reaction")
#     branch = request.args.get("branch")
    
#     if target_elem and target_mass and reaction:
#         entids = index_query("DE", target_elem, target_mass, reaction, branch, rp_elem=None, rp_mass=None)
#         data = {"hits": len(entids), "aggregations": entids}
#         return jsonify(data)

#     else:
#         return jsonify({"hits": 0, 'message': "no data"})



