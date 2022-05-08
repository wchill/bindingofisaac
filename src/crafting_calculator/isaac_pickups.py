from typing import Optional


class PickupEntry:
    def __init__(
        self,
        pickup_id: int,
        pickup_name: str,
        shorthand_name: Optional[str],
        quality: int,
    ):
        self.pickup_id = pickup_id
        self.pickup_name = pickup_name
        self.shorthand_name = shorthand_name
        self.quality = quality


# Mapping is as below - extracted from game binary
# hsbegBr.oOQ/|%v^V123[(>?~${4_X
PICKUP_LIST = [
    None,
    PickupEntry(1, "Red Heart", "h", 1),
    PickupEntry(2, "Soul Heart", "s", 4),
    PickupEntry(3, "Black Heart", "b", 5),
    PickupEntry(4, "Eternal Heart", "e", 5),
    PickupEntry(5, "Gold Heart", "g", 5),
    PickupEntry(6, "Bone Heart", "B", 5),
    PickupEntry(7, "Rotten Heart", "r", 1),
    PickupEntry(8, "Penny", ".", 1),
    PickupEntry(9, "Nickel", "o", 3),
    PickupEntry(10, "Dime", "O", 5),
    PickupEntry(11, "Lucky Penny", "Q", 8),
    PickupEntry(12, "Key", "/", 2),
    PickupEntry(13, "Golden Key", "|", 7),
    PickupEntry(14, "Charged Key", "%", 5),
    PickupEntry(15, "Bomb", "v", 2),
    PickupEntry(16, "Golden Bomb", "^", 7),
    PickupEntry(17, "Giga Bomb", "V", 10),
    PickupEntry(18, "Micro Battery", "1", 2),
    PickupEntry(19, "Lil Battery", "2", 4),
    PickupEntry(20, "Mega Battery", "3", 8),
    PickupEntry(21, "Card", "[", 2),
    PickupEntry(22, "Pill", "(", 2),
    PickupEntry(23, "Rune", ">", 4),
    PickupEntry(24, "Dice Shard", "?", 4),
    PickupEntry(25, "Cracked Key", "~", 2),
    PickupEntry(26, "Golden Penny", "$", 7),
    PickupEntry(27, "Golden Pill", "{", 7),
    PickupEntry(28, "Golden Battery", "4", 7),
    PickupEntry(29, "Poop Nugget", "_", 0),
    PickupEntry(30, "Unknown", "X", 1),
]
