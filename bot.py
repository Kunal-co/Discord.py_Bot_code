# Developed by Kunal-co also goes by the name of KCCubes
import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

def load_config():
    if not os.path.exists('config.json'):
        raise FileNotFoundError("config.json file not found. Please create one with the bot token.")
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
TOKEN = config.get("token")

if not TOKEN:
    raise ValueError("Bot token is missing in config.json")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="A Discord Bot"))
    await load_extensions()
    await bot.tree.sync()
    print("All extensions loaded and commands synced")

async def load_extensions():
    for root, dirs, files in os.walk('./cogs'):
        for filename in files:
            if filename.endswith('.py'):
                cog_path = os.path.relpath(os.path.join(root, filename), './')
                cog_name = cog_path.replace(os.sep, '.')[:-3]
                try:
                    await bot.load_extension(f'{cog_name}')
                    print(f'Loaded cog: {cog_name}')
                except Exception as e:
                    print(f'Failed to load cog {cog_name}: {e}')

bot.run(TOKEN)
