from struct import Struct
from typing import Optional, Tuple

from common.level import Side, Sector, Level
from common.resources.mapresource import MapResource

STRUCT_SIDE: Struct = Struct('<hh8s8s8sh')

STRUCT_SECTOR: Struct = Struct('<hh8s8shhh')


def unpack_side(values: Tuple):
    return Side(values[5], values[2].decode('ascii').rstrip('\x00'), values[4].decode('ascii').rstrip('\x00'), values[3].decode('ascii').rstrip('\x00'), values[0], values[1])


def unpack_sector(values: Tuple):
    return Sector(values[0], values[1], values[2].decode('ascii').rstrip('\x00'), values[3].decode('ascii').rstrip('\x00'), values[6], values[5], values[4])


class BinaryLevelReader:

    @staticmethod
    def read(resource: MapResource) -> Optional[Level]:
        sides = BinaryLevelReader._read_binary_data(resource, 'SIDEDEFS', unpack_side, STRUCT_SIDE)
        sectors = BinaryLevelReader._read_binary_data(resource, 'SECTORS', unpack_sector, STRUCT_SECTOR)

        return Level(resource.format, sides, sectors)

    @staticmethod
    def _read_binary_data(resource: MapResource, lump_name: str, unpack_func, data_struct: Struct):
        lump = resource.lumps.get(lump_name)
        if lump is None:
            return []
        data = lump.data

        # Trim any extraneous data, iter_unpack will not accept it.
        if len(data) % data_struct.size != 0:
            aligned = data_struct.size * int(len(data) / data_struct.size)
            data = data[0:aligned]

        items = []
        for unpacked in data_struct.iter_unpack(data):
            items.append(unpack_func(unpacked))

        return items
