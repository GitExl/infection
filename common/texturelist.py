import struct
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Set

from common.resources.doomimageresource import DoomImageResource
from common.wad import WADLump


S_TEXTURE_HEADER = struct.Struct('<8sIHHIH')
S_TEXTURE_PATCH = struct.Struct('<HHHHH')


@dataclass
class TexturePatch:
    x: int
    y: int
    name: str

    def pack(self, patch_index: int):
        return S_TEXTURE_PATCH.pack(self.x, self.y, patch_index, 0, 0)

    @staticmethod
    def unpack_from(data: bytes, offset: int, patch_name_list: List[str]):
        x, y, patch_index, step_dir, colormap = S_TEXTURE_PATCH.unpack_from(data, offset)
        return TexturePatch(x, y, patch_name_list[patch_index])


@dataclass
class Texture:
    name: str
    width: int
    height: int
    patches: List[TexturePatch] = field(default_factory=list)

    def pack(self, patch_names: Dict[str, int]) -> bytes:
        data = bytearray()
        data += S_TEXTURE_HEADER.pack(self.name.encode('ascii'), 0, self.width, self.height, 0, len(self.patches))

        for patch in self.patches:

            # Find existing patch name index or add as new index.
            patch_index = patch_names.get(patch.name)
            if patch_index is None:
                patch_index = len(patch_names)
                patch_names[patch.name] = patch_index

            data.extend(patch.pack(patch_index))

        return data

    @staticmethod
    def unpack_from(data: bytes, offset: int, patch_name_list: List[str]):
        name, masked, width, height, column_dir, patch_count = S_TEXTURE_HEADER.unpack_from(data, offset)
        name = name.decode('ascii').rstrip('\x00')
        offset += 22

        patches = []
        for i in range(patch_count):
            patches.append(TexturePatch.unpack_from(data, offset, patch_name_list))
            offset += 10

        return Texture(name, width, height, patches)


class TextureList:

    def __init__(self):
        self.textures: List[Texture] = [
            Texture('AAAFUNKY', 64, 128, [
                TexturePatch(0, 0, 'BODIES')
            ])
        ]

    @staticmethod
    def read_patch_names_from_lump(lump: WADLump) -> List[str]:
        offset = 0
        patch_names = []

        patch_count, = struct.unpack_from('<I', lump.data, offset)
        offset += 4

        for i in range(patch_count):
            patch_name, = struct.unpack_from('<8s', lump.data, offset)
            patch_name = patch_name.decode('ascii').rstrip('\x00')
            patch_names.append(patch_name)
            offset += 8

        return patch_names

    def add_textures_from_lump(self, lump: WADLump, patch_names: List[str]):
        offset = 0

        texture_count, = struct.unpack_from('<I', lump.data, offset)
        offset += 4

        texture_offsets = struct.unpack_from('<' + ('I' * texture_count), lump.data, offset)

        for i in range(texture_count):
            offset = texture_offsets[i]
            texture = Texture.unpack_from(lump.data, offset, patch_names)

            if i > 0:
                self.textures.append(texture)

    def add_texture_from_patch(self, name: str, patch: DoomImageResource):
        patches = [TexturePatch(0, 0, name)]
        texture = Texture(name, patch.width, patch.height, patches)

        for existing_index, existing_texture in enumerate(self.textures):
            if existing_texture.name == name:
                self.textures[existing_index] = texture
                return

        self.textures.append(texture)

    def generate_lump_data(self) -> Tuple[bytes, bytes]:
        patch_names: Dict[str, int] = {}

        texture_header = struct.pack('<I', len(self.textures))
        texture_offsets = []

        # Generate texture data.
        textures_data = bytearray()
        textures_data_start = 4 + len(self.textures) * 4
        for texture in self.textures:
            texture_offsets.append(textures_data_start + len(textures_data))
            textures_data.extend(texture.pack(patch_names))

        # Generate lump data for the patch names list.
        patch_name_list = []
        for patch_name in patch_names.keys():
            patch_name_list.append(patch_name.encode('ascii'))

        patch_names_data = bytearray()
        patch_names_data += struct.pack('<I', len(patch_name_list))
        patch_names_data += struct.pack('<' + ('8s' * len(patch_name_list)), *patch_name_list)

        texture_offset_data = struct.pack('<' + ('I' * len(self.textures)), *texture_offsets)
        textures_lump_data = texture_header + texture_offset_data + textures_data

        return textures_lump_data, patch_names_data

    def remove_unused_textures(self, used_textures: Set[str]):
        used = []

        for index, texture in enumerate(self.textures):
            if index == 0 or texture.name in used_textures:
                used.append(texture)

        self.textures = used
