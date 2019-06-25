import os, discord, random, sys
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
    print('------')
    print('Owners: Kirbae#0001, tom233145#0069, pinkpi#0001, hamdi#0001')
    print('------')
    servers = list(bot.guilds)
    print('Connected on '+ str(len(servers)) + ' servers:')
    print('\n'.join('>'+ server.name for server in servers))
    print('------')

@bot.command(name="addgame")
async def add_game(ctx, game):
    spread = client.open("Testing")
    try:
        #new_game = spread.add_worksheet(title=str(game), rows="1000", cols="26")
        spread.add_worksheet(title=str(game), rows="1000", cols="26")
    except gspread.exceptions.APIError:
        print("A(n) {} error occurred trying to add a game.".format(sys.exc_info()[0]))
        await ctx.message.channel.send("Game is already added. :confused:")
        return

    await ctx.message.channel.send("New game {} added".format(str(game)))

@bot.command(name="allgames")
async def all_games(ctx):
    spread = client.open("Testing")
    sheets = spread.worksheets()
    print(sheets)

    #Get a list of all worksheets - check
    #Have the bot say them - sheets - list
    game_list = ""
    for i in sheets: #i is a worksheet
        game_list = game_list + "\n" + i.title

    await ctx.message.channel.send("All added games for this server: \n{}".format(game_list))

@bot.command(name="deletegame")
async def delete_game(ctx, game=None):
    spread = client.open("Testing")
    sheets = spread.worksheets()

    for i in sheets:
        print(str(game), i.title)
        if(str(game) == i.title):
            spread.del_worksheet(i)
        elif(game == None):
            await ctx.message.channel.send(":fire: Must input a game to delete. :fire:")
            return
    
    await ctx.message.channel.send("Game {} successfully deleted.".format(str(game)))

bot.run(TOKEN)
