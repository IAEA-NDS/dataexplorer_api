import os
import json
from config import EXFOR_JSON

def open_json(entnum):
    file = os.path.join(EXFOR_JSON, entnum[:3], entnum + ".json")
    if os.path.exists(file):
        with open(file) as json_file:
            return json.load(json_file)
    else:
        return None