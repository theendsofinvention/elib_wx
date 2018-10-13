# coding=utf-8
"""
Builds a Weather object from METAR data as parsed by AVWX
"""
import random

from elib_wx import (
    LOGGER,
)
from elib_wx.values.value import (
    Pressure, Temperature, Visibility, WindDirection,
    WindSpeed,
)
from elib_wx.weather_abc import WeatherABC


def _make_altimeter(weather_object):
    if not weather_object.metar_data.altimeter:
        LOGGER.warning('no altimeter data found in METAR, using triangular randomized pressure '
                       '(low=720, high=790, mode= 760) [mmHg]')
        weather_object.altimeter = Pressure(int(random.triangular(720, 790, mode=760)))  # nosec
    else:
        weather_object.altimeter = Pressure(weather_object.metar_data.altimeter.value,
                                            weather_object.metar_units.altimeter)


def _make_visibility(weather_object):
    if not weather_object.metar_data.visibility:
        LOGGER.warning('no visibility data found in METAR, using triangular randomized visibility '
                       '(low=2000, high=20000, mode= 15000) [meters]')
        weather_object.visibility = Visibility(
            min((round(int(random.triangular(2000, 20000, mode=15000)), -2), 9999)))  # nosec
    else:
        if weather_object.metar_data.visibility.repr == 'P6':
            weather_object.visibility = Visibility(9999, 'm')
        elif weather_object.metar_data.visibility.repr == 'M1/4':
            weather_object.visibility = Visibility(400, 'm')
        else:
            weather_object.visibility = Visibility(weather_object.metar_data.visibility.value,
                                                   weather_object.metar_units.visibility)


def _make_temperature(weather_object):
    if weather_object.metar_data.temperature:
        weather_object.temperature = Temperature(weather_object.metar_data.temperature.value,
                                                 weather_object.metar_units.temperature)
    else:
        LOGGER.warning('no temperature value found in METAR, using triangular randomized temperature '
                       '(low=-10, high=40, mode= 18) [degrees Celsius]')
        weather_object.temperature = Temperature(round(int(random.triangular(-10, 40, mode=18)), 0), 'c')  # nosec


def _make_dew_point(weather_object):
    if weather_object.metar_data.dewpoint:
        weather_object.dew_point = Temperature(weather_object.metar_data.dewpoint.value,
                                               weather_object.metar_units.temperature)
    else:
        LOGGER.warning('no dew point data found in METAR, creating dummy dew point from temperature')
        weather_object.dew_point = weather_object.temperature.make_dummy_dew_point()


def _make_wind(weather_object):
    if not weather_object.metar_data.wind_speed:
        LOGGER.warning('no wind speed data found in METAR, using triangular randomized wind speed '
                       '(low=0, high=25, mode= 7) [knots]')
        weather_object.wind_speed = WindSpeed(random.triangular(0, 25, mode=7), 'kt')  # nosec
    else:
        weather_object.wind_speed = WindSpeed(weather_object.metar_data.wind_speed.value,
                                              weather_object.metar_units.wind_speed)
    if not weather_object.metar_data.wind_direction:
        LOGGER.warning('no wind direction data found in METAR, using random wind direction'
                       '(between 0 and 359) [degrees]')
        weather_object.wind_direction = WindDirection(random.randint(0, 359))  # nosec
    else:
        if weather_object.metar_data.wind_direction.repr == 'VRB':
            weather_object.wind_direction_is_variable = True
        weather_object.wind_direction = WindDirection(weather_object.metar_data.wind_direction.value)
    weather_object.wind_direction_range = [
        WindDirection(wind_dir.value)
        for wind_dir in weather_object.metar_data.wind_variable_direction
    ]
    if weather_object.metar_data.wind_gust:
        weather_object.wind_gust = WindSpeed(weather_object.metar_data.wind_gust.value,
                                             weather_object.metar_units.wind_speed)
    else:
        weather_object.wind_gust = WindSpeed(0)


def weather_from_metar_data(weather_object: WeatherABC):
    """
    Builds a Weather object from METAR data as parsed by AVWX

    :param weather_object: weather object to build
    :type weather_object: WeatherABC
    """
    LOGGER.debug('creating weather object based on METAR data')
    LOGGER.debug('METAR data: %s', weather_object.metar_data)
    LOGGER.debug('METAR units: %s', weather_object.metar_units)

    _make_altimeter(weather_object)
    _make_visibility(weather_object)
    weather_object.cloud_layers = [cloud_layer for cloud_layer in weather_object.metar_data.clouds]
    _make_temperature(weather_object)
    _make_dew_point(weather_object)
    _make_wind(weather_object)

    weather_object.date_time = weather_object.metar_data.time
    weather_object.other = weather_object.metar_data.other
    weather_object.remarks = weather_object.metar_data.remarks
    LOGGER.debug('resulting weather object: %s', repr(weather_object))  # pylint: disable=possibly-unused-variable
