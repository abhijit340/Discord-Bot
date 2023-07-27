# bot.py
import os
import math
import meteostat
import discord
import random
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
import seaborn as sns


#async scheduler so it does not block other events
import apscheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from dotenv import load_dotenv

from datetime import datetime, date
from meteostat import Hourly, Daily
from discord.ext import commands



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_SERVER')
GEN_CHANNEL = 1130641026713927743

GEN_CTX = 0


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

@bot.command(name = 'init', help='get intial ctx')
async def respond(ctx):
    """ dummy response """
    GEN_CTX = ctx
    response = 'initailized'
    await ctx.send(response)

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

    if math.isnan(dailyPrecip):
        dailyPrecip = 0
    
    hourlyPrecip = list((dataH.prcp.values/25.4).round(decimals=1))
    hourlyTemp = list((dataH.temp.values*1.8)+32)
    #hours = list(range(0,24))
    hours = ['12AM', '1AM', '2AM', '3AM', '4AM', '5AM', '6AM', '7AM', '8AM', '9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '3PM', '4PM', '5PM', '6PM', '7PM', '8PM', '9PM', '10PM', '11PM']


    #create graph of temp from 6am to 11pm
    print(hourlyPrecip)
    weatherTxt = f'Daily High/Low: {dailyHigh}F\/{dailyLow}F\nPrecipitation : {dailyPrecip}in'


    #seaborn charing implemenation
    

    hourlyTempData = pd.DataFrame(hourlyTemp[6:],hours[6:])
    hourlyPrecipData = pd.DataFrame(hourlyPrecip[6:],hours[6:])
    sns.set_context('talk')
    #sns.axes_style(rc={'text.color': 'white'})
    
    sns.set_style('darkgrid')
    
    fig, ax1 = plt.subplots()
    sns.lineplot(data=hourlyTempData, ax =ax1)
    ax1.get_legend().remove()
    

    

    tLine = ax1.lines[0]
    x1 = tLine.get_xydata()[:,0]
    y1 = tLine.get_xydata()[:,1]
    ax1.fill_between(x1,y1, color="blue", alpha=0.2)
    ychartMax = max(y1)+5
    ychartMin = min(y1)-5
    ax1.set_ylim(ychartMin,ychartMax)

    

    
    # only display exvery other x-label
    for xL, axis in enumerate(ax1.get_xticklabels()):
        if xL % 3 == 0:  # every 4th label is kept
            axis.set_visible(True)
        else:
            
            axis.set_visible(False)
    

    
    plt.ylabel('Temp (F)', fontdict={'color':'black'})
    plt.title(' Hourly Temp Forecast', fontdict={'color':'black'})
    

    
    
    plt.savefig('images/hourTemps.png', transparent=False)

    tempFile = discord.File('images/hourTemps.png' , filename='DailyTemps.png')
    embed= discord.Embed()
    embed.set_image(url='attachment://DailyTemps.png')
    plt.close()
    

    await ctx.send(weatherTxt)
    await ctx.send(embed=embed, file=tempFile)

    fig, ax1 = plt.subplots()
    sns.barplot( x = hours[6:] ,y = hourlyPrecip[6:])

    for xL, axis in enumerate(ax1.get_xticklabels()):
        if xL % 3 == 0:  # every 4th label is kept
            axis.set_visible(True)
        else:
            
            axis.set_visible(False)


    #sns.get_legend().remove()
    
    """
    for xL, axis in enumerate(ax1.get_xticklabels()):
        if xL % 3 == 0:  # every 4th label is kept
            axis.set_visible(True)
        else:
            
            axis.set_visible(False)
    """
    
    plt.ylabel('Precip (In.)', fontdict={'color':'black'})
    plt.title(' Hourly Precip Forecast', fontdict={'color':'black'})

    fig.savefig('images/hourPrecip.png', transparent=False)
    tempFile2 = discord.File('images/hourPrecip.png' , filename='DailyPrecip.png')
    embed2= discord.Embed()
    embed2.set_image(url='attachment://DailyPrecip.png')

    if dailyPrecip != 0:
        await ctx.send(embed=embed2, file=tempFile2)

    

 
async def func():
    await bot.wait_until_ready()

    await  GEN_CTX.invoke(self.bot.get_command('weather'))

@bot.event
async def on_ready():
    print("Ready")
    c = bot.get_channel(GEN_CHANNEL)
    await c.send('Please use command !init to set up bot')

    #initializing scheduler
    scheduler = AsyncIOScheduler()

    #sends "Your Message" at 12PM and 18PM (Local Time)
    scheduler.add_job(func, CronTrigger(hour="02", minute="57", second="0")) 
    print("Ready 3")
    #starting the scheduler
    scheduler.start()


bot.run(TOKEN)
