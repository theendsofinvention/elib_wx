# coding=utf-8
"""
Michael duPont - michael@mdupont.com
Original source: https://github.com/flyinactor91/AVWX-Engine
Modified by etcher@daribouca.net
"""
# pylint: disable=all
import typing
from datetime import datetime

from dataclasses import dataclass


@dataclass
class StationInfo:
    """
    Station info
    """
    city: str
    country: str
    elevation: float
    iata: str
    icao: str
    latitude: float
    longitude: float
    name: str
    priority: int
    state: str


@dataclass
class Units:
    """
    METAR/TAF units
    """
    altimeter: str
    altitude: str
    temperature: str
    visibility: str
    wind_speed: str


@dataclass
class Number:
    """
    Represents a number
    """
    repr: typing.Optional[str]
    value: typing.Optional[float]
    spoken: typing.Optional[str]


@dataclass
class Fraction(Number):
    """
    Represents a fractional number
    """
    numerator: int
    denominator: int
    normalized: str


@dataclass
class Timestamp:
    """
    Represents a date time object
    """
    repr: str
    dt: typing.Optional[datetime]


@dataclass
class Cloud:
    """
    Represents a cloud layer
    """
    repr: typing.Optional[str] = None
    type: typing.Optional[str] = None
    altitude: typing.Optional[int] = None
    modifier: typing.Optional[str] = None


@dataclass
class RemarksData:
    """
    Represents remark's data
    """
    dewpoint_decimal: typing.Optional[float] = None
    temperature_decimal: typing.Optional[float] = None


@dataclass
class ReportData:
    """
    Represents '(chared) report data'
    """
    raw: str
    remarks: str
    station: str
    time: Timestamp


@dataclass
class SharedData:
    """
    Represents shared data (same for TAF/METAR)
    """
    altimeter: Number
    clouds: typing.List[Cloud]
    flight_rules: str
    other: typing.List[str]
    sanitized: str
    visibility: Number
    wind_direction: Number
    wind_gust: Number
    wind_speed: Number


@dataclass
class MetarData:
    """
    Represents METAR specific data
    """
    raw: str
    remarks: str
    station: str
    time: Timestamp
    altimeter: Number
    clouds: typing.List[Cloud]
    flight_rules: str
    other: typing.List[str]
    sanitized: str
    visibility: Number
    wind_direction: Number
    wind_gust: Number
    wind_speed: Number
    dewpoint: Number
    remarks_info: RemarksData
    runway_visibility: typing.List[str]
    temperature: Number
    wind_variable_direction: typing.List[Number]


@dataclass
class TafLineData:
    """
    Represents TAF specific data
    """
    altimeter: Number
    clouds: typing.List[Cloud]
    flight_rules: str
    other: typing.List[str]
    sanitized: str
    visibility: Number
    wind_direction: Number
    wind_gust: Number
    wind_speed: Number
    end_time: Timestamp
    icing: typing.List[str]
    probability: Number
    raw: str
    start_time: Timestamp
    turbulance: typing.List[str]
    type: str
    wind_shear: str


@dataclass
class TafData:
    """
    Represents TAF specific data
    """
    raw: str
    remarks: str
    station: str
    time: Timestamp
    forecast: typing.List[TafLineData]  # noqa
    start_time: Timestamp
    end_time: Timestamp
    max_temp: typing.Optional[float] = None
    min_temp: typing.Optional[float] = None
    alts: typing.Optional[float] = None
    temps: typing.Optional[float] = None


@dataclass
class ReportTrans:
    """
    Represents transient data
    """
    altimeter: str
    clouds: str
    other: str
    visibility: str


@dataclass
class MetarTrans(ReportTrans):
    """
    Represents transient data
    """
    dewpoint: str
    remarks: dict
    temperature: str
    wind: str


@dataclass
class TafLineTrans(ReportTrans):
    """
    Represents transient data
    """
    icing: str
    turbulance: str
    wind: str
    wind_shear: str


@dataclass
class TafTrans:
    """
    Represents transient data
    """
    forecast: typing.List[TafLineTrans]  # noqa
    max_temp: str
    min_temp: str
    remarks: dict
