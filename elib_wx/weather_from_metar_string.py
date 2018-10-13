# coding=utf-8
"""
Creates a Weather object from a METAR string
"""

from elib_wx import LOGGER, avwx, utils
from elib_wx.weather_abc import WeatherABC


def weather_from_metar_string(weather_object: WeatherABC):
    """
    Creates a Weather object from a METAR string

    :param weather_object: weather object to fill
    :type weather_object: WeatherABC
    """
    LOGGER.debug('building Weather from METAR string')
    weather_object.source_type = 'METAR'
    LOGGER.debug('extracting station from METAR')
    weather_object.station_icao = utils.extract_station_from_metar_str(weather_object.source)
    LOGGER.debug('station: %s', weather_object.station_icao)
    weather_object.raw_metar_str = weather_object.source
    weather_object.metar_data, weather_object.metar_units = avwx.metar.parse(weather_object.station_icao,
                                                                             weather_object.raw_metar_str)
    weather_object.fill_from_metar_data()
