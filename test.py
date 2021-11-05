import os
import discord
from discord.ext import commands,tasks
import youtube_dl
from dotenv import load_dotenv
import random
import pickle
import asyncio
from riotwatcher import LolWatcher, ApiError
import pandas as pd
from pprint import pprint
GUILD='test'
filename = 'message_pickle'
filename2 = 'role_pickle'
load_dotenv('token.env')
TOKEN=os.getenv('DISCORD_TOKEN')
api_key=os.getenv('RIOT_TOKEN')
watcher = LolWatcher(api_key)
my_region = 'na1'
me = watcher.summoner.by_name(my_region, 'BeesInYourChair')
print(me)
message_list = []
infile = open(filename,'rb')
message_list = pickle.load(infile)
infile.close()
role_list = []
infile = open(filename2,'rb')
role_list = pickle.load(infile)
infile.close()
intents = discord.Intents().all()
client = discord.Client(intents=intents)
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)
bot = commands.Bot(command_prefix='!',intents=intents,help_command=help_command)
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.1):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename
@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    print('joining')
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")
@bot.command(name='play_song', help='To play song')
async def play(ctx,url):
    try :
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('**Now playing:** {}'.format(filename))
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
@bot.event
async def on_ready():
    print('working')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your every move"))
@bot.command(name='addquote', help='Adds a quote to the list')
async def addquote(ctx):
    print('addquote working')
    if ctx.message.author == client.user:
        return
    else:
        global message_list
        await ctx.message.channel.send('Added quote: '+ctx.message.content.partition(' ')[2]+'.')
        message_list.append(ctx.message.content.partition(' ')[2])
        outfile = open(filename,'wb')
        pickle.dump(message_list,outfile)
        outfile.close()
        print (message_list)
@bot.command(name='clearquotes', help='Clears all quotes')
async def clearquotes(ctx):
    print('clearquotes working')
    if ctx.message.author == client.user:
        return
    else:
        global message_list
        message_list = []
        outfile = open(filename,'wb')
        pickle.dump(message_list,outfile)
        outfile.close()
        print ('quotes cleared')
        await ctx.message.channel.send('Quotes cleared')
@bot.command(name='givequote', help='Gives a random quote')
async def givequote(ctx):
    print('givequote working')
    if ctx.message.author == client.user:
        return
    else:
        global message_list
        quote_message = random.choice(message_list)
        await ctx.message.channel.send(quote_message)
@bot.command(name='quotelist', help='Lists all quotes')
async def quotelist(ctx):
    print('quotelist working')
    if ctx.message.author == client.user:
        return
    else:
        global message_list
        if message_list == []:
            await ctx.message.channel.send('No quotes in list')
        else:
            quote_list = ', '.join(message_list)
            await ctx.message.channel.send(quote_list)
@bot.command(name='removequote', help='removes a specific quote')
async def removequote(ctx):
    print ('removequote working')
    if ctx.message.author == client.user:
        return
    else:
        global message_list
        messagedel = ctx.message.content.partition(' ')[2]
        message_list.remove(messagedel)
        outfile = open(filename,'wb')
        pickle.dump(message_list,outfile)
        outfile.close()
        await ctx.message.channel.send(f'Removed quote: {messagedel}')
@bot.command(name='gotrole', help='for bees, ignore')
async def gotrole(ctx,n):
    print('gotrole working')
    if ctx.message.author == client.user:
        return
    else:
         await ctx.message.channel.send(f'Got role: {n}')
         global role_list
         n = int(n)
         role_list[n-1]=role_list[n-1]+1
         print(role_list)
         outfile = open(filename2,'wb')
         pickle.dump(role_list,outfile)
         outfile.close()
         await ctx.message.channel.send(f'Role count:\nTop: {role_list[0]}\nJg: {role_list[1]}\n'+
                                        f'Mid: {role_list[2]}\nBot: {role_list[3]}\nSupp: {role_list[4]}')
@bot.command(name='clearroles', help='for bees, ignore',cog_name='test')
async def clearroles(ctx):
    print('clearroles working')
    if ctx.message.author == client.user:
        return
    else:
        global role_list
        role_list=[0, 0, 0, 0, 0]
        outfile = open(filename2,'wb')
        pickle.dump(role_list,outfile)
        outfile.close()
        await ctx.message.channel.send('Roles cleared')
        print(role_list)

@bot.command(name='champart', help='gives splash art for a champion skin, e.g. Aatrox_0')
async def champart(ctx,art):
    print('champart working')
    if ctx.message.author == client.user:
        return
    else:
        await ctx.message.channel.send(f'http://ddragon.leagueoflegends.com/cdn/img/champion/splash/{art}.jpg')

@bot.command(name='leaguerank', help='gets League ranked info')
async def leaguerank(ctx,name):
    print('leaguerank working')
    if ctx.message.author == client.user:
        return
    else:
        user_me = watcher.summoner.by_name('na1', name)
        user_ranked_stats = watcher.league.by_summoner('na1', user_me['id'])
        print(user_ranked_stats)
        await ctx.message.channel.send(f'Ranked stats for {name}:\nTier: {user_ranked_stats[0]["tier"]}'+
                                       f' {user_ranked_stats[0]["rank"]}\nLP: {user_ranked_stats[0]["leaguePoints"]}\n'+
                                       f'Wins: {user_ranked_stats[0]["wins"]}\nLosses: {user_ranked_stats[0]["losses"]}\n'+
                                       f'Win/Loss Ratio: {user_ranked_stats[0]["wins"]/(user_ranked_stats[0]["losses"]+user_ranked_stats[0]["wins"])*100}%')

#This part isn't funcitonal yet, just know it uses the match api
#my_matches = watcher.match.matchlist_by_puuid('americas', me['puuid'])
#last_match = my_matches[0]
#match_detail = watcher.match.by_id('americas', last_match)
#participants = []

#for row in match_detail['metadata']:
    #participants_row = {}
    #print(metadata['participants'])
    #participants_row['champion'] = row['championId']
    #print(participants_row)
    #participants_row['spell1'] = row['spell1Id']
    #participants_row['spell2'] = row['spell2Id']
    #participants_row['win'] = row['stats']['win']
    #participants_row['kills'] = row['stats']['kills']
    #participants_row['deaths'] = row['stats']['deaths']
    #participants_row['assists'] = row['stats']['assists']
    #participants_row['totalDamageDealt'] = row['stats']['totalDamageDealt']
    #participants_row['goldEarned'] = row['stats']['goldEarned']
    #participants_row['champLevel'] = row['stats']['champLevel']
    #participants_row['totalMinionsKilled'] = row['stats']['totalMinionsKilled']
    #participants_row['item0'] = row['stats']['item0']
    #participants_row['item1'] = row['stats']['item1']
    #participants.append(participants_row)
#df = pd.DataFrame(participants)
#df
bot.run(TOKEN)

