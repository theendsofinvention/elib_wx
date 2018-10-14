# coding=utf-8

import pytest
from hypothesis import given, strategies as st

import elib_wx
import elib_wx.static
from elib_wx import avwx
from test.utils import _TestCall, _TestValue

_TEST_DATA = [
    (
        'KLAW 121053Z AUTO 06006KT 2SM -RA 13/12 A3001',
        (
            _TestValue(attr_name='cloud_layers',
                       expected_result=[]),
            _TestCall(attr_name='_clouds_as_str',
                      expected='Sky clear.',
                      spoken=False),
            _TestCall(attr_name='_clouds_as_str',
                      expected='Sky clear.',
                      spoken=True),
        ),
    ),
    (
        'KLAW 121053Z AUTO 06006KT 10SM -RA OVC050 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122',
        (
            _TestValue(attr_name='cloud_layers',
                       expected_result=[
                           avwx.structs.Cloud(repr='OVC050', type='OVC', altitude=50, modifier=None)
                       ]),
            _TestCall(attr_name='_visibility_as_str',
                      expected='CAVOK.', spoken=False),
            _TestCall(attr_name='_clouds_as_str',
                      expected='', spoken=False),
            _TestCall(attr_name='_clouds_as_str',
                      expected='',
                      spoken=True),
        ),
    ),
    (
        'KLAW 121053Z AUTO 06006KT 10SM -RA OVC040 13/12 A3001 RMK AO2 LTG DSNT W RAB0957E08B45 SLP159 P0001 T01330122',
        (
            _TestValue(attr_name='cloud_layers',
                       expected_result=[
                           avwx.structs.Cloud(repr='OVC040', type='OVC', altitude=40, modifier=None)
                       ]),
            _TestCall(attr_name='_clouds_as_str',
                      expected='Overcast layer at 4000ft.', spoken=False),
            _TestCall(attr_name='_clouds_as_str',
                      expected='Overcast layer at four thousand feet.',
                      spoken=True),
        ),
    ),
    (
        'KLAW 121053Z AUTO 06006KT 10SM -RA OVC040 OVC200TCU 13/12 A3001',
        (
            _TestValue(attr_name='cloud_layers',
                       expected_result=[
                           avwx.structs.Cloud(repr='OVC040', type='OVC', altitude=40, modifier=None),
                           avwx.structs.Cloud(repr='OVC200TCU', type='OVC', altitude=200, modifier='TCU'),
                       ]),
            _TestCall(attr_name='_clouds_as_str',
                      expected='Overcast layer at 4000ft, Overcast layer at 20000ft (Towering Cumulus).',
                      spoken=False),
            _TestCall(attr_name='_clouds_as_str',
                      expected='Overcast layer at four thousand feet, Overcast layer at twenty thousand feet '
                               '(Towering Cumulus).',
                      spoken=True),
        ),
    ),
    (
        'KLAW 121053Z AUTO 06006KT 2SM -RA NSC 13/12 A3001',
        (
            _TestValue(attr_name='cloud_layers',
                       expected_result=[]),
            _TestCall(attr_name='_clouds_as_str',
                      expected='No significant cloud.',
                      spoken=False),
            _TestCall(attr_name='_clouds_as_str',
                      expected='No significant cloud.',
                      spoken=True),
        ),
    ),
    (
        'KLAW 121053Z AUTO 06006KT 2SM -RA BKN150 13/12 A3001',
        (
            _TestValue(attr_name='cloud_layers',
                       expected_result=[
                           avwx.structs.Cloud(repr='BKN150', type='BKN', altitude=150, modifier=None)
                       ]),
            _TestCall(attr_name='_clouds_as_str',
                      expected='Broken layer at 15000ft.',
                      spoken=False),
            _TestCall(attr_name='_clouds_as_str',
                      expected='Broken layer at fifteen thousand feet.',
                      spoken=True),
        ),
    ),
    (
        'KLAW 121053Z AUTO 06006KT 2SM -RA BKN009 13/12 A3001',
        (
            _TestValue(attr_name='cloud_layers',
                       expected_result=[
                           avwx.structs.Cloud(repr='BKN009', type='BKN', altitude=9, modifier=None)
                       ]),
            _TestCall(attr_name='_clouds_as_str',
                      expected='Broken layer at 900ft.',
                      spoken=False),
            _TestCall(attr_name='_clouds_as_str',
                      expected='Broken layer at nine hundred feet.',
                      spoken=True),
        ),
    ),
]


@pytest.mark.parametrize('metar_str, expected', _TEST_DATA)
@pytest.mark.weather
def test_clouds_in_weather_from_metar_str(metar_str, expected):
    wx = elib_wx.Weather(metar_str)
    assert isinstance(wx, elib_wx.Weather)
    for test_value in expected:
        expected, actual = test_value.verify(wx)
        assert expected == actual


@given(
    density=st.sampled_from(['FEW', 'SCT', 'BKN', 'OVC']),
    modifier=st.sampled_from(['', '', 'AC', 'ACC', 'AS', 'CB', 'CC', 'CI', 'CS', 'CU', 'FC', 'FS', 'NS', 'SC', 'ST',
                              'TCU', '', '', '', '', '']),
    altitude=st.integers(min_value=2, max_value=500),
)
@pytest.mark.weather
def test(density, modifier, altitude):
    metar_str = f'KLAW 121053Z AUTO 06006KT 2SM -RA {density}{altitude:03d}{modifier} 13/12 A300'
    wx = elib_wx.Weather(metar_str)
    cloud_layer = wx.cloud_layers[0]
    assert cloud_layer.altitude == altitude
    if modifier == '':
        assert cloud_layer.modifier is None
    else:
        assert cloud_layer.modifier == modifier
    assert cloud_layer.repr == f'{density}{altitude:03d}{modifier}'
    cloud_str = wx._clouds_as_str(spoken=False)
    if modifier != '':
        assert elib_wx.static.CLOUD_TRANSLATIONS[modifier] in cloud_str


@pytest.mark.weather
def test_no_altitude():
    metar_str = 'KLAW 121053Z AUTO 06006KT 2SM -RA BKN150 13/12 A3001'
    wx = elib_wx.Weather(metar_str)
    wx.cloud_layers[0].altitude = None
    assert 'Sky clear.' == wx._clouds_as_str(spoken=False)


@pytest.mark.weather
def test_unknown_modifier():
    metar_str = 'KLAW 121053Z AUTO 06006KT 2SM -RA BKN150XXX 13/12 A3001'
    wx = elib_wx.Weather(metar_str)
    assert 'Broken layer at 15000ft.' == wx._clouds_as_str(spoken=False)
