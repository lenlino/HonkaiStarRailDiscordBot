import io
import json
import os
import pathlib

import aiohttp
from PIL import Image


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

def get_file_path():
    return os.path.dirname(os.path.abspath(__file__))


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


async def get_relic_score(chara_id, relic_json):
    # load
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/weight.json") as f:
        weight_json = json.load(f)
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/max.json") as f:
        max_json = json.load(f)
    with open(f"{os.path.dirname(os.path.abspath(__file__))}/relic_id.json") as f:
        relic_id_json = json.load(f)
    result_json = {}

    # メインの計算
    main_weight = weight_json[chara_id]["main"][relic_id_json.get(relic_json["id"], relic_json["id"])[-1]][relic_json["main_affix"]["type"]]
    main_affix_score = (relic_json["level"] + 1) / 16 * main_weight
    result_json["main_formula"] = f'{round((relic_json["level"] + 1) / 16*100, 1)}×{main_weight}={main_affix_score*100}'


    # サブの計算
    sub_affix_score = 0
    sub_affix_formulas = []
    for sub_affix_json in relic_json["sub_affix"]:
        sub_affix_type = sub_affix_json["type"]
        score = sub_affix_json["value"] / max_json[sub_affix_type] * weight_json[chara_id]["weight"][sub_affix_type]
        sub_affix_score += score
        sub_affix_formulas.append(f'{round(sub_affix_json["value"]/max_json[sub_affix_type]*100, 1)}×{round(weight_json[chara_id]["weight"][sub_affix_type],1)}')

    result_json["score"] = main_affix_score * 0.5 + sub_affix_score * 0.5
    result_json["sub_formulas"] = sub_affix_formulas

    # 合計
    return result_json


def get_relic_score_color(score):
    if score <= 19:
        return "#888c91"
    elif 20 <= score <= 39:
        return "#428c88"
    elif 40 <= score <= 59:
        return "#4c88c8"
    elif 60 <= score <= 79:
        return "#a068d8"
    elif 80 <= score:
        return "#d2ad72"


def get_relic_score_text(score):
    if score < 20:
        return "D"
    elif 20 <= score < 40:
        return "C"
    elif 40 <= score < 60:
        return "B"
    elif 60 <= score < 80:
        return "A"
    elif 80 <= score < 100:
        return "S"
    elif 100 <= score:
        return "SS"

def get_relic_full_score_text(score):
    if score < 120:
        return "D"
    elif 120 <= score < 240:
        return "C"
    elif 240 <= score < 360:
        return "B"
    elif 360 <= score < 480:
        return "A"
    elif 480 <= score < 600:
        return "S"
    elif 600 <= score:
        return "SS"
