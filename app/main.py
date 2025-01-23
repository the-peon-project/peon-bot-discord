#/usr/bin/python3
import os
import json
import sys
import re
import logging
import discord
from discord.ext import commands
from modules import *
from modules.orchestrator import *
from modules.administrator import *
from modules.user import *
from modules.shared import configure_logging

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=settings['command_prefix'],intents=intents)

@bot.event
async def on_ready():
    logging.info(f'[{bot.user.name}] has connected to Discord!')
    channels = bot.get_all_channels()
    for channel in channels:
        if settings['control_channel'] == str(channel.name):
            await channel.send(" has connected to the server.")
            # view = AdministratorActions()
            # embed = discord.Embed(
            #     title="Peon Administrator",
            #     description="Use the buttons to manage your Peon.",
            #     color=discord.Color.green()
            # )
            # await channel.send(embed=embed, view=view)  
        else:
            if str(channel.name) == 'valheim-ocs':
                view = UserActions(gameuid=(str(channel.name)).split('-')[0],servername=(str(channel.name)).split('-')[1])
                embed = discord.Embed(
                    title="Peon",
                    description="Use the buttons to manage your Peon.",
                    color=discord.Color.blue()
                )
                await channel.send(embed=embed, view=view)  

@bot.command(name='clear',aliases=cmd_aliases["clear"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    args = identify_channel(channel_request=ctx.channel.name)
    if args[0] == 'admin': await ctx.channel.purge(limit=amount + 1)
    else: await ctx.send(embed=build_card_err(err_code="unauthorized",command="auth",permission=args[0]))

# MAIN
if __name__ == "__main__":
    # Configure logging
    configure_logging()
    print("\n------------------------------\nStarting Discord Bot...\n------------------------------\n")
    TOKEN = os.environ.get('DISCORD_TOKEN', None)
    if TOKEN:
        bot.run(TOKEN)
    else:
        logging.critical("Please create and configure a valid Discord token.")
        exit_status = 2
        sys.exit(exit_status)