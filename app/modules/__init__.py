import json
import os
import logging

project_path = "/".join(((os.path.dirname(__file__)).split("/"))[:-1])

# Settings file
settings = json.load(open(f"{project_path}/settings.json", 'r'))
# Container prefix
prefix = "peon.warcamp."

def getWarParties():
    try:
        logging.debug("Loading warcamps file") 
        return json.load(open(f"{project_path}/warparties.json", 'r'))
    except:
        logging.debug("No warcamp file found. Creating one")
        open(f"{project_path}/warparties.json", 'a').close()
        return "EMPTY"