import json
import os
import logging

# Container prefix
prefix = "peon.warcamp."
# Project working directory
project_path = "/".join(((os.path.dirname(__file__)).split("/"))[:-1])
# Configuration file
settings = json.load(open(f"{project_path}/settings.json", 'r'))

usage_text = (open(f"{project_path}/config/documents/help.md", "r")).read()

def get_peon_orcs():
    try:
        logging.debug("Loading orchestrators file") 
        return {"status" : "success" , "data" : json.load(open(f'{project_path}/config/peon.orchestrators.json', 'r'))}
    except Exception as e:
        logging.debug("No war orchestrators file found. Creating one")
        open(f"{project_path}/config/peon.orchestrators.json", 'a').close()
        return {"status" : "error", "info" : f"{e}"}