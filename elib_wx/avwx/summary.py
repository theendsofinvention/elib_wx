# coding=utf-8
"""
Michael duPont - michael@mdupont.com
Original source: https://github.com/flyinactor91/AVWX-Engine
Modified by etcher@daribouca.net
"""

# module
from .structs import MetarTrans, TafLineTrans


def metar(trans: MetarTrans) -> str:
    """
    Condense the translation strings into a single report summary string
    """
    summary = []
    if trans.wind:
        summary.append('Winds ' + trans.wind)
    if trans.visibility:
        summary.append('Vis ' + trans.visibility[:trans.visibility.find(' (')].lower())
    if trans.temperature:
        summary.append('Temp ' + trans.temperature[:trans.temperature.find(' (')])
    if trans.dewpoint:
        summary.append('Dew ' + trans.dewpoint[:trans.dewpoint.find(' (')])
    if trans.altimeter:
        summary.append('Alt ' + trans.altimeter[:trans.altimeter.find(' (')])
    if trans.other:
        summary.append(trans.other)
    if trans.clouds:
        summary.append(trans.clouds.replace(' - Reported AGL', ''))
    return ', '.join(summary)


def taf(trans: TafLineTrans) -> str:
    """
    Condense the translation strings into a single forecast summary string
    """
    summary = []
    if trans.wind:
        summary.append('Winds ' + trans.wind)
    if trans.visibility:
        summary.append('Vis ' + trans.visibility[:trans.visibility.find(' (')].lower())
    if trans.altimeter:
        summary.append('Alt ' + trans.altimeter[:trans.altimeter.find(' (')])
    if trans.other:
        summary.append(trans.other)
    if trans.clouds:
        summary.append(trans.clouds.replace(' - Reported AGL', ''))
    if trans.wind_shear:
        summary.append(trans.wind_shear)
    if trans.turbulance:
        summary.append(trans.turbulance)
    if trans.icing:
        summary.append(trans.icing)
    return ', '.join(summary)
