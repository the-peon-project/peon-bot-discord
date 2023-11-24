import logging
import json
import random

# Container prefix
prefix = "peon.warcamp."

# Import lookup files
settings = json.load(open(f"/app/settings.json", 'r'))
cmd_aliases = json.load(open(f"/app/reference/aliases.json", "r"))

# Import relevant language file data
txt_quotes = json.load(open(f"/app/reference/{settings['language'].lower()}/quotes.json", "r"))
txt_commands = json.load(open(f"/app/reference/{settings['language'].lower()}/commands.json", "r"))
txt_errors = json.load(open(f"/app/reference/{settings['language'].lower()}/errors.json", "r"))

# Create a random quote selector
def get_quote():
    return random.choice(txt_quotes)

# Load orchestrators from disk
def get_peon_orcs():
    try:
        logging.debug("Loading orchestrators file") 
        return {"status" : "success" , "data" : json.load(open(f'/app/config/peon.orchestrators.json', 'r'))}
    except Exception as e:
        logging.debug("No war orchestrators file found. Creating one")
        open(f"/app/config/peon.orchestrators.json", 'a').close()
        return {"status" : "error", "info" : f"{e}"}

def identify_channel(channel_control,channel_request,args=tuple()):
    if channel_request == channel_control:
        permission='admin'
        logging.debug(f" <control channel> - {channel_control}")
    else:
        permission='user'
        logging.debug(f" <request channel> - {channel_request}")
        if args:
            args = tuple(channel_request.split('-'))[::-1] + args
        else:
            args = tuple(channel_request.split('-'))[::-1]
    args = (permission,) + args
    return args