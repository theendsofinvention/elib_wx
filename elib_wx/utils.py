# coding=utf-8
"""
This module contains various utility functions
"""
import typing

import inflect

from elib_wx.avwx.core import valid_station
from elib_wx.static import PRESSURE_TENDENCIES, UNIT_TRANSLATION


def extract_station_from_metar_str(metar_str: str) -> str:
    """
    Returns the first block of a space-delimited string, which in the case of a METAR should be the station ICAO

    :param metar_str: METAR
    :type metar_str: str
    :return: valid station
    :rtype: str
    """
    _station = metar_str.split(' ')[0]
    return valid_station(_station)


_CONVERT = inflect.engine()


def num_to_words(num: typing.Union[str, float], group: int = 1) -> str:
    """
    Translates numbers to words

    :param num: number to translate
    :type num: float, int, str
    :param group: 1, 2 or 3 to group numbers before turning into words
    :type group: int
    :return: number as str
    :rtype: str
    """
    return _CONVERT.number_to_words(num, group=group).replace(',', '')


def num_to_ordinal(num: typing.Union[str, float]) -> str:
    """
    Return the ordinal of num.

    num can be an integer or text

    :param num: num to translate to ordinal
    :type num: str, int float
    :return: translated ordinal
    :rtype: str
    """
    return _CONVERT.ordinal(num)


def _translate_unit(unit: str) -> str:
    return UNIT_TRANSLATION[unit.lower()]


def translate_temperature_str(code: str,
                              unit: typing.Optional[str] = 'C',
                              spoken: bool = False
                              ) -> typing.Optional[str]:
    """
    Translates a 4-digit decimal temperature representation

    Ex: 1045 -> -4.5°C    0237 -> 23.7°C
    """
    if not code:
        return None
    if spoken:
        val_1, val_2 = num_to_words(int(code[1:3])), num_to_words(int(code[3]))
        ret = f"{'-' if code[0] == '1' else ''}{val_1} point {val_2}"
    else:
        ret = f"{'-' if code[0] == '1' else ''}{int(code[1:3])}.{code[3]}"
    if unit:
        if spoken:
            ret += ' degrees ' + _translate_unit(unit)
        else:
            ret += f'°{unit}'
    return ret


def temp_minmax(code: str, spoken: bool = False) -> str:
    """
    Translates a 5-digit min/max temperature code
    """
    label = 'maximum' if code[0] == '1' else 'minimum'
    prefix = 'six hours' if spoken else '6-hour'
    return f'{prefix} {label} temperature {translate_temperature_str(code[1:], spoken=spoken)}'


def pressure_tendency(code: str, unit: str = 'mb', spoken: bool = False) -> str:
    """
    Translates a 5-digit pressure outlook code

    Ex: 50123 -> 12.3 mb: Increasing, then decreasing
    """
    if spoken:
        width, precision = num_to_words(int(code[2:4])), num_to_words(int(code[4]))
        unit = _translate_unit(unit)
        return (f'Three hours pressure difference: plus or minus '
                f'{width} point {precision} {unit} - {PRESSURE_TENDENCIES[code[1]]}')

    width, precision = code[2:4], code[4]
    return (f'3-hour pressure difference: +/- '
            f'{width}.{precision} {unit} - {PRESSURE_TENDENCIES[code[1]]}')


def precip_36(code: str, unit: str = 'in', spoken: bool = False) -> str:
    """
    Translates a 5-digit 3 and 6-hour precipitation code
    """
    if spoken:
        _val1 = num_to_words(int(code[1:3]))
        _val2 = num_to_words(int(code[3:]))
        unit = _translate_unit(unit)
        return ('Precipitation in the last three hours: '
                f'{_val1} {unit}. - six hours: {_val2} {unit}')

    return ('Precipitation in the last 3 hours: '
            f'{int(code[1:3])} {unit}. - 6 hours: {int(code[3:])} {unit}')


def precip_24(code: str, unit: str = 'in', spoken: bool = False) -> str:
    """
    Translates a 5-digit 24-hour precipitation code
    """
    if spoken:
        _val1, unit = num_to_words(int(code[1:])), _translate_unit(unit)
        return f'Precipitation in the last twenty four hours: {_val1} {unit}.'

    return f'Precipitation in the last 24 hours: {int(code[1:])} {unit}.'


def sunshine_duration(code: str, unit: str = 'minutes', spoken: bool = False) -> str:
    """
    Translates a 5-digit sunlight duration code
    """
    if spoken:
        _val, unit = num_to_words(int(code[1:])), _translate_unit(unit)
        return f'Duration of sunlight: {_val} {unit}'

    return f'Duration of sunlight: {int(code[1:])} {unit}'


LEN5_DECODE = {
    '1': temp_minmax,
    '2': temp_minmax,
    '5': pressure_tendency,
    '6': precip_36,
    '7': precip_24,
    '9': sunshine_duration
}
