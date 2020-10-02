import os
from discord.ext import commands
import dotenv
import discord

intents = discord.Intents()
intents.members = True
intents.messages = True
intents.guilds = True
intents.reactions = True

config = dotenv.load_dotenv()
help = commands.DefaultHelpCommand(
    dm_help = True,
    no_category = "Other",
    commands_heading = "Commands:",
)
client = commands.Bot(command_prefix="!",help_command=help, intents=intents)

client.load_extension('cogs.registration')
client.load_extension('cogs.voting')
client.load_extension('cogs.mentor')

client.run(os.getenv("DISCORD_OAUTH"))
