from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
import uuid


class Interval:
    def __init__(self, min_value: float = 0.0, max_value: float = 1.0):
        self.min = min_value
        self.max = max_value
        self._step = 0.1

    @property
    def step(self) -> float:
        """Getter for the step value."""
        return self._step
    
    #create a setter for step
    @step.setter
    def step(self, value: float):
        """Setter for the step value."""
        if value <= 0:
            raise ValueError("Step must be a positive value.")
        self._step = value

@dataclass
class FoundationDesign:
    """
    Represents a foundation with configurable geometric properties and constraints.

    Attributes:
        step (float): The discretization step used for interval values, specified in meters. Default is 0.1 m.
        width (Interval): The interval representing the possible widths of the foundation, specified in meters. Defaults to Interval(0.6, 1.4) m.
        length (Interval): The interval representing the possible lengths of the foundation, specified in meters. Defaults to Interval(0.6, 1.4) m.
        height (Interval): The interval representing the possible heights of the foundation, specified in meters. Defaults to Interval(0.1, 0.6) m.
        length_width_ratio (Optional[float]): The ratio of length to width. Defaults to 0.0.

    Methods:
        __post_init__():
            Ensures that all interval attributes (width, length, height) share the same step value as defined by the 'step' attribute.
    """
    step : float = 0.1
    width: Interval = field(default_factory=lambda: Interval(0.6, 1.4))
    length: Interval = field(default_factory=lambda: Interval(0.6, 1.4))
    height: Interval = field(default_factory=lambda: Interval(0.1, 0.6))
    equal_length_width: bool = False

    def __post_init__(self):
        # Ensure that all intervals share the same step value
        self.width._step = self.step
        self.length._step = self.step
        self.height._step = self.step
    
    @property
    def length_width_ratio(self) -> float:
        if self.equal_length_width:
            return 1.0
        else:
            return 0.0

@dataclass
class ConcreteDesign:
    """
    Represents concrete design parameters for reinforcement.

    Attributes:
        step (float): The increment step used for calculations (default is 0.1).
        rnfr_dia (List[int]): List of available reinforcement bar diameters in millimeters (mm) (default is [12, 16, 20]).
        spacing_limits (Interval): Permissible range for reinforcement spacing in millimeters (mm), as an Interval object (default is Interval(100, 300)).

    Methods:
        __post_init__():
            Ensures that the spacing_limits Interval uses the same step value as the Concrete instance.
    """
    step : float = 0.1
    rnfr_dia: List[int] = field(default_factory=lambda: [12, 16, 20])
    spacing_limits: Interval = field(default_factory=lambda: Interval(100, 300))

    def __post_init__(self):
        # Ensure that spacing_limits shares the same step value
        self.spacing_limits._step = self.step

@dataclass
class DesignSettings:
    limit_utilisation: float = 1.0
    foundation_settings: FoundationDesign = None
    concrete_settings: ConcreteDesign = None

    _active: bool = False

    # #raise error if foundation_settings and concrete_settings are both not none
    # def __post_init__(self):
    #     if self.foundation_settings is None and self.concrete_settings is None:
    #         raise ValueError("Either foundation_settings or concrete_settings must be provided.")
    #     if self.foundation_settings is not None and self.concrete_settings is not None:
    #         raise ValueError("Only one of foundation_settings or concrete_settings can be provided.")

class DesignType(Enum):
    FOUNDATION_GEOMETRY = "foundation_geometry"
    REINFORCEMENT = "reinforcement"
    #BOTH = "both"