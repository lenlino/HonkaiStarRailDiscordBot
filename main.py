import io
import os

import asyncpg as asyncpg
import discord
import discord.ext.commands.cog

from commands import CardCommand
from generate.generate import get_json_from_url, generate_panel

bot = discord.AutoShardedBot()
token = os.environ.get('HONKAI_TOKEN')

DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASS = os.getenv("DB_PASS", "maikura123")


async def init_bot():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASS, database=DB_NAME, host=DB_HOST)
    await conn.execute('CREATE TABLE IF NOT EXISTS voice(id char(20), uid char(4));')
    await conn.close()





@bot.event
async def on_ready():

    print("起動しました")
    # await generate_panel()

bot.load_extension('commands.CardCommand')
bot.run(token)
