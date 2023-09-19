from flask import Flask, jsonify, request, Blueprint
import os
import json
import re
from config import RIPL3



ripl3_api = Blueprint('ripl3', __name__,)


def open_json(nuclide):
    elem = re.sub(r'[^A-Za-z]{1,2}', '', nuclide)
    mass = re.sub(r'[0-9]{1,3}', '', nuclide)
    file = os.path.join(RIPL3, "data/levels_json", elem, nuclide + ".json")
    with open(file) as json_file:
        return json.load(json_file)


def open_dat(nuclide):
    elem = re.sub(r'[^A-Za-z]{1,2}', '', nuclide)
    mass = re.sub(r'[0-9]{1,3}', '', nuclide)
    file = os.path.join(RIPL3, "data/levels", elem, nuclide + ".dat")
    with open(file) as json_file:
        return json.load(json_file)


@ripl3_api.route('/')
def home():
    data = "This is RIPLE-3 REST API"
    return jsonify({'message': data})


@ripl3_api.route('/levels/<string:nuclide>') #, methods = ['GET'])
def nuclide(nuclide):
    data = open_json(nuclide)
    return jsonify(data)



@ripl3_api.route('/levels/<string:nuclide>/info') #, methods = ['GET'])
def nuclide_info(nuclide):
  data = open_json(nuclide)
  return jsonify(data["level_info"])



@ripl3_api.route('/levels/<string:nuclide>/levels') #, methods = ['GET'])
def nuclide_levels(nuclide):
  data = open_json(nuclide)
  return jsonify(data["level_info"]["levels"])



@ripl3_api.route('/levels/<string:nuclide>/level_record/levelnum/<string:levelnum>') #, methods = ['GET'])
def level_num(nuclide, levelnum):
  data = open_json(nuclide)
  return jsonify(data["level_record"][int(levelnum)])


#if __name__=='__main__':
#  app.run(debug=True)
