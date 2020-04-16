
import os, discord, random, sys, json
import time
from random import randint
from discord.ext import commands
from discord.utils import find
import json

import gspread
from gspread import Client

from oauth2client.service_account import ServiceAccountCredentials

# We'll need to substitute the Prefix for an Enviroment Variable
#BOT_PREFIX = os.environ['prefix'] # -Prefix is need to declare a Command in discord ex: !pizza "!" being the Prefix
BOT_PREFIX = 'gk!'
TOKEN = os.environ['token'] # The token is also substituted for security reasons
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
#creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)

json_creds = os.getenv("CREDS_JSON")
creds_dict = json.loads(json_creds)
creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

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
                #game_cell  = spreadsheet.sheet1.cell("A1")
                #alias_cell = spreadsheet.sheet1.cell("B1")

                game_cell  = spreadsheet.sheet1.cell(1, 1)
                alias_cell = spreadsheet.sheet1.cell(1, 2)
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
    amount -= 1;
    # check if embed not too big
    if amount > 24:
        game_list = game_list.split(", ")
        embed_info = discord.Embed(title="Game Amount", description=str(amount), color=BLUE)
        embed_info.set_author(name="{} Game List".format(ctx.guild.name), icon_url=INFO)
        await ctx.message.channel.send(embed=embed_info)
        for i in sheets:
            if i.title == "Sheet1":
                print("sheet 1 skipped")
            else:
                cell = i.find("Event Id").col
                cell = i.col_values(cell)
                print(cell)
                cell = list(filter(None, cell))
                events = len(cell)-1
                embed_game = discord.Embed(title="Number of events: " + str(events), description=str(amount), color=BLUE)
                embed_game.set_author(name=i.title, icon_url=INFO)
                #await ctx.message.channel.send(embed=embed_game)
        await ctx.message.channel.send(embed=embed_game)
    # create embed
    else:
        game_list = game_list.split(", ")
        embed_info = discord.Embed(title="Game Amount", description=str(amount), color=BLUE)
        embed_info.set_author(name="{} Game List".format(ctx.guild.name), icon_url=INFO)
        for i in sheets:
            if i.title == "Sheet1":
                print("sheet 1 skipped")
            else:
                cell = i.find("Event Id").col
                cell = i.col_values(cell)
                print(cell)
                cell = list(filter(None, cell))
                events = len(cell) - 1
                embed_info.add_field(name=i.title, value="Number of events: " + str(events), inline=False)
                #await ctx.message.channel.send(embed=embed_info)
        await ctx.message.channel.send(embed=embed_info)
                
    
    # -


@bot.command(name="events")
async def events(ctx, game):
    spread = client.open(str(ctx.guild.id))
    #Get a list of all worksheets - check
    #Have the bot say them - sheets - list
    game = check_default_alias(game, ctx)
    sheet = spread.worksheet(game)
    cell = sheet.find("Event Id").col
    cell = sheet.col_values(cell)
    print(cell)
    cell = list(filter(None, cell))
    cell.pop(0)
    embed_event = discord.Embed(title=str(sheet.title), description="These are the current events for this game", color=BLUE)
    embed_event.set_author(name="{} Events List".format(ctx.guild.name), icon_url=INFO)
    embed_event.add_field(name="Events", value='\n'.join(cell), inline=False)
    await ctx.message.channel.send(embed=embed_event)
    # create embed

    # -
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
        # create embed
        embed_sh1 = discord.Embed(title="Can not delete Sheet1",description="Try deleting other games", color=RED)
        embed_sh1.set_author(name="Invalid command", icon_url=ERROR)
        # -
        if(str(game).lower() == "sheet1" and i.title == "Sheet1"):
            await ctx.message.channel.send(embed=embed_sh1)
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
                await ctx.message.channel.send(embed=embed_fail)
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
        cell = sheet.find("Player Name")
        for i in range(cell.row, sheet.row_count): #Looping through all the rows
            cell = sheet.cell(i, cell.col)
            if(cell.value == ""): #Get the first cell in that column that's blank
                sheet.update_cell(i, cell.col + 1, date)
                time_cell = sheet.update_cell(i, cell.col + 2, time)

                if(name != ""):
                    name_cell = sheet.update_cell(i, cell.col + 2, name)
                    
                sheet.update_cell(sheet.find("Event Id").row+i-1, sheet.find("Event Id").col, neweventid)
                sheet.update_cell(sheet.find("Num Players").row+i-1, sheet.find("Num Players").col, 0)

                # create embed
                embed_finish = discord.Embed(title="New players can join using the event using the Event ID.",description="Command to join is {}join [game] [event id]".format(BOT_PREFIX), color=GREEN)
                embed_finish.add_field(name="Event ID", value=neweventid, inline=True)
                embed_finish.add_field(name="Game", value=game, inline=True)
                embed_finish.set_author(name="Schedule Success", icon_url=SUCCESS)
                # -
                
                await ctx.message.channel.send(embed=embed_finish)
                return

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
                embed_info = discord.Embed(title="Scheduled game night successfully!", color=GREEN)
                embed_info.set_author(name="Schedule Success", icon_url=SUCCESS)
                # -
                await ctx.message.channel.send(embed=embed_info)
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

    game = check_default_alias(game, ctx)
    sheet = spread.worksheet(game)

    if(eventid == ""):
        # create embed
        embed_fail = discord.Embed(title="Missing information required for joining.",description="See help command for details", color=RED)
        embed_fail.set_author(name="Incomplete Command", icon_url=ERROR)
        # -
        await ctx.message.channel.send(embed=embed_fail)
        return
    for i in range(sheet.find(eventid).row, spread.worksheet(game).row_count): #Looping through all the rows
            if(sheet.cell(i,1).value == str(ctx.message.author.name)+"#"+str(ctx.message.author.discriminator)): #Get the first cell in that column that's blank
                # create embed
                embed_fail = discord.Embed(title="Event ID",description=eventid, color=RED)
                embed_fail.set_author(name="You're already signed up for this event", icon_url=ERROR)
                # -

                await ctx.message.channel.send(embed=embed_fail)
                return
            if(sheet.cell(i,1).value == ""): #Get the first cell in that column that's blank
            
                break
    try:
        numplayers = sheet.cell((sheet.find(eventid).row), (sheet.find("Num Players").col)).value

        eventCellRow = sheet.find(eventid)
        #sheet.update_cell(eventCellRow.row, 1, "these people joined:")
        empty_row = ['' for cell in range(sheet.col_count)]
        insertion_row = int(eventCellRow.row + int(numplayers) + 1)
        sheet.insert_row(empty_row, index=insertion_row)
        sheet.update_cell((sheet.find(eventid).row),(sheet.find("Num Players").col),int(numplayers)+1)
        sheet.update_cell(eventCellRow.row + int(numplayers), 1, str(ctx.message.author.name) + "#" + str(ctx.message.author.discriminator))



        # create embed
        embed_info = discord.Embed(title="Event", color=GREEN)
        embed_info.set_author(name="Joined game night successfully!", icon_url=SUCCESS)
        # -
        await ctx.message.channel.send(embed=embed_info)
        return
    except gspread.exceptions.APIError:
        print(gspread.exceptions.APIError)
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

    # create embed
    embed_nogame = discord.Embed(title="Game",description=game, color=RED)
    embed_nogame.set_author(name="Game not found, try addgame first!", icon_url=ERROR)
    # -
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

                # create embed
                embed_alias = discord.Embed(title="Game",description=game, color=GREEN)
                embed_alias.set_author(name="Updated alias(es)", icon_url=SUCCESS)
                # -
                
                await ctx.message.channel.send(embed=embed_alias)
                await ctx.message.channel.send("Aliases: ```{}```".format(str(alias_list)))
                return

            except gspread.exceptions.CellNotFound: #If the game hasn't had any aliases made for it in the past
                #print(sys.exc_info()[0])
                break
    else:
        #We've reached the end and haven't broken out of other things. So, we haven't found the game.
        
        await ctx.message.channel.send(embed=embed_nogame)
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
            # create embed
            embed_alias = discord.Embed(title="Game",description=game, color=GREEN)
            embed_alias.set_author(name="Updated alias(es)", icon_url=SUCCESS)
            # -
            await ctx.message.channel.send(embed=embed_alias)
            await ctx.message.channel.send("```{}```".format(str(alias_list)))
            return

@bot.command(name="info")
async def info(ctx, eventid=""):
    if(eventid == ""):
        embed_fail = discord.Embed(description="Please include the id of the event you want.\
                                     Use the events command to view event ids.")
        embed_fail.set_author(name="Missing Event ID.", icon_url=ERROR)
        await ctx.message.channel.send(embed=embed_fail)
        return

    game_id = eventid[:4]
    print(game_id)

    spread = client.open(str(ctx.guild.id))
    sheets = spread.worksheets()
    for s in sheets:
        #Check each sheet's first event id. If it's empty or doesn't match the game_id, skip it
        #Skip past Sheet1 because it doesn't have Event Id
        if(s.title == "Sheet1"):
            continue
        
        event_label = s.find("Event Id")
        first_event = s.cell(event_label.row + 1, event_label.col)
        if(str(first_event.value) == "" or str(first_event.value)[:4] != game_id):
            print("Wrong game. Continuing...")
            continue
        #If we found the right game
        elif(str(first_event.value)[:4] == game_id):
            try:
                cell = s.find(eventid)
                print(cell)
                
                date = s.find("Date")
                time = s.find("Time")
                name = s.find("Name")
                players = s.find("Player Name")
                num_players = s.find("Num Players")

                embed_ready = discord.Embed(color=BLUE)
                embed_ready.set_author(name="Info for event: {}".format(cell.value), icon_url=INFO)
                
                current_cell = s.cell(cell.row, date.col)
                embed_ready.add_field(name=date.value, value=current_cell.value, inline=True)

                current_cell = s.cell(cell.row, time.col)
                embed_ready.add_field(name=time.value, value=current_cell.value, inline=True)

                current_cell = s.cell(cell.row, name.col)
                name_val = ""
                #If the current cell value is empty, make it something
                if(current_cell.value == ""):
                    name_val = "None"
                else:
                    name_val = current_cell.value
                embed_ready.add_field(name=name.value, value=name_val, inline=True)

                current_cell = s.cell(cell.row, num_players.col)
                print("Num players cell: {}".format(current_cell.value))
                embed_ready.add_field(name=num_players.value, value=str(current_cell.value), inline=False)

                print(current_cell.value)

                vals = ""
                for r in range(cell.row, cell.row + int(current_cell.value)):
                    current_cell = s.cell(r, players.col)
                    print(current_cell)

                    print("Before append {}".format(vals))
                    vals = vals + "\n" + str(current_cell.value)
                    print("After append {}".format(vals))

                    if(current_cell.value == ""):
                        vals = vals + "\n" + "None"
                        print("After append nothing {}".format(vals))
                        break
                    #vals = vals + "\n" + current_cell.value

                #embed_ready.add_field(name="Number of PLayers", value=values, inline=False)
                embed_ready.add_field(name="Players", value=vals, inline=False)

                await ctx.message.channel.send(embed=embed_ready)

                return
            except gspread.exceptions.CellNotFound:
                await ctx.message.channel.send(":x: An unknown error occurred when finding the event.")
                return



bot.remove_command('help')

@bot.command(name="help")
async def helpembed(ctx,):
    embed = discord.Embed(title="Help")
    embed.add_field(name=BOT_PREFIX + "addgame [gamename]", value="Adds the mentioned game to the spreadsheet.", inline = False)
    embed.add_field(name=BOT_PREFIX + "allgames", value="Prints all games that are in the spreadsheet.", inline = False)
    embed.add_field(name=BOT_PREFIX + "deletegame [gamename]", value="Deletes the mentioned game from the spreadsheet.", inline=True)
    embed.add_field(name=BOT_PREFIX + "schedule [game]  [date] [time] [name]", value="Schedules an event(Requires Gamemaster role).", inline = True)
    embed.add_field(name=BOT_PREFIX + "join [game][event id]", value ="Joins the event you selected.", inline = False)
    embed.add_field(name=BOT_PREFIX + "addalias [game] [alias]", value="Adds an alias to make it easier to add games.", inline=False)
    embed.add_field(name=BOT_PREFIX + "events [game]", value="Shows all events with IDs for the mentioned game.", inline=False)
    embed.add_field(name=BOT_PREFIX + "info [eventid]", value="Shows all details related to the mentenioned event.", inline=False)
    embed.add_field(name=BOT_PREFIX + "help", value="Shows this screen", inline = True)
    embed.set_footer(text="Made by Kirbae#0001, tom233145#0069, Pinkpi#0001, hamdi#0001")
    await ctx.message.channel.send(embed=embed)


bot.run(TOKEN)

