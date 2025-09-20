
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
    data = {
        "Message": "This is IAEA Dataexplorer REST API", 
        "Examples:": [
            {"Reactions API (Cross Section)": "https://nds.iaea.org/dataexplorer/api/reactions/xs?target_elem=Zr&target_mass=90&reaction=n%2Cg&table=True&page=1"},
            {"Reactions API (Residual Production Cross Section)": "https://nds.iaea.org/dataexplorer/api/reactions/residual?&target_elem=Ti&target_mass=0&inc_pt=A&rp_elem=Cr&rp_mass=51&page=1"},
            {"EXFOR API example (Entry)": "https://nds.iaea.org/dataexplorer/api/exfor/entry/11111"},
            {"EXFOR API example (Subentry)": "https://nds.iaea.org/dataexplorer/api/exfor/subentry/11222/002"},
            {"EXFOR API example (Bib)": "https://nds.iaea.org/dataexplorer/api/exfor/entry/11222/bib"},
            {"RIPL-3 Level": "http://nds.iaea.org/dataexplorer/api/ripl3/levels/90Zr"}
        ]
    }
    return jsonify(data)


