import logging
import discord
from . import *
from .orchestrator import *
        
class UserActions(discord.ui.View):
    def __init__(self, gameuid, servername):
        self.gameuid = gameuid
        self.servername = servername
        super().__init__()
        
    @discord.ui.button(label="Start", style=discord.ButtonStyle.primary)
    async def server_start(self, interaction: discord.Interaction, button: discord.ui.Button):  
        username = str(interaction.user)
        logging.info(f"Server START requested by {username} - {self.gameuid} - {self.servername}")
        embed = build_card(
            title="Start Server",
            message=f"Start requested by {username}"
        )
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def server_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        username = str(interaction.user)
        logging.info(f"Server STOP requested by {username} - {self.gameuid} - {self.servername}")
        embed = build_card(
            title="Stop Server",
            message=f"Stop requested by {username}"
        )
        await interaction.response.send_message(embed=embed)