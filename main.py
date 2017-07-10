import discord
import utils as u
import logging
import time
import sys
import importlib
import sqlite3 as lite
from pathlib import Path

print('------------------------------')
print('Parameters: {}'.format(sys.argv))

if sys.argv[1] is None:
    print('------------------------------')
    print('Please specify a token for the bot to use.')
    quit(1)

# DB setup
db = lite.connect('db.db')

cur = db.cursor()
cur.execute('SELECT SQLITE_VERSION()')

data = cur.fetchone()

print("SQLite version: {}".format(data[0]))
print('------------------------------')

# Setup logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s|%(levelname)s|%(name)s| %(message)s'))
logger.addHandler(handler)

# Create Discord client
client = discord.Client()


# When bot is ready
@client.event
async def on_ready():
    print('------------------------------')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------------------------------')
    await client.change_presence(game=discord.Game(name='Say @Patt for prefix'))


# When a message is sent that can be read by Patt
@client.event
async def on_message(msg):
    # Start Time
    start_ms_time = int(round(time.time() * 1000))

    # Channel cannot be private
    if msg.channel.is_private:
        return

    # Get the server from the database
    cur.execute("SELECT * FROM guilds WHERE gid='{}'".format(msg.server.id))

    # Get the returned row
    row = cur.fetchone()

    # If the server for som reason wasn't found, set the default prefix.
    if row is None:
        prefix = '!'
    else:
        prefix = row[1]

    # If the message is '@Patt' send the guild prefix
    if msg.content == '<@{}>'.format(client.user.id):
        await client.delete_message(msg)
        await client.send_typing(msg.channel)
        await client.send_message(msg.channel, '<@{}>: This guilds prefix is `{}`'.format(msg.author.id, prefix))
        return

    # Else, check if the message was sent with the required prefix
    elif msg.content.startswith(prefix):
        msgParts = msg.content.split(' ')
        msgParts[0] = msgParts[0][1:]
        if len(msgParts[0]) > 100:
            return
        elif not msgParts[0].isalnum():
            return
        command_script = Path("C:/Users/Allen/DiscordPyBot/commands/{}/command.py".format(msgParts[0]))
        if command_script.is_file():
            # Create command context
            context = u.CommandContext()
            context.client = client
            context.message = msg
            context.args = msgParts
            context.cursor = cur
            context.database = db
            context.name = msgParts[0]
            context.client_server_data = row
            context.start_time = start_ms_time

            # Delete the users message and start typing
            await client.delete_message(msg)
            await client.send_typing(msg.channel)

            # Include and reload command module
            package = "commands.{}".format(msgParts[0])
            name = 'command'
            command_sk = getattr(__import__(package, fromlist=[name]), name)
            importlib.reload(command_sk)

            # Execute the command module
            await command_sk.execute(context)

            # Log the command
            print('CMD "{}#{}" ({}) ran "{}" on the guild "{}" ({})'
                  .format(msg.author.name, msg.author.discriminator, msg.author.id, msgParts[0], msg.server.name,
                          msg.server.id))

            # Unimport the command module, i don't know if this even works.
            del command_sk


# When Patt joins a server
@client.event
async def on_server_join(svr):
    cur.execute("INSERT INTO guilds VALUES('{}', '!')".format(svr.id))
    db.commit()


# When Patt leaves a server
@client.event
async def on_server_remove(svr):
    cur.execute("DELETE FROM guilds WHERE gid='{}'".format(svr.id))
    db.commit()


client.run(sys.argv[1])
