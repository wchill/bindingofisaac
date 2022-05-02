import time
import argparse
from .utilities import LATEST_GAME_VERSION, GAME_VERSIONS
from .calculator import (
    find_items_for_pickups,
    find_recipes_for_item,
    find_uncraftable_items,
    find_item_id,
)
from .isaac_pickups import PICKUP_LIST


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Calculate bag of crafting recipes.",
        epilog="The default behavior is to calculate the item generated by the provided pickups.",
    )
    parser.add_argument(
        "--seed",
        required=True,
        help="The seed for your save file (should be 8 characters; remove the space)",
    )
    parser.add_argument(
        "--pickups",
        required=True,
        metavar="ID",
        type=int,
        nargs="+",
        help="Use these pickup IDs in calculation. If calculating a single item to create, you must pass 8 IDs. The following are all the valid IDs: "
        + ", ".join(
            [
                f"{pickup.pickup_id} - {pickup.pickup_name}"
                for pickup in PICKUP_LIST
                if pickup is not None
            ]
        ),
    )
    parser.add_argument(
        "--game-version",
        required=False,
        help="The game version to use.",
        default=LATEST_GAME_VERSION,
        choices=GAME_VERSIONS,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--find-pickup-recipes",
        action="store_true",
        help="Find all recipes that use these pickup types.",
    )
    group.add_argument(
        "--find-item-recipes",
        metavar="ITEM_ID",
        type=int,
        help="Find all recipes matching this item ID for the given pickup types (sorted by quality).",
    )
    group.add_argument(
        "--find-uncraftable-items",
        action="store_true",
        help="Find all items that are uncraftable using this given set of pickups.",
    )
    args = parser.parse_args()

    t0 = time.monotonic()
    if args.find_pickup_recipes:
        pickups = list(set(args.pickups))
        find_items_for_pickups(args.game_version, args.seed, pickups)
    elif args.find_item_recipes:
        pickups = list(set(args.pickups))
        find_recipes_for_item(
            args.game_version, args.seed, pickups, args.find_item_recipes
        )
    elif args.find_uncraftable_items:
        pickups = list(set(args.pickups))
        find_uncraftable_items(args.game_version, args.seed, pickups)
    else:
        assert (
            len(args.pickups) == 8
        ), "You must provide 8 pickup IDs when calculating a single result."
        find_item_id(args.game_version, args.seed, args.pickups)

    t1 = time.monotonic()
    print()
    print(f"Operation took {(t1 - t0) * 1000:.2f} ms.")
