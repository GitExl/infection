from wadassembler.filters import filter_unused_textures, filter_unused_patches, filter_unused_flats
from wadassembler.processors import track_used_textures_flats, convert_sound_to_raw_doom_sound, convert_image_to_raw_doom_flat, \
    convert_image_to_doom_image, apply_image_offset, palettize_image, create_textures_from_patches
from wadassembler.readers import read_raw, read_maps, read_wav_as_sound, read_png_as_image, read_defswani_as_raw, \
    get_patches, read_as_doom_image
from wadassembler.writers import write_raw, write_maps, write_doom_image, write_textures

namespaces = {
    'root': {
        'patterns': {
            'defswani.dat': [read_defswani_as_raw],
            '*.lmp': [read_raw],
            '*.txt': [read_raw],
            '*.deh': [read_raw],
            '*.bex': [read_raw],
        },
        'writer': write_raw,
    },

    'maps': {
        'patterns': {
            'maps/**/*.wad': [read_maps, track_used_textures_flats],
        },
        'writer': write_maps,
    },

    'graphics': {
        'patterns': {
            'graphics/**/*.png': [read_png_as_image, palettize_image, convert_image_to_doom_image, apply_image_offset],
        },
        'writer': write_doom_image,
    },

    'music': {
        'patterns': {
            'music/**/*.mus': [read_raw],
            'music/**/*.mid': [read_raw],
        },
        'writer': write_raw,
    },

    'sounds': {
        'patterns': {
            'sounds/**/*.wav': [read_wav_as_sound, convert_sound_to_raw_doom_sound],
            'sounds/**/*.lmp': [read_raw],
        },
        'writer': write_raw,
    },

    'sprites': {
        'patterns': {
            'sprites/**/*.png': [read_png_as_image, palettize_image, convert_image_to_doom_image, apply_image_offset],
            'sprites/**/*.lmp': [read_as_doom_image]
        },
        'markers': ['SS_START', 'SS_END'],
        'writer': write_doom_image,
    },

    'flats': {
        'patterns': {
            'flats/**/*.png': [read_png_as_image, palettize_image, convert_image_to_raw_doom_flat],
            'flats/**/*.lmp': [read_raw],
        },
        'markers': ['FF_START', 'FF_END'],
        'filter': filter_unused_flats,
        'writer': write_raw,
    },

    'patches': {
        'patterns': {
            'textures/**/*.png': [read_png_as_image, palettize_image, convert_image_to_doom_image],
            'textures/**/*.lmp': [read_as_doom_image],
        },
        'markers': ['PP_START', 'PP_END'],
        'filter': filter_unused_patches,
        'writer': write_doom_image,
    },

    'textures': {
        'patterns': {
            'textures/**/*.png': [get_patches, create_textures_from_patches],
            'textures/**/*.lmp': [get_patches, create_textures_from_patches],
        },
        'filter': filter_unused_textures,
        'writer': write_textures,
    },

    'tx': {
        'patterns': {
            'tx/**/*.png': [read_raw],
        },
        'markers': ['TX_START', 'TX_END'],
        'writer': write_raw,
    },
}
