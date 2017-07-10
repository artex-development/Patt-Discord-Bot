import time
import datetime
import aiohttp
import discord
import time
import utils as u

async def execute(context: u.CommandContext):
    async with aiohttp.get("https://www.theartex.net/cloud/api/?sec=announcements") as r:
        if r.status == 200:
            js = await r.json()

            lang = u.lang(context.name, context.message.author)

            message = '\n' + lang['timestamp_label'] + '\n' + lang['timestamp'] + '\n\n' + lang['message_label'] + \
                      '\n' + lang['message']
            message = message.format(user_id=context.message.author.id, timestamp=js['data'][0]['trn_date'].strftime("%B %d, %Y - %I:%M %p"), message=js[
                'data'][0]['message'])

            title = lang['title']
            title = title.format(user_id=context.message.author.id, timestamp=js['data'][0]['trn_date'].strftime("%B %d, %Y - %I:%M %p"), message=js[
                'data'][0]['message'])

            time_took = int(round(time.time() * 1000)) - context.start_time

            embed = discord.Embed()
            embed.color = discord.Colour.blue()
            embed.title = title
            embed.description = message

            embed.set_author(name=context.message.author.name, icon_url=context.message.author.avatar_url)
            embed.set_footer(text="\U000023F3 Took {time}ms".format(time=time_took))
            embed.set_thumbnail(url='https://www.gravatar.com/avatar/ccc81763539bce8fab356a18d1c5c91d?d=mm&s=100')

            await context.client.send_message(context.message.channel, '', embed=embed)
