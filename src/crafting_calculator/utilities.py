from typing import List, Tuple
import os

GAME_VERSIONS = {
    "switch": {
        "name": "Switch",
        "versions": {
            "v1.5": 1,
            "v1.6": 1,
            "v1.7": 3
        }
    },
    "pc": {
        "name": "PC",
        "versions": {
            "v1.7.7a": 2,
            "v1.7.8a": 3
        }
    }
}
DEFAULT_PLATFORM = "pc"
DEFAULT_GAME_VERSION = sorted(GAME_VERSIONS[DEFAULT_PLATFORM]["versions"].keys())[-1]


QUALITY_RANGES_V1 = [
    (0, 0, 1),  # 0-8   -> quality 0-1
    (9, 0, 2),  # 9-14  -> quality 0-2
    (15, 1, 2),  # 15-18 -> quality 1-2
    (19, 1, 3),  # 19-22 -> quality 1-3
    (23, 1, 4),  # 23-26 -> quality 1-4
    (27, 2, 4),  # 27-30 -> quality 2-4
    (31, 3, 4),  # 31-34 -> quality 3-4
    (35, 4, 4),  # 35+   -> quality 4
]


QUALITY_RANGES_V2 = [
    (0, 0, 1),  # 0-8   -> quality 0-1
    (9, 0, 2),  # 9-14  -> quality 0-2
    (15, 1, 2),  # 15-18 -> quality 1-2
    (19, 2, 3),  # 19-22 -> quality 1-3
    (23, 2, 4),  # 23-26 -> quality 2-4
    (27, 3, 4),  # 27-34 -> quality 3-4
    (35, 4, 4),  # 35+   -> quality 4
]


def get_all_game_versions() -> List[str]:
    output = []
    for platform in GAME_VERSIONS:
        for version in GAME_VERSIONS[platform]["versions"]:
            output.append(f"{platform}/{version}")
    return output


def parse_game_version_string(platform_version: str) -> Tuple[str, str]:
    temp = platform_version.split("/")
    return temp[0], temp[1]


def get_calculator_version(platform: str, game_version: str) -> int:
    return GAME_VERSIONS[platform]["versions"][game_version]


def get_gamedata_path(platform: str, game_version: str, filename: str) -> str:
    return os.path.join(
        os.path.dirname(__file__), "gamedata", platform, game_version, filename
    )


def get_quality_ranges(platform: str, game_version: str) -> List[Tuple[int, int, int]]:
    if get_calculator_version(platform, game_version) == 1:
        return QUALITY_RANGES_V1
    else:
        return QUALITY_RANGES_V2


def hardcoded_recipe_requires_unlock(platform: str, game_version: str) -> bool:
    return get_calculator_version(platform, game_version) >= 3
