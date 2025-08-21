from dataclasses import dataclass, field
from typing import List, Optional
from simplex.core.materials.materials import Reinforcement
from enum import Enum


class Zone(Enum):
    """Enumeration for reinforcement zones in a foundation.
    This enum defines the possible zones for reinforcement layers in a foundation.
    """
    START = 1  # Start
    END = 2    # End
    BOTTOM = 3 # Bottom
    RIGHT = 4  # Right
    TOP = 5    # Top
    LEFT = 6   # Left

@dataclass
class ReinfLayer:
    diameter: float
    spacing: float
    concrete_cover: float
    side_cover: Optional[float] = None
    zone: Optional[Zone] = None
    material: Reinforcement = field(default_factory=Reinforcement.B500)

@dataclass
class Rebars:
    x_direction: List[ReinfLayer]
    y_direction: Optional[List[ReinfLayer]] = None

    @property
    def layers(self) -> List[ReinfLayer]:
        """Returns all reinforcement layers in both x and y directions."""
        return self.x_direction + (self.y_direction or [])

    @property
    def material(self) -> Reinforcement:
        # merge materials from both directions and check if the guids are the same. if not, raise an error
        materials = set()
        for layer in self.layers:
            if layer.material.id.guid in materials:
                continue
            materials.add(layer.material.id.guid)
        if len(materials) > 1:
            raise ValueError("Rebars must have the same material in both directions.")
        return self.x_direction[0].material if self.x_direction else self.y_direction[0].material
