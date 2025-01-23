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
        logging.info(f"Server START requested - {self.gameuid} - {self.servername}")
        embed = build_card(
            title="Start Server",
            message=f"Start requested"
        )
        await interaction.response.send_message(embed=embed)
        # if "success" in (response := server_actions('start', args))['status']: embed = build_card(title="Start Server",message=response['data'])
        # else: embed = build_card_err(err_code=response['err_code'],command=response['command'],permission=args[0]) 
        #await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def server_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        logging.info(f"Server STOP requested - {self.gameuid} - {self.servername}")
        embed = build_card(
            title="Stop Server",
            message=f"Stop requested"
        )
        await interaction.response.send_message(embed=embed)