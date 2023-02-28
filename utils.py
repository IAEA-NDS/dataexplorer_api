import os
import json

def open_json(entnum):
    file = os.path.join(EXFOR_JSON, entnum[:3], entnum + ".json")
    if os.path.exists(file):
        with open(file) as json_file:
            return json.load(json_file)
    else:
        return None