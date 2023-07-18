# bot.py
import os
import meteostat
import discord
import random

from dotenv import load_dotenv

from datetime import datetime, date
from meteostat import Hourly, Daily
from discord.ext import commands



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_SERVER')


intents=discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix= '!', intents=intents)

"""

intents=discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

"""

@bot.event
async def on_ready():
    #ready message
    print(f'{bot.user} has connected to Discord!')
    server = discord.utils.get(bot.guilds, name=SERVER)

    print(
        f'{bot.user} is connected to the following servers:\n'
        f'{server.name} (id: {server.id})'
    )

"""
@bot.event
async def on_message(message):
    #early yesy message
    if message.author == client.user:
        return  
    if message.content == 'test':
        response = 'echo'
        await message.channel.send(response)
    elif message.content =='raise-exception':
        raise discord.DiscordException


@bot.event
async def on_error(event, *args, **kwargs):
    #error testing
    with open('err.log', 'a') as f:
        if event =='on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

"""

@bot.command(name = 'hello', help='just syas hi back to you')
async def respond(ctx):
    """ dummy response """
    response = 'hi there!'
    await ctx.send(response)

@bot.command (name='roll_dice', help='Simulates dice roll, needs two args # dice and # sides on dice, ex: !roll dice 3, 6 - rolls 3 six sided dice')
async def roll (ctx, num_d:int, sides_d:int):
    dice = [
        str(random.choice(range(1, sides_d +1)))
        for _ in range(num_d)

    ]
    await ctx.send(', '.join(dice))

@bot.command(name = 'weather', help= ' gives daily weather info')
async def weather(ctx):
    
    #get current date
    today = str(date.today())

    #need to parse to get day and month
    year= int(today[0:4])
    month = int(today[5:7])
    day = int(today[8:])

    # Set time period for daily
    start_d = datetime(year, month, day)
    end_d = datetime(year, month, day)

    # Get daily data
    dataD = Daily('72219', start_d, end_d)
    dataD = dataD.fetch()

    # Set time period for hourly
    start_h = datetime(year, month, day)
    end_h = datetime(year, month, day, 23, 59)

    # Get hourly data
    dataH = Hourly('72219', start_h, end_h)
    dataH = dataH.fetch()

    # Print DataFrame
    print(dataD)

    
    #parse data, get columon values for data of concern
    dailyHigh = int(round(((dataD.tmax.values[0])*1.8)+32, 0))
    dailyLow = int(round(((dataD.tmin.values[0])*1.8)+32, 0))
    


    weatherTxt = f'Daily High: {dailyHigh}F Daily Low: {dailyLow}F'

    await ctx.send(weatherTxt)



bot.run(TOKEN)
