from typing import Dict

from wadassembler.context import Context
from common.resources.doomimageresource import DoomImageResource
from common.resources.mapresource import MapResource
from common.resources.rawresource import RawResource


def write_raw(ctx: Context, resources: Dict[str, RawResource]):
    for name, resource in resources.items():
        ctx.wad.add_lump(name, resource.data)


def write_maps(ctx: Context, resources: Dict[str, MapResource]):
    for name, map in resources.items():
        for lump_name, lump in map.lumps.items():
            ctx.wad.add_lump(lump_name, lump.data)


def write_doom_image(ctx: Context, resources: Dict[str, DoomImageResource]):
    for name, doom_image in resources.items():
        ctx.wad.add_lump(name, doom_image.generate_data(transparent_index=ctx.config['transparent_color_index']))


def write_textures(ctx: Context, resources: Dict[str, DoomImageResource]):
    textures_data, patch_names_data = ctx.texture_list.generate_lump_data()
    ctx.wad.add_lump('TEXTURE1', textures_data)
    ctx.wad.add_lump('PNAMES', patch_names_data)
