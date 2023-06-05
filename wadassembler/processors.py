import PIL
from PIL.Image import Image

from wadassembler.context import Context
from common.levelreader import BinaryLevelReader
from common.resources.doomimageresource import DoomImageResource
from common.resources.mapresource import MapResource
from common.resources.rawresource import RawResource
from common.resources.soundresource import SoundResource


def palettize_image(ctx: Context, namespace: str, name: str, resource: Image) -> Image:
    img: Image = resource.copy()
    mask = None

    # Get alpha mask from alpha channel.
    if img.mode == 'RGBA' or img.mode == 'PA' or img.mode == 'LA':
        alpha = img.getchannel('A')
        mask = PIL.Image.eval(alpha, lambda a: 0 if a > 127 else 0xFF)

    # Get alpha mask from a transparent color index.
    elif (img.mode == 'P' or img.mode == 'L') and 'transparency' in img.info and type(img.info['transparency']) is int:
        alpha_color = img.info['transparency']
        mask = PIL.Image.eval(img, lambda a: 0xFF if a == alpha_color else 0)
        mask = PIL.Image.frombytes('L', mask.size, mask.tobytes())

    # Convert to RGB.
    if img.mode == 'P' or img.mode == 'PA' or img.mode == 'L' or img.mode == 'LA' or img.mode == 'RGBA':
        img = img.convert('RGB', dither=PIL.Image.NONE)
    elif img.mode == 'RGB':
        pass
    else:
        raise Exception('Cannot palettize "{}": unsupported image mode "{}".'.format(name, img.mode))

    # Convert image to target palette.
    pal, pal_raw = ctx.get_palette_for_resource(name)
    data_in = img.getdata()
    data_out = [0] * len(data_in)
    for i in range(0, len(data_in)):
        data_out[i] = pal.get_nearest_index_doom(data_in[i])
    converted = PIL.Image.new('P', img.size)
    converted.putpalette(pal_raw, 'RGB')
    converted.putdata(data_out)

    # TODO: use this to convert when https://github.com/python-pillow/Pillow/issues/1852 is fixed
    # converted = img.quantize(256, palette=palette_image, dither=PIL.Image.NONE)

    # Apply alpha mask.
    if mask is not None:
        converted.paste(ctx.config['transparent_color_index'], mask=mask)

    return converted


def convert_image_to_raw_doom_flat(ctx: Context, namespace: str, name: str, resource: Image) -> RawResource:
    if resource.mode != 'P':
        raise Exception('Cannot convert "{}" to flat: image is not palettized.'.format(name))
    if resource.width != 64 or resource.height != 64:
        raise Exception('Cannot convert "{}" to flat: image is not 64x64.'.format(name))

    return RawResource(bytes(resource.getdata()))


def convert_sound_to_raw_doom_sound(ctx: Context, namespace: str, name: str, resource: SoundResource) -> RawResource:
    sound: SoundResource = resource

    if sound.channels != 1:
        raise Exception('Sound "{}" is not mono.'.format(name))
    if sound.bit_depth != 8:
        raise Exception('Sound "{}" is not 8 bit.'.format(name))
    if sound.sample_rate > 44100:
        raise Exception('Sound "{}" sample rate is higher than 44100 Hz.'.format(name))
    if sound.sample_rate < 8000:
        raise Exception('Sound "{}" sample rate is lower than 8000 Hz.'.format(name))

    return RawResource(bytes(sound.getdata()))


def convert_image_to_doom_image(ctx: Context, namespace: str, name: str, resource: Image) -> DoomImageResource:
    if resource.mode != 'P':
        raise Exception('Cannot convert "{}" to image: image is not palettized.'.format(name))

    return DoomImageResource.from_image(resource)


def track_used_textures_flats(ctx: Context, namespace: str, name: str, resource: MapResource) -> MapResource:
    level = BinaryLevelReader.read(resource)

    for side in level.sides:
        ctx.used_textures[side.texture_lower] = ctx.used_textures.get(side.texture_lower, 0) + 1
        ctx.used_textures[side.texture_mid] = ctx.used_textures.get(side.texture_mid, 0) + 1
        ctx.used_textures[side.texture_upper] = ctx.used_textures.get(side.texture_upper, 0) + 1

    for sector in level.sectors:
        ctx.used_flats[sector.texture_floor] = ctx.used_flats.get(sector.texture_floor, 0) + 1
        ctx.used_flats[sector.texture_ceiling] = ctx.used_flats.get(sector.texture_ceiling, 0) + 1

    return resource


def apply_image_offset(ctx: Context, namespace: str, name: str, resource: DoomImageResource) -> DoomImageResource:
    offsets = ctx.config['offsets'][namespace]

    if name in offsets:
        offset = offsets[name]
        resource.left = offset[0]
        resource.top = offset[1]

    return resource


def create_textures_from_patches(ctx: Context, namespace: str, name: str, resource: DoomImageResource) -> DoomImageResource:
    ctx.texture_list.add_texture_from_patch(name, resource)
    return resource
