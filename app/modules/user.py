import logging
import discord
from . import *
from .orchestrator import *
        
class UserActions(discord.ui.View):
    def __init__(self, gameuid, servername):
        self.gameuid = gameuid
        self.servername = servername
        super().__init__(timeout=None) # This may cause a memory leak???
        
    async def _handle_server_action(self, interaction: discord.Interaction, action: str):
        username = str(interaction.user)
        nickname = str(interaction.user.display_name)
        logging.info(f"Server {action.upper()} requested by {username} - {self.gameuid} - {self.servername}")
        embed = build_card(status='ok',message=f"**{action.capitalize()}** server requested by *@{nickname}*")
        await interaction.response.defer()
        await interaction.channel.send(embed=embed)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.primary)
    async def server_start(self, interaction: discord.Interaction, button: discord.ui.Button):  
        await self._handle_server_action(interaction, "start")

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def server_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_server_action(interaction, "stop")