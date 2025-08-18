from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Color(_message.Message):
    __slots__ = ("red", "green", "blue", "alpha")
    RED_FIELD_NUMBER: _ClassVar[int]
    GREEN_FIELD_NUMBER: _ClassVar[int]
    BLUE_FIELD_NUMBER: _ClassVar[int]
    ALPHA_FIELD_NUMBER: _ClassVar[int]
    red: float
    green: float
    blue: float
    alpha: _wrappers_pb2.FloatValue
    def __init__(self, red: _Optional[float] = ..., green: _Optional[float] = ..., blue: _Optional[float] = ..., alpha: _Optional[_Union[_wrappers_pb2.FloatValue, _Mapping]] = ...) -> None: ...

class FramePrediction(_message.Message):
    __slots__ = ("x", "y", "width", "height", "confidence", "class_id", "class_name", "class_color")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    CLASS_ID_FIELD_NUMBER: _ClassVar[int]
    CLASS_NAME_FIELD_NUMBER: _ClassVar[int]
    CLASS_COLOR_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    width: float
    height: float
    confidence: float
    class_id: int
    class_name: str
    class_color: Color
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ..., width: _Optional[float] = ..., height: _Optional[float] = ..., confidence: _Optional[float] = ..., class_id: _Optional[int] = ..., class_name: _Optional[str] = ..., class_color: _Optional[_Union[Color, _Mapping]] = ...) -> None: ...

class Frame(_message.Message):
    __slots__ = ("frame_number", "ttag_system", "ttag_steady_ns", "prediction_duration_ms", "predictions")
    FRAME_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TTAG_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TTAG_STEADY_NS_FIELD_NUMBER: _ClassVar[int]
    PREDICTION_DURATION_MS_FIELD_NUMBER: _ClassVar[int]
    PREDICTIONS_FIELD_NUMBER: _ClassVar[int]
    frame_number: int
    ttag_system: _timestamp_pb2.Timestamp
    ttag_steady_ns: int
    prediction_duration_ms: int
    predictions: _containers.RepeatedCompositeFieldContainer[FramePrediction]
    def __init__(self, frame_number: _Optional[int] = ..., ttag_system: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ttag_steady_ns: _Optional[int] = ..., prediction_duration_ms: _Optional[int] = ..., predictions: _Optional[_Iterable[_Union[FramePrediction, _Mapping]]] = ...) -> None: ...

class OccupancyMap(_message.Message):
    __slots__ = ("ttag_system", "ttag_steady_ns", "type", "scope", "compression", "lat_deg", "lon_deg", "tl_lat_deg", "tl_lon_deg", "br_lat_deg", "br_lon_deg", "width_m", "height_m", "width_px", "height_px", "grid")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[OccupancyMap.Type]
        EMPTY: _ClassVar[OccupancyMap.Type]
        OCCUPIED: _ClassVar[OccupancyMap.Type]
        MERGED: _ClassVar[OccupancyMap.Type]
    UNKNOWN: OccupancyMap.Type
    EMPTY: OccupancyMap.Type
    OCCUPIED: OccupancyMap.Type
    MERGED: OccupancyMap.Type
    class Scope(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LOCAL: _ClassVar[OccupancyMap.Scope]
        GLOBAL: _ClassVar[OccupancyMap.Scope]
    LOCAL: OccupancyMap.Scope
    GLOBAL: OccupancyMap.Scope
    class Compression(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        RAW: _ClassVar[OccupancyMap.Compression]
        GZ: _ClassVar[OccupancyMap.Compression]
        ZSTD: _ClassVar[OccupancyMap.Compression]
        JPEG: _ClassVar[OccupancyMap.Compression]
        PNG: _ClassVar[OccupancyMap.Compression]
    RAW: OccupancyMap.Compression
    GZ: OccupancyMap.Compression
    ZSTD: OccupancyMap.Compression
    JPEG: OccupancyMap.Compression
    PNG: OccupancyMap.Compression
    TTAG_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TTAG_STEADY_NS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    COMPRESSION_FIELD_NUMBER: _ClassVar[int]
    LAT_DEG_FIELD_NUMBER: _ClassVar[int]
    LON_DEG_FIELD_NUMBER: _ClassVar[int]
    TL_LAT_DEG_FIELD_NUMBER: _ClassVar[int]
    TL_LON_DEG_FIELD_NUMBER: _ClassVar[int]
    BR_LAT_DEG_FIELD_NUMBER: _ClassVar[int]
    BR_LON_DEG_FIELD_NUMBER: _ClassVar[int]
    WIDTH_M_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_M_FIELD_NUMBER: _ClassVar[int]
    WIDTH_PX_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_PX_FIELD_NUMBER: _ClassVar[int]
    GRID_FIELD_NUMBER: _ClassVar[int]
    ttag_system: _timestamp_pb2.Timestamp
    ttag_steady_ns: int
    type: OccupancyMap.Type
    scope: OccupancyMap.Scope
    compression: OccupancyMap.Compression
    lat_deg: float
    lon_deg: float
    tl_lat_deg: float
    tl_lon_deg: float
    br_lat_deg: float
    br_lon_deg: float
    width_m: float
    height_m: float
    width_px: int
    height_px: int
    grid: bytes
    def __init__(self, ttag_system: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ttag_steady_ns: _Optional[int] = ..., type: _Optional[_Union[OccupancyMap.Type, str]] = ..., scope: _Optional[_Union[OccupancyMap.Scope, str]] = ..., compression: _Optional[_Union[OccupancyMap.Compression, str]] = ..., lat_deg: _Optional[float] = ..., lon_deg: _Optional[float] = ..., tl_lat_deg: _Optional[float] = ..., tl_lon_deg: _Optional[float] = ..., br_lat_deg: _Optional[float] = ..., br_lon_deg: _Optional[float] = ..., width_m: _Optional[float] = ..., height_m: _Optional[float] = ..., width_px: _Optional[int] = ..., height_px: _Optional[int] = ..., grid: _Optional[bytes] = ...) -> None: ...

class ObjectTrack(_message.Message):
    __slots__ = ("ttag_system", "ttag_steady_ns", "track_id", "branch_id", "source_id", "age_s", "update_count", "latitude_deg", "longitude_deg", "heading_deg", "speed_mps", "covariance", "is_confirmed", "is_predicted")
    TTAG_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TTAG_STEADY_NS_FIELD_NUMBER: _ClassVar[int]
    TRACK_ID_FIELD_NUMBER: _ClassVar[int]
    BRANCH_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    AGE_S_FIELD_NUMBER: _ClassVar[int]
    UPDATE_COUNT_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_DEG_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_DEG_FIELD_NUMBER: _ClassVar[int]
    HEADING_DEG_FIELD_NUMBER: _ClassVar[int]
    SPEED_MPS_FIELD_NUMBER: _ClassVar[int]
    COVARIANCE_FIELD_NUMBER: _ClassVar[int]
    IS_CONFIRMED_FIELD_NUMBER: _ClassVar[int]
    IS_PREDICTED_FIELD_NUMBER: _ClassVar[int]
    ttag_system: _timestamp_pb2.Timestamp
    ttag_steady_ns: int
    track_id: int
    branch_id: int
    source_id: int
    age_s: float
    update_count: int
    latitude_deg: float
    longitude_deg: float
    heading_deg: float
    speed_mps: float
    covariance: _containers.RepeatedScalarFieldContainer[float]
    is_confirmed: bool
    is_predicted: bool
    def __init__(self, ttag_system: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ttag_steady_ns: _Optional[int] = ..., track_id: _Optional[int] = ..., branch_id: _Optional[int] = ..., source_id: _Optional[int] = ..., age_s: _Optional[float] = ..., update_count: _Optional[int] = ..., latitude_deg: _Optional[float] = ..., longitude_deg: _Optional[float] = ..., heading_deg: _Optional[float] = ..., speed_mps: _Optional[float] = ..., covariance: _Optional[_Iterable[float]] = ..., is_confirmed: bool = ..., is_predicted: bool = ...) -> None: ...

class ObjectTrackList(_message.Message):
    __slots__ = ("ttag_system", "ttag_steady_ns", "source_id", "tracks")
    TTAG_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TTAG_STEADY_NS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    TRACKS_FIELD_NUMBER: _ClassVar[int]
    ttag_system: _timestamp_pb2.Timestamp
    ttag_steady_ns: int
    source_id: int
    tracks: _containers.RepeatedCompositeFieldContainer[ObjectTrack]
    def __init__(self, ttag_system: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ttag_steady_ns: _Optional[int] = ..., source_id: _Optional[int] = ..., tracks: _Optional[_Iterable[_Union[ObjectTrack, _Mapping]]] = ...) -> None: ...

class Vertex(_message.Message):
    __slots__ = ("latitude_deg", "longitude_deg")
    LATITUDE_DEG_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_DEG_FIELD_NUMBER: _ClassVar[int]
    latitude_deg: float
    longitude_deg: float
    def __init__(self, latitude_deg: _Optional[float] = ..., longitude_deg: _Optional[float] = ...) -> None: ...

class TrackingZone(_message.Message):
    __slots__ = ("ttag_system", "ttag_steady_ns", "vertices")
    TTAG_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TTAG_STEADY_NS_FIELD_NUMBER: _ClassVar[int]
    VERTICES_FIELD_NUMBER: _ClassVar[int]
    ttag_system: _timestamp_pb2.Timestamp
    ttag_steady_ns: int
    vertices: _containers.RepeatedCompositeFieldContainer[Vertex]
    def __init__(self, ttag_system: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ttag_steady_ns: _Optional[int] = ..., vertices: _Optional[_Iterable[_Union[Vertex, _Mapping]]] = ...) -> None: ...
