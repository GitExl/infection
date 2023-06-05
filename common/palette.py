from math import floor
from typing import List, Dict, Tuple

from PIL import Image

from common.color import Color


class Palette:

    def __init__(self):
        self._colors: List[Color] = []
        self._cached_index_doom: Dict[int, int] = {}

    @classmethod
    def from_gradient(cls, color1: Color, color2: Color, count: int):
        palette = cls()
        for i in range(0, count):
            mixed = color1.mix(color2, i / (count - 1))
            palette.append(mixed)
        return palette

    def append(self, color: Color):
        self._colors.append(color)

    def extend(self, palette):
        self._colors.extend(palette.get_colors())

    def alter(self, hue, saturation, lightness):
        palette = Palette()
        for color in self._colors:
            palette.append(color.alter(hue, saturation, lightness))

        return palette

    def mix(self, other: Color, alpha):
        palette = Palette()
        for color in self._colors:
            palette.append(color.mix(other, alpha))

        return palette

    def add(self, other: Color, alpha):
        palette = Palette()
        for color in self._colors:
            palette.append(color.add(other, alpha))

        return palette

    def screen(self, other: Color):
        palette = Palette()
        for color in self._colors:
            palette.append(color.screen(other))

        return palette

    def darken(self, alpha):
        palette = Palette()
        for color in self._colors:
            palette.append(color.darken(alpha))

        return palette

    def brighten(self, alpha):
        palette = Palette()
        for color in self._colors:
            palette.append(color.brighten(alpha))

        return palette

    def grayscale(self):
        palette = Palette()
        for color in self._colors:
            palette.append(color.grayscale())

        return palette

    def invert(self):
        palette = Palette()
        for color in self._colors:
            palette.append(color.invert())

        return palette

    def multiply(self, alpha):
        palette = Palette()
        for color in self._colors:
            palette.append(color.multiply(alpha))

        return palette

    def get_mapping_to(self, base, mode):
        mapping = []

        if mode == 'doom':
            for color in self._colors:
                mapping.append(base.get_nearest_index_doom((color.r, color.g, color.b)))
        else:
            for color in self._colors:
                mapping.append(base.get_nearest_index_lab(color))

        return mapping

    def get_nearest_index_doom(self, color_t: Tuple[int, int, int]) -> int:
        other_hash = color_t[0] + color_t[1] * 0xFF + color_t[2] * 0xFFFF
        if other_hash in self._cached_index_doom:
            return self._cached_index_doom[other_hash]

        r = color_t[0] / 255
        g = color_t[1] / 255
        b = color_t[2] / 255

        best_distortion = (r * r + g * g + b * b) * 2
        best_index = 0

        for index, color in enumerate(self._colors):
            dr = r - color.r
            dg = g - color.g
            db = b - color.b

            distortion = dr * dr + dg * dg + db * db
            if distortion < best_distortion:
                if distortion == 0:
                    best_index = index
                    break

                best_distortion = distortion
                best_index = index

        self._cached_index_doom[other_hash] = best_index
        return best_index

    def get_nearest_index_lab(self, other):
        other = other.get_lab()

        best_index = 0
        best_delta = (other.lab_l * other.lab_l + other.lab_a * other.lab_a + other.lab_b * other.lab_b) * 2

        for index, color in enumerate(self._colors):
            color = color.get_lab()

            dh = other.lab_l - color.lab_l
            ds = other.lab_a - color.lab_a
            dl = other.lab_b - color.lab_b
            delta = dh * dh + ds * ds + dl * dl
            if delta < best_delta:
                best_index = index
                best_delta = delta

        return best_index

    def write_image(self, filename: str):
        img = Image.new('P', (16, 16))

        img_data = range(0, 256)
        img.putdata(img_data)

        img_pal = []
        for color in self._colors:
            img_pal.append(floor(color.r * 255))
            img_pal.append(floor(color.g * 255))
            img_pal.append(floor(color.b * 255))
        img.putpalette(img_pal)

        img.save(filename)

    def get_data(self, data: bytes):
        for index in range(0, len(data), 3):
            self._colors.append(Color.from_rgb(
                data[index + 0],
                data[index + 1],
                data[index + 2],
            ))

    def append_data(self, f):
        data = []
        for color in self._colors:
            data.extend([
                int(color.r * 255),
                int(color.g * 255),
                int(color.b * 255),
            ])

        f.write(bytes(data))

    def copy(self):
        palette = Palette()
        for color in self._colors:
            palette._colors.append(color.copy())
        return palette

    def get_colors(self) -> List[Color]:
        return self._colors

    def bit_crush_vga(self):
        for i, color in enumerate(self._colors):
            self._colors[i].r = (self._colors[i].r / 4) * 4
            self._colors[i].g = (self._colors[i].g / 4) * 4
            self._colors[i].b = (self._colors[i].b / 4) * 4
