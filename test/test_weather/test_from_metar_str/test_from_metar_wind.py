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
                _TestValue(attr_name='wind_speed', expected_result=6, get_value=True, units='kt'),
                _TestValue(attr_name='wind_direction', expected_result=60, get_value=True),
                _TestCall(attr_name='_wind_as_str', expected='Wind 060 6kts.', spoken=False),
                _TestCall(attr_name='_wind_as_str', expected='Wind zero six zero six knots.', spoken=True),
            ),
        ),
        (
            'KLAW 121053Z AUTO 00005MPS 10SM -RA OVC050 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 '
            'T01330122',
            (
                _TestValue(attr_name='wind_speed', expected_result=5, get_value=True, units='m/s'),
                _TestValue(attr_name='wind_direction', expected_result=0, get_value=True),
                _TestCall(attr_name='_wind_as_str', expected='Wind 000 10kts.', spoken=False),
                _TestCall(attr_name='_wind_as_str', expected='Wind zero zero zero one zero knots.', spoken=True),
                _TestValue(attr_name='wind_gust', expected_result=0, get_value=True, units='kt'),
            ),
        ),
        (
            'AGTB 271030Z VRB02KT 8000 BKN030 BKN100 08/03 Q1015 NOSIG RMK 31CLRD80',
            (
                _TestValue(attr_name='wind_speed', expected_result=2, get_value=True, units='kt'),
                _TestCall(attr_name='_wind_as_str', expected='Wind variable 2kts.', spoken=False),
                _TestCall(attr_name='_wind_as_str', expected='Wind variable two knots.', spoken=True),
                _TestValue(attr_name='wind_gust', expected_result=0, get_value=True, units='kt'),
            ),
        ),
        (
            'AGTB 271030Z VRB00KT 8000 BKN030 BKN100 08/03 Q1015 NOSIG RMK 31CLRD80',
            (
                _TestValue(attr_name='wind_speed', expected_result=0, get_value=True, units='kt'),
                _TestValue(attr_name='wind_speed', expected_result=0, get_value=True, units='m/s'),
                _TestCall(attr_name='_wind_as_str', expected='Wind calm.', spoken=False),
                _TestCall(attr_name='_wind_as_str', expected='Wind calm.', spoken=True),
                _TestValue(attr_name='wind_gust', expected_result=0, get_value=True, units='kt'),
            ),
        ),
        (
            'AGTB 271030Z 30005KT 280V350 8000 BKN030 BKN100 08/03 Q1015 NOSIG RMK 31CLRD80',
            (
                _TestValue(attr_name='wind_speed', expected_result=5, get_value=True, units='kt'),
                _TestCall(attr_name='_wind_as_str', expected='Wind 300 (variable 280 to 350) 5kts.', spoken=False),
                _TestCall(attr_name='_wind_as_str',
                          expected='Wind three zero zero (variable two eight zero to three five zero) five knots.',
                          spoken=True),
                _TestValue(attr_name='wind_gust', expected_result=0, get_value=True, units='kt'),
            ),
        ),
        (
            'AGTB 271030Z VRB05KT 280V350 8000 BKN030 BKN100 08/03 Q1015 NOSIG RMK 31CLRD80',
            (
                _TestValue(attr_name='wind_speed', expected_result=5, get_value=True, units='kt'),
                _TestCall(attr_name='_wind_as_str', expected='Wind variable (variable 280 to 350) 5kts.', spoken=False),
                _TestCall(attr_name='_wind_as_str',
                          expected='Wind variable (variable two eight zero to three five zero) five knots.',
                          spoken=True),
                _TestValue(attr_name='wind_gust', expected_result=0, get_value=True, units='kt'),
            ),
        ),
        (
            'AGTB 271030Z 30005G10KT 8000 BKN030 BKN100 08/03 Q1015 NOSIG RMK 31CLRD80',
            (
                _TestValue(attr_name='wind_speed', expected_result=5, get_value=True, units='kt'),
                _TestValue(attr_name='wind_gust', expected_result=10, get_value=True, units='kt'),
                _TestCall(attr_name='_wind_as_str', expected='Wind 300 5kts (gusting 10kts knots).', spoken=False),
                _TestCall(attr_name='_wind_as_str',
                          expected='Wind three zero zero five knots (gusting one zero knots knots).',
                          spoken=True),
            ),
        ),
    ]
)
@pytest.mark.weather
def test_wind_in_weather_from_metar_str(metar_str, expected):
    wx = elib_wx.Weather(metar_str)
    assert isinstance(wx, elib_wx.Weather)
    for test_value in expected:
        expected, actual = test_value.verify(wx)
        assert expected == actual


@pytest.mark.weather
def test_wind_in_weather_from_metar_str_no_wind_given():
    wx = elib_wx.Weather(
        'KLAW 121053Z AUTO 10SM -RA OVC050 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122'
    )
    assert isinstance(wx, elib_wx.Weather)
    assert wx.wind_direction.value()
    assert 0 <= wx.wind_direction.value() <= 359
    assert wx.wind_speed.value()
    assert 0 <= wx.wind_speed.value() <= 25
