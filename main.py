import io
import json
import os

import asyncpg as asyncpg
import discord
import discord.ext.commands.cog
from discord.ext import tasks
from dotenv import load_dotenv

import backend.backend
import generate.utils
import i18n

i18n.load_path.append(f"{os.path.dirname(os.path.abspath(__file__))}/i18n")
i18n.set('fallback', 'en')

load_dotenv()

import utils.DataBase

bot = discord.AutoShardedBot()
token = os.environ.get('HONKAI_TOKEN')
characters = []
characters_name = {}


async def init_bot():
    await utils.DataBase.init()
    status_update_task.start()
    os.chdir(f"{os.path.dirname(os.path.abspath(__file__))}/generate")
    os.system("git clone --filter=blob:none --no-checkout https://github.com/Mar-7th/StarRailRes.git")
    os.chdir('StarRailRes')
    os.system("git sparse-checkout set index_min")
    os.system("git checkout")

    with open(f"{os.path.dirname(os.path.abspath(__file__))}/generate/StarRailRes/index_min/jp/characters.json",
              encoding="utf-8") as f:
        chara_json = json.load(f)
        characters.clear()
        for key, value in chara_json.items():
            name = value["name"]
            if key == "8001":
                name = "主人公・壊滅・物理"
            elif key == "8003":
                name = "主人公・存護・炎"
            elif key == "8005":
                name = "主人公・調和・虚数"
            elif int(key) > 8000:
                continue
            characters.append(discord.OptionChoice(name=name, value=key))
            characters_name[key] = name


@bot.event
async def on_ready():
    await init_bot()
    print("起動しました")
    # await generate_panel()


@tasks.loop(minutes=10)
async def status_update_task():
    text = f"Servers: {str(len(bot.guilds))}"
    await bot.change_presence(activity=discord.CustomActivity(text))
    await generate.utils.clear_weight_dict()


bot.load_extension('commands.CardCommand')
bot.load_extension('commands.CreateWeightCommand')
bot.run(token)
