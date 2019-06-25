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
    spread = client.open(ctx.guild.id) #Change to server name later
    try:
        spread.add_worksheet(title=str(game), rows="1000", cols="26")
        sheet = spread.worksheet(game)

        sheet.update_cell(1, 1, "Player Name")
        sheet.update_cell(1, 2, "Date")
        sheet.update_cell(1, 3, "Time")
        sheet.update_cell(1, 4, "Name")
    except gspread.exceptions.APIError:
        print("A(n) {} error occurred trying to add a game.".format(sys.exc_info()[0]))
        await ctx.message.channel.send("Game is already added. :confused:")
        return

    await ctx.message.channel.send("New game {} added".format(str(game)))

@bot.command(name="allgames")
async def all_games(ctx):
    spread = client.open(ctx.guild.id) #Change to server name later
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
    spread = client.open(ctx.guild.id)
    sheets = spread.worksheets()

    for i in sheets:
        print(str(game), i.title)
        if(str(game) == i.title):
            spread.del_worksheet(i)
        elif(game == None):
            await ctx.message.channel.send(":fire: Must input a game to delete. :fire:")
            return
    
    await ctx.message.channel.send("Game {} successfully deleted.".format(str(game)))

@bot.command(name="schedule")
async def schedule(ctx, game="", date="", time="", name=""):
    #Check if the command was called from someone with a "Gamemaster" role
    server_roles = ctx.message.guild.roles
    gamemaster = None
    
    for i in server_roles:
        if(i.name == "Gamemaster"): #If there is a role called "Gamemaster"
            gamemaster = i #Get the gamemaster role
            print("Gamemaster role available.")
    
    if(gamemaster == None): #If "Gamemaster" role was not found
        await ctx.message.channel.send('No role titled "Gamemaster". Contact server staff to make this role (case-sensitive).')
        return
       
    #If the message author is in the list of people that have the "Gamemaster" role
    if(ctx.message.author in gamemaster.members):
        #Let them schedule the event
        print("Able to schedule.")
    else:
        await ctx.message.channel.send('Only those with the "Gamemaster" role can schedule game nights.')
        return

    #After all that permissions checking, time to catch incomplete information!
    #Game, date and time are absolutely mandatory, while name is optional
    if(game == "" or date == "" or time == ""):
        await ctx.message.channel.send("Missing information required for scheduling. See help command for details.")
        return

    """
    Can finally start the actual scheduling code. Yay.
    Searches for each individual element in the specified game,
    if it doesn't exist, create it
    """
    spread = client.open(ctx.guild.id)
    try:
        sheet = spread.worksheet(game)

        cell = sheet.find("Date")
        for i in range(cell.row, sheet.row_count): #Looping through all the rows
            cell = sheet.cell(i, cell.col)
            if(cell.value == ""): #Get the first cell in that column that's blank
                sheet.update_cell(i, cell.col, date)
                time_cell = sheet.update_cell(i, cell.col + 1, time)

                if(name != ""):
                    name_cell = sheet.update_cell(i, cell.col + 3, name)
                
                await ctx.message.channel.send(":white_check_mark: Scheduled game night successfully.")
                return

    except gspread.exceptions.APIError:
        await ctx.message.channel.send("Game does not exist. Make sure arguments are in Game, Date, Time order and try again.\n\
        If that doesn't work, see the addgame command.")











bot.run(TOKEN)
