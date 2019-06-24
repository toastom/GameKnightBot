<<<<<<< Updated upstream
import os
import discord
import random
=======
import os, discord, random, sys
>>>>>>> Stashed changes
from discord.ext import commands
from discord.utils import get
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# We'll need to substitute the Prefix for an Enviroment Variable
BOT_PREFIX = os.environ['prefix'] # -Prefix is need to declare a Command in discord ex: !pizza "!" being the Prefix
TOKEN = os.environ['token'] # The token is also substituted for security reasons

bot = commands.Bot(command_prefix=BOT_PREFIX)
#Google Credentials authorization
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

@bot.event
async def on_ready():
    print('discord version:')
    print(discord.__version__)
    print('------')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
<<<<<<< Updated upstream
=======
    print('------')
>>>>>>> Stashed changes
    servers = list(bot.guilds)
    print('Connected on '+ str(len(servers)) + ' servers:')
    print('\n'.join('>'+ server.name for server in servers))
    print('------')

<<<<<<< Updated upstream
bot.run(TOKEN)
=======
@bot.command(name="addgame")
async def add_game(ctx, game):
    spread = client.open("Testing")
    try:
        new_game = spread.add_worksheet(title=str(game), rows="1000", cols="26")
    except gspread.exceptions.APIError:
        print("A(n) {} error occurred.".format(sys.exc_info()[0]))
        await ctx.message.channel.send("Game is already added.")
        client.close()
        return

    await ctx.message.channel.send("New game {} added".format(str(game)))
    client.close()

bot.run(TOKEN)
>>>>>>> Stashed changes
