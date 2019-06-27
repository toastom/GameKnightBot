
import os, discord, random, sys
import time
from random import randint
from discord.ext import commands
from discord.utils import find

import gspread
from gspread import Client

from oauth2client.service_account import ServiceAccountCredentials

# We'll need to substitute the Prefix for an Enviroment Variable
BOT_PREFIX = os.environ['prefix'] # -Prefix is need to declare a Command in discord ex: !pizza "!" being the Prefix
TOKEN = os.environ['token'] # The token is also substituted for security reasons

bot = commands.Bot(command_prefix=BOT_PREFIX)
# Google Credentials authorization
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client: Client = gspread.authorize(creds)


def check_default_alias(game):
    with open("default_aliases.json", "r") as j:
        default_aliases = j.read()
    aliases = json.loads(default_aliases)
    #print(aliases)

    if(game):   lower_game = game.lower()
    else:   return

    for i in aliases.items():
        #print(i[0], i[1]) #i is a list of tuples, first is key, second is list of that key's values
        if(lower_game in i[1]): #If game is one of the aliases for games
            game = i[0] #Set game to the proper game

    game = list(game)
    for i in range(0, len(game)):
        if(game[i - 1] == " "):
            game[i] = game[i].upper()
    game = str().join(game)
    game = game.capitalize()
    print(game)
    return game


@bot.event
async def on_ready():
    print('discord version:')
    print(discord.__version__)
    print('------')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    servers = list(bot.guilds)
    print('Connected on '+ str(len(servers)) + ' servers:')
    print('\n'.join('>'+ server.name for server in servers))
    print('------')


@bot.event
async def on_guild_join(guild):
    spreadsheet = {
        'properties': {
            'title': guild.name,
            'developerMetadata': guild.id
        }
    }
    try:
        spreadsheet = client.create(str(guild.id))
        spreadsheet.share('gameknightbot@gmail.com', perm_type='user', role='writer')
        general = find(lambda x: x.name == 'general', guild.text_channels)
        if general and general.permissions_for(guild.me).send_messages:
                await general.send('Hello a Spreadsheet with the name `{}` has been created for your server'.format(str(guild.id)))
    except gspread.exceptions.APIError:
        general = find(lambda x: x.name == 'general', guild.text_channels)
        if general and general.permissions_for(guild.me).send_messages:
            await general.send('Hello a Spreadsheet with the name `{}` couldn\'t be created')


@bot.command(name="addgame")
async def add_game(ctx, *, game):
    game = check_default_alias(game)
    spread = client.open(str(ctx.guild.id))
    try:
        spread.add_worksheet(title=str(game), rows="1000", cols="26")
        sheet = spread.worksheet(game)

        sheet.update_cell(1, 1, "Player Name")
        sheet.update_cell(1, 2, "Date")
        sheet.update_cell(1, 3, "Time")
        sheet.update_cell(1, 4, "Num Attending")
        sheet.update_cell(1, 4, "Name")
        sheet.update_cell(1, 5, "Event Id")
        sheet.update_cell(1, 6, "Num Players")
        sheet.update_cell(2, 6, 0)
    except gspread.exceptions.APIError:
        print("A(n) {} error occurred trying to add a game.".format(sys.exc_info()[0]))
        await ctx.message.channel.send("Game is already added. :confused:")
        return

    await ctx.message.channel.send(":white_check_mark: New game {} added".format(str(game)))

@bot.command(name="allgames")
async def all_games(ctx):
    spread = client.open(str(ctx.guild.id))

    sheets = spread.worksheets()
    print(sheets)

    #Get a list of all worksheets - check
    #Have the bot say them - sheets - list
    game_list = ""
    for i in sheets: #i is a worksheet
        game_list = game_list + "\n" + i.title

    await ctx.message.channel.send("All added games for this server: \n{}".format(game_list))

@bot.command(name="deletegame")
async def delete_game(ctx, *, game=None):
    game = check_default_alias(game)
    spread = client.open(str(ctx.guild.id))
    sheets = spread.worksheets()

    if(game):   game = game.lower()

    for i in sheets:
        print(str(game), i.title)
        if(str(game) == i.title.lower()):
            spread.del_worksheet(i)
            game = game.capitalize()
            await ctx.message.channel.send("Game {} successfully deleted.".format(str(game)))
            return
        elif(game == None):
            await ctx.message.channel.send(":x: Must input a game to delete.")
            return
    else: #When the loop ends and we haven't returned out of the other things, then we haven't found the game.
        await ctx.message.channel.send(":x: Game {} does not exist.".format(str(game)))
        return


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
    
    game = check_default_alias(game)
    spread = client.open(str(ctx.guild.id))
    sheet = spread.worksheet(game)

    var_date = None
    var_time = None

    print(str(sheet.cell(2, 2)), str(sheet.cell(2, 3)))
    try:
        #Try to find others cell with the same data
        var_date = sheet.find(str(date))
        var_time = sheet.find(str(time))

        if(date == var_date.value):
            print("Date has been found.")
            if(time == var_time.value):
                print("Time has been found.")
                await ctx.message.channel.send("That event is already scheduled for that game.")
                return
    #No other cells are found
    except gspread.exceptions.CellNotFound:
        print("No dupes found. Proceed to scheduling event.")
        
    print(sys.exc_info()[0])

    """
    Can finally start the actual scheduling code. Yay.
    Searches for each individual element in the specified game,
    if it doesn't exist, create it
    """
    try:
        sheet = spread.worksheet(game)
        neweventid = game[0:2]+game[-2:]+"-"+str(randint(10000000, 99999999))
        cell = sheet.find("Date")
        for i in range(cell.row, sheet.row_count): #Looping through all the rows
            cell = sheet.cell(i, cell.col)
            if(cell.value == ""): #Get the first cell in that column that's blank
                sheet.update_cell(i, cell.col, date)
                time_cell = sheet.update_cell(i, cell.col + 1, time)

                if(name != ""):
                    name_cell = sheet.update_cell(i, cell.col + 2, name)
                sheet.update_cell(sheet.find("Event Id").row+i-1, sheet.find("Event Id").col, neweventid)
                sheet.update_cell(sheet.find("Num Players").row+i-1, sheet.find("Num Players").col, 0)
                await ctx.message.channel.send(":white_check_mark: Scheduled game night successfully. The Event ID is " + neweventid + ", so new players can join using .join " + game + " " + neweventid)
        date_cell = sheet.find("Date")
        time_cell = sheet.find("Time")
        print(date_cell, time_cell)

        cells_changed = []
        
        for i in range(date_cell.row, sheet.row_count): #Looping through all the rows, i is an int
            cell = sheet.cell(i, date_cell.col)
            print(str(cell))

            if(cell.value == ""): #Get the first cell in the date column that's blank
                #Update cells with Date and Time
                cells_changed.append([(i, cell.col), (i, time_cell.col)])
                print("\n{}".format("cells_changed: {}".format(cells_changed)))


                if(name != ""):
                    name_cell = sheet.find("Name")
                    cells_changed.append((i, name_cell.col))
                    print("\n{}".format(cells_changed))
                
                cells = []
                for pair, value in cells_changed:
                    new_cell = gspread.Cell(pair[0], pair[1])
                    new_cell.value = str(date)
                    cells.append(new_cell)

                    new_cell = gspread.Cell(value[0], value[1])
                    new_cell.value = str(time)
                    cells.append(new_cell)

                    print(type(pair))
                    print("Pair: {}, Value: ".format(pair))
                    print("Cells: {}".format(cells))

                sheet.update_cells(cells, "RAW")
                await ctx.message.channel.send(":white_check_mark: Scheduled game night successfully.")
                return
    except gspread.exceptions.WorksheetNotFound:
        await ctx.message.channel.send("Game does not exist. Make sure arguments are in Game, Date, Time order and try again. If that doesn't work, see the addgame command.")     

@bot.command(name="join")
async def join(ctx, game="", eventid=""):
    spread = client.open(str(ctx.guild.id))
    sheet = spread.worksheet(game)
    if(eventid == ""):
        await ctx.message.channel.send("Missing information required for joining. See help command for details.")
        return
    for i in range(1, spread.worksheet(game).row_count): #Looping through all the rows
            if(str(sheet.cell(sheet.find(eventid).row-1+i,1).value) == (str(ctx.message.author.name)+"#"+str(ctx.message.author.discriminator))): #Get the first cell in that column that's blank

                await ctx.message.channel.send("You're already signed up for this event :confused:")
                return
            if(sheet.cell(i,1).value == ""): #Get the first cell in that column that's blank
            
                break
    try:
        numplayers = sheet.cell((sheet.find("Num Players").row)+1, (sheet.find("Num Players").col)).value

        eventCellRow = sheet.find(eventid)
        sheet.update_cell(eventCellRow.row+int(numplayers), 1, str(ctx.message.author.name)+"#"+str(ctx.message.author.discriminator))
        sheet.update_cell((sheet.find("Num Players").row)+1,(sheet.find("Num Players").col),int(numplayers)+1)
        await ctx.message.channel.send(":white_check_mark: Joined game night successfully.")
        return
    except gspread.exceptions.APIError:
        await ctx.message.channel.send("Event does not exist. Make sure Event Name is valid.")
    










bot.run(TOKEN)

