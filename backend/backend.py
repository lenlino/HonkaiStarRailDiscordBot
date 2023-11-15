import io

from fastapi import APIRouter
from starlette.responses import StreamingResponse

import generate.generate

router = APIRouter()


@router.get("/gen_card/{uid}")
async def gen_card(uid: str, select_number: int, is_uid_hide: bool, calculation_value: str, lang: str):
    image_binary = io.BytesIO()
    panel_img = await generate.generate.generate_panel(uid=uid, chara_id=int(select_number), template=2,
                                                       is_hideUID=is_uid_hide
                                                       , calculating_standard=calculation_value, lang=lang)
    panel_img['img'].save(image_binary, 'PNG')
    image_binary.seek(0)
    print(image_binary)
    return StreamingResponse(content=image_binary, media_type="image/png")
