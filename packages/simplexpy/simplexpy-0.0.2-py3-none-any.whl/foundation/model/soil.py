from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

import simplex.core.error.handling

import simplex.core.error

import simplex.core
from simplex.foundation.model.id import Id
from uuid import UUID, uuid4
from abc import ABC, abstractmethod
import simplex

class Behaviour(Enum):
    """Soil behaviour"""
    UNDRAINED = 1             # undrained
    DRAINED = 2               # drained
    COMBINED = 3              # combined drained/undrained 
    ROCK = 4                  # rock
    ROCK_PLANE_GRINDED = 5    # grinded rock


class MaterialModel(Enum):
    """Material model"""
    NOSETTLEMENT = 1         # No settlement model
    LINEAR = 2               # Linear model
    LOG = 3                  # Log model - used in Denmark
    OVERCONSOLIDATED = 4     # Model for overconsolidated clay
    GENERIC = 5              # Generic model

@dataclass
class SoilMaterial:
    name: str
    drainage: Behaviour
    gamma: float = 18.0
    gamma_eff: Optional[float] = 10.0
    m0: Optional[float] = 20000.0
    phik: Optional[float] = 35.0
    ck: Optional[float] = 0.0
    cuk: Optional[float] = 0.0
    rk: Optional[float] = 0.0

    material_model: MaterialModel = field(init=False, default=MaterialModel.LINEAR)

    id: Id = field(init=False)

    def __post_init__(self):
        self.id = Id(name=self.name)
        
        self._validate()
        

    def _validate(self):
        pass

    @classmethod
    def drained(cls, name: str, phik: float, ck: float, gamma: float, gamma_eff: float, m0: float):
        return cls(
            drainage=Behaviour.DRAINED,
            name=name,
            phik=phik,
            ck=ck,
            gamma=gamma,
            gamma_eff=gamma_eff,
            m0=m0,
        )

    @classmethod
    def undrained(cls, name: str, cuk: float, gamma: float, gamma_eff: float, m0: float):
        return cls(
            drainage=Behaviour.UNDRAINED,
            name=name,
            cuk=cuk,
            gamma=gamma,
            gamma_eff=gamma_eff,
            m0=m0,
        )
    
    @classmethod
    def combined(cls, name: str, phik: float, ck: float, cuk: float, gamma: float, gamma_eff: float, m0: float):
        return cls(
            drainage=Behaviour.COMBINED,
            name=name,
            phik=phik,
            ck=ck,
            cuk=cuk,
            gamma=gamma,
            gamma_eff=gamma_eff,
            m0=m0,
        )
    
    @classmethod
    def rock(cls, name: str, rk: float, gamma: float, gamma_eff: float, m0: float):
        return cls(
            drainage=Behaviour.ROCK,
            name=name,
            rk=rk,
            gamma=gamma,
            gamma_eff=gamma_eff,
            m0=m0,
        )

@dataclass
class Borehole:
    soil_materials: List[SoilMaterial]
    top_of_layers: List[float]

    id: Id = field(init=False)

    def __post_init__(self):
        if len(self.soil_materials) != len(self.top_of_layers):
            raise ValueError(f"{simplex.core.error.handling.RED}soil_materials and top_of_layers must have the same length{simplex.core.error.handling.RESET}")

        self.id = Id(name="Borehole")

    @property
    def number_of_layers(self) -> int:
        return len(self.soil_materials)


class SoilBase(ABC):
    """
    Base class for soil properties.
    This class is not intended to be instantiated directly.
    """
    id: Id = field(init=False)

    @abstractmethod
    def __init__(self):
        pass

@dataclass
class SoilComplex(SoilBase):
    """
    Represents a complex soil profile associated with a borehole, including depth limits and ground water level.

    Attributes:
        borehole (Borehole): The borehole object containing soil layer information.
        depth_limit (float): The negative value representing the maximum depth of the soil profile (in meters).
        ground_water (float): The ground water level within the soil profile (in meters).

    Methods:
        __post_init__():
            Initializes internal IDs and validates the soil complex configuration.
        _validate():
            Validates that:
                - depth_limit is negative,
                - depth_limit is less than the last top_of_layer value in the borehole,
                - ground_water is between the first top_of_layer and the depth_limit.

    Raises:
        ValueError: If any of the validation checks fail.
    """
    borehole: Borehole
    depth_limit: float
    ground_water: float

    def __post_init__(self):
        self.id = Id(name="SoilComplex")
        self._ground_water_level_guid: Optional[UUID] = uuid4()
        self._stratum_guids: List[UUID] = [uuid4() for _ in range(self.borehole.number_of_layers)]
        self._validate()

    def _validate(self):
        if self.depth_limit > 0:
            raise ValueError(f"{simplex.core.error.handling.RED}depth_limit must be a negative value{simplex.core.error.handling.RESET}")

        if self.borehole.top_of_layers[-1] < self.depth_limit:
            raise ValueError(f"{simplex.core.error.handling.RED}The depth_limit must be less than the last top_of_layer value in the borehole{simplex.core.error.handling.RESET}")

        # Check if the ground water is between the first top_of_layer and the ground level
        if not (self.borehole.top_of_layers[0] >= self.ground_water >= self.depth_limit):
            raise ValueError(f"{simplex.core.error.handling.RED}Ground water level must be between the first top_of_layer value in the borehole and the depth_limit{simplex.core.error.handling.RESET}")


@dataclass
class SoilSimple(SoilBase):
    """
    Represents simple soil properties with predefined limits.

    Attributes:
        allowed_soil_pressure_uls (float): Ultimate limit state (ULS) allowed soil pressure in kN/m².
        allowed_soil_pressure_sls (float): Serviceability limit state (SLS) allowed soil pressure in kN/m².
        friction_coefficient (float): Soil friction coefficient (dimensionless).
    """
    allowed_soil_pressure_uls: float = 300
    allowed_soil_pressure_sls: float = 200
    friction_coefficient: float = 0.1

    def __post_init__(self):
        self.id = Id(name="SoilSimple")