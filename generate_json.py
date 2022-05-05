import argparse
import os
import json
from crafting_calculator.isaac_recipes import HardcodedRecipe
from crafting_calculator.isaac_item_pools import ItemPool
from crafting_calculator.isaac_items import ItemListEntry
from crafting_calculator.utilities import GAME_VERSIONS, DEFAULT_PLATFORM, DEFAULT_GAME_VERSION


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-folder", "-o", required=True)
    args = parser.parse_args()

    for platform in GAME_VERSIONS:
        for version in GAME_VERSIONS[platform]["versions"]:

            recipes = HardcodedRecipe.load_hardcoded_recipes(platform, version)
            item_pools = ItemPool.load_item_pools(platform, version)
            metadata = ItemListEntry.load_item_list(platform, version)

            recipes_new = {k: recipes[k].item_id for k in recipes}

            metadata_new = {}
            for item_id in metadata:
                item = metadata[item_id]
                item_metadata = {"name": item.name, "quality": item.quality}
                if item.achievement_id is not None:
                    item_metadata["achievement_id"] = item.achievement_id
                metadata_new[item_id] = item_metadata

            item_pools_new = {}
            for pool_id in item_pools:
                item_pool = item_pools[pool_id]
                item_pool_list = []
                for quality, item_list in item_pool.quality_lists.items():
                    item_pool_list.extend([{"id": item[0], "name": metadata[item[0]].name, "weight": item[1] / 100.0, "quality": quality} for item in item_list])
                item_pools_new[pool_id] = {"name": item_pool.pool_name, "items": sorted(item_pool_list, key=lambda item: item["id"])}

            output = {"itempools": item_pools_new, "metadata": metadata_new, "recipes": recipes_new}

            base_path = os.path.join(args.output_folder, "gamedata", platform, version)
            os.makedirs(base_path, exist_ok=True)
            with open(os.path.join(base_path, "data.json"), "w") as f:
                json.dump(output, f)

    with open(os.path.join(args.output_folder, "gamedata", "versions.json"), "w") as f:
        version_metadata = {"default": f"{DEFAULT_PLATFORM}/{DEFAULT_GAME_VERSION}", "platforms": GAME_VERSIONS}
        json.dump(version_metadata, f)


if __name__ == "__main__":
    main()
