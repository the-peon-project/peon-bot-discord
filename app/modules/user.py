import logging
import discord
from . import *
from .shared import *
from .orchestrator import *

async def remove_interactions(interaction,keep="0"):
        channel = interaction.channel
        logging.debug("Cleaning channel")
        async for message in channel.history(limit=50):
            if ((str(message.author)).split('#')[0] == interaction.client.user.name and message.embeds) and (message.id != keep):
                if message.embeds[0].image.url == bot_image:
                    await message.delete()

class UserActions(discord.ui.View):
    def __init__(self, gameuid, servername):
        self.gameuid = gameuid
        self.servername = servername
        self.message_body = ""
        super().__init__(timeout=None)
        
    async def _handle_server_action(self, interaction: discord.Interaction, action: str):
        # Send initial response
        # await interaction.response.send_message(f"*Processing {action} request...*", ephemeral=True)
        await interaction.response.defer()
        username = str(interaction.user)
        nickname = str(interaction.user.display_name)
        logging.info(f"Server {action.upper()} requested by <@{username}> for {self.servername} ({self.gameuid})")
        # Handle API call
        response = server_actions(action=action, args=[self.gameuid, self.servername])
        if response['status'] == 'success':
            if action == 'get': message = response['data']
            else: message = f"**{action.capitalize()}** server requested by *@{nickname}*"
            embed = build_card(status='ok', message=message)
        else: embed = build_card(status='nok', message=response.get('err_code', "Could not process server request"))
        await interaction.channel.send(embed=embed)
        await remove_interactions(interaction)


    @discord.ui.button(label="Start", style=discord.ButtonStyle.success, row=0)
    async def server_start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_server_action(interaction, 'start')
        
    @discord.ui.button(label="Restart", style=discord.ButtonStyle.secondary, row=0)
    async def server_restart(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_server_action(interaction, 'restart')

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, row=0)
    async def server_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_server_action(interaction, 'stop')
    
    @discord.ui.button(label="Info", style=discord.ButtonStyle.secondary, row=1)
    async def server_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_server_action(interaction, 'get')
    
    @discord.ui.button(label="Update", style=discord.ButtonStyle.secondary, row=1)
    async def server_update(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_server_action(interaction, 'update')

    @discord.ui.button(label="About", style=discord.ButtonStyle.secondary, row=1)
    async def server_about(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        message = await interaction.channel.send(embed=build_about_card())
        await remove_interactions(interaction,keep=message.id)