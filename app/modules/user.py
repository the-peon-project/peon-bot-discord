import logging
import discord
from . import *
from .orchestrator import *
        
class UserActions(discord.ui.View):
    def __init__(self, gameuid, servername):
        self.gameuid = gameuid
        self.servername = servername
        self.message_body = ""
        super().__init__(timeout=None) # This may cause a memory leak???
        
    async def _handle_server_action(self, interaction: discord.Interaction, action: str):
        username = str(interaction.user)
        nickname = str(interaction.user.display_name)
        logging.info(f"Server {action.upper()} requested by <@{username}> for {self.servername} ({self.gameuid})")
        if action not in ['info']:
            embed = build_card(status='ok',message=f"**{action.capitalize()}** server requested by *@{nickname}*")
        elif action == 'info': 
            embed = build_card(status='ok',message=f"{self.message_body}")
        await interaction.channel.send(embed=embed)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.success, row=0)
    async def server_start(self, interaction: discord.Interaction, button: discord.ui.Button):
        action='start'
        await interaction.response.send_message(f"*Processing {action} request...*", ephemeral=True)
        if (response := server_actions(action=action,args=[self.gameuid,self.servername]))['status'] == 'success':
            await self._handle_server_action(interaction, action)
        else: await interaction.channel.send(embed=build_card(status='nok',message=f"{response['err_code']}"))
        
    @discord.ui.button(label="Restart", style=discord.ButtonStyle.secondary, row=0)
    async def server_restart(self, interaction: discord.Interaction, button: discord.ui.Button):
        action='restart'
        await interaction.response.send_message(f"*Processing {action} request...*", ephemeral=True)
        if (response := server_actions(action=action,args=[self.gameuid,self.servername]))['status'] == 'success':
            await self._handle_server_action(interaction, action)
        else: await interaction.channel.send(embed=build_card(status='nok',message=f"{response['err_code']}"))

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, row=0)
    async def server_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        action='stop'
        await interaction.response.send_message(f"*Processing {action} request...*", ephemeral=True)
        if (response := server_actions(action=action,args=[self.gameuid,self.servername]))['status'] == 'success':
            await self._handle_server_action(interaction, action)
        else: await interaction.channel.send(embed=build_card(status='nok',message=f"{response['err_code']}"))
    
    @discord.ui.button(label="Info", style=discord.ButtonStyle.secondary, row=1)
    async def server_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        action='info'
        await interaction.response.send_message(f"*Processing {action} request...*", ephemeral=True)
        if (response := server_actions(action='get',args=[self.gameuid,self.servername]))['status'] == 'success':
            self.message_body = response['data']
            await self._handle_server_action(interaction, "info")
        else: await interaction.channel.send(embed=build_card(status='nok',message="Could not retrieve server information"))
    
    @discord.ui.button(label="Update", style=discord.ButtonStyle.secondary, row=1)
    async def server_update(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_server_action(interaction, "update")
    
    @discord.ui.button(label="About", style=discord.ButtonStyle.secondary, row=1)
    async def server_about(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_server_action(interaction, "about")