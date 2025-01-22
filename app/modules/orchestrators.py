import logging
import discord
import json
import os

# Load orchestrators from disk
def get_peon_orcs():
    try:
        config_file = "/app/config/peon.orchestrators.json"
        logging.debug("Loading orchestrators file")
        with open(config_file, 'r') as file:
            orchestrators = json.load(file)
        API_KEY = os.environ.get('LOCAL_API_KEY',None)
        if API_KEY:
            for entry in orchestrators:
                if entry["url"] == "http://peon.orc:5000":
                    if entry["key"] != API_KEY:
                        logging.debug("Updating orchestrator API key")
                        entry["key"] = f"'{API_KEY}'"
                        with open(config_file, 'w') as file:
                            json.dump(orchestrators, file, indent=4)
                        entry["key"] = API_KEY
                break
        return {"status": "success", "data": orchestrators}
    except FileNotFoundError:
        logging.debug("No orchestrators file found. Creating one.")
        default_data = []
        with open(config_file, 'w') as file:
            json.dump(default_data, file, indent=4)
        return {"status": "error", "info": "Orchestrators file not found. Created a new one."}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"status": "error", "info": str(e)}

def register_peon_orc(orc_name, orc_url, orc_key):
    try:
        orchestrators = get_peon_orcs()
        if orchestrators["status"] == "error":
            return orchestrators
        orchestrators = orchestrators["data"]
        for entry in orchestrators:
            if entry["name"] == orc_name:
                return {"status": "error", "info": "Orchestrator already registered."}
        orchestrators.append({"name": orc_name, "url": orc_url, "key": orc_key})
        config_file = "/app/config/peon.orchestrators.json"
        with open(config_file, 'w') as file:
            json.dump(orchestrators, file, indent=4)
        return {"status": "success", "info": "Orchestrator registered."}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"status": "error", "info": str(e)}

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
        embed = discord.Embed(
            title="Registration Request",
            description=f"Orchestrator: {self.orchestrator_name.value}\nURL: {self.orchestrator_url.value}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

class RegisterButton(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Register Orchestrator", style=discord.ButtonStyle.primary)
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RegisterModal()
        await interaction.response.send_modal(modal)