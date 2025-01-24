#/usr/bin/python3
import os
import sys
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
                message.embeds # and 
                # message.embeds[0].title == "Peon"
                ):
                await message.delete()
            elif (message.content.startswith(settings['command_prefix'])): 
                await message.delete()
        return True
    except Exception as e:
        logging.error(f"Error cleaning channel {channel.name}: {e}")
        return False

# Startup message
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

# Command: User interaction
@bot.command(name='peon',aliases=cmd_aliases["peon"])
@commands.has_permissions(manage_messages=True)
async def peon(ctx):
    await clean_channel(ctx.channel, bot.user)
    gameuid=(str(ctx.channel.name)).split('-')[0],
    servername=(str(ctx.channel.name)).split('-')[1]
    view = UserActions(gameuid=gameuid,servername=(servername))
    embed = discord.Embed(
        description="*Ready to work...*",
        color=discord.Color.blue()
    )
    embed.set_image(url="https://raw.githubusercontent.com/the-peon-project/peon/refs/heads/main/media/PEON_L2R_medium.png")
    await ctx.channel.send(embed=embed, view=view)  

# Command: Clean channel
@bot.command(name='clear',aliases=cmd_aliases["clear"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    #args = identify_channel(channel_request=ctx.channel.name)
    # if args[0] == 'admin': await ctx.channel.purge(limit=amount + 1)
    # else: await ctx.send(embed=build_card_err(err_code="unauthorized",command="auth",permission=args[0]))

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