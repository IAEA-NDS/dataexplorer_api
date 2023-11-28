import json
import os
from flask import jsonify, request, Blueprint
import pandas as pd

from config import EXFOR_JSON_GIT_REPO_PATH
from exfor_dictionary.exfor_dictionary import Diction
from submodules.exfor.queries import entries_query, data_query
D = Diction()

institutes = D.read_diction("3")
methods = D.read_diction("21")
detectors  = D.read_diction("22")
facilities = D.read_diction("18")

exfor_api = Blueprint('exfor', __name__,)

page_size = 100

# https://medium.com/@piedjoustephane/prototyping-object-relational-mapping-orm-model-from-a-json-object-96eb0ea05ad4
# https://realpython.com/flask-blueprint/
# This is the page of /api/exfor/ root
def open_json(entnum):
    file = os.path.join(EXFOR_JSON_GIT_REPO_PATH, "json", entnum[:3], entnum + ".json")
    print(file)
    if os.path.exists(file):
        with open(file) as json_file:
            return json.load(json_file)
    else:
        return None


def check_entlen(entnum):
    if len(entnum) != 5:
        return "EXFOR entry number is 5 chars., e.g. 12345"


def check_sublen(subent):
    if len(subent) != 3:
        return "EXFOR subentry number is 3 digit, e.g. 003"



@exfor_api.route('/')
def home():
    data = "This is EXFOR REST API"
    return jsonify({'message': data})




@exfor_api.route('/entry/<string:entnum>') #, methods = ['GET'])
def entry(entnum):
    ermsg = check_entlen(entnum)
    if ermsg:
        return jsonify({'message': ermsg })
    return jsonify(open_json(entnum))



@exfor_api.route('/entry/<string:entnum>/<string:section>') #, methods = ['GET'])
def entry_sec(entnum, section):
    ermsg = check_entlen(entnum)
    if ermsg:
        return jsonify({'message': ermsg })
        
    if section:
        key_string = {
            "reactions": "reactions",
            "bib": "bib_record",
            "histories": "histories",
            "data": "data_tables",
            "experiment": "experimental_conditions"
        }
        if key_string.get(section):
            return jsonify(open_json(entnum).get(key_string[section]))

    return jsonify({'message': "key error available keys are: " + ", ".join(key_string.keys()) + "." })



@exfor_api.route('/subentry/<string:entnum>/<string:subent>') #, methods = ['GET'])
def subentry(entnum, subent):
    if len(entnum) != 5:
        return jsonify({'message': "EXFOR entry number is 5 chars"})
    
    ermsg = check_entlen(entnum)
    if ermsg:
        return jsonify({'message': ermsg })
    ermsg = check_sublen(subent)
    if ermsg:
        return jsonify({'message': ermsg })
    
    entry = open_json(entnum)

    if entry:
        subentry = {"entry": entnum+subent}
        jkey = [ "experimental_conditions", "data_tables"]
        for j in jkey:
            if entry.get(j):
                subentry[j] = entry[j][subent]
        return jsonify(subentry)



###### ------------------------------------ ######
######             Entries
###### ------------------------------------ ######

@exfor_api.route('/entries') #, methods = ['GET'])
def entries():
    # df = pd.DataFrame()
    ## currently same as /reactions/search
    if request.args.get("query"):
        # will be implement with Elasticsearch
        pass
    page = request.args.get('page', default=1, type=int)
    # Calculate the start and end indexes for the current page
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    # Slice the data to return the current page's content
    target_elem = request.args.get("target_elem")
    target_mass = request.args.get("target_mass")
    reaction = request.args.get("reaction")

    methods = request.args.get("method")
    facility = request.args.get("facility")
    institute = request.args.get("institute")
    detectors = request.args.get("detector")

    ## From reaction code
    type = request.args.get("sf6")
    sf6 = request.args.get("sf6")  # type
    sf5 = request.args.get("sf5")  
    sf4 = request.args.get("sf4")  
    sf7 = request.args.get("sf7")  
    sf8 = request.args.get("sf8")  

    # print(sf6, elem, mass, reaction)
    kwargs = {}
    if target_elem and target_mass and reaction:
        kwargs = dict(sf6=sf6,
                    type=type, 
                    target_elem=target_elem.upper() if target_elem else None, 
                    target_mass=target_mass.upper() if target_mass else None, 
                    reaction=reaction.upper() if reaction else None,
                    methods=methods.upper() if methods else None,
                    facility=facility.upper() if facility else None,
                    institute=institute.upper() if institute else None,
                    detectors=detectors.upper() if detectors else None,
                    sf5=sf5.upper() if sf5 else None,
                    sf4=sf4.upper() if sf4 else None,
                    sf7=sf7.upper() if sf7 else None,
                    sf8=sf8.upper() if sf8 else None,)

    df = entries_query(**kwargs)
    entries = df.set_index('entry_id').to_dict('index')
    print(entries)
    # data_table = data_query(entries.keys())

    data = {"hits": len(entries), "aggregations": entries}#[{e:d} for e,d in dict(entries).items()][start_index:end_index] }
    return jsonify(data)





###### ------------------------------------ ######
######             Dictionary
###### ------------------------------------ ######

@exfor_api.route('/dict/<string:div>')
def div(div):
    if div == "entry":
        data = "specify the entry number such as /api/exfor/10300"
        return jsonify({'message': data})

    elif div == "facility":
        return jsonify(facilities)

    elif div == "institute":
        return jsonify(institutes)

    elif div == "method":
        return jsonify(methods)

    elif div == "detector":
        return jsonify(detectors)

    else:
        return jsonify({'message': "What do you want?"})



@exfor_api.route('/dict/institute/<string:code>')
def get_institute(code):
    if code:
        if institutes["codes"].get(code.upper()):
            return jsonify(institutes["codes"][code.upper()])
        else:
            return jsonify({'message': "key error available keys are: " + ", ".join(institutes["codes"].keys()) + "." })
    else:
        return jsonify(institutes)



@exfor_api.route('/dict/facility/<string:code>')
def get_facil(code):
    if code:
        if facilities["codes"].get(code.upper()):
            return jsonify(facilities["codes"][code.upper()])
        else:
            return jsonify({'message': "key error available keys are: " + ", ".join(facilities["codes"].keys()) + "." })
    else:
        return jsonify(facilities)



@exfor_api.route('/dict/method/<string:code>')
def get_metd(code):
    if code:
        if methods["codes"].get(code.upper()):
            return jsonify(methods["codes"][code.upper()])
        else:
            return jsonify({'message': "key error available keys are: " + ", ".join(methods["codes"].keys()) + "." })
    else:
        return jsonify(methods)



@exfor_api.route('/dict/detector/<string:code>')
def get_dtct(code):
    if code:
        if detectors["codes"].get(code.upper()):
            return jsonify(detectors["codes"][code.upper()])
        else:
            return jsonify({'message': "key error available keys are: " + ", ".join(detectors["codes"].keys()) + "." })
    else:
        return jsonify(detectors)







