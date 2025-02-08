import discord
from discord.ext import commands
import json
import os


# Enter your bot token here
TOKEN = "YOUR_DISCORD_BOT_TOKEN"

async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await load_extensions()
    await bot.tree.sync()
    print("All extensions loaded and commands synced and also started up (not so) custom rpc")

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
