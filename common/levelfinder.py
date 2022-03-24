from typing import Dict, List, Optional, Set

from common.level import LevelFormat
from common.wad import WADLump, WADReader


LEVEL_LUMP_NAMES: Set[str] = {
    'THINGS',
    'LINEDEFS',
    'SIDEDEFS',
    'VERTEXES',
    'SEGS',
    'SSECTORS',
    'NODES',
    'SECTORS',
    'REJECT',
    'BLOCKMAP',
    'BEHAVIOR',
    'SCRIPTS',
    'DIALOGUE',
}


class LevelData:

    def __init__(self, name: str):
        self.name: str = name
        self.lumps: Dict[str, WADLump] = {}
        self.format: LevelFormat = LevelFormat.DOOM

    def add(self, lump: WADLump):
        self.lumps[lump.name] = lump
        if lump.name == 'BEHAVIOR':
            self.format = LevelFormat.HEXEN


class LevelDataFinder:

    def __init__(self):
        self.level_data: List[LevelData] = []

    def add_from_wad(self, wad: WADReader, name: Optional[str] = None):
        for index, lump in enumerate(wad.lumps):
            if lump.name != 'THINGS':
                continue

            level_data = LevelDataFinder._collect_level_data(wad, index - 1)
            if name is not None:
                level_data.name = name
            self.level_data.append(level_data)

    @staticmethod
    def _collect_level_data(wad: WADReader, header_index: int) -> LevelData:
        header_lump = wad.lumps[header_index]
        level_data: LevelData = LevelData(header_lump.name)
        level_data.add(header_lump)

        lump_index_max = min(len(wad.lumps), header_index + 20)
        for index in range(header_index + 1, lump_index_max):
            lump = wad.lumps[index]
            if lump.name not in LEVEL_LUMP_NAMES:
                break

            level_data.add(lump)

        return level_data
