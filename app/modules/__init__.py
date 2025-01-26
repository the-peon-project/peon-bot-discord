import logging
import json
import random
import os
import re
import sys

# Settings
base_url = "https://raw.githubusercontent.com/the-peon-project"
games_url = f"{base_url}/peon-docs/refs/heads/main/manual/docs/games.md"
bot_image = f"{base_url}/peon/refs/heads/main/media/PEON_L2R_medium.png"
bot_thumbnail = f"{base_url}/peon/refs/heads/main/media/PEON_R2L_small.png"

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

def look_for_regex_in_args(regex,args):
    try:
        for argument in args:
            match = re.search(regex, argument)
            if match:
                # logging.debug(f"Found {match[0]}")
                return match[0]
    except:
        return None
    
def configure_logging():
    dev_mode = os.environ.get('DEV_MODE', 'disabled')
    print(f"DEV MODE [{dev_mode}]")
    # Set up logging to stdout
    root_logger = logging.getLogger()
    stdout_handler = logging.StreamHandler(sys.stdout)
    root_logger.addHandler(stdout_handler)

    # Set the log format and level
    log_format = '%(asctime)s %(thread)d [%(levelname)s] %(message)s'
    
    log_level = logging.DEBUG if dev_mode == 'enabled' else logging.INFO
    # Configure logging to append to Docker container logs
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[stdout_handler],
        force=True  # This ensures we override any existing configuration
    )
    
    # Ensure discord.py's logger doesn't overwhelm your logs
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.WARNING)