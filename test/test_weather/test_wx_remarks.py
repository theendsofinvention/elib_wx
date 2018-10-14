# coding=utf-8

import pytest

import elib_wx

_TEST_DATA = [
    (
        'BGTL 021556Z AUTO 09020G30KT 9999 FEW029 01/M03 A3006 RMK AO2 PK WND 14034/10 SLP165 T00071029 TSNO $',
        'Automated with precipitation sensor. Sea level pressure: one zero one six point one zero five hecto pascal. '
        'Thunderstorm information not available. ASOS requires maintenance.'
    ),
    (
        'CAHR 021600Z AUTO 18002KT 12/04 RMK AO1 SLP290 T01240035 58009',
        'Automated with no precipitation sensor. Sea level pressure: one zero two nine point one zero zero hecto '
        'pascal. Three hours pressure difference: plus or minus zero point nine millibars - Steady or increasing, '
        'then decreasing.'
    ),
    (
        'CALK 230056Z AUTO 17010KT 10SM CLR 24/02 A3014 RMK AO2 SLP118 T02440017 TSNO $ ',
        'Automated with precipitation sensor. Sea level pressure: one zero one one point one zero eight hecto pascal. '
        'Thunderstorm information not available. ASOS requires maintenance.'
    ),
    (
        'CBBC 021600Z AUTO 02010G16KT 350V070 9SM CLR 08/M08 A2991 RMK SLP131',
        'Sea level pressure: one zero one three point one zero one hecto pascal.'
    ),
    (
        'CERM 021600Z AUTO 14003KT 11/M00 RMK AO1 SLP280 T01071001 58022',
        'Automated with no precipitation sensor. Sea level pressure: one zero two eight point one zero zero hecto '
        'pascal. Three hours pressure difference: plus or minus two point two millibars - Steady or increasing, '
        'then decreasing.'
    ),
    (
        'CFP7 161900Z 35017G22KT 15SM BKN018 BKN040 OVC100 09/05 A3004 RMK SC6SC1AC1 DA2072FT LAST OBS SLP168',
        'Sea level pressure: one zero one six point one zero eight hecto pascal.'
    ),
    (
        'CINS 200256Z AUTO 00000KT 10SM CLR 21/M08 A2994 RMK AO2 SLP107 T02061078 53014 ',
        'Automated with precipitation sensor. Sea level pressure: one zero one zero point one zero seven hecto '
        'pascal. Three hours pressure difference: plus or minus one point four millibars - Decreasing or steady, '
        'then increasing.'
    ),
    (
        'CMCW 141200Z AUTO 32004KT 16/13 RMK AO1 T01590129',
        'Automated with no precipitation sensor.'
    ),
    (
        'CMFM 021600Z AUTO 11005KT 06/02 RMK AO1 SLP256 T00580015 58018',
        'Automated with no precipitation sensor. Sea level pressure: one zero two five point one zero six hecto '
        'pascal. Three hours pressure difference: plus or minus one point eight millibars - Steady or increasing, '
        'then decreasing.'
    ),
    (
        'CMFM 021600Z AUTO 11005KT 06/02 RMK AO1 SLP256 T00580015 58018',
        'Automated with no precipitation sensor. Sea level pressure: one zero two five point one zero six hecto pascal.'
        ' Three hours pressure difference: plus or minus one point eight millibars - Steady or increasing, '
        'then decreasing.'
    ),
    (
        'CP69 140352Z AUTO VRB00KT 02/02 A2990 RMK AO2 SLP143 T00220022 PWINO FZRANO TSNO ',
        'Automated with precipitation sensor. Sea level pressure: one zero one four point one zero three hecto pascal. '
        'Precipitation identifier information not available. Freezing rain information not available. Thunderstorm '
        'information not available.'
    ),
    (
        'CWBO 021600Z AUTO 06005KT M00/M01 RMK AO1 2PAST HR 0000 SLP180 P0001 T10011010 50002',
        'Automated with no precipitation sensor. Sea level pressure: one zero one eight point one zero zero hecto '
        'pascal. Hourly precipitation: zero point zero one inches. Three hours pressure difference: plus or minus zero '
        'point two millibars - Increasing, then decreasing.'
    ),
    (
        'KBKW 021602Z AUTO 22007KT 3SM -RA BR SCT014 BKN050 OVC070 19/17 A3030 RMK AO2 P0001 T01890172 TSNO',
        'Automated with precipitation sensor. Hourly precipitation: zero point zero one inches. Thunderstorm '
        'information not available.'
    ),
    (
        'CHSE 131531Z AUTO 32009G19KT 1 1/4SM RA BR OVC004 15/15 A2952 RMK AO2 CIG 002V007 P0002 TSNO ',
        'Automated with precipitation sensor. Hourly precipitation: zero point zero two inches. Thunderstorm '
        'information not available.'
    ),
]


@pytest.mark.weather
@pytest.mark.parametrize('metar_str, expected_remarks_speech', _TEST_DATA)
def test_remarks(metar_str, expected_remarks_speech):
    wx = elib_wx.Weather(metar_str)
    assert expected_remarks_speech == wx._remarks_as_str(spoken=True)
