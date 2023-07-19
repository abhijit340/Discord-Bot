# bot.py
import os
import meteostat
import discord
import random
import matplotlib.pyplot as plt 
import pandas as pd
import pyimgur
import numpy as np
import seaborn as sns

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
    dailyPrecip = round(dataD.prcp.values[0]/25.4, 1)
    hourlyPrecip = dataH.prcp.values
    hourlyTemp = list((dataH.temp.values*1.8)+32)
    #hours = list(range(0,24))
    hours = ['12AM', '1AM', '2AM', '3AM', '4AM', '5AM', '6AM', '7AM', '8AM', '9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '3PM', '4PM', '5PM', '6PM', '7PM', '8PM', '9PM', '10PM', '11PM']

    #create graph of temp from 6am to 11pm
    #07Price command here from refenc on how to imbed https://github.com/ChattyRS/RuneClock/blob/master/cogs/runescape.py#L341 

    
    print(hourlyTemp)
    weatherTxt = f'Daily High: {dailyHigh}F\nDaily Low: {dailyLow}F\nPrecipitation : {dailyPrecip}in'


    #seaborn implemenation
    

    hourlyTempData = pd.DataFrame(hourlyTemp[6:],hours[6:])
    sns.set_style('darkgrid')
    sns.set_context('talk')
    
    fig = sns.lineplot(data=hourlyTempData, legend=False)

    tLine = fig.lines[0]
    x1 = tLine.get_xydata()[:,0]
    y1 = tLine.get_xydata()[:,1]
    fig.fill_between(x1,y1, color="blue", alpha=0.2)
    ychartMax = max(y1)+5
    ychartMin = min(y1)-5
    fig.set_ylim(ychartMin,ychartMax)
    
    # only display exvery other x-label
    for xL, axis in enumerate(fig.get_xticklabels()):
        if xL % 3 == 0:  # every 4th label is kept
            axis.set_visible(True)
        else:
            axis.set_visible(False)
    

    
    plt.ylabel('Temp (F)')
    plt.title(' Hourly Temp Forecast')
    
    
    plt.savefig('images/hourTemps.png', transparent=False)
    plt.close

    tempFile = discord.File('images/hourTemps.png' , filename='DailyTemps.png')
    embed= discord.Embed()
    embed.set_image(url='attachment://DailyTemps.png')
    


    await ctx.send(weatherTxt)
    await ctx.send( embed=embed, file=tempFile)





bot.run(TOKEN)
