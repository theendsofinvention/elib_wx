# coding=utf-8
"""
Abstract base class for Weather classes
"""
import typing

import dataclasses
import elib_miz

from elib_wx import Config, avwx
from elib_wx.values.value import (
    Pressure, Temperature, Visibility, WindDirection,
    WindSpeed,
)
from elib_wx.weather_dcs import DCSWeather


@dataclasses.dataclass
class WeatherABC:
    """
    Abstract base class for Weather classes
    """
    source: str
    source_type: str
    _station_icao: str
    station_name: str
    raw_metar_str: str
    metar_data: avwx.metar.MetarData
    metar_units: avwx.structs.Units

    altimeter: Pressure
    cloud_layers: typing.List[avwx.structs.Cloud]
    visibility: Visibility
    temperature: Temperature
    dew_point: Temperature
    wind_speed: WindSpeed
    wind_direction: WindDirection
    wind_direction_range: typing.List[WindDirection]
    wind_gust: WindSpeed
    date_time: avwx.structs.Timestamp
    other: typing.List[str]
    remarks: str
    wind_direction_is_variable: bool = False
    original_dcs_weather: typing.Optional[DCSWeather] = None

    @property
    def station_icao(self):
        """
        ICAO code for station this weather object comes from.

        If no ICAO has been set, returns the dummy ICAO code (defaults to "XXXX")

        :return: ICAO station code
        :rtype: str
        """
        try:
            return self._station_icao
        except AttributeError:
            return Config.dummy_icao_code

    @station_icao.setter
    def station_icao(self, value: str):
        """
        Any update to the ICAO code also triggers an update for the station name.

        :param value: new ICAO value
        :type value: str
        """
        if value != Config.dummy_icao_code:
            avwx.core.valid_station(value)
        self._station_icao = value
        self._set_station_name()

    def apply_to_mission_dict(self, mission: elib_miz.Mission) -> elib_miz.Mission:
        """
        Generates a DCSWeather object from self and creates a new elib_miz.Mission object out of it

        :param mission: mission to modify
        :type mission: elib_miz.Mission
        :return: new, modified mission
        :rtype: elib_miz.Mission
        """
        raise NotImplementedError()

    def apply_to_miz(self, source_file: str, out_file: str, *, overwrite: bool = False) -> None:
        """
        Applies this Weather object to a MIZ file

        :param source_file: path to the source MIZ file to edit
        :type source_file: str
        :param out_file: path to the MIZ file to write
        :type out_file: str
        :param overwrite: allow overwriting existing MIZ files
        :type overwrite: bool
        """
        raise NotImplementedError()

    def generate_dcs_weather(self) -> DCSWeather:
        """
        Creates a DCSWeather from this Weather object.

        All DCS specific constraints regarding the different values are enforced

        :return: a valid DCSWeather object
        :rtype: DCSWeather
        """
        raise NotImplementedError()

    def fill_from_metar_data(self) -> None:
        """
        Creates the Weather object from METAR data
        """
        raise NotImplementedError()

    def _set_station_name(self) -> None:
        """
        Sets the name of the airport for this station from the ICAO code.

        If the ICAO code isn't found in the database, returns "unknown station".
        """
        raise NotImplementedError()

    def _from_icao(self):
        """
        Creates the Weather object from a given ICAO code
        """
        raise NotImplementedError()

    def _from_metar_string(self):
        """
        Creates the Weather object from a given METAR string
        """
        raise NotImplementedError()

    def _from_miz_file(self):
        """
        Creates the Weather object from an existing MIZ file
        """
        raise NotImplementedError()

    @property
    def is_cavok(self) -> bool:
        """
        :return: True if CAVOK conditions are fulfilled
        :rtype: bool
        """
        raise NotImplementedError()

    def _wind_as_str(self, spoken: bool) -> str:
        """
        :param spoken: tailor outputs for TTS engines
        :type spoken: bool
        :return: wind as string
        :rtype: str
        """
        raise NotImplementedError()

    def _visibility_as_str(self, spoken: bool) -> str:
        """
        :param spoken: tailor outputs for TTS engines
        :type spoken: bool
        :return: visibility as string
        :rtype: str
        """
        raise NotImplementedError()

    def _temperature_as_str(self, spoken: bool) -> str:
        """
        :param spoken: tailor outputs for TTS engines
        :type spoken: bool
        :return: temperature as string
        :rtype: str
        """
        raise NotImplementedError()

    def _dew_point_as_str(self, spoken: bool) -> str:
        """
        :param spoken: tailor outputs for TTS engines
        :type spoken: bool
        :return: dew point as string
        :rtype: str
        """
        raise NotImplementedError()

    def _altimeter_as_str(self, spoken: bool) -> str:
        """
        :param spoken: tailor outputs for TTS engines
        :type spoken: bool
        :return: altimeter as string
        :rtype: str
        """
        raise NotImplementedError()

    def _others_as_str(self) -> str:
        """
        :return: other as string
        :rtype: str
        """
        raise NotImplementedError()

    def _clouds_as_str(self, spoken: bool) -> str:
        """
        :param spoken: tailor outputs for TTS engines
        :type spoken: bool
        :return: cloud as string
        :rtype: str
        """
        raise NotImplementedError()

    def _remarks_as_str(self, spoken: bool) -> str:
        """
        :param spoken: tailor outputs for TTS engines
        :type spoken: bool
        :return: remarks as string
        :rtype: str
        """
        raise NotImplementedError()

    def _make_str_intro(self, spoken: bool) -> str:
        """
        :param spoken: tailor outputs for TTS engines
        :type spoken: bool
        :return: intro as string
        :rtype: str
        """
        raise NotImplementedError()

    def _as_str(self, spoken: bool) -> str:
        """
        :param spoken: tailor outputs for TTS engines
        :type spoken: bool
        :return: weather as string
        :rtype: str
        """
        raise NotImplementedError()

    def as_str(self) -> str:
        """
        :return: current weather as string
        :rtype: str
        """
        return self._as_str(spoken=False)

    def as_speech(self) -> str:
        """
        :return: Weather as spoken text
        :rtype: str
        """
        return self._as_str(spoken=True)
