# coding=utf-8
# type: ignore
"""
Michael duPont - michael@mdupont.com
Original source: https://github.com/flyinactor91/AVWX-Engine
Modified by etcher@daribouca.net
"""

# type: ignore
# type: ignore
# stdlib
from datetime import datetime
from os import path

# module
from . import metar, service, speech, structs, summary, taf, translate
from .core import valid_station
from .exceptions import BadStationError
from .static import INFO_KEYS

INFO_PATH = path.dirname(path.realpath(__file__)) + '/stations.json'


# STATIONS = json.load(open(INFO_PATH))


# type: ignore

class Report:
    """
    Base report to take care of service assignment and station info
    """

    #: UTC Datetime object when the report was last updated
    last_updated: datetime

    #: The un-parsed report string. Fetched on update()
    raw: str

    #: ReportData dataclass of parsed data values and units. Parsed on update()
    data: structs.ReportData

    #: ReportTrans dataclass of translation strings from data. Parsed on update()
    translations: structs.ReportTrans

    #: Units inferred from the station location and report contents
    units: structs.Units

    _station_info: structs.StationInfo

    def __init__(self, station: str) -> None:
        # Raises a BadStation error if needed
        valid_station(station)

        #: Service object used to fetch the report string
        # noinspection PyCallingNonCallable
        self.service = service.get_service(station)(self.__class__.__name__.lower())

        #: 4-character ICAO station ident code the report was initialized with
        self.station = station

    def update(self, report: str = None) -> bool:
        """
        Updates report elements. Not implemented
        """
        raise NotImplementedError()


class Metar(Report):
    """
    Class to handle METAR report data
    """

    metar_data: structs.MetarData
    metar_translations: structs.MetarTrans

    def update(self, report: str = None) -> bool:
        """Updates raw, data, and translations by fetching and parsing the METAR report

        Returns True is a new report is available, else False
        """
        if report is not None:
            self.raw = report
        else:
            raw = self.service.fetch(self.station)
            if raw == self.raw:
                return False
            self.raw = raw
        self.metar_data, self.units = metar.parse(self.station, self.raw)
        self.metar_translations = translate.metar(self.metar_data, self.units)
        self.last_updated = datetime.utcnow()
        return True

    @property
    def summary(self) -> str:
        """
        Condensed report summary created from translations
        """
        if not self.metar_translations:
            self.update()
        return summary.metar(self.metar_translations)

    @property
    def speech(self) -> str:
        """
        Report summary designed to be read by a text-to-speech program
        """
        if not self.metar_data:
            self.update()
        return speech.metar(self.metar_data, self.units)


class Taf(Report):
    """
    Class to handle TAF report data
    """

    taf_data: structs.TafData
    taf_translations: structs.TafTrans

    def update(self, report: str = None) -> bool:
        """
        Updates raw, data, and translations by fetching and parsing the TAF report

        Returns True is a new report is available, else False
        """
        if report is not None:
            self.raw = report
        else:
            raw = self.service.fetch(self.station)
            if raw == self.raw:
                return False
            self.raw = raw
        self.taf_data, self.units = taf.parse(self.station, self.raw)
        self.taf_translations = translate.taf(self.taf_data, self.units)
        self.last_updated = datetime.utcnow()
        return True

    @property
    def summary(self):
        """
        Condensed summary for each forecast created from translations
        """
        if not self.taf_translations:
            self.update()
        return [summary.taf(trans) for trans in self.taf_translations.forecast]

    @property
    def speech(self) -> str:
        """
        Report summary designed to be read by a text-to-speech program
        """
        if not self.taf_data:
            self.update()
        return speech.taf(self.taf_data, self.units)
