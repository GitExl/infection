import json
from os import makedirs
from pathlib import Path
from random import randint
from typing import Dict

from common.resources.soundresource import SoundResource
from common.wad import WADReader
from common.resources.doomimageresource import DoomImageResource


def corrupt_image(image: DoomImageResource, line_count, block_count):
    pixels = bytearray(image.pixels)

    for i in range(0, block_count):
        x_dest = randint(0, image.width)
        y_dest = randint(0, image.height)

        x_src = randint(0, image.width)
        y_src = randint(0, image.height)

        width = 8
        height = 8
        if x_src + width > image.width:
            width = image.width - x_src
        if x_dest + width > image.width:
            width = image.width - x_dest
        if y_src + height > image.height:
            height = image.height - y_src
        if y_dest + height > image.height:
            height = image.height - y_dest

        for y in range(0, height):
            src_index = x_src + (y_src + y) * image.width
            dest_index = x_dest + (y_dest + y) * image.width

            src_row = pixels[src_index:src_index + width]
            dest_row = pixels[dest_index:dest_index + width]

            pixels[dest_index:dest_index + width] = src_row
            pixels[src_index:src_index + width] = dest_row

    # Corrupt vertical lines.
    for i in range(0, line_count):
        x = randint(0, image.width)
        y_src = randint(0, image.height)
        for y in range(y_src, image.height - 1):
            pixels[x + y * image.width] = randint(0, 255)

    image.pixels = bytes(pixels)


def corrupt_sound(sound: SoundResource):
    data = bytearray(sound.data)

    # Bit crush
    crush = 6
    for i in range(0, 5):
        start = randint(0, len(data))
        end = start + randint(1024, 4096)
        if end >= len(data):
            end = len(data)

        for j in range(start, end, crush):
            avg = int(sum(data[j:j + crush]) / crush)
            data[j:j + crush] = [avg] * crush

    # Noise
    for i in range(0, 4):
        start = randint(0, len(data))
        end = start + randint(256, 1024)
        if end >= len(data):
            end = len(data)

        for j in range(start, end):
            data[j] = int((data[j] + randint(0, 95)) / 2)

    sound.data = bytes(data)


print('Reading configuration...')
with open('config_corrupt.json', 'r') as f:
    config = json.load(f)
with open('config_corrupt_local.json', 'r') as f:
    config_local = json.load(f)

config = {**config, **config_local}

dest_path_sprites = Path(config['dest_path_sprites'])
dest_path_sounds = Path(config['dest_path_sounds'])
sprite_list = config['sprites']
line_count = config['corrupt_lines']
block_count = config['corrupt_blocks']


print('Loading WADs...')
lumps = {}
wad_files = []
wad_list = []
for wad in config['wads']:
    wad_file = WADReader(wad)
    wad_files.append(wad_file)
    for lump in wad_file.lumps:
        lumps[lump.name] = lump


print('Gathering sprite data...')
sprites: Dict[str, DoomImageResource] = {}
for sprite_name, new_sprite_name in sprite_list.items():

    for lump_name, lump in lumps.items():
        if lump_name[:4] != sprite_name:
            continue

        key = lump_name
        key = new_sprite_name + key[4:]
        sprites[key] = DoomImageResource.from_data(lump.data, lump.name)

print('Gathering sound data...')
sound_files: Dict[str, SoundResource] = {}
for sound_lump_name, sound_file_name in config['sounds'].items():
    sound_lump = lumps[sound_lump_name]
    sound_files[sound_file_name] = SoundResource.from_doom_sound(sound_lump.data)


print('Corrupting sprites...')
makedirs(dest_path_sprites, exist_ok=True)
for name, image in sprites.items():
    corrupt_image(image, line_count, block_count)

    output_path = dest_path_sprites / Path(name).with_suffix('.lmp')
    data = image.generate_data()
    with open(output_path, 'wb') as f:
        f.write(data)

print('Corrupting sounds...')
makedirs(dest_path_sounds, exist_ok=True)
for name, sound in sound_files.items():
    corrupt_sound(sound)

    output_path = dest_path_sounds / Path(name).with_suffix('.lmp')
    data = sound.getdata()
    with open(output_path, 'wb') as f:
        f.write(data)
