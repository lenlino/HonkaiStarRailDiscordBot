import datetime
import json
import os

import aiohttp
import discord
import discord.ext.commands.cog
from discord.ext import tasks
from dotenv import load_dotenv

import generate.utils
import i18n

i18n.load_path.append(f"{os.path.dirname(os.path.abspath(__file__))}/i18n")
i18n.set('fallback', 'en')

load_dotenv()

import utils.DataBase

bot = discord.AutoShardedBot()
token = os.environ.get('HONKAI_TOKEN')
be_address = os.environ.get('BE_ADDRESS', "https://hcs.lenlino.com")
emoji_guild_id = os.environ.get('EMOJI_GUILD_ID', "1118740618882072596,864441028866080768")
resource_url = "https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/"
characters = []
characters_name = {}


async def init_bot():
    await utils.DataBase.init()
    status_update_task.start()
    regi_weight_task.start()


async def git_task():
    os.chdir(f"{os.path.dirname(os.path.abspath(__file__))}/generate")
    os.system("git clone --filter=blob:none --no-checkout https://github.com/Mar-7th/StarRailRes.git")
    os.chdir('StarRailRes')
    os.system("git sparse-checkout set index_min")
    os.system("git checkout")
    os.system("git pull")


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


@tasks.loop(hours=24)
async def regi_weight_task():
    await git_task()
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
            elif key == "1224":
                name = "三月なのか・巡狩・虚数"
            elif int(key) > 8000:
                continue

            characters.append(discord.OptionChoice(name=f"{name}({key})", value=key))
            characters_name[key] = f"{name}({key})"

    channel = bot.get_channel(1242779790914752592)
    async for mes in channel.history(before=(datetime.datetime.now() + datetime.timedelta(days=-3))):
        if len(mes.attachments) == 0:
            continue

        weight_json = json.loads(await mes.attachments[0].read())
        embed = mes.embeds[0]
        embed_title = embed.title
        embed_desc = embed.description
        reactions = mes.reactions

        print(f"{embed_title} {embed_desc}")

        if weight_json["lang"]["en"] != "" and weight_json["lang"]["en"] != "string":
            chara_id = f"{mes.attachments[0].filename.replace('.json', '')}_{weight_json['lang']['en']}"
        else:
            chara_id = f"{mes.attachments[0].filename.replace('.json', '')}"

        if embed_desc == "追加申請":
            if embed_title.endswith("(投票中)"):
                print("kiku")
                if reactions[0].count >= reactions[1].count:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(f"{be_address}/weight/"
                                                f"{chara_id}"
                            , json=weight_json) as response:
                            print(await response.text())
                    if chara_id.startswith("8"):
                        async with aiohttp.ClientSession() as session:
                            async with session.post(f"{be_address}/weight/"
                                                    f"{chara_id.replace(mes.attachments[0].filename.replace('.json', ''), str(int(chara_id) + 1))}"
                                , json=weight_json) as response:
                                print(await response.text())
                    embed.title = embed_title.replace("(投票中)", "(承認済)")
                    embed.colour = discord.Colour.brand_green()
                else:
                    embed.title = embed_title.replace("(投票中)", "(非承認)")
                    embed.colour = discord.Colour.brand_red()
                await mes.edit(embed=embed)
        elif embed_desc == "修正申請":
            if embed_title.endswith("(投票中)"):
                if reactions[0].count >= reactions[1].count:
                    async with aiohttp.ClientSession() as session:
                        async with session.put(f"{be_address}/weight/{chara_id}"
                            , json=weight_json) as response:
                            print(await response.text())
                    if chara_id.startswith("8"):
                        async with aiohttp.ClientSession() as session:
                            async with session.put(f"{be_address}/weight/"
                                                   f"{chara_id.replace(mes.attachments[0].filename.replace('.json', ''), str(int(chara_id) + 1))}"
                                , json=weight_json) as response:
                                print(await response.text())
                    embed.title = embed_title.replace("(投票中)", "(承認済)")
                    embed.colour = discord.Colour.brand_green()
                else:
                    embed.title = embed_title.replace("(投票中)", "(非承認)")
                    embed.colour = discord.Colour.brand_red()
                await mes.edit(embed=embed)


bot.load_extension('commands.CardCommand')
bot.load_extension('commands.CreateWeightCommand')
bot.load_extension('commands.ChangeWeightCommand')
bot.run(token)
