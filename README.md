# GameKnight
GameKnight is a helpful game night scheduling bot using Google Spreadsheets API made for the first ever Discord Hack Week. The bot allows you to organize events by working with spreadsheets in the background and then retrieving the information when you wish to access it. As a Game Night Organizer, you will need the role "Gamemaster" allowing you to add scheduled events to the Server's spreadsheet. Because of the server sided access of GameKnight, it will work great in big servers where there would be a lot of different games for people to join into. It can also work great for smaller servers that just want a better way to organize their game nights.

# Discord Hack Week Team

Hello! Thanks for this awesome experience to meet with others and improve ourselves, you guys are the best. This is the link for our test server: https://discord.gg/GAuPQqd The link will expire after 25 uses. If you have any questions about anything related to the bot, ping one of us and we'll get to you shortly. -tom233145 aka toastom.

# Use
-To schedule a game, first you will need to add a game to your server. To do this, simply type "gk!addgame [game]" and the bot will create a sheet in the background to organize this new game. You can also delete a game with "gk!deletegame [game]". Just make sure the game that you're trying to delete exists! You can also view all games in your server with "gk!allgames". This will show all games registered to the server as well as all events currently active on that server.

-So you're ready to schedule a game? GameKnightBot makes this easy for you. Just type "gk!schedule [game] [date] [time] [optional: event name]" and it will be automatically scheduled for you and assigned an Event ID. This EventID is unique to every event in the game spreadsheet, and can be given to friends and others to sign up easily.

-Want to join a game? Find out the EventID, then type "gk!join [game] [Event ID]." This will sign you up for the event with the same Event ID for the corresponding game. Don't be late! If you want more info about an event, just type "gk!info [Event ID]".

-Hey, we get it. Some people have different names for games. You don't know how many times people are talking about GTA V, and I have no idea what they're talking about, because I call it "carGame." Well aliases are for you! Type "gk!addalias [game] [alias]" and the bot will register when you try to sign up for a game using that alias. For example if you had the alias "Civ 5" for "Civ V", then joining a Civ V event, you could type "gk!join "Civ 5" [Event ID]" to join instead.

-Want a less detailed but probably just as helpful now that you understand the basics version of what I just said? Type "gk!help" for info about each command and how to use it.

# About Our Team

Our team is a group of teenagers all from different places, representing US West Coast, US East Coast, Winnipeg Canada, and even the Netherlands. We had a lot of fun figuring things out during this competition, and were really inspired by tom233145#0069's original idea for this bot. Our team members are listed here as Pinkpi#0001 (16), tom233145#0069 (17), hamdi#0001 (18), and Kirbae#0001 (19).

"I'm Pinkpi and my favorite game to play with people is generally Duck Game because we mess around the whole time and try out glitches and it's super fun. I hope this bot can help people stay more organized when creating events. I suck at organization, that's why I created a robot to do it instead of me. I'm so glad that our team situation worked out the way it did, everyone was super helpful and amazing. <3 Love you guys!" -Me (Pinkpi)

"I'm Hamdi and my favorite game to play with people is Overwatch because I really like being stuck in Gold since season 2" -🧂Hamdi🧂

"I'm Kirbae and my favorite video game to play with people is Fivem/Gta V because I made some good friends in that game and it's just easy to have fun" -Kirbae

"I'm the owner of this github account and my discord is tom233145. My favorite game right now is Dauntless because of the grind. It [The Bot] was really an idea for a server I'm in that has game nights occasionally, but not that common. Going to try to get them to have some more with this." -tom233145

# The Future of GameKnight

Our original ideas for the implementation of this bot involved global search of events between servers, with the bot storing an invite link for people who join. Events could also be open or closed, joining closed events could require acceptance by the Game Night Organizer. We will also work on smaller updates, like being able to toggle whether or not you need the Gamemaster role to schedule events, which some people may not want to use, and custom prefixes. These are all things that we were not able to implement during hackweek, however they are the next steps.

Readme by Pinkpi with quotes from tom233145, Kirbae, and Hamdi
