
import os, discord, random, sys

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
            await general.send('Hello a Spreadsheet with the name `{}` couldnt be created')




@bot.command(name="addgame")
async def add_game(ctx, game):
    spread = client.open(str(ctx.guild.id)) #Change to server name later
    try:
        spread.add_worksheet(title=str(game), rows="1000", cols="26")
        sheet = spread.worksheet(game)

        sheet.update_cell(1, 1, "Player Name")
        sheet.update_cell(1, 2, "Date")
        sheet.update_cell(1, 3, "Time")
        sheet.update_cell(1, 4, "Name")
        sheet.update_cell(1, 6, "Num Players")
        sheet.update_cell(2, 6, 0)
    except gspread.exceptions.APIError:
        print("A(n) {} error occurred trying to add a game.".format(sys.exc_info()[0]))
        await ctx.message.channel.send("Game is already added. :confused:")
        return

    await ctx.message.channel.send("New game {} added".format(str(game)))

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
async def delete_game(ctx, game=None):
    spread = client.open(str(ctx.guild.id))
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
    spread = client.open(str(ctx.guild.id))
    try:
        sheet = spread.worksheet(game)

        cell = sheet.find("Date")
        for i in range(cell.row, sheet.row_count): #Looping through all the rows
            cell = sheet.cell(i, cell.col)
            if(cell.value == ""): #Get the first cell in that column that's blank
                sheet.update_cell(i, cell.col, date)
                time_cell = sheet.update_cell(i, cell.col + 1, time)

                if(name != ""):
                    name_cell = sheet.update_cell(i, cell.col + 2, name)
                
                await ctx.message.channel.send(":white_check_mark: Scheduled game night successfully.")
                return
    except gspread.exceptions.APIError:
        await ctx.message.channel.send("Game does not exist. Make sure arguments are in Game, Date, Time order and try again.\n\
        if that doesn't work, see the addgame command")     

@bot.command(name="join")
async def join(ctx, game="", eventname=""):
    spread = client.open(str(ctx.guild.id))
    sheet = spread.worksheet(game)
    if(game == "" or eventname == ""):
        await ctx.message.channel.send("Missing information required for joining. See help command for details.")
        return
    for i in range(1, spread.worksheet(game).row_count): #Looping through all the rows
            if(sheet.cell(i,1).value == str(ctx.message.author.name)+"#"+str(ctx.message.author.discriminator)): #Get the first cell in that column that's blank

                await ctx.message.channel.send("You're already signed up for this event :confused:")
                return
            if(sheet.cell(i,1).value == ""): #Get the first cell in that column that's blank
            
                break
    try:
        numplayers = sheet.cell((sheet.find("Num Players").row)+1, (sheet.find("Num Players").col)).value

        eventCellRow = sheet.find(eventname)
        sheet.update_cell(eventCellRow.row+int(numplayers), 1, str(ctx.message.author.name)+"#"+str(ctx.message.author.discriminator))
        sheet.update_cell((sheet.find("Num Players").row)+1,(sheet.find("Num Players").col),int(numplayers)+1)
        await ctx.message.channel.send(":white_check_mark: Joined game night successfully.")
        return
    except gspread.exceptions.APIError:
        await ctx.message.channel.send("Event does not exist. Make sure Event Name is valid.")


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

