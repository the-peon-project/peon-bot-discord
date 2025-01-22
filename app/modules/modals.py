import logging
import discord
from . import *
from .orchestrator import *

class RegisterModal(discord.ui.Modal, title='Register Orchestrator'):
    orchestrator_name = discord.ui.TextInput(
        label='Orchestrator Name',
        placeholder='Enter an orchestrator name...',
        required=True,
        min_length=3,
        max_length=50
    )
    orchestrator_url = discord.ui.TextInput(
        label='URL',
        placeholder='Enter the server URL. e.g. http://myserver.place:5000',
        required=True,
        min_length=5,
        max_length=100
    )
    orchestrator_api_key = discord.ui.TextInput(
        label='API-KEY',
        placeholder="Enter the orchestrator's API key.",
        required=True,
        min_length=1,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        logging.info(f"Orchestrator registration: {self.orchestrator_name.value} at {self.orchestrator_url.value}")
        if register_peon_orc(self.orchestrator_name.value, self.orchestrator_url.value, self.orchestrator_api_key.value)["status"] == "success":
            embed = build_card(title="Registration Request", message=f"Orchestrator: {self.orchestrator_name.value}\nURL: {self.orchestrator_url.value} registered succesfully")
        else:
            embed = build_card_err(err_code="bad.code", command="bad.code", permission="user")
        await interaction.response.send_message(embed=embed)

class RegisterButton(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Register Orchestrator", style=discord.ButtonStyle.primary)
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RegisterModal()
        await interaction.response.send_modal(modal)
        
