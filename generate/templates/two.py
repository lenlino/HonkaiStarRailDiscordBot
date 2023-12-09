import io
import json
import math
import os
import pathlib
import textwrap

import aiohttp
import i18n
from PIL import ImageDraw, Image, ImageFont

from generate.utils import get_json_from_url, get_json_from_json, get_image_from_url, get_relic_score_text, \
    get_star_image_path_from_int, convert_old_roman_from_int, get_relic_score, get_file_path, get_relic_full_score_text

font_file_path = f"{get_file_path()}/assets/zh-cn.ttf"


async def generate_panel(uid="805477392", chara_id=1, is_hideUID=False, calculating_standard="compatibility", lang="jp"):
    font_color = "#f0eaca"
    touka_color = "#191919"
    json = await get_json_from_url(f"https://api.mihomo.me/sr_info_parsed/{uid}?lang={lang}")
    if lang == "jp" or lang == "cn" or lang == "cht":
        light_cone_name_limit = 9
        chara_name_limit = 5
        relic_main_affix_name_limit = 6
    else:
        light_cone_name_limit = 18
        chara_name_limit = 18
        relic_main_affix_name_limit = 10
    helta_json = json["characters"][int(chara_id)]
    img = Image.open(f"{get_file_path()}/assets/bkg.png").convert(
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
    skill_level_font = ImageFont.truetype(font_file_path, 25)
    normal_font = ImageFont.truetype(font_file_path, 30)
    title_font = ImageFont.truetype(font_file_path, 60)
    retic_title_font = ImageFont.truetype(font_file_path, 25)
    retic_main_affix_title_font = ImageFont.truetype(font_file_path, 27)
    retic_main_affix_title_small_font = ImageFont.truetype(font_file_path, 25)
    retic_formula_font = ImageFont.truetype(font_file_path, 18)
    card_font = ImageFont.truetype(font_file_path, 36)

    draw = ImageDraw.Draw(img)

    # キャライメージ
    chara_img = Image.open(await get_image_from_url(
        f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{helta_json['portrait']}")).resize(
        (750, 750)).crop((150, 0, 550, 750))
    img.paste(chara_img, (50, 50), chara_img)
    draw.rounded_rectangle((50, 50, 450, 800), radius=2, fill=None,
                           outline=font_color, width=1)
    star_img = Image.open(await get_image_from_url(
        f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{get_star_image_path_from_int(int(helta_json['rarity']))}")).resize(
        (306, 72))
    img.paste(star_img, (210, 50), star_img)
    draw.text((315, 105), f"Lv.{helta_json['level']}", font_color,
              font=normal_font)
    icon = Image.open(await get_image_from_url(
        f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{helta_json['element']['icon']}")).resize(
        (40, 40))
    img.paste(icon, (400, 100), icon)

    # キャラステータス
    for index, i in enumerate(helta_json["attributes"]):
        icon = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{i['icon']}")).resize(
            (55, 55))
        img.paste(icon, (500, 140 + index * 60), icon)
        draw.text((560, 150 + index * 60), f"{i['name']}", font_color, spacing=10, align='left', font=normal_font)
        draw.rounded_rectangle((490, 145 + index * 60, 1060, 155 + index * 60 + 36), radius=2, fill=None,
                               outline=font_color, width=1)
        if i["field"] != "crit_rate" and i["field"] != "crit_dmg":
            draw.text((1050, 150 + index * 60), f"{i['display']}", font_color, spacing=10, align='right',
                      font=small_font, anchor='ra')
            addition = get_json_from_json(helta_json["additions"], "field", i["field"])
            draw.text((1050, 150 + index * 60 + 18), f"+{addition.get('display', '0')}", "#9be802", spacing=10,
                      align='right',
                      font=small_font, anchor='ra')
            draw.text((980, 150 + index * 60), f"{int(i['display']) + int(addition.get('display', '0'))}", font_color,
                      font=normal_font, anchor='ra')
        else:
            draw.text((1050, 150 + index * 60), f"{i['display']}", font_color, spacing=10, align='right',
                      font=small_font, anchor='ra')
            addition = get_json_from_json(helta_json["additions"], "field", i["field"])
            draw.text((1050, 150 + index * 60 + 18), f"+{addition.get('display', '0')}", "#9be802", spacing=10,
                      align='right',
                      font=small_font, anchor='ra')
            draw.text((980, 150 + index * 60), f"{math.floor((float(i['value']) + float(addition.get('value', '0')))*1000)/10}%", font_color,
                      font=normal_font, anchor='ra')
    show_count = 0
    for index, i in enumerate(helta_json["properties"]):
        if i["field"] == "sp_rate":
            i["display"] = str(round((i["value"] + 1) * 100, 1))+"%"
        if i["field"] != "def" and i["field"] != "crit_rate" and i["field"] != "atk" and i["field"] != "hp" and i[
            "field"] != "crit_dmg" and i["field"] != "spd":
            icon = Image.open(await get_image_from_url(
                f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{i['icon']}")).resize(
                (55, 55))
            draw.rounded_rectangle((490, 505 + show_count * 60, 1060, 515 + show_count * 60 + 36), radius=2, fill=None,
                                   outline=font_color, width=1)
            img.paste(icon, (500, 500 + show_count * 60), icon)
            draw.text((560, 510 + show_count * 60), f"{i['name']}", font_color, spacing=10, align='left',
                      font=normal_font)
            draw.text((1050, 510 + show_count * 60), f"{i['display']}", font_color, spacing=10, align='right',
                      font=normal_font, anchor='ra')
            show_count += 1

    # キャラタイトル
    draw.multiline_text((500, 140), '\n'.join(textwrap.wrap(helta_json['name'], chara_name_limit)), "#f0eaca", anchor="ld", font=title_font)


    draw.line(((490, 135), (1060, 135)), fill=font_color, width=3)
    path_icon = Image.open(await get_image_from_url(
        f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{helta_json['path']['icon']}")).resize(
        (50, 50))
    img.paste(path_icon, (960, 80), path_icon)
    draw.text((1035, 105), f"{helta_json['rank']}", font_color, font=normal_font, anchor="mm")
    draw.rounded_rectangle((1020, 82, 1050, 127), radius=2, fill=None,
                           outline=font_color, width=2)
    relic_full_score = 0
    # 遺物
    for index, i in enumerate(helta_json["relics"]):
        icon = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{i['icon']}")).resize(
            (100, 100))
        star_img = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{get_star_image_path_from_int(i['rarity'])}")).resize(
            (153, 36))
        main_attribute_icon = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{i['main_affix']['icon']}")).resize(
            (42, 42))
        relic_score_json = await get_relic_score(helta_json["id"], i)
        relic_score = round(relic_score_json["score"] * 100, 1)
        relic_full_score += relic_score
        relic_main_affix_name = '\n'.join(textwrap.wrap(i['main_affix']['name'], relic_main_affix_name_limit))
        if index < 3:
            draw.rounded_rectangle((1100, 50 + index * 330, 1490, 365 + index * 330), radius=2, fill=None,
                                   outline=font_color, width=1)
            img.paste(icon, (1110, 60 + index * 330), icon)

            img.paste(main_attribute_icon, (1200, 62 + index * 330), main_attribute_icon)
            draw.text((1240, 100 + index * 330), f"{relic_main_affix_name}\n{i['main_affix']['display']}", font_color,
                      font=retic_main_affix_title_font, anchor="lm")

            draw.rounded_rectangle((1195, 145 + index * 330, 1245, 173 + index * 330), radius=2, fill=None,
                                   outline=font_color, width=2)
            draw.text((1220, 160 + index * 330), f"+{i['level']}", font_color,
                      font=retic_title_font, anchor="mm")

            # スコア
            if calculating_standard != "no_score":
                draw.text((1440, 135 + index * 330), f"{relic_score}", font_color,
                      font=retic_title_font, anchor="mm")
                draw.text((1440, 95 + index * 330), f"{get_relic_score_text(relic_score)}", font_color,
                      font=title_font, anchor="mm")

            img.paste(star_img, (1075, 140 + index * 330), star_img)
            for sub_index, sub_i in enumerate(i["sub_affix"]):
                sub_affix_icon = Image.open(await get_image_from_url(
                f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{sub_i['icon']}")).resize(
                (40, 40))
                img.paste(sub_affix_icon, (1100, 175 + index * 330 + sub_index * 50), sub_affix_icon)
                draw.text((1140, 180 + index * 330 + sub_index * 50), f"{sub_i['name']}", font_color,
                          font=retic_title_font)
                draw.text((1480, 180 + index * 330 + sub_index * 50), f"{sub_i['display']}", font_color,
                          font=retic_title_font, anchor='ra')
                if calculating_standard != "no_score":
                    draw.text((1480, 165 + index * 330 + sub_index * 50), f"{relic_score_json['sub_formulas'][sub_index]}",
                          "#808080", font=retic_formula_font, anchor='ra')
        else:
            draw.rounded_rectangle((1500, 50 + (index - 3) * 330, 1890, 365 + (index - 3) * 330), radius=2, fill=None,
                                   outline=font_color, width=1)
            img.paste(icon, (1510, 60 + (index - 3) * 330), icon)

            img.paste(main_attribute_icon, (1600, 62 + (index - 3) * 330), main_attribute_icon)
            draw.text((1640, 100 + (index - 3) * 330), f"{relic_main_affix_name}\n{i['main_affix']['display']}",
                      font_color, font=retic_main_affix_title_font, anchor="lm")

            draw.rounded_rectangle((1595, 145 + (index - 3) * 330, 1645, 173 + (index - 3) * 330), radius=2, fill=None,
                                   outline=font_color, width=2)
            draw.text((1620, 160 + (index - 3) * 330), f"+{i['level']}", font_color,
                      font=retic_title_font, anchor="mm")

            # スコア
            if calculating_standard != "no_score":
                draw.text((1840, 135 + (index - 3) * 330), f"{relic_score}", font_color,
                      font=retic_title_font, anchor="mm")
                draw.text((1840, 95 + (index - 3) * 330), f"{get_relic_score_text(relic_score)}", font_color,
                      font=title_font, anchor="mm")

            img.paste(star_img, (1475, 145 + (index - 3) * 330), star_img)
            for sub_index, sub_i in enumerate(i["sub_affix"]):
                sub_affix_icon = Image.open(await get_image_from_url(
                    f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{sub_i['icon']}")).resize(
                    (40, 40))
                img.paste(sub_affix_icon, (1500, 175 + (index - 3) * 330 + sub_index * 50), sub_affix_icon)
                draw.text((1540, 180 + (index - 3) * 330 + sub_index * 50), f"{sub_i['name']}", font_color,
                          font=retic_title_font)
                draw.text((1880, 180 + (index - 3) * 330 + sub_index * 50), f"{sub_i['display']}", font_color,
                          font=retic_title_font, anchor='ra')
                if calculating_standard != "no_score":
                    draw.text((1880, 165 + (index - 3) * 330 + sub_index * 50), f"{relic_score_json['sub_formulas'][sub_index]}",
                          "#808080", font=retic_formula_font, anchor='ra')

    #relic合計スコアor遺物組み合わせ
    draw.rounded_rectangle((50, 840, 450, 1000), radius=2, fill=None,
                           outline=font_color, width=1)
    if calculating_standard != "no_score":
        draw.text((80, 870), f"{i18n.t('message.score', locale=lang)}{round(relic_full_score, 1)}", font_color,
                  font=card_font)
        draw.text((380, 920), f"{get_relic_full_score_text(relic_full_score)}", font_color,
                  font=title_font, anchor="mm")
        draw.text((80, 930), i18n.t('message.compatibility_criteria', locale=lang), font_color,
                  font=card_font)
    else:
        for sets_index, sets in enumerate(helta_json["relic_sets"]):
            draw.text((80, 865+sets_index*40), f"{sets['num']} - {sets['name']}", font_color,
                  font=retic_main_affix_title_font)


    # カード
    if helta_json.get("light_cone"):
        draw.rounded_rectangle((490, 840, 1060, 1000), radius=2, fill=None,
                               outline=font_color, width=1)
        card_img = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{helta_json['light_cone']['icon']}")).resize(
            (160, 150))
        card_star_img = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{get_star_image_path_from_int(int(helta_json['light_cone']['rarity']))}")).resize(
            (214, 48))
        img.paste(card_img, (500, 840), card_img)
        draw.multiline_text((700, 890), '\n'.join(textwrap.wrap(helta_json['light_cone']['name'], light_cone_name_limit)), font_color,
                  font=card_font, anchor="lm")
        draw.line(((680, 860), (680, 980)), fill=font_color, width=1)
        img.paste(card_star_img, (460, 950), card_star_img)
        draw.text((705, 930), f"Lv.{helta_json['light_cone']['level']}", font_color,
                  font=card_font)
        draw.text((830, 930), f"{convert_old_roman_from_int(int(helta_json['light_cone']['rank']))}", font_color,
                  font=card_font)

    # UID
    if is_hideUID is not True:
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
    skill_index = 0
    used_ultra = False
    used_normal = False
    for index, i in enumerate(helta_json["skills"]):
        if skill_index >= 5:
            break
        if i["max_level"] == 1 and i["type"] != "Maze":
            continue
        if i["type"] == "Ultra":
            if used_ultra:
                continue
            used_ultra = True
        elif i["type"] == "Normal":
            if used_normal:
                continue
            used_normal = True
        skill_icon = Image.open(await get_image_from_url(
            f"https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/{i['icon']}")).resize(
            (45, 45))
        img.paste(skill_icon, (70 + skill_index * 78, 722), skill_icon)
        draw.ellipse(((65 + skill_index * 78, 715), (120 + skill_index * 78, 770)), fill=None,
                     outline=font_color, width=3)
        draw.rounded_rectangle((73 + skill_index * 78, 762, 112 + skill_index * 78, 788), radius=4, fill="#ffffff")
        draw.text((93 + skill_index * 78, 775), f"{i['level']}", "#000000",
                  font=skill_level_font, align="center", anchor="mm")
        skill_index += 1

    result = {}
    result['img'] = img.resize((img.width // 2, img.height // 2))
    result['score'] = relic_full_score
    result['chara_name'] = helta_json['name']
    # img.save('lenna_square_pillow.png', quality=95)
    return result
