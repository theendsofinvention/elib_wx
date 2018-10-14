# coding=utf-8
"""
Generates a DCSWeather object from self and creates a new elib_miz.Mission object out of it
"""

import copy
import pprint

import elib_miz

from elib_wx import LOGGER
from elib_wx.weather_abc import WeatherABC


def apply_weather_to_mission_dict(weather_object: WeatherABC, mission: elib_miz.Mission) -> elib_miz.Mission:
    """
    Generates a DCSWeather object from self and creates a new elib_miz.Mission object out of it

    :param weather_object: weather object to apply to mission dictionary
    :type weather_object: WeatherABC
    :param mission: mission to modify
    :type mission: elib_miz.Mission
    :return: new, modified mission
    :rtype: elib_miz.Mission
    """
    LOGGER.info('generating DCS weather')
    dcs_weather = weather_object.generate_dcs_weather()
    new_mission_dict = copy.deepcopy(mission.d)
    new_mission_l10n = copy.deepcopy(mission.l10n)
    new_mission = elib_miz.Mission(new_mission_dict, new_mission_l10n)
    LOGGER.debug('DCS weather: %s', pprint.pformat(dcs_weather))
    LOGGER.debug('applying weather to mission file')
    wxd = new_mission.weather
    wxd.altimeter = dcs_weather.altimeter
    wxd.turbulence = dcs_weather.turbulence
    wxd.temperature = dcs_weather.temperature
    wxd.wind_ground_speed = dcs_weather.wind_ground_speed
    wxd.wind_ground_dir = dcs_weather.wind_ground_dir
    wxd.wind_at2000_speed = dcs_weather.wind_2000_speed
    wxd.wind_at2000_dir = dcs_weather.wind_2000_dir
    wxd.wind_at8000_speed = dcs_weather.wind_8000_speed
    wxd.wind_at8000_dir = dcs_weather.wind_8000_dir
    wxd.precipitation_code = dcs_weather.precipitation_code
    wxd.cloud_base = dcs_weather.cloud_base
    wxd.cloud_density = dcs_weather.cloud_density
    wxd.cloud_thickness = dcs_weather.cloud_thickness
    wxd.fog_enabled = dcs_weather.fog_enabled
    wxd.fog_thickness = dcs_weather.fog_thickness
    wxd.fog_visibility = dcs_weather.fog_visibility
    wxd.dust_enabled = dcs_weather.dust_enabled
    wxd.dust_density = dcs_weather.dust_density
    return new_mission
