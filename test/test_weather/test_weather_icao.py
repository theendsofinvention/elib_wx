# coding=utf-8

import pytest

import elib_wx


@pytest.mark.weather
def test_unknown_icao():
    metar_str = 'KZZZ 121053Z AUTO 10SM -RA OVC050 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122'
    wx = elib_wx.Weather(metar_str)
    assert 'unknown airport (KZZZ)' == wx.station_name


@pytest.mark.weather
def test_wrong_icao():
    metar_str = '1234 121053Z AUTO 10SM -RA OVC050 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122'
    with pytest.raises(elib_wx.BadStationError):
        elib_wx.Weather(metar_str)


@pytest.mark.weather
def test_known_icao(with_db):
    metar_str = 'KLAS 121053Z AUTO 10SM -RA OVC050 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122'
    wx = elib_wx.Weather(metar_str)
    assert wx.station_name == 'McCarran International Airport'
