import json
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, Optional

import PIL
from PIL.Image import Image

from common.animatedtextures import AnimatedTextures
from common.texturelist import TextureList
from common.wad import WADReader, WADWriter


class Context:

    def __init__(self, target=None):
        self.config: Dict[str, any] = self.read_config()

        if target is not None:
            if target not in self.config['targets']:
                raise Exception('Unknown target {}.'.format(target))
            self.config.update(self.config['targets'][target])

        self.iwad: WADReader = WADReader(Path(self.config['iwad']))
        self.wad: WADWriter = WADWriter(Path(self.config['output_wad']), 'PWAD')
        self.source_path: Path = Path(self.config['source_path'])

        self.playpal_file: Optional[Image] = None
        self.playpal_iwad: Optional[Image] = None
        self.read_playpal_data()

        self.used_textures: Dict[str, int] = {}
        self.used_flats: Dict[str, int] = {}

        self.texture_list: TextureList = TextureList()
        self.read_texture_data()

        self.animated_textures: AnimatedTextures = AnimatedTextures()

        self.namespaces: Dict[str, Dict[str, any]] = {}

    def __del__(self):
        if self.wad is not None:
            self.wad.close()
        if self.iwad is not None:
            self.iwad.close()

    def get_palette_for_resource(self, name: str) -> PIL.Image.Image:
        for mask, source in self.config['palette_overrides'].items():
            if fnmatch(name, mask):
                if source == 'iwad':
                    return self.playpal_iwad
                elif source == 'file':
                    return self.playpal_file
                else:
                    raise Exception('Unknown palette override source "{}"'.format(source))

        if self.playpal_file and self.config['palette_from_file']:
            return self.playpal_file
        return self.playpal_iwad

    def read_playpal_data(self):
        playpal_index = self.iwad.lump_index('PLAYPAL')
        if playpal_index == -1:
            raise Exception('IWAD has no PLAYPAL lump.')

        playpal_lump = self.iwad.lumps[playpal_index]
        playpal_data = playpal_lump.data[0:768]
        self.playpal_iwad = PIL.Image.new('P', (8, 8))
        self.playpal_iwad.putpalette(playpal_data, 'RGB')

        playpal_file = self.source_path / Path('playpal.lmp')
        if playpal_file.exists():
            playpal_data = playpal_file.read_bytes()[:768]
            self.playpal_file = PIL.Image.new('P', (8, 8))
            self.playpal_file.putpalette(playpal_data, 'RGB')

    def read_texture_data(self):
        patch_names_index = self.iwad.lump_index('PNAMES')
        if patch_names_index == -1:
            raise Exception('IWAD has no PNAMES lump.')
        patch_names = TextureList.read_patch_names_from_lump(self.iwad.lumps[patch_names_index])

        textures1_index = self.iwad.lump_index('TEXTURE1')
        if textures1_index != -1:
            self.texture_list.add_textures_from_lump(self.iwad.lumps[textures1_index], patch_names)

        textures2_index = self.iwad.lump_index('TEXTURE2')
        if textures2_index != -1:
            self.texture_list.add_textures_from_lump(self.iwad.lumps[textures2_index], patch_names)

    def read_config(self) -> Dict[str, any]:
        with open('config_assemble.json', 'r') as f:
            config = json.load(f)

        with open('config_assemble_local.json', 'r') as f:
            config_local = json.load(f)

        return {**config, **config_local}
