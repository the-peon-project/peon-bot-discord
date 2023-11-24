#/usr/bin/python3
import os
import sys
import re
import logging
import discord
from discord.ext import commands
from modules import *
from modules.peon_orc_api import *
from modules.shared import configure_logging

intents = discord.Intents.default()
intents.message_content = True

# Settings
bot = commands.Bot(command_prefix=settings['command_prefix'],intents=intents)
control_channel=settings['control_channel']

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
        embed.set_image(url=f"https://raw.githubusercontent.com/the-peon-project/peon-warplans/main/{game_uid}/logo.png")
    return embed

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
    await ctx.send(embed=build_card(image_url=settings['logo']))

@bot.command(name='getall',aliases=cmd_aliases["getall"])
async def get_all(ctx):
    logging.debug("Servers & hosts \'get\' requested")
    if ctx.channel.name == control_channel:
        if "success" in ( peon_orchestrators := get_peon_orcs())['status']: # type: ignore
            response = get_servers_all(peon_orchestrators['data'])
            await ctx.send(embed=build_card(title="All Servers",message=response['data']))
        else:
            await ctx.send(embed=build_card_err(err_code="orc.none",command="register",permission="admin"))
    else:
        await ctx.send(embed=build_card_err(err_code="unauthorized",command="auth",permission="user"))

@bot.command(name='get',aliases=cmd_aliases["get"])
async def get(ctx, *args):
    args = identify_channel(channel_control=control_channel,channel_request=ctx.channel.name, args=args)
    logging.debug(f"Server GET requested - {args} ")
    if "success" in (response := server_actions('get', args))['status']: embed = build_card(title="Get Server",message=response['data']) # type: ignore
    else: embed = build_card_err(err_code=response['err_code'],command=response['command'],permission=args[0]) 
    await ctx.send(embed=embed)

@bot.command(name='start',aliases=cmd_aliases["start"])
async def start(ctx, *args):
    args = identify_channel(channel_control=control_channel,channel_request=ctx.channel.name, args=args)
    logging.info(f"Server START requested - {args} ")
    if "success" in (response := server_actions('start', args))['status']: embed = build_card(title="Start Server",message=response['data']) # type: ignore
    else: embed = build_card_err(err_code=response['err_code'],command=response['command'],permission=args[0]) 
    await ctx.send(embed=embed)
    
@bot.command(name='update',aliases=cmd_aliases["update"])
async def update(ctx, *args):
    args = identify_channel(channel_control=control_channel,channel_request=ctx.channel.name, args=args)
    logging.info(f"Server UPDATE requested - {args} ")
    if "success" in (response := server_actions('update', args))['status']: embed = build_card(title="Update Server",message=response['data']) # type: ignore
    else: embed = build_card_err(err_code=response['err_code'],command=response['command'],permission=args[0]) 
    await ctx.send(embed=embed)

@bot.command(name='stop',aliases=cmd_aliases["stop"])
async def stop(ctx, *args):
    args = identify_channel(channel_control=control_channel,channel_request=ctx.channel.name, args=args)
    logging.info(f"Server STOP requested - {args} ")
    if "success" in (response := server_actions('stop', args))['status']: embed = build_card(title="Stop Server",message=response['data']) # type: ignore
    else: embed = build_card_err(err_code=response['err_code'],command=response['command'],permission=args[0]) 
    await ctx.send(embed=embed)

@bot.command(name='restart',aliases=cmd_aliases["restart"])
async def restart(ctx, *args):
    args = identify_channel(channel_control=control_channel,channel_request=ctx.channel.name, args=args)
    logging.info(f"Server RESTART requested - {args} ")
    if "success" in (response := server_actions('restart', args))['status']: embed = build_card(title="Restart Server",message=response['data']) # type: ignore
    else: embed = build_card_err(err_code=response['err_code'],command=response['command'],permission=args[0]) 
    await ctx.send(embed=embed)

@bot.command(name='register',aliases=cmd_aliases["register"])
async def register(ctx, *args):
    args = identify_channel(channel_control=control_channel,channel_request=ctx.channel.name, args=args)
    logging.info("Server REGISTRATION requested.")
    if len(args) != 3:
        response = "TODO" # error_message('parameterCount', 'register')
        await ctx.send(response)

@bot.command(name='usage',aliases=cmd_aliases["usage"])
async def usage(ctx):
    response = "TODO"
    await ctx.send("TODO")

@bot.command(name='clear',aliases=cmd_aliases["clear"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if ctx.channel.name == control_channel:
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"{amount} message(s) got deleted")
    else:
        response = "TODO" # error_message('unauthorized', 'auth')
        await ctx.send(response)
        
@bot.command(name='plans')
async def get_plans(ctx):
    logging.debug("All plans \'get\' requested")
    if ctx.channel.name == control_channel:
        if "success" in (peon_orchestrators := get_peon_orcs())['status']: # type: ignore
            response = get_warplans(peon_orchestrators['data'])
        else: response = "TODO" # error_message('none', 'register')
    else: response = "TODO" # error_message('unauthorized', 'auth')
    await ctx.send(response)
    
@bot.command(name='plan')
async def get_plan(ctx, *args):
    logging.debug("Plan 'get' requested")
    if ctx.channel.name == control_channel:
        if "success" in (peon_orchestrators := get_peon_orcs())['status']: # type: ignore
            if "success" in (response := get_warplan(peon_orchestrators['data'], args))["status"]: # type: ignore
                embed = discord.Embed()
                embed.set_thumbnail(url=response['image_url'])
                embed.add_field(name='WARPLAN', value=response['message'])
                await ctx.send(embed=embed)
            else:
                await ctx.send(response['message'])
        else:
            response = "TODO" #error_message('none', 'register')
            await ctx.send(response)
    else:
        response = "TODO" # error_message('unauthorized', 'auth')
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