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

async def clean_channel(channel, bot_user, limit=50):
    """Clean bot messages from channel"""
    try:
        async for message in channel.history(limit=limit):
            if (message.author == bot_user and 
                message.embeds and 
                message.embeds[0].title == "Peon"):
                await message.delete()
        return True
    except Exception as e:
        logging.error(f"Error cleaning channel {channel.name}: {e}")
        return False

@bot.event
async def on_ready():
    logging.info(f'[{bot.user.name}] has connected to Discord!')
    bot_channels = []
    for channel in bot.get_all_channels():
        if (isinstance(channel, discord.TextChannel) and channel.permissions_for(channel.guild.me).send_messages):
            bot_channels.append(channel)
    for channel in bot_channels:
        await clean_channel(channel, bot.user)
        if settings['control_channel'] == str(channel.name):
            await channel.send(" has connected to the server.")
        else:
            if str(channel.name) == 'valheim-ocs':
                # Send new UserActions
                view = UserActions(
                    gameuid=(str(channel.name)).split('-')[0],
                    servername=(str(channel.name)).split('-')[1]
                )
                embed = discord.Embed(
                    title="Peon",
                    description="*Ready to work...*",
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