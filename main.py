import io

import aiohttp
import discord
from PIL import Image

bot = discord.AutoShardedBot()


@bot.slash_command(description="読み上げを開始・終了するのだ", guilds=["864441028866080768"])
async def panel(ctx):
    await ctx.defer()
    await generate_panel()
    embed = discord.Embed(
        title="崩壊スターレイル",
        color=discord.Colour.dark_blue(),
        description="満員で入れないのだ。",
    )
    #embed.set_image(url="https://api.mihomo.me/panel/resources/bkg.png")
    await ctx.send_followup(embed=embed)


async def generate_panel():
    img = Image.open(await get_image_from_url("https://api.mihomo.me/panel/resources/bkg.png"))
    img = img.rotate(90, expand=True)
    chara_img = Image.open(await get_image_from_url("https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/image/character_portrait/1013.png")).resize((img.width // 2, img.height))
    img.paste(chara_img, (0,0), chara_img)
    img.show()


async def get_image_from_url(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return io.BytesIO(await response.content.read())


bot.run('token')
