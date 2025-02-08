# REPORT BOT CODE developed by KCCubes
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import io
import json
import os

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
# Enter your discord bot token here and run the file make sure to keep them inside "" for it to work
TOKEN="YOUR_DISCORD_BOT_TOKEN"
REPORT_ROLE = "🔒 | Report-staff"
# if you feel like this name isnt good you can change it just keep in " "
# any code below this i would recommend not to change if you are not a discord bot developer.

def load_server_config():
    if os.path.exists('server.json'):
        with open('server.json', 'r') as f:
            return json.load(f)
    return {}

def save_server_config(config):
    with open('server.json', 'w') as f:
        json.dump(config, f, indent=4)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Reports"))
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="download", description="Get the bots files link and the server invite link for Empirica")
async def support_command(interaction: discord.Interaction):
    server_invite_link = "https://discord.gg/k9W9Vadtv4"
    bot_files_link = ""

    embed = discord.Embed(
        title="Support server & Bot files Links",
        description="Here are the support server and bot files links:",
        color=discord.Color.blue()
    )

    embed.add_field(name="Bot Files:", value=bot_files_link, inline=False)
    embed.add_field(name="Server Invite:", value=server_invite_link, inline=False)

    embed.set_footer(text="Use the links as needed.")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="List available bot commands and descriptions")
@app_commands.guild_only()
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Bot Commands",
        description="Here's a list of commands available in the bot:",
        color=discord.Color.blue()
    )
    embed.add_field(name="/ping", value="Check the bot's latency.", inline=False)
    embed.add_field(name="/setupreport", value="Setup report channels and the report system.", inline=False)
    embed.add_field(name="/reportrole", value=f"Create the '{REPORT_ROLE}' role.", inline=False)
    embed.add_field(name="/verifiedreport <user>", value=f"Send a verification message to the mentioned user.\nOnly users with '{REPORT_ROLE}' role can use this command.", inline=False)
    embed.add_field(name="/download", value=f"Get the download link of the bot and its server invite also.")
    embed.set_footer(text="Use the commands in the format /command_name")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setupreport", description="setups report & submit report channel")
@app_commands.guild_only()
async def setupreport(interaction: discord.Interaction):
    guild = interaction.guild

    category = discord.utils.get(guild.categories, name="Reports")
    if not category:
        category = await guild.create_category("Reports")

    config = load_server_config()
    guild_config = config.get(str(guild.id), {})

    report_channel = guild.get_channel(guild_config.get("report_channel_id")) if "report_channel_id" in guild_config else None
    submit_channel = guild.get_channel(guild_config.get("submit_channel_id")) if "submit_channel_id" in guild_config else None

    if not report_channel:
        report_channel = await guild.create_text_channel("report", category=category)
        await report_channel.edit(slowmode_delay=300)
        await report_channel.set_permissions(
            guild.default_role,
            send_messages=False,
            read_messages=True,
            add_reactions=False
        )
        guild_config["report_channel_id"] = report_channel.id

    if not submit_channel:
        submit_channel = await guild.create_text_channel("reports-submitted", category=category)
        report_role = discord.utils.get(guild.roles, name=REPORT_ROLE)
        if not report_role:
            report_role = await guild.create_role(name=REPORT_ROLE, permissions=discord.Permissions.none())

        await submit_channel.set_permissions(guild.default_role, read_messages=False, send_messages=False)
        await submit_channel.set_permissions(report_role, read_messages=True, send_messages=True)

        guild_config["submit_channel_id"] = submit_channel.id

    config[str(guild.id)] = guild_config
    save_server_config(config)

    embed = discord.Embed(
        title="Report Players",
        description=(
            "**You can report a user you believe is breaking a rule. Be sure to include evidence with your report.**\n"
            "**Your message will be deleted and forwarded to a channel only visible to staff.**\n\n"
            "**Note:**\n"
            "1) Don't spam [spam=10day mute]\n"
            "2) The bot will ask in DMs to send the image so don’t send here"
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Server: {guild.name}", icon_url=guild.icon.url)

    await report_channel.send(embed=embed)

    await interaction.response.send_message(
        f"Report setup completed! Channels created: {report_channel.mention} and {submit_channel.mention}",
        ephemeral=True
    )
    
@bot.tree.command(name="reportrole", description="creates a report role for staff to allow them to manage reports and verify them")
@app_commands.guild_only()
async def reportrole(interaction: discord.Interaction):
    existing_role = discord.utils.get(interaction.guild.roles, name=REPORT_ROLE)
    if existing_role:
        await interaction.response.send_message(f"The role '{REPORT_ROLE}' already exists.", ephemeral=True)
        return
    role = await interaction.guild.create_role(name=REPORT_ROLE)
    await interaction.response.send_message(f"Role '{role.name}' created successfully!", ephemeral=True)

@bot.tree.command(name="verifiedreport", description="Send a verification message to the mentioned user.")
@app_commands.describe(user="The user to send the verification message to")
@app_commands.guild_only()
async def verifiedreport(interaction: discord.Interaction, user: discord.Member):
    role = discord.utils.get(interaction.user.roles, name=REPORT_ROLE)
    if not role:
        await interaction.response.send_message(f"You do not have the required role '{REPORT_ROLE}' to use this command.", ephemeral=True)
        return
    embed = discord.Embed(
        title="Your report has been verified ✅",
        description=(
            f"Your report has been verified ⬆️ by the server {interaction.guild.name}\n"
            f"Thanks for reporting the problem on our server. Actions will be taken.\n"
            f"Stay safe ✅\n"
            f"Verified 🔗 by {interaction.user.mention}"
        ),
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Verified by: {interaction.user.name}")
    try:
        await user.send(embed=embed)
        await interaction.response.send_message(f"Verified message sent to {user.mention}.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"Could not send message to {user.mention}. They may have DMs disabled.", ephemeral=True)

@bot.event
async def on_message(message):
    if message.guild is None:
        return

    if message.author == message.guild.me:
        return

    guild_id = str(message.guild.id)
    config = load_server_config()

    if guild_id in config and message.channel.id == config[guild_id]['report_channel_id']:
        if message.author.bot:
            await message.delete()
            return

        submit_channel = bot.get_channel(config[guild_id]['submit_channel_id'])

        if submit_channel:
            embed = discord.Embed(title="New Report", description=f"Report from {message.author.mention}", color=0x00ff00)
            embed.add_field(name="Description", value=message.content[:1024], inline=False)

            files = []
            for attachment in message.attachments:
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp:
                        if resp.status == 200:
                            file = io.BytesIO(await resp.read())
                            file.seek(0)
                            files.append(discord.File(fp=file, filename=attachment.filename))

            await submit_channel.send(embed=embed, files=files)
            await message.delete()

@bot.event
async def on_application_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        missing_perms = ", ".join(error.missing_permissions)
        await interaction.response.send_message(
            f"Error: You lack the following permission(s): **{missing_perms}**.",
            ephemeral=True
        )
    elif isinstance(error, app_commands.BotMissingPermissions):
        missing_perms = ", ".join(error.missing_permissions)
        await interaction.response.send_message(
            f"Error: I lack the following permission(s): **{missing_perms}**. Please adjust my role permissions.",
            ephemeral=True
        )
    elif isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message(
            "Error: You do not meet the requirements to use this command.",
            ephemeral=True
        )
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"Error: This command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
            ephemeral=True
        )
    elif isinstance(error, app_commands.CommandNotFound):
        await interaction.response.send_message(
            "Error: This command does not exist.",
            ephemeral=True
        )
    elif isinstance(error, app_commands.MissingRequiredArgument):
        await interaction.response.send_message(
            f"Error: Missing required argument: {error.param.name}. Please check the command format.",
            ephemeral=True
        )
    elif isinstance(error, app_commands.CommandInvokeError):
        original = getattr(error, "original", None)
        if isinstance(original, discord.Forbidden):
            await interaction.response.send_message(
                "Error: I don't have the required permissions to execute this command.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"Error: An error occurred while executing the command: {original}",
                ephemeral=True
            )
    else:
        await interaction.response.send_message(
            "Error: An unexpected error occurred. Please contact support if the issue persists.",
            ephemeral=True
        )

bot.run(TOKEN)