import xml.etree.ElementTree as ET
from collections import namedtuple


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


ItemPoolEntry = namedtuple("ItemPoolEntry", ["item_id", "weight"])


class ItemPool:
    def __init__(self, pool_id: int, pool_name: str):
        self.pool_id = pool_id
        self.pool_name = pool_name
        self.items = []
        self.lowered_quality = pool_name in LOWERED_QUALITY_POOLS

    def add_item(self, item_id: int, weight: float) -> None:
        self.items.append(ItemPoolEntry(item_id, weight))


with open("itempools.xml", "r") as f:
    itempools = ET.fromstring(f.read())

    for idx, pool in enumerate(itempools):
        assert pool.tag == "Pool"
        pool_name = pool.attrib["Name"]

        if pool_name in CRAFTABLE_ITEM_POOLS:
            item_pool = ItemPool(idx, pool_name)
            for item in pool:
                assert item.tag == "Item"
                item_pool.add_item(int(item.attrib["Id"]), float(item.attrib["Weight"]))
            ITEM_POOLS[item_pool.pool_id] = item_pool
