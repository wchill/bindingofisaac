import xml.etree.ElementTree as ET
from typing import Optional


_item_achievement_id_mapping = {}
_item_id_to_name_mapping = {}
ITEMS = {}


class ItemListEntry:
    def __init__(self, item_id: int, name: str, quality: int, achievement_id: Optional[int]):
        self.item_id = item_id
        self.name = name
        self.quality = quality
        self.achievement_id = achievement_id

    @property
    def quality_str(self) -> str:
        return '★' * self.quality + '☆' * (4 - self.quality)


with open("items.xml", "r") as f, open("stringtable.sta", "r") as g:
    items = ET.fromstring(f.read())
    string_table = ET.fromstring(g.read())
    assert items.tag == "items"
    for item in items:
        if item.tag in ["passive", "familiar", "active"]:
            item_id = int(item.attrib["id"])
            if "achievement" in item.attrib:
                assert item_id not in _item_achievement_id_mapping
                _item_achievement_id_mapping[item_id] = int(item.attrib["achievement"])

            item_name_string_tag = string_table.find(f"./category[@name='Items']/key[@name='{item.attrib['name'][1:]}']")[0]
            _item_id_to_name_mapping[item_id] = item_name_string_tag.text
        else:
            assert item.tag in ["trinket", "null"]


with open("items_metadata.xml", "r") as f:
    items_metadata = ET.fromstring(f.read())
    assert items_metadata.tag == "items"

    for item in items_metadata:
        if item.tag == "item":
            item_id = int(item.attrib["id"])
            item_name = _item_id_to_name_mapping[item_id]
            item_quality = int(item.attrib["quality"])
            item_achievement_id = _item_achievement_id_mapping.get(item_id)
            ITEMS[item_id] = ItemListEntry(item_id, item_name, item_quality, item_achievement_id)
