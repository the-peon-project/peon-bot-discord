#/usr/bin/python3
import os
import re
import logging
import discord
from discord.ext import commands
from modules.peon_orc_api import *
from modules.messaging import *
from modules import project_path, usage_text, settings

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!',intents=intents)

@bot.event
async def on_ready():
    channels = bot.get_all_channels()
    for channel in channels:
        if re.search('text', str(channel.category), re.IGNORECASE):
            if re.search('bot', str(channel.name), re.IGNORECASE):
                await channel.send(" has connected to the server.\n *Type ``!usage`` for furthur information*")
    logging.info(f'[{bot.user.name}] has connected to Discord!')

@bot.command(name='poke')
async def poke(ctx):
    logging.debug('Poke requested')
    await ctx.send(f"*{quote('hello')}*")

@bot.command(name='getall',aliases=settings["aliases"]["getall"])
async def get_all(ctx):
    logging.debug("Servers & hosts \'get\' requested")
    if "success" in ( peon_orchestrators := get_peon_orcs())['status']: # type: ignore
        response = get_servers_all(peon_orchestrators['data'])
    else:
        response = error_message('none', 'register') 
    await ctx.send(response)

@bot.command(name='get',aliases=settings["aliases"]["get"])
async def get(ctx, *args):
    logging.debug(f"Server get requested - {args} ")
    await ctx.send(server_actions('get', args))

@bot.command(name='start',aliases=settings["aliases"]["start"])
async def start(ctx, *args):
    logging.info(f"Server start requested - {args} ")
    await ctx.send(server_actions('start', args))

@bot.command(name='stop',aliases=settings["aliases"]["stop"])
async def stop(ctx, *args):
    logging.info(f"Server stop requested - {args} ")
    await ctx.send(server_actions('stop', args))


@bot.command(name='restart',aliases=settings["aliases"]["restart"])
async def restart(ctx, *args):
    logging.info(f"Server restart requested - {args} ")
    await ctx.send(server_actions('restart', args))


@bot.command(name='register',aliases=settings["aliases"]["register"])
async def register(ctx, *args):
    logging.info("Server registration requested.")
    if len(args) != 3:
        await ctx.send(error_message('parameterCount', 'register'))


@bot.command(name='usage',aliases=settings["aliases"]["usage"])
async def usage(ctx):
    await ctx.send(usage_text)

@bot.command(name='clear',aliases=settings["aliases"]["clear"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{amount} message(s) got deleted")

# MAIN
if __name__ == "__main__":
    TOKEN = os.environ['DISCORD_TOKEN']
    logging.basicConfig(filename='/var/log/peon/bot.discord.log', filemode='a',format='%(asctime)s %(thread)d [%(levelname)s] - %(message)s', level=logging.DEBUG)
    logging.debug(bot.run(TOKEN))
