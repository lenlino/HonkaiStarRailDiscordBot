import os

import aiohttp

from generate.templates import one, two
from generate.utils import conn

font_file_path = f"{os.path.dirname(os.path.abspath(__file__))}/assets/zh-cn.ttf"
be_address = os.environ.get("BE_ADDRESS", "https://hcs.lenlino.com")


async def generate_panel(uid="805477392", chara_id=1, template=1, is_hideUID=False, calculating_standard="compatibility", lang="jp", is_hide_roll=False):
    result_json = {}
    async with aiohttp.ClientSession(connector_owner=False, connector=conn) as session:
        async with session.get(f"{be_address}/gen_card/{uid}?lang={lang}&select_number={chara_id}&calculation_value={calculating_standard}"
                               f"&is_uid_hide={is_hideUID}&is_hide_roll={is_hide_roll}") as response:

            if response.status == 200:
                result_json["img"] = await response.read()
                #print(response.headers)
                result_json["header"] = {"score": response.headers.get("x-score"), "top_score": response.headers.get("x-top-score"),
                                         "before_score": response.headers.get("x-before-score"), "median": response.headers.get("x-median"),
                                         "mean": response.headers.get("x-mean"), "rank": response.headers.get("x-rank"),
                                         "data_count": response.headers.get("x-data-count")}
                return result_json
            else:
                result_json["detail"] = response.status
                return result_json

    if template == 1:
        return await one.generate_panel(uid=uid, chara_id=chara_id, is_hideUID=is_hideUID, calculating_standard=calculating_standard)
    elif template == 2:
        return await two.generate_panel(uid=uid, chara_id=chara_id, is_hideUID=is_hideUID, calculating_standard=calculating_standard, lang=lang, is_hide_roll=is_hide_roll)


