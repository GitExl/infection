from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class LevelFormat(Enum):
    DOOM = 'doom'
    HEXEN = 'hexen'


@dataclass(frozen=True)
class Side:
    __slots__ = ['sector', 'texture_upper', 'texture_mid', 'texture_lower', 'texture_x', 'texture_y']

    sector: int
    texture_upper: str
    texture_mid: str
    texture_lower: str
    texture_x: int
    texture_y: int


@dataclass(frozen=True)
class Sector:
    __slots__ = ['z_floor', 'z_ceiling', 'texture_floor', 'texture_ceiling', 'ids', 'type', 'light']

    z_floor: int
    z_ceiling: int
    texture_floor: str
    texture_ceiling: str
    ids: List[int]
    type: int
    light: int


class Level:

    def __init__(self, format: LevelFormat, sides: Optional[List[Side]] = None,
                 sectors: Optional[List[Sector]] = None):
        self.format: LevelFormat = format
        self.sides: List[Side] = [] if sides is None else sides
        self.sectors: List[Sector] = [] if sectors is None else sectors
