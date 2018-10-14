# coding=utf-8
"""
Michael duPont - michael@mdupont.com
Original source: https://github.com/flyinactor91/AVWX-Engine
Modified by etcher@daribouca.net
"""

import json
import os
from copy import deepcopy
from datetime import datetime
from glob import glob

# library
import pytest
from dataclasses import asdict

# module
from elib_wx.avwx import Taf, core, structs, taf


@pytest.mark.long
def test_fetch():
    """
    Tests if the old fetch function returns a report from a Service object
    """
    for station in ('KJFK', 'PHNL', 'EGLL', 'RKSI'):
        report = taf.fetch(station)
        assert isinstance(report, str)
        assert report.startswith(station) or report.startswith('AMD ' + station)


def test_parse():
    """
    Tests returned structs from the parse function
    """
    report = ('PHNL 042339Z 0500/0606 06018G25KT P6SM FEW030 SCT060 FM050600 06010KT '
              'P6SM FEW025 SCT060 FM052000 06012G20KT P6SM FEW030 SCT060')
    data, units = taf.parse(report[:4], report)
    assert isinstance(data, structs.TafData)
    assert isinstance(units, structs.Units)
    assert data.raw == report


def test_prob_line():
    """
    Even though PROB__ is not in TAF_NEWLINE, it should still separate,
    add a new line, and include the prob value in line.probability
    """
    report = ("TAF AMD CYBC 271356Z 2714/2802 23015G25KT P6SM BKN090 "
              "TEMPO 2714/2718 P6SM -SHRA BKN060 OVC090 "
              "FM271800 22015G25KT P6SM OVC040 "
              "TEMPO 2718/2724 6SM -SHRA "
              "PROB30 2718/2724 VRB25G35KT 1SM +TSRA BR BKN020 OVC040CB "
              "FM280000 23008KT P6SM BKN040 RMK FCST BASED ON AUTO OBS. NXT FCST BY 272000Z")
    _taf = Taf('CYBC')
    _taf.update(report)
    lines = _taf.taf_data.forecast
    assert len(lines) == 6
    assert lines[3].probability is None
    assert lines[4].probability == core.make_number('30')
    assert lines[4].raw.startswith('PROB30')


def test_wind_shear():
    """
    Wind shear should be recognized as its own element in addition to wind
    """
    report = ("TAF AMD CYOW 282059Z 2821/2918 09008KT WS015/20055KT P6SM BKN220 "
              "BECMG 2821/2823 19015G25KT "
              "FM290300 21013G23KT P6SM -SHRA BKN040 OVC100 "
              "TEMPO 2903/2909 4SM BR OVC020 "
              "FM290900 25012KT P6SM SCT030 "
              "FM291300 32017G27KT P6SM OVC030 "
              "TEMPO 2913/2918 P6SM -SHRA OVC020 RMK NXT FCST BY 290000Z")
    _taf = Taf('CYBC')
    _taf.update(report)
    lines = _taf.taf_data.forecast
    assert len(lines) == 7
    assert lines[0].wind_shear == 'WS015/20055'
    assert _taf.taf_translations.forecast[1].clouds is None


def test_prob_tempo():
    """
    Non-PROB types should take precedence but still fill the probability value
    """
    report = ("EGLL 192253Z 2000/2106 28006KT 9999 BKN035 "
              "PROB30 TEMPO 2004/2009 BKN012 "
              "PROB30 TEMPO 2105/2106 8000 BKN006")
    _taf = Taf('EGLL')
    _taf.update(report)
    lines = _taf.taf_data.forecast
    for line in lines:
        assert isinstance(line.start_time, structs.Timestamp)
        assert isinstance(line.end_time, structs.Timestamp)
    for i in range(1, 3):
        assert lines[i].type == 'TEMPO'
        assert lines[i].probability.value == 30


# maxDiff = None
def test_taf_ete():
    """
    Performs an end-to-end test of all TAF JSON files
    """

    def _nodate(s):
        return s[s.find('-') + 2:]

    for path in glob(os.path.dirname(os.path.realpath(__file__)) + '/taf/*.json'):
        ref = json.load(open(path))
        station = Taf(path.split('/')[-1][:4])
        assert station.last_updated is None
        assert station.update(ref['data']['raw']) is True
        assert isinstance(station.last_updated, datetime)
        # Clear timestamp due to parse_date limitations
        nodt = deepcopy(station.taf_data)
        for key in ('time', 'start_time', 'end_time'):
            setattr(nodt, key, None)
        for i in range(len(nodt.forecast)):
            for key in ('start_time', 'end_time'):
                setattr(nodt.forecast[i], key, None)
        assert asdict(nodt) == ref['data']
        assert asdict(station.taf_translations) == ref['translations']
        assert station.summary == ref['summary']
        assert _nodate(station.speech) == _nodate(ref['speech'])
        # assert asdict(station.station_info) == ref['station_info']
