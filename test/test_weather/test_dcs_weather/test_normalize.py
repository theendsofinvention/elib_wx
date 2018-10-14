# coding=utf-8

import pytest
from hypothesis import given, strategies as st

import elib_wx


@pytest.mark.weather
@pytest.mark.parametrize(
    'attr, min_, max_',
    [
        ('altimeter', 720, 790),
        ('temperature', -20, 40),
        ('turbulence', 0, 60),
        ('dust_density', 300, 3000),
        ('fog_visibility', 0, 6000),
        ('cloud_base', 300, 5000),
        ('cloud_thickness', 200, 2000),
        ('wind_speed', 0, 50),
    ]
)
@given(value=st.floats(allow_nan=False, allow_infinity=False))
def test_normalize(attr, min_, max_, value):
    func = getattr(elib_wx.weather.DCSWeather, f'normalize_{attr}')
    assert min_ <= func(value) <= max_
