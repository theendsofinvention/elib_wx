# coding=utf-8

import pytest

import elib_wx


@pytest.mark.long
def test_all_metars(metar_string):
    if metar_string[0] not in ('O', 'K', 'U'):
        return
    assert isinstance(metar_string, str)
    try:
        wx = elib_wx.Weather(metar_string)
        assert isinstance(wx, elib_wx.Weather)
        wx.as_speech()
    except elib_wx.BadStationError:
        pass
