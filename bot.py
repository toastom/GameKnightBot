
import os, discord, random, sys
import time
from random import randint
from discord.ext import commands
from discord.utils import find
import json

import gspread
from gspread import Client

from oauth2client.service_account import ServiceAccountCredentials

# We'll need to substitute the Prefix for an Enviroment Variable
BOT_PREFIX = "&" # -Prefix is need to declare a Command in discord ex: !pizza "!" being the Prefix
TOKEN = os.environ['testtoken'] # The token is also substituted for security reasons
# Icons for embeds
SUCCESS = "http://www.pngmart.com/files/3/Green-Tick-PNG-Pic.png"
ERROR = "http://icons.iconarchive.com/icons/google/noto-emoji-symbols/1024/73030-no-entry-icon.png"
INFO = "https://cdn4.iconfinder.com/data/icons/meBaze-Freebies/512/info.png"
# Colors for embeds
GREEN = 0x3cf048
RED = 0xff522b
BLUE = 0x3c8df0
YELLOW = 0xf0e73c


bot = commands.Bot(command_prefix=BOT_PREFIX)
# Google Credentials authorization
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client: Client = gspread.authorize(creds)

def check_server_alias(game, context):
    spread = client.open(str(context.guild.id))
    sheet = spread.sheet1

    try:
        #game_cell = sheet.find("Game")
        alias_cell = sheet.find("Alias")
        #Loop through all the rows, don't worry we'll break or return out before the end
        for r in range(alias_cell.row, sheet.row_count):
            server_alias = sheet.cell(r, alias_cell.col)
            server_alias = server_alias.value
            print("Server alias: ", server_alias)
            if(server_alias != ""):
                #Server alias is a string, get rid of the '[]' and separate each alias
                server_alias.replace("[", "")
                server_alias.replace("]", "")
                server_alias.split(", ")
                print(str(server_alias))

                if(game in server_alias):
                    return sheet.cell(r, alias_cell.col - 1).value
            else:
                return False
    
    #If we don't find a game
    except gspread.exceptions.CellNotFound:
        return False


def check_default_alias(game, context):
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
            break
    else: #Game is not found in default_aliases
        server_game = check_server_alias(game, context)
        #If we did find the game in server aliases
        if(server_game):
            #game = server_game
            return server_game
        

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
        # create embed
        embed_ready = discord.Embed(title="You're ready to create and join game nights! ", description=str(guild.id), color=GREEN)
        embed_ready.set_author(name="A spreadsheet with your server ID has been made!", icon_url=str(guild.icon))
        # -
        general = find(lambda x: x.name == 'general', guild.text_channels)
        if general and general.permissions_for(guild.me).send_messages:
                game_cell  = spreadsheet.sheet1.cell("A1")
                alias_cell = spreadsheet.sheet1.cell("B1")
                game_cell.update_cell("Game")
                alias_cell.update_cell("Alias")

                await general.send(embed=embed_ready)
    except gspread.exceptions.APIError:
        # create embed
        embed_fail = discord.Embed(title="Unexpected error", color=RED)
        embed_fail.set_author(name="A spreadsheet with your server ID could NOT be made!", icon_url=str(guild.icon))
        # -
        general = find(lambda x: x.name == 'general', guild.text_channels)
        if general and general.permissions_for(guild.me).send_messages:
            await general.send(embed=embed_fail)


@bot.command(name="addgame")
async def add_game(ctx, *, game):
    game = check_default_alias(game, ctx)
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
        # create embed
        embed_ready = discord.Embed(title="Game", description=str(game), color=GREEN)
        embed_ready.set_author(name="Game Added", icon_url=SUCCESS)
        # -
    except gspread.exceptions.APIError:
        # create embed
        embed_fail = discord.Embed(title="Game already exists!",description=str(game), color=RED)
        embed_fail.set_author(name="A game could not be added.", icon_url=ERROR)
        # -
        print("A(n) {} error occurred trying to add a game.".format(sys.exc_info()[0]))
        await ctx.message.channel.send(embed=embed_fail)
        return

    await ctx.message.channel.send(embed=embed_ready)

@bot.command(name="allgames")
async def all_games(ctx):
    spread = client.open(str(ctx.guild.id))

    sheets = spread.worksheets()

    #Get a list of all worksheets - check
    #Have the bot say them - sheets - list
    game_list = ""
    amount = 0;
    for i in sheets: #i is a worksheet
        game_list = game_list + "\n" + i.title
        amount += 1;

    # create embed
    embed_info = discord.Embed(title="Game Amount" ,description=str(amount), color=BLUE)
    embed_info.set_author(name="{} Game List".format(ctx.guild.name), icon_url=INFO)
    # -

    await ctx.message.channel.send(embed=embed_info)
    await ctx.message.channel.send("```{}```".format(game_list))

@bot.command(name="deletegame")
async def delete_game(ctx, *, game=None):
    game = check_default_alias(game, ctx)
    spread = client.open(str(ctx.guild.id))
    sheets = spread.worksheets()
    # create embed
    embed_fail = discord.Embed(title="Game does not exist" ,description=str(game), color=RED)
    embed_fail.set_author(name="Game NOT deleted", icon_url=ERROR)
    # -

    if(game):   game = game.lower()

    for i in sheets:
        print(str(game), i.title)
        if(str(game).lower() == "sheet1" and i.title == "Sheet1"):
            await ctx.message.channel.send(":x: Cannot delete Sheet1. Try deleting other games.")
            return
            
        elif(str(game) == i.title.lower()):
            spread.del_worksheet(i)
            game = game.capitalize()

            old_game_alias = spread.sheet1.find(game)
            spread.sheet1.delete_row(old_game_alias.row)

            # create embed
            embed_ready = discord.Embed(title="Game" ,description=str(game), color=GREEN)
            embed_ready.set_author(name="Game Deleted", icon_url=SUCCESS)
            # -
            await ctx.message.channel.send(embed=embed_ready)
            return
        elif(game == None):
            # create embed
            embed_err = discord.Embed(title="Must input a game to delete", color=RED)
            embed_err.set_author(name="Game NOT deleted", icon_url=ERROR)
            # -
            await ctx.message.channel.send(embed=embed_err)
            return
    else: #When the loop ends and we haven't returned out of the other things, then we haven't found the game.
        
        await ctx.message.channel.send(embed=embed_fail)
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
        # create embed
        embed_fail = discord.Embed(title="Gamemaster role does not exist. Contact server staff to ask them to make this role. (case-sensitive)", color=RED)
        embed_fail.set_author(name="Gamemaster not available", icon_url=ERROR)
        # -
        await ctx.message.channel.send(embed=embed_fail)
        return
       
    #If the message author is in the list of people that have the "Gamemaster" role
    if(ctx.message.author in gamemaster.members):
        #Let them schedule the event
        print("Able to schedule.")
    else:
        # create embed
        embed_fail = discord.Embed(title='Only those with the "Gamemaster" role can schedule game nights', color=RED)
        embed_fail.set_author(name="Permission denied", icon_url=ERROR)
        # -
        await ctx.message.channel.send(embed=embed_fail)
        return

    #After all that permissions checking, time to catch incomplete information!
    #Game, date and time are absolutely mandatory, while name is optional
    if(game == "" or date == "" or time == ""):
        # create embed
        embed_fail = discord.Embed(title="Missing information required for scheduling. See help command for details.", color=RED)
        embed_fail.set_author(name="Incomplete command", icon_url=ERROR)
        # -
        await ctx.message.channel.send(embed=embed_fail)
        return
    
    game = check_default_alias(game, ctx)
    spread = client.open(str(ctx.guild.id))
    sheet = spread.worksheet(game)
        
    try:
        

        var_date = None
        var_time = None

        print(str(sheet.cell(2, 2)), str(sheet.cell(2, 3)))
        #Try to find others cell with the same data
        var_date = sheet.find(str(date))
        var_time = sheet.find(str(time))

        if(date == var_date.value):
            print("Date has been found.")
            if(time == var_time.value):
                print("Time has been found.")
                # create embed
                embed_fail = discord.Embed(title="This event is already scheduled for that game.", color=RED)
                embed_fail.set_author(name="Unavailable slot", icon_url=ERROR)
                # -
                await ctx.message.channel.send("That event is already scheduled for that game.")
                return
    #No other cells are found
    except gspread.exceptions.CellNotFound:
        print("No dupes found. Proceed to scheduling event.")
    except gspread.exceptions.WorksheetNotFound:
        # create embed
        embed_fail = discord.Embed(title="Game does not exist. Make sure arguments are in Game, Date, Time order and try again. If that doesn't work, see the addgame command.", color=RED)
        embed_fail.set_author(name="Game not found", icon_url=ERROR)
        # -
        await ctx.message.channel.send(embed=embed_fail)  
        
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
                # create embed
                embed_info = discord.Embed(title="Scheduled game night successfully!.", color=GREEN)
                embed_info.set_author(name="Schedule Success", icon_url=SUCCESS)
                # -
                await ctx.message.channel.send(":white_check_mark: Scheduled game night successfully.")
                return
    except gspread.exceptions.WorksheetNotFound:
        # create embed
        embed_fail = discord.Embed(title="Game does not exist. Make sure arguments are in Game, Date, Time order and try again. If that doesn't work, see the addgame command.", color=RED)
        embed_fail.set_author(name="Game not found", icon_url=ERROR)
        # -
        await ctx.message.channel.send(embed=embed_fail)     

@bot.command(name="join")
async def join(ctx, game="", eventid=""):
    spread = client.open(str(ctx.guild.id))
    sheet = spread.worksheet(game)
    if(eventid == ""):
        # create embed
        embed_fail = discord.Embed(title="Missing information required for joining.",description="See help command for details", color=RED)
        embed_fail.set_author(name="Incomplete Command", icon_url=ERROR)
        # -
        await ctx.message.channel.send(embed=embed_fail)
        return
    for i in range(1, spread.worksheet(game).row_count): #Looping through all the rows
            if(sheet.cell(i,1).value == str(ctx.message.author.name)+"#"+str(ctx.message.author.discriminator)): #Get the first cell in that column that's blank
                # create embed
                embed_fail = discord.Embed(title="Event", color=RED)
                embed_fail.set_author(name="You're already signed up for this event", icon_url=ERROR)
                # -

                await ctx.message.channel.send(embed=embed_fail)
                return
            if(sheet.cell(i,1).value == ""): #Get the first cell in that column that's blank
            
                break
    try:
        numplayers = sheet.cell((sheet.find("Num Players").row)+1, (sheet.find("Num Players").col)).value

        eventCellRow = sheet.find(eventid)
        sheet.update_cell(eventCellRow.row+int(numplayers), 1, str(ctx.message.author.name)+"#"+str(ctx.message.author.discriminator))
        sheet.update_cell((sheet.find("Num Players").row)+1,(sheet.find("Num Players").col),int(numplayers)+1)

        # create embed
        embed_info = discord.Embed(title="Event", color=GREEN)
        embed_info.set_author(name="Joined game night successfully!", icon_url=SUCCESS)
        # -
        await ctx.message.channel.send(embed=embed_info)
        return
    except gspread.exceptions.APIError:
        # create embed
        embed_fail = discord.Embed(title="Event", color=RED)
        embed_fail.set_author(name="Event does not exist.", icon_url=ERROR)
        # -
        await ctx.message.channel.send(embed=embed_fail)
    


@bot.command(name="addalias")
async def add_alias(ctx, game="", *, alias=""):
    """
    Game should be the exact name of the sheet when passed by user.
    Multiple names can be entered at a time, separated by a comma and a space ', '.
    Custom aliases are assigned exactly as given, including trailing whitespace after the first alias in the list.
    Spacing is used in the middle of the alias given: e.g. 'addalias Minecraft mine craft' will allow the user to type 'addgame mine craft'.
    Be careful when adding new aliases. They will conflict with the default aliases provided by GameKnight. Consult defaultalias before making
        custom aliases.
    """
    #Check for all information first
    if(game == "" or alias == ""):
        await ctx.message.channel.send(":x: Missing desired game or alias(es) to assign.")
        return

    spread = client.open(str(ctx.guild.id))
    sheet = spread.sheet1
    game_cell = sheet.find("Game")
    alias_cell = sheet.find("Alias")

    w_sheets = spread.worksheets()
    for g in w_sheets:
        if(g.title == game):
            print("Game found.")
            #So we know the game exists. Let's see if it already has an alias list made
            try: #Update the alias cell if we have added aliases for this game in the past
                prev_game = sheet.find(game)
                #Update the alias list with the request
                alias_cell = sheet.cell(prev_game.row, alias_cell.col)
                
                alias_cell_list = []
                alias_cell_list.append(alias_cell) 
                print(alias_cell_list)

                alias_list = alias.split(", ")

                #Add the new aliases to the previous values
                alias_cell_list[0].value = alias_cell_list[0].value + str(alias_list)
                #Update the cell with alias
                sheet.update_cell(alias_cell.row, alias_cell.col, alias_cell_list[0].value)

                #Cell string cleanup
                alias_cell = sheet.cell(prev_game.row, alias_cell.col)
                new_ac = alias_cell.value.replace("][", ", ")
                sheet.update_cell(alias_cell.row, alias_cell.col, new_ac)

                await ctx.message.channel.send(":white_check_mark: Updated alias(es) {} for game {}.".format(str(alias_list), game))
                return

            except gspread.exceptions.CellNotFound: #If the game hasn't had any aliases made for it in the past
                #print(sys.exc_info()[0])
                break
    else:
        #We've reached the end and haven't broken out of other things. So, we haven't found the game.
        await ctx.message.channel.send(":x: Game {} is not found. Consider addgame first!".format(game))
        return

    #Add alias to list of aliases
    #Split the input into different aliases
    alias_list = alias.split(", ")
    print(alias_list)

    #Now find the next blank cell in the same column as the empty game_cell
    for i in range(game_cell.row, sheet.row_count):
        cell = sheet.cell(i, game_cell.col)
        #Found the next empty cell, now we attach the game to it, find the alias column and do the same
        if(cell.value == ""):
            sheet.update_cell(cell.row, cell.col, game)
            sheet.update_cell(cell.row, alias_cell.col, str(alias_list))

            #sheet.update_cell(cell.row, alias_cell.col, str(alias_list)) #Since we're passing a string here, every time we get this value
                                                                         #cast to a list
            await ctx.message.channel.send(":white_check_mark: Added new alias(es) {} for game {}.".format(str(alias_list), game))
            return





bot.remove_command('help')

@bot.command(name="help")
async def helpembed(ctx,):
    embed = discord.Embed(title="Help")
    embed.add_field(name=BOT_PREFIX + "addgame[gamename]", value="Adds the mentioned game to the spreadsheet", inline = False)
    embed.add_field(name=BOT_PREFIX + "allgames", value="Prints all games that are in the spreadsheet", inline = False)
    embed.add_field(name=BOT_PREFIX + "deletegame[gamename]", value="Deletes the mentioned game from the spreadsheet", inline=True)
    embed.add_field(name=BOT_PREFIX + "schedule[game][date][time][name]", value="Schedules an event(Requires gamemaster role)", inline = True)
    embed.add_field(name=BOT_PREFIX + "join[game][event name]", value ="Joins the event you selected", inline = False)
    embed.add_field(name=BOT_PREFIX + "help", value="Shows this screen", inline = True)
    embed.set_footer(text="Made by Kirbae#0001, tom233145#0069, Pinkpi#0001, hamdi#0001")
    await ctx.message.channel.send(embed=embed)

bot.run(TOKEN)

