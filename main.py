import io
import os

import asyncpg as asyncpg
import discord
import discord.ext.commands.cog
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()

import utils.DataBase

bot = discord.AutoShardedBot()
token = os.environ.get('HONKAI_TOKEN')


async def init_bot():
    await utils.DataBase.init()
    status_update_task.start()


@bot.event
async def on_ready():
    await init_bot()
    print("起動しました")
    # await generate_panel()


@tasks.loop(minutes=10)
async def status_update_task():
    text = f"正常稼働中　Servers: {str(len(bot.guilds))}"
    await bot.change_presence(activity=discord.CustomActivity(text))


bot.load_extension('commands.CardCommand')
bot.run(token)
