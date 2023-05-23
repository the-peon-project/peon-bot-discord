import json
import os
import logging

# Container prefix
prefix = "peon.warcamp."
# Project working directory
project_path = "/".join(((os.path.dirname(__file__)).split("/"))[:-1])
# Configuration file
settings = json.load(open(f"{project_path}/settings.json", 'r'))

usageText = (open(f"{project_path}/config/documents/help.md", "r")).read()

def dev_mode():
    if os.path.isdir(f"{project_path}/dev"):
        logging.warn("DEV MODE ENABLED")
        return True
    else:
        return False

def get_peon_orchestrators():
    try:
        logging.debug("Loading orchestrators file") 
        return json.load(open(f"{project_path}/config/peon.orchestrators.json", 'r'))
    except:
        logging.debug("No war orchestrators file found. Creating one")
        open(f"{project_path}/config/peon.orchestrators.json", 'a').close()
        return "EMPTY"