# coding=utf-8
"""
Creates a Weather object from a given ICAO
"""

from elib_wx import LOGGER, avwx
from elib_wx.weather_abc import WeatherABC


def weather_from_icao(weather_object: WeatherABC):
    """
    Creates a Weather object from a given ICAO

    :param weather_object: weather object to fill
    :type weather_object: WeatherABC
    """
    LOGGER.debug('building Weather from ICAO code')
    weather_object.source_type = 'ICAO'
    weather_object.station_icao = weather_object.source.upper()
    weather_object.raw_metar_str = avwx.metar.fetch(weather_object.station_icao)
    weather_object.metar_data, weather_object.metar_units = avwx.metar.parse(weather_object.station_icao,
                                                                             weather_object.raw_metar_str)
    weather_object.fill_from_metar_data()
