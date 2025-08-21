from abc import ABC
from enum import Enum
from typing import Optional
from simplex.foundation.model.id import Id
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from abc import abstractmethod


class LoadType(Enum):
    CHARACTERISTIC = 1
    FREQUENT = 2
    QUASI_PERMANENT = 3
    ULTIMATE = 4
    ACCIDENTAL = 5
    #FIRE = 6
    SEISMIC = 7


class FoundationLoading(ABC):
    id: Id = field(init=False)

    @abstractmethod
    def __init__(self):
        pass

    def __post_init__(self):
        self.id = Id(name=self.name)
        self._load_case_id: Optional[UUID] = uuid4()
        self._load_combination_id: Optional[UUID] = uuid4()


@dataclass
class PointFoundationLoading(FoundationLoading):
    """
    Represents the loading applied to a point foundation.

    Attributes:
        name (str): The name of the loading case.
        type (LoadType): The type of load applied.
        hx (float): Horizontal load in the x-direction (kN). Defaults to 0.
        hy (float): Horizontal load in the y-direction (kN). Defaults to 0.
        n (float): Vertical load (normal force) (kN). Defaults to 0.
        mx (float): Moment about the x-axis (kNm). Defaults to 0.
        my (float): Moment about the y-axis (kNm). Defaults to 0.
        sw (float): Self-weight factor. Defaults to 1.
    """
    name: str
    type: LoadType
    hx: float = 0
    hy: float = 0
    n: float = 0
    mx: float = 0
    my: float = 0
    sw: float = 1

@dataclass
class LineFoundationLoading(FoundationLoading):
    """
    Represents the loading applied to a line foundation.

    Attributes:
        name (str): The name of the loading case.
        type (LoadType): The type of load applied.
        hx (float): Horizontal load in the x-direction (kN/m). Defaults to 0.
        hy (float): Horizontal load in the y-direction (kN/m). Defaults to 0.
        n (float): Axial force (kN/m). Defaults to 0.
        my (float): Moment about the y-axis (kNm/m). Defaults to 0.
        sw (float): Self-weight factor. Defaults to 1.
    """
    name: str
    type: LoadType
    hx: float = 0
    hy: float = 0
    n: float = 0
    my: float = 0
    sw: float = 1