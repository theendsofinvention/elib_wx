# coding=utf-8
"""
Main interface module for elib_wx
"""

import elib_miz

from elib_wx import (
    LOGGER, airports_db, exc, weather_dcs_generate, weather_from_icao, weather_from_metar_data,
    weather_from_metar_string, weather_from_miz, weather_to_mission, weather_to_miz, weather_translate,
)
from elib_wx.weather_abc import WeatherABC
from elib_wx.weather_dcs import DCSWeather


class Weather(WeatherABC):  # pylint: disable=too-many-instance-attributes
    """
    Represents a "weather" situation
    """

    def __init__(self, source: str) -> None:
        if not isinstance(source, str):
            raise exc.InvalidWeatherSourceError(source, f'expected a string, got {type(source)}')
        self.source = source
        if len(source) == 4:
            self._from_icao()
        elif source.lower().endswith('.miz'):
            self._from_miz_file()
        else:
            self._from_metar_string()

    @property
    def is_cavok(self) -> bool:
        if self.visibility.value() < 9999:
            return False
        for cloud_layer in self.cloud_layers:
            if cloud_layer.modifier:
                if 'TCU' in str(cloud_layer.modifier):
                    return False
                if 'CB' in str(cloud_layer.modifier):
                    return False
            if cloud_layer.altitude and cloud_layer.altitude < 50:
                return False
        return True

    def apply_to_mission_dict(self, mission: elib_miz.Mission) -> elib_miz.Mission:
        """
        Generates a DCSWeather object from self and creates a new elib_miz.Mission object out of it

        :param mission: mission to modify
        :type mission: elib_miz.Mission
        :return: new, modified mission
        :rtype: elib_miz.Mission
        """
        return weather_to_mission.apply_weather_to_mission_dict(self, mission)

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
        weather_to_miz.apply_weather_to_miz(weather_object=self,
                                            source_file=source_file,
                                            out_file=out_file,
                                            overwrite=overwrite)

    def generate_dcs_weather(self) -> DCSWeather:
        """
        Creates a DCSWeather from this Weather object.

        All DCS specific constraints regarding the different values are enforced

        :return: a valid DCSWeather object
        :rtype: DCSWeather
        """
        return weather_dcs_generate.generate_dcs_weather(weather_object=self)

    def fill_from_metar_data(self):
        weather_from_metar_data.weather_from_metar_data(weather_object=self)

    def _set_station_name(self) -> None:
        """
        Sets the name of the airport for this station from the ICAO code.

        If the ICAO code isn't found in the database, returns "unknown station".
        """
        self.station_name = airports_db.get_airport_name_from_icao(self.station_icao)

    def _from_icao(self):
        weather_from_icao.weather_from_icao(weather_object=self)

    def _from_metar_string(self):
        weather_from_metar_string.weather_from_metar_string(weather_object=self)

    def _from_miz_file(self):
        weather_from_miz.weather_from_miz_file(self)

    def _wind_as_str(self, spoken: bool) -> str:
        return weather_translate.wind(weather_object=self, spoken=spoken)

    def _visibility_as_str(self, spoken: bool) -> str:
        return weather_translate.visibility(weather_object=self, spoken=spoken)

    def _temperature_as_str(self, spoken: bool) -> str:
        return weather_translate.temperature(weather_object=self, spoken=spoken)

    def _dew_point_as_str(self, spoken: bool) -> str:
        return weather_translate.dew_point(weather_object=self, spoken=spoken)

    def _altimeter_as_str(self, spoken: bool) -> str:
        return weather_translate.altimeter(weather_object=self, spoken=spoken)

    def _others_as_str(self) -> str:
        return weather_translate.other(self)

    def _clouds_as_str(self, spoken: bool) -> str:
        return weather_translate.clouds(weather_object=self, spoken=spoken)

    def _remarks_as_str(self, spoken: bool) -> str:
        return weather_translate.remarks(weather_object=self, spoken=spoken)

    def _make_str_intro(self, spoken: bool) -> str:
        return weather_translate.intro(weather_object=self, spoken=spoken)

    def _as_str(self, spoken: bool) -> str:
        intro = self._make_str_intro(spoken=spoken)
        wind = self._wind_as_str(spoken=spoken)
        visibility = self._visibility_as_str(spoken=spoken)
        temperature = self._temperature_as_str(spoken=spoken)
        dew_point = self._dew_point_as_str(spoken=spoken)
        altimeter = self._altimeter_as_str(spoken=spoken)
        other = self._others_as_str()
        clouds = self._clouds_as_str(spoken=spoken)
        try:
            remarks = self._remarks_as_str(spoken=spoken) or ''
        except (IndexError, ValueError):
            LOGGER.warning('failed to parse remarks: %s', self.remarks)
            remarks = ''
        _result = [intro, wind, visibility, temperature, dew_point, altimeter, other, clouds, remarks]
        _result = [x for x in _result if x != '']
        result = ' '.join(_result)
        return result.replace('  ', ' ')
