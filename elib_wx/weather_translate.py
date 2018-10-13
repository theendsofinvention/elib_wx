# coding=utf-8
"""
Provides methods to translate a Weather object into a readable/speakable string
"""
import typing

from elib_wx import LOGGER, avwx, static, utils
from elib_wx.values.value import Altitude
from elib_wx.weather_abc import WeatherABC


def wind(weather_object: WeatherABC, spoken: bool) -> str:
    """
    Translate wind component of an ABCWeather object into a readable/speakable string

    :param weather_object: source weather object
    :type weather_object: WeatherABC
    :param spoken: tailor outputs for TTS engines
    :type spoken: bool
    :return: translated result
    :rtype: str
    """
    if weather_object.wind_speed.value() == 0:
        return 'Wind calm.'
    if weather_object.wind_direction_is_variable:
        wind_dir = 'variable'
    else:
        wind_dir = weather_object.wind_direction.to_string(spoken=spoken)

    if weather_object.wind_direction_range and isinstance(weather_object.wind_direction_range, list):
        var1 = weather_object.wind_direction_range[0].to_string(spoken=spoken)
        var2 = weather_object.wind_direction_range[1].to_string(spoken=spoken)
        wind_dir += f' (variable {var1} to {var2})'

    wind_speed = weather_object.wind_speed.to_string(unit='kt', spoken=spoken)

    if weather_object.wind_gust.value() > 0:
        gust_speed = weather_object.wind_gust.to_string(unit='kt', spoken=spoken)
        wind_speed += f' (gusting {gust_speed} knots)'

    return f'Wind {wind_dir} {wind_speed}.'


def visibility(weather_object, spoken: bool) -> str:
    """
    Translate visibility component of an ABCWeather object into a readable/speakable string

    :param weather_object: source weather object
    :type weather_object: WeatherABC
    :param spoken: tailor outputs for TTS engines
    :type spoken: bool
    :return: translated result
    :rtype: str
    """
    if weather_object.is_cavok:
        if spoken:
            return 'cavok.'
        return 'CAVOK.'
    if weather_object.visibility.value() >= 9999:
        if spoken:
            return 'Visibility ten kilometers or more, ten miles or more.'

        return 'Visibility 10km or more, 10SM or more.'
    if spoken:
        m_val = weather_object.visibility.value('m')
        if m_val % 1000 == 0:
            value_as_str_meters = utils.num_to_words(int(weather_object.visibility.value('m') / 1000),
                                                     group=0) + ' kilometers'
        else:
            value_as_str_meters = utils.num_to_words(weather_object.visibility.value('m'), group=0) + ' meters'
        value_as_str_meters = value_as_str_meters.replace(',', '')
        value_as_str_miles = utils.num_to_words(weather_object.visibility.value('sm'), group=0) + ' miles'
        return f'Visibility {value_as_str_meters}, {value_as_str_miles}.'

    visibility_value = weather_object.visibility.to_string(spoken=spoken, all_units=True)
    return f'Visibility {visibility_value}.'


def temperature(weather_object, spoken: bool) -> str:
    """
    Translate temperature component of an ABCWeather object into a readable/speakable string

    :param weather_object: source weather object
    :type weather_object: WeatherABC
    :param spoken: tailor outputs for TTS engines
    :type spoken: bool
    :return: translated result
    :rtype: str
    """
    temperature_value = weather_object.temperature.to_string(spoken=spoken, all_units=True)
    return f'Temperature {temperature_value}.'


def dew_point(weather_object, spoken: bool) -> str:
    """
    Translate dew point component of an ABCWeather object into a readable/speakable string

    :param weather_object: source weather object
    :type weather_object: WeatherABC
    :param spoken: tailor outputs for TTS engines
    :type spoken: bool
    :return: translated result
    :rtype: str
    """
    dew_point_value = weather_object.dew_point.to_string(spoken=spoken, all_units=True)
    return f'Dew point {dew_point_value}.'


def altimeter(weather_object, spoken: bool) -> str:
    """
    Translate altimeter component of an ABCWeather object into a readable/speakable string

    :param weather_object: source weather object
    :type weather_object: WeatherABC
    :param spoken: tailor outputs for TTS engines
    :type spoken: bool
    :return: translated result
    :rtype: str
    """
    altimeter_value = weather_object.altimeter.to_string(spoken=spoken, all_units=True)
    return f'Altimeter {altimeter_value}.'


def other(weather_object) -> str:
    """
    Translate other component of an ABCWeather object into a readable/speakable string

    :param weather_object: source weather object
    :type weather_object: WeatherABC
    :return: translated result
    :rtype: str
    """
    _other = avwx.speech.other(weather_object.other)
    if _other:
        return _other + '.'
    return ''


def _parse_cloud_layer_as_str(self, cloud, ret: list, spoken: bool):
    if cloud.altitude is None:
        LOGGER.warning('no altitude given, skipping cloud layer: %s', cloud.repr)
        return
    cloud_str = static.CLOUD_TRANSLATIONS[cloud.type]
    if cloud.modifier:
        try:
            cloud_str += f' ({static.CLOUD_TRANSLATIONS[cloud.modifier]})'
        except KeyError:
            LOGGER.warning('unknown cloud modifier: %s', cloud.modifier)
    altitude_as_str = str(cloud.altitude)
    while len(altitude_as_str) != 3:
        altitude_as_str = '0' + altitude_as_str
    if spoken:
        cloud_alt = []

        _cloud_alt_in_thousand_feet_str = int(cloud.altitude / 10)

        if _cloud_alt_in_thousand_feet_str > 0:
            cloud_alt.append(utils.num_to_words(_cloud_alt_in_thousand_feet_str, group=0) + ' thousand')

        clouds_altitude_hundreds = altitude_as_str[2]
        if clouds_altitude_hundreds != '0':
            cloud_alt.append(utils.num_to_words(clouds_altitude_hundreds, group=0))
            cloud_alt.append('hundred')

        cloud_alt.append('feet')
        ret.append(cloud_str.format(' '.join(cloud_alt)))
    else:
        cloud_base = Altitude(cloud.altitude * 100, self.metar_units.altitude)
        ret.append(cloud_str.format(cloud_base.to_string(unit='ft', spoken=spoken)))


def clouds(weather_object, spoken: bool) -> str:
    """
    Translate clouds component of an ABCWeather object into a readable/speakable string

    :param weather_object: source weather object
    :type weather_object: WeatherABC
    :param spoken: tailor outputs for TTS engines
    :type spoken: bool
    :return: translated result
    :rtype: str
    """
    if weather_object.is_cavok:
        return ''
    if ' NSC ' in weather_object.raw_metar_str:
        return 'No significant cloud.'
    _clear = bool(' CLR ' in weather_object.raw_metar_str) or bool(' SKC ' in weather_object.raw_metar_str)
    if _clear or not weather_object.cloud_layers:
        return 'Sky clear.'
    ret: typing.List[str] = []
    for cloud in weather_object.cloud_layers:
        _parse_cloud_layer_as_str(weather_object, cloud, ret, spoken)
    if ret:
        return ', '.join(ret) + '.'
    return 'Sky clear.'


def _parse_rmk(rmk: str, ret: dict, spoken: bool) -> None:
    rlen = len(rmk)
    # Static single-word elements
    if rmk in avwx.static.REMARKS_ELEMENTS:
        ret[rmk] = avwx.static.REMARKS_ELEMENTS[rmk]
    # Digit-only encoded elements
    elif rmk.isdigit():
        if rlen == 5 and rmk[0] in utils.LEN5_DECODE:
            _ret = utils.LEN5_DECODE[rmk[0]](rmk, spoken=spoken)  # type: ignore
            rmk_: str = _ret
            ret[rmk] = rmk_
        # 24-hour min/max temperature
        elif rlen == 9:
            val1, val2 = utils.translate_temperature_str(rmk[1:5]), utils.translate_temperature_str(rmk[5:])
            ret[rmk] = f'24-hour temperature: max {val1} min {val2}'
    # Sea level pressure: SLP218
    elif rmk.startswith('SLP'):
        if spoken:
            val_1, val_2 = utils.num_to_words(int('10' + rmk[3:5])), utils.num_to_words(int('10' + rmk[5]))
            ret[rmk] = f'Sea level pressure: {val_1} point {val_2} hecto pascal'
        else:
            ret[rmk] = f'Sea level pressure: 10{rmk[3:5]}.{rmk[5]} hPa'
    # Temp/Dew with decimal: T02220183
    # elif rlen == 9 and rmk[0] == 'T' and rmk[1:].isdigit():
    #     continue
    # ret[rmk] = f'Temperature {_remarks._tdec(rmk[1:5])} and dewpoint {_remarks._tdec(rmk[5:])}'
    # Precipitation amount: P0123
    elif rlen == 5 and rmk[0] == 'P' and rmk[1:].isdigit():
        if spoken:
            val_1 = utils.num_to_words(int(rmk[1:3]))
            val_2 = utils.num_to_words(rmk[3:])
            ret[rmk] = f'Hourly precipitation: {val_1} point {val_2} inches'.replace(',', '')
        else:
            ret[rmk] = f'Hourly precipitation: {int(rmk[1:3])}.{rmk[3:]} in'
    # Weather began/ended
    elif rlen == 5 and rmk[2] in ('B', 'E') and rmk[3:].isdigit() and rmk[:2] in avwx.static.WX_TRANSLATIONS:
        state = 'began' if rmk[2] == 'B' else 'ended'
        ret[rmk] = f'{avwx.static.WX_TRANSLATIONS[rmk[:2]]} {state} at :{rmk[3:]}'


def remarks(weather_object, spoken: bool) -> str:
    """
    Translate remarks component of an ABCWeather object into a readable/speakable string

    :param weather_object: source weather object
    :type weather_object: WeatherABC
    :param spoken: tailor outputs for TTS engines
    :type spoken: bool
    :return: translated result
    :rtype: str
    """
    ret = {}
    _remarks = str(weather_object.remarks)
    # Add and replace static multi-word elements
    for key in avwx.static.REMARKS_GROUPS:
        if key in _remarks:
            ret[key.strip()] = avwx.static.REMARKS_GROUPS[key]
            _remarks.replace(key, ' ')
    # For each remaining element
    for rmk in _remarks.split()[1:]:
        _parse_rmk(rmk, ret, spoken)
    result = [value for value in ret.values()]
    if 'NOSIG' in weather_object.raw_metar_str:
        result.append('No significant change')
    if result:
        return '. '.join(result) + '.'

    return ''


def intro(weather_object, spoken: bool) -> str:
    """
    Translate intro component of an ABCWeather object into a readable/speakable string

    :param weather_object: source weather object
    :type weather_object: WeatherABC
    :param spoken: tailor outputs for TTS engines
    :type spoken: bool
    :return: translated result
    :rtype: str
    """
    if weather_object.date_time.dt:
        day_name = weather_object.date_time.dt.strftime('%A')
        day_date = utils.num_to_ordinal(weather_object.date_time.dt.strftime('%d'))
        if spoken:
            day_date = utils.num_to_words(day_date, group=0)
        month = weather_object.date_time.dt.strftime('%B')
        time = weather_object.date_time.dt.strftime('%H%M')
        if spoken:
            time = utils.num_to_words(weather_object.date_time.dt.strftime('%H%M'))
        return f'Weather for {weather_object.station_name} on {day_name} the {day_date} of {month} at {time} zulu.'

    return f'Weather for {weather_object.station_name}.'
