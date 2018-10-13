# coding=utf-8

import pytest

import elib_wx
from test.utils import _TestCall, _TestValue


@pytest.mark.parametrize(
    'metar_str, expected',
    [
        (
            'KLAW 121053Z AUTO 06006KT 10SM -RA OVC050 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 '
            'P0001 T01330122',
            (
                _TestValue(attr_name='temperature', expected_result=13, get_value=True, units='c'),
                _TestValue(attr_name='temperature', expected_result=55, get_value=True, units='f'),
                _TestValue(attr_name='dew_point', expected_result=12, get_value=True, units='c'),
                _TestValue(attr_name='dew_point', expected_result=54, get_value=True, units='f'),
                _TestCall(attr_name='_temperature_as_str', expected='Temperature 13°C, 55°F.', spoken=False),
                _TestCall(attr_name='_temperature_as_str',
                          expected='Temperature one three degrees celsius, five five degrees fahrenheit.',
                          spoken=True),
                _TestCall(attr_name='_dew_point_as_str', expected='Dew point 12°C, 54°F.', spoken=False),
                _TestCall(attr_name='_dew_point_as_str',
                          expected='Dew point one two degrees celsius, five four degrees fahrenheit.',
                          spoken=True),
            ),
        ),
        (
            'KLAW 121053Z AUTO 06006KT 10SM -RA OVC050 M13/M15 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 '
            'P0001 T01330122',
            (
                _TestValue(attr_name='temperature', expected_result=-13, get_value=True, units='c'),
                _TestValue(attr_name='temperature', expected_result=9, get_value=True, units='f'),
                _TestValue(attr_name='dew_point', expected_result=-15, get_value=True, units='c'),
                _TestValue(attr_name='dew_point', expected_result=5, get_value=True, units='f'),
                _TestCall(attr_name='_temperature_as_str', expected='Temperature -13°C, 9°F.', spoken=False),
                _TestCall(attr_name='_temperature_as_str',
                          expected='Temperature minus one three degrees celsius, nine degrees fahrenheit.',
                          spoken=True),
            ),
        ),
    ]
)
@pytest.mark.weather
def test_temperature_in_weather_from_metar_str(metar_str, expected):
    wx = elib_wx.Weather(metar_str)
    assert isinstance(wx, elib_wx.Weather)
    for test_value in expected:
        expected, actual = test_value.verify(wx)
        assert expected == actual


@pytest.mark.weather
def test_temperature_in_weather_from_metar_str_no_dewpoint_given():
    wx = elib_wx.Weather(
        'KLAW 121053Z AUTO 10SM -RA OVC050 13/// RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122'
    )
    assert isinstance(wx, elib_wx.Weather)
    assert wx.dew_point.value() < wx.temperature.value()


def test_temperature_in_weather_from_metar_str_no_temperature_given():
    wx = elib_wx.Weather(
        'KLAW 121053Z AUTO 10SM -RA OVC050 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122'
    )
    assert isinstance(wx, elib_wx.Weather)
    assert wx.dew_point.value() < wx.temperature.value()
