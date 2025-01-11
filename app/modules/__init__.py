import logging
import json
import random
import os

# Container prefix
prefix = "peon.warcamp."

# Import lookup files
cmd_aliases = json.load(open(f"/app/reference/aliases.json", "r"))
settings={}
settings['language'] = os.environ.get('LANGUAGE', 'english').lower()
settings['timezone'] = os.environ.get('TIMEZONE', 'UTC')
settings['command_prefix'] = os.environ.get('COMMAND_PREFIX', '!')
settings['control_channel'] = os.environ.get('CONTROL_CHANNEL', 'peon')

# Import relevant language file data
language=os.environ.get('LANGUAGE', 'english').lower()
txt_quotes = json.load(open(f"/app/reference/{settings['language']}/quotes.json", "r"))
txt_commands = json.load(open(f"/app/reference/{settings['language']}/commands.json", "r"))
txt_errors = json.load(open(f"/app/reference/{settings['language']}/errors.json", "r"))

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
                    if entry["key"] != API_KEY:
                        logging.debug("Updating orchestrator API key")
                        entry["key"] = f"'{API_KEY}'"
                        with open(config_file, 'w') as file:
                            json.dump(orchestrators, file, indent=4)
                        entry["key"] = API_KEY
                break
        return {"status": "success", "data": orchestrators}
    except FileNotFoundError:
        logging.debug("No orchestrators file found. Creating one.")
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