# coding=utf-8

import pytest
from mockito import expect, when

from elib_wx import avwx, exc, utils, weather


def test_from_metar_string():
    test_string = 'some string'
    test_icao = 'UGTB'
    expect(weather.Weather)._set_station_name()
    expect(weather.Weather).fill_from_metar_data()
    when(utils).extract_station_from_metar_str(test_string).thenReturn(test_icao)
    when(avwx.metar).parse(test_icao, test_string).thenReturn(('metar data', 'metar_units'))
    wx = weather.Weather(test_string)
    assert wx.source == test_string
    assert wx.station_icao == test_icao
    assert wx.source_type == 'METAR'


def test_from_icao():
    test_icao = 'UGTB'
    metar_string = 'metar string'
    expect(weather.Weather)._set_station_name()
    expect(weather.Weather).fill_from_metar_data()
    when(avwx.metar).fetch(test_icao).thenReturn(metar_string)
    when(avwx.metar).parse(test_icao, metar_string).thenReturn(('metar data', 'metar_units'))
    wx = weather.Weather(test_icao)
    assert wx.source == test_icao
    assert wx.station_icao == test_icao
    assert wx.source_type == 'ICAO'


@pytest.mark.parametrize(
    'source', [None, 1, -1, 0, False, True, None, 0.1]
)
@pytest.mark.weather
def test_wrong_source(source):
    with pytest.raises(exc.InvalidWeatherSourceError):
        # noinspection PyTypeChecker
        weather.Weather(source)
