import io
import os

import asyncpg as asyncpg
import discord
import discord.ext.commands.cog
from dotenv import load_dotenv

import utils.DataBase
from commands import CardCommand
from generate.generate import get_json_from_url, generate_panel
from utils.DataBase import get_connection

load_dotenv()
bot = discord.AutoShardedBot()
token = os.environ.get('HONKAI_TOKEN')


async def init_bot():
    await utils.DataBase.init()


@bot.event
async def on_ready():
    await init_bot()
    print("起動しました")
    # await generate_panel()


bot.load_extension('commands.CardCommand')
bot.run(token)
