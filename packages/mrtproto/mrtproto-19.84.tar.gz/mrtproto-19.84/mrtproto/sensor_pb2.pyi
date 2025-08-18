from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

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

class Range(_message.Message):
    __slots__ = ("ttag_system", "ttag_steady_ns", "type", "range_m", "range_uncertainty_m", "max_range_m", "field_of_view_deg", "pose", "target_id")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Range.Type]
        ULTRASOUND: _ClassVar[Range.Type]
        INFRARED: _ClassVar[Range.Type]
        LASER: _ClassVar[Range.Type]
    UNKNOWN: Range.Type
    ULTRASOUND: Range.Type
    INFRARED: Range.Type
    LASER: Range.Type
    TTAG_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TTAG_STEADY_NS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    RANGE_M_FIELD_NUMBER: _ClassVar[int]
    RANGE_UNCERTAINTY_M_FIELD_NUMBER: _ClassVar[int]
    MAX_RANGE_M_FIELD_NUMBER: _ClassVar[int]
    FIELD_OF_VIEW_DEG_FIELD_NUMBER: _ClassVar[int]
    POSE_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    ttag_system: _timestamp_pb2.Timestamp
    ttag_steady_ns: int
    type: Range.Type
    range_m: float
    range_uncertainty_m: float
    max_range_m: float
    field_of_view_deg: float
    pose: Pose
    target_id: str
    def __init__(self, ttag_system: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ttag_steady_ns: _Optional[int] = ..., type: _Optional[_Union[Range.Type, str]] = ..., range_m: _Optional[float] = ..., range_uncertainty_m: _Optional[float] = ..., max_range_m: _Optional[float] = ..., field_of_view_deg: _Optional[float] = ..., pose: _Optional[_Union[Pose, _Mapping]] = ..., target_id: _Optional[str] = ...) -> None: ...

class TargetPosition(_message.Message):
    __slots__ = ("ttag_system", "ttag_steady_ns", "target_id", "lat_deg", "lon_deg", "confidence")
    TTAG_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TTAG_STEADY_NS_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    LAT_DEG_FIELD_NUMBER: _ClassVar[int]
    LON_DEG_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    ttag_system: _timestamp_pb2.Timestamp
    ttag_steady_ns: int
    target_id: str
    lat_deg: float
    lon_deg: float
    confidence: float
    def __init__(self, ttag_system: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ttag_steady_ns: _Optional[int] = ..., target_id: _Optional[str] = ..., lat_deg: _Optional[float] = ..., lon_deg: _Optional[float] = ..., confidence: _Optional[float] = ...) -> None: ...

class TargetPositions(_message.Message):
    __slots__ = ("ttag_system", "ttag_steady_ns", "positions")
    TTAG_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TTAG_STEADY_NS_FIELD_NUMBER: _ClassVar[int]
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    ttag_system: _timestamp_pb2.Timestamp
    ttag_steady_ns: int
    positions: _containers.RepeatedCompositeFieldContainer[TargetPosition]
    def __init__(self, ttag_system: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ttag_steady_ns: _Optional[int] = ..., positions: _Optional[_Iterable[_Union[TargetPosition, _Mapping]]] = ...) -> None: ...
