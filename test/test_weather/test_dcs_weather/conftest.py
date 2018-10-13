# coding=utf-8

import typing

import pytest

from test.utils import _TestValue


@pytest.fixture(
    params=[
        (
            # Generic test
            'KLAW 121053Z AUTO 06006KT 10SM OVC050 13/12 Q1013',
            (
                _TestValue(attr_name='altimeter', expected_result=760),
                _TestValue(attr_name='temperature', expected_result=13),
                _TestValue(attr_name='wind_ground_speed', expected_result=3),
                _TestValue(attr_name='wind_ground_dir', expected_result=240),
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
            'KLAW 121053Z AUTO 06006KT 5000 -RA OVC050 13/12 Q1013',
            (
                _TestValue(attr_name='fog_enabled', expected_result=True),
                _TestValue(attr_name='fog_thickness', expected_result=1000),
                _TestValue(attr_name='fog_visibility', expected_result=5000),
            ),
        ),
        (
            # Reported visibility over 6000
            'KLAW 121053Z AUTO 06006KT 8000 -RA OVC050 13/12 Q1013',
            (
                _TestValue(attr_name='fog_enabled', expected_result=True),
                _TestValue(attr_name='fog_thickness', expected_result=1000),
                _TestValue(attr_name='fog_visibility', expected_result=6000),
            ),
        ),
        (
            # Turbulence
            'KLAW 121053Z AUTO 06006G12KT 8000 OVC050 13/12 Q1013',
            (
                _TestValue(attr_name='turbulence', expected_result=20),
                _TestValue(attr_name='wind_ground_speed', expected_result=3),
            ),
        ),
    ],

    ids=['Generic test', 'Reported visibility at 5000', 'Reported visibility over 6000', 'Turbulence']
)
def test_data(request) -> typing.Tuple[str, typing.Set[_TestValue]]:
    yield request.param[0], request.param[1]
