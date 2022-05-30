# bot.py
import os
import random
import json
import re

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

responses=json.load(open("/root/peon-bot-discord/app/documents/quotes.json"))
with open('/root/peon-bot-discord/app/documents/help.md') as f:
    helpText = f.readlines()

usageText = (open("/root/peon-bot-discord/app/documents/help.md", "r")).read()

@bot.event
async def on_ready():
    channels = bot.get_all_channels()
    for channel in channels:
        if re.search('text', str(channel.category), re.IGNORECASE):
            if re.search('bot', str(channel.name), re.IGNORECASE):
                await channel.send(f" has connected to the server.\n *Type ``!usage`` for furuthur information*")
    print(f'[{bot.user.name}] has connected to Discord!')

@bot.command(name='poke')
async def poke(ctx):
    await ctx.send(random.choice(responses["respond"]))

@bot.command(name='usage')
async def usage(ctx):
    await ctx.send(usageText)

bot.run(TOKEN)