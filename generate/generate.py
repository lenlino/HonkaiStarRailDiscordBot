import io
import os
import pathlib

import aiohttp
from PIL import ImageDraw, Image, ImageFont

font_file_path = f"{os.path.dirname(os.path.abspath(__file__))}/assets/zh-cn.ttf"


async def generate_panel(uid="805477392", chara_id=1):
    font_color = "#f0eaca"
    touka_color = "#191919"
    json = await get_json_from_url(f"https://api.mihomo.me/sr_info_parsed/{uid}?lang=jp")
    helta_json = json["characters"][int(chara_id)]
    img = Image.open(f"{os.path.dirname(os.path.abspath(__file__))}/assets/bkg.png").convert(
        'RGBA')
    color_code = helta_json["element"]["color"]
    a = Image.new('RGBA', (1920, 1080))
    draw_img = ImageDraw.Draw(a)
    draw_img.rectangle(
        ((0, 0), (1920, 1080)),
        fill=(int(color_code[1:3], 16), int(color_code[3:5], 16), int(color_code[5:7], 16), 100)
    )
    img = Image.alpha_composite(img, a)
    # img = img.rotate(90, expand=True)
    small_font = ImageFont.truetype(font_file_path, 18)
    normal_font = ImageFont.truetype(font_file_path, 30)
    title_font = ImageFont.truetype(font_file_path, 60)
    retic_title_font = ImageFont.truetype(font_file_path, 25)
    retic_title_small_font = ImageFont.truetype(font_file_path, 19)
    card_font = ImageFont.truetype(font_file_path, 36)

    draw = ImageDraw.Draw(img)

    # キャライメージ
    chara_img = Image.open(await get_image_from_url(
        f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{helta_json['portrait']}")).resize(
        (750, 750)).crop((150, 0, 550, 750))
    img.paste(chara_img, (50, 50), chara_img)
    draw.rounded_rectangle((50, 50, 450, 800), radius=2, fill=None,
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
        draw.text((560, 150 + index * 60), f"{i['name']}", font_color, spacing=10, align='left', font=normal_font)
        draw.rounded_rectangle((490, 145 + index * 60, 1060, 155 + index * 60 + 36), radius=2, fill=None,
                               outline=font_color, width=2)
        if i["field"] != "crit_rate" and i["field"] != "crit_dmg":
            draw.text((1050, 150 + index * 60), f"{i['display']}", font_color, spacing=10, align='right',
                      font=small_font, anchor='ra')
            addition = get_json_from_json(helta_json["additions"], "field", i["field"])
            draw.text((1050, 150 + index * 60 + 18), f"+{addition.get('display', '0')}", "#9be802", spacing=10,
                      align='right',
                      font=small_font, anchor='ra')
            draw.text((1000, 150 + index * 60), f"{int(i['display']) + int(addition.get('display', '0'))}", font_color,
                      font=normal_font, anchor='ra')
        else:
            draw.text((1050, 150 + index * 60), f"{i['display']}", font_color, spacing=10, align='right',
                      font=normal_font, anchor='ra')
    show_count = 0
    for index, i in enumerate(helta_json["properties"]):
        if i["field"] != "def" and i["field"] != "crit_rate" and i["field"] != "atk" and i["field"] != "hp" and i[
            "field"] != "crit_dmg" and i["field"] != "spd":
            icon = Image.open(await get_image_from_url(
                f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{i['icon']}")).resize(
                (55, 55))
            draw.rounded_rectangle((490, 505 + show_count * 60, 1060, 515 + show_count * 60 + 36), radius=2, fill=None,
                                   outline=font_color, width=2)
            img.paste(icon, (500, 500 + show_count * 60), icon)
            draw.text((560, 510 + show_count * 60), f"{i['name']}", font_color, spacing=10, align='left',
                      font=normal_font)
            draw.text((1050, 510 + show_count * 60), f"{i['display']}", font_color, spacing=10, align='right',
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
    draw.rounded_rectangle((919, 82, 1014, 127), radius=2, fill=None,
                           outline=font_color, width=2)
    draw.text((1029, 90), f"{helta_json['promotion']}", font_color, font=normal_font)
    draw.rounded_rectangle((1019, 82, 1051, 127), radius=2, fill=None,
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
            draw.rounded_rectangle((1100, 50 + index * 330, 1490, 365 + index * 330), radius=2, fill=None,
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
            draw.rounded_rectangle((1187, 145 + index * 330, 1235, 173 + index * 330), radius=2, fill=None,
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
            draw.rounded_rectangle((1500, 50 + (index - 3) * 330, 1890, 365 + (index - 3) * 330), radius=2, fill=None,
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
            draw.rounded_rectangle((1587, 145 + (index - 3) * 330, 1635, 173 + (index - 3) * 330), radius=2, fill=None,
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
        draw.rounded_rectangle((50, 840, 1050, 1000), radius=2, fill=None,
                               outline=font_color, width=2)
        card_img = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{helta_json['light_cone']['icon']}")).resize(
            (160, 150))
        card_star_img = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{get_star_image_path_from_int(int(helta_json['light_cone']['rarity']))}")).resize(
            (214, 48))
        img.paste(card_img, (60, 840), card_img)
        draw.text((610, 870), f"{helta_json['light_cone']['name']}", font_color,
                  font=card_font, anchor='ra')
        draw.line(((220, 860), (220, 980)), fill=font_color, width=1)
        img.paste(card_star_img, (610, 860), card_star_img)
        draw.text((610, 930), f"Lv.{helta_json['light_cone']['level']}", font_color,
                  font=card_font, anchor='ra')
        draw.text((660, 930), f"{convert_old_roman_from_int(int(helta_json['light_cone']['promotion']))}", font_color,
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
        draw.rounded_rectangle((73 + index * 63, 762, 112 + index * 63, 788), radius=2, fill="#ffffff",
                               outline="#ffffff", width=2)
        draw.text((85 + index * 63, 760), f"{i['level']}", "#000000",
                  font=normal_font)

    # img.save('lenna_square_pillow.png', quality=95)
    return img


async def get_image_from_url(url: str):
    replaced_path = url.replace("https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/", "")
    if url.startswith("https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/") and os.path.exists(
        f"{os.path.dirname(os.path.abspath(__file__))}/{replaced_path}"):
        return f"{os.path.dirname(os.path.abspath(__file__))}/{replaced_path}"
    print(f"{os.path.dirname(os.path.abspath(__file__))}/{replaced_path}")
    filepath = pathlib.Path(f"{os.path.dirname(os.path.abspath(__file__))}/{replaced_path}")
    filepath.parent.mkdir(parents=True, exist_ok=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            Image.open(io.BytesIO(await response.content.read())).save(filepath, quality=95)
            return f"{os.path.dirname(os.path.abspath(__file__))}/{replaced_path}"


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
