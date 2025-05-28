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

        # If this is the characters.json file and we're decoding to CharacterIndex
        if path.name == "characters.json" and t == CharacterIndex:
            # Parse the JSON manually first
            data = json.loads(content)

            # Replace null max_sp values with a default value (0.0)
            for character in data.values():
                if "max_sp" in character and character["max_sp"] is None:
                    character["max_sp"] = 0.0

            # Convert back to JSON string
            content = json.dumps(data)

        # If this is the relic_sets.json file and we're decoding to RelicSetIndex
        elif path.name == "relic_sets.json" and t == RelicSetIndex:
            # Parse the JSON manually first
            data = json.loads(content)

            # Add missing guide_overview field with an empty string as default value
            for relic_set in data.values():
                if "guide_overview" not in relic_set:
                    relic_set["guide_overview"] = ""

            # Convert back to JSON string
            content = json.dumps(data)

        # Use msgspec to decode with the specified type
        return decode(content, type=t)

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

        # Use the original decode_json for the rest
        from starrailres.utils import decode_json
        self.character_ranks = decode_json(
            folder / "character_ranks.json", CharacterRankIndex
        )
        self.character_skills = decode_json(
            folder / "character_skills.json", CharacterSkillIndex
        )
        self.character_skill_trees = decode_json(
            folder / "character_skill_trees.json", CharacterSkillTreeIndex
        )
        self.character_promotions = decode_json(
            folder / "character_promotions.json", CharacterPromotionIndex
        )
        self.light_cones = decode_json(folder / "light_cones.json", LightConeIndex)
        self.light_cone_ranks = decode_json(
            folder / "light_cone_ranks.json", LightConeRankIndex
        )
        self.light_cone_promotions = decode_json(
            folder / "light_cone_promotions.json", LightConePromotionIndex
        )
        self.relics = decode_json(folder / "relics.json", RelicIndex)
        self.relic_sets = custom_decode_json(folder / "relic_sets.json", RelicSetIndex)
        self.relic_main_affixes = decode_json(
            folder / "relic_main_affixes.json", RelicMainAffixIndex
        )
        self.relic_sub_affixes = decode_json(
            folder / "relic_sub_affixes.json", RelicSubAffixIndex
        )
        self.paths = decode_json(folder / "paths.json", PathIndex)
        self.elements = decode_json(folder / "elements.json", ElementIndex)
        self.properties = decode_json(folder / "properties.json", PropertyIndex)
        self.avatars = decode_json(folder / "avatars.json", AvatarIndex)
