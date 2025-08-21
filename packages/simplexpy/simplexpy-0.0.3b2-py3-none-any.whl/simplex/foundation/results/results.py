from calendar import c
from curses.textpad import rectangle
from dataclasses import dataclass, field
from encodings import cp1026
from typing import ClassVar, List

from click import core
import simplex.core.protos.generated
import simplex.core.materials
import simplex.core
import simplex.core.protos
import simplex.core.protos.generated.Material
import simplex.core.protos.generated.Material.material_pb2
import simplex.core.protos.generated.Result.control_pb2 as control_pb2
from simplex.foundation.model.reinforcement import ReinfLayer, Zone
from enum import Enum
from abc import ABC, abstractmethod
import simplex

class Direction(Enum):
    WIDTH = "width"
    LENGTH = "length"
    BOTH = "both"

@dataclass
class RCResults:
    _side_results: list

    widthGuid: ClassVar[str] = ""
    lengthGuid: ClassVar[str] = ""

    @staticmethod
    def _from_proto(proto):

        RCResults.widthGuid = proto.project.output.foundation[0].concrete_input.concrete_width.id.guid
        RCResults.lengthGuid = proto.project.output.foundation[0].concrete_input.concrete_length.id.guid

        return RCResults(
            _side_results=proto.project.output.rc,
        )
    
    def _filter_controls(self, elem_guid, concrete_type):
        # Filter by elemGuid
        filtered_by_elem = [item for item in self._side_results if item.elem_guid == elem_guid]
        # Then filter by concreteType inside each item's 'controls'
        result = []
        for item in filtered_by_elem:
            result.extend([ctrl for ctrl in item.controls if ctrl.concrete_type == concrete_type])
        return result

    def anchorage_bottom(self, direction: Direction = Direction.BOTH):
        controller = control_pb2.CONTROL_TYPE_CONCRETE_ANCHORAGE_BTM
        if direction == Direction.WIDTH:
            return self._filter_controls(RCResults.widthGuid, controller)[0].values["anchorage_length"]
        elif direction == Direction.LENGTH:
            return self._filter_controls(RCResults.lengthGuid, controller)[0].values["anchorage_length"]
        elif direction == Direction.BOTH:
            return [
                self._filter_controls(RCResults.widthGuid, controller)[0].values["anchorage_length"],
                self._filter_controls(RCResults.lengthGuid, controller)[0].values["anchorage_length"]
            ]
        else:
            raise ValueError("Invalid direction")

    def anchorage_top(self, direction: Direction = Direction.BOTH):
        controller = control_pb2.CONTROL_TYPE_CONCRETE_ANCHORAGE_TOP
        if direction == Direction.WIDTH:
            return self._filter_controls(RCResults.widthGuid, controller)[0].values["anchorage_length"]
        elif direction == Direction.LENGTH:
            return self._filter_controls(RCResults.lengthGuid, controller)[0].values["anchorage_length"]
        elif direction == Direction.BOTH:
            return [
                self._filter_controls(RCResults.widthGuid, controller)[0].values["anchorage_length"],
                self._filter_controls(RCResults.lengthGuid, controller)[0].values["anchorage_length"]
            ]
        else:
            raise ValueError("Invalid direction")

    def concrete_moment_negative(self, direction: Direction = Direction.BOTH):
        controller = control_pb2.CONTROL_TYPE_CONCRETE_NEGATIVE_MOMENT_M1
        if direction == Direction.WIDTH:
            return self._filter_controls(RCResults.widthGuid, controller)[0]
        elif direction == Direction.LENGTH:
            return self._filter_controls(RCResults.lengthGuid, controller)[0]
        elif direction == Direction.BOTH:
            return [
                self._filter_controls(RCResults.widthGuid, controller)
                + self._filter_controls(RCResults.lengthGuid, controller)
            ]
        else:
            raise ValueError("Invalid direction")

    def concrete_moment_positive(self, direction: Direction = Direction.BOTH):
        controller = control_pb2.CONTROL_TYPE_CONCRETE_POSITIVE_MOMENT_M1
        if direction == Direction.WIDTH:
            return self._filter_controls(RCResults.widthGuid, controller)[0]
        elif direction == Direction.LENGTH:
            return self._filter_controls(RCResults.lengthGuid, controller)[0]
        elif direction == Direction.BOTH:
            return [
                self._filter_controls(RCResults.widthGuid, controller)
                + self._filter_controls(RCResults.lengthGuid, controller)
            ]
        else:
            raise ValueError("Invalid direction")

    def concrete_normal_force(self, direction: Direction = Direction.BOTH):
        controller = control_pb2.CONTROL_TYPE_CONCRETE_AXIAL_FORCE
        if direction == Direction.WIDTH:
            return self._filter_controls(RCResults.widthGuid, controller)[0]
        elif direction == Direction.LENGTH:
            return self._filter_controls(RCResults.lengthGuid, controller)
        elif direction == Direction.BOTH:
            return [
                self._filter_controls(RCResults.widthGuid, controller)
                + self._filter_controls(RCResults.lengthGuid, controller)
            ]
        else:
            raise ValueError("Invalid direction")

    def concrete_shear(self, direction: Direction = Direction.BOTH):
        controller = control_pb2.CONTROL_TYPE_CONCRETE_SHEAR_FORCE
        if direction == Direction.WIDTH:
            return self._filter_controls(RCResults.widthGuid, controller)[0]
        elif direction == Direction.LENGTH:
            return self._filter_controls(RCResults.lengthGuid, controller)[0]
        elif direction == Direction.BOTH:
            return [
                self._filter_controls(RCResults.widthGuid, controller)
                + self._filter_controls(RCResults.lengthGuid, controller)
            ]
        else:
            raise ValueError("Invalid direction")


@dataclass
class FoundationResults:
    _controls: list

    @staticmethod
    def from_proto(proto):
        return FoundationResults(
            _controls=proto.project.output.foundation[0].controls,
        )
    
    @property
    def concrete_punching_perimeter_capacity(self):
        result =  [x for x in self._controls if x.concrete_type == control_pb2.CONTROL_TYPE_CONCRETE_PUNCHING_PERIMETER]
        return result[0] if result else None

    @property
    def concrete_punching_column(self):
        result =  [x for x in self._controls if x.concrete_type == control_pb2.CONTROL_TYPE_CONCRETE_PUNCHING_COLUMN]
        return result[0] if result else None

    @property
    def unreinforced_concrete_capacity(self):
        result = [x for x in self._controls if x.foundation_type.type == control_pb2.CONTROL_TYPE_FOUNDATION_UNREINFORCED]
        return result[0] if result else None

    @property
    def sliding_capacity(self):
        result = [x for x in self._controls if x.foundation_type.type == control_pb2.CONTROL_TYPE_FOUNDATION_SLIDING]
        return result[0] if result else None

    @property
    def overturning_capacity(self):
        result = [x for x in self._controls if x.foundation_type.type == control_pb2.CONTROL_TYPE_FOUNDATION_OVERTURNING]
        return result[0] if result else None

    @property
    def settlement_capacity(self):
        result = [x for x in self._controls if x.foundation_type.type == control_pb2.CONTROL_TYPE_FOUNDATION_SETTLEMENT]
        return result[0] if result else None

    @property
    def uplift_capacity(self):
        result = [x for x in self._controls if x.foundation_type.type == control_pb2.CONTROL_TYPE_FOUNDATION_UPLIFT]
        return result[0] if result else None

    @property
    def bearing_capacity(self):
        result = [x for x in self._controls if x.foundation_type.type == control_pb2.CONTROL_TYPE_FOUNDATION_BEARING]
        return result[0] if result else None

@dataclass
class LCombResults:
    @staticmethod
    def from_proto(proto):
        return LCombResults()


@dataclass
class Results:
    rc: RCResults
    foundation: FoundationResults
    lcombs: LCombResults

    @classmethod
    def from_proto(cls, proto):
        return cls(
            rc=RCResults._from_proto(proto),
            foundation=FoundationResults.from_proto(proto),
            lcombs=LCombResults.from_proto(proto)
        )

    @property
    def worst_utilisation(self) -> object:
        """
        Find the object with the highest utilization value across all RC and foundation results.
        
        Returns:
            object: The object with the highest utilization value, or None if no utilization values are available
        """
        worst_object = None
        worst_utilization = 0.0
        
        # Check foundation results
        foundation_worst = self._worst_utilisation_foundation()
        if foundation_worst is not None:
            worst_object = foundation_worst
            worst_utilization = foundation_worst.utilization
        
        # Check RC results
        rc_worst = self._worst_utilisation_rc()
        if rc_worst is not None:
            if worst_object is None or rc_worst.utilization > worst_utilization:
                worst_object = rc_worst
        
        return worst_object

    def _worst_utilisation_foundation(self) -> object:
        """
        Find the foundation object with the highest utilization value.
        
        Returns:
            object: The foundation object with the highest utilization value, or None if no utilization values are available
        """
        UTILISATION_KEY = "utilization"
        
        worst_object = None
        worst_utilization = 0.0
        
        foundation_properties = [
            self.foundation.concrete_punching_perimeter_capacity,
            self.foundation.concrete_punching_column,
            self.foundation.sliding_capacity,
            self.foundation.bearing_capacity,
            self.foundation.overturning_capacity,
            self.foundation.uplift_capacity,
            self.foundation.settlement_capacity,
            self.foundation.unreinforced_concrete_capacity
        ]
        
        for prop in foundation_properties:
            if prop is not None and hasattr(prop, UTILISATION_KEY):
                try:
                    util_value = prop.utilization
                    if util_value > worst_utilization:
                        worst_utilization = util_value
                        worst_object = prop
                except (AttributeError, TypeError):
                    pass
        
        return worst_object

    def _worst_utilisation_rc(self) -> object:
        """
        Find the RC object with the highest utilization value.
        
        Returns:
            object: The RC object with the highest utilization value, or None if no utilization values are available
        """
        UTILISATION_KEY = "utilization"
        
        worst_object = None
        worst_utilization = 0.0
        
        rc_methods = [
            lambda: self.rc.concrete_moment_positive(),
            lambda: self.rc.concrete_moment_negative(),
            lambda: self.rc.concrete_shear(),
            lambda: self.rc.concrete_normal_force(),
            lambda: self.rc.anchorage_bottom(),
            lambda: self.rc.anchorage_top()
        ]
        
        for method in rc_methods:
            try:
                result = method()
                if result is not None:
                    # Handle both single results and lists of results
                    if isinstance(result, list):
                        for item in result:
                            if hasattr(item, UTILISATION_KEY):
                                try:
                                    util_value = item.utilization
                                    if util_value > worst_utilization:
                                        worst_utilization = util_value
                                        worst_object = item
                                except (AttributeError, TypeError):
                                    pass
                    elif hasattr(result, UTILISATION_KEY):
                        try:
                            util_value = result.utilization
                            if util_value > worst_utilization:
                                worst_utilization = util_value
                                worst_object = result
                        except (AttributeError, TypeError):
                            pass
            except (AttributeError, TypeError, IndexError):
                pass
        
        return worst_object

@dataclass
class DesignResults(ABC):
    
    @abstractmethod
    def __init__(self):
        pass

@dataclass
class DesignFoundationResult(DesignResults):
    length: float
    width: float
    height: float
    _concrete_material: str

    @property
    def volume(self) -> float:
        return self.length * self.width * self.height
    
    @property
    def CO_2_emission(self) -> float:
        co2_index = simplex.core.materials.Concrete.get_curr_co2_index(self._concrete_material)
        return co2_index * self.volume if co2_index else 0.0

    @classmethod
    def from_proto(cls, proto_input):
        # Select the first material where type == MTRL_CONCRETE

        concrete_material = next(
            (m.id.name for m in proto_input.mtrl_db if m.type == simplex.core.protos.generated.Material.material_pb2.MTRL_CONCRETE),
            None
        )
        
        rectangle = proto_input.structures[0].elements[0].foundation.simple_foundation.geometry.point_foundation.rectangle
        foundation_geometry = proto_input.structures[0].elements[0].foundation.simple_foundation.geometry
        return cls(
            length=rectangle.length,
            width=rectangle.width,
            height=foundation_geometry.height,
            _concrete_material=concrete_material,
        )


@dataclass
class DesignReinforcementResult(DesignResults):
    reinforcement_x: List[ReinfLayer]
    reinforcement_y: List[ReinfLayer]

    @classmethod
    def from_proto(cls, proto_input):

        grps_x = [x for x in proto_input.structures[0].elements[0].foundation.simple_foundation.concrete_parameters.rebars.grps if x.direction.x == 1.0]
        grps_y = [x for x in proto_input.structures[0].elements[0].foundation.simple_foundation.concrete_parameters.rebars.grps if x.direction.y == 1.0]

        reinforcement_x = []
        for grp in grps_x:
            layer = next((element for element in proto_input.structures[0].elements[0].foundation.simple_foundation.concrete_parameters.rebars.lays if element.grp_guid == grp.id.guid))

            reinforcement_x.append(
                ReinfLayer(
                    diameter=grp.diameter,
                    spacing=layer.s,
                    concrete_cover=layer.d,
                    zone=Zone(layer.zone),
                    material=None
                )
            )

        reinforcement_y = []
        for grp in grps_y:
            layer = next((element for element in proto_input.structures[0].elements[0].foundation.simple_foundation.concrete_parameters.rebars.lays if element.grp_guid == grp.id.guid))

            reinforcement_y.append(
                ReinfLayer(
                    diameter=grp.diameter,
                    spacing=layer.s,
                    concrete_cover=layer.d,
                    zone=Zone(layer.zone),
                    material=None
                )
            )

        return cls(
            reinforcement_x=reinforcement_x,
            reinforcement_y=reinforcement_y
        )