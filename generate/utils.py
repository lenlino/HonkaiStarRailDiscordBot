import io
import json
import os
import pathlib
import pandas as pd

import aiohttp
from PIL import Image
from starrailres import Index
from starrailres.models.info import CharacterBasicInfo, LevelInfo, LightConeBasicInfo, SubAffixBasicInfo, RelicBasicInfo


conn = aiohttp.TCPConnector(limit_per_host=1)
be_address = os.environ.get('BE_ADDRESS', "https://hcs.lenlino.com")


async def get_image_from_url(url: str):
    replaced_path = url.replace("https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/", "")
    if url.startswith("https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/") and os.path.exists(
        f"{os.path.dirname(os.path.abspath(__file__))}/{replaced_path}"):
        return f"{os.path.dirname(os.path.abspath(__file__))}/{replaced_path}"
    print(f"{os.path.dirname(os.path.abspath(__file__))}/{replaced_path}")
    filepath = pathlib.Path(f"{os.path.dirname(os.path.abspath(__file__))}/{replaced_path}")
    filepath.parent.mkdir(parents=True, exist_ok=True)
    async with aiohttp.ClientSession(connector_owner=False, connector=conn) as session:
        async with session.get(url) as response:
            Image.open(io.BytesIO(await response.content.read())).save(filepath, quality=95)
            return f"{os.path.dirname(os.path.abspath(__file__))}/{replaced_path}"


async def get_json_from_urlpath(path: str):
    async with aiohttp.ClientSession(connector_owner=False, connector=conn) as session:
        async with session.get(f"{be_address}{path}") as response:
            if response.status == 200:
                result_json = await response.json()
                return result_json
            return None


async def get_json_from_url(uid: str, lang: str):
    result_json = {}
    async with aiohttp.ClientSession(connector_owner=False, connector=conn) as session:
        async with session.get(f"{be_address}/sr_info_parsed/{uid}?lang={lang}") as response:
            if response.status == 200:
                result_json = await response.json()
    if len(result_json.keys()) == 0 or "detail" in result_json:
        filepath = pathlib.Path(f"{os.path.dirname(os.path.abspath(__file__))}/StarRailRes/index_min/{lang}")
        index = Index(filepath)
        async with aiohttp.ClientSession(connector_owner=False, connector=conn) as session:
            async with session.get(f"https://enka.network/api/hsr/uid/{uid}") as response:
                if response.status != 200:
                    result_json["detail"] = response.status
                    return result_json
                enka_result_json = await response.json()
                detail_info_json = enka_result_json["detailInfo"]
                record_info_json = detail_info_json["recordInfo"]
                result_json = {
                    "player": {
                        "uid": enka_result_json["uid"],
                        "nickname": detail_info_json["nickname"],
                        "level": detail_info_json["level"],
                        "world_level": detail_info_json["worldLevel"],
                        "friend_count": detail_info_json["friendCount"],
                        "avatar": index.get_avatar_info(detail_info_json["headIcon"]),
                        "signature": detail_info_json.get("signature", ""),
                        "is_display": detail_info_json["isDisplayAvatar"],
                        "space_info": {
                            "memory_data": {
                                "level": record_info_json.get("scheduleMaxLevel", 0),
                                "chaos_id": 0,
                                "chaos_level": 0
                            },
                            "universe_level": record_info_json["maxRogueChallengeScore"],
                            "challenge_data": {
                                "maze_group_id": 0,
                                "maze_group_index": 0,
                                "pre_maze_group_index": record_info_json.get("scheduleMaxLevel", 0)
                            },
                            "pass_area_progress": record_info_json["maxRogueChallengeScore"],
                            "light_cone_count": record_info_json["equipmentCount"],
                            "avatar_count": record_info_json["avatarCount"],
                            "achievement_count": record_info_json["achievementCount"]
                        }
                    }
                }
                characters_list = []
                for characters in detail_info_json["avatarDetailList"]:
                    skill_list = []
                    for skilltree in characters["skillTreeList"]:
                        skill_list.append(LevelInfo(id=str(skilltree["pointId"]), level=int(skilltree["level"])))

                    if "equipment" in characters:
                        equipment = characters["equipment"]
                        basic_light_cone = LightConeBasicInfo(id=str(equipment["tid"]), rank=int(equipment["rank"]),
                                                              level=int(equipment["level"]),
                                                              promotion=equipment["promotion"])
                    else:
                        basic_light_cone = None

                    basic_relics = []
                    for relic in characters["relicList"]:
                        subaffix_list = []
                        for subaffix in relic["subAffixList"]:
                            subaffix_list.append(
                                SubAffixBasicInfo(id=str(subaffix["affixId"]), cnt=subaffix.get("cnt", 0),
                                                  step=subaffix.get("step", 0)))
                        basic_relics.append(RelicBasicInfo(
                            id=str(relic["tid"]),
                            level=relic["level"],
                            main_affix_id=str(relic["mainAffixId"]),
                            sub_affix_info=subaffix_list,
                        ))
                    charabase_json = index.get_character_info(CharacterBasicInfo(
                        id=str(characters["avatarId"]),
                        rank=characters.get("rank", 0),
                        level=characters["level"],
                        promotion=characters["promotion"],
                        skill_tree_levels=skill_list,
                        light_cone=basic_light_cone,
                        relics=basic_relics,
                    ))
                    if charabase_json:
                        from msgspec import to_builtins
                        characters_list.append(to_builtins(charabase_json))
                result_json["characters"] = characters_list
    return result_json


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
    main_weight = weight_json[chara_id]["main"][relic_id_json.get(relic_json["id"], relic_json["id"])[-1]][
        relic_json["main_affix"]["type"]]
    main_affix_score = (relic_json["level"] + 1) / 16 * main_weight
    result_json[
        "main_formula"] = f'{round((relic_json["level"] + 1) / 16 * 100, 1)}×{main_weight}={main_affix_score * 100}'

    # サブの計算
    sub_affix_score = 0
    sub_affix_formulas = []
    for sub_affix_json in relic_json["sub_affix"]:
        sub_affix_type = sub_affix_json["type"]
        # print(f"{weight_json[chara_id]['weight'][sub_affix_type]}/{sub_affix_type}")
        # print(f"{weight_json[chara_id]['weight']}")
        score = (sub_affix_json["value"] / max_json[sub_affix_type]) * weight_json[chara_id]["weight"][sub_affix_type]
        sub_affix_score += score
        sub_affix_formulas.append(
            f'{round(sub_affix_json["value"] / max_json[sub_affix_type] * 100, 1)}×{round(weight_json[chara_id]["weight"][sub_affix_type], 1)}')

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
    elif 100 <= score < 120:
        return "SS"
    elif 120 <= score:
        return "OP"


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
    elif 600 <= score < 720:
        return "SS"
    elif 720 <= score:
        return "OP"


def get_mihomo_lang(discord_lang):
    if discord_lang == "id":
        return "id"
    elif discord_lang == "fr":
        return "fr"
    elif discord_lang == "de":
        return "de"
    elif discord_lang == "es-ES":
        return "es"
    elif discord_lang == "ja":
        return "jp"
    elif discord_lang == "ko":
        return "kr"
    elif discord_lang == "pt-BR":
        return "pt"
    elif discord_lang == "ru":
        return "ru"
    elif discord_lang == "th":
        return "th"
    elif discord_lang == "vi":
        return "vi"
    elif discord_lang == "zh-TW":
        return "cht"
    elif discord_lang == "zh-CN":
        return "cn"
    else:
        return "en"


weight_dict = {}


async def clear_weight_dict():
    weight_dict.clear()


async def get_weight(chara_id):
    """with open(f"{os.path.dirname(os.path.abspath(__file__))}/weight.json") as f:
        weight_json = json.load(f)"""

    if str(chara_id) in weight_dict:
        return weight_dict[str(chara_id)]["weight"]
    else:
        weight_dict[str(chara_id)] = await get_json_from_urlpath(f"/weight/{chara_id}")
        return await get_weight(chara_id)


async def get_weight_list(chara_id):
    """with open(f"{os.path.dirname(os.path.abspath(__file__))}/weight.json") as f:
        weight_json = json.load(f)"""

    return await get_json_from_urlpath(f"/weight_list/{chara_id}")


def get_score_rank(chara_id, uid, score):
    json_path = f"{os.path.dirname(os.path.abspath(__file__))}/scores/{chara_id}.json"
    result = {}
    if os.path.exists(json_path):
        df = pd.read_json(json_path, orient='columns')
    else:
        df = pd.DataFrame({"score": {}, "rank": {}})
    uid = str(uid) + 'u'
    before_score = df["score"].get(uid, 0)
    df.loc[uid] = [score, 0]
    df['rank'] = df['score'].rank(ascending=False, method='min')
    if before_score > score:
        df["score"][uid] = before_score
        result['top_score'] = round(before_score, 1)
    else:
        result['top_score'] = round(score, 1)

    df.to_json(json_path)

    result["before_score"] = before_score
    result['median'] = round(df.median()['score'], 1)
    result['mean'] = round(df.mean()['score'], 1)
    result['rank'] = int(round(df['rank'].get(uid, 1), 0))
    result['data_count'] = len(df)

    return result
