# bot.py
import os
import re
from dotenv import load_dotenv
import logging
from discord.ext import commands
from modules.peon_orc_api import *
from modules.messaging import *
from modules import project_path, devMode

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
async def poke(ctx):
    logging.debug(f'Poke requested')
    await ctx.send(f"*{quote('hello')}*")


@bot.command(name='getall')
async def getAll(ctx):
    logging.debug(f"Servers & hosts \'get\' requested")
    peon_orchestrators = getPeonOrchestrators()
    if peon_orchestrators != "EMPTY":
        response = getServersAll(peon_orchestrators)
    else:
        response = errorMessage('none', 'register')
    await ctx.send(response)


@bot.command(name='get')
async def get(ctx, *args):
    logging.debug(f"Server get requested - {args[0]} {args[1]}")
    await ctx.send(serverActions('get', args))


@bot.command(name='start')
async def start(ctx, *args):
    logging.info(f"Server start requested - {args[0]} {args[1]}")
    await ctx.send(serverActions('start', args))


@bot.command(name='stop')
async def stop(ctx, *args):
    logging.info(f"Server stop requested - {args[0]} {args[1]}")
    await ctx.send(serverActions('stop', args))


@bot.command(name='restart')
async def restart(ctx, *args):
    logging.info(f"Server restart requested - {args[0]} {args[1]}")
    await ctx.send(serverActions('restart', args))


@bot.command(name='register')
async def register(ctx, *args):
    logging.info("Server registration requested.")
    if len(args) != 3:
        await ctx.send(errorMessage('parameterCount', 'register'))


@bot.command(name='usage')
async def usage(ctx):
    await ctx.send(usageText)

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{amount} message(s) got deleted")

# MAIN
if __name__ == "__main__":
    if devMode:
        load_dotenv(f"{project_path}/dev/.env")
        TOKEN = os.getenv('DISCORD_TOKEN')
    else:
        TOKEN = os.environ['DISCORD_TOKEN']
    usageText = (open(f"{project_path}/documents/help.md", "r")).read()
    logging.basicConfig(filename='/var/log/peon/bot.discord.log', filemode='a',
                        format='%(asctime)s %(thread)d [%(levelname)s] - %(message)s', level=logging.DEBUG)
    logging.debug(bot.run(TOKEN))
