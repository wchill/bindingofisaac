import xml.etree.ElementTree as ET
from typing import List, Optional

from isaac_pickups import PICKUP_LIST


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
    def convert_pickup_list_to_int64(pickups: List[str]) -> int:
        assert len(pickups) == 8
        sorted_array = sorted(pickups, reverse=True)
        accumulator = 0
        for num in sorted_array:
            accumulator <<= 8
            accumulator |= num

        return accumulator


def find_hardcoded_recipe(pickups: List[str]) -> Optional[HardcodedRecipe]:
    pickup_num = HardcodedRecipe.convert_pickup_list_to_int64(pickups)
    return HARDCODED_RECIPES.get(pickup_num)


with open("recipes.xml", "r") as f:
    recipes = ET.fromstring(f.read())
    assert recipes.tag == "recipes"

    for recipe in recipes:
        recipe_entry = HardcodedRecipe(
            int(recipe.attrib["output"]), recipe.attrib["input"]
        )
        HARDCODED_RECIPES[recipe_entry.pickup_num] = recipe_entry
