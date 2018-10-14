# coding=utf-8
"""
Top-level package for elib_wx.
"""
# pylint: disable=wrong-import-position
import logging

from pkg_resources import DistributionNotFound, get_distribution

try:
    __version__ = get_distribution('elib_wx').version
except DistributionNotFound:  # pragma: no cover
    # package is not installed
    __version__ = 'not installed'

__author__ = """etcher"""
__email__ = 'etcher@daribouca.net'


class Config:
    """
    elib_wx config options
    """
    dummy_icao_code: str = "XXXX"


LOGGER = logging.getLogger('elib.wx')

# noinspection PyPep8
from elib_wx.exc import (
    ELIBWxError, StationNotFoundError, SourceMizFileNotFoundError, FileAlreadyExistsError,
    InvalidICAOError, InvalidWeatherSourceError,
)
# noinspection PyPep8
from elib_wx.avwx.exceptions import BadStationError, InvalidRequestError, SourceError
# noinspection PyPep8
from elib_wx.weather import Weather
