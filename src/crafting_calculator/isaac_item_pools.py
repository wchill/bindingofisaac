import xml.etree.ElementTree as ET
from collections import defaultdict
from .isaac_items import ITEMS
import os
import itertools


CRAFTABLE_ITEM_POOLS = [
    "treasure",
    "shop",
    "boss",
    "devil",
    "angel",
    "secret",
    "shellGame",
    "goldenChest",
    "redChest",
    "curse",
    "planetarium",
]

LOWERED_QUALITY_POOLS = ["devil", "angel", "secret"]

ITEM_POOLS = {}
ITEM_POOLS_XML_PATH = os.path.join(os.path.dirname(__file__), "itempools.xml")


class ItemPool:
    def __init__(self, pool_id: int, pool_name: str):
        self.pool_id = pool_id
        self.pool_name = pool_name
        self.lowered_quality = pool_name in LOWERED_QUALITY_POOLS
        self.quality_lists = defaultdict(list)

    def get_all_items(self):
        keys = self.quality_lists.keys()
        return sorted(itertools.chain.from_iterable([self.quality_lists[key] for key in keys]), key=lambda x: x[0])

    def add_item(self, item_id: int, weight: float, quality: int) -> None:
        self.quality_lists[quality].append((item_id, int(weight * 100)))


with open(ITEM_POOLS_XML_PATH, "r", encoding="utf-8") as f:
    itempools = ET.fromstring(f.read())

    for idx, pool in enumerate(itempools):
        assert pool.tag == "Pool"
        pool_name = pool.attrib["Name"]

        if pool_name in CRAFTABLE_ITEM_POOLS:
            item_pool = ItemPool(idx, pool_name)
            for item in pool:
                assert item.tag == "Item"
                item_id = int(item.attrib["Id"])
                quality = ITEMS[item_id].quality
                item_pool.add_item(item_id, float(item.attrib["Weight"]), quality)
            ITEM_POOLS[item_pool.pool_id] = item_pool
