import os

GAME_VERSIONS = ["1.5", "1.6", "1.7"]
LATEST_GAME_VERSION = GAME_VERSIONS[-1]


def get_gamedata_path(game_version: str, filename: str) -> str:
    return os.path.join(
        os.path.dirname(__file__), "gamedata", f"v{game_version}", filename
    )
