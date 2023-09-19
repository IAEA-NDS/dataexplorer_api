
from flask import jsonify, request, Blueprint
import pandas as pd
# from .search_api import reaction_query, get_entry_bib, data_query

reactions_api = Blueprint('reactions', __name__,)


@reactions_api.route('/')
def home():
    data = "This is REACTIONS REST API"
    return jsonify({'message': data})


# @reactions_api.route('list/<string:type>') #, methods = ['GET'])
# def get_list(type):
#     elem = request.args.get("target_elem")
#     mass = request.args.get("target_mass")
#     reaction = request.args.get("reaction")
#     print(type, elem, mass, reaction)
#     if elem and mass and reaction:
#         entids, entries = reaction_query(type, elem, mass, reaction, branch=None, rp_elem=None, rp_mass=None)
#         data = {"len": len(entids), "aggregations": entids}
#         return jsonify(data)
    
#     else:
#         return jsonify({'message': "no data"})


# @reactions_api.route('index/<string:type>') #, methods = ['GET'])
# def get_index(type):
#     elem = request.args.get("target_elem")
#     mass = request.args.get("target_mass")
#     reaction = request.args.get("reaction")

#     if elem and mass and reaction:
#         entids, entries = reaction_query(type, elem, mass, reaction, branch=None, rp_elem=None, rp_mass=None)
#         data = {"len": len(entids), "aggregations": entids}

#         return jsonify(data)
    
#     else:
#         return jsonify({'message': "no data"})



# @reactions_api.route('bib/<string:type>') #, methods = ['GET'])
# def get_bib(type):
#     elem = request.args.get("target_elem")
#     mass = request.args.get("target_mass")
#     reaction = request.args.get("reaction")

#     if elem and mass and reaction:
#         entids, entries = reaction_query(type, elem, mass, reaction, branch=None, rp_elem=None, rp_mass=None)

#     if entids:
#         legend = get_entry_bib(entries)
#         index_df = pd.DataFrame.from_dict(legend, orient="index").reset_index()

#         return jsonify(index_df.to_dict('records'))
    
#     else:
#         return jsonify({'message': "no data"})




# @reactions_api.route('data/<string:type>') #, methods = ['GET'])
# def data_guery(type):
#     elem = request.args.get("target_elem")
#     mass = request.args.get("target_mass")
#     reaction = request.args.get("reaction")
#     print(type, elem, mass, reaction)
#     if elem and mass and reaction:
#         entids, entries = reaction_query(type, elem, mass, reaction, branch=None, rp_elem=None, rp_mass=None)
#         data = {"len": len(entids), "aggregations": entids}
#         return jsonify(data)
    
#     if entries:
#         df = data_query(entids.keys(), branch=None)

#     else:
#         return jsonify({'message': "no data"})
