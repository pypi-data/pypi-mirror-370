from itertools import cycle
import random
from typing import Iterable


class Color:
    """An RGBA color."""

    def __init__(self, r: int, g: int, b: int, a: int = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def with_alpha(self, a: int):
        """Return the color with a given alpha component."""
        return self.__class__(self.r, self.g, self.b, a)

    def brighten(self, alpha: float):
        """Brighten the color by a multiplier factor."""
        return self.__class__(
            r=int(self.r * alpha),
            g=int(self.g * alpha),
            b=int(self.b * alpha),
            a=self.a,
        )

    def rgb(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)

    def rgba(self) -> tuple[int, int, int, int]:
        return (self.r, self.g, self.b, self.a)

    @staticmethod
    def create_palette() -> Iterable:
        """Generate colors from a pre-defined palette."""
        # taken from: https://github.com/jiffyclub/palettable/blob/master/palettable/cartocolors/colormaps.py
        pastel = [
            Color(102, 197, 204),
            Color(246, 207, 113),
            Color(248, 156, 116),
            Color(220, 176, 242),
            Color(135, 197, 95),
            Color(158, 185, 243),
            Color(254, 136, 177),
            Color(201, 219, 116),
            Color(139, 224, 164),
            Color(180, 151, 231),
        ]

        random.seed(42)
        random.shuffle(pastel)
        yield from cycle(pastel)
