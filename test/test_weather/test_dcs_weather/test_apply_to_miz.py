# coding=utf-8


from pathlib import Path

import elib_miz
import pytest

import elib_wx


@pytest.mark.weather
def test_apply_to_miz(test_data, wx_test_file_1):
    test_miz_file = './test.miz'
    metar, expected = test_data
    wx = elib_wx.Weather(metar)
    wx.apply_to_miz(str(wx_test_file_1), test_miz_file)
    with elib_miz.Miz(test_miz_file) as miz:
        for test_value in expected:
            expected, actual = test_value.verify(miz.mission.weather)
            assert expected == actual


@pytest.mark.weather
def test_apply_to_miz_file_exists(test_data, wx_test_file_1):
    metar, _ = test_data
    wx = elib_wx.Weather(metar)
    test_miz_file = Path('./test.miz').absolute()
    test_miz_file.touch()
    with pytest.raises(elib_wx.FileAlreadyExistsError):
        wx.apply_to_miz(str(wx_test_file_1), str(test_miz_file))


@pytest.mark.weather
def test_apply_to_miz_file_exists_overwrite(wx_test_file_1):
    wx = elib_wx.Weather('KLAW 121053Z AUTO 06006G12KT 8000 OVC050 13/12 Q1013')
    test_miz_file = Path('./test.miz').absolute()
    test_miz_file.touch()
    wx.apply_to_miz(str(wx_test_file_1), str(test_miz_file), overwrite=True)


@pytest.mark.weather
def test_apply_to_miz_no_source_file():
    wx = elib_wx.Weather('KLAW 121053Z AUTO 06006G12KT 8000 OVC050 13/12 Q1013')
    test_miz_file = Path('./test.miz').absolute()
    with pytest.raises(elib_wx.SourceMizFileNotFoundError):
        wx.apply_to_miz(test_miz_file, str(test_miz_file))
