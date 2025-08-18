from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Position(_message.Message):
    __slots__ = ("latitude_deg", "longitude_deg")
    LATITUDE_DEG_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_DEG_FIELD_NUMBER: _ClassVar[int]
    latitude_deg: float
    longitude_deg: float
    def __init__(self, latitude_deg: _Optional[float] = ..., longitude_deg: _Optional[float] = ...) -> None: ...

class AngularRate(_message.Message):
    __slots__ = ("x_dps", "y_dps", "z_dps")
    X_DPS_FIELD_NUMBER: _ClassVar[int]
    Y_DPS_FIELD_NUMBER: _ClassVar[int]
    Z_DPS_FIELD_NUMBER: _ClassVar[int]
    x_dps: float
    y_dps: float
    z_dps: float
    def __init__(self, x_dps: _Optional[float] = ..., y_dps: _Optional[float] = ..., z_dps: _Optional[float] = ...) -> None: ...

class Acceleration(_message.Message):
    __slots__ = ("x_mps2", "y_mps2", "z_mps2")
    X_MPS2_FIELD_NUMBER: _ClassVar[int]
    Y_MPS2_FIELD_NUMBER: _ClassVar[int]
    Z_MPS2_FIELD_NUMBER: _ClassVar[int]
    x_mps2: float
    y_mps2: float
    z_mps2: float
    def __init__(self, x_mps2: _Optional[float] = ..., y_mps2: _Optional[float] = ..., z_mps2: _Optional[float] = ...) -> None: ...

class MagneticField(_message.Message):
    __slots__ = ("x_gauss", "y_gauss", "z_gauss")
    X_GAUSS_FIELD_NUMBER: _ClassVar[int]
    Y_GAUSS_FIELD_NUMBER: _ClassVar[int]
    Z_GAUSS_FIELD_NUMBER: _ClassVar[int]
    x_gauss: float
    y_gauss: float
    z_gauss: float
    def __init__(self, x_gauss: _Optional[float] = ..., y_gauss: _Optional[float] = ..., z_gauss: _Optional[float] = ...) -> None: ...

class Euler(_message.Message):
    __slots__ = ("roll_deg", "pitch_deg", "heading_deg")
    ROLL_DEG_FIELD_NUMBER: _ClassVar[int]
    PITCH_DEG_FIELD_NUMBER: _ClassVar[int]
    HEADING_DEG_FIELD_NUMBER: _ClassVar[int]
    roll_deg: float
    pitch_deg: float
    heading_deg: float
    def __init__(self, roll_deg: _Optional[float] = ..., pitch_deg: _Optional[float] = ..., heading_deg: _Optional[float] = ...) -> None: ...

class BodyVelocity(_message.Message):
    __slots__ = ("x_mps", "y_mps", "z_mps")
    X_MPS_FIELD_NUMBER: _ClassVar[int]
    Y_MPS_FIELD_NUMBER: _ClassVar[int]
    Z_MPS_FIELD_NUMBER: _ClassVar[int]
    x_mps: float
    y_mps: float
    z_mps: float
    def __init__(self, x_mps: _Optional[float] = ..., y_mps: _Optional[float] = ..., z_mps: _Optional[float] = ...) -> None: ...

class InertialVelocity(_message.Message):
    __slots__ = ("north_mps", "east_mps", "down_mps")
    NORTH_MPS_FIELD_NUMBER: _ClassVar[int]
    EAST_MPS_FIELD_NUMBER: _ClassVar[int]
    DOWN_MPS_FIELD_NUMBER: _ClassVar[int]
    north_mps: float
    east_mps: float
    down_mps: float
    def __init__(self, north_mps: _Optional[float] = ..., east_mps: _Optional[float] = ..., down_mps: _Optional[float] = ...) -> None: ...

class WaterCurrent(_message.Message):
    __slots__ = ("speed_mps", "direction_deg")
    SPEED_MPS_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_DEG_FIELD_NUMBER: _ClassVar[int]
    speed_mps: float
    direction_deg: float
    def __init__(self, speed_mps: _Optional[float] = ..., direction_deg: _Optional[float] = ...) -> None: ...

class FuelGauge(_message.Message):
    __slots__ = ("voltage_V", "current_A", "state_of_charge_percent")
    VOLTAGE_V_FIELD_NUMBER: _ClassVar[int]
    CURRENT_A_FIELD_NUMBER: _ClassVar[int]
    STATE_OF_CHARGE_PERCENT_FIELD_NUMBER: _ClassVar[int]
    voltage_V: float
    current_A: float
    state_of_charge_percent: float
    def __init__(self, voltage_V: _Optional[float] = ..., current_A: _Optional[float] = ..., state_of_charge_percent: _Optional[float] = ...) -> None: ...

class VehicleData(_message.Message):
    __slots__ = ("position", "position_source", "position_ttag_ns_steady", "attitude", "attitude_source", "attitude_ttag_ns_steady", "angular_rate", "angular_rate_source", "angular_rate_ttag_ns_steady", "acceleration", "acceleration_source", "acceleration_ttag_ns_steady", "magnetic_field", "magnetic_field_source", "magnetic_field_ttag_ns_steady", "depth_m", "depth_source", "depth_ttag_ns_steady", "altitude_m", "altitude_source", "altitude_ttag_ns_steady", "speed_mps", "speed_source", "speed_ttag_ns_steady", "course_deg", "course_source", "course_ttag_ns_steady", "body_velocity", "body_velocity_source", "body_velocity_ttag_ns_steady", "water_current", "water_current_source", "water_current_ttag_ns_steady", "water_relative_speed_mps", "water_relative_speed_source", "water_relative_speed_ttag_ns_steady", "fuel_gauge", "fuel_gauge_source", "fuel_gauge_ttag_ns_steady")
    class DataSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DS_NODATA: _ClassVar[VehicleData.DataSource]
        DS_IMU: _ClassVar[VehicleData.DataSource]
        DS_AHRS: _ClassVar[VehicleData.DataSource]
        DS_GPS: _ClassVar[VehicleData.DataSource]
        DS_DEPTH: _ClassVar[VehicleData.DataSource]
        DS_ALTITUDE: _ClassVar[VehicleData.DataSource]
        DS_SPEED: _ClassVar[VehicleData.DataSource]
        DS_ESTIMATION: _ClassVar[VehicleData.DataSource]
        DS_COMPUTATION: _ClassVar[VehicleData.DataSource]
        DS_SIMULATION: _ClassVar[VehicleData.DataSource]
        DS_INS: _ClassVar[VehicleData.DataSource]
    DS_NODATA: VehicleData.DataSource
    DS_IMU: VehicleData.DataSource
    DS_AHRS: VehicleData.DataSource
    DS_GPS: VehicleData.DataSource
    DS_DEPTH: VehicleData.DataSource
    DS_ALTITUDE: VehicleData.DataSource
    DS_SPEED: VehicleData.DataSource
    DS_ESTIMATION: VehicleData.DataSource
    DS_COMPUTATION: VehicleData.DataSource
    DS_SIMULATION: VehicleData.DataSource
    DS_INS: VehicleData.DataSource
    POSITION_FIELD_NUMBER: _ClassVar[int]
    POSITION_SOURCE_FIELD_NUMBER: _ClassVar[int]
    POSITION_TTAG_NS_STEADY_FIELD_NUMBER: _ClassVar[int]
    ATTITUDE_FIELD_NUMBER: _ClassVar[int]
    ATTITUDE_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ATTITUDE_TTAG_NS_STEADY_FIELD_NUMBER: _ClassVar[int]
    ANGULAR_RATE_FIELD_NUMBER: _ClassVar[int]
    ANGULAR_RATE_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ANGULAR_RATE_TTAG_NS_STEADY_FIELD_NUMBER: _ClassVar[int]
    ACCELERATION_FIELD_NUMBER: _ClassVar[int]
    ACCELERATION_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ACCELERATION_TTAG_NS_STEADY_FIELD_NUMBER: _ClassVar[int]
    MAGNETIC_FIELD_FIELD_NUMBER: _ClassVar[int]
    MAGNETIC_FIELD_SOURCE_FIELD_NUMBER: _ClassVar[int]
    MAGNETIC_FIELD_TTAG_NS_STEADY_FIELD_NUMBER: _ClassVar[int]
    DEPTH_M_FIELD_NUMBER: _ClassVar[int]
    DEPTH_SOURCE_FIELD_NUMBER: _ClassVar[int]
    DEPTH_TTAG_NS_STEADY_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_M_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ALTITUDE_TTAG_NS_STEADY_FIELD_NUMBER: _ClassVar[int]
    SPEED_MPS_FIELD_NUMBER: _ClassVar[int]
    SPEED_SOURCE_FIELD_NUMBER: _ClassVar[int]
    SPEED_TTAG_NS_STEADY_FIELD_NUMBER: _ClassVar[int]
    COURSE_DEG_FIELD_NUMBER: _ClassVar[int]
    COURSE_SOURCE_FIELD_NUMBER: _ClassVar[int]
    COURSE_TTAG_NS_STEADY_FIELD_NUMBER: _ClassVar[int]
    BODY_VELOCITY_FIELD_NUMBER: _ClassVar[int]
    BODY_VELOCITY_SOURCE_FIELD_NUMBER: _ClassVar[int]
    BODY_VELOCITY_TTAG_NS_STEADY_FIELD_NUMBER: _ClassVar[int]
    WATER_CURRENT_FIELD_NUMBER: _ClassVar[int]
    WATER_CURRENT_SOURCE_FIELD_NUMBER: _ClassVar[int]
    WATER_CURRENT_TTAG_NS_STEADY_FIELD_NUMBER: _ClassVar[int]
    WATER_RELATIVE_SPEED_MPS_FIELD_NUMBER: _ClassVar[int]
    WATER_RELATIVE_SPEED_SOURCE_FIELD_NUMBER: _ClassVar[int]
    WATER_RELATIVE_SPEED_TTAG_NS_STEADY_FIELD_NUMBER: _ClassVar[int]
    FUEL_GAUGE_FIELD_NUMBER: _ClassVar[int]
    FUEL_GAUGE_SOURCE_FIELD_NUMBER: _ClassVar[int]
    FUEL_GAUGE_TTAG_NS_STEADY_FIELD_NUMBER: _ClassVar[int]
    position: Position
    position_source: VehicleData.DataSource
    position_ttag_ns_steady: int
    attitude: Euler
    attitude_source: VehicleData.DataSource
    attitude_ttag_ns_steady: int
    angular_rate: AngularRate
    angular_rate_source: VehicleData.DataSource
    angular_rate_ttag_ns_steady: int
    acceleration: Acceleration
    acceleration_source: VehicleData.DataSource
    acceleration_ttag_ns_steady: int
    magnetic_field: MagneticField
    magnetic_field_source: VehicleData.DataSource
    magnetic_field_ttag_ns_steady: int
    depth_m: float
    depth_source: VehicleData.DataSource
    depth_ttag_ns_steady: int
    altitude_m: float
    altitude_source: VehicleData.DataSource
    altitude_ttag_ns_steady: int
    speed_mps: float
    speed_source: VehicleData.DataSource
    speed_ttag_ns_steady: int
    course_deg: float
    course_source: VehicleData.DataSource
    course_ttag_ns_steady: int
    body_velocity: BodyVelocity
    body_velocity_source: VehicleData.DataSource
    body_velocity_ttag_ns_steady: int
    water_current: WaterCurrent
    water_current_source: VehicleData.DataSource
    water_current_ttag_ns_steady: int
    water_relative_speed_mps: float
    water_relative_speed_source: VehicleData.DataSource
    water_relative_speed_ttag_ns_steady: int
    fuel_gauge: FuelGauge
    fuel_gauge_source: VehicleData.DataSource
    fuel_gauge_ttag_ns_steady: int
    def __init__(self, position: _Optional[_Union[Position, _Mapping]] = ..., position_source: _Optional[_Union[VehicleData.DataSource, str]] = ..., position_ttag_ns_steady: _Optional[int] = ..., attitude: _Optional[_Union[Euler, _Mapping]] = ..., attitude_source: _Optional[_Union[VehicleData.DataSource, str]] = ..., attitude_ttag_ns_steady: _Optional[int] = ..., angular_rate: _Optional[_Union[AngularRate, _Mapping]] = ..., angular_rate_source: _Optional[_Union[VehicleData.DataSource, str]] = ..., angular_rate_ttag_ns_steady: _Optional[int] = ..., acceleration: _Optional[_Union[Acceleration, _Mapping]] = ..., acceleration_source: _Optional[_Union[VehicleData.DataSource, str]] = ..., acceleration_ttag_ns_steady: _Optional[int] = ..., magnetic_field: _Optional[_Union[MagneticField, _Mapping]] = ..., magnetic_field_source: _Optional[_Union[VehicleData.DataSource, str]] = ..., magnetic_field_ttag_ns_steady: _Optional[int] = ..., depth_m: _Optional[float] = ..., depth_source: _Optional[_Union[VehicleData.DataSource, str]] = ..., depth_ttag_ns_steady: _Optional[int] = ..., altitude_m: _Optional[float] = ..., altitude_source: _Optional[_Union[VehicleData.DataSource, str]] = ..., altitude_ttag_ns_steady: _Optional[int] = ..., speed_mps: _Optional[float] = ..., speed_source: _Optional[_Union[VehicleData.DataSource, str]] = ..., speed_ttag_ns_steady: _Optional[int] = ..., course_deg: _Optional[float] = ..., course_source: _Optional[_Union[VehicleData.DataSource, str]] = ..., course_ttag_ns_steady: _Optional[int] = ..., body_velocity: _Optional[_Union[BodyVelocity, _Mapping]] = ..., body_velocity_source: _Optional[_Union[VehicleData.DataSource, str]] = ..., body_velocity_ttag_ns_steady: _Optional[int] = ..., water_current: _Optional[_Union[WaterCurrent, _Mapping]] = ..., water_current_source: _Optional[_Union[VehicleData.DataSource, str]] = ..., water_current_ttag_ns_steady: _Optional[int] = ..., water_relative_speed_mps: _Optional[float] = ..., water_relative_speed_source: _Optional[_Union[VehicleData.DataSource, str]] = ..., water_relative_speed_ttag_ns_steady: _Optional[int] = ..., fuel_gauge: _Optional[_Union[FuelGauge, _Mapping]] = ..., fuel_gauge_source: _Optional[_Union[VehicleData.DataSource, str]] = ..., fuel_gauge_ttag_ns_steady: _Optional[int] = ...) -> None: ...

class AhrsIf(_message.Message):
    __slots__ = ("angular_rate", "acceleration", "magfield", "euler")
    ANGULAR_RATE_FIELD_NUMBER: _ClassVar[int]
    ACCELERATION_FIELD_NUMBER: _ClassVar[int]
    MAGFIELD_FIELD_NUMBER: _ClassVar[int]
    EULER_FIELD_NUMBER: _ClassVar[int]
    angular_rate: AngularRate
    acceleration: Acceleration
    magfield: MagneticField
    euler: Euler
    def __init__(self, angular_rate: _Optional[_Union[AngularRate, _Mapping]] = ..., acceleration: _Optional[_Union[Acceleration, _Mapping]] = ..., magfield: _Optional[_Union[MagneticField, _Mapping]] = ..., euler: _Optional[_Union[Euler, _Mapping]] = ...) -> None: ...

class AltitudeIf(_message.Message):
    __slots__ = ("altitude_m",)
    ALTITUDE_M_FIELD_NUMBER: _ClassVar[int]
    altitude_m: float
    def __init__(self, altitude_m: _Optional[float] = ...) -> None: ...

class BatteryIf(_message.Message):
    __slots__ = ("voltage_V", "current_A", "state_of_charge_percent")
    VOLTAGE_V_FIELD_NUMBER: _ClassVar[int]
    CURRENT_A_FIELD_NUMBER: _ClassVar[int]
    STATE_OF_CHARGE_PERCENT_FIELD_NUMBER: _ClassVar[int]
    voltage_V: float
    current_A: float
    state_of_charge_percent: int
    def __init__(self, voltage_V: _Optional[float] = ..., current_A: _Optional[float] = ..., state_of_charge_percent: _Optional[int] = ...) -> None: ...

class DepthIf(_message.Message):
    __slots__ = ("depth_m",)
    DEPTH_M_FIELD_NUMBER: _ClassVar[int]
    depth_m: float
    def __init__(self, depth_m: _Optional[float] = ...) -> None: ...

class EffectorIf(_message.Message):
    __slots__ = ("command",)
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    command: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, command: _Optional[_Iterable[float]] = ...) -> None: ...

class InsIf(_message.Message):
    __slots__ = ("angular_rate", "acceleration", "magfield", "euler", "body_velocity", "position", "inertial_velocity")
    ANGULAR_RATE_FIELD_NUMBER: _ClassVar[int]
    ACCELERATION_FIELD_NUMBER: _ClassVar[int]
    MAGFIELD_FIELD_NUMBER: _ClassVar[int]
    EULER_FIELD_NUMBER: _ClassVar[int]
    BODY_VELOCITY_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    INERTIAL_VELOCITY_FIELD_NUMBER: _ClassVar[int]
    angular_rate: AngularRate
    acceleration: Acceleration
    magfield: MagneticField
    euler: Euler
    body_velocity: BodyVelocity
    position: Position
    inertial_velocity: InertialVelocity
    def __init__(self, angular_rate: _Optional[_Union[AngularRate, _Mapping]] = ..., acceleration: _Optional[_Union[Acceleration, _Mapping]] = ..., magfield: _Optional[_Union[MagneticField, _Mapping]] = ..., euler: _Optional[_Union[Euler, _Mapping]] = ..., body_velocity: _Optional[_Union[BodyVelocity, _Mapping]] = ..., position: _Optional[_Union[Position, _Mapping]] = ..., inertial_velocity: _Optional[_Union[InertialVelocity, _Mapping]] = ...) -> None: ...

class GpsIf(_message.Message):
    __slots__ = ("rmc_data", "gga_data")
    class RmcData(_message.Message):
        __slots__ = ("latitude_deg", "longitude_deg", "ground_speed_kt", "course_true_deg")
        LATITUDE_DEG_FIELD_NUMBER: _ClassVar[int]
        LONGITUDE_DEG_FIELD_NUMBER: _ClassVar[int]
        GROUND_SPEED_KT_FIELD_NUMBER: _ClassVar[int]
        COURSE_TRUE_DEG_FIELD_NUMBER: _ClassVar[int]
        latitude_deg: float
        longitude_deg: float
        ground_speed_kt: float
        course_true_deg: float
        def __init__(self, latitude_deg: _Optional[float] = ..., longitude_deg: _Optional[float] = ..., ground_speed_kt: _Optional[float] = ..., course_true_deg: _Optional[float] = ...) -> None: ...
    class GgaData(_message.Message):
        __slots__ = ("latitude_deg", "longitude_deg", "altitude_m", "num_satellite", "fix_quality")
        class FixQuality(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            FQ_INVALID: _ClassVar[GpsIf.GgaData.FixQuality]
            FQ_GPS: _ClassVar[GpsIf.GgaData.FixQuality]
            FQ_DGPS: _ClassVar[GpsIf.GgaData.FixQuality]
            FQ_PPS: _ClassVar[GpsIf.GgaData.FixQuality]
            FQ_RTK_FIXED: _ClassVar[GpsIf.GgaData.FixQuality]
            FQ_RTK_FLOAT: _ClassVar[GpsIf.GgaData.FixQuality]
            FQ_ESTIMATED: _ClassVar[GpsIf.GgaData.FixQuality]
            FQ_MANUAL: _ClassVar[GpsIf.GgaData.FixQuality]
            FQ_SIMULATION: _ClassVar[GpsIf.GgaData.FixQuality]
        FQ_INVALID: GpsIf.GgaData.FixQuality
        FQ_GPS: GpsIf.GgaData.FixQuality
        FQ_DGPS: GpsIf.GgaData.FixQuality
        FQ_PPS: GpsIf.GgaData.FixQuality
        FQ_RTK_FIXED: GpsIf.GgaData.FixQuality
        FQ_RTK_FLOAT: GpsIf.GgaData.FixQuality
        FQ_ESTIMATED: GpsIf.GgaData.FixQuality
        FQ_MANUAL: GpsIf.GgaData.FixQuality
        FQ_SIMULATION: GpsIf.GgaData.FixQuality
        LATITUDE_DEG_FIELD_NUMBER: _ClassVar[int]
        LONGITUDE_DEG_FIELD_NUMBER: _ClassVar[int]
        ALTITUDE_M_FIELD_NUMBER: _ClassVar[int]
        NUM_SATELLITE_FIELD_NUMBER: _ClassVar[int]
        FIX_QUALITY_FIELD_NUMBER: _ClassVar[int]
        latitude_deg: float
        longitude_deg: float
        altitude_m: float
        num_satellite: int
        fix_quality: GpsIf.GgaData.FixQuality
        def __init__(self, latitude_deg: _Optional[float] = ..., longitude_deg: _Optional[float] = ..., altitude_m: _Optional[float] = ..., num_satellite: _Optional[int] = ..., fix_quality: _Optional[_Union[GpsIf.GgaData.FixQuality, str]] = ...) -> None: ...
    RMC_DATA_FIELD_NUMBER: _ClassVar[int]
    GGA_DATA_FIELD_NUMBER: _ClassVar[int]
    rmc_data: GpsIf.RmcData
    gga_data: GpsIf.GgaData
    def __init__(self, rmc_data: _Optional[_Union[GpsIf.RmcData, _Mapping]] = ..., gga_data: _Optional[_Union[GpsIf.GgaData, _Mapping]] = ...) -> None: ...

class ObstacleIf(_message.Message):
    __slots__ = ("id", "circle", "polygon", "zone_type", "is_stationary", "lifespan_s", "course_deg", "speed_mps", "point_of_interest")
    class ZoneType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ZONE_KEEP_OUT: _ClassVar[ObstacleIf.ZoneType]
        ZONE_KEEP_IN: _ClassVar[ObstacleIf.ZoneType]
    ZONE_KEEP_OUT: ObstacleIf.ZoneType
    ZONE_KEEP_IN: ObstacleIf.ZoneType
    class Circle(_message.Message):
        __slots__ = ("origin", "radius_m")
        ORIGIN_FIELD_NUMBER: _ClassVar[int]
        RADIUS_M_FIELD_NUMBER: _ClassVar[int]
        origin: Position
        radius_m: float
        def __init__(self, origin: _Optional[_Union[Position, _Mapping]] = ..., radius_m: _Optional[float] = ...) -> None: ...
    class Polygon(_message.Message):
        __slots__ = ("vertices",)
        VERTICES_FIELD_NUMBER: _ClassVar[int]
        vertices: _containers.RepeatedCompositeFieldContainer[Position]
        def __init__(self, vertices: _Optional[_Iterable[_Union[Position, _Mapping]]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    CIRCLE_FIELD_NUMBER: _ClassVar[int]
    POLYGON_FIELD_NUMBER: _ClassVar[int]
    ZONE_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_STATIONARY_FIELD_NUMBER: _ClassVar[int]
    LIFESPAN_S_FIELD_NUMBER: _ClassVar[int]
    COURSE_DEG_FIELD_NUMBER: _ClassVar[int]
    SPEED_MPS_FIELD_NUMBER: _ClassVar[int]
    POINT_OF_INTEREST_FIELD_NUMBER: _ClassVar[int]
    id: str
    circle: ObstacleIf.Circle
    polygon: ObstacleIf.Polygon
    zone_type: ObstacleIf.ZoneType
    is_stationary: bool
    lifespan_s: float
    course_deg: float
    speed_mps: float
    point_of_interest: Position
    def __init__(self, id: _Optional[str] = ..., circle: _Optional[_Union[ObstacleIf.Circle, _Mapping]] = ..., polygon: _Optional[_Union[ObstacleIf.Polygon, _Mapping]] = ..., zone_type: _Optional[_Union[ObstacleIf.ZoneType, str]] = ..., is_stationary: bool = ..., lifespan_s: _Optional[float] = ..., course_deg: _Optional[float] = ..., speed_mps: _Optional[float] = ..., point_of_interest: _Optional[_Union[Position, _Mapping]] = ...) -> None: ...

class Obstacles(_message.Message):
    __slots__ = ("ttag_system", "ttag_steady_ns", "obstacles")
    TTAG_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TTAG_STEADY_NS_FIELD_NUMBER: _ClassVar[int]
    OBSTACLES_FIELD_NUMBER: _ClassVar[int]
    ttag_system: _timestamp_pb2.Timestamp
    ttag_steady_ns: int
    obstacles: _containers.RepeatedCompositeFieldContainer[ObstacleIf]
    def __init__(self, ttag_system: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ttag_steady_ns: _Optional[int] = ..., obstacles: _Optional[_Iterable[_Union[ObstacleIf, _Mapping]]] = ...) -> None: ...

class Path(_message.Message):
    __slots__ = ("ttag_system", "ttag_steady_ns", "path", "obstacles", "speed_mps", "start", "end_local", "end_global", "global_path")
    TTAG_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TTAG_STEADY_NS_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    OBSTACLES_FIELD_NUMBER: _ClassVar[int]
    SPEED_MPS_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_LOCAL_FIELD_NUMBER: _ClassVar[int]
    END_GLOBAL_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_PATH_FIELD_NUMBER: _ClassVar[int]
    ttag_system: _timestamp_pb2.Timestamp
    ttag_steady_ns: int
    path: _containers.RepeatedCompositeFieldContainer[Position]
    obstacles: _containers.RepeatedCompositeFieldContainer[ObstacleIf]
    speed_mps: float
    start: Position
    end_local: Position
    end_global: Position
    global_path: _containers.RepeatedCompositeFieldContainer[Position]
    def __init__(self, ttag_system: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., ttag_steady_ns: _Optional[int] = ..., path: _Optional[_Iterable[_Union[Position, _Mapping]]] = ..., obstacles: _Optional[_Iterable[_Union[ObstacleIf, _Mapping]]] = ..., speed_mps: _Optional[float] = ..., start: _Optional[_Union[Position, _Mapping]] = ..., end_local: _Optional[_Union[Position, _Mapping]] = ..., end_global: _Optional[_Union[Position, _Mapping]] = ..., global_path: _Optional[_Iterable[_Union[Position, _Mapping]]] = ...) -> None: ...

class VehicleStateIf(_message.Message):
    __slots__ = ("ttag_ns", "vehicle_data", "mode", "health_items", "fault_response")
    class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        VS_STANDBY: _ClassVar[VehicleStateIf.Mode]
        VS_MANUAL: _ClassVar[VehicleStateIf.Mode]
        VS_HEALTHY_MISSION: _ClassVar[VehicleStateIf.Mode]
        VS_UNHEALTHY_MISSION: _ClassVar[VehicleStateIf.Mode]
        VS_LOITER: _ClassVar[VehicleStateIf.Mode]
        VS_MISSION_PLANNING: _ClassVar[VehicleStateIf.Mode]
        VS_UNHEALTHY_MISSION_PLANNING: _ClassVar[VehicleStateIf.Mode]
    VS_STANDBY: VehicleStateIf.Mode
    VS_MANUAL: VehicleStateIf.Mode
    VS_HEALTHY_MISSION: VehicleStateIf.Mode
    VS_UNHEALTHY_MISSION: VehicleStateIf.Mode
    VS_LOITER: VehicleStateIf.Mode
    VS_MISSION_PLANNING: VehicleStateIf.Mode
    VS_UNHEALTHY_MISSION_PLANNING: VehicleStateIf.Mode
    class FaultResponseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FR_IGNORE: _ClassVar[VehicleStateIf.FaultResponseType]
        FR_HALT: _ClassVar[VehicleStateIf.FaultResponseType]
        FR_LOITER: _ClassVar[VehicleStateIf.FaultResponseType]
        FR_GO_RALLY: _ClassVar[VehicleStateIf.FaultResponseType]
        FR_GO_FIRST: _ClassVar[VehicleStateIf.FaultResponseType]
        FR_GO_LAST: _ClassVar[VehicleStateIf.FaultResponseType]
        FR_GO_LAUNCH: _ClassVar[VehicleStateIf.FaultResponseType]
        FR_CUSTOM: _ClassVar[VehicleStateIf.FaultResponseType]
    FR_IGNORE: VehicleStateIf.FaultResponseType
    FR_HALT: VehicleStateIf.FaultResponseType
    FR_LOITER: VehicleStateIf.FaultResponseType
    FR_GO_RALLY: VehicleStateIf.FaultResponseType
    FR_GO_FIRST: VehicleStateIf.FaultResponseType
    FR_GO_LAST: VehicleStateIf.FaultResponseType
    FR_GO_LAUNCH: VehicleStateIf.FaultResponseType
    FR_CUSTOM: VehicleStateIf.FaultResponseType
    class HealthItem(_message.Message):
        __slots__ = ("index", "uid", "sensor_id", "is_valid", "enabled", "is_healthy")
        INDEX_FIELD_NUMBER: _ClassVar[int]
        UID_FIELD_NUMBER: _ClassVar[int]
        SENSOR_ID_FIELD_NUMBER: _ClassVar[int]
        IS_VALID_FIELD_NUMBER: _ClassVar[int]
        ENABLED_FIELD_NUMBER: _ClassVar[int]
        IS_HEALTHY_FIELD_NUMBER: _ClassVar[int]
        index: int
        uid: str
        sensor_id: int
        is_valid: bool
        enabled: bool
        is_healthy: bool
        def __init__(self, index: _Optional[int] = ..., uid: _Optional[str] = ..., sensor_id: _Optional[int] = ..., is_valid: bool = ..., enabled: bool = ..., is_healthy: bool = ...) -> None: ...
    class FaultResponse(_message.Message):
        __slots__ = ("response_type", "health_item_index")
        RESPONSE_TYPE_FIELD_NUMBER: _ClassVar[int]
        HEALTH_ITEM_INDEX_FIELD_NUMBER: _ClassVar[int]
        response_type: VehicleStateIf.FaultResponseType
        health_item_index: int
        def __init__(self, response_type: _Optional[_Union[VehicleStateIf.FaultResponseType, str]] = ..., health_item_index: _Optional[int] = ...) -> None: ...
    TTAG_NS_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_DATA_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    HEALTH_ITEMS_FIELD_NUMBER: _ClassVar[int]
    FAULT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ttag_ns: int
    vehicle_data: VehicleData
    mode: VehicleStateIf.Mode
    health_items: _containers.RepeatedCompositeFieldContainer[VehicleStateIf.HealthItem]
    fault_response: VehicleStateIf.FaultResponse
    def __init__(self, ttag_ns: _Optional[int] = ..., vehicle_data: _Optional[_Union[VehicleData, _Mapping]] = ..., mode: _Optional[_Union[VehicleStateIf.Mode, str]] = ..., health_items: _Optional[_Iterable[_Union[VehicleStateIf.HealthItem, _Mapping]]] = ..., fault_response: _Optional[_Union[VehicleStateIf.FaultResponse, _Mapping]] = ...) -> None: ...

class MavlinkMissionItemInt(_message.Message):
    __slots__ = ("target_system", "target_component", "mission_type", "seq", "command", "frame", "current", "autocontinue", "param1", "param2", "param3", "param4", "x", "y", "z")
    TARGET_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    TARGET_COMPONENT_FIELD_NUMBER: _ClassVar[int]
    MISSION_TYPE_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    FRAME_FIELD_NUMBER: _ClassVar[int]
    CURRENT_FIELD_NUMBER: _ClassVar[int]
    AUTOCONTINUE_FIELD_NUMBER: _ClassVar[int]
    PARAM1_FIELD_NUMBER: _ClassVar[int]
    PARAM2_FIELD_NUMBER: _ClassVar[int]
    PARAM3_FIELD_NUMBER: _ClassVar[int]
    PARAM4_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    Z_FIELD_NUMBER: _ClassVar[int]
    target_system: int
    target_component: int
    mission_type: int
    seq: int
    command: int
    frame: int
    current: bool
    autocontinue: bool
    param1: float
    param2: float
    param3: float
    param4: float
    x: int
    y: int
    z: float
    def __init__(self, target_system: _Optional[int] = ..., target_component: _Optional[int] = ..., mission_type: _Optional[int] = ..., seq: _Optional[int] = ..., command: _Optional[int] = ..., frame: _Optional[int] = ..., current: bool = ..., autocontinue: bool = ..., param1: _Optional[float] = ..., param2: _Optional[float] = ..., param3: _Optional[float] = ..., param4: _Optional[float] = ..., x: _Optional[int] = ..., y: _Optional[int] = ..., z: _Optional[float] = ...) -> None: ...

class MavlinkMission(_message.Message):
    __slots__ = ("mission_items", "fence_items", "rally_items")
    MISSION_ITEMS_FIELD_NUMBER: _ClassVar[int]
    FENCE_ITEMS_FIELD_NUMBER: _ClassVar[int]
    RALLY_ITEMS_FIELD_NUMBER: _ClassVar[int]
    mission_items: _containers.RepeatedCompositeFieldContainer[MavlinkMissionItemInt]
    fence_items: _containers.RepeatedCompositeFieldContainer[MavlinkMissionItemInt]
    rally_items: _containers.RepeatedCompositeFieldContainer[MavlinkMissionItemInt]
    def __init__(self, mission_items: _Optional[_Iterable[_Union[MavlinkMissionItemInt, _Mapping]]] = ..., fence_items: _Optional[_Iterable[_Union[MavlinkMissionItemInt, _Mapping]]] = ..., rally_items: _Optional[_Iterable[_Union[MavlinkMissionItemInt, _Mapping]]] = ...) -> None: ...
