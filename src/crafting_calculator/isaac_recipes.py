import xml.etree.ElementTree as ET
from functools import lru_cache
from typing import Dict, List, Optional

from .utilities import get_gamedata_path
from .isaac_pickups import PICKUP_LIST


pickup_shorthand_to_id_mapping = {
    e.shorthand_name: e.pickup_id
    for e in PICKUP_LIST
    if e is not None and e.shorthand_name is not None
}


HARDCODED_RECIPES = {}


class HardcodedRecipe:
    def __init__(self, item_id: int, input_pickups: str):
        self.item_id = item_id
        self.pickups = [pickup_shorthand_to_id_mapping[ch] for ch in input_pickups]
        self.pickup_num = self.convert_pickup_list_to_int64(self.pickups)

    @staticmethod
    def convert_pickup_list_to_int64(pickups: List[int]) -> int:
        assert len(pickups) == 8
        sorted_array = sorted(pickups, reverse=True)
        accumulator = 0
        for num in sorted_array:
            accumulator <<= 8
            accumulator |= num

        return accumulator

    @staticmethod
    @lru_cache()
    def load_hardcoded_recipes(game_version: str) -> Dict[int, "HardcodedRecipe"]:
        recipes_xml_path = get_gamedata_path(game_version, "recipes.xml")
        output = {}

        with open(recipes_xml_path, "r", encoding="utf-8") as f:
            recipes = ET.fromstring(f.read())
            assert recipes.tag == "recipes"

            for recipe in recipes:
                recipe_entry = HardcodedRecipe(
                    int(recipe.attrib["output"]), recipe.attrib["input"]
                )
                output[recipe_entry.pickup_num] = recipe_entry

        return output


def find_hardcoded_recipe(
    game_version: str, pickups: List[int]
) -> Optional[HardcodedRecipe]:
    pickup_num = HardcodedRecipe.convert_pickup_list_to_int64(pickups)
    recipes = HardcodedRecipe.load_hardcoded_recipes(game_version)
    return recipes.get(pickup_num)
