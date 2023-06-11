#/usr/bin/python3
import os
import sys
import re
import logging
import discord
from discord.ext import commands
from modules import usage_text, settings, identify_channel
from modules.peon_orc_api import *
from modules.messaging import *
from modules.shared import configure_logging

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!',intents=intents)

control_channel='peon'

@bot.event
async def on_ready():
    channels = bot.get_all_channels()
    for channel in channels:
        if re.search('text', str(channel.category), re.IGNORECASE):
            if re.search(control_channel, str(channel.name), re.IGNORECASE):
                await channel.send(" has connected to the server.\n *Type ``!usage`` for furthur information*")
    logging.info(f'[{bot.user.name}] has connected to Discord!')

@bot.command(name='poke')
async def poke(ctx):
    logging.debug('Poke requested')
    await ctx.send(f"*{quote('hello')}*")

@bot.command(name='getall',aliases=settings["aliases"]["getall"])
async def get_all(ctx):
    logging.debug("Servers & hosts \'get\' requested")
    if ctx.channel.name == control_channel:
        if "success" in ( peon_orchestrators := get_peon_orcs())['status']: # type: ignore
            response = get_servers_all(peon_orchestrators['data'])
        else:
            response = error_message('none', 'register')
    else:
        response = error_message('unauthorized', 'auth')
    await ctx.send(response)

@bot.command(name='get',aliases=settings["aliases"]["get"])
async def get(ctx, *args):
    args = identify_channel(channel_control=control_channel,channel_request=ctx.channel.name, args=args)
    logging.debug(f"Server GET requested - {args} ")
    await ctx.send(server_actions('get', args))

@bot.command(name='start',aliases=settings["aliases"]["start"])
async def start(ctx, *args):
    args = identify_channel(channel_control=control_channel,channel_request=ctx.channel.name, args=args)
    logging.info(f"Server START requested - {args} ")
    await ctx.send(server_actions('start', args))

@bot.command(name='stop',aliases=settings["aliases"]["stop"])
async def stop(ctx, *args):
    args = identify_channel(channel_control=control_channel,channel_request=ctx.channel.name, args=args)
    logging.info(f"Server STOP requested - {args} ")
    await ctx.send(server_actions('stop', args))

@bot.command(name='restart',aliases=settings["aliases"]["restart"])
async def restart(ctx, *args):
    args = identify_channel(channel_control=control_channel,channel_request=ctx.channel.name, args=args)
    logging.info(f"Server RESTART requested - {args} ")
    await ctx.send(server_actions('restart', args))

@bot.command(name='register',aliases=settings["aliases"]["register"])
async def register(ctx, *args):
    args = identify_channel(channel_control=control_channel,channel_request=ctx.channel.name, args=args)
    logging.info("Server REGISTRATION requested.")
    if len(args) != 3:
        await ctx.send(error_message('parameterCount', 'register'))

@bot.command(name='usage',aliases=settings["aliases"]["usage"])
async def usage(ctx):
    await ctx.send(usage_text)

@bot.command(name='clear',aliases=settings["aliases"]["clear"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if ctx.channel.name == control_channel:
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"{amount} message(s) got deleted")
    else:
        await ctx.send(error_message('unauthorized', 'auth'))
        
@bot.command(name='plans')
async def get_plans(ctx):
    logging.debug("All plans \'get\' requested")
    if ctx.channel.name == control_channel:
        if "success" in (peon_orchestrators := get_peon_orcs())['status']: # type: ignore
            response = get_warplans(peon_orchestrators['data'])
        else: response = error_message('none', 'register')
    else: response = error_message('unauthorized', 'auth')
    await ctx.send(response)
    
@bot.command(name='plan')
async def get_plan(ctx, *args):
    logging.debug("Plan 'get' requested")
    if ctx.channel.name == control_channel:
        if "success" in (peon_orchestrators := get_peon_orcs())['status']: # type: ignore
            if "success" in (response := get_warplan(peon_orchestrators['data'], args))["status"]: # type: ignore
                embed = discord.Embed()
                embed.set_image(url=response['image_url'])
                embed.add_field(name='WARPLAN', value=response['message'])
                await ctx.send(embed=embed)
            else:
                await ctx.send(response['message'])
        else:
            response = error_message('none', 'register')
            await ctx.send(response)
    else:
        response = error_message('unauthorized', 'auth')
        await ctx.send(response)

# MAIN
if __name__ == "__main__":
    # Configure logging
    configure_logging()
    # Get Discord token
    TOKEN = os.environ.get('DISCORD_TOKEN', None)
    if TOKEN:
        logging.debug(bot.run(TOKEN))
    else:
        logging.error("Please create and configure a valid Discord token.")
        # Force a non-zero exit status
        exit_status = 2
        sys.exit(exit_status)