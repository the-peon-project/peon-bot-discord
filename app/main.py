#/usr/bin/python3
import os
import json
import sys
import re
import logging
import discord
from discord.ext import commands
from modules import *
from modules.peon_orc_api import *
from modules.shared import configure_logging
import requests

intents = discord.Intents.default()
intents.message_content = True

# Settings
games_url = "https://raw.githubusercontent.com/the-peon-project/peon-docs/refs/heads/main/manual/docs/games.md"
bot = commands.Bot(command_prefix=settings['command_prefix'],intents=intents)

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
        if settings['control_channel'] == str(channel.name):
            await channel.send(" has connected to the server.")
    logging.info(f'[{bot.user.name}] has connected to Discord!')

@bot.command(name='poke')
async def poke(ctx):
    logging.debug('Poke requested')
    await ctx.send(embed=build_card(image_url=settings['logo']))

@bot.command(name='about')
async def get_plans(ctx):
    logging.debug("'About' requested")
    response = "## [The PEON Project](<https://warcamp.org>)\n"
    response += "> A community-driven project to provide automated deployment and managing community game servers.\n\n"
    response += "The project is open-source, free to use and is maintained by volunteers and donations.\n"
    response += "### Versions\n"
    response += f"Orchestrator: [-.-.-](<https://docs.warcamp.org/development/01_orchestrator/>)\n"
    response += f"Bot-Discord: [{os.environ.get('VERSION', '-.-.-')}](<https://docs.warcamp.org/development/50_bot_discord/>)\n"
    try:
        file_contents = requests.get(games_url).text
        response += "### Supported Games\nBelow is a list of games that are currently supported by the PEON Project.\n"
        for line in file_contents.splitlines():
            if re.search('- \[x\]', line):
                line = re.sub('- \[x\]', '- ', line)
                line = re.sub('./guides/games/', 'https://docs.warcamp.org/guides/games/', line)
                line = re.sub('.md', '', line)
                response += line + '\n'
        response += "To see which other game servers are currently being built go [here](<https://docs.warcamp.org/games>).\n"
        response += "To request a different game server please log a request as an issue [here](<https://github.com/the-peon-project/peon-warplans/issues>).\n"
        response += "### Bugs/Issues\nPlease log any bugs or issues [here](<https://github.com/the-peon-project/peon/issues>).\n"
        response += "### Donations\nIf you would like to donate to the project please go [here](<https://ko-fi.com/umlatt>).\n"
        response += "### Community\nJoin the community on [Discord](<https://discord.gg/KJFVyayH8g>)\n"
        embed = discord.Embed(description=response)
        embed.set_image(url="https://raw.githubusercontent.com/the-peon-project/peon/refs/heads/main/media/PEON_outline_small.png")
    except requests.RequestException as e:
        logging.error(f"Failed to fetch file contents: {e}")
        embed = build_card_err(err_code="bad.code",command="bad.code",permission='user')
    finally:
        await ctx.send(embed=embed)

@bot.command(name='getall',aliases=cmd_aliases["getall"])
async def get_all(ctx):
    args = identify_channel(channel_request=ctx.channel.name)
    logging.debug(f"Servers & hosts GET requested - {args} ")
    if args[0] == 'admin':
        if "success" in ( peon_orchestrators := get_peon_orcs())['status']: embed = build_card(title="All Servers",message=get_servers_all(peon_orchestrators['data'])['data'])
        else: embed=build_card_err(err_code="orc.none",command="register",permission='admin')
    else: embed=build_card_err(err_code="unauthorized",command="auth",permission='user')
    await ctx.send(embed=embed)

@bot.command(name='get',aliases=cmd_aliases["get"])
async def get(ctx, *args):
    args = identify_channel(channel_request=ctx.channel.name, args=args)
    logging.debug(f"Server GET requested - {args} ")
    if "success" in (response := server_actions('get', args))['status']: embed = build_card(title="Get Server",message=response['data'])
    else: embed = build_card_err(err_code=response['err_code'],command=response['command'],permission=args[0]) 
    await ctx.send(embed=embed)

@bot.command(name='start',aliases=cmd_aliases["start"])
async def start(ctx, *args):
    args = identify_channel(channel_request=ctx.channel.name, args=args)
    logging.info(f"Server START requested - {args} ")
    if "success" in (response := server_actions('start', args))['status']: embed = build_card(title="Start Server",message=response['data'])
    else: embed = build_card_err(err_code=response['err_code'],command=response['command'],permission=args[0]) 
    await ctx.send(embed=embed)
    
@bot.command(name='update',aliases=cmd_aliases["update"])
async def update(ctx, *args):
    args = identify_channel(channel_request=ctx.channel.name, args=args)
    logging.info(f"Server UPDATE requested - {args} ")
    if "success" in (response := server_actions('update', args))['status']: embed = build_card(title="Update Server",message=response['data'])
    else: embed = build_card_err(err_code=response['err_code'],command=response['command'],permission=args[0]) 
    await ctx.send(embed=embed)

@bot.command(name='stop',aliases=cmd_aliases["stop"])
async def stop(ctx, *args):
    args = identify_channel(channel_request=ctx.channel.name, args=args)
    logging.info(f"Server STOP requested - {args} ")
    if "success" in (response := server_actions('stop', args))['status']: embed = build_card(title="Stop Server",message=response['data'])
    else: embed = build_card_err(err_code=response['err_code'],command=response['command'],permission=args[0]) 
    await ctx.send(embed=embed)

@bot.command(name='restart',aliases=cmd_aliases["restart"])
async def restart(ctx, *args):
    args = identify_channel(cchannel_request=ctx.channel.name, args=args)
    logging.info(f"Server RESTART requested - {args} ")
    if "success" in (response := server_actions('restart', args))['status']: embed = build_card(title="Restart Server",message=response['data'])
    else: embed = build_card_err(err_code=response['err_code'],command=response['command'],permission=args[0]) 
    await ctx.send(embed=embed)

@bot.command(name='register',aliases=cmd_aliases["register"])
async def register(ctx, *args):
    args = identify_channel(channel_request=ctx.channel.name, args=args)
    logging.info("Server REGISTRATION requested.")
    if len(args) != 3:
        response = "TODO" # error_message('parameterCount', 'register')
        await ctx.send(response)

@bot.command(name='usage',aliases=cmd_aliases["usage"])
async def usage(ctx):
    args = identify_channel(channel_request=ctx.channel.name)
    with open(f"/app/reference/{settings['language']}/commands.json", 'r') as file:
        commands = json.load(file)
    response = ""
    for command, info in commands.items():
        if info[args[0]]:
            if args[0] == 'admin':
                response += f"`{info[args[0]]}` {info['note']}\n\n"
            else:
                response += f"**{command.capitalize()}** {info['symbol']} `{info[args[0]]}`\n"
                response += f"{info['note']}\n\n"
    embed = build_card(title="Usage Information",message=response)
    await ctx.send(embed=embed)
        
@bot.command(name='plans')
async def get_plans(ctx):
    logging.debug("All plans \'get\' requested")
    args = identify_channel(channel_request=ctx.channel.name)
    if "success" in (peon_orchestrators := get_peon_orcs())['status']:
        if "success" in (warplans := get_warplans(peon_orchestrators['data']))['status']:
            embed = build_card(title="War Plans",message=warplans['data'])
        else: embed = build_card_err(err_code="plans.dne",command="plans",permission=args[0])
    else: embed = build_card_err(err_code="orc.none",command="register",permission=args[0])
    await ctx.send(embed=embed)
    
@bot.command(name='plan')
async def get_plan(ctx, *args):
    logging.debug("Plan 'get' requested")
    if ctx.channel.name == settings['control_channel']:
        if "success" in (peon_orchestrators := get_peon_orcs())['status']:
            if "success" in (response := get_warplan(peon_orchestrators['data'], args))["status"]:
                embed = discord.Embed()
                embed.set_thumbnail(url=response['image_url'])
                embed.add_field(name='WARPLAN', value=response['message'])
                await ctx.send(embed=embed)
            else:
                await ctx.send(response['message'])
        else:
            response = "TODO" #error_message('none', 'register') # TODO
            await ctx.send(response)
    else:
        response = "TODO" # error_message('unauthorized', 'auth') # TODO
        await ctx.send(response)

# Atypical structure
@bot.command(name='clear',aliases=cmd_aliases["clear"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    args = identify_channel(channel_request=ctx.channel.name)
    if args[0] == 'admin': await ctx.channel.purge(limit=amount + 1)
    else: await ctx.send(embed=build_card_err(err_code="unauthorized",command="auth",permission=args[0]))

# MAIN
if __name__ == "__main__":
    # Configure logging
    configure_logging()
    # Get Discord token
    print("\n------------------------------\nStarting Discord Bot...\n------------------------------\n")
    TOKEN = os.environ.get('DISCORD_TOKEN', None)
    if TOKEN:
        bot.run(TOKEN)
    else:
        logging.error("Please create and configure a valid Discord token.")
        # Force a non-zero exit status
        exit_status = 2
        sys.exit(exit_status)