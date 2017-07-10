import discord
import time


async def execute(context):
    msg = context.message
    embed = discord.Embed()
    embed.color = discord.Colour.gold()
    embed.description = "description"
    embed.title = "title2"
    embed.set_author(name=context.message.author.name, icon_url=context.message.author.avatar_url)
    time_took = int(round(time.time() * 1000)) - context.start_time
    embed.set_footer(text="\U000023F3 Took {}ms".format(time_took))
    await context.client.send_message(context.message.channel, '<@{}>: Test'.format(context.message.author.id), embed=embed)