# coding=utf-8
"""
Michael duPont - michael@mdupont.com
Original source: https://github.com/flyinactor91/AVWX-Engine
Modified by etcher@daribouca.net
"""

from elib_wx.exc import ELIBWxError


class BadStationError(ELIBWxError):
    """
    Station does not exist
    """

    def __init__(self, station: str, msg: str) -> None:
        self.station = station
        self.msg = msg
        super(BadStationError, self).__init__(f'{self.msg}: {self.station}')


class InvalidRequestError(ELIBWxError):
    """
    Unable to fetch data
    """
    pass


class SourceError(ELIBWxError):
    """
    Source servers returned an error code
    """
    pass
