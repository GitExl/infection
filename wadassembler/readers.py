from pathlib import Path
from typing import List, Tuple

import PIL
from PIL.Image import Image

from wadassembler.context import Context
from common.levelfinder import LevelDataFinder
from common.resources.doomimageresource import DoomImageResource
from common.resources.mapresource import MapResource
from common.resources.rawresource import RawResource
from common.resources.soundresource import SoundResource
from common.wad import WADReader


def read_raw(ctx: Context, file: Path) -> List[Tuple[str, RawResource]]:
    return [(file.stem.upper(), RawResource(file.read_bytes()))]


def read_png_as_image(ctx: Context, file: Path) -> List[Tuple[str, Image]]:
    return [(file.stem.upper(), PIL.Image.open(file))]


def read_wav_as_sound(ctx: Context, file: Path) -> List[Tuple[str, SoundResource]]:
    return [(file.stem.upper(), SoundResource.from_wave_file(file))]


def read_maps(ctx: Context, file: Path) -> List[Tuple[str, MapResource]]:
    with WADReader(file) as wad:
        level_finder = LevelDataFinder()
        level_finder.add_from_wad(wad)

    levels = []
    for level in level_finder.level_data:
        levels.append((level.name, MapResource(level.format, level.name, level.lumps)))

    return levels


def read_as_doom_image(ctx: Context, file: Path) -> List[Tuple[str, DoomImageResource]]:
    return [(file.stem.upper(), DoomImageResource.from_file(file, ctx.config['transparent_color_index']))]


def read_defswani_as_raw(ctx: Context, file: Path) -> List[Tuple[str, RawResource]]:
    ctx.animated_textures.read_from_text(file)

    return [
        ('ANIMATED', RawResource(ctx.animated_textures.get_animated_data())),
        ('SWITCHES', RawResource(ctx.animated_textures.get_switches_data()))
    ]


def get_patches(ctx: Context, file: Path) -> List[Tuple[str, DoomImageResource]]:
    name = file.stem.upper()
    patch = ctx.namespaces['patches'].get(name)
    if patch is None:
        raise Exception('Cannot find patch "{}" for texture.'.format(name))

    return [(name, patch)]
