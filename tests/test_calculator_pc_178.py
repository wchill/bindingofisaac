import os
import json
import pytest
from crafting_calculator.isaac_rng import string_to_seed
from crafting_calculator.isaac_pickups import PICKUP_LIST
from crafting_calculator.calculator import get_result


def pickup_names_to_list(pickup_list):
    ret = []
    for selected_pickup in pickup_list:
        for pickup in PICKUP_LIST:
            if pickup and selected_pickup == pickup.pickup_name:
                ret.append(pickup.pickup_id)
    return ret


def load_test_cases(path):
    with open(path, "r") as f:
        cases = json.load(f)

    return [(c["seed_str"], c["pickups"], c["output"], c["unlocked"]) for c in cases]


class TestCraftingCalculatorPc178:
    @pytest.mark.parametrize(
        "seed_str,pickups,correct_id,items_unlocked",
        load_test_cases(
            os.path.join(os.path.dirname(__file__), "test_cases", "pc178.json")
        ),
    )
    def test_calculation(self, seed_str, pickups, correct_id, items_unlocked):
        seed = string_to_seed(seed_str)
        recipe, item_ids, quality_sum = get_result("pc", "v1.7.8a", pickups, seed)
        if items_unlocked:
            # note: PC data might be bugged. unlocked items are being rerolled
            assert (
                correct_id == item_ids[0]
            ), f"Expected {correct_id} but got {item_ids} for {pickups}"
        else:
            assert (
                correct_id in item_ids
            ), f"Expected {correct_id} but got {item_ids} for {pickups}"

    def test_calculation_manual(self):
        seed_str = "28rynmmm"
        pickups = [6, 21, 27, 11, 27, 22, 23, 20]
        correct_id = 711
        items_unlocked = True

        seed = string_to_seed(seed_str)
        recipe, item_ids, quality_sum = get_result("pc", "v1.7.8a", pickups, seed)
        if items_unlocked:
            assert (
                correct_id == item_ids[0]
            ), f"Expected {correct_id} but got {item_ids} for {pickups}"
        else:
            assert (
                correct_id in item_ids
            ), f"Expected {correct_id} but got {item_ids} for {pickups}"


if __name__ == "__main__":
    pytest.main()
