#/usr/bin/python3
import os
import json
import sys
import re
import logging
import discord
from discord.ext import commands
from modules import *
from modules.administrator import *
from modules.orchestrator import *
from modules.shared import configure_logging
import requests

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=settings['command_prefix'],intents=intents)

@bot.event
async def on_ready():
    channels = bot.get_all_channels()
    for channel in channels:
        if settings['control_channel'] == str(channel.name):
            await channel.send(" has connected to the server.")
    logging.info(f'[{bot.user.name}] has connected to Discord!')

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