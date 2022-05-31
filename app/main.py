# bot.py
import os
import re
from dotenv import load_dotenv
import logging
import discord
from discord.ext import commands
from modules.peon_orc_api import *
from modules.messaging import *
from modules import project_path, devMode, getPeonOrchestrators

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    channels = bot.get_all_channels()
    for channel in channels:
        if re.search('text', str(channel.category), re.IGNORECASE):
            if re.search('bot', str(channel.name), re.IGNORECASE):
                await channel.send(f" has connected to the server.\n *Type ``!usage`` for furthur information*")
    logging.info(f'[{bot.user.name}] has connected to Discord!')

@bot.command(name='poke')
async def poke(ctx, user: discord.User):
    logging.debug(f'Poke requested')
    await ctx.send(f"*{quote('hello')}*")

@bot.command(name='getall')
async def getAll(ctx):
    peon_orchestrators = getPeonOrchestrators()
    if peon_orchestrators != "EMPTY":
        response=f"*\'{quote('hello')}\'*\n"
        for orchestrator in peon_orchestrators:
            response+=f"**{orchestrator['name']}**\n```c"
            for server in getServers(orchestrator['url'],orchestrator['key'])["servers"]:
                response += f"\n{server['game_uid']}.{server['servername']}\t[{server['container_state']}]"
            response += "\n```"
    else:
        response = errorMessage('none','register')
    await ctx.send(response)

@bot.command(name='get')
async def get(ctx, *args):
    peon_orchestrators = getPeonOrchestrators()
    if len(args) != 2:
        response = errorMessage('parameterCount','get')
    elif peon_orchestrators == "EMPTY":
        response = errorMessage('none','register')
    elif not ([orchestrator for orchestrator in peon_orchestrators if args[0] == orchestrator['name']]):
        response = errorMessage('orc.dne', 'get')
    else:
        orchestrator = ([orchestrator for orchestrator in peon_orchestrators if args[0] == orchestrator['name']])[0]
        response=f"*\'{quote('ok')}\'*\n"
        apiresponse = getServer(orchestrator['url'],orchestrator['key'],args[1])
        if "error" in apiresponse:
            response = errorMessage('srv.dne', 'getall')
        else:
            response += f"**{args[1]}**\n"
            data = apiresponse['server']
            response += f"```yaml\nGameUID        : {data['game_uid']}\nServerName     : {data['servername']}\nContainerState : {data['container_state']}\nServerState    : {data['server_state']}\nDescription    : {data['description']}\n```"
    await ctx.send(response)

@bot.command(name='register')
async def register(ctx, *args):
    print("Server registration requested.")
    if len(args) != 3:
        await ctx.send(errorMessage('parameterCount','register'))


@bot.command(name='usage')
async def usage(ctx):
    await ctx.send(usageText)

####### MAIN
if __name__ == "__main__":
    if devMode:
        load_dotenv(f"{project_path}/dev/.env")
        TOKEN = os.getenv('DISCORD_TOKEN')
    else:
        TOKEN = os.environ['DISCORD_TOKEN']
    usageText = (open(f"{project_path}/documents/help.md", "r")).read()
    logging.basicConfig(filename='/var/log/peon/bot.discord.log', filemode='a', format='%(asctime)s %(thread)d [%(levelname)s] - %(message)s', level=logging.DEBUG)
    logging.debug(bot.run(TOKEN))
    