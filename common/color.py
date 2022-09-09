from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, HSLColor, LabColor


class Color:

    def __init__(self, r: int, g: int, b: int):
        self.srgb = sRGBColor(r, g, b)
        self.r = self.srgb.clamped_rgb_r
        self.g = self.srgb.clamped_rgb_g
        self.b = self.srgb.clamped_rgb_b

        self.cache_lab = None
        self.cache_hsl = None

    def get_hsl(self):
        if self.cache_hsl is None:
            self.cache_hsl = convert_color(self.srgb, HSLColor)
        return self.cache_hsl

    def get_lab(self):
        if self.cache_lab is None:
            self.cache_lab = convert_color(self.srgb, LabColor)
        return self.cache_lab

    def alter(self, hue, saturation, lightness):
        hsl = self.get_hsl()
        hsl.hsl_h += hue
        hsl.hsl_s += saturation
        hsl.hsl_l += lightness

        rgb = convert_color(hsl, sRGBColor)

        return Color(
            rgb.clamped_rgb_r,
            rgb.clamped_rgb_g,
            rgb.clamped_rgb_b,
        )

    def mix(self, other, alpha: float):
        return Color(
            self.r + (other.r - self.r) * alpha,
            self.g + (other.g - self.g) * alpha,
            self.b + (other.b - self.b) * alpha,
        )

    def add(self, other, alpha: float):
        value = (1.0 - (self.r * 0.299 + self.g * 0.587 + self.b * 0.114)) * alpha
        return Color(
            self.r + other.r * value,
            self.g + other.g * value,
            self.b + other.b * value,
        )

    def screen(self, other):
        return Color(
            1.0 - (1.0 - self.r) * (1.0 - other.r),
            1.0 - (1.0 - self.g) * (1.0 - other.g),
            1.0 - (1.0 - self.b) * (1.0 - other.b),
        )

    def darken(self, alpha: float):
        return Color(
            self.r * (1.0 - alpha),
            self.g * (1.0 - alpha),
            self.b * (1.0 - alpha),
        )

    def brighten(self, alpha: float):
        return Color(
            self.r + (self.r * alpha),
            self.g + (self.g * alpha),
            self.b + (self.b * alpha),
        )

    def grayscale(self):
        value = self.r * 0.299 + self.g * 0.587 + self.b * 0.114
        return Color(
            value,
            value,
            value
        )

    def invert(self):
        return Color(
            1.0 - self.r,
            1.0 - self.g,
            1.0 - self.b,
        )

    def multiply(self, alpha: float):
        return Color(
            self.r * alpha,
            self.g * alpha,
            self.b * alpha,
        )

    def copy(self):
        return Color(self.r, self.g, self.b)

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int):
        return cls(r / 255.0, g / 255.0, b / 255.0)

    def __repr__(self):
        return '({:.02f}, {:.02f}, {:.02f})'.format(self.r, self.g, self.b)
