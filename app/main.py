# bot.py
import os
import random
import json

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

responses=json.load(open("/root/peon-bot-discord/app/documents/quotes.json"))

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='poke')
async def nine_nine(ctx):
    peon_quotes = responses["respond"]

    response = random.choice(peon_quotes)
    await ctx.send(response)

bot.run(TOKEN)