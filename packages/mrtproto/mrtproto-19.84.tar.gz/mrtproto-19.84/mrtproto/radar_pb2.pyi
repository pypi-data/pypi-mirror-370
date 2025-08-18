from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATE_OFF: _ClassVar[State]
    STATE_STANDBY: _ClassVar[State]
    STATE_WARMING_UP: _ClassVar[State]
    STATE_TIMED_IDLE: _ClassVar[State]
    STATE_STOPPING: _ClassVar[State]
    STATE_SPINNING_DOWN: _ClassVar[State]
    STATE_STARTING: _ClassVar[State]
    STATE_SPINNING_UP: _ClassVar[State]
    STATE_TRANSMIT: _ClassVar[State]

class CommandType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMMAND_NONE: _ClassVar[CommandType]
    COMMAND_TURN_ON: _ClassVar[CommandType]
    COMMAND_TURN_OFF: _ClassVar[CommandType]
    COMMAND_SET_RANGE: _ClassVar[CommandType]
    COMMAND_SET_GAIN: _ClassVar[CommandType]
    COMMAND_SET_RAIN: _ClassVar[CommandType]
    COMMAND_SET_SEA: _ClassVar[CommandType]
STATE_OFF: State
STATE_STANDBY: State
STATE_WARMING_UP: State
STATE_TIMED_IDLE: State
STATE_STOPPING: State
STATE_SPINNING_DOWN: State
STATE_STARTING: State
STATE_SPINNING_UP: State
STATE_TRANSMIT: State
COMMAND_NONE: CommandType
COMMAND_TURN_ON: CommandType
COMMAND_TURN_OFF: CommandType
COMMAND_SET_RANGE: CommandType
COMMAND_SET_GAIN: CommandType
COMMAND_SET_RAIN: CommandType
COMMAND_SET_SEA: CommandType

class Pose(_message.Message):
    __slots__ = ("lat_deg", "lon_deg", "heading_deg", "position_covariance", "heading_error_deg")
    LAT_DEG_FIELD_NUMBER: _ClassVar[int]
    LON_DEG_FIELD_NUMBER: _ClassVar[int]
    HEADING_DEG_FIELD_NUMBER: _ClassVar[int]
    POSITION_COVARIANCE_FIELD_NUMBER: _ClassVar[int]
    HEADING_ERROR_DEG_FIELD_NUMBER: _ClassVar[int]
    lat_deg: float
    lon_deg: float
    heading_deg: float
    position_covariance: _containers.RepeatedScalarFieldContainer[float]
    heading_error_deg: float
    def __init__(self, lat_deg: _Optional[float] = ..., lon_deg: _Optional[float] = ..., heading_deg: _Optional[float] = ..., position_covariance: _Optional[_Iterable[float]] = ..., heading_error_deg: _Optional[float] = ...) -> None: ...

class Spokes(_message.Message):
    __slots__ = ("num_spoke", "first_spoke_index", "range_m", "spokes")
    NUM_SPOKE_FIELD_NUMBER: _ClassVar[int]
    FIRST_SPOKE_INDEX_FIELD_NUMBER: _ClassVar[int]
    RANGE_M_FIELD_NUMBER: _ClassVar[int]
    SPOKES_FIELD_NUMBER: _ClassVar[int]
    num_spoke: int
    first_spoke_index: int
    range_m: float
    spokes: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, num_spoke: _Optional[int] = ..., first_spoke_index: _Optional[int] = ..., range_m: _Optional[float] = ..., spokes: _Optional[_Iterable[bytes]] = ...) -> None: ...

class Info(_message.Message):
    __slots__ = ("timestamp", "ttag_steady_ns", "state", "gain", "rain", "sea", "range", "scan_speed", "spokes", "pose")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TTAG_STEADY_NS_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    GAIN_FIELD_NUMBER: _ClassVar[int]
    RAIN_FIELD_NUMBER: _ClassVar[int]
    SEA_FIELD_NUMBER: _ClassVar[int]
    RANGE_FIELD_NUMBER: _ClassVar[int]
    SCAN_SPEED_FIELD_NUMBER: _ClassVar[int]
    SPOKES_FIELD_NUMBER: _ClassVar[int]
    POSE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    ttag_steady_ns: int
    state: State
    gain: int
    rain: int
    sea: int
    range: int
    scan_speed: int
    spokes: Spokes
    pose: Pose
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ttag_steady_ns: _Optional[int] = ..., state: _Optional[_Union[State, str]] = ..., gain: _Optional[int] = ..., rain: _Optional[int] = ..., sea: _Optional[int] = ..., range: _Optional[int] = ..., scan_speed: _Optional[int] = ..., spokes: _Optional[_Union[Spokes, _Mapping]] = ..., pose: _Optional[_Union[Pose, _Mapping]] = ...) -> None: ...

class Command(_message.Message):
    __slots__ = ("command", "value")
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    command: CommandType
    value: int
    def __init__(self, command: _Optional[_Union[CommandType, str]] = ..., value: _Optional[int] = ...) -> None: ...
