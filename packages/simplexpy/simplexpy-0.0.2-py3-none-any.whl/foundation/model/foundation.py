from dataclasses import dataclass, field
from uuid import UUID, uuid4
from typing import Optional
from simplex.foundation.model.reinforcement import Rebars  # Assuming reinforcement.py is in the same directory
from simplex.core.geometry.point import Point2d
from simplex.foundation.model.id import Id
from simplex.core.materials import Concrete


@dataclass
class FoundationBase:
    id: Id = field(init=False)

@dataclass
class RectangularFoundation(FoundationBase):
    """
    Represents a rectangular foundation element with optional eccentricities, material, reinforcement, and position.

    Attributes:
        lx_bottom (float): Length of the bottom side of the foundation in the x-direction.
        ly_bottom (float): Length of the bottom side of the foundation in the y-direction.
        lx_top (float): Length of column base which sits on the foundation in the x-direction.
        ly_top (float): Length of column base which sits on the foundation in the y-direction.
        height (float): Height of the foundation.
        eccentricity_x (Optional[float]): Eccentricity in the x-direction. Defaults to 0.0.
        eccentricity_y (Optional[float]): Eccentricity in the y-direction. Defaults to 0.0.
        material (Optional[Concrete]): Material of the foundation. Defaults to Concrete.C25_30().
        reinforcement (Optional[Reinforcement]): Reinforcement details. Defaults to None.
        top_of_footing (Optional[float]): Elevation of the top of the footing. Defaults to 0.0.
        position (Point2d): Position of the foundation in 2D space. Defaults to (0.0, 0.0).
        name (Optional[str]): Name of the foundation. Defaults to "Point foundation".

    Methods:
        __post_init__(): Initializes the foundation's unique identifier after dataclass initialization.
    """
    lx_bottom: float = 1.4
    ly_bottom: float = 1.4
    lx_top: float = 0.3
    ly_top: float = 0.3
    height: float = 0.4
    eccentricity_x: float = 0.0
    eccentricity_y: float = 0.0
    material: Concrete = field(default_factory=Concrete.C25_30)
    reinforcement: Optional[Rebars] = None
    top_of_footing: float = 0.0
    position: Point2d = field(default_factory=lambda: Point2d(0.0, 0.0))

    name: str = "Point foundation"

    def __post_init__(self):
        self.id = Id(name=self.name)

        self._validate_geometry()


    def _validate_geometry(self):
        if self.lx_bottom <= 0 or self.ly_bottom <= 0:
            raise ValueError("Length in x and y directions must be positive.")
        if self.height <= 0:
            raise ValueError("Height must be positive.")
        # check if eccentricities are within the lx_bottom and ly_bottom dimensions
        if not (0 <= self.eccentricity_x <= self.lx_bottom):
            raise ValueError("Eccentricity in x-direction must be between 0 and lx_bottom.")
        if not (0 <= self.eccentricity_y <= self.ly_bottom):
            raise ValueError("Eccentricity in y-direction must be between 0 and ly_bottom.")




@dataclass
class LineFoundation(FoundationBase):
    """
    Represents a line foundation element with geometric, material, and reinforcement properties.

    Attributes:
        lx_bottom (float): Length of the foundation in the x-direction at the bottom (default: 1.4).
        ly_bottom (float): Width of the wall which sits on the foundation in the y-direction (default: 0.3).
        height (float): Height (thickness) of the foundation (default: 0.4).
        eccentricity_x (float): Eccentricity of the foundation in the x-direction (default: 0.0).
        material (Concrete): Concrete material used for the foundation (default: Concrete.C25_30).
        reinforcement (Optional[Rebars]): Reinforcement details for the foundation (default: None).
        top_of_footing (float): Elevation of the top of the footing (default: 0.0).
        positions (Point2d): Position of the foundation in 2D space (default: Point2d(0.0, 0.0)).
        name (str): Name of the foundation (default: "Line foundation").

    Methods:
        __post_init__(): Initializes the foundation's unique identifier after instantiation.
    """
    lx_bottom: float = 1.4
    lx_top: float = 0.3
    height: float = 0.4
    eccentricity_x: float = 0.0
    material: Concrete = field(default_factory=Concrete.C25_30)
    reinforcement: Optional[Rebars] = None
    top_of_footing: float = 0.0
    position: Point2d = field(default_factory=lambda: Point2d(0.0, 0.0))

    name: str = "Line foundation"


    def __post_init__(self):
        self.id = Id(name=self.name)

        self._validate_geometry()
        self._validate_reinforcement()

    def _validate_geometry(self):
        if self.lx_bottom <= 0:
            raise ValueError("Length in x direction must be positive.")
        if self.height <= 0:
            raise ValueError("Height must be positive.")
        # check if eccentricities are within the lx_bottom and ly_bottom dimensions
        if not (0 <= self.eccentricity_x <= self.lx_bottom):
            raise ValueError("Eccentricity in x-direction must be between 0 and lx_bottom.")
        
    def _validate_reinforcement(self):
        if self.reinforcement is None:
            return
        
        if self.reinforcement.y_direction:
            raise ValueError("Reinforcement is not allowed in the y-direction.")
