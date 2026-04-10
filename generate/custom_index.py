import json
from pathlib import Path
from typing import Type, TypeVar

from msgspec.json import decode
from starrailres import Index as OriginalIndex
from starrailres.models.characters import (
    CharacterIndex,
    CharacterRankIndex,
    CharacterSkillIndex,
    CharacterSkillTreeIndex,
    CharacterPromotionIndex,
)
from starrailres.models.light_cones import (
    LightConeIndex,
    LightConePromotionIndex,
    LightConeRankIndex,
)
from starrailres.models.relics import (
    RelicIndex,
    RelicSetIndex,
    RelicMainAffixIndex,
    RelicSubAffixIndex,
)
from starrailres.models.paths import PathIndex
from starrailres.models.elements import ElementIndex
from starrailres.models.properties import PropertyIndex
from starrailres.models.avatars import AvatarIndex

T = TypeVar("T")

def custom_decode_json(path: Path, t: Type[T]) -> T:
    """
    Custom decode_json function that handles:
    1. null values for max_sp in characters.json
    2. missing guide_overview field in relic_sets.json
    """
    if not path.exists():
        raise FileNotFoundError(path)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    data = json.loads(content)

    for entry in data.values():
        if isinstance(entry, dict):
            # null値の文字列フィールドを空文字に変換
            for key, val in entry.items():
                if val is None:
                    entry[key] = ""
            # max_spはfloat型なので修正
            if "max_sp" in entry and entry["max_sp"] == "":
                entry["max_sp"] = 0.0
            # guide_overviewはList[str]型
            if "guide_overview" in entry:
                if isinstance(entry["guide_overview"], str):
                    entry["guide_overview"] = [entry["guide_overview"]] if entry["guide_overview"] else []

    return decode(json.dumps(data), type=t)

class CustomIndex(OriginalIndex):
    """
    Custom Index class that uses custom_decode_json to handle:
    1. null values for max_sp in characters.json
    2. missing guide_overview field in relic_sets.json
    """
    def __init__(self, folder: Path) -> None:
        if not folder.exists():
            raise Exception("Please select an existing index folder!")

        # Use custom_decode_json instead of decode_json
        self.characters = custom_decode_json(folder / "characters.json", CharacterIndex)

        self.character_ranks = custom_decode_json(
            folder / "character_ranks.json", CharacterRankIndex
        )
        self.character_skills = custom_decode_json(
            folder / "character_skills.json", CharacterSkillIndex
        )
        self.character_skill_trees = custom_decode_json(
            folder / "character_skill_trees.json", CharacterSkillTreeIndex
        )
        self.character_promotions = custom_decode_json(
            folder / "character_promotions.json", CharacterPromotionIndex
        )
        self.light_cones = custom_decode_json(folder / "light_cones.json", LightConeIndex)
        self.light_cone_ranks = custom_decode_json(
            folder / "light_cone_ranks.json", LightConeRankIndex
        )
        self.light_cone_promotions = custom_decode_json(
            folder / "light_cone_promotions.json", LightConePromotionIndex
        )
        self.relics = custom_decode_json(folder / "relics.json", RelicIndex)
        self.relic_sets = custom_decode_json(folder / "relic_sets.json", RelicSetIndex)
        self.relic_main_affixes = custom_decode_json(
            folder / "relic_main_affixes.json", RelicMainAffixIndex
        )
        self.relic_sub_affixes = custom_decode_json(
            folder / "relic_sub_affixes.json", RelicSubAffixIndex
        )
        self.paths = custom_decode_json(folder / "paths.json", PathIndex)
        self.elements = custom_decode_json(folder / "elements.json", ElementIndex)
        self.properties = custom_decode_json(folder / "properties.json", PropertyIndex)
        self.avatars = custom_decode_json(folder / "avatars.json", AvatarIndex)
