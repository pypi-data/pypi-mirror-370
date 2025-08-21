import input_pb2 as _input_pb2
from Utils import utils_pb2 as _utils_pb2
import structure_pb2 as _structure_pb2
from Utils import eurocode_pb2 as _eurocode_pb2
import sections_pb2 as _sections_pb2
from Material import material_pb2 as _material_pb2
from FireProtection import steel_pb2 as _steel_pb2
from FireProtection import timber_pb2 as _timber_pb2
from Soilmodel import soil_model_pb2 as _soil_model_pb2
import output_pb2 as _output_pb2
from Result import result_pb2 as _result_pb2
from Utils import log_pb2 as _log_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

from input_pb2 import Data
from output_pb2 import Data
from output_pb2 import LoadCombinationOutput
from output_pb2 import SupportResult
from output_pb2 import ElementResult
from Utils.log_pb2 import LogValue
from Utils.log_pb2 import LogEntry
from Utils.log_pb2 import Log
from Utils.log_pb2 import LogType
DESCRIPTOR: _descriptor.FileDescriptor
LOG_TYPE_ERROR: _log_pb2.LogType
LOG_TYPE_INFORMATION: _log_pb2.LogType
LOG_TYPE_UNSPECIFIED: _log_pb2.LogType
LOG_TYPE_WARNING: _log_pb2.LogType

class Data(_message.Message):
    __slots__ = ["input", "log", "output"]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    input: _input_pb2.Data
    log: _log_pb2.Log
    output: _output_pb2.Data
    def __init__(self, input: _Optional[_Union[_input_pb2.Data, _Mapping]] = ..., output: _Optional[_Union[_output_pb2.Data, _Mapping]] = ..., log: _Optional[_Union[_log_pb2.Log, _Mapping]] = ...) -> None: ...
