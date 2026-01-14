import logging
import discord
from typing import List, Optional
from . import *
from .orchestrator import *
from .shared import *

class PersistentAdministratorView(discord.ui.View):
    """Persistent view that survives bot restarts"""
    def __init__(self):
        super().__init__(timeout=None)

class EnhancedAdministratorView(discord.ui.View):
    """Enhanced administrator interface with better UX"""
    def __init__(self):
        super().__init__(timeout=300)  # 5 minute timeout
        
    @discord.ui.button(label="🏢 Register Orchestrator", style=discord.ButtonStyle.success, row=0)
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = EnhancedRegisterModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🗑️ Remove Orchestrator", style=discord.ButtonStyle.danger, row=0)
    async def deregister_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View(timeout=60)
        view.add_item(EnhancedDeregisterSelect())
        embed = discord.Embed(
            title="🗑️ Remove Orchestrator",
            description="Select an orchestrator to remove from the registry:",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🏗️ Create Server", style=discord.ButtonStyle.primary, row=0)
    async def create_server_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = EnhancedCreateServerView()
        embed = discord.Embed(
            title="🏗️ Create New Server",
            description="Select a game plan to create a new server:",
            color=discord.Color.green()
        )
        embed.add_field(
            name="💡 Tip",
            value="You can also use `/create <game_type> <server_name>` for quick creation!",
            inline=False
        )
        await interaction.response.send_message(embed=embed, view=view)

    @discord.ui.button(label="📋 Server Overview", style=discord.ButtonStyle.secondary, row=1)
    async def list_servers_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        if 'error' in (result := get_peon_orcs())['status']:
            embed = build_card(status='nok', title="❌ No Orchestrators", message="No orchestrators are currently registered.")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🖥️ Server Overview",
            description="Current status of all managed servers:",
            color=discord.Color.blue()
        )
        
        total_servers = 0
        running_servers = 0
        
        for orchestrator in result['data']:
            try:
                servers = get_servers(orchestrator['url'], orchestrator['key'])
                orc_status = get_orchestrator_details(orchestrator['url'], orchestrator['key'])
                
                if orc_status['status'] == 'success':
                    status_emoji = "🟢"
                    orc_title = f"{status_emoji} **{orchestrator['name']}**"
                else:
                    status_emoji = "🔴"
                    orc_title = f"{status_emoji} **{orchestrator['name']}** (Offline)"
                
                server_list = ""
                for server in servers[:5]:  # Limit to 5 per orchestrator
                    server_status = server.get('server_state', '').lower()
                    server_emoji = "🟢" if server_status == 'running' else "🔴" if server_status == 'exited' else "🟡"
                    game_type = server.get('game_uid', 'unknown')
                    name = server.get('servername', 'unknown')
                    server_list += f"{server_emoji} `{game_type}.{name}` [{server_status}]\n"
                    total_servers += 1
                    if server_status == 'running':
                        running_servers += 1
                
                if len(servers) > 5:
                    server_list += f"... and {len(servers) - 5} more servers"
                
                if not server_list:
                    server_list = "— No servers found"
                
                embed.add_field(
                    name=orc_title,
                    value=server_list,
                    inline=False
                )
                
            except Exception as e:
                embed.add_field(
                    name=f"🔴 **{orchestrator['name']}** (Error)",
                    value=f"❌ Connection failed: {str(e)[:100]}...",
                    inline=False
                )
        
        embed.add_field(
            name="📊 Summary",
            value=f"**{running_servers}/{total_servers}** servers running",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)

    @discord.ui.button(label="📦 Import Servers", style=discord.ButtonStyle.secondary, row=1)
    async def import_servers_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        if 'error' in (result := get_peon_orcs())['status']:
            embed = build_card(status='nok', message="No orchestrators registered")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📦 Server Import Results",
            description="Importing servers from orchestrators...",
            color=discord.Color.blue()
        )
        
        success_count = 0
        total_count = len(result['data'])
        
        for orchestrator in result['data']:
            try:
                import_result = import_servers(orchestrator['url'], orchestrator['key'])
                if import_result['status'] == 'success':
                    success_count += 1
                    embed.add_field(
                        name=f"✅ {orchestrator['name']}",
                        value="Import completed successfully",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name=f"❌ {orchestrator['name']}",
                        value=f"Error: {import_result.get('message', 'Unknown error')[:100]}",
                        inline=True
                    )
            except Exception as e:
                embed.add_field(
                    name=f"❌ {orchestrator['name']}",
                    value=f"Connection error: {str(e)[:100]}",
                    inline=True
                )
        
        embed.color = discord.Color.green() if success_count == total_count else discord.Color.orange()
        embed.add_field(
            name="📊 Summary",
            value=f"**{success_count}/{total_count}** orchestrators imported successfully",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)

    @discord.ui.button(label="📚 Browse Plans", style=discord.ButtonStyle.secondary, row=1)
    async def browse_plans_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = EnhancedPlansView()
        embed = discord.Embed(
            title="📚 Game Plan Browser",
            description="Explore available game server plans:",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="💡 Quick Commands",
            value="• `/list plans` - Show all available plans\n• `/create <game_type> <name>` - Quick server creation",
            inline=False
        )
        await interaction.response.send_message(embed=embed, view=view)

    @discord.ui.button(label="🔄 Update Plans", style=discord.ButtonStyle.secondary, row=2)
    async def update_plans_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        if 'error' in (result := get_peon_orcs())['status']:
            embed = build_card(status='nok', message="No orchestrators registered")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔄 Plans Update Results",
            description="Updating game plans from remote repository...",
            color=discord.Color.blue()
        )
        
        success_count = 0
        total_new_plans = 0
        
        for orchestrator in result['data']:
            try:
                update_result = update_plans(orchestrator['url'], orchestrator['key'])
                if update_result['status'] == 'success':
                    success_count += 1
                    new_recipes = update_result['data'].get('new_recipies', {})
                    new_count = len(new_recipes)
                    total_new_plans += new_count
                    
                    if new_count > 0:
                        new_games = ", ".join(list(new_recipes.keys())[:3])
                        if len(new_recipes) > 3:
                            new_games += f" and {len(new_recipes) - 3} more"
                        embed.add_field(
                            name=f"✨ {orchestrator['name']}",
                            value=f"{new_count} new plans: {new_games}",
                            inline=True
                        )
                    else:
                        embed.add_field(
                            name=f"✅ {orchestrator['name']}",
                            value="Plans are up to date",
                            inline=True
                        )
                else:
                    embed.add_field(
                        name=f"❌ {orchestrator['name']}",
                        value=f"Update failed: {update_result.get('message', 'Unknown')[:50]}",
                        inline=True
                    )
            except Exception as e:
                embed.add_field(
                    name=f"❌ {orchestrator['name']}",
                    value=f"Error: {str(e)[:50]}",
                    inline=True
                )
        
        embed.color = discord.Color.green() if success_count > 0 else discord.Color.red()
        embed.add_field(
            name="📊 Summary",
            value=f"**{total_new_plans}** new plans added across **{success_count}** orchestrators",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)

    @discord.ui.button(label="ℹ️ System Info", style=discord.ButtonStyle.secondary, row=2)
    async def system_info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="📊 System Information",
            description="Current bot and orchestrator status:",
            color=discord.Color.blue()
        )
        
        # Bot info
        embed.add_field(
            name="🤖 Bot Status",
            value=f"**Online** • Latency: {round(interaction.client.latency * 1000)}ms",
            inline=True
        )
        
        # Orchestrator count and status
        if 'error' in (result := get_peon_orcs())['status']:
            embed.add_field(
                name="🏢 Orchestrators",
                value="None registered",
                inline=True
            )
        else:
            online_count = 0
            for orc in result['data']:
                orc_status = get_orchestrator_details(orc['url'], orc['key'])
                if orc_status['status'] == 'success':
                    online_count += 1
            
            embed.add_field(
                name="🏢 Orchestrators",
                value=f"{online_count}/{len(result['data'])} online",
                inline=True
            )
        
        embed.add_field(
            name="🛠️ Available Commands",
            value="Use `/help` to see all available slash commands",
            inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

# Enhanced Modal for orchestrator registration
class EnhancedRegisterModal(discord.ui.Modal, title='🏢 Register New Orchestrator'):
    orchestrator_name = discord.ui.TextInput(
        label='Orchestrator Name',
        placeholder='e.g., "Main Server", "Production Orc"...',
        required=True,
        min_length=3,
        max_length=50
    )
    orchestrator_url = discord.ui.TextInput(
        label='Orchestrator URL',
        placeholder='http://your-server.com:5000 or http://192.168.1.100:5000',
        required=True,
        min_length=10,
        max_length=100
    )
    orchestrator_api_key = discord.ui.TextInput(
        label='API Key',
        placeholder="Enter the orchestrator's API key",
        required=True,
        min_length=1,
        max_length=100,
        style=discord.TextStyle.short
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        logging.info(f"Orchestrator registration attempt: {self.orchestrator_name.value} at {self.orchestrator_url.value}")
        
        # Test connection first
        test_result = get_orchestrator_details(self.orchestrator_url.value, self.orchestrator_api_key.value)
        
        if test_result['status'] != 'success':
            embed = discord.Embed(
                title="❌ Registration Failed",
                description=f"Could not connect to orchestrator at `{self.orchestrator_url.value}`",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Error Details",
                value=test_result.get('message', 'Connection failed'),
                inline=False
            )
            embed.add_field(
                name="💡 Troubleshooting",
                value="• Check URL format (include http://)\n• Verify the orchestrator is running\n• Confirm the API key is correct\n• Ensure network connectivity",
                inline=False
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Register orchestrator
        response = register_peon_orc(
            self.orchestrator_name.value, 
            self.orchestrator_url.value, 
            self.orchestrator_api_key.value
        )
        
        if response["status"] == "success":
            embed = discord.Embed(
                title="✅ Registration Successful!",
                description=f"Orchestrator **{self.orchestrator_name.value}** has been registered!",
                color=discord.Color.green()
            )
            embed.add_field(
                name="🏢 Orchestrator Details",
                value=f"**Name:** {self.orchestrator_name.value}\n**URL:** {self.orchestrator_url.value}",
                inline=False
            )
            
            # Add orchestrator info if available
            if 'version' in response['info']:
                embed.add_field(
                    name="📊 Version Info",
                    value=f"Orchestrator version: {response['info']['version']}",
                    inline=False
                )
        else:
            embed = discord.Embed(
                title="❌ Registration Failed",
                description=response.get('info', 'Unknown error occurred'),
                color=discord.Color.red()
            )
        
        # Try to replace the original modal message with the result
        try:
            await interaction.edit_original_response(embed=embed, view=None)
        except:
            await interaction.followup.send(embed=embed, ephemeral=True)

class EnhancedDeregisterSelect(discord.ui.Select):
    def __init__(self):
        options = []
        try:
            if (orchestrators := get_peon_orcs())["status"] == "success":
                for orc in orchestrators['data']:
                    # Test connection status
                    status = get_orchestrator_details(orc['url'], orc['key'])
                    status_emoji = "🟢" if status['status'] == 'success' else "🔴"
                    
                    options.append(discord.SelectOption(
                        label=f"{status_emoji} {orc['name']}",
                        value=orc['name'],
                        description=f"URL: {orc['url'][:50]}{'...' if len(orc['url']) > 50 else ''}"
                    ))
        except Exception as e:
            logging.error(f"Error loading orchestrators for deregistration: {e}")
        
        if not options:
            options = [discord.SelectOption(label="No orchestrators found", value="none", description="Register an orchestrator first")]
        
        super().__init__(
            placeholder='Select an orchestrator to remove...',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            embed = build_card(status='nok', message="No orchestrators available to remove")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        view = EnhancedDeregisterConfirmView(self.values[0])
        embed = discord.Embed(
            title="⚠️ Confirm Removal",
            description=f"Are you sure you want to remove orchestrator **{self.values[0]}**?",
            color=discord.Color.red()
        )
        embed.add_field(
            name="⚠️ Warning",
            value="This action cannot be undone. You'll need to re-register if you want to use this orchestrator again.",
            inline=False
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class EnhancedDeregisterConfirmView(discord.ui.View):
    def __init__(self, orchestrator_name: str):
        super().__init__(timeout=30)
        self.orchestrator_name = orchestrator_name

    @discord.ui.button(label="❌ Remove Orchestrator", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        response = deregister_peon_orc(self.orchestrator_name)
        
        if response["status"] == "success":
            embed = discord.Embed(
                title="✅ Orchestrator Removed",
                description=f"**{self.orchestrator_name}** has been successfully removed from the registry.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ Removal Failed",
                description=f"Failed to remove orchestrator: {response.get('info', 'Unknown error')}",
                color=discord.Color.red()
            )
        
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Removal Cancelled",
            description="Orchestrator removal has been cancelled.",
            color=discord.Color.grey()
        )
        await interaction.response.edit_message(embed=embed, view=None)

class EnhancedCreateServerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(EnhancedGamePlanSelect())

class EnhancedGamePlanSelect(discord.ui.Select):
    def __init__(self):
        options = []
        try:
            if (orchestrators := get_peon_orcs())["status"] == "success" and orchestrators["data"]:
                orc = orchestrators["data"][0]
                plans_result = get_all_plans(orc['url'], orc['key'])
                if plans_result["status"] == "success":
                    plans = plans_result["data"][:25]  # Discord limit
                    for plan in plans:
                        game_uid = plan.get('game_uid', '')
                        title = plan.get('title', game_uid)
                        if game_uid:
                            # Add emoji based on game type
                            emoji = self._get_game_emoji(game_uid)
                            options.append(discord.SelectOption(
                                label=f"{emoji} {title}",
                                value=game_uid,
                                description=f"Create a {game_uid} server"
                            ))
        except Exception as e:
            logging.error(f"Error loading plans: {e}")
        
        if not options:
            options = [discord.SelectOption(
                label="No plans available",
                value="none",
                description="Check orchestrator connection"
            )]
        
        super().__init__(
            placeholder='Select a game plan to create a server...',
            min_values=1,
            max_values=1,
            options=options
        )
    
    def _get_game_emoji(self, game_uid: str) -> str:
        """Get appropriate emoji for game type"""
        emoji_map = {
            'minecraft': '🧩',
            'valheim': '⚔️',
            'palworld': '🐾',
            'ark': '🦕',
            'rust': '🔥',
            'csgo': '🔫',
            'cs2': '🔫',
            'satisfactory': '🏗️',
            'enshrouded': '🌫️',
            'vrising': '🧛',
            'starbound': '🌌'
        }
        return emoji_map.get(game_uid.lower(), '🎮')

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            embed = build_card(status='nok', message="No plans available")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        modal = EnhancedServerCreateModal(self.values[0])
        await interaction.response.send_modal(modal)

class EnhancedServerCreateModal(discord.ui.Modal, title='🏗️ Create New Server'):
    def __init__(self, game_uid: str):
        super().__init__(title=f'🏗️ Create {game_uid.upper()} Server')
        self.game_uid = game_uid
        
        self.server_name = discord.ui.TextInput(
            label='Server Name',
            placeholder='Enter a unique server name (no spaces or special chars)...',
            required=True,
            min_length=3,
            max_length=50
        )
        self.server_description = discord.ui.TextInput(
            label='Description (Optional)',
            placeholder='Brief description of this server...',
            required=False,
            max_length=200,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.server_name)
        self.add_item(self.server_description)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if 'error' in (result := get_peon_orcs())['status']:
            embed = build_card(status='nok', message="No orchestrators registered")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        orchestrator = result['data'][0]
        user_settings = {}
        if self.server_description.value:
            user_settings['description'] = self.server_description.value
        
        create_result = server_create(
            orchestrator['url'],
            orchestrator['key'],
            self.game_uid,
            self.server_name.value,
            user_settings
        )
        
        if create_result['status'] == 'success':
            embed = discord.Embed(
                title="✅ Server Created Successfully!",
                description=f"Your new **{self.game_uid}** server is ready!",
                color=discord.Color.green()
            )
            embed.add_field(name="🎮 Game Type", value=self.game_uid.upper(), inline=True)
            embed.add_field(name="📝 Server Name", value=self.server_name.value, inline=True)
            
            if self.server_description.value:
                embed.add_field(name="📄 Description", value=self.server_description.value, inline=False)
            
            embed.add_field(
                name="🚀 Next Steps",
                value=f"Use `/server start {self.game_uid}.{self.server_name.value}` to start the server!",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Server Creation Failed",
                description="There was an issue creating your server.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Error Details",
                value=create_result.get('message', 'Unknown error'),
                inline=False
            )
        
        # Try to replace the original modal message with the result
        try:
            await interaction.edit_original_response(embed=embed, view=None)
        except:
            await interaction.followup.send(embed=embed)

class EnhancedPlansView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(EnhancedPlansSelect())

class EnhancedPlansSelect(discord.ui.Select):
    def __init__(self):
        options = []
        try:
            if (orchestrators := get_peon_orcs())["status"] == "success" and orchestrators["data"]:
                orc = orchestrators["data"][0]
                plans_result = get_all_plans(orc['url'], orc['key'])
                if plans_result["status"] == "success":
                    plans = plans_result["data"][:25]  # Discord limit
                    for plan in plans:
                        game_uid = plan.get('game_uid', '')
                        title = plan.get('title', game_uid)
                        if game_uid:
                            # Add emoji based on game type
                            emoji = self._get_game_emoji(game_uid)
                            options.append(discord.SelectOption(
                                label=f"{emoji} {title}",
                                value=game_uid,
                                description=f"View details for {game_uid} servers"
                            ))
        except Exception as e:
            logging.error(f"Error loading plans: {e}")
        
        if not options:
            options = [discord.SelectOption(
                label="No plans available",
                value="none",
                description="Check orchestrator connection"
            )]
        
        super().__init__(
            placeholder='Select a plan to view configuration details...',
            min_values=1,
            max_values=1,
            options=options
        )
    
    def _get_game_emoji(self, game_uid: str) -> str:
        """Get appropriate emoji for game type"""
        emoji_map = {
            'minecraft': '🧩',
            'valheim': '⚔️',
            'palworld': '🐾',
            'ark': '🦕',
            'rust': '🔥',
            'csgo': '🔫',
            'cs2': '🔫',
            'satisfactory': '🏗️',
            'enshrouded': '🌫️',
            'vrising': '🧛',
            'starbound': '🌌'
        }
        return emoji_map.get(game_uid.lower(), '🎮')

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            embed = build_card(status='nok', message="No plans available")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        await interaction.response.defer()
        
        if 'error' in (result := get_peon_orcs())['status']:
            embed = build_card(status='nok', message="No orchestrators registered")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
            
        orchestrator = result['data'][0]
        plan_result = get_warplan([orchestrator], self.values[0])
        
        if plan_result['status'] == 'success':
            embed = discord.Embed(
                title=f"📄 {self.values[0].upper()} Plan Details",
                description="Configuration settings for this game server type:",
                color=discord.Color.blue()
            )
            
            # Parse the plan data to make it more readable
            plan_data = plan_result['data']
            
            # Extract the JSON part
            if "```json" in plan_data:
                json_part = plan_data.split("```json")[1].split("```")[0]
                embed.add_field(
                    name="⚙️ Configuration Options",
                    value=f"```json{json_part}```",
                    inline=False
                )
            else:
                embed.add_field(
                    name="⚙️ Configuration",
                    value=plan_data,
                    inline=False
                )
            
            embed.add_field(
                name="🚀 Quick Create",
                value=f"Use `/create {self.values[0]} <server_name>` to create this server type!",
                inline=False
            )
        else:
            embed = build_card(
                status='nok',
                title="Plan Details Error",
                message=f"Could not load plan details: {plan_result.get('err_code', 'Unknown error')}"
            )
        
        await interaction.followup.send(embed=embed)
    def __init__(self):
        super().__init__()
        
    @discord.ui.button(label="Register Orchestrator", style=discord.ButtonStyle.primary, row=0)
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RegisterModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="De-Register Orchestrator", style=discord.ButtonStyle.primary, row=0)
    async def deregister_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View()
        view.add_item(DeregisterSelect())
        await interaction.response.send_message("Select an orchestrator to remove:", view=view)

    @discord.ui.button(label="Create Server", style=discord.ButtonStyle.success, row=0)
    async def create_server_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = CreateServerView()
        embed = discord.Embed(description="Select a game plan to create a new server:", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, view=view)

    @discord.ui.button(label="List All Servers", style=discord.ButtonStyle.secondary, row=1)
    async def list_servers_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if 'error' in (result := get_peon_orcs())['status']:
            embed = build_card(status='nok', message="No orchestrators registered")
            await interaction.followup.send(embed=embed)
            return
        
        servers_text = "**All Servers:**\n```\n"
        for orchestrator in result['data']:
            try:
                servers = get_servers(orchestrator['url'], orchestrator['key'])
                servers_text += f"\n--- {orchestrator['name']} ---\n"
                for server in servers:
                    status_icon = "🟢" if server.get('server_state', '').lower() == 'running' else "🔴"
                    servers_text += f"{status_icon} {server.get('game_uid', 'unknown')}.{server.get('servername', 'unknown')} [{server.get('server_state', 'unknown')}]\n"
            except Exception as e:
                servers_text += f"\n--- {orchestrator['name']} (unavailable) ---\n"
        servers_text += "```"
        
        embed = build_card(status='ok', message=servers_text)
        await interaction.followup.send(embed=embed)

    @discord.ui.button(label="Import Servers", style=discord.ButtonStyle.secondary, row=1)
    async def import_servers_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if 'error' in (result := get_peon_orcs())['status']:
            embed = build_card(status='nok', message="No orchestrators registered")
            await interaction.followup.send(embed=embed)
            return
        
        import_results = []
        for orchestrator in result['data']:
            try:
                import_result = import_servers(orchestrator['url'], orchestrator['key'])
                if import_result['status'] == 'success':
                    import_results.append(f"✅ {orchestrator['name']}: Import successful")
                else:
                    import_results.append(f"❌ {orchestrator['name']}: {import_result.get('message', 'Import failed')}")
            except Exception as e:
                import_results.append(f"❌ {orchestrator['name']}: {str(e)}")
        
        results_text = "**Server Import Results:**\n" + "\n".join(import_results)
        embed = build_card(status='ok', message=results_text)
        await interaction.followup.send(embed=embed)

    @discord.ui.button(label="Browse Plans", style=discord.ButtonStyle.secondary, row=1)
    async def browse_plans_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = PlansView()
        embed = discord.Embed(description="Available Game Plans:", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, view=view)

    @discord.ui.button(label="Update Plans", style=discord.ButtonStyle.secondary, row=2)
    async def update_plans_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if 'error' in (result := get_peon_orcs())['status']:
            embed = build_card(status='nok', message="No orchestrators registered")
            await interaction.followup.send(embed=embed)
            return
        
        update_results = []
        for orchestrator in result['data']:
            try:
                update_result = update_plans(orchestrator['url'], orchestrator['key'])
                if update_result['status'] == 'success':
                    new_recipes = update_result['data'].get('new_recipies', {})
                    if new_recipes:
                        new_count = len(new_recipes)
                        update_results.append(f"✅ {orchestrator['name']}: {new_count} new plans added")
                    else:
                        update_results.append(f"✅ {orchestrator['name']}: Plans up to date")
                else:
                    update_results.append(f"❌ {orchestrator['name']}: {update_result.get('message', 'Update failed')}")
            except Exception as e:
                update_results.append(f"❌ {orchestrator['name']}: {str(e)}")
        
        results_text = "**Plans Update Results:**\n" + "\n".join(update_results)
        embed = build_card(status='ok', message=results_text)
        await interaction.followup.send(embed=embed)

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
            embed = build_card(status='nok', message="Could not get the orchestrator registered")
        await interaction.response.send_message(embed=embed)

class DeregisterConfirmView(discord.ui.View):
    def __init__(self, orchestrator_name: str):
        super().__init__()
        self.orchestrator_name = orchestrator_name

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (response := deregister_peon_orc(self.orchestrator_name))["status"] == "success":
            embed = build_card(
                title="Deregistration Request",
                message=response["info"]
            )
        else:
            embed = build_card(
                status='nok',
                title="Deregistration Request",
                message=f"Failed to deregister orchestrator: {response.get('info', 'Unknown error')}"
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

class CreateServerView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(GamePlanSelect())

class GamePlanSelect(discord.ui.Select):
    def __init__(self):
        # Get available plans from first available orchestrator
        options = []
        try:
            if (orchestrators := get_peon_orcs())["status"] == "success" and orchestrators["data"]:
                orc = orchestrators["data"][0]
                plans_result = get_all_plans(orc['url'], orc['key'])
                if plans_result["status"] == "success":
                    plans = plans_result["data"][:25]  # Discord limit
                    options = [
                        discord.SelectOption(
                            label=plan.get('title', plan.get('game_uid', 'Unknown')),
                            value=plan.get('game_uid', ''),
                            description=f"Create a {plan.get('game_uid', '')} server"
                        )
                        for plan in plans if plan.get('game_uid')
                    ]
        except Exception as e:
            logging.error(f"Error loading plans: {e}")
        
        if not options:
            options = [discord.SelectOption(label="No plans available", value="none", description="Check orchestrator connection")]
        
        super().__init__(
            placeholder='Select a game plan...',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            embed = build_card(status='nok', message="No plans available")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        modal = ServerCreateModal(self.values[0])
        await interaction.response.send_modal(modal)

class ServerCreateModal(discord.ui.Modal, title='Create New Server'):
    def __init__(self, game_uid: str):
        super().__init__(title=f'Create {game_uid.upper()} Server')
        self.game_uid = game_uid
        
        self.server_name = discord.ui.TextInput(
            label='Server Name',
            placeholder='Enter a unique server name...',
            required=True,
            min_length=3,
            max_length=50
        )
        self.server_description = discord.ui.TextInput(
            label='Description',
            placeholder='Optional server description...',
            required=False,
            max_length=200,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.server_name)
        self.add_item(self.server_description)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if 'error' in (result := get_peon_orcs())['status']:
            embed = build_card(status='nok', message="No orchestrators registered")
            await interaction.followup.send(embed=embed)
            return
        
        # Use first available orchestrator
        orchestrator = result['data'][0]
        user_settings = {}
        if self.server_description.value:
            user_settings['description'] = self.server_description.value
            
        create_result = server_create(
            orchestrator['url'], 
            orchestrator['key'], 
            self.game_uid, 
            self.server_name.value,
            user_settings
        )
        
        if create_result['status'] == 'success':
            embed = build_card(
                status='ok',
                message=f"Server **{self.game_uid}.{self.server_name.value}** created successfully!"
            )
        else:
            embed = build_card(
                status='nok',
                message=f"Failed to create server: {create_result.get('message', 'Unknown error')}"
            )
        
        # Try to replace the original modal message with the result
        try:
            await interaction.edit_original_response(embed=embed, view=None)
        except:
            await interaction.followup.send(embed=embed)

class PlansView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(PlansSelect())

class PlansSelect(discord.ui.Select):
    def __init__(self):
        # Get available plans from first available orchestrator
        options = []
        try:
            if (orchestrators := get_peon_orcs())["status"] == "success" and orchestrators["data"]:
                orc = orchestrators["data"][0]
                plans_result = get_all_plans(orc['url'], orc['key'])
                if plans_result["status"] == "success":
                    plans = plans_result["data"][:25]  # Discord limit
                    options = [
                        discord.SelectOption(
                            label=plan.get('title', plan.get('game_uid', 'Unknown')),
                            value=plan.get('game_uid', ''),
                            description=f"{plan.get('game_uid', '')} - View plan details"
                        )
                        for plan in plans if plan.get('game_uid')
                    ]
        except Exception as e:
            logging.error(f"Error loading plans: {e}")
        
        if not options:
            options = [discord.SelectOption(label="No plans available", value="none", description="Check orchestrator connection")]
        
        super().__init__(
            placeholder='Select a plan to view details...',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            embed = build_card(status='nok', message="No plans available")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        await interaction.response.defer()
        
        if 'error' in (result := get_peon_orcs())['status']:
            embed = build_card(status='nok', message="No orchestrators registered")
            await interaction.followup.send(embed=embed)
            return
            
        # Get plan details from first orchestrator
        orchestrator = result['data'][0]
        plan_result = get_warplan([orchestrator], self.values[0])
        
        if plan_result['status'] == 'success':
            embed = build_card(
                title=f"Plan Details: {self.values[0].upper()}",
                message=plan_result['data']
            )
        else:
            embed = build_card(
                status='nok',
                message=f"Could not get plan details: {plan_result.get('err_code', 'Unknown error')}"
            )
        
        await interaction.followup.send(embed=embed)