import os
from discord.ext import commands
import dotenv
config = dotenv.load_dotenv()
help = commands.DefaultHelpCommand(
    dm_help = True,
    no_category = "Other",
    commands_heading = "Commands:",
)
client = commands.Bot(command_prefix="!",help_command=help)

client.load_extension('cogs.Registration')
client.run(os.getenv("DISCORD_OAUTH"))
