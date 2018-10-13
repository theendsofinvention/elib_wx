# coding=utf-8

import pytest
from mockito import expect

import elib_wx


@pytest.mark.weather
def test_weather_from_icao(with_db):
    icao = 'EBBR'
    expect(elib_wx.avwx.metar).fetch(icao).thenReturn('raw metar str')
    expect(elib_wx.avwx.metar).parse(icao, 'raw metar str').thenReturn(('metar data', 'metar units'))
    expect(elib_wx.Weather).fill_from_metar_data()
    wx = elib_wx.Weather(icao)
    assert wx.source_type == 'ICAO'
    assert wx.metar_data == 'metar data'
    assert wx.metar_units == 'metar units'
    assert wx.station_name == 'Brussels Airport'


@pytest.mark.weather
def test_weather_from_icao_unknown_icao():
    icao = 'KLXX'
    expect(elib_wx.avwx.metar).fetch(icao).thenReturn('raw metar str')
    expect(elib_wx.avwx.metar).parse(icao, 'raw metar str').thenReturn(('metar data', 'metar units'))
    expect(elib_wx.Weather).fill_from_metar_data()
    wx = elib_wx.Weather(icao)
    assert 'unknown airport (KLXX)' == wx.station_name


@pytest.mark.weather
def test_weather_from_icao_wrong_icao():
    icao = '1234'
    with pytest.raises(elib_wx.BadStationError):
        elib_wx.Weather(icao)
