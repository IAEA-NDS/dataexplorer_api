import json
import os
from flask import jsonify, request, Blueprint

from config import EXFOR_JSON_GIT_REPO_PATH
from exfor_dictionary.exfor_dictionary import Diction
D = Diction()

institutes = D.read_diction("3")
methods = D.read_diction("21")
detectors  = D.read_diction("22")
facilities = D.read_diction("18")

exfor_api = Blueprint('exfor', __name__,)

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







