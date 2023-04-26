import json
import os
from flask import Flask, jsonify, request


app = Flask(__name__)

## Blueprint
from exfor.exfor_api import exfor_api
app.register_blueprint(exfor_api, url_prefix='/exfor')

from ripl3.ripl3_api import ripl3_api
app.register_blueprint(ripl3_api, url_prefix='/ripl3')


@app.route('/')
def home():
    data = "This is IAEA Dataexplorer REST API"
    return jsonify({'data': data})


