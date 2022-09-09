from common.color import Color
from common.palette import Palette


def generate_base_palette():
    base = Palette()

    base.append(Color.from_rgb(0, 0, 0))
    base.append(Color.from_rgb(31, 23, 11))
    base.append(Color.from_rgb(23, 15, 7))
    base.append(Color.from_rgb(75, 75, 75))
    base.append(Color.from_rgb(255, 255, 255))
    base.extend(Palette.from_gradient(Color.from_rgb(27, 27, 27), Color.from_rgb(7, 7, 7), 4))
    base.extend(Palette.from_gradient(Color.from_rgb(47, 55, 31), Color.from_rgb(15, 23, 0), 4).alter(7, 0, 0))
    base.extend(Palette.from_gradient(Color.from_rgb(79, 59, 43), Color.from_rgb(63, 43, 27), 3).alter(0, -0.05, -0.02))

    # Red, flesh
    base.extend(Palette.from_gradient(Color.from_rgb(255, 183, 183), Color.from_rgb(163, 59, 59), 16).alter(5, -0.03, -0.05))
    base.extend(Palette.from_gradient(Color.from_rgb(155, 51, 51), Color.from_rgb(67, 0, 0), 16).alter(5, -0.03, -0.05))

    # Skin\brown
    base.extend(Palette.from_gradient(Color.from_rgb(255, 235, 223), Color.from_rgb(203, 127, 79), 16))
    base.extend(Palette.from_gradient(Color.from_rgb(191, 123, 75), Color.from_rgb(43, 35, 15), 16))

    # Grey
    base.extend(Palette.from_gradient(Color.from_rgb(239, 239, 239), Color.from_rgb(35, 35, 35), 32).alter(0, 0, -0.01))

    # Green
    base.extend(Palette.from_gradient(Color.from_rgb(119, 255, 111), Color.from_rgb(11, 23, 7), 16).alter(26, 0, -0.01))

    # Beige
    base.extend(Palette.from_gradient(Color.from_rgb(191, 167, 143), Color.from_rgb(83, 63, 47), 16).alter(0, 0.04, -0.06))
    base.extend(Palette.from_gradient(Color.from_rgb(159, 131, 99), Color.from_rgb(67, 51, 27), 8).alter(0, 0.04, -0.06))

    # Olive
    base.extend(Palette.from_gradient(Color.from_rgb(123, 127, 99), Color.from_rgb(55, 63, 39), 8).alter(-9, 0.02, -0.05))

    # Yellow\brown
    base.extend(Palette.from_gradient(Color.from_rgb(255, 255, 115), Color.from_rgb(115, 43, 0), 8).mix(Color.from_rgb(255, 0, 0), 0.08))

    # White\red, blood
    base.extend(Palette.from_gradient(Color.from_rgb(255, 255, 255), Color.from_rgb(255, 31, 31), 8).alter(-7, 0.11, -0.13))
    base.extend(Palette.from_gradient(Color.from_rgb(255, 0, 0), Color.from_rgb(67, 0, 0), 16).alter(-7, 0.11, -0.13))

    # Blue
    blue = Palette.from_gradient(Color.from_rgb(231, 231, 255), Color.from_rgb(27, 27, 255), 8)
    blue.extend(Palette.from_gradient(Color.from_rgb(0, 0, 255), Color.from_rgb(0, 0, 83), 8))
    base.extend(blue.alter(-25, -0.06, -0.05))

    # Orange
    base.extend(Palette.from_gradient(Color.from_rgb(255, 255, 255), Color.from_rgb(255, 127, 27), 8))
    base.extend(Palette.from_gradient(Color.from_rgb(243, 115, 23), Color.from_rgb(175, 67, 0), 8))

    # Yellow
    base.extend(Palette.from_gradient(Color.from_rgb(255, 255, 255), Color.from_rgb(255, 255, 0), 8).mix(Color.from_rgb(255, 0, 0), 0.07))

    # Ochre
    base.extend(Palette.from_gradient(Color.from_rgb(167, 63, 0), Color.from_rgb(135, 35, 0), 4).mix(Color.from_rgb(255, 0, 0), 0.07))

    # Dark brown
    base.extend(Palette.from_gradient(Color.from_rgb(79, 59, 39), Color.from_rgb(47, 27, 11), 4).alter(0, 0.04, -0.06))

    # Dark blue
    base.extend(Palette.from_gradient(Color.from_rgb(0, 0, 83), Color.from_rgb(0, 0, 0), 8).alter(-22, 0.02, 0))

    base.append(Color.from_rgb(255, 159, 67))
    base.append(Color.from_rgb(255, 231, 75))
    base.append(Color.from_rgb(255, 123, 255))

    # Magenta
    base.extend(Palette.from_gradient(Color.from_rgb(255, 0, 255), Color.from_rgb(111, 0, 107), 4))

    base.append(Color.from_rgb(167, 107, 107))

    return base


palettes = []

base = generate_base_palette()
palettes.append(base)

# Hurt
for i in range(1, 9):
    palettes.append(base.mix(Color.from_rgb(255, 0, 0), (1 / 9) * i))

# Pickup
for i in range(1, 5):
    palettes.append(base.mix(Color.from_rgb(215, 186, 69), 0.125 * i))

# Radsuit
palettes.append(base.mix(Color.from_rgb(0, 255, 0), 0.125))

base.write_image('palette.png')
with open('src/playpal.lmp', 'wb') as f:
    for index, palette in enumerate(palettes):
        palette.append_data(f)

colormaps = []

# Sector brightness
for i in range(0, 32):
    colormaps.append(base.darken(i / 32))

# Invulnerability
colormaps.append(base.grayscale().invert())

# Empty
colormaps.append(base.darken(1.0))

with open('src/colormap.lmp', 'wb') as f:
    for colormap in colormaps:
        mapping = colormap.get_mapping_to(base, 'doom')
        f.write(bytes(mapping))
