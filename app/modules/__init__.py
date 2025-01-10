import logging
import json
import random
import os

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
        config_file = "/app/config/peon.orchestrators.json"
        logging.debug("Loading orchestrators file")
        with open(config_file, 'r') as file:
            orchestrators = json.load(file)
        API_KEY = os.environ.get('LOCAL_API_KEY',None)
        if API_KEY:
            for entry in orchestrators:
                if entry["url"] == "http://peon.orc:5000":
                    entry["key"] = API_KEY
                break
            with open(config_file, 'w') as file:
                json.dump(orchestrators, file, indent=4)
        return {"status": "success", "data": orchestrators}
    
    except FileNotFoundError:
        logging.debug("No orchestrators file found. Creating one.")
        # Create an empty orchestrators file with a default structure
        default_data = []
        with open(config_file, 'w') as file:
            json.dump(default_data, file, indent=4)
        return {"status": "error", "info": "Orchestrators file not found. Created a new one."}
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"status": "error", "info": str(e)}

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