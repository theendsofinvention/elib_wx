# coding=utf-8

import pytest

import elib_wx
from elib_wx.values.value import Temperature
import elib_wx.static
from test.utils import _TestValue
from hypothesis import strategies as st, given, settings

_TEST_DATA = [
    (
        # Generic test
        'KLAW 121053Z AUTO 06006KT 10SM OVC050 13/12 Q1013 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122',
        (
            _TestValue(attr_name='altimeter', expected_result=760),
            _TestValue(attr_name='temperature', expected_result=13),
            _TestValue(attr_name='wind_ground_speed', expected_result=3),
            _TestValue(attr_name='wind_ground_dir', expected_result=60),
            _TestValue(attr_name='turbulence', expected_result=0),
            _TestValue(attr_name='fog_enabled', expected_result=False),
            _TestValue(attr_name='fog_thickness', expected_result=1000),
            _TestValue(attr_name='fog_visibility', expected_result=6000),
            _TestValue(attr_name='dust_enabled', expected_result=False),
            _TestValue(attr_name='dust_density', expected_result=3000),
            _TestValue(attr_name='precipitation_code', expected_result=0),
        )
    ),
    (
        # Reported visibility at 5000
        'KLAW 121053Z AUTO 06006KT 5000 -RA OVC050 13/12 Q1013 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122',
        (
            _TestValue(attr_name='fog_enabled', expected_result=True),
            _TestValue(attr_name='fog_thickness', expected_result=1000),
            _TestValue(attr_name='fog_visibility', expected_result=5000),
        ),
    ),
    (
        # Reported visibility over 6000
        'KLAW 121053Z AUTO 06006KT 8000 -RA OVC050 13/12 Q1013 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122',
        (
            _TestValue(attr_name='fog_enabled', expected_result=True),
            _TestValue(attr_name='fog_thickness', expected_result=1000),
            _TestValue(attr_name='fog_visibility', expected_result=6000),
        ),
    ),
    (
        # Turbulence
        'KLAW 121053Z AUTO 06006G12KT 8000 OVC050 13/12 Q1013 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122',
        (
            _TestValue(attr_name='turbulence', expected_result=20),
            _TestValue(attr_name='wind_ground_speed', expected_result=3),
        ),
    ),
]


@pytest.mark.weather
# @pytest.mark.parametrize(
#     'metar, expected', _TEST_DATA
# )
def test_generate_dcs_weather(test_data):
    metar, expected = test_data
    wx = elib_wx.Weather(metar)
    dcs_wx = wx.generate_dcs_weather()
    for test_value in expected:
        expected, actual = test_value.verify(dcs_wx)
        assert expected == actual


# noinspection PyProtectedMember
_CLOUDS_TEST_DATA = [(k, v) for k, v in elib_wx.static.CLOUD_METAR_TO_DCS.items()]
# noinspection PyProtectedMember
_CLOUDS_TEST_IDS = [repr(k) + '_' + repr(v) for k, v in elib_wx.static.CLOUD_METAR_TO_DCS.items()]


@pytest.mark.parametrize('coverage, range_', _CLOUDS_TEST_DATA, ids=_CLOUDS_TEST_IDS)
@pytest.mark.weather
def test_generate_dcs_weather_cloud_layers(coverage, range_):
    _min_coverage = 0
    metar = f'KLAW 121053Z AUTO 06006KT 10SM {coverage}050 13/12 Q1013'
    wx = elib_wx.Weather(metar)
    dcs_wx = wx.generate_dcs_weather()
    assert max(_min_coverage, range_[0]) <= dcs_wx.cloud_density <= max(_min_coverage, range_[1])


@pytest.mark.parametrize('coverage, range_', _CLOUDS_TEST_DATA, ids=_CLOUDS_TEST_IDS)
@pytest.mark.parametrize('rain_marker', ('DZ', 'SH', 'RA', 'UP'))
@pytest.mark.parametrize('modifier', ('', '-', '+'))
@given(temperature=st.floats(allow_infinity=False, allow_nan=False))
@settings(max_examples=20)
@pytest.mark.weather
def test_generate_dcs_weather_rain(coverage, range_, rain_marker, modifier, temperature):
    _min_coverage = 5
    metar = f'KLAW 121053Z AUTO 06006KT 10SM {modifier}{rain_marker} {coverage}050 ///// Q1013'
    wx = elib_wx.Weather(metar)
    wx.temperature = Temperature(temperature)
    dcs_wx = wx.generate_dcs_weather()
    assert max(_min_coverage, range_[0]) <= dcs_wx.cloud_density <= max(_min_coverage, range_[1])
    assert 1 == dcs_wx.precipitation_code
    assert 0 <= dcs_wx.temperature


def test_generate_dcs_weather_rain_debug():
    _min_coverage = 5
    metar = f'KLAW 121053Z AUTO 06006KT 10SM +RA BKN050 M01/M01 Q1013'
    wx = elib_wx.Weather(metar)
    dcs_wx = wx.generate_dcs_weather()
    assert 1 == dcs_wx.precipitation_code
    assert 0 <= dcs_wx.temperature


@pytest.mark.parametrize('coverage, range_', _CLOUDS_TEST_DATA, ids=_CLOUDS_TEST_IDS)
@pytest.mark.parametrize('snow_marker', ('SN',))
@pytest.mark.parametrize('modifier', ('', '-', '+'))
@given(temperature=st.floats(allow_infinity=False, allow_nan=False))
@settings(max_examples=20)
@pytest.mark.weather
def test_generate_dcs_weather_snow(coverage, range_, snow_marker, modifier, temperature):
    _min_coverage = 5
    metar = f'KLAW 121053Z AUTO 06006KT 10SM {modifier}{snow_marker} {coverage}050 {temperature}/// Q1013'
    wx = elib_wx.Weather(metar)
    dcs_wx = wx.generate_dcs_weather()
    assert max(_min_coverage, range_[0]) <= dcs_wx.cloud_density <= max(_min_coverage, range_[1])
    assert dcs_wx.temperature < 0
    assert 3 == dcs_wx.precipitation_code


@pytest.mark.parametrize('coverage, range_', _CLOUDS_TEST_DATA, ids=_CLOUDS_TEST_IDS)
@pytest.mark.parametrize('snow_marker', ('TS',))
@pytest.mark.parametrize('modifier', ('', '-', '+'))
@given(temperature=st.floats(allow_infinity=False, allow_nan=False))
@settings(max_examples=20)
@pytest.mark.weather
def test_generate_dcs_weather_thunderstorm(coverage, range_, snow_marker, modifier, temperature):
    _min_coverage = 9
    metar = f'KLAW 121053Z AUTO 06006KT 10SM {modifier}{snow_marker} {coverage}050 {temperature}/// Q1013'
    wx = elib_wx.Weather(metar)
    dcs_wx = wx.generate_dcs_weather()
    assert max(_min_coverage, range_[0]) <= dcs_wx.cloud_density <= max(_min_coverage, range_[1])
    assert 2 == dcs_wx.precipitation_code
    assert 0 <= dcs_wx.temperature


@pytest.mark.parametrize('coverage, range_', _CLOUDS_TEST_DATA, ids=_CLOUDS_TEST_IDS)
@pytest.mark.parametrize('snow_marker', ('GR', 'SG', 'PL', 'GS'))
@pytest.mark.parametrize('modifier', ('', '-', '+'))
@given(temperature=st.floats(allow_infinity=False, allow_nan=False))
@settings(max_examples=20)
@pytest.mark.weather
def test_generate_dcs_weather_snow_storm(coverage, range_, snow_marker, modifier, temperature):
    _min_coverage = 9
    metar = f'KLAW 121053Z AUTO 06006KT 10SM {modifier}{snow_marker} {coverage}050 {temperature}/// Q1013'
    wx = elib_wx.Weather(metar)
    dcs_wx = wx.generate_dcs_weather()
    assert max(_min_coverage, range_[0]) <= dcs_wx.cloud_density <= max(_min_coverage, range_[1])
    assert dcs_wx.temperature < 0
    assert 4 == dcs_wx.precipitation_code
    assert dcs_wx.temperature < 0


@pytest.mark.parametrize('dust_marker', ('DU', 'DS', 'PO', 'SS'))
@pytest.mark.parametrize('modifier', ('', '-', '+'))
@pytest.mark.parametrize('visibility', [100, 200, 300, 500, 1000, 3000, 5000, 8000, 9999])
@pytest.mark.weather
def test_generate_dcs_weather_dust(dust_marker, modifier, visibility):
    metar = f'KLAW 121053Z AUTO 06006KT {visibility:04d} {modifier}{dust_marker} 050 13/12 Q1013'
    wx = elib_wx.Weather(metar)
    dcs_wx = wx.generate_dcs_weather()
    dust_visibility = (min(300, visibility), max(3000, visibility))
    if visibility <= 5000:
        assert dcs_wx.dust_enabled is True
        assert max(300, dust_visibility[0]) <= dcs_wx.dust_density <= min(3000, dust_visibility[1])
    else:
        assert dcs_wx.dust_enabled is False
        assert 3000 == dcs_wx.dust_density


@pytest.mark.weather
def test_missing_cloud_layer_altitude():
    wx = elib_wx.Weather('KLAW 121053Z AUTO 06006KT 10SM OVC050 13/12 Q1013')
    wx.cloud_layers[0].altitude = None
    dcs_wx = wx.generate_dcs_weather()
    assert 5000 <= dcs_wx.cloud_base <= 25000
    assert 0 == dcs_wx.cloud_base % 1000


@pytest.mark.weather
def test_wrong_cloud_layer_altitude():
    wx = elib_wx.Weather('KLAW 121053Z AUTO 06006KT 10SM OVC050 13/12 Q1013')
    wx.metar_units.altitude = 'test'
    with pytest.raises(ValueError):
        wx.generate_dcs_weather()


@pytest.mark.weather
def test_turbulence_but_wind_speed_zero():
    wx = elib_wx.Weather('KLAW 121053Z AUTO 06006G12KT 10SM OVC050 13/12 Q1013')
    wx.wind_speed._raw_value = 0
    assert wx.wind_gust.value() > 0
    dcs_wx = wx.generate_dcs_weather()
    assert dcs_wx.turbulence > 0
    assert 1 == dcs_wx.wind_ground_speed
    assert 1 == wx.wind_speed.value()
