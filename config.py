import os
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import site

DEVENV = True 

if DEVENV:
    ## Application file location
    TOP_DIR = "/Users/sin/Dropbox/Development/dataexplorer2/"

    ## Data directory linked from the code
    DATA_DIR = "/Users/sin/Documents/nucleardata/EXFOR/"

    API_BASE_URL = "http://127.0.0.1:5000/"


else:
    ## Application file location
    TOP_DIR = "/srv/www/dataexplorer2/"

    ## Data directory linked from the code
    DATA_DIR = "/srv/data/dataexplorer2/"

    API_BASE_URL = "https://int-nds.iaea.org/dataexplorer/api/"


## Package locations
SITE_DIR = site.getsitepackages()[0]
EXFOR_PARSER = os.path.join(SITE_DIR, "exforparser")
EXFOR_DICTIONARY = os.path.join(SITE_DIR, "exfor_dictionary")
ENDF_TABLES = os.path.join(SITE_DIR, "endftables_sql")
RIPL3 = os.path.join(SITE_DIR, "ripl3_json")


## Define the location of files ussed in the interface
MT_PATH_JSON = os.path.join(EXFOR_PARSER, "tabulated/mf3.json")
MT50_PATH_JSON = os.path.join(EXFOR_PARSER, "tabulated/mt50.json")

MAPPING_FILE = os.path.join(TOP_DIR, "exfor/datahandle/mapping.json")
MASS_RANGE_FILE = os.path.join(TOP_DIR, "submodules/utilities/A_min_max.txt")

## Define the location of data files
EXFOR_DB = os.path.join(DATA_DIR, "exfor.sqlite")
ENDFTAB_DB = os.path.join(DATA_DIR, "endftables.sqlite")
MASTER_GIT_REPO_PATH = os.path.join(DATA_DIR, "exfor_master")
EXFOR_JSON_GIT_REPO_PATH = os.path.join(DATA_DIR, "exfor_json")
EXFORTABLES_PY_GIT_REPO_PATH = os.path.join(DATA_DIR, "exfortables_py")
ENDFTABLES_PATH = os.path.join(DATA_DIR, "libraries.all/")



""" SQL database """
engines = {
    "exfor": db.create_engine("sqlite:///" + EXFOR_DB),
    "endftables": db.create_engine("sqlite:///" + ENDFTAB_DB),
}

engine = db.create_engine("sqlite:///" + EXFOR_DB, echo=True)


session = sessionmaker(autocommit=False, autoflush=True, bind=engines["exfor"])
session_lib = sessionmaker(autocommit=False, autoflush=True, bind=engines["endftables"])
