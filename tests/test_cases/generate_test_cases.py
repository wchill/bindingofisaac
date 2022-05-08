from typing import List, Optional, Union
import json
import random
from crafting_calculator.isaac_items import ItemListEntry
from crafting_calculator.isaac_pickups import PICKUP_LIST
from crafting_calculator.isaac_rng import string_to_seed
from crafting_calculator.utilities import DEFAULT_GAME_VERSION, DEFAULT_PLATFORM
from crafting_calculator.isaac_recipes import HardcodedRecipe
from static_test_cases import STATIC_TEST_CASES


def pickup_names_to_list(pickup_list):
    ret = []
    for selected_pickup in pickup_list:
        for pickup in PICKUP_LIST:
            if pickup and selected_pickup == pickup.pickup_name:
                ret.append(pickup.pickup_id)
    return ret


class IsaacTestCase:
    def __init__(self, seed: str, pickups: Union[List[int], List[str]], expected_output: Optional[int]):
        self.seed = seed
        if isinstance(pickups[0], str):
            pickups = pickup_names_to_list(pickups)
        self.pickups = pickups
        self.expected_output = expected_output


def make_static_test_cases():
    output_cases = []
    for case in STATIC_TEST_CASES:
        output_cases.append({
            "seed_str": case[0],
            "seed": string_to_seed(case[0]),
            "pickups": case[1],
            "type": "static",
        })

    return output_cases


def make_test_cases_from_recipes():
    output_cases = []
    seeds = ["28rynmmm", "7bvmyw7d", "g0rgkxtq"]
    default_platform, default_version = DEFAULT_PLATFORM, DEFAULT_GAME_VERSION

    item_list = ItemListEntry.load_item_list(default_platform, default_version)
    recipes = HardcodedRecipe.load_hardcoded_recipes(default_platform, default_version)
    for recipe in recipes.values():
        for seed in seeds:
            achievement_id = item_list[recipe.item_id].achievement_id
            output_cases.append({
                "seed_str": seed,
                "seed": string_to_seed(seed),
                "pickups": recipe.pickups,
                "achievement_id": achievement_id,
                "type": "recipe",
            })

    return output_cases


def make_random_test_cases():
    output_cases = []
    seeds = ["28rynmmm", "7bvmyw7d", "g0rgkxtq"]

    for seed in seeds:
        for _ in range(200):
            pickups = random.choices(list(range(1, 30)), k=8)
            output_cases.append({
                "seed_str": seed,
                "seed": string_to_seed(seed),
                "pickups": pickups,
                "type": "random",
            })

    return output_cases


if __name__ == "__main__":
    cases = make_static_test_cases()
    cases.extend(make_test_cases_from_recipes())
    cases.extend(make_random_test_cases())
    with open("binary_inputs.json", "w") as f:
        json.dump(cases, f)
