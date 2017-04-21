from discord.ext import commands
from cogs.utils.dataIO import dataIO
import discord
import os
#Commit patch note error tracking #9

class Seen:
    '''Check when someone was last seen.'''
    def __init__(self, bot):
        self.bot = bot

    async def _get_channel(self, id):
        return discord.utils.get(self.bot.get_all_channels(), id=id)

    async def listener(self, message):
        if not message.channel.is_private and self.bot.user.id != message.author.id:
            server = message.server
            channel = message.channel
            author = message.author
            ts = message.timestamp
            filename = 'data/seen/{}/{}.json'.format(server.id, author.id)
            if not os.path.exists('data/seen/{}'.format(server.id)):
                os.makedirs('data/seen/{}'.format(server.id))
            data = {}
            data['TIMESTAMP'] = '{} {}:{}:{}'.format(ts.date(), ts.hour, ts.minute, ts.second)
            data['MESSAGE'] = message.clean_content
            data['NAME'] = author.display_name
            data['CHANNEL'] = channel.id
            dataIO.save_json(filename, data)

    @commands.command(pass_context=True, no_pm=True, name='seen')
    async def _seen(self, context, username: discord.Member):
        '''seen <@username>'''
        server = context.message.server
        author = username
        filename = 'data/seen/{}/{}.json'.format(server.id, author.id)
        if dataIO.is_valid_json(filename):
            data = dataIO.load_json(filename)
            ts = data['TIMESTAMP']
            last_message = data['MESSAGE']
            channel = await self._get_channel(data['CHANNEL'])
            em = discord.Embed(color=discord.Color.green())
            #em = discord.Embed(description='\nMessage:\n```{}```'.format(last_message), color=discord.Color.green())
            avatar = author.avatar_url if author.avatar else author.default_avatar_url
            em.set_author(name='{} was last seen on {} UTC in #{}'.format(author.display_name, ts, channel.name), icon_url=avatar)
            await self.bot.say(embed=em)
        else:
            message = 'I haven\'t seen {} yet.'.format(author.display_name)
            await self.bot.say('{}'.format(message))


def check_folder():
    if not os.path.exists('data/seen'):
        print('Creating data/seen folder...')
        os.makedirs('data/seen')


def setup(bot):
    check_folder()
    n = Seen(bot)
    bot.add_listener(n.listener, 'on_message')
    bot.add_cog(n)
