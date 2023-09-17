import io
import json
import math
import os
import pathlib

import aiohttp
from PIL import ImageDraw, Image, ImageFont

from generate.templates import one, two

font_file_path = f"{os.path.dirname(os.path.abspath(__file__))}/assets/zh-cn.ttf"


async def generate_panel(uid="805477392", chara_id=1, template=1, is_hideUID=False):
    if template == 1:
        return await one.generate_panel(uid=uid, chara_id=chara_id, is_hideUID=is_hideUID)
    elif template == 2:
        return await two.generate_panel(uid=uid, chara_id=chara_id, is_hideUID=is_hideUID)


