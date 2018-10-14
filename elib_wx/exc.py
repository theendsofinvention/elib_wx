# coding=utf-8
"""
Exceptions for elib_miz
"""


class ELIBWxError(Exception):
    """Base error for elib_miz"""


class InvalidWeatherSourceError(ELIBWxError):
    """Raised when Weather receives an invalid source"""

    def __init__(self, source, msg: str) -> None:
        self.source = source
        self.source_type = type(source)
        self.msg = msg
        msg = f'{msg}: "{self.source}" ({self.source_type})'
        super(InvalidWeatherSourceError, self).__init__(msg)


class InvalidICAOError(ELIBWxError):
    """Raised when an invalid ICAO code is given"""

    def __init__(self, icao: str) -> None:
        self.icao = icao
        super(InvalidICAOError, self).__init__(f'invalid ICAO code: {icao}')


class StationNotFoundError(ELIBWxError):
    """Raised when an ICAO seems valid but no station was found"""

    def __init__(self, icao: str) -> None:
        self.icao = icao
        link = 'http://tgftp.nws.noaa.gov/data/observations/metar/stations/'
        msg = f'A list of all available stations can be found at: {link}'
        super(StationNotFoundError, self).__init__(f'station not found: {icao}\n{msg}')


class FileAlreadyExistsError(ELIBWxError):
    """Raised when an existing file would be overwritten"""

    def __init__(self, file: str) -> None:
        self.file = file
        super(FileAlreadyExistsError, self).__init__(f'file already exists: {file}')


class SourceMizFileNotFoundError(ELIBWxError):
    """Raised when an existing file would be overwritten"""

    def __init__(self, file: str) -> None:
        self.file = file
        super(SourceMizFileNotFoundError, self).__init__(f'source MIZ file not found: {file}')
