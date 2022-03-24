from typing import Dict

from common.level import LevelFormat
from common.levelfinder import LevelData
from common.wad import WADLump


class MapResource:

    def __init__(self, format: LevelFormat, name: str, lumps: Dict[str, WADLump]):
        self.format: LevelFormat = format
        self.name: str = name
        self.lumps: Dict[str, WADLump] = lumps

    @staticmethod
    def from_level_data(level_data: LevelData):
        return MapResource(level_data.name, level_data.lumps)
