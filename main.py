import io
import os
import pathlib

import aiohttp
import asyncpg as asyncpg
import discord
from PIL import Image, ImageDraw, ImageFont

bot = discord.AutoShardedBot()
token = os.environ.get('HONKAI_TOKEN')
font_file_path = "assets/zh-cn.ttf"
DB_HOST = 'localhost'
DB_PORT = '5433'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASS = os.getenv("DB_PASS", "maikura123")


async def init_bot():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASS, database=DB_NAME, host=DB_HOST)
    await conn.execute('CREATE TABLE IF NOT EXISTS voice(id char(20), uid char(4));')
    await conn.close()


class View(discord.ui.View):
    pass


class Select(discord.ui.Select):
    pass


class Button(discord.ui.Button):
    pass


class Modal(discord.ui.Modal):
    pass


@bot.slash_command(description="読み上げを開始・終了するのだ", guilds=["864441028866080768"])
async def panel(ctx, uid: discord.Option(required=False, input_type=int, description="UID")):
    await ctx.defer()
    selecter = Select()
    generate_button = Button()
    uid_change_button = Button()
    select_number = 0

    async def selector_callback(interaction):
        try:
            await interaction.response.send_message("")
        except discord.errors.HTTPException:
            pass

    async def button_callback(interaction):
        await interaction.response.defer()
        if selecter.options[0].label == "UID未設定":
            await interaction.followup.send("UIDが設定されていません。")
            return
        with io.BytesIO() as image_binary:
            generate_button.label = "生成中..."
            generate_button.disabled = True
            print(uid)
            await ctx.edit(view=View(selecter, generate_button, uid_change_button))
            panel_img = await generate_panel(uid=uid, chara_id=int(selecter.values[0]))
            nonlocal select_number
            select_number = int(selecter.values[0])
            panel_img.save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.followup.send(file=discord.File(image_binary, "panel.png"))
            generate_button.label = "パネル生成"
            generate_button.disabled = False
            await set_uid(uid)

    async def uid_change_button_callback(interaction):
        modal = Modal(title="UID変更")
        modal.add_item(discord.ui.InputText(label="UID"))

        async def uid_change_modal_callback(modal_interaction):
            await modal_interaction.response.defer()
            await set_uid(modal.children[0].value)

        modal.callback = uid_change_modal_callback
        await interaction.response.send_modal(modal)

    async def set_uid(changed_uid):
        info = await get_json_from_url(f"https://api.mihomo.me/sr_info/{changed_uid}")
        if "detail" not in info:
            embed.description = f"ニックネーム: {info['detailInfo']['nickname']}\nUID: {info['detailInfo']['uid']}"
            nonlocal uid
            uid = info['detailInfo']['uid']
            json = await get_json_from_url(f"https://api.mihomo.me/sr_info_parsed/{uid}?lang=jp")
            selecter.options = []
            for index, i in enumerate(json["characters"]):
                selecter.append_option(
                    discord.SelectOption(label=i["name"], value=str(index), default=True if index == select_number else False))
            await ctx.edit(view=View(selecter, generate_button, uid_change_button))
        else:
            embed.description = "UIDが指定されていない、または存在しないUIDです。"

        await ctx.edit(embed=embed)


    selecter.callback = selector_callback
    selecter.options = [discord.SelectOption(label="UID未設定",default=True)]
    selecter.custom_id = "check_id"
    generate_button.label = "パネル生成"
    generate_button.callback = button_callback
    generate_button.row = 4
    generate_button.style = discord.ButtonStyle.primary
    uid_change_button.label = "UID変更"
    uid_change_button.callback = uid_change_button_callback
    uid_change_button.row = 4
    embed = discord.Embed(
        title="HSR パネル生成",
        color=discord.Colour.dark_blue(),
        description="読み込み中...",
    )

    await ctx.send_followup(embed=embed, view=View(selecter, generate_button, uid_change_button))
    await set_uid(uid)
    return


@bot.event
async def on_ready():
    print("起動しました")
    # await generate_panel()


async def generate_panel(uid="805477392", chara_id=1):
    font_color = "#f0eaca"
    touka_color = "#191919"
    json = await get_json_from_url(f"https://api.mihomo.me/sr_info_parsed/{uid}?lang=jp")
    helta_json = json["characters"][int(chara_id)]
    img = Image.open("assets/black.png").convert(
        'RGBA')
    color_code = helta_json["element"]["color"]
    a = Image.new('RGBA', (1920, 1080))
    draw_img = ImageDraw.Draw(a)
    draw_img.rectangle(
        ((0, 0), (1920, 1080)),
        fill=(int(color_code[1:3], 16), int(color_code[3:5], 16), int(color_code[5:7], 16), 200)
    )
    img = Image.alpha_composite(img, a)
    # img = img.rotate(90, expand=True)
    small_font = ImageFont.truetype(font_file_path, 18)
    normal_font = ImageFont.truetype(font_file_path, 24)
    title_font = ImageFont.truetype(font_file_path, 60)
    retic_title_font = ImageFont.truetype(font_file_path, 24)
    retic_title_small_font = ImageFont.truetype(font_file_path, 19)
    card_font = ImageFont.truetype(font_file_path, 36)

    draw = ImageDraw.Draw(img)

    # キャライメージ
    chara_img = Image.open(await get_image_from_url(
        f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{helta_json['portrait']}")).resize(
        (750, 750)).crop((150, 0, 550, 750))
    img.paste(chara_img, (50, 50), chara_img)
    draw.rounded_rectangle((50, 50, 450, 800), radius=10, fill=None,
                           outline=font_color, width=2)
    star_img = Image.open(await get_image_from_url(
        f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{get_star_image_path_from_int(int(helta_json['rarity']))}")).resize(
        (306, 72))
    img.paste(star_img, (210, 50), star_img)

    # キャラステータス
    for index, i in enumerate(helta_json["attributes"]):
        icon = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{i['icon']}")).resize(
            (55, 55))
        img.paste(icon, (500, 140 + index * 60), icon)
        draw.text((560, 155 + index * 60), f"{i['name']}", font_color, spacing=10, align='left', font=normal_font)
        draw.rounded_rectangle((490, 145 + index * 60, 1060, 155 + index * 60 + 36), radius=10, fill=None,
                               outline=font_color, width=2)
        if i["field"] != "crit_rate" and i["field"] != "crit_dmg":
            draw.text((1050, 150 + index * 60), f"{i['display']}", font_color, spacing=10, align='right',
                      font=small_font, anchor='ra')
            addition = get_json_from_json(helta_json["additions"], "field", i["field"])
            draw.text((1050, 150 + index * 60 + 18), f"+{addition.get('display', '0')}", "#9be802", spacing=10,
                      align='right',
                      font=small_font, anchor='ra')
            draw.text((1000, 155 + index * 60), f"{int(i['display']) + int(addition.get('display', '0'))}", font_color,
                      font=normal_font, anchor='ra')
        else:
            draw.text((1050, 155 + index * 60), f"{i['display']}", font_color, spacing=10, align='right',
                      font=normal_font, anchor='ra')
    show_count = 0
    for index, i in enumerate(helta_json["properties"]):
        if i["field"] != "def" and i["field"] != "crit_rate" and i["field"] != "atk" and i["field"] != "hp" and i[
            "field"] != "crit_dmg" and i["field"] != "spd":
            icon = Image.open(await get_image_from_url(
                f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{i['icon']}")).resize(
                (55, 55))
            draw.rounded_rectangle((490, 505 + show_count * 60, 1060, 515 + show_count * 60 + 36), radius=10, fill=None,
                                   outline=font_color, width=2)
            img.paste(icon, (500, 500 + show_count * 60), icon)
            draw.text((560, 515 + show_count * 60), f"{i['name']}", font_color, spacing=10, align='left',
                      font=normal_font)
            draw.text((1050, 515 + show_count * 60), f"{i['display']}", font_color, spacing=10, align='right',
                      font=normal_font, anchor='ra')
            show_count += 1

    # キャラタイトル
    draw.text((500, 50), helta_json['name'], "#f0eaca", spacing=10, align='left', font=title_font)
    icon = Image.open(await get_image_from_url(
        f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{helta_json['element']['icon']}")).resize(
        (55, 55))
    img.paste(icon, (500 + (len(helta_json['name'])) * 60, 70), icon)
    draw.text((500 + (len(helta_json['name'])) * 60 + 55, 90), f"Lv.{helta_json['level']}", font_color,
              font=normal_font)
    draw.line(((490, 135), (1060, 135)), fill=font_color, width=3)
    path_icon = Image.open(await get_image_from_url(
        f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{helta_json['path']['icon']}")).resize(
        (50, 50))
    img.paste(path_icon, (914, 80), path_icon)
    draw.text((964, 90), f"{helta_json['path']['name']}", font_color, font=normal_font)
    draw.rounded_rectangle((919, 82, 1014, 127), radius=10, fill=None,
                           outline=font_color, width=2)
    draw.text((1029, 90), f"{helta_json['promotion']}", font_color, font=normal_font)
    draw.rounded_rectangle((1019, 82, 1051, 127), radius=10, fill=None,
                           outline=font_color, width=2)

    # 聖遺物
    for index, i in enumerate(helta_json["relics"]):
        icon = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{i['icon']}")).resize(
            (100, 100))
        star_img = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{get_star_image_path_from_int(5)}")).resize(
            (153, 36))
        if index < 3:
            draw.rounded_rectangle((1100, 50 + index * 330, 1490, 365 + index * 330), radius=10, fill=None,
                                   outline=font_color, width=2)
            img.paste(icon, (1110, 60 + index * 330), icon)
            if len(i["name"]) > 11:
                draw.text((1220, 60 + index * 330), f"{i['name'][:11]}\n{i['name'][11:]}", font_color,
                          align='left',
                          font=retic_title_small_font)
            else:
                draw.text((1220, 70 + index * 330), f"{i['name']}", font_color, spacing=10, align='left',
                          font=retic_title_font)

            draw.text((1240, 110 + index * 330), f"{i['main_affix']['name']}\n{i['main_affix']['display']}", font_color,
                      font=retic_title_font)
            draw.rounded_rectangle((1187, 145 + index * 330, 1235, 173 + index * 330), radius=10, fill=None,
                                   outline=font_color, width=2)
            draw.text((1190, 145 + index * 330), f"+{i['level']}", font_color,
                      font=retic_title_font)
            img.paste(star_img, (1070, 145 + index * 330), star_img)
            for sub_index, sub_i in enumerate(i["sub_affix"]):
                draw.text((1110, 180 + index * 330 + sub_index * 50), f"{sub_i['name']}", font_color,
                          font=retic_title_font)
                draw.text((1480, 180 + index * 330 + sub_index * 50), f"{sub_i['display']}", font_color,
                          font=retic_title_font, anchor='ra')
        else:
            draw.rounded_rectangle((1500, 50 + (index - 3) * 330, 1890, 365 + (index - 3) * 330), radius=10, fill=None,
                                   outline=font_color, width=2)
            img.paste(icon, (1510, 60 + (index - 3) * 330), icon)
            if len(i["name"]) > 11:
                draw.text((1610, 60 + (index - 3) * 330), f"{i['name'][:11]}\n{i['name'][11:]}", font_color,
                          align='left',
                          font=retic_title_small_font)
            else:
                draw.text((1610, 70 + (index - 3) * 330), f"{i['name']}", font_color, spacing=10, align='left',
                          font=retic_title_font)

            draw.text((1640, 110 + (index - 3) * 330), f"{i['main_affix']['name']}\n{i['main_affix']['display']}",
                      font_color,
                      font=retic_title_font)
            draw.rounded_rectangle((1587, 145 + (index - 3) * 330, 1635, 173 + (index - 3) * 330), radius=10, fill=None,
                                   outline=font_color, width=2)
            draw.text((1590, 145 + (index - 3) * 330), f"+{i['level']}", font_color,
                      font=retic_title_font)
            img.paste(star_img, (1470, 145 + (index - 3) * 330), star_img)
            for sub_index, sub_i in enumerate(i["sub_affix"]):
                draw.text((1510, 180 + (index - 3) * 330 + sub_index * 50), f"{sub_i['name']}", font_color,
                          font=retic_title_font)
                draw.text((1870, 180 + (index - 3) * 330 + sub_index * 50), f"{sub_i['display']}", font_color,
                          font=retic_title_font, anchor='ra')

    # カード
    if helta_json.get("light_cone"):
        draw.rounded_rectangle((40, 840, 1050, 1000), radius=10, fill=None,
                               outline=font_color, width=2)
        card_img = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{helta_json['light_cone']['icon']}")).resize(
            (150, 150))
        card_star_img = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{get_star_image_path_from_int(int(helta_json['light_cone']['rarity']))}")).resize(
            (204, 48))
        img.paste(card_img, (50, 850), card_img)
        draw.text((600, 870), f"{helta_json['light_cone']['name']}", font_color,
                  font=card_font, anchor='ra')
        draw.line(((200, 860), (200, 980)), fill=font_color, width=1)
        img.paste(card_star_img, (600, 860), card_star_img)
        draw.text((600, 930), f"Lv.{helta_json['light_cone']['level']}", font_color,
                  font=card_font, anchor='ra')
        draw.text((650, 930), f"{convert_old_roman_from_int(int(helta_json['light_cone']['promotion']))}", font_color,
                  font=card_font, anchor='ra')

    # UID
    draw.text((50, 1010), f"UID: {json['player']['uid']}", font_color,
              font=normal_font)

    # スキルレベル
    a = Image.new('RGBA', (1920, 1080))
    draw_img = ImageDraw.Draw(a)
    draw_img.rectangle(
        ((50, 700), (450, 800)),
        fill=(25, 25, 25, 128)
    )
    img = Image.alpha_composite(img, a)
    draw = ImageDraw.Draw(img)
    for index, i in enumerate(helta_json["skills"]):
        skill_icon = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{i['icon']}")).resize(
            (45, 45))
        img.paste(skill_icon, (70 + index * 63, 722), skill_icon)
        draw.ellipse(((65 + index * 63, 715), (120 + index * 63, 770)), fill=None,
                     outline=font_color, width=3)
        draw.rounded_rectangle((73 + index * 63, 762, 112 + index * 63, 788), radius=10, fill="#ffffff",
                               outline="#ffffff", width=2)
        draw.text((85 + index * 63, 760), f"{i['level']}", "#000000",
                  font=normal_font)

    #img.save('lenna_square_pillow.png', quality=95)
    return img


async def get_image_from_url(url: str):
    replaced_path = url.replace("https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/","")
    if url.startswith("https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/") and os.path.exists(replaced_path):
        return replaced_path
    print(replaced_path)
    filepath = pathlib.Path(replaced_path)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            Image.open(io.BytesIO(await response.content.read())).save(filepath, quality=95)
            return replaced_path


async def get_json_from_url(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


def get_json_from_json(json_list, key, value):
    for i in json_list:
        if i[key] == value:
            return i
    return {}


def get_star_image_path_from_int(level: int):
    if level == 1:
        return "icon/deco/Rarity1.png"
    elif level == 2:
        return "icon/deco/Rarity2.png"
    elif level == 3:
        return "icon/deco/Rarity3.png"
    elif level == 4:
        return "icon/deco/Rarity4.png"
    elif level == 5:
        return "icon/deco/Rarity5.png"


def convert_old_roman_from_int(n):
    r = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    if n < 1 or 10 < n:
        return ''
    return r[n - 1]


bot.run(token)
