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
from modules.shared import *

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=settings['command_prefix'],intents=intents)

async def clean_channel(channel, bot_user, limit=10):
    try:
        async for message in channel.history(limit=limit):
            if (message.author == bot_user and message.embeds):
                if message.embeds[0].image.url == bot_image:
                    await message.delete()
            elif (message.content.startswith(settings['command_prefix']) and message.author != bot_user): 
                await message.delete()
        return True
    except Exception as e:
        logging.error(f"Error cleaning channel {channel.name}: {e}")
        return False

# Startup message
@bot.event
async def on_ready():
    logging.info(f'Connected as bot named @{bot.user.name}. Running PEON init tasks...')
    for channel in bot.get_all_channels():
        if isinstance(channel, discord.TextChannel):
            permissions = channel.permissions_for(channel.guild.me)
            if permissions.send_messages:
                await clean_channel(channel, bot.user, limit=100)
        if settings['control_channel'] == str(channel.name): control_channel = channel
    logging.info(f"Informing bot readiness to admin channel <{settings['control_channel']}>")
    await control_channel.send(" has connected to the server.")

# Command: User interaction
@bot.command(name='peon',aliases=cmd_aliases["peon"])
@commands.has_permissions(manage_messages=True)
async def peon(ctx):
    await clean_channel(ctx.channel, bot.user,limit=20)
    logging.debug(f"PEON Bot called for <{str(ctx.channel.name)}>")
    try:
        gameuid=(str(ctx.channel.name)).split('-')[0]
        servername=(str(ctx.channel.name)).split('-')[1]
    except:
        gameuid = None
        servername = None
    if gameuid and servername:     
        view = UserActions(gameuid=gameuid,servername=servername)
        embed = discord.Embed(description=f"*{get_quote()}*",color=discord.Color.blue())
        embed.set_image(url=bot_image)
        await ctx.channel.send(embed=embed, view=view)
    else:
        await ctx.send(embed=build_card(status='nok',message="This doesn't look like a warcamp, warchief!"))

# Command: Clean channel
@bot.command(name='clear',aliases=cmd_aliases["clear"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    #args = identify_channel(channel_request=ctx.channel.name)
    # if args[0] == 'admin': await ctx.channel.purge(limit=amount + 1)
    # else: await ctx.send(embed=build_card_err(err_code="unauthorized",command="auth",permission=args[0]))

@bot.command(name='about')
async def get_about(ctx):
    logging.debug("'About' requested")
    await ctx.send(embed=build_about_card())

# MAIN
if __name__ == "__main__":
    # Configure logging
    print("\n------------------------------\nStarting Discord Bot...\n------------------------------\n")
    configure_logging()
    TOKEN = os.environ.get('DISCORD_TOKEN', None)
    if TOKEN:
        bot.run(TOKEN)
    else:
        logging.critical("Please create and configure a valid Discord token.")
        exit_status = 2
        sys.exit(exit_status)