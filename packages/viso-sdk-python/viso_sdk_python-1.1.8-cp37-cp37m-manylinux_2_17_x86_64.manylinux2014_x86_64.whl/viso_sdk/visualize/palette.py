import numpy as np
import colorsys
import random
from PIL import ImageColor


class ColorPalette:

    def __init__(self, n, rng=None):
        if not n > 0:
            raise ValueError(f"Invalid Color Palette number - {n}")

        if rng is None:
            rng = random.Random(0xACE)

        candidates_num = 100
        hsv_colors = [(1.0, 1.0, 1.0)]
        for _ in range(1, n):
            colors_candidates = [(rng.random(), rng.uniform(0.8, 1.0), rng.uniform(0.5, 1.0))
                                 for _ in range(candidates_num)]
            min_distances = [self.min_distance(hsv_colors, c) for c in colors_candidates]
            arg_max = int(np.argmax(min_distances))
            hsv_colors.append(colors_candidates[arg_max])

        self.palette = [self.hsv2rgb(*hsv) for hsv in hsv_colors]

    @staticmethod
    def dist(c1, c2):
        dh = min(abs(c1[0] - c2[0]), 1 - abs(c1[0] - c2[0])) * 2
        ds = abs(c1[1] - c2[1])
        dv = abs(c1[2] - c2[2])
        return dh * dh + ds * ds + dv * dv

    @classmethod
    def min_distance(cls, colors_set, color_candidate):
        distances = [cls.dist(o, color_candidate) for o in colors_set]
        return np.min(distances)

    @staticmethod
    def hsv2rgb(h, s, v):
        return tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))

    def __getitem__(self, n):
        return self.palette[n % len(self.palette)]

    def __len__(self):
        return len(self.palette)


PALETTE = ColorPalette(256)
DEFAULT_OPACITY = 100


def get_rgba_color(color=None):
    if color is None:
        return None

    if isinstance(color, tuple):
        color = list(color)

    if type(color) == str:
        rgba = ImageColor.getcolor(color, "RGBA")
        return tuple([rgba[0], rgba[1], rgba[2], rgba[-1]])

    if len(color) == 3:  # rgb
        return tuple([color[0], color[1], color[2], DEFAULT_OPACITY])

    elif len(color) == 4:  # rgba
        alpha = color[3]
        if 0 <= alpha <= 1.0:  # [0.0 1.0]
            alpha = int(alpha * 255)
        else:  # [0, 255]
            alpha = int(alpha)
        return tuple([color[0], color[1], color[2], alpha])

    else:
        return None


def get_rgba_color_with_palette_id(palette_id):
    if palette_id is not None:
        color = PALETTE[palette_id % 256]
        return tuple([color[2], color[1], color[0], DEFAULT_OPACITY])
    else:
        return None
