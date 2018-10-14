# coding=utf-8

import pytest

import elib_wx
from test.utils import _TestCall, _TestValue


@pytest.mark.parametrize(
    'metar_str, expected',
    [
        (
            'KLAW 121053Z AUTO 06006KT 10SM -RA OVC040 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 '
            'T01330122',
            (
                _TestValue(attr_name='visibility', expected_result=16100, get_value=True),
                _TestValue(attr_name='visibility', expected_result=10, get_value=True, units='SM'),
                _TestCall(attr_name='_visibility_as_str',
                          expected='Visibility 10km or more, 10SM or more.',
                          spoken=False),
                _TestCall(attr_name='_visibility_as_str',
                          expected='Visibility ten kilometers or more, ten miles or more.',
                          spoken=True),
            ),
        ),
        (
            'KLAW 121053Z AUTO 06006KT 5SM -RA OVC040 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 '
            'T01330122',
            (
                _TestValue(attr_name='visibility', expected_result=8000, get_value=True),
                _TestValue(attr_name='visibility', expected_result=5, get_value=True, units='SM'),
                _TestCall(attr_name='_visibility_as_str',
                          expected='Visibility 8000m, 5.0SM.',
                          spoken=False),
                _TestCall(attr_name='_visibility_as_str',
                          expected='Visibility eight kilometers, five point zero miles.',
                          spoken=True),
            ),
        ),
        (
            'KLAW 121053Z AUTO 06006KT 6500 -RA OVC040 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 '
            'T01330122',
            (
                _TestValue(attr_name='visibility', expected_result=6500, get_value=True),
                _TestValue(attr_name='visibility', expected_result=4.0, get_value=True, units='SM'),
                _TestCall(attr_name='_visibility_as_str',
                          expected='Visibility 6500m, 4.0SM.',
                          spoken=False),
                _TestCall(attr_name='_visibility_as_str',
                          expected='Visibility six thousand five hundred meters, four point zero miles.',
                          spoken=True),
            ),
        ),
        (
            'KLAW 121053Z AUTO 06006KT 9999 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122',
            (
                _TestCall(attr_name='_visibility_as_str',
                          expected='CAVOK.',
                          spoken=False),
                _TestCall(attr_name='_visibility_as_str',
                          expected='cavok.',
                          spoken=True),
            ),
        ),
        (
            'KLAW 121053Z AUTO 06006KT 9999 OVC050 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122',
            (
                _TestCall(attr_name='_visibility_as_str',
                          expected='CAVOK.',
                          spoken=False),
                _TestCall(attr_name='_visibility_as_str',
                          expected='cavok.',
                          spoken=True),
            ),
        ),
        (
            'KLAW 121053Z AUTO 06006KT 9999 OVC050TCU 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 '
            'T01330122',
            (
                _TestCall(attr_name='_visibility_as_str',
                          expected='Visibility 10km or more, 10SM or more.',
                          spoken=False),
                _TestCall(attr_name='_visibility_as_str',
                          expected='Visibility ten kilometers or more, ten miles or more.',
                          spoken=True),
            ),
        ),
        (
            'KLAW 121053Z AUTO 06006KT 9999 OVC050CB 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 '
            'T01330122',
            (
                _TestCall(attr_name='_visibility_as_str',
                          expected='Visibility 10km or more, 10SM or more.',
                          spoken=False),
                _TestCall(attr_name='_visibility_as_str',
                          expected='Visibility ten kilometers or more, ten miles or more.',
                          spoken=True),
            ),
        ),
        (
            'KLAW 121053Z AUTO 06006KT 9999 OVC050CI 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 '
            'T01330122',
            (
                _TestCall(attr_name='_visibility_as_str',
                          expected='CAVOK.',
                          spoken=False),
                _TestCall(attr_name='_visibility_as_str',
                          expected='cavok.',
                          spoken=True),
            ),
        ),
    ]
)
@pytest.mark.weather
def test_visibility_in_weather_from_metar_str(metar_str, expected):
    wx = elib_wx.Weather(metar_str)
    assert isinstance(wx, elib_wx.Weather)
    for test_value in expected:
        expected, actual = test_value.verify(wx)
        assert expected == actual


@pytest.mark.weather
def test_visibility_in_weather_from_metar_str_no_visibility_given():
    wx = elib_wx.Weather(
        'KLAW 121053Z AUTO -RA OVC050 13/12 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122'
    )
    assert isinstance(wx, elib_wx.Weather)
    assert wx.visibility.value()
    assert 2000 <= wx.visibility.value() <= 20000


@pytest.mark.parametrize(
    'visibility, expected',
    [
        ('P6SM', 9999),
        ('M1/4SM', 400),
    ]
)
@pytest.mark.weather
def test_visibility_in_weather_from_metar_str_special_cases(visibility, expected):
    wx = elib_wx.Weather(
        f'KLAW 121053Z AUTO {visibility} -RA OVC050 13/12 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122'
    )
    assert isinstance(wx, elib_wx.Weather)
    assert expected == wx.visibility.value()
