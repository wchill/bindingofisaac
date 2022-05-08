import pytest
from crafting_calculator.isaac_pickups import PICKUP_LIST
from crafting_calculator.isaac_rng import string_to_seed
from crafting_calculator.calculator import get_result


def pickup_names_to_list(pickup_list):
    ret = []
    for selected_pickup in pickup_list:
        for pickup in PICKUP_LIST:
            if pickup and selected_pickup == pickup.pickup_name:
                ret.append(pickup.pickup_id)
    return ret


class TestCraftingCalculatorSwitch15:
    @pytest.mark.parametrize(
        "seed_string,pickups,correct_id",
        [
            (
                "7bvmyw7d",
                pickup_names_to_list(
                    [
                        "Red Heart",
                        "Red Heart",
                        "Soul Heart",
                        "Soul Heart",
                        "Penny",
                        "Nickel",
                        "Nickel",
                        "Key",
                    ]
                ),
                375,
            ),
            (
                "g0rgkxtq",
                pickup_names_to_list(
                    [
                        "Red Heart",
                        "Red Heart",
                        "Soul Heart",
                        "Soul Heart",
                        "Soul Heart",
                        "Nickel",
                        "Bomb",
                        "Bomb",
                    ]
                ),
                375,
            ),
            (
                "g0rgkxtq",
                pickup_names_to_list(
                    [
                        "Soul Heart",
                        "Soul Heart",
                        "Penny",
                        "Nickel",
                        "Bomb",
                        "Bomb",
                        "Bomb",
                        "Bomb",
                    ]
                ),
                375,
            ),
            (
                "dg9wm41b",
                pickup_names_to_list(
                    [
                        "Soul Heart",
                        "Nickel",
                        "Nickel",
                        "Nickel",
                        "Nickel",
                        "Penny",
                        "Bomb",
                        "Bomb",
                    ]
                ),
                349,
            ),
            (
                "dg9wm41b",
                pickup_names_to_list(
                    [
                        "Red Heart",
                        "Nickel",
                        "Nickel",
                        "Nickel",
                        "Nickel",
                        "Nickel",
                        "Bomb",
                        "Bomb",
                    ]
                ),
                376,
            ),
            (
                "g0rgkxtq",
                pickup_names_to_list(
                    [
                        "Soul Heart",
                        "Soul Heart",
                        "Soul Heart",
                        "Soul Heart",
                        "Soul Heart",
                        "Soul Heart",
                        "Soul Heart",
                        "Penny",
                    ]
                ),
                419,
            ),
            (
                "dg9wm41b",
                pickup_names_to_list(
                    [
                        "Red Heart",
                        "Nickel",
                        "Nickel",
                        "Nickel",
                        "Nickel",
                        "Dime",
                        "Bomb",
                        "Bomb",
                    ]
                ),
                299,
            ),
            (
                "ffqdxrfg",
                pickup_names_to_list(
                    [
                        "Bomb",
                        "Bomb",
                        "Bomb",
                        "Penny",
                        "Key",
                        "Key",
                        "Dime",
                        "Dime",
                    ]
                ),
                599,
            ),
            (
                "t0kg01zf",
                pickup_names_to_list(
                    [
                        "Dime",
                        "Bomb",
                        "Bomb",
                        "Penny",
                        "Penny",
                        "Penny",
                        "Penny",
                        "Golden Bomb",
                    ]
                ),
                116,
            ),
            (
                "t0kg01zf",
                pickup_names_to_list(
                    [
                        "Penny",
                        "Penny",
                        "Penny",
                        "Dime",
                        "Red Heart",
                        "Soul Heart",
                        "Key",
                        "Bomb",
                    ]
                ),
                138,
            ),
            (
                "t0kg01zf",
                pickup_names_to_list(
                    [
                        "Bomb",
                        "Bomb",
                        "Red Heart",
                        "Red Heart",
                        "Soul Heart",
                        "Soul Heart",
                        "Nickel",
                        "Nickel",
                    ]
                ),
                51,
            ),
            (
                "kndjdqwg",
                pickup_names_to_list(
                    [
                        "Eternal Heart",
                        "Golden Bomb",
                        "Pill",
                        "Pill",
                        "Bomb",
                        "Bomb",
                        "Key",
                        "Penny",
                    ]
                ),
                142,
            ),
            (
                "7aldagay",
                pickup_names_to_list(
                    [
                        "Red Heart",
                        "Eternal Heart",
                        "Eternal Heart",
                        "Key",
                        "Golden Key",
                        "Bomb",
                        "Penny",
                        "Golden Penny",
                    ]
                ),
                380,
            ),
        ],
    )
    def test_calculation(self, seed_string, pickups, correct_id):
        seed = string_to_seed(seed_string)
        recipe, item_id, quality_sum = get_result("switch", "v1.5", pickups, seed)
        assert item_id == correct_id


if __name__ == "__main__":
    pytest.main()
