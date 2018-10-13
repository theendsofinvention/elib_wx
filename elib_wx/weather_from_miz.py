# coding=utf-8
"""
Creates a Weather object from a MIZ file
"""

import datetime

import elib_miz

from elib_wx import Config, LOGGER, avwx, static
from elib_wx.values.value import Altitude, Length, Pressure, Temperature, WindDirection, WindSpeed
from elib_wx.weather_abc import WeatherABC
from elib_wx.weather_dcs import DCSWeather


def _make_clouds(weather_object, mission_weather, ):
    if mission_weather.cloud_density == 0:
        LOGGER.debug('no cloud found in mission')
        weather_object.cloud_layers = []
    else:
        LOGGER.debug('cloud density in mission: %s', mission_weather.cloud_density)
        cloud_type = static.CLOUD_DCS_TO_METAR[mission_weather.cloud_density]
        LOGGER.debug('inferred cloud type: %s', cloud_type)
        LOGGER.debug('cloud base in mission: %s', mission_weather.cloud_base)
        cloud_alt = int(round(Altitude(mission_weather.cloud_base, 'm').value('ft') / 100, 0))
        LOGGER.debug('inferred cloud altitude: %s', cloud_alt)
        weather_object.cloud_layers = [
            avwx.structs.Cloud(
                repr=f'{cloud_type}{cloud_alt:03d}',
                type=cloud_type,
                altitude=cloud_alt,
                modifier=None,
            )
        ]
        LOGGER.debug('resulting cloud layer: %s', weather_object.cloud_layers)


def _make_fog(weather_object, mission_weather):
    if not mission_weather.fog_enabled:
        LOGGER.debug('no fog in mission, setting visibility to 9999')
        weather_object.visibility = Length(9999, 'm')
    else:
        LOGGER.debug('fog visibility in mission: %s', mission_weather.fog_visibility)
        weather_object.visibility = Length(mission_weather.fog_visibility, 'm')


def _make_turbulence(weather_object, mission_weather):
    if mission_weather.turbulence > 0:
        LOGGER.debug('turbulence found in mission')
        wind_speed = mission_weather.wind_ground_speed
        weather_object.wind_gust = WindSpeed(wind_speed + wind_speed * (mission_weather.turbulence / 10), 'm/s')
        weather_object.wind_speed = WindSpeed(wind_speed, 'm/s')
    else:
        LOGGER.debug('no turbulence found in mission')
        weather_object.wind_speed = WindSpeed(mission_weather.wind_ground_speed, 'm/s')
        weather_object.wind_gust = WindSpeed(0)


def _make_date_time(weather_object, mission):
    LOGGER.debug('mission theatre is: %s', mission.theatre)
    if mission.theatre in (elib_miz.static.Theater.caucasus,
                           elib_miz.static.Theater.persian_gulf,
                           ):
        tz_info = datetime.timezone(offset=datetime.timedelta(hours=4))
    elif mission.theatre == elib_miz.static.Theater.nevada:
        tz_info = datetime.timezone(offset=-datetime.timedelta(hours=7))
    else:
        raise ValueError(f'Theatre not managed: {mission.theatre}')
    LOGGER.debug('using offset: %s', tz_info)
    date_time = datetime.datetime(
        year=mission.year,
        month=mission.month,
        day=mission.day,
        hour=mission.hour,
        minute=mission.minute,
        second=mission.second,
        tzinfo=tz_info
    )
    utc_time = date_time.astimezone(datetime.timezone.utc)
    weather_object.date_time = avwx.structs.Timestamp(
        repr=utc_time.strftime('%H%M%SZ'),
        dt=utc_time,
    )


def _make_dust(weather_object, mission_weather):
    if mission_weather.dust_enabled:
        LOGGER.debug('dust found in mission')
        if mission_weather.dust_density < 1000:
            weather_object.other.append('DS')
        else:
            weather_object.other.append('PO')


def _make_precipitations(weather_object, mission_weather):
    if mission_weather.precipitation_code == 1:
        LOGGER.debug('rain found in mission')
        weather_object.other.append('RA')
    if mission_weather.precipitation_code == 2:
        LOGGER.debug('thunderstorm found in mission')
        weather_object.other.append('+RATS')
    if mission_weather.precipitation_code == 3:
        LOGGER.debug('snow found in mission')
        weather_object.other.append('SN')
    if mission_weather.precipitation_code == 4:
        LOGGER.debug('blizzard found in mission')
        weather_object.other.append('+BLSN')


def _make_metar(weather_object):
    _metar_icao = weather_object.station_icao
    _metar_time = weather_object.date_time.repr
    _metar_wind = f'{weather_object.wind_direction.value():03}{weather_object.wind_speed.value("kt"):02}KTS'
    _metar_visibility = f'{weather_object.visibility.value():04d}M'
    _metar_other = ' '.join(weather_object.other)
    _metar_clouds = f'{weather_object.cloud_layers[0].repr}' if weather_object.cloud_layers else ''
    _minus = 'M' if weather_object.temperature.value() < 0 else ''
    _metar_temperature = f'{_minus}{weather_object.temperature.value():02}/' \
                         f'{_minus}{weather_object.dew_point.value():02}'
    _metar_pressure = f'Q{weather_object.altimeter.value(unit="hpa"):04d}'
    _metar_remarks = weather_object.remarks

    _result = (
        _metar_icao, _metar_time, _metar_wind, _metar_visibility, _metar_other, _metar_clouds,
        _metar_temperature, _metar_pressure, _metar_remarks
    )
    # Strip empty strings from result
    _result = [x for x in _result if x != '']

    weather_object.raw_metar_str = ' '.join(_result)
    weather_object.metar_units = avwx.structs.Units(altimeter='m',
                                                    altitude='ft',
                                                    temperature='c',
                                                    visibility='m',
                                                    wind_speed='kt')


def weather_from_miz_file(weather_object: WeatherABC):
    """
    Creates a Weather object from a MIZ file

    :param weather_object: weather object to fill
    :type weather_object: WeatherABC
    """
    LOGGER.debug('building Weather from MIZ file')
    LOGGER.debug('source MIZ file: %s', weather_object.source)
    weather_object.station_icao = Config.dummy_icao_code
    weather_object.source_type = 'MIZ file'
    with elib_miz.Miz(weather_object.source) as miz:
        mission_weather = miz.mission.weather
        mission = miz.mission
    weather_object.altimeter = Pressure(mission_weather.altimeter, 'mmhg')
    LOGGER.debug('altimeter: %s', weather_object.altimeter)

    _make_clouds(weather_object, mission_weather)
    _make_fog(weather_object, mission_weather)

    LOGGER.debug('inferred visibility: %s', weather_object.visibility)
    weather_object.temperature = Temperature(mission_weather.temperature, 'c')
    LOGGER.debug('inferred temperature: %s', weather_object.temperature)
    weather_object.dew_point = weather_object.temperature.make_dummy_dew_point()
    LOGGER.debug('inferred dew point: %s', weather_object.dew_point)

    _make_turbulence(weather_object, mission_weather)

    LOGGER.debug('inferred wind speed: %s', weather_object.wind_speed)
    LOGGER.debug('inferred wind gust: %s', weather_object.wind_gust)

    weather_object.wind_direction = WindDirection(mission_weather.wind_ground_dir).reverse()
    weather_object.wind_direction_is_variable = False
    weather_object.wind_direction_range = []

    _make_date_time(weather_object, mission)

    weather_object.other = []

    _make_dust(weather_object, mission_weather)

    _make_precipitations(weather_object, mission_weather)

    if weather_object.temperature.value() < 0:
        LOGGER.debug('freezing conditions found in mission')
        weather_object.other.append('FZ')
    LOGGER.debug('inferred others: %s', weather_object.other)
    weather_object.remarks = 'NOSIG'

    _make_metar(weather_object)

    # Store the original DCS weather so there's no discrepancies if we create a new one from this Weather
    dcs_wx = DCSWeather(
        altimeter=mission_weather.altimeter,
        turbulence=mission_weather.turbulence,
        temperature=mission_weather.temperature,
        wind_ground_speed=mission_weather.wind_ground_speed,
        wind_ground_dir=mission_weather.wind_ground_dir,
        wind_2000_speed=mission_weather.wind_at2000_speed,
        wind_2000_dir=mission_weather.wind_at2000_dir,
        wind_8000_speed=mission_weather.wind_at8000_speed,
        wind_8000_dir=mission_weather.wind_at8000_dir,
        precipitation_code=mission_weather.precipitation_code,
        cloud_density=mission_weather.cloud_density,
        cloud_base=mission_weather.cloud_base,
        cloud_thickness=mission_weather.cloud_thickness,
        fog_enabled=mission_weather.fog_enabled,
        fog_visibility=mission_weather.fog_visibility,
        fog_thickness=mission_weather.fog_thickness,
        dust_enabled=mission_weather.dust_enabled,
        dust_density=mission_weather.dust_density
    )
    weather_object.original_dcs_weather = dcs_wx
