## generate a Point3d class for 3D points in space
from dataclasses import dataclass
from typing import Optional

@dataclass
class Point2d:
    """A class representing a point in 2D space."""
    x: float = 0.0
    y: float = 0.0

@dataclass
class Point3d(Point2d):
    """A class representing a point in 3D space."""
    z: float = 0.0


