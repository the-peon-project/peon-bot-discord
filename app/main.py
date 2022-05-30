# bot.py
import os
import re
import logging
from discord.ext import commands
from dotenv import load_dotenv
from modules.peon_orc_api import *
from modules.messaging import *
from modules import project_path, settings


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

usageText = (open(f"{project_path}/documents/help.md", "r")).read()

@bot.event
async def on_ready():
    channels = bot.get_all_channels()
    for channel in channels:
        if re.search('text', str(channel.category), re.IGNORECASE):
            if re.search('bot', str(channel.name), re.IGNORECASE):
                await channel.send(f" has connected to the server.\n *Type ``!usage`` for furthur information*")
    print(f'[{bot.user.name}] has connected to Discord!')


@bot.command(name='poke')
async def poke(ctx):
    await ctx.send(f"*{quote('hello')}*")

@bot.command(name='getall')
async def getAll(ctx):
    serverString="```c"
    for server in getServers("http://dockerdev.za.cloudlet.cloud:5000","my-super-secret-api-key")["servers"]:
        serverString = f"{serverString}\n{server['game_uid']}.{server['servername']}"
    serverString = f"{serverString}\n```"
    await ctx.send(serverString)

@bot.command(name='register')
async def register(ctx, *args):
    print("Server registration requested.")
    if len(args) != 3:
        await ctx.send(errorMessage('parameterCount','register'))


@bot.command(name='usage')
async def usage(ctx):
    await ctx.send(usageText)

bot.run(TOKEN)
