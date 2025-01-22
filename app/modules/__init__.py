import logging
import json
import random
import os
import re
import discord

# Settings
base_url = "https://raw.githubusercontent.com/the-peon-project"
games_url = f"{base_url}/peon-docs/refs/heads/main/manual/docs/games.md"

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

def identify_channel(channel_request,args=tuple()):
    if channel_request == settings['control_channel']:
        permission='admin'
        logging.debug(f" <control channel> - {settings['control_channel']}")
    else:
        permission='user'
        logging.debug(f" <request channel> - {settings['control_channel']}")
        if args:
            args = tuple(channel_request.split('-'))[::-1] + args
        else:
            args = tuple(channel_request.split('-'))[::-1]
    args = (permission,) + args
    return args

def look_for_regex_in_args(regex,args):
    try:
        for argument in args:
            match = re.search(regex, argument)
            if match:
                logging.debug(f"{match[0]}")
                return match[0]
    except:
        return None

def build_card_err(err_code='bad.code',command='bad.code',permission='user'):
    embed = discord.Embed(color=discord.Color.orange())
    embed.description = '_"{0}"_'.format(txt_errors[err_code])
    code = txt_commands[command][permission]
    note = txt_commands[command]['note']
    message=f"{note}"
    if code:
        message+=f"```bash\n{code}```"
    embed.add_field(name=f"Request failure",value=message)
    return embed

def build_card(title=None,message=None,image_url=None,thumbnail_url=None,game_uid=None):
    embed = discord.Embed(color=discord.Color.green())
    embed.description = f'_"{get_quote()}"_'
    if message:
        embed.add_field(name=title, value=message)
    if image_url:
        embed.set_image(url=image_url)
    elif thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    elif game_uid:
        embed.set_image(url=f"{base_url}/peon-warplans/main/{game_uid}/logo.png")
    return embed