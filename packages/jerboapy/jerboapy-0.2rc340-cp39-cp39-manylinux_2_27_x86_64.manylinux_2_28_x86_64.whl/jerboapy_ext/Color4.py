import numpy as np
from typing import List

class Color4:
    EPSILON = 1e-2
    BRIGHTER = 20
    DARKER = -20

    # Pré-définition des couleurs standards
    RED = None
    GREEN = None
    BLUE = None
    LIGHTGRAY = None
    BLACK = None
    WHITE = None
    MAGENTA = None
    YELLOW = None
    CYAN = None
    GRAY = None
    DARKGRAY = None
    LIGHTGRAY = None
    ORANGE = None
    PINK = None
    PURPLE = None
    BROWN = None
    LIME = None
    TEAL = None
    NAVY = None
    OLIVE = None
    SILVER = None
    GOLD = None
    CORAL = None
    INDIGO = None
    LAVENDER = None
    MAROON = None
    CHOCOLATE = None
    SALMON = None
    SKYBLUE = None
    IVORY = None
    AQUA = None

    def __init__(self, r: float, g: float, b: float, a: float = 1.0):
        self.rgba = np.array([r, g, b, a], dtype=np.float32)

    def copy(self) -> 'Color4':
        return Color4(*self.rgba)

    def toNumpy(self) -> np.ndarray:
        return self.rgba

    def r(self) -> float:
        return self.rgba[0]

    def g(self) -> float:
        return self.rgba[1]

    def b(self) -> float:
        return self.rgba[2]

    def a(self) -> float:
        return self.rgba[3]

    def getR(self) -> float:
        return self.r()

    def setR(self, r: float):
        self.rgba[0] = r

    def getG(self) -> float:
        return self.g()

    def setG(self, g: float):
        self.rgba[1] = g

    def getB(self) -> float:
        return self.b()

    def setB(self, b: float):
        self.rgba[2] = b

    def getA(self) -> float:
        return self.a()

    def setA(self, a: float):
        self.rgba[3] = a

    def setRGB(self, r: float, g: float, b: float, a: float = None):
        self.rgba[:3] = [r, g, b]
        if a is not None:
            self.rgba[3] = a

    def equals(self, obj: object) -> bool:
        if not isinstance(obj, Color4):
            return False
        return np.allclose(self.rgba, obj.rgba, atol=self.EPSILON)

    @staticmethod
    def middle(a: 'Color4', b: 'Color4') -> 'Color4':
        return Color4(*(a.rgba + b.rgba) / 2)

    @staticmethod
    def middle_list(colors: List['Color4']) -> 'Color4':
        rgba_sum = np.sum([color.rgba for color in colors], axis=0)
        return Color4(*(rgba_sum / len(colors)))

    def __str__(self) -> str:
        return f"Color4(r={self.r()}, g={self.g()}, b={self.b()}, a={self.a()})"

    @staticmethod
    def make(r: float, g: float, b: float, a: float = 1.0) -> 'Color4':
        return Color4(r, g, b, a)

    @staticmethod
    def randomColor() -> 'Color4':
        return Color4(*np.random.rand(3), 1.0)

    @staticmethod
    def darker(color: 'Color4') -> 'Color4':
        factor = 0.8
        return Color4(*(color.rgba[:3] * factor), color.a())

    def brighter(self, i: float = 1.2) -> 'Color4':
        return Color4(
            *np.clip(self.rgba[:3] * i, 0.0, 1.0),
            self.a()
        )

    def toGray(self) -> 'Color4':
        gray = 0.299 * self.r() + 0.587 * self.g() + 0.114 * self.b()
        return Color4(gray, gray, gray, self.a())

    def scale(self, d: float):
        self.rgba[:3] *= d

    def scaleAdd(self, r: float):
        self.rgba[:3] += r

    def compareTo(self, o: 'Color4') -> int:
        if self.equals(o):
            return 0
        return -1 if np.sum(self.rgba[:3]) < np.sum(o.rgba[:3]) else 1
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color4):
            return NotImplemented
        return np.array_equal(self.rgba, other.rgba)
    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Color4):
            return NotImplemented
        return not np.array_equal(self.rgba, other.rgba)

    def __array__(self) -> np.ndarray:
        return self.rgba

# Initialisation des couleurs standards
Color4.RED = Color4(1.0, 0.0, 0.0)
Color4.GREEN = Color4(0.0, 1.0, 0.0)
Color4.BLUE = Color4(0.0, 0.0, 1.0)
Color4.LIGHTGRAY = Color4(0.5, 0.5, 0.5)
Color4.BLACK = Color4(0.0, 0.0, 0.0)
Color4.WHITE = Color4(1.0, 1.0, 1.0)
Color4.MAGENTA = Color4(1.0, 0.0, 1.0)
Color4.YELLOW = Color4(1.0, 1.0, 0.0)
Color4.CYAN = Color4(0.0, 1.0, 1.0)
Color4.GRAY = Color4(0.5, 0.5, 0.5)
Color4.DARKGRAY = Color4(0.25, 0.25, 0.25)
Color4.LIGHTGRAY = Color4(0.75, 0.75, 0.75)
Color4.ORANGE = Color4(1.0, 0.5, 0.0)
Color4.PINK = Color4(1.0, 0.75, 0.8)
Color4.PURPLE = Color4(0.5, 0.0, 0.5)
Color4.BROWN = Color4(0.65, 0.16, 0.16)
Color4.LIME = Color4(0.0, 1.0, 0.0)
Color4.TEAL = Color4(0.0, 0.5, 0.5)
Color4.NAVY = Color4(0.0, 0.0, 0.5)
Color4.OLIVE = Color4(0.5, 0.5, 0.0)
Color4.SILVER = Color4(0.75, 0.75, 0.75)
Color4.GOLD = Color4(1.0, 0.84, 0.0)
Color4.CORAL = Color4(1.0, 0.5, 0.31)
Color4.INDIGO = Color4(0.29, 0.0, 0.51)
Color4.LAVENDER = Color4(0.9, 0.9, 0.98)
Color4.MAROON = Color4(0.5, 0.0, 0.0)
Color4.CHOCOLATE = Color4(0.82, 0.41, 0.12)
Color4.SALMON = Color4(0.98, 0.5, 0.45)
Color4.SKYBLUE = Color4(0.53, 0.81, 0.92)
Color4.IVORY = Color4(1.0, 1.0, 0.94)
Color4.AQUA = Color4(0.0, 1.0, 1.0)