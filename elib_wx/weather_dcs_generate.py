# coding=utf-8
"""
Generates a DCSWeather object that can be applied to a MIZ file from a an ABCWeather object
"""

import random
import typing

# pylint: disable=possibly-unused-variable
import dataclasses

from elib_wx import LOGGER
from elib_wx.static import CLOUD_METAR_TO_DCS
from elib_wx.values.value import (
    CloudBase, WindSpeed,
)
from elib_wx.weather_abc import WeatherABC
from elib_wx.weather_dcs import DCSWeather


def _make_ground_wind(weather_object) -> typing.Tuple[int, int, int]:
    if weather_object.wind_gust.value() > 0:
        if weather_object.wind_speed.value() == 0:
            weather_object.wind_speed = WindSpeed(1)
        wind_ground_speed = DCSWeather.normalize_wind_speed(
            round(weather_object.wind_speed.value('m/s')),
            'wind speed at ground level',
        )
        turbulence = DCSWeather.normalize_turbulence(
            round(float(weather_object.wind_gust.value() / wind_ground_speed))) * 10
    else:
        turbulence = 0
        wind_ground_speed = DCSWeather.normalize_wind_speed(
            weather_object.wind_speed.value('m/s'),
            'wind speed at ground level',
        )
    wind_ground_dir = weather_object.wind_direction.reverse().value()
    return wind_ground_speed, wind_ground_dir, turbulence


def _make_wind_in_altitude(weather_object) -> typing.Tuple[int, int, int, int]:
    wind_2000_speed = DCSWeather.normalize_wind_speed(
        weather_object.wind_speed.randomize_at_2000m().value(),
        'wind speed at 2000 meters'
    )
    wind_2000_dir = weather_object.wind_direction.randomize_at_2000m().reverse().value()
    wind_8000_speed = DCSWeather.normalize_wind_speed(
        weather_object.wind_speed.randomize_at_8000m().value(),
        'wind speed at 8000 meters'
    )
    wind_8000_dir = weather_object.wind_direction.randomize_at_8000m().reverse().value()
    return wind_2000_speed, wind_2000_dir, wind_8000_speed, wind_8000_dir


def _make_fog(weather_object) -> typing.Tuple[bool, int, int]:
    if weather_object.visibility.value() >= 9999:
        fog_enabled = False
        fog_thickness = 1000
        fog_visibility = 6000
    else:
        fog_enabled = True
        fog_thickness = 1000
        fog_visibility = DCSWeather.normalize_fog_visibility(round(weather_object.visibility.value()))
    return fog_enabled, fog_thickness, fog_visibility


def _make_dust(weather_object) -> typing.Tuple[bool, int]:
    dust_enabled = False
    dust_density = 3000
    for _dust_indicator in {'DU', 'DS', 'PO', 'SS'}:
        if any(_dust_indicator in other for other in weather_object.metar_data.other):
            if weather_object.visibility.value() > 5000:
                LOGGER.debug('there is dust in the area but visibility is over 5000m, not adding dust')
                break
            else:
                LOGGER.warning('there is dust in the area, visibility will be severely restricted')
                dust_enabled = True
                dust_density = DCSWeather.normalize_dust_density(weather_object.visibility.value())
                break
    return dust_enabled, dust_density


def _make_clouds(weather_object) -> typing.Tuple[int, int, int]:
    cloud_density = 0
    cloud_base = 300
    cloud_thickness = 200
    _layer_in_use = None
    for _layer in weather_object.cloud_layers:
        _coverage = random.randint(*CLOUD_METAR_TO_DCS[_layer.type])  # nosec
        if _coverage > cloud_density:
            cloud_density = _coverage
            _layer_in_use = _layer
    if _layer_in_use:
        LOGGER.debug('using cloud layer: %s', _layer_in_use.repr)
        if not _layer_in_use.altitude:
            LOGGER.warning(
                'no cloud altitude data found in METAR, using random number between 5 and 35 thousand feet'
            )
            cloud_base = random.randint(5, 25) * 1000  # nosec
        else:
            if not weather_object.metar_units.altitude == 'ft':
                raise ValueError(weather_object.metar_units.altitude)
            cloud_base = CloudBase(_layer_in_use.altitude * 100, 'ft').value('m')
        cloud_thickness = int(cloud_density / 10 * 2000)
    else:
        LOGGER.debug('no clouds')

    cloud_base = DCSWeather.normalize_cloud_base(cloud_base)
    cloud_thickness = DCSWeather.normalize_cloud_thickness(cloud_thickness)

    return cloud_base, cloud_density, cloud_thickness


@dataclasses.dataclass
class WeatherPhenomenon:
    """
    Represents a weather phenomenon (rain, snow, storm, ...)
    """
    name: str
    precipitation_code: int
    min_cloud_density: int
    indicators: typing.Set[str]
    min_temp: typing.Optional[int] = None
    max_temp: typing.Optional[int] = None


WEATHER_PHENOMENONS = [
    WeatherPhenomenon('rain',
                      indicators={'DZ', 'SH', 'RA', 'UP'},
                      precipitation_code=1,
                      min_cloud_density=5,
                      min_temp=0,
                      ),
    WeatherPhenomenon('snow',
                      indicators={'SN'},
                      precipitation_code=3,
                      min_cloud_density=5,
                      max_temp=-1,
                      ),
    WeatherPhenomenon('thunderstorm',
                      indicators={'TS'},
                      precipitation_code=2,
                      min_cloud_density=9,
                      min_temp=0,
                      ),
    WeatherPhenomenon('snow storm',
                      indicators={'GR', 'SG', 'PL', 'GS'},
                      precipitation_code=4,
                      min_cloud_density=9,
                      max_temp=-1,
                      ),
]


def _make_precipitations(weather_object, temperature, cloud_density) -> typing.Tuple[int, int, int]:
    precipitation_code = 0
    for phenomenon in WEATHER_PHENOMENONS:
        for indicator in phenomenon.indicators:
            if any(indicator in other for other in weather_object.metar_data.other):
                precipitation_code = phenomenon.precipitation_code
                LOGGER.warning('%s reported in the area', phenomenon.name)
                if phenomenon.min_temp is not None and temperature < phenomenon.min_temp:
                    LOGGER.warning('forcing temperature to %s due to %s', phenomenon.min_temp, phenomenon.name)
                    temperature = phenomenon.min_temp
                if phenomenon.max_temp is not None and temperature > phenomenon.max_temp:
                    LOGGER.warning('forcing temperature to %s due to %s', phenomenon.max_temp, phenomenon.name)
                    temperature = phenomenon.max_temp
                if cloud_density < phenomenon.min_cloud_density:
                    LOGGER.warning('forcing cloud density to %s due to %s',
                                   phenomenon.min_cloud_density, phenomenon.name)
                    cloud_density = phenomenon.min_cloud_density
                break

    return precipitation_code, temperature, cloud_density


def generate_dcs_weather(weather_object: WeatherABC) -> DCSWeather:  # pylint: disable=too-many-locals
    """
    Creates a DCSWeather from a Weather object.

    All DCS specific constraints regarding the different values are enforced

    :return: a valid DCSWeather object
    :rtype: DCSWeather
    """
    if weather_object.original_dcs_weather is not None:
        return weather_object.original_dcs_weather

    altimeter = DCSWeather.normalize_altimeter(weather_object.altimeter.value('mmhg'))
    temperature = DCSWeather.normalize_temperature(weather_object.temperature.value('c'))

    wind_ground_speed, wind_ground_dir, turbulence = _make_ground_wind(weather_object)
    wind_2000_speed, wind_2000_dir, wind_8000_speed, wind_8000_dir = _make_wind_in_altitude(weather_object)
    fog_enabled, fog_thickness, fog_visibility = _make_fog(weather_object)
    dust_enabled, dust_density = _make_dust(weather_object)
    cloud_base, cloud_density, cloud_thickness = _make_clouds(weather_object)
    precipitation_code, temperature, cloud_density = _make_precipitations(weather_object,
                                                                          temperature,
                                                                          cloud_density,
                                                                          )

    _local_data = dict(**locals())
    del _local_data['weather_object']
    _data = {key: _local_data[key] for key in _local_data.keys() if not key.startswith('_')}
    return DCSWeather(**_data)
