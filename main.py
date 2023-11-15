import asyncio
import os

import discord
import discord.ext.commands.cog
from discord.ext import tasks
from dotenv import load_dotenv
from fastapi import FastAPI

import i18n
from backend.backend import router

i18n.load_path.append(f"{os.path.dirname(os.path.abspath(__file__))}/i18n")
i18n.set('fallback', 'en')

load_dotenv()

# dotenv読み込んでからimport
import utils.DataBase

bot = discord.AutoShardedBot()
token = os.environ.get('HONKAI_TOKEN')

#app = FastAPI()
#app.include_router(router)


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
    text = f"Servers: {str(len(bot.guilds))}"
    await bot.change_presence(activity=discord.CustomActivity(text))


async def run():
    await bot.start(token)


bot.load_extension('commands.CardCommand')
#asyncio.create_task(run())
