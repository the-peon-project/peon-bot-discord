import logging
import discord
from . import *
from .shared import *
from .orchestrator import *

async def remove_interactions(interaction,keep="0",message_prefix=None):
        channel = interaction.channel
        logging.debug("Cleaning channel")
        async for message in channel.history(limit=50):
            if ((str(message.author)).split('#')[0] == interaction.client.user.name and message.embeds) and (message.id != keep):
                if message.embeds[0].image.url and message.embeds[0].image.url == bot_image:
                    await message.delete()
                elif message.embeds[0].thumbnail and message.embeds[0].thumbnail.url == bot_thumbnail:
                    await message.delete()
                elif message.embeds[0].color == discord.Color.yellow():
                    await message.delete()
                elif message_prefix:
                    if message.content.startswith(message_prefix):
                        await message.delete()

class UserActions(discord.ui.View):
    def __init__(self, gameuid, servername):
        self.gameuid = gameuid
        self.servername = servername
        self.message_body = ""
        super().__init__(timeout=None)
        
    def _disable_all_buttons(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

    async def _handle_server_action(self, interaction: discord.Interaction, action: str):
        self._disable_all_buttons()
        await interaction.response.edit_message(view=self)
        username = str(interaction.user)
        nickname = str(interaction.user.display_name)
        logging.info(f"Server {action.upper()} triggered by <@{username}> for {self.servername} ({self.gameuid})")
        response = server_actions(action=action, args=[self.gameuid, self.servername])
        if response['status'] == 'success':
            if action == 'get': message = response['data']
            else: message = f"Server **{action.upper()}** triggered by *@{nickname}*"
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
        self._disable_all_buttons()
        await interaction.response.edit_message(view=self)
        view = discord.ui.View()
        view.add_item(UpdateModeSelect(self.gameuid, self.servername))
        embed = discord.Embed(description="Select an update type:",color=discord.Color.yellow())
        embed.set_thumbnail(url=f"{bot_thumbnail}")  # Add size parameter
        await interaction.followup.send(embed=embed, view=view)

    @discord.ui.button(label="About", style=discord.ButtonStyle.secondary, row=1)
    async def server_about(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._disable_all_buttons()
        await interaction.response.edit_message(content="*Getting about info...*", view=self)
        message = await interaction.channel.send(embed=build_about_card())
        await remove_interactions(interaction,keep=message.id)

class UpdateModeSelect(discord.ui.Select):
    def __init__(self, gameuid: str, servername: str):
        self.gameuid = gameuid
        self.servername = servername
        options = [
            discord.SelectOption(label="Game Server",value="server",description="Update the game server files <default>"),
            discord.SelectOption(label="Server Container",value="image",description="Update the PEON container in which the game server runs."),
            discord.SelectOption(label="Complete Upgrade",value="full",description="Update both the game server & the Peon container")
        ]
        super().__init__(placeholder='Select update mode...',min_values=1,max_values=1,options=options)
        self.disabled = False  # Add initial disabled state

    def _disable_select(self):
        self.disabled = True
        self.view.stop()  # Stop the view to prevent further interactions
        
    async def callback(self, interaction: discord.Interaction):
        self._disable_select()
        view = UpdateConfirmView(self.values[0], self.gameuid, self.servername)
        selected_option = next(opt for opt in self.options if opt.value == self.values[0])
        embed = discord.Embed(description=f"Are you sure you want to perform a *{selected_option.label}* update?",color=discord.Color.yellow())
        embed.set_thumbnail(url=f"{bot_thumbnail}")  # Add size parameter
        await interaction.response.edit_message(embed=embed, view=view)

class UpdateConfirmView(discord.ui.View):
    def __init__(self, mode: str, gameuid: str, servername: str):
        super().__init__()
        self.mode = mode
        self.gameuid = gameuid
        self.servername = servername
        
    def _disable_all_buttons(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._disable_all_buttons()
        await interaction.response.edit_message(view=self)
        username = str(interaction.user)
        nickname = str(interaction.user.display_name)
        logging.info(f"Server **UPDATE ({(self.mode).upper()})** {self.mode} triggered by <@{username}> for {self.servername} ({self.gameuid})")
        response = server_actions(action='update', args=[self.gameuid, self.servername, self.mode])
        if response['status'] == 'success': embed = build_card(status='ok',  message=f"Server **UPDATE ({(self.mode).upper()})** triggered by *@{nickname}*")
        else: embed = build_card(status='nok', message="Server **UPDATE ({(self.mode).upper()})** triggered by *@{nickname}* FAILED")
        await interaction.channel.send(embed=embed)
        await remove_interactions(interaction)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await remove_interactions(interaction)