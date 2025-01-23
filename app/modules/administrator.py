import logging
import discord
from . import *
from .orchestrator import *

class AdministratorActions(discord.ui.View):
    def __init__(self):
        super().__init__()
        
    @discord.ui.button(label="Register Orchestrator", style=discord.ButtonStyle.primary)
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RegisterModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="De-Register Orchestrator", style=discord.ButtonStyle.primary)
    async def deregister_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View()
        view.add_item(DeregisterSelect())
        await interaction.response.send_message("Select an orchestrator to remove:", view=view)

# Orchestrator Registration Modal
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
        if (response := register_peon_orc(self.orchestrator_name.value, self.orchestrator_url.value, self.orchestrator_api_key.value))["status"] == "success":
            response_string = f"Orchestrator: {self.orchestrator_name.value}\nURL: {self.orchestrator_url.value} registered succesfully\n```bash\n"
            for key,value in response['info'].items():
                response_string += f"{key}: {value}\n"
            response_string += "```"
            embed = build_card(title="Registration Request", message=response_string)
        else:
            embed = build_card_err(err_code="bad.code", command="bad.code", permission="user", note=response['info'])
        await interaction.response.send_message(embed=embed)

class DeregisterConfirmView(discord.ui.View):
    def __init__(self, orchestrator_name: str):
        super().__init__()
        self.orchestrator_name = orchestrator_name

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO: Add actual deregister_peon_orc() function call here
        embed = build_card(
            title="Deregistration Request",
            message=f"Orchestrator '{self.orchestrator_name}' has been deregistered."
        )
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = build_card(
            title="Deregistration Request",
            message="Deregistration cancelled."
        )
        await interaction.response.send_message(embed=embed)

class DeregisterSelect(discord.ui.Select):
    def __init__(self):
        options = []
        if (orchestrators := get_peon_orcs())["status"] == "success":
            options = [
                discord.SelectOption(label=orc['name'], value=orc['name'])
                for orc in orchestrators['data']
            ]
        super().__init__(
            placeholder='Select an orchestrator to remove...',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        view = DeregisterConfirmView(self.values[0])
        await interaction.response.send_message(
            f"Are you sure you want to deregister orchestrator '{self.values[0]}'?",
            view=view
        )