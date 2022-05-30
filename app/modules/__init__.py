import json
import os
import logging

project_path = "/".join(((os.path.dirname(__file__)).split("/"))[:-1])

# Settings file
settings = json.load(open(f"{project_path}/settings.json", 'r'))
# Container prefix
prefix = "peon.warcamp."

def getPeonOrchestrators():
    try:
        logging.debug("Loading orchestrators file") 
        return json.load(open(f"{project_path}/peon.orchestrators.json", 'r'))
    except:
        logging.debug("No warorchestrators file found. Creating one")
        open(f"{project_path}/peon.orchestrators.json", 'a').close()
        return "EMPTY"