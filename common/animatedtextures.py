import struct
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set, Dict

from common.resources.rawresource import RawResource
from common.texturelist import TextureList


S_SWITCH_TEXTURE = struct.Struct('<9s9sH')
S_ANIMATED_TEXTURE = struct.Struct('<B9s9sI')


@dataclass(frozen=True)
class AnimatedTexture:
    speed: int
    last: str
    first: str

    def pack(self, type: int) -> bytes:
        return S_ANIMATED_TEXTURE.pack(
            type,
            self.last.encode('ascii'),
            self.first.encode('ascii'),
            self.speed
        )


@dataclass(frozen=True)
class SwitchTexture:
    episode: int
    texture1: str
    texture2: str

    def pack(self) -> bytes:
        return S_SWITCH_TEXTURE.pack(
            self.texture1.encode('ascii'),
            self.texture2.encode('ascii'),
            self.episode
        )


class AnimatedTextures:

    def __init__(self):
        self.textures: List[AnimatedTexture] = []
        self.flats: List[AnimatedTexture] = []
        self.switches: List[SwitchTexture] = []

    def get_animated_data(self) -> bytes:
        data = bytearray()

        for flat in self.flats:
            data.extend(flat.pack(0))
        for texture in self.textures:
            data.extend(texture.pack(1))

        data.append(0xFF)

        return data

    def get_switches_data(self) -> bytes:
        data = bytearray()

        for switch in self.switches:
            data.extend(switch.pack())

        data.extend(b'\x00' * 20)

        return data

    def read_from_text(self, file_path: Path):
        self.textures = []
        self.flats = []
        self.switches = []

        with open(file_path, 'r') as f:
            for line_index, line in enumerate(f.readlines()):

                # Strip comments.
                comment_pos = line.find('#')
                if comment_pos != -1:
                    line = line[:comment_pos]

                line = line.strip()
                if not len(line):
                    continue

                line = line.upper()

                # Detect headers.
                if line == '[SWITCHES]':
                    mode = 'switches'
                    continue
                elif line == '[FLATS]':
                    mode = 'flats'
                    continue
                elif line == '[TEXTURES]':
                    mode = 'textures'
                    continue

                # Add new flat/texture.
                if mode == 'flats' or mode == 'textures':
                    parts = line.split()
                    if len(parts) != 3:
                        raise Exception('File {} line {} must have 3 parts.'.format(file_path, line_index + 1))

                    speed, last, first = parts
                    speed = int(speed)
                    if speed < 1:
                        raise Exception('File {} line {} has an invalid speed.')

                    if mode == 'textures':
                        self.textures.append(AnimatedTexture(speed, last, first))
                    elif mode == 'flats':
                        self.flats.append(AnimatedTexture(speed, last, first))

                # Add new switch.
                elif mode == 'switches':
                    parts = line.split()
                    if len(parts) != 3:
                        raise Exception('File {} line {} must have 3 parts.'.format(file_path, line_index + 1))

                    episode, texture1, texture2 = parts
                    episode = int(episode)
                    if episode < 1 or episode > 3:
                        raise Exception('File {} line {} has an invalid episode.')

                    self.switches.append(SwitchTexture(episode, texture1, texture2))

    def get_animated_flat_names(self, used_flats: Dict[str, int], flat_resources: Dict[str, RawResource]) -> Set[str]:
        animated_flats = set()
        flat_names = list(flat_resources.keys())

        for animated_flat in self.flats:

            # Attempt to locate first and last flats inside current list of flats.
            try:
                first_index = flat_names.index(animated_flat.first)
                last_index = flat_names.index(animated_flat.last)
            except ValueError:
                continue

            # Create a dict of flat names in this series. The first and last, and any listed inbetween.
            series_flat_names = {
                flat_names[first_index],
                flat_names[last_index],
            }
            for i in range(first_index + 1, last_index):
                series_flat_names.add(flat_names[i])

            # If any one flat of this set is used, mark them all as used.
            for flat_name in series_flat_names:
                if flat_name in used_flats:
                    animated_flats.update(series_flat_names)
                    break

        return animated_flats

    def get_animated_texture_names(self, used_textures: Dict[str, int], texture_list: TextureList) -> Set[str]:
        animated_textures = set()

        texture_names = []
        for texture in texture_list.textures:
            texture_names.append(texture.name)

        for animated_texture in self.textures:

            # Attempt to locate first and last textures inside current list of textures.
            try:
                first_index = texture_names.index(animated_texture.first)
                last_index = texture_names.index(animated_texture.last)
            except ValueError:
                continue

            # Create a dict of texture names in this series. The first and last, and any listed inbetween.
            series_texture_names = {
                texture_names[first_index],
                texture_names[last_index],
            }
            for i in range(first_index + 1, last_index):
                series_texture_names.add(texture_names[i])

            # If any one texture of this set is used, mark them all as used.
            for texture_name in series_texture_names:
                if texture_name in used_textures:
                    animated_textures.update(series_texture_names)
                    break

        return animated_textures

    def get_animated_switch_names(self, used_textures: Dict[str, int]) -> Set[str]:
        switch_textures = set()

        for switch in self.switches:
            if switch.texture1 in used_textures or switch.texture2 in used_textures:
                switch_textures.add(switch.texture1)
                switch_textures.add(switch.texture2)

        return switch_textures
