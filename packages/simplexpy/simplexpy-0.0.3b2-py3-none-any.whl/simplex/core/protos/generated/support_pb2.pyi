from Utils import utils_pb2 as _utils_pb2
import stage_pb2 as _stage_pb2
from Utils import utils_pb2 as _utils_pb2_1
from Utils import topology_pb2 as _topology_pb2
from Geometry import geometry_pb2 as _geometry_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from Utils.utils_pb2 import SemVer
from Utils.utils_pb2 import ID
from Utils.utils_pb2 import Owner
from stage_pb2 import Data
from stage_pb2 import Beam
from stage_pb2 import Foundation
from stage_pb2 import RetainingWall
from stage_pb2 import Pile
from stage_pb2 import Element
from stage_pb2 import RCSpecific
from stage_pb2 import RC
from stage_pb2 import SteelSpecific
from stage_pb2 import TimberSpecific
from stage_pb2 import SoilSpecific
from stage_pb2 import SupportElementConnection
from stage_pb2 import Support
from stage_pb2 import ExposureClass
from stage_pb2 import LifeCategory
from stage_pb2 import EnvironmentalClass
from stage_pb2 import SupportLevel
DESCRIPTOR: _descriptor.FileDescriptor
ENVIROMENTAL_CLASS_AGGRESSIVE: _stage_pb2.EnvironmentalClass
ENVIROMENTAL_CLASS_EXTRA_AGGRESSIVE: _stage_pb2.EnvironmentalClass
ENVIROMENTAL_CLASS_MODERATE: _stage_pb2.EnvironmentalClass
ENVIROMENTAL_CLASS_PASSIVE: _stage_pb2.EnvironmentalClass
ENVIROMENTAL_CLASS_UNSPECIFIED: _stage_pb2.EnvironmentalClass
EXPOSURE_CLASS_UNSPECIFIED: _stage_pb2.ExposureClass
EXPOSURE_CLASS_X0: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XA1: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XA2: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XA3: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XC1: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XC2: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XC3: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XC4: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XD1: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XD2: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XD3: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XF1: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XF2: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XF3: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XF4: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XS1: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XS2: _stage_pb2.ExposureClass
EXPOSURE_CLASS_XS3: _stage_pb2.ExposureClass
LIFE_CATEGORY_L100: _stage_pb2.LifeCategory
LIFE_CATEGORY_L20: _stage_pb2.LifeCategory
LIFE_CATEGORY_L50: _stage_pb2.LifeCategory
LIFE_CATEGORY_UNSPECIFIED: _stage_pb2.LifeCategory
OWNER_COMPANY: _utils_pb2_1.Owner
OWNER_OFFICE: _utils_pb2_1.Owner
OWNER_STRUSOFT: _utils_pb2_1.Owner
OWNER_UNSPECIFIED: _utils_pb2_1.Owner
OWNER_USER: _utils_pb2_1.Owner
SUPPORT_LEVEL_BOTTOM: _stage_pb2.SupportLevel
SUPPORT_LEVEL_CENTER: _stage_pb2.SupportLevel
SUPPORT_LEVEL_TOP: _stage_pb2.SupportLevel
SUPPORT_LEVEL_UNSPECIFIED: _stage_pb2.SupportLevel

class Data(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: _utils_pb2_1.ID
    def __init__(self, id: _Optional[_Union[_utils_pb2_1.ID, _Mapping]] = ...) -> None: ...
