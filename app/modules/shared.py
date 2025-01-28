import logging
import sys
import requests
import os
import discord
from . import *
from .orchestrator import get_peon_orcs, get_orchestrator_details

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

def build_card(status='err',message="*HEY DEV, SOMETHING WENT WRONG BUT PEON NEED SOMETHING TO SAY!!!*"):
    if   status == 'ok':  embed = discord.Embed(description=f"{message}",color=discord.Color.blue())
    elif status == 'nok': embed = discord.Embed(description=f"{message}",color=discord.Color.orange())
    elif status == 'err': embed = discord.Embed(description=f"{message}",color=discord.Color.red())
    else:                 embed = discord.Embed(description=f"{message}")
    return embed

def build_about_card():
    with open(f"/app/reference/{settings['language']}/about.md", "r") as file:
        response = file.read()
    response = response.replace('[BOT_VERSION]',os.environ.get('VERSION', '-.-.-'))
    if (orchestrators := get_peon_orcs())['status'] == "success":
        if orchestrators['data']:
            orcstring = ""
            for orc in orchestrators['data']:
                if (orc_response := get_orchestrator_details(url=orc['url'],api_key=orc['key']))['status'] == "success":
                    info = orc_response['data']
                    orcstring += f"- Orchestrator: {orc['name']} [{info['version']}](<https://docs.warcamp.org/development/50_bot_discord/#release-notes>)\n"
                else:
                    orcstring += f"- Orchestrator: {orc['name']} [UNKNOWN](<https://docs.warcamp.org/development/50_bot_discord/#release-notes>)\n"
            response = response.replace('[ORCHESTRATORS]',f"{orcstring}")
    try:
        file_contents = requests.get(games_url).text
        servers = "### Supported Games\nBelow is a list of games that are currently supported by the PEON Project.\n"
        for line in file_contents.splitlines():
            if re.search('- \[x\]', line):
                line = re.sub('- \[x\]', '- ', line)
                line = re.sub('./guides/games/', 'https://docs.warcamp.org/guides/games/', line)
                line = re.sub('.md', '', line)
                servers += line + '\n'
    except:
        servers = ""
    response = response.replace('[GAME_SERVERS]',servers)
    embed = discord.Embed(description=response)
    embed.set_image(url=bot_image) 
    return embed