# coding=utf-8

import pytest

import elib_wx
from test.utils import _TestCall, _TestValue


@pytest.mark.parametrize(
    'metar_str, expected',
    [
        (
            'KLAW 121053Z AUTO 06006KT 10SM -RA OVC050 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 '
            'T01330122',
            (
                _TestValue(attr_name='altimeter', expected_result=30.01, get_value=True, units='inhg'),
                _TestCall(attr_name='_altimeter_as_str',
                          expected='Altimeter 762mmHg, 1016hPa, 30.01inHg.',
                          spoken=False),
                _TestCall(attr_name='_altimeter_as_str',
                          expected='Altimeter seven six two millimeters of mercury, one zero one six hecto Pascals, '
                                   'three zero point zero one inches of mercury.',
                          spoken=True),
            ),
        ),
        (
            'KLAW 121053Z AUTO 06006KT 10SM -RA OVC050 13/12 Q1013 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 '
            'T01330122',
            (
                _TestValue(attr_name='altimeter', expected_result=1013, get_value=True, units='hpa'),
                _TestValue(attr_name='altimeter', expected_result=29.91, get_value=True, units='inhg'),
                _TestValue(attr_name='altimeter', expected_result=760, get_value=True, units='mmhg'),
                _TestCall(attr_name='_altimeter_as_str',
                          expected='Altimeter 760mmHg, 1013hPa, 29.91inHg.',
                          spoken=False),
                _TestCall(attr_name='_altimeter_as_str',
                          expected='Altimeter seven six zero millimeters of mercury, one zero one three hecto Pascals, '
                                   'two nine point nine one inches of mercury.',
                          spoken=True),
            ),
        ),
    ]
)
@pytest.mark.weather
def test_altimeter_in_weather_from_metar_str(metar_str, expected):
    wx = elib_wx.Weather(metar_str)
    assert isinstance(wx, elib_wx.Weather)
    for test_value in expected:
        expected, actual = test_value.verify(wx)
        assert expected == actual


@pytest.mark.weather
def test_altimeter_in_weather_from_metar_str_no_altimeter_given():
    wx = elib_wx.Weather(
        'KLAW 121053Z AUTO 10SM -RA OVC050 13/12 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122'
    )
    assert isinstance(wx, elib_wx.Weather)
    assert wx.altimeter.value()
    assert 720 <= wx.altimeter.value() <= 790
