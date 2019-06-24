import os, discord, random
from discord.ext import commands
from discord.utils import get

# We'll need to substitute the Prefix for an Enviroment Variable
BOT_PREFIX = os.environ['prefix'] # -Prfix is need to declare a Command in discord ex: !pizza "!" being the Prefix
TOKEN = os.environ['token'] # The token is also substituted for security reasons

bot = commands.Bot(command_prefix=BOT_PREFIX)

@bot.event
async def on_ready():
    print('discord version:')
    print(discord.__version__)
    print('------')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print('Owner: Kirbae#0001')
    print('------')
    servers = list(bot.guilds)
    print('Connected on '+ str(len(servers)) + ' servers:')
    print('\n'.join('>'+ server.name for server in servers))
    print('------')

bot.run(TOKEN)