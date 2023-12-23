import io
import os

import asyncpg as asyncpg
import discord
import discord.ext.commands.cog
from discord.ext import tasks
from dotenv import load_dotenv

import backend.backend
import i18n

i18n.load_path.append(f"{os.path.dirname(os.path.abspath(__file__))}/i18n")
i18n.set('fallback', 'en')

load_dotenv()

import utils.DataBase

bot = discord.AutoShardedBot()
token = os.environ.get('HONKAI_TOKEN')


async def init_bot():
    await utils.DataBase.init()
    status_update_task.start()
    os.chdir('generate')
    os.system("git clone --filter=blob:none --no-checkout https://github.com/Mar-7th/StarRailRes.git")
    os.chdir('StarRailRes')
    os.system("git sparse-checkout set index_min")
    os.system("git checkout")


@bot.event
async def on_ready():
    await init_bot()
    print("起動しました")
    # await generate_panel()


@tasks.loop(minutes=10)
async def status_update_task():
    text = f"Servers: {str(len(bot.guilds))}"
    await bot.change_presence(activity=discord.CustomActivity(text))


bot.load_extension('commands.CardCommand')
bot.run(token)
