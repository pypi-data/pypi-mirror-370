import numpy as np
from typing import List, Collection, Union, Set

class Point3:
    EPSILON = 1e-3
    sqrt2 = np.sqrt(2.0)
    sqrt1_2 = 1.0 / sqrt2
    ZERO = None  # Will be initialized later as Point3(0, 0, 0)
    PI = 3.141592653589793

    def __init__(self, x=0.0, y=None, z=None):
        if isinstance(x, Point3) and isinstance(y, Point3):
            # Cas où deux objets Point3 sont passés
            a, b = x, y
            self.x = b.x - a.x
            self.y = b.y - a.y
            self.z = b.z - a.z
        elif y is None and z is None:
            # Cas où un seul argument est passé (x, y, z par défaut à 0.0)
            self.x = x
            self.y = 0.0
            self.z = 0.0
        else:
            # Cas où trois arguments sont passés
            self.x = x
            self.y = y
            self.z = z

    def toNumpy(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=np.float32)

    @staticmethod
    def toDegree(rad: float) -> float:
        return np.degrees(rad)

    @staticmethod
    def toRadian(deg: float) -> float:
        return np.radians(deg)

    @staticmethod
    def CentreCercle3Point(a: 'Point3', b: 'Point3', c: 'Point3') -> 'Point3':
        # Calculate the midpoints of AB and BC
        mid_ab = Point3.linear(a, b, 0.5)
        mid_bc = Point3.linear(b, c, 0.5)

        # Calculate the normal vectors to AB and BC
        ab = b.sub(a)
        bc = c.sub(b)
        normal_ab = Point3(-ab.y, ab.x, 0)
        normal_bc = Point3(-bc.y, bc.x, 0)

        # Solve for the intersection of the two lines
        # Line 1: mid_ab + t * normal_ab
        # Line 2: mid_bc + s * normal_bc
        # We solve for t and s such that the two lines intersect
        A = np.array([
            [normal_ab.x, -normal_bc.x],
            [normal_ab.y, -normal_bc.y]
        ])
        B = np.array([
            mid_bc.x - mid_ab.x,
            mid_bc.y - mid_ab.y
        ])

        try:
            t, _ = np.linalg.solve(A, B)
        except np.linalg.LinAlgError:
            raise ValueError("The points are collinear and do not define a unique circle.")

        # Calculate the center of the circle
        center = Point3(
            mid_ab.x + t * normal_ab.x,
            mid_ab.y + t * normal_ab.y,
            0
        )
        return center

    def equals(self, o: object) -> bool:
        if not isinstance(o, Point3):
            return False
        return np.isclose(self.x, o.x, atol=self.EPSILON) and \
               np.isclose(self.y, o.y, atol=self.EPSILON) and \
               np.isclose(self.z, o.z, atol=self.EPSILON)

    def get(self, i: int) -> float:
        return [self.x, self.y, self.z][i]

    def add(self, p: 'Point3') -> 'Point3':
        # print(f"Adding Point3: ({self.x}, {self.y}, {self.z}) + ({p.x}, {p.y}, {p.z})")
        return Point3(self.x + p.x, self.y + p.y, self.z + p.z)

    def add_const(self, n: 'Point3') -> 'Point3':
        return self.add(n)

    def sub(self, p: 'Point3') -> 'Point3':
        return Point3(self.x - p.x, self.y - p.y, self.z - p.z)

    def scale(self, v: float) -> 'Point3':
        # print(f"Scaling Point3: ({self.x}, {self.y}, {self.z}) by {v}")
        return Point3(self.x * v, self.y * v, self.z * v)

    def div(self, v: float) -> 'Point3':
        return Point3(self.x / v, self.y / v, self.z / v)

    def dot(self, p: 'Point3') -> float:
        return self.x * p.x + self.y * p.y + self.z * p.z

    def cross(self, v: 'Point3') -> 'Point3':
        cross_product = np.cross([self.x, self.y, self.z], [v.x, v.y, v.z])
        return Point3(*cross_product)

    def norm(self) -> float:
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def norm2(self) -> float:
        return self.x**2 + self.y**2 + self.z**2

    def normalize(self):
        n = self.norm()
        if n > 0:
            self.x /= n
            self.y /= n
            self.z /= n
        return self

    def distance(self, p: 'Point3') -> float:
        return np.sqrt((self.x - p.x)**2 + (self.y - p.y)**2 + (self.z - p.z)**2)

    def copy(self) -> 'Point3':
        return Point3(self.x, self.y, self.z)

    def __str__(self) -> str:
        return f"Point3({self.x}, {self.y}, {self.z})"

    @staticmethod
    def middle(points: Union[List['Point3'], Collection['Point3'], 'Point3']) -> 'Point3':
        if isinstance(points, Point3):
            # Si un seul point est fourni, on le retourne directement
            return points
        elif isinstance(points, (list, set, tuple)):
            # Si une collection de points est fournie, on calcule le barycentre
            x_sum = sum(p.x for p in points)
            y_sum = sum(p.y for p in points)
            z_sum = sum(p.z for p in points)
            count = len(points)
            if count == 0:
                raise ValueError("La collection de points est vide.")
            return Point3(x_sum / count, y_sum / count, z_sum / count)
        else:
            raise TypeError("L'argument doit être un Point3 ou une collection de Point3.")

    @staticmethod
    def barycenter(a: 'Point3', ca: float, b: 'Point3', cb: float) -> 'Point3':
        total_weight = ca + cb
        if total_weight == 0:
            raise ValueError("The sum of weights (ca + cb) must not be zero.")
        x = (a.x * ca + b.x * cb) / total_weight
        y = (a.y * ca + b.y * cb) / total_weight
        z = (a.z * ca + b.z * cb) / total_weight
        return Point3(x, y, z)

    @staticmethod
    def clamp(val: float, min_val: float, max_val: float) -> float:
        return max(min(val, max_val), min_val)

    def isInside(self, a: 'Point3', b: 'Point3') -> bool:
        return a.x <= self.x <= b.x and a.y <= self.y <= b.y and a.z <= self.z <= b.z

    def compareTo(self, o: 'Point3') -> int:
        if self.equals(o):
            return 0
        return -1 if self.norm() < o.norm() else 1

    @staticmethod
    def min(a: 'Point3', b: 'Point3') -> 'Point3':
        return Point3(min(a.x, b.x), min(a.y, b.y), min(a.z, b.z))

    @staticmethod
    def max(a: 'Point3', b: 'Point3') -> 'Point3':
        return Point3(max(a.x, b.x), max(a.y, b.y), max(a.z, b.z))

    @staticmethod
    def linear(a: 'Point3', b: 'Point3', k: float) -> 'Point3':
        return Point3(a.x + k * (b.x - a.x), a.y + k * (b.y - a.y), a.z + k * (b.z - a.z))
    
    def __add__(self, other):
        if isinstance(other, Point3):
            return Point3(self.x + other.x, self.y + other.y, self.z + other.z)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Point3):
            return Point3(self.x - other.x, self.y - other.y, self.z - other.z)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Point3(self.x * other, self.y * other, self.z * other)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Point3(self.x / other, self.y / other, self.z / other)
        return NotImplemented

    def __eq__(self, other):
        if not isinstance(other, Point3):
            return False
        return self.equals(other)

    def __neg__(self):
        return Point3(-self.x, -self.y, -self.z)
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
    def __array__(self, dtype=None):
        if dtype is None:
            dtype = np.float32
        return np.array([self.x, self.y, self.z], dtype=dtype)

    # def __add__(self, other):
    #     if isinstance(other, Point3):
    #         return Point3(self.x + other.x, self.y + other.y, self.z + other.z)
    #     raise TypeError("Unsupported operand type(s) for +: 'Point3' and '{}'".format(type(other).__name__))

# Initialize the ZERO constant
Point3.ZERO = Point3(0.0, 0.0, 0.0)