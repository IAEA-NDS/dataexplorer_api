
from flask import Flask, jsonify


app = Flask(__name__)

## Blueprint
from exfor.exfor_api import exfor_api
app.register_blueprint(exfor_api, url_prefix='/exfor')


from ripl3.ripl3_api import ripl3_api
app.register_blueprint(ripl3_api, url_prefix='/ripl3')

from reactions.reactions_api import reactions_api
app.register_blueprint(reactions_api, url_prefix='/reactions')


@app.route('/')
def home():
    data = "This is IAEA Dataexplorer REST API"
    return jsonify({'data': data})


