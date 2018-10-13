# coding=utf-8
"""
Michael duPont - michael@mdupont.com
Original source: https://github.com/flyinactor91/AVWX-Engine
Modified by etcher@daribouca.net
"""
# pylint: disable=too-many-lines

import logging
import typing
from copy import copy
from datetime import datetime, timedelta
from itertools import permutations

from dateutil.relativedelta import relativedelta

from .exceptions import BadStationError
from .static import (
    CARDINAL_DIRECTIONS, CLOUD_LIST, CLOUD_TRANSLATIONS, FLIGHT_RULES, FRACTIONS, IN_REGIONS, METAR_RMK, M_IN_REGIONS,
    M_NA_REGIONS, NA_REGIONS, NUMBER_REPL, SPECIAL_NUMBERS, TAF_NEWLINE, TAF_NEWLINE_STARTSWITH, TAF_RMK,
)
from .structs import Cloud, Fraction, Number, Timestamp, Units

LOGGER = logging.getLogger('elib.wx')


def valid_station(station: str) -> str:
    """
    Checks the validity of a station ID

    This function doesn't return anything. It merely raises a BadStation error if needed
    """
    LOGGER.debug('checking if station is valid: %s', station)
    station = station.strip()
    if len(station) != 4:
        raise BadStationError(station, 'ICAO station idents must be four characters long')
    uses_na_format(station)
    LOGGER.debug('station is valid: %s', station)
    return station


def uses_na_format(station: str) -> bool:
    """
    Returns True if the station uses the North American format,
    False if the International format
    """
    LOGGER.debug('checking if station uses NA format: %s', station)
    if station[0] in NA_REGIONS:
        LOGGER.debug('station does use NA format: %s', station)
        return True
    if station[0] in IN_REGIONS:
        LOGGER.debug('station does not use NA format: %s', station)
        return False
    if station[:2] in M_NA_REGIONS:
        LOGGER.debug('station does use NA format: %s', station)
        return True
    if station[:2] in M_IN_REGIONS:
        LOGGER.debug('station does not use NA format: %s', station)
        return False
    raise BadStationError(station, "station ICAO doesn't start with a recognized character set")


def is_unknown(val: str) -> bool:
    """
    Returns True if val contains only '/' characters
    """
    LOGGER.debug('checking if value is defined: %s', val)
    if val is None:
        raise TypeError('val should not be None')
    clean_val = str(val).replace('.', '')
    for char in ('/', 'X'):
        if clean_val == char * len(clean_val):
            LOGGER.debug('value is not defined: %s', val)
            return True
    LOGGER.debug('value is defined: %s', val)
    return False


def unpack_fraction(num: str) -> str:
    """
    Returns unpacked fraction string 5/2 -> 2 1/2
    """
    nums = [int(n) for n in num.split('/') if n]
    if len(nums) == 2 and nums[0] > nums[1]:
        LOGGER.debug('unpacking fraction: %s', num)
        over = nums[0] // nums[1]
        rem = nums[0] % nums[1]
        num = f'{over} {rem}/{nums[1]}'
    else:
        LOGGER.debug('not a fraction: %s', num)
    LOGGER.debug('returning: %s', num)
    return num


def remove_leading_zeros(num: str) -> str:
    """
    Strips zeros while handling -, M, and empty strings
    """
    LOGGER.debug('stripping leading zeroes from: %s', num)
    if not num:
        LOGGER.debug('nothing to do, returning: %s', num)
        return num
    if num.startswith('M'):
        LOGGER.debug('stripping leading "M"')
        ret = 'M' + num[1:].lstrip('0')
    elif num.startswith('-'):
        LOGGER.debug('stripping leading "-"')
        ret = '-' + num[1:].lstrip('0')
    else:
        LOGGER.debug('stripping leading "0"')
        ret = num.lstrip('0')
    if ret in ('', 'M', '-'):
        LOGGER.debug('return value is only qualifier, returning "0"')
        return '0'

    LOGGER.debug('returning: %s', ret)
    return ret


def spoken_number(num: str) -> str:
    """
    Returns the spoken version of a number

    Ex: 1.2 -> one point two
        1 1/2 -> one and one half
    """
    ret = []
    LOGGER.debug('converting number to spoken text: %s', num)
    for part in num.split(' '):
        if part in FRACTIONS:
            ret.append(FRACTIONS[part])
        else:
            ret.append(' '.join([NUMBER_REPL[char] for char in part if char in NUMBER_REPL]))
    result = ' and '.join(ret)
    LOGGER.debug('returning: %s', result)
    return result


def _make_number(num: typing.Optional[str] = None,
                 repr_: typing.Optional[str] = None,
                 speak: typing.Optional[str] = None) -> typing.Optional[Number]:
    if num is None and repr_ is None:
        return None
    # Check special
    if num is not None and num in SPECIAL_NUMBERS:
        return Number(repr_ or num, None, SPECIAL_NUMBERS[num])
    # Create Fraction
    if num is not None and '/' in num:
        nmr, dnm = [int(i) for i in num.split('/')]
        unpacked = unpack_fraction(num)
        spoken = spoken_number(unpacked)
        # noinspection PyArgumentList
        return Fraction(repr_ or num, nmr / dnm, spoken, nmr, dnm, unpacked)
    if num is not None:
        # Create Number
        val_str = num.replace('M', '-')
        val = float(val_str) if '.' in num else int(val_str)
        return Number(repr_ or num, val, spoken_number(speak or str(val)))

    return None


def make_number(num: typing.Optional[str] = None,
                repr_: typing.Optional[str] = None,
                speak: typing.Optional[str] = None) -> typing.Optional[Number]:
    """
    Returns a Number or Fraction dataclass for a number string
    """
    if not num or is_unknown(num):
        return None
    if num == 'NIL':
        return None
    if '-' * len(num) == num:
        return None
    if 'M' * len(num) == num:
        return None
    # Check CAVOK
    if num == 'CAVOK':
        return Number('CAVOK', 9999, 'ceiling and visibility ok')
    return _make_number(num, repr_, speak)


def find_first_in_list(txt: str, str_list: typing.List[str]) -> int:
    """
    Returns the index of the earliest occurrence of an item from a list in a string

    Ex: find_first_in_list('foobar', ['bar', 'fin']) -> 3
    """
    start = len(txt) + 1
    for item in str_list:
        if start > txt.find(item) > -1:
            start = txt.find(item)
    return start if len(txt) + 1 > start > -1 else -1


def get_remarks(txt: str) -> typing.Tuple[typing.List[str], str]:
    """
    Returns the report split into components and the remarks string

    Remarks can include items like RMK and on, NOSIG and on, and BECMG and on
    """
    txt = txt.replace('?', '').strip()
    # First look for Altimeter in txt
    alt_index = len(txt) + 1
    for item in [' A2', ' A3', ' Q1', ' Q0', ' Q9']:
        index = txt.find(item)
        if len(txt) - 6 > index > -1 and txt[index + 2:index + 6].isdigit():
            alt_index = index
    # Then look for earliest remarks 'signifier'
    sig_index = find_first_in_list(txt, METAR_RMK)
    if sig_index == -1:
        sig_index = len(txt) + 1
    if sig_index > alt_index > -1:
        return txt[:alt_index + 6].strip().split(' '), txt[alt_index + 7:]
    if alt_index > sig_index > -1:
        return txt[:sig_index].strip().split(' '), txt[sig_index + 1:]
    return txt.strip().split(' '), ''


def get_taf_remarks(txt: str) -> typing.Tuple[str, str]:
    """
    Returns report and remarks separated if found
    """
    remarks_start = find_first_in_list(txt, TAF_RMK)
    if remarks_start == -1:
        return txt, ''
    remarks = txt[remarks_start:]
    txt = txt[:remarks_start].strip()
    return txt, remarks


STR_REPL = {' C A V O K ': ' CAVOK ', '?': ' '}


def sanitize_report_string(txt: str) -> str:
    """
    Provides sanitation for operations that work better when the report is a string

    Returns the first pass sanitized report string
    """
    if len(txt) < 4:
        return txt
    # Standardize whitespace
    txt = ' '.join(txt.split())
    # Prevent changes to station ID
    stid, txt = txt[:4], txt[4:]
    # Replace invalid key-value pairs
    for key, rep in STR_REPL.items():
        txt = txt.replace(key, rep)
    # Check for missing spaces in front of cloud layers
    # Ex: TSFEW004SCT012FEW///CBBKN080
    for cloud in CLOUD_LIST:
        if cloud in txt and ' ' + cloud not in txt:
            start, counter = 0, 0
            while txt.count(cloud) != txt.count(' ' + cloud):
                cloud_index = start + txt[start:].find(cloud)
                if len(txt[cloud_index:]) >= 3:
                    target = txt[cloud_index + len(cloud):cloud_index + len(cloud) + 3]
                    if target.isdigit() or not target.strip('/'):
                        txt = txt[:cloud_index] + ' ' + txt[cloud_index:]
                start = cloud_index + len(cloud) + 1
                # Prevent infinite loops
                if counter > txt.count(cloud):
                    break
                counter += 1
    return stid + txt


# noinspection SpellCheckingInspection
LINE_FIXES = {
    'TEMP0': 'TEMPO', 'TEMP O': 'TEMPO', 'TMPO': 'TEMPO', 'TE MPO': 'TEMPO',
    'TEMP ': 'TEMPO ', 'T EMPO': 'TEMPO', ' EMPO': ' TEMPO', 'TEMO': 'TEMPO',
    'BECM G': 'BECMG', 'BEMCG': 'BECMG', 'BE CMG': 'BECMG', 'B ECMG': 'BECMG',
    ' BEC ': ' BECMG ', 'BCEMG': 'BECMG', 'BEMG': 'BECMG',
}


def sanitize_line(txt: str) -> str:
    """
    Fixes common mistakes with 'new line' signifier so that they can be recognized
    """
    for key in LINE_FIXES:
        index = txt.find(key)
        if index > -1:
            txt = txt[:index] + LINE_FIXES[key] + txt[index + len(key):]
    # Fix when space is missing following new line signifier
    for item in ['BECMG', 'TEMPO']:
        if item in txt and item + ' ' not in txt:
            index = txt.find(item) + len(item)
            txt = txt[:index] + ' ' + txt[index:]
    return txt


def _extra_space_exists(str1: str, str2: str, ls1: int, ls2: int) -> bool:
    if str1.isdigit():
        # 10 SM
        _cond1 = str2 in ['SM', '0SM']
        # 12 /10
        _cond2 = ls2 > 2 and str2[0] == '/' and str2[1:].isdigit()
        if any((_cond1, _cond2)):
            return True
    if str2.isdigit():
        # OVC 040
        _cond1 = str1 in CLOUD_LIST
        # 12/ 10
        _cond2 = ls1 > 2 and str1.endswith('/') and str1[:-1].isdigit()
        # 12/1 0
        _cond3 = ls2 == 1 and ls1 > 3 and str1[:2].isdigit() and '/' in str1 and str1[3:].isdigit()
        # Q 1001
        _cond4 = str1 in ['Q', 'A']
        if any((_cond1, _cond2, _cond3, _cond4)):
            return True
    return False


def extra_space_exists(str1: str, str2: str) -> bool:
    """
    Return True if a space shouldn't exist between two items
    """
    ls1, ls2 = len(str1), len(str2)
    if _extra_space_exists(str1, str2, ls1, ls2):
        return True
    # 36010G20 KT
    _vrb: bool = str1.startswith('VRB')
    _d35 = str1[3:5].isdigit()
    _d05 = str1[:5].isdigit()
    _cond1 = (_d05 or (_vrb and _d35))

    conds = (
        str2 == 'KT' and str1[-1].isdigit() and _cond1,
        # 36010K T
        str2 == 'T' and ls1 >= 6 and _cond1 and str1[-1] == 'K',
        # OVC022 CB
        str2 in CLOUD_TRANSLATIONS and str2 not in CLOUD_LIST and ls1 >= 3 and str1[:3] in CLOUD_LIST,
        # FM 122400
        str1 in ['FM', 'TL'] and (str2.isdigit() or (str2.endswith('Z') and str2[:-1].isdigit())),
        # TX 20/10
        str1 in ['TX', 'TN'] and str2.find('/') != -1
    )
    if any(conds):
        return True

    return False


# noinspection SpellCheckingInspection
ITEM_REMV = ['AUTO', 'COR', 'NSC', 'NCD', '$', 'KT', 'M', '.', 'RTD', 'SPECI', 'METAR', 'CORR']
ITEM_REPL = {'CALM': '00000KT'}
VIS_PERMUTATIONS = [''.join(p) for p in permutations('P6SM')]
VIS_PERMUTATIONS.remove('6MPS')


def sanitize_report_list(wxdata: typing.List[str],  # noqa pylint: disable=too-many-branches,too-many-locals
                         remove_clr_and_skc: bool = True
                         ) -> typing.Tuple[typing.List[str], typing.List[str], str]:
    """
    Sanitize wxData

    We can remove and identify "one-off" elements and fix other issues before parsing a line

    We also return the runway visibility and wind shear since they are very easy to recognize
    and their location in the report is non-standard
    """
    shear = ''
    runway_vis = []
    for i, item in reversed(list(enumerate(wxdata))):
        ilen = len(item)
        _i5d = item[:5].isdigit()
        _i3d = item[1:3].isdigit()
        _ivrb = item.startswith('VRB')
        try:
            _i5kt = item[5] in ['K', 'T']
        except IndexError:
            _i5kt = False
        try:
            _i8kt = item[8] in ['K', 'T']
        except IndexError:
            _i8kt = False
        cond1 = (ilen == 6 and _i5kt and (_i5d or _ivrb))
        cond2 = (ilen == 9 and _i8kt and item[5] == 'G' and (_i5d or _ivrb))
        # Remove elements containing only '/'
        # noinspection SpellCheckingInspection
        if is_unknown(item):
            wxdata.pop(i)
        # Identify Runway Visibility
        elif ilen > 4 and item[0] == 'R' and (item[3] == '/' or item[4] == '/') and _i3d:
            runway_vis.append(wxdata.pop(i))
        # Remove RE from wx codes, REVCTS -> VCTS
        elif ilen in [4, 6] and item.startswith('RE'):
            wxdata[i] = item[2:]
        # Fix a slew of easily identifiable conditions where a space does not belong
        elif i and extra_space_exists(wxdata[i - 1], item):
            wxdata[i - 1] += wxdata.pop(i)
        # Remove spurious elements
        elif item in ITEM_REMV:
            wxdata.pop(i)
        # Remove 'Sky Clear' from METAR but not TAF
        elif remove_clr_and_skc and item in ['CLR', 'SKC']:
            wxdata.pop(i)
        # Replace certain items
        elif item in ITEM_REPL:
            wxdata[i] = ITEM_REPL[item]
        # Remove amend signifier from start of report ('CCA', 'CCB',etc)
        elif ilen == 3 and item.startswith('CC') and item[2].isalpha():
            wxdata.pop(i)
        # Identify Wind Shear
        elif ilen > 6 and item.startswith('WS') and item[5] == '/':
            shear = wxdata.pop(i).replace('KT', '')
        # Fix inconsistent 'P6SM' Ex: TP6SM or 6PSM -> P6SM
        elif ilen > 3 and item[-4:] in VIS_PERMUTATIONS:
            wxdata[i] = 'P6SM'
        # Fix wind T
        elif cond1 or cond2:
            wxdata[i] = item[:-1] + 'KT'
        # Fix joined TX-TN
        elif ilen > 16 and len(item.split('/')) == 3:
            if item.startswith('TX') and 'TN' not in item:
                tn_index = item.find('TN')
                wxdata.insert(i + 1, item[:tn_index])
                wxdata[i] = item[tn_index:]
            elif item.startswith('TN') and item.find('TX') != -1:
                tx_index = item.find('TX')
                wxdata.insert(i + 1, item[:tx_index])
                wxdata[i] = item[tx_index:]
    return wxdata, runway_vis, shear


# pylint: disable=too-many-branches
def get_altimeter(wxdata: typing.List[str], units: Units, version: str = 'NA'  # noqa
                  ) -> typing.Tuple[typing.List[str], typing.Optional[Number]]:
    """
    Returns the report list and the removed altimeter item

    Version is 'NA' (North American / default) or 'IN' (International)
    """
    if not wxdata:
        return wxdata, None
    altimeter = ''
    target: str = wxdata[-1]
    if version == 'NA':
        # Version target
        if target[0] == 'A':
            altimeter = wxdata.pop()[1:]
        # Other version but prefer normal if available
        elif target[0] == 'Q':
            if wxdata[-2][0] == 'A':
                wxdata.pop()
                altimeter = wxdata.pop()[1:]
            else:
                units.altimeter = 'hPa'
                altimeter = wxdata.pop()[1:].lstrip('.')
        # Else grab the digits
        elif len(target) == 4 and target.isdigit():
            altimeter = wxdata.pop()
    elif version == 'IN':
        # Version target
        if target[0] == 'Q':
            altimeter = wxdata.pop()[1:].lstrip('.')
            if '/' in altimeter:
                altimeter = altimeter[:altimeter.find('/')]
        # Other version but prefer normal if available
        elif target[0] == 'A':
            if len(wxdata) >= 2 and wxdata[-2][0] == 'Q':
                wxdata.pop()
                altimeter = wxdata.pop()[1:]
            else:
                units.altimeter = 'inHg'
                altimeter = wxdata.pop()[1:]
    # Some stations report both, but we only need one
    if wxdata and (wxdata[-1][0] == 'A' or wxdata[-1][0] == 'Q'):
        wxdata.pop()
    # convert to Number
    if not altimeter:
        return wxdata, None
    if units.altimeter == 'inHg' and '.' not in altimeter:
        value = altimeter[:2] + '.' + altimeter[2:]
    else:
        value = altimeter
    if altimeter == 'M' * len(altimeter):
        return wxdata, None
    while value and not value[0].isdigit():
        value = value[1:]
    if value.endswith('INS'):
        value = value[:-3]
    if altimeter.endswith('INS'):
        altimeter = altimeter[:-3]
    return wxdata, make_number(value, altimeter)


def get_taf_alt_ice_turb(wxdata: typing.List[str]
                         ) -> typing.Tuple[typing.List[str], str, typing.List[str], typing.List[str]]:
    """
    Returns the report list and removed: Altimeter string, Icing list, Turbulence list
    """
    altimeter = ''
    icing, turbulence = [], []
    for i, item in reversed(list(enumerate(wxdata))):
        if len(item) > 6 and item.startswith('QNH') and item[3:7].isdigit():
            altimeter = wxdata.pop(i)[3:7]
        elif item.isdigit():
            if item[0] == '6':
                icing.append(wxdata.pop(i))
            elif item[0] == '5':
                turbulence.append(wxdata.pop(i))
    return wxdata, altimeter, icing, turbulence


def is_possible_temp(temp: str) -> bool:
    """
    Returns True if all characters are digits or 'M' (for minus)
    """
    for char in temp:
        if not (char.isdigit() or char == 'M'):
            return False
    return True


def get_temp_and_dew(wxdata: typing.List[str]
                     ) -> typing.Tuple[typing.List[str], typing.Optional[Number], typing.Optional[Number]]:
    """
    Returns the report list and removed temperature and dewpoint strings
    """
    for i, item in reversed(list(enumerate(wxdata))):
        if '/' in item:
            # ///07
            if item[0] == '/':
                item = '/' + item.lstrip('/')
            # 07///
            elif item[-1] == '/':
                item = item.rstrip('/') + '/'
            tempdew = item.split('/')
            if len(tempdew) != 2:
                continue
            valid = True
            for j, temp in enumerate(tempdew):
                if temp in ['MM', 'XX']:
                    tempdew[j] = ''
                elif not is_possible_temp(temp):
                    valid = False
                    break
            if valid:
                wxdata.pop(i)
                return wxdata, make_number(tempdew[0]), make_number(tempdew[1])
    return wxdata, None, None


def get_station_and_time(wxdata: typing.List[str]) -> typing.Tuple[typing.List[str], str, str]:
    """
    Returns the report list and removed station ident and time strings
    """
    station = wxdata.pop(0)
    qtime = wxdata[0]
    if wxdata and qtime.endswith('Z') and qtime[:-1].isdigit():
        rtime = wxdata.pop(0)
    elif wxdata and len(qtime) == 6 and qtime.isdigit():
        rtime = wxdata.pop(0) + 'Z'
    else:
        rtime = ''
    return wxdata, station, rtime


# pylint: disable=too-many-boolean-expressions
def get_wind(wxdata: typing.List[str], units: Units  # noqa pylint: disable=too-many-locals
             ) -> typing.Tuple[typing.List[str],
                               typing.Optional[Number],
                               typing.Optional[Number],
                               typing.Optional[Number],
                               typing.List[typing.Optional[Number]]]:
    """
    Returns the report list and removed:
    Direction string, speed string, gust string, variable direction list
    """
    direction, speed, gust = '', '', ''
    variable: typing.List[typing.Optional[Number]] = []
    if wxdata:
        item = copy(wxdata[0])
        for rep in ['(E)']:
            item = item.replace(rep, '')
        item = item.replace('O', '0')
        # 09010KT, 09010G15KT
        _cond1 = any((item.endswith('KT'), item.endswith('KTS'), item.endswith('MPS'), item.endswith('KMH')))
        _cond2 = bool(len(item) == 5 or (len(item) >= 8 and item.find('G') != -1) and item.find('/') == -1)
        _cond3 = (_cond2 and (item[:5].isdigit() or (item.startswith('VRB') and item[3:5].isdigit())))
        if _cond1 or _cond3:
            # In order of frequency
            if item.endswith('KT'):
                item = item.replace('KT', '')
            elif item.endswith('KTS'):
                item = item.replace('KTS', '')
            elif item.endswith('MPS'):
                units.wind_speed = 'm/s'
                item = item.replace('MPS', '')
            elif item.endswith('KMH'):
                units.wind_speed = 'km/h'
                item = item.replace('KMH', '')
            direction = item[:3]
            if 'G' in item:
                g_index = item.find('G')
                gust = item[g_index + 1:]
                speed = item[3:g_index]
            else:
                speed = item[3:]
            wxdata.pop(0)
    # Separated Gust
    if wxdata and 1 < len(wxdata[0]) < 4 and wxdata[0][0] == 'G' and wxdata[0][1:].isdigit():
        gust = wxdata.pop(0)[1:]
    # Variable Wind Direction
    try:
        _wxlen7 = len(wxdata[0]) == 7
    except IndexError:
        _wxlen7 = False
    try:
        _wxd03d = wxdata[0][:3].isdigit()
    except IndexError:
        _wxd03d = False
    if wxdata and _wxlen7 and _wxd03d and wxdata[0][3] == 'V' and wxdata[0][4:].isdigit():
        variable = [make_number(i, speak=i) for i in wxdata.pop(0).split('V')]
    # Convert to Number
    direction = CARDINAL_DIRECTIONS.get(direction, direction)
    _resulting_direction = make_number(direction, speak=direction)
    _resulting_speed = make_number(speed)
    _resulting_gust = make_number(gust)
    return wxdata, _resulting_direction, _resulting_speed, _resulting_gust, variable


def get_visibility(wxdata: typing.List[str], units: Units) -> typing.Tuple[typing.List[str], typing.Optional[Number]]:
    """
    Returns the report list and removed visibility string
    """
    visibility = ''
    if wxdata:
        item = copy(wxdata[0])
        # Vis reported in statue miles
        if item.endswith('SM'):  # 10SM
            if item in ('P6SM', 'M1/4SM'):
                visibility = item[:-2]
            elif '/' not in item:
                visibility = str(int(item[:item.find('SM')]))
            else:
                visibility = item[:item.find('SM')]  # 1/2SM
            wxdata.pop(0)
            units.visibility = 'sm'
        # Vis reported in meters
        elif len(item) == 4 and item.isdigit():
            visibility = wxdata.pop(0)
            units.visibility = 'm'
        elif 7 >= len(item) >= 5 and item[:4].isdigit() and (item[4] in ['M', 'N', 'S', 'E', 'W'] or item[4:] == 'NDV'):
            visibility = wxdata.pop(0)[:4]
            units.visibility = 'm'
        elif len(item) == 5 and item[1:].isdigit() and item[0] in ['M', 'P', 'B']:
            visibility = wxdata.pop(0)[1:]
            units.visibility = 'm'
        elif item.endswith('KM') and item[:item.find('KM')].isdigit():
            visibility = item[:item.find('KM')] + '000'
            wxdata.pop(0)
            units.visibility = 'm'
        # Vis statute miles but split Ex: 2 1/2SM
        elif len(wxdata) > 1 and wxdata[1].endswith('SM') and '/' in wxdata[1] and item.isdigit():
            vis1 = wxdata.pop(0)  # 2
            vis2 = wxdata.pop(0).replace('SM', '')  # 1/2
            visibility = str(int(vis1) * int(vis2[2]) + int(vis2[0])) + vis2[1:]  # 5/2
            units.visibility = 'sm'
    return wxdata, make_number(visibility)


def starts_new_line(item: str) -> bool:
    """
    Returns True if the given element should start a new report line
    """
    if item in TAF_NEWLINE:
        return True

    for start in TAF_NEWLINE_STARTSWITH:
        if item.startswith(start):
            return True

    return False


def split_taf(txt: str) -> typing.List[str]:
    """
    Splits a TAF report into each distinct time period
    """
    lines = []
    split = txt.split()
    last_index = 0
    for i, item in enumerate(split):
        if starts_new_line(item) and i != 0 and not split[i - 1].startswith('PROB'):
            lines.append(' '.join(split[last_index:i]))
            last_index = i
    lines.append(' '.join(split[last_index:]))
    return lines


# TAF line report type and start/end times
def get_type_and_times(wxdata: typing.List[str]) -> typing.Tuple[typing.List[str], str, str, str]:
    """
    Returns the report list and removed:
    Report type string, start time string, end time string
    """
    report_type, start_time, end_time = 'FROM', '', ''
    if wxdata:
        # TEMPO, BECMG, INTER
        if wxdata[0] in TAF_NEWLINE:
            report_type = wxdata.pop(0)
        # PROB[30,40]
        elif len(wxdata[0]) == 6 and wxdata[0].startswith('PROB'):
            report_type = wxdata.pop(0)
    if wxdata:
        # 1200/1306
        if len(wxdata[0]) == 9 and wxdata[0][4] == '/' and wxdata[0][:4].isdigit() and wxdata[0][5:].isdigit():
            start_time, end_time = wxdata.pop(0).split('/')
        # FM120000
        elif len(wxdata[0]) > 7 and wxdata[0].startswith('FM'):
            report_type = 'FROM'
            if '/' in wxdata[0] and wxdata[0][2:].split('/')[0].isdigit() and wxdata[0][2:].split('/')[1].isdigit():
                start_time, end_time = wxdata.pop(0)[2:].split('/')
            elif wxdata[0][2:8].isdigit():
                start_time = wxdata.pop(0)[2:6]
            # TL120600
            if wxdata and len(wxdata[0]) > 7 and wxdata[0].startswith('TL') and wxdata[0][2:8].isdigit():
                end_time = wxdata.pop(0)[2:6]
    return wxdata, report_type, start_time, end_time


def _is_tempo_or_prob(report_type: str) -> bool:
    """
    Returns True if report type is TEMPO or PROB__
    """
    if report_type == 'TEMPO':
        return True
    if len(report_type) == 6 and report_type.startswith('PROB'):
        return True
    return False


def _get_next_time(lines: typing.List[dict], target: str) -> str:
    """
    Returns the next FROM target value or empty
    """
    for line in lines:
        if line[target] and not _is_tempo_or_prob(line['type']):
            return line[target]
    return ''


def find_missing_taf_times(lines: typing.List[dict], start: str, end: str) -> typing.List[dict]:
    """
    Fix any missing time issues (except for error/empty lines)
    """
    if not lines:
        return lines
    # Assign start time
    lines[0]['start_time'] = start
    # Fix other times
    last_fm_line = 0
    for i, line in enumerate(lines):
        if _is_tempo_or_prob(line['type']):
            continue
        last_fm_line = i
        # Search remaining lines to fill empty end or previous for empty start
        for target, other, direc in (('start', 'end', -1), ('end', 'start', 1)):
            target += '_time'
            if not line[target]:
                line[target] = _get_next_time(lines[i::direc][1:], other + '_time')
    # Special case for final forecast
    if last_fm_line:
        lines[last_fm_line]['end_time'] = end
    # Reset original end time if still empty
    if lines and not lines[0]['end_time']:
        lines[0]['end_time'] = end
    return lines


def get_temp_min_and_max(wxlist: typing.List[str]) -> typing.Tuple[typing.List[str], str, str]:
    """
    Pull out Max temp at time and Min temp at time items from wx list
    """
    temp_max, temp_min = '', ''
    for i, item in reversed(list(enumerate(wxlist))):
        if len(item) > 6 and item[0] == 'T' and '/' in item:
            # TX12/1316Z
            if item[1] == 'X':
                temp_max = wxlist.pop(i)
            # TNM03/1404Z
            elif item[1] == 'N':
                temp_min = wxlist.pop(i)
            # TM03/1404Z T12/1316Z -> Will fix TN/TX
            elif item[1] == 'M' or item[1].isdigit():
                if temp_min:
                    _val1 = int(temp_min[2:temp_min.find('/')].replace('M', '-'))
                    _val2 = int(item[1:item.find('/')].replace('M', '-'))
                    if _val1 > _val2:
                        temp_max = 'TX' + temp_min[2:]
                        temp_min = 'TN' + item[1:]
                    else:
                        temp_max = 'TX' + item[1:]
                else:
                    temp_min = 'TN' + item[1:]
                wxlist.pop(i)
    return wxlist, temp_max, temp_min


def _get_digit_list(alist: typing.List[str], from_index: int) -> typing.Tuple[typing.List[str], typing.List[str]]:
    """
    Returns a list of items removed from a given list of strings
    that are all digits from 'from_index' until hitting a non-digit item
    """
    ret = []
    alist.pop(from_index)
    while len(alist) > from_index and alist[from_index].isdigit():
        ret.append(alist.pop(from_index))
    return alist, ret


def get_oceania_temp_and_alt(wxlist: typing.List[str]
                             ) -> typing.Tuple[typing.List[str], typing.List[str], typing.List[str]]:
    """
    Get Temperature and Altimeter lists for Oceania TAFs
    """
    tlist: typing.List[str]
    qlist: typing.List[str]
    if 'T' in wxlist:
        wxlist, tlist = _get_digit_list(wxlist, wxlist.index('T'))
    if 'Q' in wxlist:
        wxlist, qlist = _get_digit_list(wxlist, wxlist.index('Q'))
    return wxlist, tlist, qlist


def sanitize_cloud(cloud: str) -> str:
    """
    Fix rare cloud layer issues
    """
    if len(cloud) < 4:
        return cloud
    if not cloud[3].isdigit() and cloud[3] != '/':
        if cloud[3] == 'O':
            cloud = cloud[:3] + '0' + cloud[4:]  # Bad "O": FEWO03 -> FEW003
        else:  # Move modifiers to end: BKNC015 -> BKN015C
            cloud = cloud[:3] + cloud[4:] + cloud[3]
    if not cloud.startswith('VV'):
        if len(cloud) < 6 or (not cloud[5].isdigit() and not cloud[4] == '/'):
            cloud = cloud[:3] + '0' + cloud[3:]
    return cloud


def split_cloud(cloud: str) -> typing.Tuple[typing.Optional[str], typing.Optional[int], typing.Optional[str]]:
    """
    Transforms a cloud string into a list of strings: [Type, Height (, Optional Modifier)]
    """
    split: typing.List[typing.Any] = []
    cloud = sanitize_cloud(cloud)
    if cloud.startswith('VV'):
        split.append(cloud[:2])
        cloud = cloud[2:]
    while len(cloud) >= 3:
        split.append(cloud[:3])
        cloud = cloud[3:]
    if cloud:
        split.append(cloud)
    # Nullify unknown elements
    for i, item in enumerate(split):
        if is_unknown(item):
            split[i] = None
    # Add null altitude or convert to int
    if len(split) == 1:
        split.append(None)
    elif isinstance(split[1], str) and split[1].isdigit():
        split[1] = int(split[1])
    if len(split) == 2:
        split.append(None)
    _cloud_type: typing.Optional[str] = split[0] or None
    _cloud_altitude: typing.Optional[int] = int(split[1]) if split[1] else None
    _clout_modifier: typing.Optional[str] = split[2] or None
    return _cloud_type, _cloud_altitude, _clout_modifier
    # return split[0], split[1], split[2]


def make_cloud(cloud: str) -> Cloud:
    """
    Returns a Cloud dataclass for a cloud string

    This function assumes the input is potentially valid
    """
    return Cloud(cloud, *split_cloud(cloud))


def get_clouds(wxdata: typing.List[str]) -> typing.Tuple[typing.List[str], typing.List[Cloud]]:
    """
    Returns the report list and removed list of split cloud layers
    """
    clouds = []
    for i, item in reversed(list(enumerate(wxdata))):
        if item[:3] in CLOUD_LIST or item[:2] == 'VV':
            cloud: str = wxdata.pop(i)
            if '/' in cloud:
                cloud = cloud.split('/')[0]
            # if cloud.endswith('TCU'):
            #     cloud = cloud.replace('TCU', 'CU')
            made_cloud = make_cloud(cloud)
            clouds.append(made_cloud)
    try:
        return wxdata, sorted(clouds, key=lambda cloud_: (cloud_.altitude, cloud_.type))
    except TypeError:
        return wxdata, clouds


def get_flight_rules(vis: Number, ceiling: typing.Optional[Cloud]) -> int:
    """
    Returns int based on current flight rules from parsed METAR data

    0=VFR, 1=MVFR, 2=IFR, 3=LIFR

    Note: Common practice is to report IFR if visibility unavailable
    """
    # Parse visibility
    if vis is None:
        return 2
    if vis.repr is not None and (vis.repr == 'CAVOK' or vis.repr.startswith('P6')):
        vis_value = 10
    elif vis.repr is not None and vis.repr.startswith('M'):
        vis_value = 0
    # Convert meters to miles
    elif vis.value is not None and vis.repr is not None and len(vis.repr) == 4:
        vis_value = int(vis.value * 0.000621371)
    elif vis.value is not None:
        vis_value = int(vis.value)
    else:
        return 2
    # Parse ceiling
    cld = ceiling.altitude if (ceiling is not None and ceiling.altitude is not None) else 99
    # Determine flight rules
    if (vis_value <= 5) or (cld <= 30):
        if (vis_value < 3) or (cld < 10):
            if (vis_value < 1) or (cld < 5):
                return 3  # LIFR
            return 2  # IFR
        return 1  # MVFR
    return 0  # VFR


def get_taf_flight_rules(lines: typing.List[dict]) -> typing.List[dict]:
    """
    Get flight rules by looking for missing data in prior reports
    """
    for i, line in enumerate(lines):
        temp_vis, temp_cloud = line['visibility'], line['clouds']
        for report in reversed(lines[:i]):
            if not _is_tempo_or_prob(report['type']):
                if temp_vis == '':
                    temp_vis = report['visibility']
                if 'SKC' in report['other'] or 'CLR' in report['other']:
                    temp_cloud = 'temp-clear'
                elif not temp_cloud:
                    temp_cloud = report['clouds']
                if temp_vis != '' and temp_cloud != []:
                    break
        if temp_cloud == 'temp-clear':
            temp_cloud = []
        line['flight_rules'] = FLIGHT_RULES[get_flight_rules(temp_vis, get_ceiling(temp_cloud))]
    return lines


def get_ceiling(clouds: typing.List[Cloud]) -> typing.Optional[Cloud]:
    """
    Returns ceiling layer from Cloud-List or None if none found

    Assumes that the clouds are already sorted lowest to highest

    Only 'Broken', 'Overcast', and 'Vertical Visibility' are considered ceilings

    Prevents errors due to lack of cloud information (eg. '' or 'FEW///')
    """
    for cloud in clouds:
        if cloud.altitude and cloud.type in ('OVC', 'BKN', 'VV'):
            return cloud
    return None


def parse_date(date: str, hour_threshold: int = 200) -> typing.Optional[datetime]:
    """
    Parses a report timestamp in ddhhZ or ddhhmmZ format

    This function assumes the given timestamp is within the hour threshold from current date
    """
    # Format date string
    if not isinstance(date, str):
        return None
    date = date.strip('Z')
    if len(date) == 4:
        date += '00'
    if not (len(date) == 6 and date.isdigit()):
        return None
    # Create initial guess
    now = datetime.utcnow()
    guess = now.replace(day=int(date[0:2]),
                        hour=int(date[2:4]) % 24,
                        minute=int(date[4:6]) % 60,
                        second=0, microsecond=0)
    hourdiff = (guess - now) / timedelta(minutes=1) / 60
    # Handle changing months
    if hourdiff > hour_threshold:
        guess += relativedelta(months=-1)
    elif hourdiff < -hour_threshold:
        guess += relativedelta(months=+1)
    return guess


def make_timestamp(timestamp: str) -> Timestamp:
    """
    Returns a Timestamp dataclass for a report timestamp in ddhhZ or ddhhmmZ format
    """
    return Timestamp(timestamp, parse_date(timestamp))
