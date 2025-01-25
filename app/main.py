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

async def clean_channel(channel, bot_user, limit=10):
    """Clean bot messages from channel"""
    try:
        async for message in channel.history(limit=limit):
            if (message.author == bot_user and message.embeds):
                await message.delete()
            elif (message.content.startswith(f"!{settings['command_prefix']}")): 
                await message.delete()
        return True
    except Exception as e:
        logging.error(f"Error cleaning channel {channel.name}: {e}")
        return False

# Startup message
@bot.event
async def on_ready():
    logging.info(f'[{bot.user.name}] has connected to Discord!')
    for channel in bot.get_all_channels():
        if isinstance(channel, discord.TextChannel):
            permissions = channel.permissions_for(channel.guild.me)
            if permissions.send_messages:
                await clean_channel(channel, bot.user, limit=100)
        if settings['control_channel'] == str(channel.name):
            await channel.send(" has connected to the server.")

# Command: User interaction
@bot.command(name='peon',aliases=cmd_aliases["peon"])
@commands.has_permissions(manage_messages=True)
async def peon(ctx):
    await clean_channel(ctx.channel, bot.user,limit=20)
    try:
        gameuid=(str(ctx.channel.name)).split('-')[0],
        servername=(str(ctx.channel.name)).split('-')[1]
    except:
        gameuid = None
        servername = None
    if gameuid and servername:     
        view = UserActions(gameuid=gameuid,servername=(servername))
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
async def get_plans(ctx):
    logging.debug("'About' requested")
    with open(f"/app/reference/{settings['language']}/about.md", "r") as file:
        response = file.read()
    response = response.replace('[BOT_VERSION]',os.environ.get('VERSION', '-.-.-'))
    if (orchestrators := get_peon_orcs())['status'] == "success":
        if orchestrators['data']:
            orcstring = ""
            for orc in orchestrators['data']:
                if (orc_response := get_orchestrator_details(url=orc['url'],api_key=orc['key']))['status'] == "success":
                    info = orc_response['data']
                    orcstring += f"- Orchestrator: {orc['name']} [{info['version']}](<https://docs.warcamp.org/development/50_bot_discord/#release-notes>)\n"
                else:
                    orcstring += f"- Orchestrator: {orc['name']} [UNKNOWN](<https://docs.warcamp.org/development/50_bot_discord/#release-notes>)\n"
            response = response.replace('[ORCHESTRATORS]',f"{orcstring}")
    try:
        file_contents = requests.get(games_url).text
        servers = "### Supported Games\nBelow is a list of games that are currently supported by the PEON Project.\n"
        for line in file_contents.splitlines():
            if re.search('- \[x\]', line):
                line = re.sub('- \[x\]', '- ', line)
                line = re.sub('./guides/games/', 'https://docs.warcamp.org/guides/games/', line)
                line = re.sub('.md', '', line)
                servers += line + '\n'
    except:
        servers = ""
    response = response.replace('[GAME_SERVERS]',servers)
    embed = discord.Embed(description=response)
    embed.set_image(url=bot_image) 
    await ctx.send(embed=embed)

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