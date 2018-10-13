# coding=utf-8
# type: ignore
"""
Michael duPont - michael@mdupont.com
Original source: https://github.com/flyinactor91/AVWX-Engine
Modified by etcher@daribouca.net
"""
import logging
# type: ignore
# stdlib
# module
import typing

from elib_wx.avwx import core, remarks, service
from elib_wx.avwx.static import FLIGHT_RULES, IN_UNITS, NA_UNITS
from elib_wx.avwx.structs import MetarData, Units

LOGGER = logging.getLogger('elib.wx')


def fetch(station: str) -> str:
    """
    Returns METAR report string or raises an error

    Maintains backwards comparability but uses the new Service object.
    It is recommended to use the Service class directly instead of this function
    """
    LOGGER.debug('fetching METAR for station: %s', station)
    return service.get_service(station)('metar').fetch(station)


def parse(station: str, txt: str) -> typing.Tuple[MetarData, Units]:
    """
    Returns MetarData and Units dataclasses with parsed data and their associated units
    """
    core.valid_station(station)
    return parse_na(txt) if core.uses_na_format(station[:2]) else parse_in(txt)


def parse_na(txt: str) -> typing.Tuple[MetarData, Units]:
    """
    Parser for the North American METAR variant
    """
    units = Units(**NA_UNITS)
    clean = core.sanitize_report_string(txt)
    wxresp: typing.Dict[str, typing.Any] = {'raw': txt, 'sanitized': clean}
    wxdata, wxresp['remarks'] = core.get_remarks(clean)
    wxdata, wxresp['runway_visibility'], _ = core.sanitize_report_list(wxdata)
    wxdata, wxresp['station'], wxresp['time'] = core.get_station_and_time(wxdata)
    wxdata, wxresp['clouds'] = core.get_clouds(wxdata)
    wxdata, wind_dir, wind_speed, wind_gust, wind_var = core.get_wind(wxdata, units)
    wxresp['wind_direction'] = wind_dir
    wxresp['wind_speed'] = wind_speed
    wxresp['wind_gust'] = wind_gust
    wxresp['wind_variable_direction'] = wind_var
    wxdata, wxresp['altimeter'] = core.get_altimeter(wxdata, units)
    wxdata, wxresp['visibility'] = core.get_visibility(wxdata, units)
    wxresp['other'], wxresp['temperature'], wxresp['dewpoint'] = core.get_temp_and_dew(wxdata)
    condition = core.get_flight_rules(wxresp['visibility'], core.get_ceiling(wxresp['clouds']))
    wxresp['flight_rules'] = FLIGHT_RULES[condition]
    wxresp['remarks_info'] = remarks.parse(wxresp['remarks'])
    wxresp['time'] = core.make_timestamp(wxresp['time'])
    return MetarData(**wxresp), units


def parse_in(txt: str) -> typing.Tuple[MetarData, Units]:
    """
    Parser for the International METAR variant
    """
    units = Units(**IN_UNITS)
    clean = core.sanitize_report_string(txt)
    wxresp: typing.Dict[str, typing.Any] = {'raw': txt, 'sanitized': clean}
    wxdata, wxresp['remarks'] = core.get_remarks(clean)
    wxdata, wxresp['runway_visibility'], _ = core.sanitize_report_list(wxdata)
    wxdata, wxresp['station'], wxresp['time'] = core.get_station_and_time(wxdata)
    if 'CAVOK' not in wxdata:
        wxdata, wxresp['clouds'] = core.get_clouds(wxdata)
    wxdata, wind_dir, wind_speed, wind_gust, wind_var = core.get_wind(wxdata, units)
    wxresp['wind_direction'] = wind_dir
    wxresp['wind_speed'] = wind_speed
    wxresp['wind_gust'] = wind_gust
    wxresp['wind_variable_direction'] = wind_var
    wxdata, wxresp['altimeter'] = core.get_altimeter(wxdata, units, 'IN')
    if 'CAVOK' in wxdata:
        wxresp['visibility'] = core.make_number('CAVOK')
        wxresp['clouds'] = []
        wxdata.remove('CAVOK')
    else:
        wxdata, wxresp['visibility'] = core.get_visibility(wxdata, units)
    wxresp['other'], wxresp['temperature'], wxresp['dewpoint'] = core.get_temp_and_dew(wxdata)
    condition = core.get_flight_rules(wxresp['visibility'], core.get_ceiling(wxresp['clouds']))
    wxresp['flight_rules'] = FLIGHT_RULES[condition]
    wxresp['remarks_info'] = remarks.parse(wxresp['remarks'])
    wxresp['time'] = core.make_timestamp(wxresp['time'])
    return MetarData(**wxresp), units
