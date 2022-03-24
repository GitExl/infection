from typing import Dict

from wadassembler.context import Context
from common.resources.doomimageresource import DoomImageResource
from common.resources.rawresource import RawResource


def filter_unused_textures(ctx: Context, resources: Dict[str, DoomImageResource]) -> Dict[str, DoomImageResource]:
    if not ctx.config.get('removed_unused_textures', False):
        return resources

    # Track textures explicitly marked as used.
    extra_used_textures = set()
    for texture_name in ctx.config['used_textures']:
        extra_used_textures.add(texture_name)

    # Track animated and switch textures.
    extra_used_textures.update(ctx.animated_textures.get_animated_texture_names(ctx.used_textures, ctx.texture_list))
    extra_used_textures.update(ctx.animated_textures.get_animated_switch_names(ctx.used_textures))

    # Mark extra tracked textures as used.
    for texture_name in extra_used_textures:
        if texture_name in ctx.used_textures:
            ctx.used_textures[texture_name] += 1
        else:
            ctx.used_textures[texture_name] = 1

    ctx.texture_list.remove_unused_textures(set(ctx.used_textures.keys()))

    return resources


def filter_unused_patches(ctx: Context, resources: Dict[str, DoomImageResource]) -> Dict[str, DoomImageResource]:
    if not ctx.config.get('removed_unused_patches', False):
        return resources

    used_patches: Dict[str, DoomImageResource] = {}
    for texture in ctx.texture_list.textures:
        for patch in texture.patches:
            if patch.name in resources:
                used_patches[patch.name] = resources[patch.name]

    return used_patches


def filter_unused_flats(ctx: Context, resources: Dict[str, RawResource]) -> Dict[str, RawResource]:
    if not ctx.config.get('removed_unused_flats', False):
        return resources

    # Track flats explicitly marked as used.
    extra_used_flats = set()
    for flat_name in ctx.config['used_flats']:
        extra_used_flats.add(flat_name)

    # Track animated flats.
    extra_used_flats.update(ctx.animated_textures.get_animated_flat_names(ctx.used_flats, resources))

    # Mark extra tracked flats as used.
    for flat_name in extra_used_flats:
        if flat_name in ctx.used_flats:
            ctx.used_flats[flat_name] += 1
        else:
            ctx.used_flats[flat_name] = 1

    # Return only used flats.
    used_flats: Dict[str, RawResource] = {}
    for name, flat in resources.items():
        if name in ctx.used_flats:
            used_flats[name] = flat

    return used_flats
